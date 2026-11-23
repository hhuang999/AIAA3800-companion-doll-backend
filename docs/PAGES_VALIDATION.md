# 公开项目站点发布与验收记录

公开静态站点托管于 `main:/docs`，地址：

- 主互动展示站：<https://hhuang999.github.io/AIAA3800-companion-doll-backend/>
- 在线研究与架构说明书：<https://hhuang999.github.io/AIAA3800-companion-doll-backend/research-design/>

## 当前站点验收门禁（旗舰互动主页与独立说明书）

1. **数据源一致性**：[`assets/project-data.json`](assets/project-data.json) 由 [`scripts/build_project_site.py`](../scripts/build_project_site.py) 直接从目标 Git 提交的 `companion/companion/config/` 提取，包含全部 **9 张启用策略卡**、**3 段 `< 90s` 短练习** 与 **19 篇学术参考文献**。
2. **门面口径纯粹性**：公开展示站、说明书与 11 张矢量图谱均聚焦产品动机、交互机制与多 Agent 架构，不暴露内部编号（如旧条目编码/场景编号）、版本迭代词与本地压测统计表，全部文献统一渲染为标准“作者 + 年份”。
3. **浏览器真机实测（Desktop `1440×900` & Mobile `390×844`）**：
   - 主页与说明书 HTTP 200，零控制台异常（Console/PageError = 0），零静态资源加载失败；
   - 桌面与手机端 `scrollWidth <= clientWidth`，无横向页面溢出，移动端优先加载 `-small.webp` 轻量图像；
   - 情境沙盒切换/同意/拒绝、三线架构监视台切换、策略协议检查器筛选、11 张图谱 Tab/键盘切换与 Lightbox `Escape` 关闭全部可正常交互；
   - 历史静态入口（`index-v1.html`、`index-v2.html`、`showcase.html`、`architecture-course/`、`architecture-v2/`、`diagrams/`）均提供平滑跳转至当前主页或图谱区，保证外部书签零 404。

## 历史演进归档摘要

- **2026-11-04**：完成首次视觉重塑（Daylight 暖光材质与 Teenage Engineering 技术排版），引入自托管 `Manrope` + `Noto Sans SC` 字体。
- **2026-11-09**：将交互沙盒置顶首页并重构阅读版目录导航。
- **2026-11-19**：适配仓库更名 `hhuang999/AIAA3800-companion-doll-backend` 后的全部 GitHub Pages 与源码追溯基址。
- **2026-11-21**：完成门面层纯建筑化重写、6 组概念场景实拍级图库与 11 张工程矢量图纸上线；原有基于 `course-1.0` 六策略及早期测试数字的旧版静态页已平滑重定向并归档。
