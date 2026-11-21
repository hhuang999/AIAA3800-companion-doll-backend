"""Stream plain speech immediately with early first-clause dispatch and safe rail recovery."""

import re
import threading
import time
from collections.abc import Iterator

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from companion.cognition.models import Usage
from companion.cognition.policy import boundary_blocks_probe, prompt_projection
from companion.llm.client import LLMClient
from companion.memory.service import estimate_tokens

from .config import Config
from .helpers import resolve_emoji
from .models import TurnContext
from .output_rail import OutputRail

SEVERE_RAILS = {"rail_medical", "rail_appearance", "rail_intimate", "rail_guarantee"}
DANGLING_PREFIX = re.compile(
    r"^(?:这|那|它|他|她|所以|而且|但是|不过|然后|因为|或者|这样|那样|因此|再|也|还)"
)


def _content_chars(text: str) -> int:
    return sum(1 for ch in text if "\u4e00" <= ch <= "\u9fff" or ch.isalnum())


class Talker:
    def __init__(self, config: Config, llm: LLMClient) -> None:
        self.config = config
        self.llm = llm
        self.rail = OutputRail(config)
        self.env = Environment(
            loader=FileSystemLoader(config.directory / "prompts"),
            undefined=StrictUndefined,
            autoescape=False,
        )

    def parse_tag(self, line: str, context: TurnContext, violations: list[str]) -> str:
        match = re.fullmatch(
            r"<<state=([^;]+);card=([^;]+);emo=([^;]+);offer=([^>]+)>>", line.strip()
        )
        if not match:
            violations.append("missing_tag")
            return self.config.rules["emojis"]["default"]
        stage, card, emoji, offer = match.groups()
        if stage != context.stage.value:
            violations.append("tag_state_mismatch")
        if card != (context.card_id or "-"):
            violations.append("card_not_allowed")
        if offer != "-":
            # Invitations are issued by the deterministic template path.
            violations.append("offer_not_allowed")
        if emoji not in self.config.rules["emojis"]["allowed"]:
            violations.append("emoji_not_allowed")
            return self.config.rules["emojis"]["default"]
        return emoji

    @staticmethod
    def _next_boundary(buffer: str, *, allow_clause: bool) -> tuple[int | None, bool]:
        strong = set("。！？!?…；\n")
        clauses = set("，,：:")
        closing = set('”’」』"')
        in_quote = False
        chars = 0
        for i, char in enumerate(buffer):
            if char == '"':
                in_quote = not in_quote
            elif char in ("“", "「", "『"):
                in_quote = True
            elif char in ("”", "」", "』"):
                in_quote = False
            if "\u4e00" <= char <= "\u9fff" or char.isalnum():
                chars += 1
            if char in strong and chars >= 2:
                end = i + 1
                while end < len(buffer) and buffer[end] in closing:
                    end += 1
                if not in_quote:
                    return end, False
                if end > i + 1 or char == "\n" or chars >= 45:
                    return end, False
            if allow_clause and not in_quote and char in clauses and chars >= 8:
                return i + 1, True
        return None, False

    def run(
        self,
        context: TurnContext,
        history: list[dict],
        cancel: threading.Event,
        metrics: dict,
        violations: list[str],
        step: int = 1,
        sentence_limit: int | None = None,
    ) -> Iterator[tuple[str, str]]:
        config = self.config
        sentence_limit = sentence_limit or config.settings.dialogue.max_sentences
        card_id = (
            config.resolve_card_id(context.card_id)
            if hasattr(config, "resolve_card_id")
            else context.card_id
        )
        card = config.cards.get(card_id)
        previous_reply = next(
            (row["text"] for row in reversed(history) if row["role"] == "assistant"), ""
        )
        question_budget = int(
            not any(mark in previous_reply for mark in ("?", "？"))
            or card is not None
            or any(mark in context.text for mark in ("?", "？"))
        )
        if any(
            a.kind == "no_topic_probe" and a.target in (None, "current_topic")
            for a in context.policy_frame.avoid
        ) or any(
            boundary_blocks_probe(b, None, context.text)
            for b in context.policy_frame.active_boundaries
        ):
            question_budget = 0
        policy_json = prompt_projection(
            context.policy_frame, config.settings.cognition.context_tokens
        )
        prompt = self.env.get_template("talker.j2").render(
            persona=config.persona,
            rules=config.rules,
            context=context,
            stage=config.stages[context.stage.value],
            card=card,
            step=step,
            action_step=card.talker.steps[min(step, len(card.talker.steps)) - 1] if card else None,
            signals=context.signals.model_dump_json(),
            question_budget=question_budget,
        )
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": "<policy_data>" + policy_json + "</policy_data>"},
        ]
        for row in history:
            messages.append({"role": row["role"], "content": row["text"]})
        if not history or history[-1].get("id") != context.turn_id:
            messages.append({"role": "user", "content": context.text})
        metrics["talker_usage"] = Usage(
            input_tokens=estimate_tokens(messages), source="estimated"
        ).model_dump()

        def record_usage(value):
            metrics["talker_usage"] = value.model_dump()

        stream = self.llm.stream_chat(
            config.settings.llm.talker_model,
            messages,
            cancel,
            context.t0 + config.settings.timing.talker_total_timeout_s,
            first_token_timeout_s=config.settings.timing.talker_first_token_timeout_ms / 1000,
            temperature=0.7,
            max_tokens=160,
            usage_callback=record_usage,
        )
        header = ""
        buffer = ""
        parsed = False
        discard_header = False
        emoji = resolve_emoji(context, card, config)
        count = 0
        questions = 0
        effective_limit = sentence_limit
        early_clause_used = False
        dropped_previous = False
        severe_abort = False

        def check_sentence(segment: str) -> tuple[str, ...]:
            rejected = self.rail.check(
                segment, context.stage, tuple(card.talker.never_say) if card else ()
            )
            question_count = sum(segment.count(mark) for mark in ("?", "？"))
            if questions + question_count > question_budget:
                rejected += ("rail_questions",)
            return rejected

        try:
            for token in stream:
                if cancel.is_set():
                    return
                metrics.setdefault("first_token_ms", (time.monotonic() - context.t0) * 1000)
                if discard_header:
                    if "\n" not in token:
                        continue
                    _, token = token.split("\n", 1)
                    discard_header = False
                if not parsed:
                    header += token
                    stripped = header.lstrip()
                    if stripped and not stripped.startswith("<"):
                        buffer, parsed = header, True
                    elif "\n" in header:
                        line, buffer = header.split("\n", 1)
                        parsed_emoji = self.parse_tag(line, context, violations)
                        if (
                            line.startswith("<<")
                            and parsed_emoji in config.rules["emojis"]["allowed"]
                        ):
                            emoji = parsed_emoji
                        elif not line.startswith("<<"):
                            buffer = line + "\n" + buffer
                        parsed = True
                    elif len(header) > 256:
                        violations.append("missing_tag")
                        buffer = "" if header.startswith("<<") else header
                        discard_header = header.startswith("<<")
                        parsed = True
                    else:
                        continue
                else:
                    buffer += token
                if count:
                    buffer = buffer.lstrip(" \n")
                while True:
                    allow_clause = count == 0 and not early_clause_used
                    boundary, is_clause = self._next_boundary(buffer, allow_clause=allow_clause)
                    if boundary is None:
                        break
                    sentence, buffer = buffer[:boundary].strip(), buffer[boundary:]
                    if not sentence:
                        continue
                    if dropped_previous and DANGLING_PREFIX.match(sentence):
                        violations.append("rail_orphan_fragment")
                        continue
                    rejected = check_sentence(sentence)
                    if rejected:
                        violations.extend(rejected)
                        dropped_previous = True
                        if count == 0 and set(rejected) & SEVERE_RAILS:
                            severe_abort = True
                            break
                        continue
                    dropped_previous = False
                    if is_clause:
                        early_clause_used = True
                        effective_limit = sentence_limit + 1
                    if count >= effective_limit:
                        violations.append("too_many_sentences")
                        return
                    metrics.setdefault("first_sentence_ms", (time.monotonic() - context.t0) * 1000)
                    questions += sum(sentence.count(mark) for mark in ("?", "？"))
                    count += 1
                    yield sentence, emoji
                    if count >= effective_limit:
                        if _content_chars(buffer) > 0:
                            violations.append("too_many_sentences")
                        return
                if severe_abort:
                    break
            if not parsed and not severe_abort:
                if header.startswith("<<"):
                    violations.append("malformed_tag")
                buffer = "" if header.startswith("<<") else header
            tail = buffer.strip()
            if (
                not severe_abort
                and _content_chars(tail) > 0
                and count < effective_limit
                and not cancel.is_set()
                and not (dropped_previous and DANGLING_PREFIX.match(tail))
            ):
                rejected = check_sentence(tail)
                if rejected:
                    violations.extend(rejected)
                else:
                    count += 1
                    metrics.setdefault("first_sentence_ms", (time.monotonic() - context.t0) * 1000)
                    yield tail, emoji
            if count == 0 and not cancel.is_set():
                metrics["fallback"] = True
                yield config.stages[context.stage.value]["fallback"], emoji
        finally:
            close = getattr(stream, "close", None)
            if close:
                close()
