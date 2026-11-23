# Companion System Technical Specification & Empirical Benchmarks (English)

> **Document Scope**: Objective system specification, engineering parameters, and verified empirical benchmarks for **Companion (小伴)** — a multi-agent daily emotional companionship prototype designed around routine academic and evaluative stress in Chinese secondary school contexts. Every symbol, threshold, and metric is verified directly against source code, YAML configuration, and archived JSON logs. For the Chinese edition see [`SYSTEM_SPEC_AND_BENCHMARKS_ZH.md`](SYSTEM_SPEC_AND_BENCHMARKS_ZH.md); for BibTeX entries see [`references.bib`](references.bib).

---

## 1. Problem Space & Literature-to-Mechanism Translation

### 1.1 Five Concurrent Stressor Domains & Four Psychological Pathways

Designed around late-evening study, exam score release, subject-track selection, and pre-exam/bedtime routines, the domain model structures daily stressors along five non-mutually-exclusive axes ([`core/models.py`](../../companion/core/models.py)):

| Stressor Identifier | Concrete Academic & Family Triggers | Co-Occurring Pathways | Generic LLM Failure Mode |
| --- | --- | --- | --- |
| `academic` | Unresolved homework/problem-set friction, rest guilt at 10:30 PM | `rumination`, `sleep` | Immediately pushes unsolicited 1-2-3 study schedules |
| `social_evaluative` | Salient mock/monthly class ranks, acute somatic pre-exam tension | `self_criticism`, `sleep` | Invalidating reassurance ("ranks don't matter" / "you will ace it") |
| `relationship` | Parental horizontal comparison ("cousin/top student"), peer friction | `loneliness`, `rumination` | Prescribes reconciliation or lectures on filial duty regardless of safety |
| `future` | High-school subject selection anxiety, loss of day-to-day meaning | `rumination` | Dictates tracks or gives unverified admissions forecasts |
| `self` | Over-generalizing one exam slip into global worthlessness, body critique | `self_criticism` | Hollow praise ("you are already the best") or appearance judgments |

### 1.2 Traceable Mapping Across 19 Academic & Public-Health Sources

The runtime **never fetches full-text articles online or extrapolates clinical effect sizes**. Instead, curated excerpts, study boundaries, and exclusion constraints in `companion/companion/config/content_manifest.yaml` govern how each reference informs deterministic protocol rules:

