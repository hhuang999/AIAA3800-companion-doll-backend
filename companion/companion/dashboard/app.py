"""Read-only Warm Daylight runtime observatory for Companion."""

import argparse
import html
import json
import sqlite3
import statistics
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st

st.set_page_config(
    page_title="小伴 Companion · 运行观测台",
    page_icon="●",
    layout="wide",
)

THEME_CSS = """
<style>
  :root {
    --bg: #F7F3EC;
    --surface: #EFEAE0;
    --card: #FFFFFF;
    --dark: #252C27;
    --ink: #242824;
    --muted: #5A6058;
    --line: #D5D8D0;
    --accent: #BF471B;
    --accent-soft: #FBECE6;
    --olive: #3B5246;
    --olive-soft: #E9EFEA;
  }
  .stApp {
    background-color: var(--bg);
    color: var(--ink);
  }
  .te-banner {
    background: var(--card);
    border: 1px solid var(--line);
    border-left: 4px solid var(--accent);
    border-radius: 8px;
    padding: 14px 18px;
    margin-bottom: 14px;
  }
  .te-kicker {
    font-family: Consolas, ui-monospace, monospace;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.12em;
    color: var(--accent);
    margin: 0 0 4px;
  }
  .te-title {
    font-size: 20px;
    font-weight: 700;
    margin: 0 0 4px;
    color: var(--ink);
  }
  .te-sub {
    font-size: 13px;
    color: var(--muted);
    margin: 0;
  }
  .te-sub code {
    overflow-wrap: anywhere;
  }
  .te-kpi-card {
    background: var(--card);
    border: 1px solid var(--line);
    border-radius: 8px;
    padding: 10px 12px;
    margin-bottom: 10px;
  }
  .te-kpi-label {
    font-family: Consolas, ui-monospace, monospace;
    font-size: 11px;
    font-weight: 700;
    color: var(--muted);
    letter-spacing: 0.06em;
    margin-bottom: 4px;
  }
  .te-kpi-val {
    font-size: 16px;
    font-weight: 700;
    color: var(--ink);
  }
  .te-pill-row {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin: 6px 0 14px;
  }
  .te-pill {
    display: inline-block;
    padding: 3px 9px;
    border-radius: 4px;
    font-family: Consolas, ui-monospace, monospace;
    font-size: 11.5px;
    font-weight: 700;
    border: 1px solid var(--line);
    background: var(--surface);
    color: var(--ink);
  }
  .te-pill-accent {
    background: var(--accent-soft);
    color: var(--accent);
    border-color: #E8B5A2;
  }
  .te-pill-olive {
    background: var(--olive-soft);
    color: var(--olive);
    border-color: #BFD0C4;
  }
  .te-lane-card {
    background: var(--card);
    border: 1px solid var(--line);
    border-radius: 8px;
    padding: 11px 14px;
    margin-bottom: 10px;
  }
  .te-lane-head {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 8px;
    margin-bottom: 6px;
  }
  .te-lane-step {
    font-family: Consolas, ui-monospace, monospace;
    font-size: 11px;
    font-weight: 700;
    color: var(--accent);
    letter-spacing: 0.08em;
  }
  .te-lane-body {
    font-size: 13.5px;
    line-height: 1.55;
    color: var(--ink);
  }
  .te-quote {
    margin-top: 6px;
    padding: 6px 10px;
    background: var(--surface);
    border-left: 3px solid var(--olive);
    border-radius: 4px;
    font-size: 12.5px;
    color: var(--ink);
  }
</style>
"""


def parse_args() -> Path:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--db", type=Path, default=Path("data/companion.db"))
    known, _ = parser.parse_known_args()
    return known.db


def read_rows(db_path: Path, sql: str, params: tuple = ()) -> list[dict]:
    if not db_path.exists():
        return []
    con = sqlite3.connect(f"file:{db_path.resolve()}?mode=ro", uri=True, timeout=5.0)
    con.row_factory = sqlite3.Row
    try:
        return [dict(row) for row in con.execute(sql, params).fetchall()]
    except sqlite3.OperationalError:
        return []
    finally:
        con.close()


def mark_handled(db_path: Path, event_id: int) -> None:
    con = sqlite3.connect(db_path, timeout=5.0)
    try:
        with con:
            con.execute(
                "UPDATE risk_events SET handled=1, handled_at=? WHERE id=?",
                (datetime.now(timezone.utc).isoformat(), event_id),
            )
    finally:
        con.close()


