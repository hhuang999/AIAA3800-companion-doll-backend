"""Regression tests covering Stage 1-3 upgrades: scoped boundaries, concepts, Talker, and fast-path."""

import asyncio
import io
import threading
import wave
from concurrent.futures import Future
from datetime import timedelta

import pytest
from companion.adapters.output import RecordingOutputPort
from companion.adapters.xiaozhi.output import XiaozhiOutputPort, encode_audio_in_memory
from companion.cognition.base import EvidenceRef, utcnow
from companion.cognition.models import (
    CandidateAction,
    PlanCandidate,
    SupportPlan,
    TurnPolicyFrame,
)
from companion.cognition.policy import build_turn_policy
from companion.core.api import CompanionCore
from companion.core.models import (
    OutputEvent,
    PlaybackSegment,
    SessionState,
    Snapshot,
    Stage,
    TurnContext,
    TurnSignals,
)
from companion.core.state_machine import StateMachine
from companion.core.talker import Talker
from companion.llm.fake import FakeLLM
from companion.memory.models import MemoryBundle, MemoryCandidate, MemoryItem
from companion.memory.service import MemoryService


def _fake_wav(samples: int = 3200, rate: int = 16000) -> bytes:
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(rate)
        wav.writeframes(b"\x00\x00" * samples)
    return buf.getvalue()


def test_scoped_boundary_allows_unrelated_bedtime_exercise(config, store):
    core = CompanionCore(config, store, FakeLLM())
    port = RecordingOutputPort(core.on_playback_event, auto_complete=False)
    core.bind_output("s", "u", port)
    try:
        t1 = core.on_input("s", "1", "以后不要问我数学考试的事", TurnSignals())
        for event in core.respond("s", t1):
            core.dispatch(event)
        assert core.wait_idle()
        boundaries = [m for m in store.memory_items("u") if m.kind == "interaction_boundary"]
        assert any(
            b.boundary_rule == "no_topic_probe" and b.target == "数学考试" for b in boundaries
        )

        core.llm.exercise_id = "bedtime"
        t2 = core.on_input("s", "2", "我现在准备睡了，想试一个睡前暂停练习", TurnSignals())
        for event in core.respond("s", t2):
            core.dispatch(event)
        assert core.wait_idle()
        assert core.sessions["s"].state.pending_offer is not None

        t3 = core.on_input("s", "3", "那行吧，你讲讲看", TurnSignals())
        for event in core.respond("s", t3):
            core.dispatch(event)
        assert port.events[-1].purpose == "exercise_offer"

        t4 = core.on_input("s", "4", "可以呀试试", TurnSignals())
        for event in core.respond("s", t4):
            core.dispatch(event)
        assert port.events[-1].type == "exercise_plan"
        assert core.sessions["s"].state.mode == "exercise"
    finally:
        core.close()


def test_scoped_no_advice_blocks_matching_card_only(config):
    state = SessionState(session_id="s", user_key="u", user_turns=1, latest_turn_id=1)
    ref = EvidenceRef(kind="user_turn", id=1, claim="原话")
    boundary = MemoryItem(
        memory_id="b1",
        user_key="u",
        version=1,
        source_cursor=1,
        kind="interaction_boundary",
        key="no_advice:选科",
        value="今天先别给选科建议",
        boundary_rule="no_advice",
        target="选科",
        epistemic_status="stated",
        source_refs=(ref,),
    )
    bundle = MemoryBundle(boundaries=(boundary,))
    plan = PlanCandidate(
        objective="invite_action",
        understanding="考虑策略选择",
        evidence=(ref,),
    )
    support_plan = SupportPlan(
        **plan.model_dump(exclude={"candidate_actions"}),
        candidate_actions=(
            CandidateAction(
                action_id="values_exploration",
                kind="card",
                evidence=(ref,),
                when_met=True,
                exclusions_present=False,
            ),
            CandidateAction(
                action_id="worry_parking",
                kind="card",
                evidence=(ref,),
                when_met=True,
                exclusions_present=False,
            ),
        ),
        plan_id="p1",
        version=1,
        candidate_version=1,
        user_key="u",
        session_id="s",
        topic_revision=0,
        source_turn_id=1,
        source_user_index=1,
        checked_through_user_index=1,
        policy_revision=0,
        base_plan_version=0,
        boundary_revision=0,
        created_at=utcnow(),
        valid_until=utcnow() + timedelta(minutes=5),
        max_user_turn_delta=2,
        review_status="approved",
    )
    policy_values = build_turn_policy(
        state,
        support_plan,
        bundle,
        bundle.boundaries,
        current_text="我好纠结高一怎么选科",
        config=config,
    )
    assert "values_exploration" not in policy_values.allowed_action_ids
    policy_sleep = build_turn_policy(
        state,
        support_plan,
        bundle,
        bundle.boundaries,
        current_text="准备睡了有点睡不着",
        config=config,
    )
    assert "worry_parking" in policy_sleep.allowed_action_ids


