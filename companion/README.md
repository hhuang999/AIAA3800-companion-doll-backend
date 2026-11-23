# companion-backend

Python 3.10 情感陪伴玩偶后端。包含独立 CLI、实时 Talker、后台有界多角色协作、确定性许可状态、风险接管、练习计划、四类有来源和范围的 SQLite 关系记忆和 Streamlit 看板。

当前维护与验证见 [工程 review](docs/ENGINEERING_REVIEW.md)。完整仓库的接手入口为根 AGENTS.md 与 [ENGINEERING.md](../ENGINEERING.md)；以下升级材料中的原始任务已经完成。

```sh
python -m pip install -e '.[test]'
companion --fake
companion --env-file /path/to/.env
companion-dashboard --db data/companion.db
pytest
```

默认 development 启用 9 张分级支持策略卡、3 段 `< 90s` 可中止短练习与固定危机支持文本（关联 19 篇学术文献依据）。仅用于合成案例或成年成员课程原型验证；demo 准入另核验来源、逐项回放、摘要与音频。当前系统规格与实测汇总见 [`docs/reference-pack/README.md`](docs/reference-pack/README.md)；内容准入与早期记录见 `docs/CONTENT.md`、`docs/VALIDATION.md`。完整项目的 Windows 安装 / 运行脚本及小智补丁位于此包上层的项目仓库。

## v2 默认路径

Analysis 解释有限证据，Planner 生成候选策略；deliberation 另并行生成独立 Brief，再由跨家族 Critic 绑定确切版本评审，最多修订一次并复核（非行动纯倾听/共情且无活跃邀约时走自适应 Fast-Path）。routine 只发布非行动策略。Core 冻结 TurnPolicyFrame，控制变化、记忆版本、TTL、DeltaChecker 与四重版本号 CAS 共同决定是否采用。行动仍由原有许可状态机与卡片 Validator 决定。

`/policy`、`/memory`、`/jobs` 可观察该路径；默认配置含各角色模型及调用/token预算。FakeLLM 与 Aihubmix 走同一协议。

- [中英双语权威系统规格与图表素材包](docs/reference-pack/README.md)
- [运行、迁移、重试、清除与 wheel 验证](docs/V2_OPERATIONS.md)
- [2026-11-21 基准实测汇总（JSON）](docs/evidence/course-2.0-bench.json)
- [小智协议、凭据与联调交接](docs/XIAOZHI_HANDOFF.md)
- [在线互动展示站](https://hhuang999.github.io/AIAA3800-companion-doll-backend/)
- [在线研究与架构说明书](https://hhuang999.github.io/AIAA3800-companion-doll-backend/research-design/)
- [完整安装与运行说明](../ENGINEERING.md)

`python -m companion.tools.migrate --db data/companion.db` 可停服升级。v1→v2 先作 SQLite backup，再事务迁移；未知更高版本拒绝，回退恢复备份到新路径。wheel 包含所有配置、七角色提示词和迁移 SQL。
