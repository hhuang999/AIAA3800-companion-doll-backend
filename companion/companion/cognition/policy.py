"""Local plan selection and scoped boundary enforcement. No network or background Future is awaited."""

import json

from companion.memory.concepts import action_domain_text, concept_clusters, targets_overlap
from companion.memory.models import MemoryCandidate
from companion.memory.service import estimate_tokens

from .base import utcnow
from .models import TurnPolicyFrame

NON_ACTION = {
    "listen",
    "clarify",
    "comfort",
    "reflect",
    "close",
    "quiet",
    "attuned_listen",
    "tentative_reflect",
    "low_energy_companionship",
    "quiet_presence",
}


def plan_invalid_reason(plan, state, revisions, items, now=None):
    if plan is None:
        return "no_plan"
    now = now or utcnow()
    if state.lifecycle != "active" or state.mode != "normal":
        return "lifecycle_or_mode"
    if plan.user_key != state.user_key or plan.session_id != state.session_id:
        return "identity"
    if plan.status != "active":
        return plan.status
    if (
        plan.valid_until <= now
        or state.user_turns - plan.source_user_index > plan.max_user_turn_delta
    ):
        return "expired"
    if plan.topic_revision != state.topic_revision or plan.policy_revision != state.policy_revision:
        return "control_revision"
    if plan.boundary_revision != revisions["boundary_revision"]:
        return "boundary_revision"
    versions = {item.memory_id: item.version for item in items if item.status == "active"}
    if any(versions.get(i) != v for i, v in plan.memory_dependency_versions):
        return "memory_dependency"
    return None


def effective_boundaries(bundle):
    # A scoped latest exception masks a restriction without deleting its record.
    ordered = sorted(bundle.boundaries, key=lambda item: item.source_cursor, reverse=True)
    exceptions = []
    result = []
    for item in ordered:
        if item.boundary_rule in ("allow", "revoke"):
            exceptions.append((item.target, item.source_cursor))
        elif not any(
            cursor > item.source_cursor
            and (
                exc_target == item.target
                or (
                    exc_target not in (None, "current_topic")
                    and item.target not in (None, "current_topic")
                    and targets_overlap(exc_target, item.target)
                )
            )
            for exc_target, cursor in exceptions
        ):
            result.append(item)
    return tuple(result)


def no_advice_blocks_text(target: str | None, current_text: str, recent_text: str = "") -> bool:
    """Return True if a no_advice boundary with this target covers the current turn."""
    if target in (None, "all_topics", "current_topic"):
        return True
    if not current_text.strip():
        return not recent_text or targets_overlap(target, recent_text)
    if targets_overlap(target, current_text):
        return True
    current_clusters = concept_clusters(current_text)
    if current_clusters:
        return False
    return not recent_text or targets_overlap(target, recent_text)


def no_advice_blocks_action(
    target: str | None, action_obj: object, current_text: str, recent_text: str = ""
) -> bool:
    """Return True if a no_advice boundary blocks this specific card/exercise."""
    if target in (None, "all_topics", "current_topic"):
        return True
    if action_obj is not None:
        if targets_overlap(target, action_domain_text(action_obj)):
            return True
        return bool(current_text.strip() and targets_overlap(target, current_text))
    return no_advice_blocks_text(target, current_text, recent_text)


def boundary_blocks_probe(boundary, question_text: str | None, current_text: str = "") -> bool:
    """Check whether a no_topic_probe / no_memory_mention boundary forbids probing here."""
    if boundary.boundary_rule not in ("no_topic_probe", "no_memory_mention"):
        return False
    if boundary.target in (None, "all_topics", "current_topic"):
        return True
    combined = f"{question_text or ''} {current_text}".strip()
    return bool(combined and targets_overlap(boundary.target, combined))


def _resolve_action_obj(config, action_id: str, kind: str | None = None):
    if config is None:
        return None
    if kind == "exercise" or action_id in config.exercises:
        return config.exercises.get(action_id)
    resolve = getattr(config, "resolve_card_id", None)
    resolved_id = resolve(action_id) if resolve else action_id
    return config.cards.get(resolved_id)


def advice_blocked_for_turn(
    policy: TurnPolicyFrame,
    current_text: str,
    *,
    recent_text: str = "",
    action_id: str | None = None,
    action_kind: str | None = None,
    config=None,
) -> bool:
    """Scoped check for whether active boundaries or plan.avoid block advice/offers this turn."""
    action_obj = _resolve_action_obj(config, action_id, action_kind) if action_id else None
    for boundary in policy.active_boundaries:
        if boundary.boundary_rule == "no_advice" and no_advice_blocks_action(
            boundary.target, action_obj, current_text, recent_text
        ):
            return True
    for item in policy.avoid:
        if item.kind == "no_advice" and no_advice_blocks_action(
            item.target, action_obj, current_text, recent_text
        ):
            return True
    return False