| Reference (Author, Year) | Empirical Basis & Study Scope | System Mechanism / Card Grounding | Preserved Scope Constraint |
| --- | --- | --- | --- |
| Ye et al., 2019 | ASQ-CN validation in Chinese secondary students ($N=420$, $\alpha=.82\text{--}.90$) | Five-domain stress coverage & `values_exploration` | Survey factor taxonomy != diagnostic checklist |
| Wang et al., 2025 | Zhejiang 3-wave adolescent cohort ($N=2965$); sleep (31.0%) & loneliness (26.8%) statistically mediate burden -> symptoms | `worry_parking`, `bedtime` exercise & bedtime context gating | Observational cohort constraints; no causal sleep-cure claim |
| Dickerson & Kemeny, 2004 | Meta-analysis of 208 laboratory stress studies; uncontrollable social evaluation elicits acute stress responses | `exam_steadying`, `comparison_reframe`, `expectation_boundary` | Lab cortisol reactivity != adolescent clinical outcome |
| Zhao & Hu, 2022 | Changsha secondary schools ($N=3480$); 73.0% help-seeking (99.3% informal vs. 13.9% formal services) | `safe_support` low-friction bridge & informal peer-like tone | Cross-sectional single-city data; no behavioral shift claim |
| Gulliver et al., 2010 | Systematic review (22 youth studies); stigma, confidentiality doubts & self-reliance dominate barriers | `safe_communication`, `safe_support`, single-step `PendingOffer` | Supports autonomy/anti-judgment motivation only |
| Leigh et al., 2025 | Two adolescent experiments (ages 11–14); concrete vs. abstract processing improves proximal social problem solving | `concrete_step` focusing on a single five-minute next step | Proximal task measure != single-turn therapeutic effect |
| Lunn et al., 2023 | Meta-analysis (121 youth studies); perfectionistic concerns correlate ($r \approx 0.40$) with distress vs. high strivings | `kind_self_talk` separating striving from global self-blame | Correlational evidence; reframing is optional support |
| WHO & UNICEF, 2023 | *EASE* guide; Calming My Body & Stop–Think–Go small solvable step decomposition | Bounded small-step decomposition in `concrete_step` | EASE requires 7 supervised group sessions; mechanism-only use |
| Bluth et al., 2024 | Adolescent mindful self-compassion RCT ($N=59$) | Friend-perspective grounded reframing in `kind_self_talk` | `OutputRail` forbids hollow cheering & appearance remarks |
| Filia et al., 2021 | Narrative review of youth relational interventions (IPT-A communication analysis) | `safe_communication` low-pressure phrasing rehearsal | Strictly requires explicit `safe_contact`; blocked if unsafe |
| Chen et al., 2022 | Jiangsu Senior-1 online career course ($N=957$, 5 weeks); exploration reduces uncertainty distress | `values_exploration` narrowing confusion to one verifiable question | Forbids prescriptive major or score recommendations |
| Scullin et al., 2018 | Polysomnography RCT ($N=57$ healthy young adults); 5-min bedtime to-do offload reduced sleep latency | `worry_parking` (2-step wrap-up) & `bedtime` exercise | Prohibits five-item task dumps; adult lab scope noted |
| WHO et al., 2011 | *Psychological First Aid (PFA)* field guide; Look–Listen–Link, zero pressure, voluntary link | `safe_support`, `grounding`, fixed crisis script & instant exit | Acute crisis framework != routine exam tutoring evidence |
| Liu et al., 2021 | ACL 2021 ESConv support framework (Explore–Comfort–Action) | Deterministic `StateMachine` tier progression | Trained human supporters in corpus; gated by consent FSM |
| Deng et al., 2024 | ICLR 2024 Plug-and-Play Policy Planner decoupling policy decision from surface realization | `Planner` emits structured directives/steps -> constrained `Talker` | Untrained LLM deliberation does not inherit RL policy results |
| Dunning et al., 2022 | Updated youth mindfulness RCT meta-analysis; mixed effect vs. active controls, adverse body-focus risk | Non-breath-hold `breathing_60s`, eyes-open `grounding` fallback | Strict `< 90s` cap, voluntary opt-in, instant abort on discomfort |
| Yeager et al., 2022 | *Nature* multi-cohort RCTs; synergistic mindset reappraises somatic arousal as resource mobilization | `exam_steadying` normalizes pre-test heart rate + tiny start step | U.S. educational trials; never promises score improvement |
| Megalokonomou & Zhang, 2024 | High-school salient rank mechanisms amplifying horizontal comparison and discouragement | `comparison_reframe` shifting from public rank to personal baseline | Contextualizes rank salience without denying exam reality |
| Ding et al., 2026 | Parental social comparison taxonomy in Chinese adolescents | `expectation_boundary` separating parental anxiety from personal pace | `unsafe_relationship` excludes coercive/abusive home settings |

Vector figure: [`figures/en/01-problem-and-literature-en.pdf`](figures/en/01-problem-and-literature-en.pdf).

---

## 2. Layered Companionship, 9+3 Protocol & Deterministic Consent FSM

### 2.1 Tier-1 Empathy Matrix & Silent Safety Gate

Routine venting stays in **Tier-1 Non-Action Presence** by default without requiring opt-in, and constrains question load to at most one question per turn (`question_budget = 0` in `quiet`):

1. **`attuned_listen`**: Grounded reflection tied strictly to recent user turns; zero unsolicited task lists.
2. **`tentative_reflect`**: Gentle naming of mixed affect (e.g., frustration mixed with guilt) inviting user correction.
3. **`low_energy_companionship`**: Triggered when `readiness == "low"` or advice is declined; normalizes rest without assigning tasks.
4. **`quiet_presence`**: Triggered on quiet requests ("stop asking", "just stay quiet"); locks questions to `0` and clears pending offers.

If the orthogonal **Silent Safety Lane** (L1 deterministic lexicon + async L2 `qwen-flash` classifier) flags `risk_level == "high"`, the system switches permanently within the session to `mode = "crisis"` and delivers verified fixed crisis support (`crisis.yaml`).

### 2.2 Tier-2 Catalog: 9 Strategy Cards & 3 Fixed-Audio Exercises

