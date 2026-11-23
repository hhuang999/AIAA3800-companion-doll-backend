# 小伴 Companion：权威系统技术规格与实测基准手册（中文版）

> **文档定位**：本手册为 **小伴 Companion**（面向中国初高中升学日常压力的情感陪伴与语音交互原型系统）的纯客观系统规格与实测汇总，所有结构、参数与实验数据均直接核对于仓库源码、YAML 配置与已归档 JSON 测试证据。对应英文版见 [`SYSTEM_SPEC_AND_BENCHMARKS_EN.md`](SYSTEM_SPEC_AND_BENCHMARKS_EN.md)，学术文献条目见 [`references.bib`](references.bib)。

---

## 一、研究背景、问题空间与 19 篇文献机制转译

### 1.1 初高中升学日常五类压力源与四条共同通路

面向中国初高中生晚自习前后、成绩公布、选科分班与睡前情境，系统将并发日常压力源抽象为 5 个一级维度（[`core/models.py`](../../companion/core/models.py)）：

| 压力类型标识 | 典型校园与家庭触发情境 | 四条关联心理放大通路 | 通用大模型的典型失配 |
| --- | --- | --- | --- |
| `academic` | 晚自习刷题卡壳、错题积累、精力透支后的休息内疚 | `rumination`（抽象反复想“为什么总做不到”）、`sleep` | 立即输出 1-2-3 学习规划清单，加重认知过载 |
| `social_evaluative` | 模考与月考公开排名、考前急性躯体紧张（心慌/手抖） | `self_criticism`、`sleep` | 机械安慰“成绩不重要”或“肯定能考好”引发逆反 |
| `relationship` | 父母横向比较（如“别人家孩子”）、同伴或宿舍摩擦 | `loneliness`、`rumination` | 不分家庭安全风险直接劝和或教“体谅父母” |
| `future` | 选科/分班/志愿方向困惑、日常刷题意义感迷失 | `rumination` | 越权代为选择选科组合或做出绝对前途预测 |
| `self` | 单次考试失手后全盘自我否定、完美主义担忧与外貌苛责 | `self_criticism` | 空洞夸奖（“你已经最棒了”）或违背边界评价外貌 |

### 1.2 19 篇学术与公共卫生文献的可追溯映射表

系统**严禁在线直接抓取或全文检索论文并外推原始效应量**，而是通过人工逐篇核查摘要/全文与适用边界（`companion/companion/config/content_manifest.yaml`），将可迁移机制转译为确定性策略规则与护栏：