def test_concept_cluster_retrieval_matches_parent_and_exam_synonyms(store, config):
    core = CompanionCore(config, store, FakeLLM())
    try:
        state = SessionState(session_id="s", user_key="u")
        store.create_session(state)
        t1 = store.add_input(state, "1", "父母总问我模考排名让我压力好大", "user", TurnSignals())
        memory = MemoryService(store)
        memory.commit(
            (
                MemoryCandidate(
                    kind="episodic_event",
                    key="家庭排名压力",
                    value="父母比较模考成绩带来压迫感",
                    source_refs=(EvidenceRef(kind="user_turn", id=t1, claim="原话"),),
                ),
            ),
            state,
            t1,
        )
        bundle = memory.retrieve(state, "爸妈今天又一直唠叨我分数")
        assert any(item.key == "家庭排名压力" for item in bundle.items)
        boundary = memory.explicit_boundary("以后别再问我的月考成绩", state, t1)
        assert boundary is not None and boundary.boundary_rule == "no_topic_probe"
        generic = memory.explicit_boundary("以后不要再聊英语演讲那件事了", state, t1)
        assert generic is not None and "英语" in (generic.target or "")
        non_boundary = memory.explicit_boundary(
            "高一马上要选科分班了，还不想一下子定死未来，想找个能查清楚的小问题，怎么办？",
            state,
            t1,
        )
        assert non_boundary is None
    finally:
        core.close()


@pytest.mark.parametrize(
    "phrase",
    ["那行吧，你讲讲看", "可以呀试试", "好啊那我听听", "行呀说说看"],
)
def test_colloquial_consent_matches_while_negations_fail(config, phrase):
    machine = StateMachine(config)
    assert machine.matches("agree", phrase)
    assert not machine.matches("agree", "还行吧不用了")
    assert not machine.matches("agree", "不是我不愿意试，算了")


def test_dialogue_clarification_does_not_invalidate_factual_memory(config, store):
    core = CompanionCore(config, store, FakeLLM())
    core.bind_output("s", "u", RecordingOutputPort(core.on_playback_event))
    try:
        core.on_input("s", "1", "我叫小林，不是故意不刷题", TurnSignals())
        core.on_input("s", "2", "我不是担心这道题，我是烦他们一直比排名", TurnSignals())
        active_names = [
            m.value for m in store.memory_items("u") if m.key == "nickname" and m.status == "active"
        ]
        assert active_names == ["小林"]

        core.on_input("s", "3", "你记错了，我叫小琳", TurnSignals())
        active_after = [
            m.value for m in store.memory_items("u") if m.key == "nickname" and m.status == "active"
        ]
        assert active_after == ["小琳"]
    finally:
        core.close()


def test_talker_severe_rail_orphan_guard_early_clause_and_dynamic_emoji(config):
    llm = FakeLLM(
        streams=[
            "你肯定抑郁症的药有问题。而且这只是我的想法。",
            "先喘口气慢慢缓下来，其实你已经撑过很多天啦。接下来只挑一个小点看。",
        ]
    )
    frame = TurnPolicyFrame(objective="low_energy_companionship")
    context = TurnContext(
        session_id="s",
        turn_id=1,
        generation=1,
        text="学不动了好累",
        kind="user",
        stage=Stage.comfort,
        mode="normal",
        snapshot=Snapshot(session_id="s", user_key="u"),
        policy_frame=frame,
        signals=TurnSignals(emotion="SAD"),
        t0=0.0,
    )
    talker = Talker(config, llm)
    v1 = []
    out1 = list(talker.run(context, [], threading.Event(), {}, v1))
    assert out1 == [(config.stages["comfort"]["fallback"], "😔")]
    assert "rail_medical" in v1

    v2 = []
    out2 = list(talker.run(context, [], threading.Event(), {}, v2))
    assert len(out2) == 3
    assert out2[0] == ("先喘口气慢慢缓下来，", "😔")
    assert all(emoji == "😔" for _, emoji in out2)

    llm_orphan = FakeLLM(
        streams=["一切都会好的。但是你不用担心。", "你一定行。嗯，我在这里听你慢慢说。"]
    )
    talker_orphan = Talker(config, llm_orphan)
    v3 = []
    out3 = list(talker_orphan.run(context, [], threading.Event(), {}, v3))
    assert out3 == [(config.stages["comfort"]["fallback"], "😔")]
    assert "rail_cliche" in v3 and "rail_orphan_fragment" in v3

    listen_ctx = context.model_copy(
        update={
            "stage": Stage.explore,
            "signals": TurnSignals(),
            "policy_frame": TurnPolicyFrame(objective="attuned_listen"),
        }
    )
    v4 = []
    out4 = list(talker_orphan.run(listen_ctx, [], threading.Event(), {}, v4))
    assert out4 == [("嗯，我在这里听你慢慢说。", "😌")]
    assert "rail_cliche" in v4


