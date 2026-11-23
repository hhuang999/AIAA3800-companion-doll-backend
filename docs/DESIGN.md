# 小伴 Companion 展示站设计系统：Warm Daylight × Teenage Engineering

本规范适用于公开 GitHub Pages 旗舰互动主页 [`index.html`](index.html)、深度研究与架构说明书 [`research-design/index.html`](research-design/index.html) 以及 11 张矢量工程图纸 [`assets/diagrams/`](assets/diagrams/)。产品底层规则与真实后端实现见根 [`PRODUCT.md`](../PRODUCT.md) 与 [`companion/docs/reference-pack/`](../companion/docs/reference-pack/README.md)。

## 视觉定调与审美原则

站点融合 **Warm Daylight Tactility（暖光羊毛触感）** 与 **Teenage Engineering 硬件工程排版**：先让温润无压迫的实体陪伴形象与学习生活场景建立氛围，再以克制的细线标尺、状态胶囊、交互沙盒与高清矢量图谱清晰拆解多 Agent 工程系统。

- **反模板化节奏**：通过全幅日光摄影、`Editorial Pull-Quote` 叙事引语、高对比暗色信号监视台（`CompanionCore` 控制总线）、交替的鼠尾草绿记忆剖面以及网格画廊建立清晰节律，避免同质化白框堆砌。
- **门面层内容契约**：首页与说明书 100% 聚焦产品痛点、9 张支持策略卡 + 3 段短练习的交互设计，以及三线解耦架构；完整实验参数与系统压测归口于后端 [`reference-pack/`](../companion/docs/reference-pack/README.md)，不在展示站呈现单元测试通过数或延迟统计表。

## 色彩与字体令牌（Design Tokens）

| 用途 | 令牌值 | 说明 |
| --- | --- | --- |
| 主画布背景 | `#F5F5F1` / `#F7F3EC` | 暖白纸面与温润亚麻底色 |
| 卡片与对照区背景 | `#FFFFFF` / `#EFEAE0` | 高可读表面与柔和层次区分 |
| 核心文字 / 暗色控制台 | `#242824` / `#252C27` | 墨碳正文与 CompanionCore 深色控制面板 |
| 次要文字 / 细线边界 | `#5A6058` / `#D5D8D0` | 低饱和辅助说明与 1px 精密标尺 |
| 信号赤陶（交互强调） | `#BF471B` / `#E7612F` | 选中态、活跃通路脉冲与策略许可标识 |
| 鼠尾草绿 / 橄榄墨绿 | `#E3E7DC` / `#3B5246` | 记忆与边界保护模块 |

- **自托管字体**：`Manrope` + `Noto Sans SC`（见 [`assets/fonts/README.md`](assets/fonts/README.md)，OFL 许可），数字统一启用 `tabular-nums`，代码与阶段标识使用 `Consolas` / `JetBrains Mono`。
- **可访问性与动效**：支持 `prefers-reduced-motion` 自动降级；完整键盘可达（方向键切换图谱、Lightbox `Escape` 关闭与焦点恢复、原生语义控件）。

## 核心交互与资产清单

- **4 组升学日常情境交互沙盒**：基于合成演示流呈现“刚出成绩挫败倾听”“父母对比与单步许可”“晚自习疲惫与随时喊停”“睡前入睡困难与话题边界隔离”，严格标注合成示意属性，不调用外部 API。
- **三线解耦信号监视台**：交互切换实时表达线、有界后台认知线、静默安全与蕴含记忆线，呈现四重版本号 CAS 提交逻辑。
- **9 卡 + 3 练策略协议检查器**：动态读取 [`assets/project-data.json`](assets/project-data.json)，按压力场景筛选并展开机制说明、准入/排除规则与“作者 + 年份”标准文献引用。
- **视觉资产清单**：
  - 6 组无文字概念场景摄影图（[`assets/image-provenance.json`](assets/image-provenance.json)，均含 `-small.webp` 轻量移动端）：`companion-daylight`（16:9 主图）、`companion-touch`（4:5 触感）、`companion-desk-scale`（16:9 22cm 尺度）、`companion-study-night`（16:9 晚自习归来）、`companion-wake-gesture`（16:9 轻触唤醒/暂停）、`companion-bedtime`（16:9 睡前床头）。概念图底部不叠加侵入式文字说明条，仅用于生活质感与尺度示意。
  - 11 张矢量工程图谱（`assets/diagrams/01-context-and-stressors` 至 `11-interaction-walkthroughs`，SVG + `@2x PNG`）。