| 文献来源（Author & Year） | 研究样本与核心机制发现 | 对应系统策略卡 / 机制落地 | 严格保留的边界限制 |
| --- | --- | --- | --- |
| Ye 等, 2019 | 中国中学生 $N=420$，ASQ-CN 六因子验证（内部一致性 0.82–0.90） | 五维压力覆盖与 `values_exploration` 需求结构 | 量表结构不直接等价于临床诊断类别 |
| Wang 等, 2025 | 浙江初高中生 $N=2965$ 三波纵向队列；睡眠（31.0%）与孤独（26.8%）中介学业负担与情绪症状 | `worry_parking`、`bedtime` 短练习与夜间上下文隔离 | 观察队列及地区/疫期限制，不推论短语音直接改善睡眠或抑郁 |
| Dickerson & Kemeny, 2004 | 208 项急性压力实验元分析；社会评价威胁与不可控感触发强急性应激反应 | `exam_steadying`、`comparison_reframe`、`expectation_boundary` | 实验室皮质醇指标不能外推长期青少年结局 |
| Zhao & Hu, 2022 | 长沙四所中学 $N=3480$；73.0% 求助，其中非正式支持 99.3% vs 正式服务 13.9% | `safe_support` 低门槛桥接、同龄感低评判语言姿态 | 单地自陈横断面数据，不声明改变现实求助率 |
| Gulliver 等, 2010 | 22 项青少年求助障碍综述；污名、保密担忧与自主偏好最突出 | `safe_communication`、`safe_support` 与 `PendingOffer` 单步控制权 | 仅作去评判与自主控制权设计动机 |
| Leigh 等, 2025 | 11–14 岁青少年两项实验；具体化加工相对抽象反刍改善近端问题解决 | `concrete_step`（聚焦眼前可动最小一步） | 近端任务指标，不推论一轮对话的临床疗效 |
| Lunn 等, 2023 | 6–24 岁 121 项研究元分析；完美主义“担忧”维度与焦虑抑郁显著相关（$r\approx 0.40$） | `kind_self_talk` 剥离“高标准努力”与“全盘自我批判” | 相关性数据，不承诺单句重构即产生疗效 |
| WHO & UNICEF, 2023 | EASE 青少年心理援助手册；Calming Body / Stop–Think–Go 小问题拆解 | `concrete_step` 的“小、可解、具体”边界约束 | 原项目需七次受督导小组与照护者参与，此处只借用拆解原则 |
| Bluth 等, 2024 | 青少年正念自我关怀八周 RCT（$N=59$）；减缓自我苛责轨迹 | `kind_self_talk` 对好友平实比照句式，禁止空洞夸奖 | 样本文化背景局限，严格通过 `OutputRail` 禁绝空洞安慰 |
| Filia 等, 2021 | 青少年人际干预综述；IPT-A 沟通分析与低负担角色练习结构 | `safe_communication`（先理清冲突、再练一句平实表达） | 强约束仅当 `safe_contact` 成立且排除 `unsafe_relationship` 时启用 |
| Chen 等, 2022 | 江苏高一 $N=957$ 五周在线生涯课程；信息探索降低选科迷茫 | `values_exploration` 引导挑一个可核查方向小问题 | 严禁代报志愿或断言天赋匹配 |
| Scullin 等, 2018 | 青年成人 $N=57$ 多导睡眠实验；睡前写具体待办缩短入睡潜伏期 | `worry_parking`（2 步收尾）与 `bedtime` 练习 | 成人单夜书写实验，禁止在睡前列出五项待办清单加压 |
| WHO 等, 2011 | 心理急救（PFA）现场指南；Look–Listen–Link 与尊重意愿不强迫原则 | `safe_support`、`grounding`、危机固定话术与自由喊停权限 | 主要针对危机现场支持，不作为普通考试减压疗效证据 |
| Liu 等, 2021 | ACL 2021 ESConv 情感支持对话框架（探索 → 安慰 → 行动三阶段） | `StateMachine` 分层阶段演进骨架 | 原语料来自受训人类支持者，线上须加硬性许可门控 |
| Deng 等, 2024 | ICLR 2024 Plug-and-Play 策略规划器（策略决策与文本生成解耦） | `Planner` 输出结构化策略指令与步骤，`Talker` 负责自然表达 | 后台多 Agent 无监督微调协作不直接继承原论文训练结论 |
| Dunning 等, 2022 | 儿童青少年正念 RCT 更新元分析；主动对照下效应有限且存在身体不适风险 | `breathing_60s`（不屏气控息、可睁眼）与 `grounding` 外部着陆替代 | 强约束所有短练习 `< 90s`、需自愿进入并随时停止 |
| Yeager 等, 2022 | *Nature* 多队列随机实验；协同心态重评将考前躯体唤醒解释为调动资源 | `exam_steadying`（正常化心跳/手汗 + 最小开考起手动作） | 教育干预背景差异，不向学生宣称必能提升考分 |
| Megalokonomou & Zhang, 2024 | 高中显著排名研究；高可见度榜单放大退缩感并遮蔽自身纵向进步 | `comparison_reframe`（引导从他人进度/榜单回看个人两天基线） | 不否认现实竞争，仅调节自我对照参照系 |
| Ding 等, 2026 | 中国青少年父母社会比较分类模型；区分批评贬低型比较的心理代价 | `expectation_boundary`（剥离父母焦虑与自身节奏，绝不劝“都是为你好”） | 若涉及暴力/危险控制则被 `unsafe_relationship` 硬排除 |

