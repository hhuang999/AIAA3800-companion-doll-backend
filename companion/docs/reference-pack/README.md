# 小伴 Companion：中英双语系统技术规格与图表素材包
# Bilingual System Specification & Figure Asset Pack

本目录归口维护 **小伴 Companion**（面向中国初高中升学日常压力的情感陪伴智能体后端与语音交互原型）的**纯客观系统技术规格、19 篇学术文献 BibTeX、实测基准汇总表，以及中英双套高清矢量图（SVG + PDF + `@2x PNG`）**。所有文本、参数与数值均核对自仓库源码、`settings.yaml`、`content_manifest.yaml` 与归档 JSON 证据，不依赖任何未采集的外部调研。

---

## 一、文档与文献索引 / Documents & Bibliography

| 文件 / File | 语言 / Lang | 用途说明 / Purpose |
| --- | --- | --- |
| [`SYSTEM_SPEC_AND_BENCHMARKS_ZH.md`](SYSTEM_SPEC_AND_BENCHMARKS_ZH.md) | 中文 | 完整技术规格、9 卡 + 3 练策略协议、19 篇文献映射、`settings.yaml` 参数核准、多轮回放/文本/语音/安全/记忆实测与局限 |
| [`SYSTEM_SPEC_AND_BENCHMARKS_EN.md`](SYSTEM_SPEC_AND_BENCHMARKS_EN.md) | English | Authoritative English counterpart covering problem space, consent FSM, three-lane architecture, empirical tables, and boundaries |
| [`references.bib`](references.bib) | BibTeX | 19 篇逐条核对的标准学术与公共卫生参考文献条目（可直接在 LaTeX / BibTeX 引用） |

- **底层 JSON 实测证据源**：[`course-2.0-bench.json`](../evidence/course-2.0-bench.json)（2026-11-21 多轮回放、文本流与小智环回 Opus 语音） · [`online-regression-20261109.json`](../evidence/online-regression-20261109.json)（2026-11-09 120 条静默安全守门矩阵） · [`grounded-memory-20261109.json`](../evidence/grounded-memory-20261109.json)（2026-11-09 抽取边界与 6 组反事实蕴含审查）。
- **工程与站点入口**：[`ENGINEERING.md`](../../../ENGINEERING.md) · [`PROJECT_RESEARCH_AND_SYSTEM_DESIGN.md`](../research-design/PROJECT_RESEARCH_AND_SYSTEM_DESIGN.md) · [`docs/index.html`](../../../docs/index.html)。

---

## 二、英文高清矢量图与延迟基准图库 / English Vector Figures (`figures/en/`)

以下全部 9 张英文图谱均提供无损矢量 **`SVG`**、单页 **`PDF`**（适合 LaTeX `\includegraphics` 直接插入）以及 `@2x` 高清 **`PNG`**（2400px 宽）：