All 9 enabled strategy cards enforce `requires_permission: true` and `limits.per_session: 1`. Eight cards define 3 action steps and `worry_parking` defines 2 steps; runtime execution caps turns at `min(settings.max_action_turns=4, len(card.talker.steps))` (`state_machine.py:212`).

| Card ID (`cards/*.yaml`) | Core Role | Targets (`pressure_types` / `pathways`) | Steps & Emoji | Context Gates (`required` / `excluded`) | Grounding Citations |
| --- | --- | --- | --- | --- | --- |
| `concrete_step` | Shift rumination to one tiny concrete step | `academic` / `rumination` | 3 / 🤔 | `excl`: `unsafe_relationship` | Leigh 2025 · WHO/UNICEF 2023 |
| `exam_steadying` | Reappraise pre-exam somatic arousal & anchor opening step | `academic`, `social_evaluative` / `sleep` | 3 / 😌 | `excl`: `unsafe_relationship` | Yeager 2022 · Dickerson 2004 |
| `kind_self_talk` | Replace global self-attack with friend-standard realism | `self`, `social_evaluative` / `self_criticism` | 3 / 🙂 | `excl`: `unsafe_relationship` | Lunn 2023 · Bluth 2024 |
| `comparison_reframe` | Return from salient class rank to personal baseline | `social_evaluative` / `self_criticism` | 3 / 😌 | `excl`: `unsafe_relationship` | Megalokonomou 2024 · Dickerson 2004 |
| `expectation_boundary` | Separate parental anxiety from personal study pace | `relationship`, `social_evaluative` / `[]` | 3 / 😌 | `excl`: `unsafe_relationship` | Ding 2026 · Dickerson 2004 |
| `safe_communication` | Rehearse one low-pressure everyday phrase | `relationship` / `[]` | 3 / 🤔 | `req`: `safe_contact`; `excl`: `unsafe_relationship`, `no_private_space`, `bedtime` | Filia 2021 · Gulliver 2010 |
| `safe_support` | Identify one trusted human support avenue | all 5 stressors / `loneliness` | 3 / 🙂 | `excl`: `bedtime` | Zhao 2022 · Gulliver 2010 · WHO 2011 |
| `values_exploration` | Narrow future uncertainty into one verifiable question | `future` / `[]` | 3 / 🤔 | `excl`: `bedtime` | Chen 2022 · Ye 2019 |
| `worry_parking` | Park one pre-sleep worry externally and stop | `[]` / `sleep`, `rumination` | **2** / 😌 | `req`: `bedtime`; `excl`: `unsafe_relationship` | Scullin 2018 · Wang 2025 |

> Every card excludes `emotion_intensity == "high"` and `readiness == "low"` via deterministic `constraints`.

| Exercise ID (`exercises/*.yaml`) | Segment Count & Pauses | Measured Audio Duration (`11-21`) | Context Gates | Citations |
| --- | --- | --- | --- | --- |
| `breathing_60s` | 5 lines / 13.0s pause | **43.5s** (`< 90s`, no breath-hold) | `excl`: `body_focus_distress`, `unsafe_relationship` | Dunning 2022 |
| `grounding` | 4 lines / 11.0s pause | **41.7s** (`< 90s`, eyes-open object anchor) | `excl`: `unsafe_relationship` | WHO 2011 |
| `bedtime` | 4 lines / 10.0s pause | **39.0s** (`< 90s`, bedtime settle) | `req`: `bedtime`; `excl`: `unsafe_relationship`, `body_focus_distress` | Scullin 2018 · Wang 2025 |

- Across exercises and fixed system cues, `prepare_audio` binds **24 pre-synthesized segments** verified at `--mode demo` startup.

### 2.3 Single-Step `PendingOffer`, Lookahead Regex & Scoped Boundaries

1. **7 Stages** (`core/models.py`): `opening`, `explore`, `comfort`, `permission`, `action`, `closing`, `quiet`.
2. **Explicit Opt-In Gate** (`core/state_machine.py`): Help requests (`ask` in `rules.yaml`) advance to `permission` holding a single `PendingOffer(kind, target_id)` valid for `offer_valid_turns = 2`. Colloquial `agree` uses a negative-lookahead pattern (`^(?!.*(?:难受|算了|不用|不想|不要|不愿|不行|不可以|没用))...`) so negated utterances ("not that I don't want to...") never mis-fire as consent. Explicit refusal, crying, high intensity, or correction clears the offer, records `cards_refused`/`exercises_refused`, and returns to `explore`. Explicit exercise refusal clears `resume_script_id`; only neutral ambient noise interruption offers a gentle resume check.
3. **Scoped Boundary Engine** (`cognition/policy.py`, `memory/concepts.py`): `no_advice:<target>` and `no_topic_probe:<topic>` compute domain cluster overlap via `targets_overlap()` so blocking academic/exam probing leaves bedtime soothing (`worry_parking`) unobstructed.
4. **Reconnect Onboarding Skip** (`core/helpers.py:resolve_opening`): Queries SQLite for prior `user` turns on `wake` so returning sessions skip introductory prompts and surface eligible boundary-checked followups.