对应英文矢量架构图：[`figures/en/01-problem-and-literature-en.pdf`](figures/en/01-problem-and-literature-en.pdf)（中文版：[`figures/zh/01-context-and-stressors.pdf`](figures/zh/01-context-and-stressors.pdf) 与 [`02-evidence-to-design.pdf`](figures/zh/02-evidence-to-design.pdf)）。

---

## 二、分层陪伴体系、9+3 策略协议与确定性交互状态机

### 2.1 L1 默认主动共情四态与绝对沉默守门

日常倾诉默认停驻在 **L1 非行动层**，无需请求许可；且任一轮仅在规则边界允许时附带至多 1 个开放问题（`quiet` 状态强制问题预算 `= 0`）：

1. **`attuned_listen`**：紧扣用户刚提到的具体事实细节做平实回应，零说教、少追问。
2. **`tentative_reflect`**：试探性命名混合或夹心情绪（如委屈夹着愧疚），句式显式保留纠偏余地。
3. **`low_energy_companionship`**：当 `readiness == "low"`（晚自习散架、极度疲惫或明确拒建议）时激活，温和正常化休息，**严格禁止安排任何学习或练习任务**。
4. **`quiet_presence`**：响应“不想说 / 让我静静 / 今天先到这儿”，将提问预算锁死为 `0` 并清空活跃邀约。

若 **静默安全线**（L1 规则词表 + L2 并发风险分类器）判定 `risk_level == "high"`，系统即刻切入固定危机接管通道（`mode = "crisis"`），停发所有策略卡并播报已审核固定文本（`crisis.yaml`）。

### 2.2 L2 九张支持策略卡与三段短练习完整规格表

全部 9 张启用策略卡均设置 `requires_permission: true` 与 `limits.per_session: 1`；除 `worry_parking` 为 2 步短收尾外，其余 8 张均为 3 步口语引导（`state_machine.py:212` 运行时行动上限取 `min(settings.max_action_turns=4, len(card.talker.steps))`）。

| 策略卡 ID (`cards/*.yaml`) | 中文名称 | 靶点 (`pressure_types` / `pathways`) | 步骤数 & 表情 | 上下文硬门槛 (`required` / `excluded`) | 文献依据 |
| --- | --- | --- | --- | --- | --- |
| `concrete_step` | 从反复想转向具体的一步 | `academic` / `rumination` | 3 步 / 🤔 | `excl`: `unsafe_relationship` | Leigh 2025 · WHO/UNICEF 2023 |
| `exam_steadying` | 考前紧绷稳住身体信号 | `academic`, `social_evaluative` / `sleep` | 3 步 / 😌 | `excl`: `unsafe_relationship` | Yeager 2022 · Dickerson 2004 |
| `kind_self_talk` | 把全盘苛责换回平实的说法 | `self`, `social_evaluative` / `self_criticism` | 3 步 / 🙂 | `excl`: `unsafe_relationship` | Lunn 2023 · Bluth 2024 |
| `comparison_reframe` | 从榜单横向比回到自己的基线 | `social_evaluative` / `self_criticism` | 3 步 / 😌 | `excl`: `unsafe_relationship` | Megalokonomou 2024 · Dickerson 2004 |
| `expectation_boundary` | 把父母的焦虑和自己节奏分开 | `relationship`, `social_evaluative` / `[]` | 3 步 / 😌 | `excl`: `unsafe_relationship` | Ding 2026 · Dickerson 2004 |
| `safe_communication` | 顺一句低压力的沟通说法 | `relationship` / `[]` | 3 步 / 🤔 | `req`: `safe_contact`; `excl`: `unsafe_relationship`, `no_private_space`, `bedtime` | Filia 2021 · Gulliver 2010 |
| `safe_support` | 挑一个让你放心的现实支持入口 | 全部五类压力 / `loneliness` | 3 步 / 🙂 | `excl`: `bedtime` | Zhao 2022 · Gulliver 2010 · WHO 2011 |
| `values_exploration` | 挑一个目前好奇的方向小问题 | `future` / `[]` | 3 步 / 🤔 | `excl`: `bedtime` | Chen 2022 · Ye 2019 |
| `worry_parking` | 睡前把一件担心先存我这儿 | `[]` / `sleep`, `rumination` | **2 步** / 😌 | `req`: `bedtime`; `excl`: `unsafe_relationship` | Scullin 2018 · Wang 2025 |