def parse_json(raw: str | None, fallback: object = None) -> object:
    if not raw:
        return fallback
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return fallback


def percentile_90(values: list[float]) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    idx = min(len(ordered) - 1, int(len(ordered) * 0.9))
    return ordered[idx]


def job_duration_ms(job: dict) -> float | None:
    if job.get("started_at") and job.get("finished_at"):
        t0 = datetime.fromisoformat(str(job["started_at"]).replace("Z", "+00:00"))
        t1 = datetime.fromisoformat(str(job["finished_at"]).replace("Z", "+00:00"))
        return round((t1 - t0).total_seconds() * 1000, 1)
    return None


def esc(value: object) -> str:
    return html.escape(str(value if value is not None else "-"))


def render_swimlane(jobs: list[dict], plans: list[dict], runs: list[dict]) -> None:
    """Render concise Multi-Agent collaboration swimlane cards with raw JSON tucked away."""
    st.subheader("Multi-Agent 协作泳道")
    latest_job = next(
        (j for j in jobs if j.get("kind") != "end_consolidation"),
        jobs[0] if jobs else None,
    )
    end_job = next((j for j in jobs if j.get("kind") == "end_consolidation"), None)
    latest_plan = plans[0] if plans else None
    if latest_job is None and latest_plan is None:
        st.info("该会话尚未产生后台多角色协作任务（例如仅首轮直出问候或测试精简会话）。")
        return

    job_data = parse_json(latest_job["data"], {}) if latest_job else {}
    plan_data = parse_json(latest_plan["data"], {}) if latest_plan else {}
    triggers = ", ".join(job_data.get("triggers") or ()) or "-"
    rev_line = (
        f"topic_rev={job_data.get('topic_revision', 0)} · "
        f"policy_rev={job_data.get('policy_revision', 0)} · "
        f"boundary_rev={job_data.get('boundary_revision', 0)}"
    )

    job_runs = [r for r in runs if latest_job and r.get("job_id") == latest_job["job_id"]]
    run_map = {r["role"]: r for r in job_runs}
    analysis_res = parse_json((run_map.get("analysis") or {}).get("result"), {}) or {}
    brief_res = parse_json((run_map.get("brief") or {}).get("result"), {}) or {}
    pressures = ", ".join(analysis_res.get("pressure_types") or ()) or "-"
    pathways = ", ".join(analysis_res.get("pathway_signals") or ()) or "-"
    need = analysis_res.get("expressed_need") or "-"
    readiness = analysis_res.get("readiness") or "-"
    concerns = [c.get("statement") for c in (brief_res.get("concerns") or ()) if c.get("statement")]

    sel = job_data.get("strategy_selection") or {}
    selected_ids = sel.get("selected_ids") or []
    decisions = sel.get("decisions") or []
    rejected = [
        f"{d.get('strategy_id')} ({', '.join(d.get('reasons') or ())})"
        for d in decisions
        if not d.get("eligible")
    ][:3]

    review_status = str(plan_data.get("review_status") or "-")
    badge_cls = "te-pill-olive" if "fast_path" in review_status else "te-pill-accent"
    actions = [
        f"{a.get('action_id')} ({a.get('kind')})"
        for a in (plan_data.get("candidate_actions") or ())
    ]
    dur_ms = job_duration_ms(latest_job) if latest_job else None
    end_ms = job_duration_ms(end_job) if end_job else None
    run_timings = " | ".join(
        f"{r['role']}: {float(r['duration_ms']):.0f}ms"
        for r in reversed(job_runs)
        if r.get("duration_ms") is not None
    )
    if end_ms is not None:
        run_timings = (
            f"{run_timings} · end_consolidation: {end_ms:.0f}ms"
            if run_timings
            else f"end_consolidation: {end_ms:.0f}ms"
        )

    cards_html = f"""
    <div class="te-lane-card">
      <div class="te-lane-head">
        <span class="te-lane-step">01 · TRIGGER &amp; BOUNDARY REVISION</span>
        <span class="te-pill">{esc(latest_job["status"] if latest_job else "-")}</span>
      </div>
      <div class="te-lane-body">
        触发信号：<code>{esc(triggers)}</code><br>
        <span style="color:var(--muted);font-size:12px;">{esc(rev_line)}</span>
      </div>
    </div>
    <div class="te-lane-card">
      <div class="te-lane-head">
        <span class="te-lane-step">02 · ANALYSIS // BLIND BRIEF</span>
        <span class="te-pill">readiness={esc(readiness)}</span>
      </div>
      <div class="te-lane-body">
        压力：<code>{esc(pressures)}</code> · 通路：<code>{esc(pathways)}</code> · 需要：<code>{esc(need)}</code><br>
        <span style="color:var(--muted);font-size:12px;">Brief 风险点：{esc("；".join(concerns) or "无异常提示")}</span>
      </div>
    </div>
    <div class="te-lane-card">
      <div class="te-lane-head">
        <span class="te-lane-step">03 · CATALOG FILTER</span>
        <span class="te-pill te-pill-accent">{len(selected_ids)} selected</span>
      </div>
      <div class="te-lane-body">
        入围策略：<code>{esc(", ".join(selected_ids) or "无行动候选（纯共情）")}</code><br>
        <span style="color:var(--muted);font-size:12px;">过滤项：{esc("；".join(rejected) or "无被排除项")}</span>
      </div>
    </div>
    <div class="te-lane-card">
      <div class="te-lane-head">
        <span class="te-lane-step">04 · PLANNER &amp; CRITIC / FAST-PATH</span>
        <span class="te-pill {badge_cls}">{esc(review_status)}</span>
      </div>
      <div class="te-lane-body">
        Objective：<code>{esc(plan_data.get("objective") or "-")}</code> · Actions：<code>{esc(", ".join(actions) or "-")}</code><br>
        <span style="color:var(--muted);font-size:12px;">理解摘要：{esc(plan_data.get("understanding") or "-")}</span>
      </div>
    </div>
    <div class="te-lane-card">
      <div class="te-lane-head">
        <span class="te-lane-step">05 · CAS PUBLISH &amp; LATENCY</span>
        <span class="te-pill">{esc(f"{dur_ms:.0f} ms" if dur_ms is not None else "-")}</span>
      </div>
      <div class="te-lane-body">
        Plan v{esc(latest_plan["version"] if latest_plan else "-")} · Status：<code>{esc(latest_plan["status"] if latest_plan else "-")}</code><br>
        <span style="color:var(--muted);font-size:12px;">角色耗时：{esc(run_timings or "-")}</span>
      </div>
    </div>
    """
    st.markdown(cards_html, unsafe_allow_html=True)

    with st.expander("🔍 原始协议负载（调试用）"):
        st.json({"latest_job": job_data, "latest_plan": plan_data})