Vector figure: [`figures/en/02-strategy-taxonomy-consent-en.pdf`](figures/en/02-strategy-taxonomy-consent-en.pdf).

---

## 3. Three-Lane Architecture & Verified Configuration Parameters

### 3.1 `settings.yaml` Model Allocation & Budgets

Verified directly from [`companion/companion/config/settings.yaml`](../../companion/config/settings.yaml):

| Role / Component | Configured Model / Backend | Latency & Token Budgets | Architectural Scope |
| --- | --- | --- | --- |
| **Realtime Talker** | `qwen-flash` (`enable_thinking: false`) | 1st-token timeout `2500 ms`; turn timeout `10 s`; max `3` sentences | Reads frozen `TurnPolicyFrame` only; filtered by `OutputRail` |
| **Silent Safety (Risk)** | L1 Lexicon + L2 `qwen-flash` | `4` workers; gate wait `400 ms`; total risk timeout `2500 ms` | Unblocks non-high turns at 400 ms; late `high` increments `generation` & aborts audio |
| **Blind Brief & DeltaGuard** | `qwen-flash` | Shared cognitive budget | `Brief` emits counter-evidence in parallel; `DeltaChecker` validates mid-flight turns once |
| **Analysis & Planner** | `gpt-4.1-mini` | `deliberation`: `8` calls / `6000` output / `32000` total tokens / `20 s` deadline | Uses compact structured contract instead of full JSON Schema; `Catalog` pre-filters |
| **Cross-Family Critic** | `qwen-flash` (`critic_model`) | Max `1` revision pass (version `1 -> 2`) | Audits `gpt-4.1-mini` Planner output + turn evidence; bypassed by safe Fast-Path |
| **Memory / End + Grounder** | Extraction `gpt-4.1-mini`; Review `qwen-flash` | `memory` & `end_consolidation`: `2` calls / `20 s` each (`1800` / `2400` output cap); `routine`: `4` calls | Two-call entailment check + verbatim quote summary |
| **TTS & In-Memory Opus** | `gpt-4o-mini-tts` (`voice: coral`, `opus`) | Exercise cap `90 s`; `MAX_PACKET_CACHE = 64` LRU | Dispatches streaming clause `>= 8` chars outside closing quotes; PyAV + `opuslib_next` 60 ms RAM frames |

### 3.2 Concurrency, Memory Grounding & Persistence Guarantees

1. **Adaptive Non-Action Fast-Path (`fast_path_non_action`)** (`cognition/orchestrator.py:384-403`): On `version == 1`, when `objective in NON_ACTION`, `candidate_actions == []`, `local_issues == []`, and **`not protects_active_offer`** (ensuring active approved offers in `Stage.permission` are never clobbered), background deliberation skips draining `Brief` and invoking `Critic`.
2. **Quadruple-Version Transactional CAS** (`cognition/policy.py:26-48`, `orchestrator.py:614-649`): Background plans expire after `plan_ttl_s = 120 s` or `plan_turn_delta > 4` user turns without renewal. Inside `UserLock + SessionLock + SQLite Transaction`, `plan_invalid_reason()` and `publish()` enforce: (1) matching `topic_revision` & `policy_revision` (`control_revision`), (2) unchanged `boundary_revision` pre- and post-memory commit, (3) `support_plan_version == base_plan_version` and matching `user_turns`, and (4) matching `memory_dependency_versions` while `lifecycle == "active"` and `mode == "normal"`. Verified memories still persist cleanly via `partial_commit` even if an action proposal hits `final_cas_conflict`.
3. **Dual Plan Isolation & Monotonic `generation`**: `active_plan_id` manages segmented audio playback while `active_support_plan_id` holds strategy frames; user speech, barge-in, or crisis risk monotonically increments `generation` to drop stale TTS clauses and Opus frames immediately (`core/helpers.py:resolve_emoji` maps context to `[😶, 🙂, 😔, 😌, 🤔, 😰]`).
4. **Source-Entailed Memory & 8 School Clusters** (`cognition/consolidation.py`, `memory/concepts.py`): `ConsolidationGrounder` checks `PREMISE` (verbatim user turns) -> `HYPOTHESIS` entailment before commit; `extractive_summary()` concatenates verbatim user quotes (`<= 150` chars); name/fact corrections mark older items `superseded`. Retrieval and boundary matching share eight zero-dependency Chinese concept clusters: `parent_family`, `exam_grade`, `peer_school`, `future_track`, `sleep_burnout`, `appearance_self`, `time_plan`, `identity_name`.
5. **Hardware Gateway & Storage**: Pinned upstream Xiaozhi server commit `92337881a7b6553614b47e137a774d02bf40512f` (6 patches enforcing Bearer auth, server-side `device_id -> user_key`, and SenseVoice acoustic cues); SQLite `user_version = 2`, single-writer `WriterLease`, consistent backup `v1 -> v2` migration, and `mode=ro` URI WAL Streamlit telemetry dashboard.