> 注：9 张策略卡在 `constraints` 中一致排除 `excluded_emotion_intensities: [high]` 与 `excluded_readiness: [low]`（高情绪唤醒或低准备度优先共情接住，禁止直接推策略执行）。

| 短练习 ID (`exercises/*.yaml`) | 名称 | 段落数 & 停顿总计 | 2026-11-21 实测音频总长 | 上下文准入 / 排除 | 文献依据 |
| --- | --- | --- | --- | --- | --- |
| `breathing_60s` | 自然呼吸小暂停 | 5 句 / 13.0s 停顿 | **43.5s** (`< 90s`) | `excl`: `body_focus_distress`, `unsafe_relationship` | Dunning 2022 |
| `grounding` | 看看身边的一样东西 | 4 句 / 11.0s 停顿 | **41.7s** (`< 90s`) | `excl`: `unsafe_relationship` | WHO 2011 |
| `bedtime` | 睡前短暂停 | 4 句 / 10.0s 停顿 | **39.0s** (`< 90s`) | `req`: `bedtime`; `excl`: `unsafe_relationship`, `body_focus_distress` | Scullin 2018 · Wang 2025 |

- **固定音频资产绑定**（`companion/docs/evidence/course-2.0-bench.json`）：上述 3 套练习连同固定迎新与安全提示，共预合成并校验 **24 段音频片段**。

### 2.3 单步许可状态机、负向瞻前词表与局部作用域边界

1. **7 阶段状态机**（[`core/models.py`](../../companion/core/models.py)）：`opening` · `explore` · `comfort` · `permission` · `action` · `closing` · `quiet`。
2. **`PendingOffer` 单步门控**（[`core/state_machine.py`](../../companion/core/state_machine.py)）：
   - 当用户发出求帮助问句（匹配 `rules.yaml` `ask`）且非拒绝时，在资格池内择优 1 项发出单步情境化邀请并进入 `permission`，有效期 `offer_valid_turns = 2` 轮。
   - **口语同意正则（负向瞻前保护）**（[`config/rules.yaml`](../../companion/config/rules.yaml)）：使用 `^(?!.*(?:难受|算了|不用|不想|不要|不愿|不行|不可以|没用))...`，既能承接“行吧你讲讲看”“可以呀试试”，又能防止“不是我不愿意”“难受算了”等含否定前缀话语被误判为同意。
   - **明确拒绝或哭声/高唤醒/纠错**：立刻清除 `pending_offer`、将目标记入会话拒绝集 `cards_refused` 或 `exercises_refused`，退回纯倾听（`explore`）；练习途中若出现明确拒听，清空 `resume_script_id` 永不强行续播，仅对无拒绝意涵的环境声响（中性中断）保留重评恢复入口。
3. **局部作用域边界（Scoped Boundaries）**：区分 `no_advice:current_topic`、`no_advice:<cluster>`（如 `future_track`）与 `no_topic_probe:<topic>`（如 `成绩`），通过 [`memory/concepts.py`](../../companion/memory/concepts.py) 的领域重叠函数 `targets_overlap()` 实现精细隔离——例如封锁数学排名追问时，仍能平滑承接睡前 `worry_parking` 或失眠安抚。
4. **重连防重复指引**（[`core/helpers.py`](../../companion/core/helpers.py) `resolve_opening`）：在新连接 `wake` 时查库确认历史是否存在用户 `user` 轮次；已有历史对话则直接跳过首见新手引导并检索可安全触发的 `followup`。