def test_orchestrator_uses_fast_path_for_non_action_and_drain_brief_preserves_primary(
    config, store
):
    core = CompanionCore(config, store, FakeLLM())
    core.bind_output("s", "u", RecordingOutputPort(core.on_playback_event))
    try:
        core.on_input("s", "1", "今天真的好累，只想说说不想要办法", TurnSignals())
        assert core.wait_idle()
        plan = store.active_support_plan("s")
        assert plan is not None and plan.review_status == "fast_path_non_action"
        assert not [r for r in core.llm.requests if r["role"] == "critic"]

        core.on_input("s", "2", "那道数学题卡住了，怎么办", TurnSignals())
        assert core.wait_idle()
        plan2 = store.active_support_plan("s")
        assert plan2 is not None and plan2.review_status == "approved"
        assert any(r["role"] == "critic" for r in core.llm.requests)

        failing_brief: Future = Future()
        failing_brief.set_exception(TimeoutError("brief timed out"))
        cancel = threading.Event()
        core.cognition._drain_brief(failing_brief, cancel)
    finally:
        core.close()


def test_in_memory_wav_encode_and_container_guard():
    with pytest.raises(ValueError, match="Unsupported in-memory audio container"):
        encode_audio_in_memory(b"NOT_AUDIO")
    pytest.importorskip("opuslib_next")
    wav_bytes = _fake_wav(3200, 16000)
    packets = encode_audio_in_memory(wav_bytes)
    assert len(packets) >= 3 and all(isinstance(p, bytes) and p for p in packets)


def test_short_phrase_packet_cache_skips_repeat_tts(tmp_path):
    class StubTransport:
        def __init__(self):
            self.encodes = 0

        async def encode(self, data):
            self.encodes += 1
            return [b"opus-frame"]

        async def stop(self):
            return None

    class StubTTS:
        def __init__(self):
            self.calls = 0

        def cache_key(self, text):
            return f"k:{text}"

        def synthesize(self, text):
            self.calls += 1
            return b"RIFFfake"

        def duration(self, data):
            return 0.5

    async def exercise():
        loop = asyncio.get_running_loop()
        tts = StubTTS()
        transport = StubTransport()
        port = XiaozhiOutputPort(loop, lambda _e: None, tts, transport, tmp_path)
        ev1 = OutputEvent(
            output_id="o1", session_id="s", turn_id=1, generation=1, text="好，先听你说。"
        )
        ev2 = OutputEvent(
            output_id="o2", session_id="s", turn_id=2, generation=2, text="好，先听你说。"
        )
        p1, d1 = await port._prepare(ev1, PlaybackSegment(text=ev1.text), False)
        p2, d2 = await port._prepare(ev2, PlaybackSegment(text=ev2.text), False)
        await port.close()
        assert (p1, d1) == (p2, d2)
        assert tts.calls == 1 and transport.encodes == 1

    asyncio.run(exercise())


def test_identity_name_concept_retrieves_only_when_raised_user_name(config, store):
    memory = MemoryService(store)
    state = SessionState(session_id="s_name", user_key="u_name")
    store.create_session(state)
    tid = store.add_input(state, "inp-2", "你记错了，我是小琳", "user", TurnSignals())
    cand = MemoryCandidate(
        kind="fact_preference",
        key="user_name",
        value="小琳",
        scope="persistent",
        mention_policy="only_when_raised",
        source_refs=(EvidenceRef(kind="user_turn", id=str(tid), claim="更正名字为小琳"),),
    )
    results = memory.commit((cand,), state, tid, {("user_turn", str(tid))})
    assert results and results[0].startswith("accepted:")

    bundle = memory.retrieve(state, "你还记得我上次让你怎么叫我吗？")
    assert any(item.value == "小琳" for item in bundle.items)


