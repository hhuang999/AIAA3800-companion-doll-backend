# 项目站点维护说明

公开静态站发布源为 `main:/docs`，呈现面向中国初高中生日常升学压力陪伴的系统功能、策略协议与多 Agent 架构设计：

- [`docs/index.html`](index.html)：Warm Daylight × Teenage Engineering 旗舰交互主页（含 4 组升学日常情境状态机沙盒、三线解耦架构信号监视台、来源蕴含记忆与局部边界展区、9 卡 + 3 练策略协议检查器、11 张高清矢量图谱画廊与本地快速启动入口）。
- [`docs/research-design/index.html`](research-design/index.html)：完整研究与系统架构说明书在线阅读版（对应 Markdown 源文件 [`PROJECT_RESEARCH_AND_SYSTEM_DESIGN.md`](../companion/docs/research-design/PROJECT_RESEARCH_AND_SYSTEM_DESIGN.md)）。
- [`docs/showcase.html`](showcase.html)：兼容历史书签平滑跳转至 `./`。
- [`docs/assets/diagrams/`](assets/diagrams/)：`01-context-and-stressors` 至 `11-interaction-walkthroughs` 全套 11 张统一风格矢量 `SVG` 与 `@2x PNG` 工程图纸。
- **桌面玩偶概念图像资产库（统一造型，含 `-small.webp` 轻量移动端版本，来源说明见 [`image-provenance.json`](assets/image-provenance.json)）**：

| 资产名称 | 画幅比例 | 桌面端 / 移动端文件 | 应用位置与概念说明 |
| --- | --- | --- | --- |
| 阳光书桌主图 | `16:9` | [`companion-daylight.webp`](assets/companion-daylight.webp) / [`-small`](assets/companion-daylight-small.webp) | 首页 Hero 与仓库主页主图，确立暖白奶油羊毛玩偶参照形象 |
| 织物轻触近景 | `4:5` | [`companion-touch.webp`](assets/companion-touch.webp) / [`-small`](assets/companion-touch-small.webp) | 首页“记忆与边界”板块，展现温润无压迫的日常陪伴触感 |
| 硬件实体尺度 | `16:9` | [`companion-desk-scale.webp`](assets/companion-desk-scale.webp) / [`-small`](assets/companion-desk-scale-small.webp) | 约 22cm 掌心实体尺度对比（A5 硬壳本与中性笔旁）与短绒肌理 |
| 晚自习归来陪伴 | `16:9` | [`companion-study-night.webp`](assets/companion-study-night.webp) / [`-small`](assets/companion-study-night-small.webp) | 夜里十点半暖光台灯下安静在场、不催促刷题的低负担氛围 |
| 轻触唤醒与喊停 | `16:9` | [`companion-wake-gesture.webp`](assets/companion-wake-gesture.webp) / [`-small`](assets/companion-wake-gesture-small.webp) | 伸手轻拍肩侧示意触控唤醒或随时暂停，交互主权归学生 |
| 睡前床头安静在场 | `16:9` | [`companion-bedtime.webp`](assets/companion-bedtime.webp) / [`-small`](assets/companion-bedtime-small.webp) | 微光亚麻寝具与原木床头柜旁无屏幕光在场，衔接睡前认知卸载 |

## 更新与核验步骤

1. 更新 `companion/companion/config/` 中的策略卡、短练习或文献元信息并完成提交后，执行：
   ```powershell
   .venv/Scripts/python.exe scripts/build_project_site.py --revision HEAD
   ```
   导出脚本直接从干净的 Git 提交读取启用策略、短练习与文献来源至 `docs/assets/project-data.json`。
2. 如需重绘 11 张工程矢量图纸及 `@2x PNG`，可通过本机无头 Chrome 渲染并用视觉检视工具逐张核验无截断、无叠压。
3. 启动本地静态服务并用真实浏览器分别在 `1440×900` 与 `390×844` 核对零水平溢出、全资源 `200`、全部交互切换可用：
   ```powershell
   .venv/Scripts/python.exe -m http.server 8765 --bind 127.0.0.1 --directory docs
   ```
4. 本目录仅包含公开结构与合成交互示例，绝不存放密钥、令牌、数据库或个人隐私记录。