对应交互图谱：[`figures/en/02-strategy-taxonomy-consent-en.pdf`](figures/en/02-strategy-taxonomy-consent-en.pdf)（中文版：[`figures/zh/03-strategy-taxonomy.pdf`](figures/zh/03-strategy-taxonomy.pdf) · [`04-strategy-card-anatomy.pdf`](figures/zh/04-strategy-card-anatomy.pdf) · [`05-consent-boundary-fsm.pdf`](figures/zh/05-consent-boundary-fsm.pdf) · [`11-interaction-walkthroughs.pdf`](figures/zh/11-interaction-walkthroughs.pdf)）。

---

## 三、三线解耦架构与关键工程参数核准表

### 3.1 `settings.yaml` 权威模型分配与资源预算

直接核对于 [`companion/companion/config/settings.yaml`](../../companion/config/settings.yaml)：

| 角色 / 子系统 | 绑定模型 / 实现 | 超时 / 预算约束 | 职责边界 |
| --- | --- | --- | --- |
| **实时表达（Talker）** | `qwen-flash`（`enable_thinking: false`） | 首 Token 超时 `2500 ms`；总超时 `10 s`；最多 `3` 句 | 仅消费冻结 `TurnPolicyFrame`，受 `OutputRail` 黑名单约束 |
| **安全并发双层线（Risk）** | L1 正则词表 + L2 `qwen-flash` | 线程池 `4` workers；安全闸门 `400 ms`；分类总超时 `2500 ms` | 到 400 ms 未完则暂放正常输出；迟到 `high` 结果仍可递增 `generation` 中止播报 |
| **独立简报 & 增量核对（Brief / Delta）** | `qwen-flash` | 共享认知预算池 | `Brief` 并行生成盲审反证；`DeltaChecker` 对中途插话做单次兼容核对 |
| **情境分析 & 策略规划（Analysis / Planner）** | `gpt-4.1-mini` | `deliberation` 共享上限：`8 calls` / `6000` output tokens / `32000` total tokens / `20 s` deadline | 由紧凑格式契约替代全量 JSON Schema 注入，`Catalog` 前置确定性过滤 |
| **跨家族独立评议（Critic）** | `qwen-flash`（`critic_model`） | 最多触发 `1` 次退回修订 | 异构小模型独立审计 Planner 方案与原话证据，非行动纯倾听可触发 Fast-Path |
| **记忆抽取 & 结束蕴含核对（Memory / End + Grounder）** | 抽取 `gpt-4.1-mini`；核对复用 `qwen-flash` | `memory` & `end_consolidation` 各自 `2 calls` / `20 s` deadline（output 上限分别为 `1800` / `2400`） | 两阶段防幻觉记忆提交；`routine` 协作限制为 `4 calls` / `16000` total |
| **流式 TTS & Opus 端侧编码** | `gpt-4o-mini-tts`（音色 `coral`，`response_format: opus`） | 练习总长上限 `90 s`；`64` 项内存短语 LRU 缓存 | Talker 达 $\ge 8$ 字遇分句标点（闭合引号外）立即送 TTS，PyAV + `opuslib_next` 纯内存打包 `60 ms` Opus 帧 |

### 3.2 关键并发与持久化核心机制