| 编号 | 主题 / Subject | SVG | Vector PDF | High-DPI PNG |
| --- | --- | --- | --- | --- |
| **01** | Problem Space, Pathways & 19-Source Mechanism Mapping | [SVG](figures/en/01-problem-and-literature-en.svg) | [PDF](figures/en/01-problem-and-literature-en.pdf) | [PNG](figures/en/01-problem-and-literature-en.png) |
| **02** | Layered L1/L2 Taxonomy, PendingOffer Consent FSM & Boundaries | [SVG](figures/en/02-strategy-taxonomy-consent-en.svg) | [PDF](figures/en/02-strategy-taxonomy-consent-en.pdf) | [PNG](figures/en/02-strategy-taxonomy-consent-en.png) |
| **03** | Three-Lane Decoupled System Architecture & `CompanionCore` | [SVG](figures/en/03-system-architecture-en.svg) | [PDF](figures/en/03-system-architecture-en.pdf) | [PNG](figures/en/03-system-architecture-en.png) |
| **04** | Bounded Multi-Agent Deliberation, Fast-Path & Cross-Family Critic | [SVG](figures/en/04-multiagent-deliberation-en.svg) | [PDF](figures/en/04-multiagent-deliberation-en.pdf) | [PNG](figures/en/04-multiagent-deliberation-en.png) |
| **05** | Quadruple-Version Transactional CAS & `DeltaChecker` Arbitration | [SVG](figures/en/05-cas-concurrency-en.svg) | [PDF](figures/en/05-cas-concurrency-en.pdf) | [PNG](figures/en/05-cas-concurrency-en.png) |
| **06** | Source-Entailed Grounded Memory & 8 School Concept Clusters | [SVG](figures/en/06-grounded-memory-en.svg) | [PDF](figures/en/06-grounded-memory-en.pdf) | [PNG](figures/en/06-grounded-memory-en.png) |
| **07** | Streaming Clause TTS, In-Memory 60ms Opus & Fixed Exercises | [SVG](figures/en/07-voice-opus-pipeline-en.svg) | [PDF](figures/en/07-voice-opus-pipeline-en.pdf) | [PNG](figures/en/07-voice-opus-pipeline-en.png) |
| **08** | Three End-to-End Synthetic Interaction Walkthrough Traces | [SVG](figures/en/08-interaction-walkthroughs-en.svg) | [PDF](figures/en/08-interaction-walkthroughs-en.pdf) | [PNG](figures/en/08-interaction-walkthroughs-en.png) |
| **09** | Empirical Latency Breakdown, Replay Cognition & Safety Matrix | [SVG](figures/en/09-latency-benchmarks-en.svg) | [PDF](figures/en/09-latency-benchmarks-en.pdf) | [PNG](figures/en/09-latency-benchmarks-en.png) |

---

## 三、中文矢量图谱与基准图库 / Chinese Vector Figures (`figures/zh/` & `docs/assets/diagrams/`)

中文体系第 01–11 张架构/机制原图（SVG + `@2x PNG`）集中维护于 [`docs/assets/diagrams/`](../../../docs/assets/diagrams/)；本包 `figures/zh/` 额外导出全套 11 张无损单页矢量 **`PDF`** 与新增的第 12 张客观实测基准对比图：

| 编号 | 图谱主题 | 矢量 PDF (`figures/zh/`) | 对应公开 SVG / `@2x PNG` |
| --- | --- | --- | --- |
| **01** | 初高中升学五类压力源与四条共同通路 | [PDF](figures/zh/01-context-and-stressors.pdf) | [SVG](../../../docs/assets/diagrams/01-context-and-stressors.svg) · [PNG](../../../docs/assets/diagrams/01-context-and-stressors.png) |
| **02** | 心理学与 HCI 文献转译链 | [PDF](figures/zh/02-evidence-to-design.pdf) | [SVG](../../../docs/assets/diagrams/02-evidence-to-design.svg) · [PNG](../../../docs/assets/diagrams/02-evidence-to-design.png) |
| **03** | 分层陪伴能力全景（L1 + 9 卡 + 3 练） | [PDF](figures/zh/03-strategy-taxonomy.pdf) | [SVG](../../../docs/assets/diagrams/03-strategy-taxonomy.svg) · [PNG](../../../docs/assets/diagrams/03-strategy-taxonomy.png) |
| **04** | 单张支持策略卡 YAML 协议结构解剖 | [PDF](figures/zh/04-strategy-card-anatomy.pdf) | [SVG](../../../docs/assets/diagrams/04-strategy-card-anatomy.svg) · [PNG](../../../docs/assets/diagrams/04-strategy-card-anatomy.png) |
| **05** | 确定性状态机、单步许可与作用域边界 | [PDF](figures/zh/05-consent-boundary-fsm.pdf) | [SVG](../../../docs/assets/diagrams/05-consent-boundary-fsm.svg) · [PNG](../../../docs/assets/diagrams/05-consent-boundary-fsm.png) |
| **06** | 三线解耦系统总图与 Core 权威控制 | [PDF](figures/zh/06-system-architecture.pdf) | [SVG](../../../docs/assets/diagrams/06-system-architecture.svg) · [PNG](../../../docs/assets/diagrams/06-system-architecture.png) |
| **07** | 有界多 Agent 协作、快路径与跨家族互审 | [PDF](figures/zh/07-multiagent-deliberation.pdf) | [SVG](../../../docs/assets/diagrams/07-multiagent-deliberation.svg) · [PNG](../../../docs/assets/diagrams/07-multiagent-deliberation.png) |
| **08** | 四重版本号 CAS 发布与 DeltaGuard 控制 | [PDF](figures/zh/08-cas-concurrency.pdf) | [SVG](../../../docs/assets/diagrams/08-cas-concurrency.svg) · [PNG](../../../docs/assets/diagrams/08-cas-concurrency.png) |
| **09** | 来源蕴含记忆核对与八组概念簇召回 | [PDF](figures/zh/09-grounded-memory.pdf) | [SVG](../../../docs/assets/diagrams/09-grounded-memory.svg) · [PNG](../../../docs/assets/diagrams/09-grounded-memory.png) |
| **10** | 流式分句 TTS、内存 60ms Opus 与固定音频 | [PDF](figures/zh/10-voice-opus-pipeline.pdf) | [SVG](../../../docs/assets/diagrams/10-voice-opus-pipeline.svg) · [PNG](../../../docs/assets/diagrams/10-voice-opus-pipeline.png) |
| **11** | 三幕典型日常交互走查 | [PDF](figures/zh/11-interaction-walkthroughs.pdf) | [SVG](../../../docs/assets/diagrams/11-interaction-walkthroughs.svg) · [PNG](../../../docs/assets/diagrams/11-interaction-walkthroughs.png) |
| **12** | **本机环回语音/文本延迟与安全矩阵基准图** | [PDF](figures/zh/12-latency-benchmarks-zh.pdf) | [SVG](figures/zh/12-latency-benchmarks-zh.svg) · [PNG](figures/zh/12-latency-benchmarks-zh.png) |

