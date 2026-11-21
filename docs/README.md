# 项目站点维护说明

公开静态站发布源为 `main:/docs`，呈现面向中国初高中生日常升学压力陪伴的系统功能、策略协议与多 Agent 架构设计：

- [`docs/index.html`](index.html)：Warm Daylight × Teenage Engineering 旗舰交互主页（含 4 组升学日常情境状态机沙盒、三线解耦架构信号监视台、来源蕴含记忆与局部边界展区、9 卡 + 3 练策略协议检查器、11 张高清矢量图谱画廊与本地快速启动入口）。
- [`docs/research-design/index.html`](research-design/index.html)：完整研究与系统架构说明书在线阅读版（对应 Markdown 源文件 [`PROJECT_RESEARCH_AND_SYSTEM_DESIGN.md`](../companion/docs/research-design/PROJECT_RESEARCH_AND_SYSTEM_DESIGN.md)）。
- [`docs/showcase.html`](showcase.html)：兼容历史书签平滑跳转至 `./`。
- [`docs/assets/diagrams/`](assets/diagrams/)：`01-context-and-stressors` 至 `11-interaction-walkthroughs` 全套 11 张统一风格矢量 `SVG` 与 `@2x PNG` 工程图纸。
- [`docs/assets/companion-daylight*.webp`](assets/) 与 [`companion-touch*.webp`](assets/)：暖光奶油羊毛桌面玩偶概念图像（来源说明见 [`image-provenance.json`](assets/image-provenance.json)）。

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