1. **自适应非行动快路径（`fast_path_non_action`）**（[`cognition/orchestrator.py`](../../companion/cognition/orchestrator.py)）：仅当候选首版 `objective ∈ NON_ACTION`、`candidate_actions == []`、`local_issues == []` 且 **`not protects_active_offer`**（当前不存在处于 `permission` 阶段且已核准待同意的活跃邀约）时，直接跳过阻塞等待 `Brief` 与 `Critic` 进入出版闸门；从而在不覆盖活跃许可邀约的前提下大幅压缩日常倾诉后台跳数。
2. **四重版本号事务 CAS 与失效保护**（[`cognition/policy.py`](../../companion/cognition/policy.py) + [`orchestrator.py`](../../companion/cognition/orchestrator.py)）：
   - `DeltaGuard` 有效窗口严格封顶：`plan_ttl_s = 120 s` 且新增用户轮次 `plan_turn_delta <= 4`（到期不续期）。
   - `publish()` 在 `UserLock + SessionLock + SQLite Transaction` 内原子比对：(a) `topic_revision` & `policy_revision`（`control_revision`）；(b) 记忆提交前后的 `boundary_revision`；(c) `support_plan_version == base_plan_version` 及 `user_turns == checked_through_user_index`；(d) `memory_dependency_versions` 全部仍为活跃且 `lifecycle == "active"`、`mode == "normal"`。即使建议因版本冲突被 `final_cas_conflict` 拒绝，经来源核验的新记忆仍可走 `partial_commit` 安全落库。
   - **双 Plan ID 隔离**：`active_plan_id` 专职管理固定音频分段播放队列，`active_support_plan_id` 专职承载对话支持帧，二者互不混用；`generation` 单调递增取消过期分句队列与音频。
3. **来源蕴含记忆与 8 组概念簇**（[`cognition/consolidation.py`](../../companion/cognition/consolidation.py) + [`memory/concepts.py`](../../companion/memory/concepts.py)）：
   - `ConsolidationGrounder` 将用户原话设为 `PREMISE`、抽取记忆设为 `HYPOTHESIS` 做跨家族蕴含校验（非 `entailed` 立即剔除）；会话摘要 `extractive_summary()` 严格按 `summary_evidence` 中的 `user_turn` 原话逐字拼接（`<= 150` 字，杜绝模型脱离原文润色杜撰）。
   - **零依赖 8 组中文校园领域概念簇**：`parent_family`、`exam_grade`、`peer_school`、`future_track`、`sleep_burnout`、`appearance_self`、`time_plan`、`identity_name`。用户明确纠错（如“我是小琳，不是小林”）自动通过 `supersedes_id` 废止旧记录。
4. **端侧协议与数据库持久化**（[`xiaozhi_patch/`](../../../xiaozhi_patch/README.md) + [`companion/store/`](../../companion/store/)）：
   - 小智服务端固定上游提交 `92337881a7b6553614b47e137a774d02bf40512f`（6 处补丁，强制 `Bearer Token` 与 `device_id -> user_key` 服务端映射，支持 `SenseVoice` 声学表情信号 `Cry` / `SAD` / `FEARFUL` / `HAPPY`）。
   - SQLite `user_version = 2`，严格单写者进程租约 `WriterLease`，支持一致备份下的 `v1 -> v2` 事务迁移及断电后重启恢复未完成结束整理任务；Streamlit 运行观测台以只读模式 `uri=True, mode=ro` 连接 WAL 数据库（唯一写入动作仅限人工风险审核确认）。

对应系统矢量图：[`figures/en/03`–`07.pdf`](figures/en/)（中文版：[`figures/zh/06`–`10.pdf`](figures/zh/)）。

---

## 四、权威实测评估基准总表（严格来源溯源）

> **口径纪律**：下文不同批次测量的测试条件、语料集与日期严格分栏标注，绝不跨批次混用对比。

### 4.1 多轮合成质量回放（`companion/docs/evidence/course-2.0-bench.json`，`2026-11-21`）

- **配置组合与摘要**：Talker/Risk/Brief/Critic/Delta 使用 `qwen-flash`，Analysis/Planner/Memory/End 使用 `gpt-4.1-mini`；包摘要 `ff5ff4205060847bd9ec7cbfeb24361cc45ff48837eff8b4d0f04f8bbbfafbe1`；回放套件 `course-quality-2`（22 组合成场景覆盖全部 9 卡 + 3 练 + 安全边界 + 跨会话记忆）。

