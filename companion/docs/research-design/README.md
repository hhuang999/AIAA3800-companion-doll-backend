# 研究背景、策略协议与系统架构说明书

本目录维护 **小伴 Companion**（面向中国初高中升学日常压力陪伴的多 Agent 语音与对话系统）的研究论证与系统设计长文源码：

- **在线阅读（GitHub Pages 说明书页）**：<https://hhuang999.github.io/AIAA3800-companion-doll-backend/research-design/>
- **在线互动展示主页**：<https://hhuang999.github.io/AIAA3800-companion-doll-backend/>
- **公开站点说明书发布文件**：[`docs/research-design/index.html`](../../../docs/research-design/index.html)
- **唯一 Markdown 编辑源文件**：[`PROJECT_RESEARCH_AND_SYSTEM_DESIGN.md`](PROJECT_RESEARCH_AND_SYSTEM_DESIGN.md)
- **中英双语系统规格、BibTeX 与实测基准素材包**：[`../reference-pack/README.md`](../reference-pack/README.md)
- **项目工程与运行入口**：[`ENGINEERING.md`](../../../ENGINEERING.md) · [`README.md`](../../../README.md)

## 正文结构与视觉资产

正文 [`PROJECT_RESEARCH_AND_SYSTEM_DESIGN.md`](PROJECT_RESEARCH_AND_SYSTEM_DESIGN.md) 涵盖 8 个核心章节与 3 份附录（模块映射、本地运行命令、19 篇学术文献标准参考文献表），统一采用标准“作者 + 年份”内嵌引用格式：

- **11 张高清工程矢量图谱**（SVG + `@2x PNG`，Warm Daylight × Teenage Engineering 规范）：集中维护于 [`docs/assets/diagrams/`](../../../docs/assets/diagrams/)（`01-context-and-stressors` 至 `11-interaction-walkthroughs`），英文矢量与延迟基准图维护于 [`../reference-pack/figures/`](../reference-pack/README.md)。
- **6 组统一造型玩偶概念摄影场景图**（含 `-small.webp` 轻量移动端版本）：集中维护于 [`docs/assets/`](../../../docs/assets/)（`companion-daylight`、`companion-touch`、`companion-desk-scale`、`companion-study-night`、`companion-wake-gesture`、`companion-bedtime`），生成提示词与来源说明见 [`image-provenance.json`](../../../docs/assets/image-provenance.json)。
- **内容配置数据源**：9 张支持策略卡、3 段 `< 90s` 可中止短练习与 19 篇文献由 `scripts/build_project_site.py --revision HEAD` 从提交树导出至 [`docs/assets/project-data.json`](../../../docs/assets/project-data.json)。

## 维护约定

- 在线阅读版（`docs/research-design/index.html`）与本目录 Markdown 正文保持口径唯一，已移除本目录早期的重复 `index.html` 副本，统一由 [`docs/research-design/index.html`](../../../docs/research-design/index.html) 对外提供阅读体验。
- 本目录下 `PLAN.md`、`FACT_CHECK.md`、`EDITORIAL_REVISION.md` 与 `sources/performance.json`（已标注 `archived_baseline_2026-11-04`）均为早期文稿演进归档记录；当前最新系统规格与实测基准以 [`../reference-pack/SYSTEM_SPEC_AND_BENCHMARKS_ZH.md`](../reference-pack/SYSTEM_SPEC_AND_BENCHMARKS_ZH.md) 为准。