def build_turn_policy(
    state,
    plan,
    bundle,
    all_items,
    *,
    current_text: str = "",
    recent_text: str = "",
    config=None,
    now=None,
):
    boundaries = effective_boundaries(bundle)
    reason = plan_invalid_reason(plan, state, bundle.model_dump(), all_items, now)
    objective = "quiet" if state.stage.value == "quiet" else "listen"
    guidance = ()
    actions = ()
    avoid = ()
    question = None
    if not reason:
        checked = plan.checked_through_user_index >= state.user_turns
        objective = plan.objective if checked else "listen"
        guidance = (
            plan.response_guidance
            if checked
            else ("承接当前原话，先理解感受，不引入旧话题或新建议。",)
        )
        reason = "verified" if checked else "unchecked_delta_non_action"
        actions = tuple(a.action_id for a in plan.candidate_actions) if checked else ()
        if checked:
            avoid, question = plan.avoid, plan.open_question
            no_advice_targets = [a.target for a in avoid if a.kind == "no_advice"]
            if no_advice_targets:
                actions = tuple(
                    identifier
                    for identifier in actions
                    if not any(
                        no_advice_blocks_action(
                            t,
                            _resolve_action_obj(config, identifier),
                            current_text,
                            recent_text,
                        )
                        for t in no_advice_targets
                    )
                )
                if (
                    not actions
                    and objective not in NON_ACTION
                    and any(
                        no_advice_blocks_text(t, current_text, recent_text)
                        for t in no_advice_targets
                    )
                ):
                    objective = "listen"
            actions = tuple(
                identifier
                for identifier in actions
                if not any(
                    a.kind == "no_repeat_offer" and a.target in (None, identifier) for a in avoid
                )
            )
    no_advice_boundaries = [b for b in boundaries if b.boundary_rule == "no_advice"]
    if no_advice_boundaries:
        actions = tuple(
            identifier
            for identifier in actions
            if not any(
                no_advice_blocks_action(
                    b.target,
                    _resolve_action_obj(config, identifier),
                    current_text,
                    recent_text,
                )
                for b in no_advice_boundaries
            )
        )
        if (
            not actions
            and objective not in NON_ACTION
            and any(
                no_advice_blocks_text(b.target, current_text, recent_text)
                for b in no_advice_boundaries
            )
        ):
            objective = "listen"
    if question and any(boundary_blocks_probe(b, question, current_text) for b in boundaries):
        question = None
    return TurnPolicyFrame(
        effective_support_plan_id=plan.plan_id
        if plan and reason in ("verified", "unchecked_delta_non_action")
        else None,
        effective_support_plan_version=plan.version
        if plan and reason in ("verified", "unchecked_delta_non_action")
        else None,
        objective=objective,
        response_guidance=guidance,
        avoid=avoid,
        open_question=question,
        active_boundaries=tuple(
            MemoryCandidate.model_validate(b.model_dump(include=set(MemoryCandidate.model_fields)))
            for b in boundaries
        ),
        allowed_action_ids=actions,
        memory_projection=bundle,
        selection_reason=reason or "safe_default",
        checked_through_user_index=plan.checked_through_user_index if plan else 0,
    )


def exercise_eligibility(
    plan, frame, new_inputs, matches, *, current_text: str = "", recent_text: str = "", config=None
):
    """Return allowed IDs and whether conditions are current, including consent-only deltas."""
    if plan is None or frame.selection_reason not in ("verified", "unchecked_delta_non_action"):
        return (), False
    for row in new_inputs:
        signals = json.loads(row["signals"])
        if (
            not matches("agree", row["text"])
            or signals.get("emotion") not in (None, "NEUTRAL")
            or set(signals.get("events", ())) - {"Speech"}
        ):
            return (), False
    no_advice_targets = [
        b.target for b in frame.active_boundaries if b.boundary_rule == "no_advice"
    ] + [item.target for item in plan.avoid if item.kind == "no_advice"]
    allowed = tuple(
        action.action_id
        for action in plan.candidate_actions
        if action.kind == "exercise"
        and action.when_met
        and not action.exclusions_present
        and not any(
            no_advice_blocks_action(
                target,
                _resolve_action_obj(config, action.action_id, "exercise"),
                current_text,
                recent_text,
            )
            for target in no_advice_targets
        )
        and not any(
            item.kind == "no_repeat_offer" and item.target in (None, action.action_id)
            for item in plan.avoid
        )
    )
    return allowed, True


def prompt_projection(frame, budget=1200):
    from companion.memory.service import MemoryService

    value = {
        "objective": frame.objective,
        "guidance": frame.response_guidance,
        "avoid": [a.model_dump() for a in frame.avoid],
        "open_question": frame.open_question,
        "selection": frame.selection_reason,
        "boundaries": [
            {"rule": b.boundary_rule, "target": b.target, "scope": b.scope}
            for b in frame.active_boundaries
        ],
        "allowed_actions": frame.allowed_action_ids,
        "memory": [MemoryService.project(m) for m in frame.memory_projection.items],
    }
    while value["memory"] and estimate_tokens(value) > budget:
        value["memory"].pop()
    while value["guidance"] and estimate_tokens(value) > budget:
        value["guidance"] = value["guidance"][:-1]
    # Boundaries are mandatory. If extremely many exist, retain a conservative typed union.
    if estimate_tokens(value) > budget:
        value["boundaries"] = [
            {"rule": rule, "target": "all_topics", "scope": "current_turn"}
            for rule in sorted({b["rule"] for b in value["boundaries"]})
        ]
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
