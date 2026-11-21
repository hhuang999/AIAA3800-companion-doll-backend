"""Stateless helpers for Talker presentation, opening selection, and session context."""

from companion.cognition.policy import effective_boundaries
from companion.memory.concepts import targets_overlap

from .models import Stage, TurnContext


def resolve_emoji(context: TurnContext, card: object | None, config: object) -> str:
    """Map current dialogue context, nonverbal signals, and policy objective to an allowed emoji."""
    emojis = config.rules["emojis"]
    allowed = set(emojis["allowed"])
    default = emojis["default"]

    def pick(candidate: str) -> str:
        return candidate if candidate in allowed else default

    if card is not None:
        return pick(card.emo)
    if context.kind == "idle_end" or context.stage == Stage.closing:
        return pick("😌")
    if context.kind == "wake":
        return pick("🙂")
    objective = context.policy_frame.objective
    if context.stage == Stage.quiet or objective in ("quiet", "quiet_presence"):
        return pick("😌")
    if (
        context.stage == Stage.comfort
        or "Cry" in context.signals.events
        or context.signals.emotion in ("SAD", "FEARFUL")
        or objective in ("comfort", "low_energy_companionship")
    ):
        return pick("😔")
    if context.stage == Stage.permission or objective in (
        "clarify",
        "tentative_reflect",
        "invite_action",
        "invite_exercise",
    ):
        return pick("🤔")
    if context.signals.emotion == "HAPPY":
        return pick("🙂")
    if objective in ("attuned_listen", "reflect", "listen"):
        return pick("😌")
    return default


def resolve_opening(core: object, state: object, session_id: str) -> tuple[str, str, int | None]:
    """Select onboarding, boundary-checked followup, or greeting for wake inputs."""
    if not core.store.onboarding_done(state.user_key):
        has_prior = bool(
            core.store.query(
                "SELECT 1 FROM turns t JOIN sessions s ON s.session_id=t.session_id "
                "WHERE s.user_key=? AND t.role='user' LIMIT 1",
                (state.user_key,),
            )
        )
        if has_prior:
            core.store.mark_onboarding(state.user_key)
        else:
            return core.config.persona["onboarding"], "onboarding", None
    followup = core.store.reserve_followup(state.user_key, session_id, core.today())
    if followup:
        boundaries = effective_boundaries(core.cognition.memory.retrieve(state, "", proactive=True))
        if any(
            b.target == "current_topic"
            or (b.target and targets_overlap(b.target, followup["content"]))
            for b in boundaries
        ):
            with core.store.transaction() as db:
                db.execute(
                    "UPDATE followups SET status='pending',reservation_session_id=NULL "
                    "WHERE id=? AND status='reserved'",
                    (followup["id"],),
                )
            followup = None
    text = (
        core.config.persona["followup"].format(content=followup["content"])
        if followup
        else core.config.persona["greeting"]
    )
    return text, "opening", followup["id"] if followup else None


def recent_user_context(store: object, session_id: str, prior_turn_id: int) -> str:
    """Return recent user utterances in this session for scoped boundary disambiguation."""
    rows = store.query(
        "SELECT text FROM turns WHERE session_id=? AND role='user' AND id<? ORDER BY id DESC LIMIT 3",
        (session_id, prior_turn_id),
    )
    return " ".join(row["text"] for row in reversed(rows))