Vector figures: [`03`–`08` PDFs](figures/en/).

---

## 4. Authoritative Empirical Benchmarks (Strictly Sourced)

### 4.1 Multi-Turn Live-Model Replay (`companion/docs/evidence/course-2.0-bench.json`, `2026-11-21`)

Model profile: `qwen-flash` (Talker, Risk, Brief, Critic, Delta) + `gpt-4.1-mini` (Analysis, Planner, Memory, End); manifest digest `ff5ff4205060847bd9ec7cbfeb24361cc45ff48837eff8b4d0f04f8bbbfafbe1`; suite `course-quality-2`:

| Metric | Archived Baseline (`2026-11-04`) | Current System (`2026-11-21`) | Delta / Notes |
| --- | --- | --- | --- |
| **Scenario & Target Coverage** | 9/9 targets executed | **22/22 scenarios · 12/12 targets executed** | All 9 strategy cards + 3 exercises + refusal/scope traces |
| **Background Execution & Timeouts** | 2 job / 2 role timeouts | **0 timeouts** (58 completed, 8 partial, 3 rejected) | `0 / 69` timeouts under 20s deadline |
| **Cognition Deliberation P50 / P90** | `10729.5 ms` / `15422.6 ms` ($n=75$) | **`5889.1 ms` / `7389.3 ms`** (Max `8186.9 ms`, $n=46$) | **-45.1% P50 · -52.1% P90** |
| **Replay Talker 1st Sentence P50 / P90** | `1281.0 ms` / `1406.0 ms` ($n=41$) | **`1062.0 ms` / `1219.0 ms`** ($n=63$) | 1st token P50 **`1000.0 ms`** / P90 `1063.0 ms` |
| **End Consolidation ($n=23$)** | — | **P50 `7314.4 ms` · P90 `12034.3 ms`** | Shared 2-call / 20s grounded memory & summary budget |

### 4.2 Streaming Text & Xiaozhi Loopback Opus Voice (`course-2.0-bench.json`, `2026-11-21`)

- **Streaming Text Probe ($n=30$, 0 errors / 0 fallbacks / 0 risk degradations)**: First-token P50 **`1016.0 ms`** (P90 `1453.0 ms`), First-sentence P50 **`1109.5 ms`** (P90 `1578.0 ms`), Total P50 **`1202.5 ms`** (P90 `1656.0 ms`).
- **Xiaozhi Loopback Opus Voice Probe ($n=30$, 0 failures, `end_status=done`, `jobs_completed=8`)**:

