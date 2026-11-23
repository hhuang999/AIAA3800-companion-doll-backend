# 小伴 Companion：产品定位与公开展示规范

## Platform

公开静态站点托管于 GitHub Pages（`main:/docs`），包含旗舰互动展示主页（`docs/index.html`）与深度研究及架构说明书（`docs/research-design/index.html`）。站点完全离线静态运行，不挂载任何在线对话 API 或私钥。

## Product and Audience

**小伴 Companion** 是基于 Python 3.10 模块化单体的情感陪伴玩偶后端与日常交互系统，聚焦中国初高中生在升学备考过程中的五类日常学业与评价压力情境。本原型仅面向课堂演示、合成测试案例与成年成员角色扮演验证，不构成心理健康诊断或临床干预产品。

公开仓库与展示站服务于课程教师、助教（TA）、研究者与端侧接入工程师：先通过真实学习生活质感建立“不催促刷题、交互主权归学生”的陪伴体验认知，再逐层深入策略协议、三线解耦架构与工程技术规格。

## Core Capabilities & Visual System

- **分层陪伴与策略体系**：L1 四态安全陪伴底座 + L2 9 张分级支持策略卡 + 3 段 `< 90s` 可随时中止短语音练习，全量可追溯至 19 篇教育心理学、社会学与情感支持对话文献（数据源：`docs/assets/project-data.json`）。
- **确定性内核控制**：独立安全风险兜底通道、`PendingOffer` 单步许可状态机与否定前瞻口语判定规则、有界多 Agent 后台协作与四重版本号 CAS 仲裁、来源蕴含约束关系记忆与 8 组校园领域概念簇、以及面向 ESP32 语音网关的内存 60ms Opus 流式管线。
- **视觉体系（Warm Daylight × Teenage Engineering）**：主展示站与说明书采用自托管 `Manrope` + `Noto Sans SC` 字体与 `#F5F5F1` / `#F7F3EC` / `#BF471B` / `#242824` 暖光工程调色板；搭配 11 张矢量工程图谱（`docs/assets/diagrams/`）与 6 组无文字概念场景摄影图（`docs/assets/companion-*.webp`，仅作桌面尺度与触感概念示意，不代表已定型量产硬件）。
- **门面与学术资料分层**：公开展示站与仓库主页 `README.md` 专注呈现产品动机、交互功能与底层架构；系统完整技术参数、BibTeX 参考文献与各项基准实测汇总统一维护于 [`companion/docs/reference-pack/`](companion/docs/reference-pack/README.md)。