def test_talker_keeps_closing_quote_at_sentence_limit(config):
    llm = FakeLLM(
        streams=[
            "原来你是不小心带回家了。难怪他误会。要不试试说：“抱歉让你担心了。”",
        ]
    )
    frame = TurnPolicyFrame(objective="invite_action", allowed_action_ids=("safe_communication",))
    context = TurnContext(
        session_id="s_q",
        turn_id=1,
        generation=1,
        text="其实那天带回家了",
        kind="user",
        stage=Stage.action,
        mode="normal",
        card_id="safe_communication",
        snapshot=Snapshot(session_id="s_q", user_key="u_q"),
        policy_frame=frame,
        signals=TurnSignals(),
        t0=0.0,
    )
    out = list(Talker(config, llm).run(context, [], threading.Event(), {}, [], sentence_limit=3))
    assert len(out) == 3
    assert out[2][0].endswith("”")


def test_interrupted_exercise_refusal_and_sleep_close_clear_resume_while_noise_keeps_waiting(
    config,
):
    machine = StateMachine(config)
    snap = Snapshot(
        session_id="s_ex", user_key="u_ex", offer_exercise=True, preferred_exercise="breathing_60s"
    )

    st_refuse = SessionState(
        session_id="s_ex",
        user_key="u_ex",
        stage=Stage.permission,
        resume_script_id="breathing_60s",
        resume_index=2,
    )
    r_refuse = machine.apply_rules(
        st_refuse, "刚才那样留意呼吸有点别扭，不想继续了。", TurnSignals(), snap
    )
    assert r_refuse.directive is None
    assert st_refuse.resume_script_id is None and "breathing_60s" in st_refuse.exercises_refused

    st_sleep = SessionState(
        session_id="s_ex2",
        user_key="u_ex",
        stage=Stage.permission,
        resume_script_id="bedtime",
        resume_index=1,
    )
    r_sleep = machine.apply_rules(st_sleep, "行啦，今晚就歇这儿。", TurnSignals(), snap)
    assert (
        r_sleep.directive == "quiet"
        and st_sleep.stage == Stage.quiet
        and st_sleep.resume_script_id is None
    )

    st_noise = SessionState(
        session_id="s_ex3",
        user_key="u_ex",
        stage=Stage.permission,
        resume_script_id="breathing_60s",
        resume_index=1,
    )
    r_noise = machine.apply_rules(st_noise, "刚才有声音", TurnSignals(), snap)
    assert r_noise.directive == "waiting_card" and st_noise.resume_script_id == "breathing_60s"


def test_risk_watch_does_not_overwrite_active_ask_for_help_plan(config, store):
    from companion.core.models import RiskResult

    llm = FakeLLM()
    core = CompanionCore(config, store, llm)
    core.bind_output("s_rw", "u_rw", RecordingOutputPort(core.on_playback_event))
    try:
        tid1 = core.on_input(
            "s_rw", "1", "爸妈又拿成绩比，我暂时不想争吵，胸口又堵，怎么办？", TurnSignals()
        )
        for ev in core.respond("s_rw", tid1):
            core.dispatch(ev)
        assert core.wait_idle()
        plan_before = store.active_support_plan("s_rw")
        assert plan_before is not None and plan_before.objective == "invite_action"

        # Delayed risk_watch on the already-deliberated turn or on permission agree must not enqueue overwrite.
        before_jobs = len(store.query("SELECT job_id FROM cognitive_jobs WHERE session_id='s_rw'"))
        core._risk_result(
            "s_rw", tid1, RiskResult(level="watch", source="model", category="other"), 120.0
        )
        tid2 = core.on_input("s_rw", "2", "好，你说。", TurnSignals())
        for ev in core.respond("s_rw", tid2):
            core.dispatch(ev)
        core._risk_result(
            "s_rw", tid2, RiskResult(level="watch", source="model", category="other"), 90.0
        )
        assert core.wait_idle()
        after_jobs = len(store.query("SELECT job_id FROM cognitive_jobs WHERE session_id='s_rw'"))
        assert after_jobs == before_jobs
        assert core.sessions["s_rw"].state.stage == Stage.action
    finally:
        core.close()


def test_resolve_opening_skips_onboarding_when_user_already_spoke(config, store):
    from companion.core.helpers import resolve_opening

    llm = FakeLLM()
    core = CompanionCore(config, store, llm)
    core.bind_output("s1", "u_hist", RecordingOutputPort(core.on_playback_event))
    try:
        tid = core.on_input("s1", "1", "我叫小琳，今天好烦。", TurnSignals())
        for ev in core.respond("s1", tid):
            core.dispatch(ev)
        assert core.wait_idle()
        core.on_session_end("s1", "reconnect")
        assert core.wait_idle()

        core.bind_output("s2", "u_hist", RecordingOutputPort(core.on_playback_event))
        _, purpose, _ = resolve_opening(core, core.sessions["s2"].state, "s2")
        assert purpose == "opening"
        assert core.store.onboarding_done("u_hist")
    finally:
        core.close()