| Pipeline Stage | Baseline P50 / P90 (`11-04`) | Current P50 / P90 (`11-21`) | Relative Change & Distribution Notes |
| --- | --- | --- | --- |
| **Talker First Token** | `1187.5 ms` / `1359.0 ms` | **`1000.0 ms` / `1078.0 ms`** | `-15.8%` P50 |
| **First Sentence / 400ms Gate** | `1257.5 ms` / `1421.0 ms` | **`1101.0 ms` / `1203.0 ms`** | `-12.4%` P50 |
| **TTS Audio Complete** | `3539.0 ms` / `3937.0 ms` | **`2507.5 ms` / `2890.0 ms`** | **`-29.1%` P50** ($n=28$ uncached turns) |
| **In-Memory Opus 1st Packet Ready** | `3586.0 ms` / `3984.0 ms` | **`2421.5 ms` / `2750.0 ms`** | **`-32.5%` P50** (zero disk WAV round-trip) |
| **Client First Packet Arrived (E2E)** | `3609.0 ms` / `4015.0 ms` | **`2656.0 ms` / `3140.0 ms`** | **`-26.4%` P50** (Mean `2511.4 ms`, Min `1000.0 ms`, Max `3406.0 ms`; 2 full LRU cache hits on #20 `1172.0 ms` & #30 `1015.0 ms`) |
| **Server Playback Completed** | `9273.0 ms` / `11031.0 ms` | **`8101.5 ms` / `9781.0 ms`** | `-12.6%` P50 |
| **Voice Background Cognition** | `12610.7 ms` / `15316.3 ms` ($n=8$) | **`6457.0 ms`** ($n=7$) | **`-48.8%` P50** |

### 4.3 Silent Safety Matrix (`online-regression-20261109.json`, `2026-11-09`)

Evaluated over $n=120$ developer-authored synthetic utterances (`none=40 / watch=40 / high=40`, `qwen-flash` L2 + L1 lexicon; `classifier_failures = 0`; crisis `abort_to_stop_ms = 16.0 ms`): `high_recall = 1.0`, `watch_recall = 1.0`, `false_high_rate = 0.0`, `timely_high_recall = 1.0`. Combined lexicon+classifier confusion matrix: `none -> (28, 12, 0)`, `watch -> (0, 37, 3)`, `high -> (0, 0, 40)` (classifier alone: `40/0/0`, `0/37/3`, `0/0/40`).

### 4.4 Grounded Memory Counterfactual Check (`grounded-memory-20261109.json`, `2026-11-09`)

- **8 extraction boundary cases**: Fragment-only time strings without subject ownership produce empty typed memory (`[]`) while verbatim summaries quote the exact turn; explicit personal facts and temporary refusals bind to exact `persistent` vs. `session` scopes.
- **6 forced counterfactual reviews**: 4/4 unsupported/over-generalized candidates rejected (`not_enough_information`); 2/2 explicitly stated claims accepted (`entailed`).

### 4.5 Offline Regression & Isolated Wheel Verification

- `./scripts/run.ps1 test`: Ruff lint passed, 137 Python files formatted cleanly, **`224 passed, 1 skipped, 3 deselected`** in offline pytest (single skip at `test_course2_upgrades.py:310` reflects root `.venv` intentionally separating `opuslib_next` into `vendor/xiaozhi-venv`; 3 online tests explicitly excluded by `-m "not online and not hardware"`).
- Isolated wheel check verified packaging completeness, 4-role deliberation, transactional `v1 -> v2` backup migration, idempotent startup, and CLI sanity.

Vector benchmark figure: [`figures/en/09-latency-benchmarks-en.pdf`](figures/en/09-latency-benchmarks-en.pdf).

---

## 5. System Boundaries & Limitations

1. **Non-Clinical Prototype Scope**: Literature citations guide mechanism adaptation only (gentle tone, voluntary opt-in, instant exit, safe exclusions); the system makes **zero clinical diagnostic, therapeutic efficacy, or academic-placement guarantee claims**.
2. **Synthetic & Adult Role-Play Corpus**: Multi-turn quality replays, risk evaluation utterances (pending independent clinical labeling review), and latency probes rely exclusively on synthetic scenarios and developer role-play rather than studies with actual minor students.
3. **Loopback vs. Physical ESP32 Acoustic Latency**: Measured `2.66 s` client first-packet latency captures localhost loopback WebSocket streaming + real upstream LLM/TTS + Opus encoding under active background cognition; physical ESP32 Wi-Fi jitter, speaker DAC buffering, and acoustic wake-word ASR front-end latency require separate on-device hardware measurement.
4. **Concept Visuals Disclaimer**: Plush companion photography assets in [`docs/assets/`](../../../docs/assets/) (`companion-*.webp`) are AI-generated industrial concept studies depicting physical desk scale (~22 cm) and calming bedtime aesthetics; hardware enclosure tooling and capacitive touch sensors remain hardware-track prototypes.
