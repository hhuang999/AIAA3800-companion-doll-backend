import json
import uuid

import pytest
from companion.adapters.output import RecordingOutputPort
from companion.cognition.models import SituationAssessment
from companion.content.catalog import StrategyCatalog
from companion.core.api import CompanionCore
from companion.core.models import SessionState, Stage, TurnSignals
from companion.llm.fake import FakeLLM

CASES = [
    ("concrete_step", "academic", "rumination", (), "我总想数学函数那道题卡住的地方，怎么办"),
    ("exam_steadying", "academic", "sleep", (), "明早模考我心慌手心出汗脑子空白，怎么稳住"),
    ("kind_self_talk", "self", "self_criticism", (), "总觉得一次考砸就是整个人不行，怎么办"),
    (
        "comparison_reframe",
        "social_evaluative",
        "self_criticism",
        (),
        "排名榜一出来同桌刷得那么快我掉队了，怎么办",
    ),
    (
        "expectation_boundary",
        "relationship",
        None,
        (),
        "爸妈总拿成绩跟亲戚比我不想吵架，怎么办",
    ),
    (
        "safe_communication",
        "relationship",
        None,
        ("safe_contact",),
        "我想跟不会伤害我的同桌解释误会，怎么办",
    ),
    (
        "safe_support",
        "relationship",
        "loneliness",
        (),
        "我觉得孤独又怕被评价，想找安全的人聊聊，怎么办",
    ),
    (
        "values_exploration",
        "future",
        None,
        (),
        "高一选科好迷茫还不想定死专业，怎么办",
    ),
    ("worry_parking", "academic", "sleep", ("bedtime",), "准备睡了还在担心明天的考试，怎么办"),
]


@pytest.mark.parametrize("identifier,pressure,pathway,contexts,text", CASES)
def test_each_course_strategy_filters_refusal_and_exclusions(
    config, identifier, pressure, pathway, contexts, text
):
    assessment = SituationAssessment(
        expressed_need="solve",
        pressure_types=(pressure,),
        pathway_signals=(pathway,) if pathway else (),
        readiness="medium",
        support_constraints=contexts,
    )
    state = SessionState(session_id="s", user_key="u")
    catalog = StrategyCatalog(config)

    def decision(value=assessment):
        return next(
            d for d in catalog.select(value, state, text).decisions if d.strategy_id == identifier
        )

    assert decision().eligible
    assert not decision(assessment.model_copy(update={"expressed_need": "listen"})).eligible
    assert not decision(assessment.model_copy(update={"emotion_intensity": "high"})).eligible
    card = config.cards[identifier]
    if card.protocol.required_contexts:
        assert (
            "missing_required_context"
            in decision(assessment.model_copy(update={"support_constraints": ()})).reasons
        )
    if card.protocol.excluded_contexts:
        assert (
            "context_excluded"
            in decision(
                assessment.model_copy(
                    update={"support_constraints": (*contexts, card.protocol.excluded_contexts[0])}
                )
            ).reasons
        )
    state.cards_refused.add(identifier)
    assert "refused_this_session" in decision().reasons


@pytest.mark.parametrize("identifier,pressure,pathway,contexts,text", CASES)
def test_each_strategy_runs_roles_permission_step_feedback_and_exit(
    config, store, identifier, pressure, pathway, contexts, text
):
    # Intentional forced-candidate coverage is distinct from natural-selection evaluation.
    config.cards = {identifier: config.cards[identifier]}

    def analysis(payload):
        latest = next(row for row in reversed(payload["history"]) if row["role"] == "user")
        return {
            "facts": [
                {
                    "statement": latest["text"],
                    "evidence": [
                        {"kind": "user_turn", "id": latest["id"], "claim": "合成情境原话"}
                    ],
                }
            ],
            "expressed_need": "solve",
            "pressure_types": [pressure],
            "pathway_signals": [pathway] if pathway else [],
            "readiness": "medium",
            "support_constraints": list(contexts),
        }

    fake = FakeLLM(roles={"analysis": [analysis]})
    core = CompanionCore(config, store, fake)
    port = RecordingOutputPort(core.on_playback_event)
    core.bind_output("s", "u", port)

    def say(message):
        turn = core.on_input("s", uuid.uuid4().hex, message, TurnSignals())
        events = list(core.respond("s", turn))
        for event in events:
            core.dispatch(event)
        return turn, events

    try:
        say(text)
        assert core.sessions["s"].state.stage == Stage.permission
        assert core.sessions["s"].state.card_in_use is None
        assert core.wait_idle()
        plan = store.active_support_plan("s")
        assert plan and plan.candidate_actions[0].action_id == identifier
        _turn, events = say("好，你说")
        assert core.sessions["s"].state.card_in_use == identifier
        assert (
            events
            and "".join(e.text for e in events) == fake.content["strategy_replies"][identifier][0]
        )
        assert events[0].support.identifier == identifier
        assert events[0].support.version == config.cards[identifier].protocol.version
        assert events[0].support.step == 1
        assert store.query("SELECT * FROM card_usage WHERE card_id=?", (identifier,))
        say("刚才这个办法没帮助，停一下")
        state = core.sessions["s"].state
        assert state.card_in_use is None and identifier in state.cards_refused
        feedback = [
            json.loads(r["data"])
            for r in store.query(
                "SELECT data FROM interaction_events WHERE event_type='explicit_feedback'"
            )
        ]
        assert feedback[-1]["payload"]["valence"] == "negative"
        assert feedback[-1]["payload"]["attribution"] == "explicit"
        assert feedback[-1]["payload"]["support"]["identifier"] == identifier
        memories = [m for m in store.memory_items("u") if m.kind == "support_experience"]
        assert memories and memories[0].support.identifier == identifier
        assert memories[0].feedback_valence == "negative"
        forged = memories[0].model_copy(
            update={"support": memories[0].support.model_copy(update={"version": "invented"})}
        )
        from companion.memory.models import MemoryCandidate

        candidate = MemoryCandidate.model_validate(
            forged.model_dump(include=set(MemoryCandidate.model_fields))
        )
        result = core.cognition.memory.commit((candidate,), state, state.latest_turn_id)
        assert result[0].startswith("rejected:Support attribution")
        assert core.wait_idle()
        assert state.card_in_use is None
    finally:
        core.close()


def test_legacy_s16_resolves_to_concrete_step(config):
    from datetime import date

    from companion.core.models import (
        Assessment,
        CardEvidence,
        CardSelection,
        ReasonerOutput,
        SeekerState,
    )
    from companion.core.validator import Validator

    assert config.resolve_card_id("S16") == "concrete_step"
    output = ReasonerOutput(
        assessment=Assessment(
            pathway_signals=("rumination",), seeker_state=SeekerState(readiness="medium")
        ),
        cards=CardSelection(
            allowed=("S16",),
            preferred="S16",
            evidence=(
                CardEvidence(
                    card_id="S16", when_met=True, exclusions_present=False, source_turn_ids=(1,)
                ),
            ),
        ),
    )
    validated, rejected = Validator(config).validate(
        output, SessionState(session_id="s", user_key="u"), {1}, date.today()
    )
    assert not rejected
    assert validated.cards.allowed == ("concrete_step",)
    assert validated.cards.preferred == "concrete_step"