| 测量指标 | 早期参考基线（`2026-11-04`） | 当前系统实测（`2026-11-21`） | 相对变化 / 说明 |
| --- | --- | --- | --- |
| **场景与目标通过率** | 9/9 目标执行 | **22/22 场景通过 · 12/12 目标执行** | 含全部 9 张策略卡 + 3 段短练习与拒答/边界回归 |
| **后台任务执行分布 & 超时** | 2 个任务超时 / 2 个角色超时 | **0 超时**（69 项任务中：58 completed / 8 partial / 3 rejected） | `0 / 69` timeout（20s deadline 下零超时） |
| **后台认知协作耗时 P50 / P90** | `10729.5 ms` / `15422.6 ms` ($n=75$) | **`5889.1 ms` / `7389.3 ms`**（Max `8186.9 ms`, $n=46$） | **P50 `-45.1%` · P90 `-52.1%`** |
| **回放 Talker 首句 P50 / P90** | `1281.0 ms` / `1406.0 ms` ($n=41$) | **`1062.0 ms` / `1219.0 ms`** ($n=63$) | 首 Token P50 **`1000.0 ms`** / P90 `1063.0 ms` |
| **会话结束整理（`end_consolidation`）** | — | **P50 `7314.4 ms` / P90 `12034.3 ms`** ($n=23$) | 共享 2-Call / 20s 蕴含记忆与逐字摘要上限 |

### 4.2 流式文本与小智 WebSocket 环回 Opus 语音分阶段实测（`course-2.0-bench.json`，`2026-11-21`）

1. **流式文本核心探针（$n=30$ 连续对话回合）**：0 错误、0 回退（fallback）、0 风险降级——
   - **首 Token**：P50 **`1016.0 ms`** / P90 `1453.0 ms`（早期基线 P50 `1242.5 ms` / P90 `1625.0 ms`）
   - **首句完整切分**：P50 **`1109.5 ms`** / P90 `1578.0 ms`（早期基线 P50 `1398.5 ms` / P90 `1828.0 ms`）
   - **整轮文本完成**：P50 **`1202.5 ms`** / P90 `1656.0 ms`
2. **小智 WebSocket 环回 Opus 语音探针（$n=30$ 合成语音回合，0 失败，`end_status=done`）**：

| 语音流水线阶段 | 早期基线 P50 / P90 (`11-04`) | 当前实测 P50 / P90 (`11-21`) | 相对基线优化 & 注解 |
| --- | --- | --- | --- |
| **Talker 首 Token** | `1187.5 ms` / `1359.0 ms` | **`1000.0 ms` / `1078.0 ms`** | `-15.8%` P50 |
| **首句 / 400ms 安全闸门放行** | `1257.5 ms` / `1421.0 ms` | **`1101.0 ms` / `1203.0 ms`** | `-12.4%` P50（稳定并行门控） |
| **TTS 合成完成** | `3539.0 ms` / `3937.0 ms` | **`2507.5 ms` / `2890.0 ms`** | **`-29.1%` P50**（$n=28$ 未命中缓存回合） |
| **内存 60ms Opus 首包就绪** | `3586.0 ms` / `3984.0 ms` | **`2421.5 ms` / `2750.0 ms`** | **`-32.5%` P50**（绕过磁盘 WAV 读写） |
| **客户端首包到达（总端到端）** | `3609.0 ms` / `4015.0 ms` | **`2656.0 ms` / `3140.0 ms`** | **`-26.4%` P50**（Mean `2511.4 ms`, Min `1000.0 ms`, Max `3406.0 ms`；#20/`1172.0 ms` & #30/`1015.0 ms` 命中 64 项短语 LRU） |
| **服务端完整播报完成** | `9273.0 ms` / `11031.0 ms` | **`8101.5 ms` / `9781.0 ms`** | `-12.6%` P50 |
| **语音并发期间后台认知** | `12610.7 ms` / `15316.3 ms` ($n=8$) | **`6457.0 ms`** ($n=7$) | **`-48.8%` P50** |

### 4.3 静默安全守门矩阵（[`online-regression-20261109.json`](../evidence/online-regression-20261109.json)，`2026-11-09`）