---

## 四、无文字玩偶概念场景摄影素材库 / Concept Photography (`docs/assets/`)

全部 6 组场景均采用统一暖白奶油短绒玩偶设定（约 22 cm 卵石轮廓、双深棕小豆眼、极小圆耳、无屏幕、无按钮、零文字与零水印，详细提示词溯源见 [`image-provenance.json`](../../../docs/assets/image-provenance.json)）：

| 场景名称 / Scene | 比例 & 主图分辨率 | 轻量移动端分辨率 | 桌面主图 / 移动端文件 | 应用场景与表达重点 / Usage |
| --- | --- | --- | --- | --- |
| 日光书桌主视觉 | `16:9` · `1672×941` | `960×540` | [`companion-daylight.webp`](../../../docs/assets/companion-daylight.webp) / [`-small`](../../../docs/assets/companion-daylight-small.webp) | Hero 主视觉与造型核心基准；白日安静桌面在场 |
| 掌心尺度对照 | `16:9` · `1600×900` | `960×540` | [`companion-desk-scale.webp`](../../../docs/assets/companion-desk-scale.webp) / [`-small`](../../../docs/assets/companion-desk-scale-small.webp) | A5 硬壳本与中性笔旁真实尺度与织物质感 |
| 晚自习归来陪伴 | `16:9` · `1600×900` | `960×540` | [`companion-study-night.webp`](../../../docs/assets/companion-study-night.webp) / [`-small`](../../../docs/assets/companion-study-night-small.webp) | 夜晚暖光台灯旁无压迫静坐，不催促刷题 |
| 织物轻触近景 | `4:5` · `1122×1402` | `768×960` | [`companion-touch.webp`](../../../docs/assets/companion-touch.webp) / [`-small`](../../../docs/assets/companion-touch-small.webp) | 近景材质与跨会话记忆/边界温柔承接 |
| 轻触唤醒与暂停 | `16:9` · `1600×900` | `960×540` | [`companion-wake-gesture.webp`](../../../docs/assets/companion-wake-gesture.webp) / [`-small`](../../../docs/assets/companion-wake-gesture-small.webp) | 手部轻触肩侧示意主动唤醒或随时喊停，表达交互主权 |
| 睡前床头安静在场 | `16:9` · `1600×900` | `960×540` | [`companion-bedtime.webp`](../../../docs/assets/companion-bedtime.webp) / [`-small`](../../../docs/assets/companion-bedtime-small.webp) | 无屏幕刺眼光的微光卧室在场，衔接睡前认知卸载 |