def render_grounded_memories(memories: list[dict]) -> None:
    """Render Grounded Memory entries highlighting verbatim user source quotes."""
    st.subheader("Grounded Memory & 边界溯源")
    if not memories:
        st.caption("当前用户暂无活跃长期记忆或边界记录。")
        return

    raw_dump = []
    for m in memories[:8]:
        d = parse_json(m["data"], {}) or {}
        refs = d.get("source_refs") or []
        first_ref = refs[0] if refs and isinstance(refs[0], dict) else {}
        quote = first_ref.get("quote") or first_ref.get("claim") or "-"
        kind = str(m["kind"])
        pill_cls = "te-pill-accent" if kind == "interaction_boundary" else "te-pill-olive"
        rule_tag = (
            f" · {d.get('boundary_rule')}:{d.get('target') or '*'}"
            if d.get("boundary_rule")
            else ""
        )
        card_html = f"""
        <div class="te-lane-card">
          <div class="te-lane-head">
            <span class="te-pill {pill_cls}">{esc(kind)}{esc(rule_tag)}</span>
            <span class="te-pill">{esc(m["scope"])} · {esc(d.get("epistemic_status") or "-")}</span>
          </div>
          <div class="te-lane-body">
            <strong>{esc(m["key"])}</strong>：{esc(d.get("value"))}
            <div class="te-quote">用户原话引文：“{esc(quote)}”</div>
          </div>
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)
        raw_dump.append({"memory_id": m["memory_id"], "kind": kind, "data": d})

    with st.expander("🔍 原始记忆条目 JSON（调试用）"):
        st.json(raw_dump)


def dashboard() -> None:
    st.markdown(THEME_CSS, unsafe_allow_html=True)
    db_path = parse_args()

    st.markdown(
        '<div class="te-banner">'
        '<p class="te-kicker">AIAA 3800 COMPANION · READ-ONLY OBSERVATORY</p>'
        '<p class="te-title">小伴 Companion 运行观测台</p>'
        f'<p class="te-sub">数据库：<code>{esc(db_path.name)}</code> · WAL 只读连接（唯一写入：风险处理确认）</p>'
        "</div>",
        unsafe_allow_html=True,
    )

    sessions = read_rows(
        db_path,
        "SELECT session_id, user_key, started_at, ended_at, lifecycle, state, summary "
        "FROM sessions ORDER BY started_at DESC LIMIT 20",
    )

    selected_session = None
    if sessions:
        labels = [f"{s['session_id'][:8]} · {s['user_key']} ({s['lifecycle']})" for s in sessions]
        chosen_idx = st.sidebar.selectbox(
            "选择观察会话", range(len(sessions)), format_func=lambda i: labels[i]
        )
        selected_session = sessions[chosen_idx]
        state = parse_json(selected_session["state"], {}) or {}
        pending = state.get("pending_offer") or {}
        st.sidebar.markdown(
            f"""
            <div class="te-kpi-card">
              <div class="te-kpi-label">CORE STATE AUTHORITY</div>
              <div class="te-kpi-val">Stage: {esc(state.get("stage"))}</div>
              <div class="te-sub" style="margin-top:6px;">
                Mode: <code>{esc(state.get("mode"))}</code> · Card: <code>{esc(state.get("card_in_use"))}</code><br>
                Generation: <code>{esc(state.get("generation", 0))}</code> · Offer: <code>{esc(pending.get("target_id") or "none")}</code>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        with st.sidebar.expander("🔍 原始会话状态（调试用）"):
            st.json(state)
    else:
        st.sidebar.info("当前数据库暂无会话记录。")

    current_tab, risk_tab, analysis_tab, stats_tab = st.tabs(
        ["当前会话", "风险提醒", "后台分析", "运行统计"]
    )

    with current_tab:
        if selected_session is None:
            st.info("暂无会话可供展示。")
        else:
            sid = selected_session["session_id"]
            uid = selected_session["user_key"]
            state = parse_json(selected_session["state"], {}) or {}
            policies = read_rows(
                db_path,
                "SELECT turn_id, data FROM turn_policies WHERE session_id=? ORDER BY turn_id DESC LIMIT 1",
                (sid,),
            )
            latest_policy = parse_json(policies[0]["data"], {}) if policies else {}
            memories = read_rows(
                db_path,
                "SELECT memory_id, kind, key, scope, status, data "
                "FROM memory_items WHERE user_key=? AND status='active' ORDER BY source_cursor DESC",
                (uid,),
            )
            boundaries = []
            for m in memories:
                if m["kind"] == "interaction_boundary":
                    d = parse_json(m["data"], {}) or {}
                    boundaries.append(f"{d.get('boundary_rule')}:{d.get('target') or '*'}")

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("当前 Stage", str(state.get("stage") or "-"))
            c2.metric("L1/L2 Objective", str(latest_policy.get("objective") or "-"))
            c3.metric("当前策略卡", str(state.get("card_in_use") or "-"))
            c4.metric(
                "Generation · Offer",
                f"g{state.get('generation', 0)} · {(state.get('pending_offer') or {}).get('target_id') or '无'}",
            )

            pills = [
                f'<span class="te-pill">session: {esc(sid[:8])}</span>',
                f'<span class="te-pill te-pill-olive">cards_used: {esc(", ".join(state.get("cards_used") or ()) or "none")}</span>',
            ] + [
                f'<span class="te-pill te-pill-accent">边界隔离: {esc(b)}</span>'
                for b in boundaries
            ]
            st.markdown(f'<div class="te-pill-row">{"".join(pills)}</div>', unsafe_allow_html=True)

            turns = read_rows(
                db_path,
                "SELECT id, role, input_kind, text, stage, mode, card, latency, risk_level "
                "FROM turns WHERE session_id=? ORDER BY id",
                (sid,),
            )
            outputs = read_rows(
                db_path,
                "SELECT turn_id, data, status FROM outputs WHERE session_id=? ORDER BY created_at",
                (sid,),
            )
            outputs_by_turn: dict[int, list[dict]] = {}
            for row in outputs:
                outputs_by_turn.setdefault(row["turn_id"], []).append(
                    {**(parse_json(row["data"], {}) or {}), "delivery_status": row["status"]}
                )
            jobs = read_rows(
                db_path,
                "SELECT job_id, kind, status, source_turn_id, queued_at, started_at, finished_at, data, error "
                "FROM cognitive_jobs WHERE session_id=? ORDER BY queued_at DESC",
                (sid,),
            )
            plans = read_rows(
                db_path,
                "SELECT plan_id, version, status, data FROM support_plans WHERE session_id=? ORDER BY version DESC",
                (sid,),
            )
            runs = read_rows(
                db_path,
                "SELECT a.job_id, a.role, a.model, a.attempt, a.status, a.duration_ms, a.result, a.error "
                "FROM agent_runs a JOIN cognitive_jobs j USING(job_id) WHERE j.session_id=? ORDER BY a.started_at DESC",
                (sid,),
            )
            jobs_by_turn: dict[int, list[dict]] = {}
            for j in jobs:
                if j["source_turn_id"] is not None:
                    jobs_by_turn.setdefault(int(j["source_turn_id"]), []).append(j)

            col_chat, col_lens = st.columns([1.1, 1.0], gap="medium")
            with col_chat:
                st.subheader("对话流与单步许可输出")
                for turn in turns:
                    with st.chat_message(turn["role"]):
                        st.write(turn["text"] or f"<{turn['input_kind']}>")
                        lat = parse_json(turn["latency"], {}) or {}
                        meta_bits = [
                            f"turn #{turn['id']}",
                            f"stage={turn['stage'] or '-'}",
                            f"card={turn['card'] or '-'}",
                        ]
                        t_jobs = jobs_by_turn.get(int(turn["id"]), [])
                        if t_jobs:
                            jd = parse_json(t_jobs[0]["data"], {}) or {}
                            meta_bits.append(
                                f"triggers={','.join(jd.get('triggers') or ()) or '-'}"
                            )
                        if "first_sentence_ms" in lat:
                            meta_bits.append(f"first_sentence={lat['first_sentence_ms']:.0f}ms")
                        elif "gate_release_ms" in lat:
                            meta_bits.append(f"gate={lat['gate_release_ms']:.0f}ms")
                        st.caption(" · ".join(meta_bits))
                        for out in outputs_by_turn.get(turn["id"], []):
                            if out.get("text"):
                                st.markdown(
                                    f"> `{out.get('purpose', 'reply')}` {out.get('emoji', '')} {out['text']}"
                                )
                            elif out.get("type") == "exercise_plan":
                                plan = out.get("plan") or {}
                                st.markdown(
                                    f"> `exercise_plan` ({plan.get('script_id', '-')}, "
                                    f"segments={len(plan.get('segments', []))})"
                                )
                if selected_session.get("summary"):
                    st.info(f"会话引文摘要：{selected_session['summary']}")

            with col_lens:
                render_swimlane(jobs, plans, runs)
                render_grounded_memories(memories)

    with risk_tab:
        unhandled = read_rows(
            db_path,
            "SELECT id, session_id, turn_id, level, source, category, reason, created_at "
            "FROM risk_events WHERE handled=0 ORDER BY id DESC",
        )
        if not unhandled:
            st.success("当前无待处理风险提醒；后台安全兜底分类器处于静默保护状态。")
        else:
            for event in unhandled:
                st.error(f"#{event['id']} · {event['level']} · {event['reason']}")
                st.caption(
                    f"session={event['session_id'][:8]} · turn=#{event['turn_id']} · "
                    f"source={event['source']} · category={event['category']}"
                )
                if st.button("标记为已处理", key=f"ack-{event['id']}"):
                    mark_handled(db_path, int(event["id"]))
                    st.rerun()

        handled_rows = read_rows(
            db_path,
            "SELECT id, session_id, turn_id, level, source, reason, handled_at "
            "FROM risk_events WHERE handled=1 ORDER BY id DESC LIMIT 10",
        )
        if handled_rows:
            st.subheader("已处理历史记录")
            st.dataframe(handled_rows, width="stretch")

    with analysis_tab:
        if selected_session is None:
            st.info("选择会话后查看后台多角色协作、策略目录过滤与支持方案发布记录。")
        else:
            sid = selected_session["session_id"]
            jobs = read_rows(
                db_path,
                "SELECT job_id, kind, status, source_turn_id, queued_at, started_at, finished_at, data, error "
                "FROM cognitive_jobs WHERE session_id=? ORDER BY queued_at DESC",
                (sid,),
            )
            st.subheader("后台认知任务（Cognitive Jobs）")
            if jobs:
                job_view = []
                for j in jobs:
                    d = parse_json(j["data"], {}) or {}
                    sel = d.get("strategy_selection") or {}
                    job_view.append(
                        {
                            "job": j["job_id"][:8],
                            "kind": j["kind"],
                            "triggers": ", ".join(d.get("triggers") or ()),
                            "status": j["status"],
                            "ms": job_duration_ms(j),
                            "selected_cards": ", ".join(sel.get("selected_ids") or ()),
                            "error": j["error"] or "",
                        }
                    )
                st.dataframe(job_view, width="stretch")
            else:
                st.info("该会话尚未触发后台认知任务。")

            plans = read_rows(
                db_path,
                "SELECT plan_id, version, status, data FROM support_plans WHERE session_id=? ORDER BY version DESC",
                (sid,),
            )
            if plans:
                st.subheader("候选支持方案与 Critic / Fast-Path 审核")
                plan_rows = []
                for p in plans:
                    d = parse_json(p["data"], {}) or {}
                    acts = [a.get("action_id") for a in d.get("candidate_actions") or []]
                    plan_rows.append(
                        {
                            "plan_v": p["version"],
                            "status": p["status"],
                            "review": d.get("review_status"),
                            "objective": d.get("objective"),
                            "actions": ", ".join(acts) or "-",
                            "guidance": " / ".join(d.get("response_guidance") or ()),
                        }
                    )
                st.dataframe(plan_rows, width="stretch")

            runs = read_rows(
                db_path,
                "SELECT a.role, a.model, a.attempt, a.status, a.duration_ms, a.error "
                "FROM agent_runs a JOIN cognitive_jobs j USING(job_id) WHERE j.session_id=? ORDER BY a.started_at DESC",
                (sid,),
            )
            if runs:
                st.subheader("角色级模型调用明细（Brief / Analysis / Planner / Critic / End）")
                st.dataframe(runs, width="stretch")

            with st.expander("🔍 原始任务与方案 JSON（调试用）"):
                st.json(
                    {
                        "jobs": [parse_json(j["data"], {}) for j in jobs],
                        "plans": [parse_json(p["data"], {}) for p in plans],
                    }
                )

    with stats_tab:
        all_turns = read_rows(db_path, "SELECT latency, output_status FROM turns WHERE role='user'")
        first_sent = []
        for t in all_turns:
            lat = parse_json(t["latency"], {}) or {}
            if "first_sentence_ms" in lat:
                first_sent.append(float(lat["first_sentence_ms"]))
        all_jobs = read_rows(
            db_path, "SELECT kind, status, started_at, finished_at FROM cognitive_jobs"
        )
        bg_ms = []
        status_counts: dict[str, int] = {}
        for j in all_jobs:
            status_counts[j["status"]] = status_counts.get(j["status"], 0) + 1
            if j["kind"] != "end_consolidation":
                dur = job_duration_ms(j)
                if dur is not None:
                    bg_ms.append(dur)

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("用户总轮次", len(all_turns))
        m2.metric("后台任务总量 / 超时", f"{len(all_jobs)} / {status_counts.get('timed_out', 0)}")
        m3.metric(
            "Talker 首句 P50 / P90",
            f"{statistics.median(first_sent):.0f} / {percentile_90(first_sent):.0f} ms"
            if first_sent
            else "-",
        )
        m4.metric(
            "后台认知 P50 / P90",
            f"{statistics.median(bg_ms):.0f} / {percentile_90(bg_ms):.0f} ms" if bg_ms else "-",
        )
        if status_counts:
            st.subheader("认知任务状态分布")
            st.dataframe(
                [{"status": k, "count": v} for k, v in sorted(status_counts.items())],
                width="stretch",
            )
        if sessions:
            st.subheader("会话摘要（引文合成 Summary）")
            st.dataframe(
                [
                    {
                        "session": s["session_id"][:8],
                        "user": s["user_key"],
                        "lifecycle": s["lifecycle"],
                        "summary": s["summary"] or "-",
                    }
                    for s in sessions
                ],
                width="stretch",
            )


dashboard()