- **测试条件**：$n=120$ 人工编制合成风险测试语料（`none=40 / watch=40 / high=40`，`label_status: developer-authored; pending independent review`），L2 采用 `qwen-flash`，`classifier_failures = 0`；小智危机抢断实测 `abort_to_stop_ms = 16.0 ms`。
- **核心指标**：`high_recall = 1.0` · `watch_recall = 1.0` · `false_high_rate = 0.0` · `timely_high_recall = 1.0`。

| 真实标签（$n=40$ / 类） | 分类器单独预测 (`none` / `watch` / `high`) | 词表 + 分类器联合预测 (`none` / `watch` / `high`) |
| --- | --- | --- |
| **`none` (40)** | `40` / `0` / `0` | `28` / `12` / `0`（零高危误报，仅 12 条保守进关注监控） |
| **`watch` (40)** | `0` / `37` / `3` | `0` / `37` / `3`（零漏报为无风险） |
| **`high` (40)** | `0` / `0` / `40` | `0` / `0` / `40`（**100% 召回且零故障**） |

### 4.4 来源蕴含记忆反事实核验（[`grounded-memory-20261109.json`](../evidence/grounded-memory-20261109.json)，`2026-11-09`）

- **8 组抽取边界回归**：精准过滤无主体片段输入（如孤立“早上9点至下午5点。”、`以后再聊` 不得上升为长期工作时间偏好），同时正确入库明确声明的持久事实（“我在广州读高中”）与会话级拒建议边界（“这次先别给建议。” -> `interaction_boundary / session`）。
- **6 组强制反事实审查**：4 组缺主体/泛化越界候选全部被 `ConsolidationGrounder` 拦截（`not_enough_information`），2 组有原话明确支撑的事实通过（`entailed`）。

### 4.5 离线回归与孤立包装迁移验证

- **离线代码门禁**（`./scripts/run.ps1 test`）：Ruff 规则检查通过，137 个源文件格式校验通过，全量离线 pytest **`224 passed, 1 skipped, 3 deselected`**（唯一跳过项 `test_course2_upgrades.py:310` 因根 `.venv` 未安装 `opuslib_next`，该库运行于独立小智环境 `vendor/xiaozhi-venv`；3 项被排除项为显式 `-m online` 在线用例）。
- **孤立 Wheel 与持久化迁移验证**：在隔离虚拟环境中验证 wheel 安装、4 角色后台协作、`v1 -> v2` 事务备份迁移、重复启动幂等与 CLI 运行正常。

对应基准剖析图：[`figures/zh/12-latency-benchmarks-zh.pdf`](figures/zh/12-latency-benchmarks-zh.pdf)（英文版：[`figures/en/09-latency-benchmarks-en.pdf`](figures/en/09-latency-benchmarks-en.pdf)）。

---

## 五、客观系统边界与局限性

1. **非临床定位与机制转译上限**：所涉 19 篇学术文献仅用于提炼低负担、可撤回、尊重边界的交互机制；系统定位为日常陪伴原型，**不作任何医学诊断、临床心理治疗效力或升学录取预测声明**。
2. **合成与成年人扮演验证边界**：全部对话测试、120 条风险语料与 22 段多轮回放均在合成语料及开发团队成员扮演条件下执行，风险语料标注尚待第三方独立心理专业复核，且未针对真实未成年人开展临床对照或实地量化评估。
3. **本机网络环回 vs 真机物理链路**：语音首包 P50 `2.66 s` 系同一宿主机下 `text -> TTS -> Opus -> WebSocket` 环回测量，已包含外部模型往返与并发认知负载，但**未包含**物理 ESP32 端侧 Wi-Fi 无线抖动、I2S 声学播放硬件缓冲与前端唤醒声学采样误差。
4. **概念渲染图说明**：展示站配图（[`docs/assets/companion-*.webp`](../../../docs/assets/)）为固定造型的概念视觉渲染，仅用于表达约 22 cm 桌面实体尺度与晚自习/床头在场氛围，不代表最终量产外壳结构或既定触控传感器规格。
