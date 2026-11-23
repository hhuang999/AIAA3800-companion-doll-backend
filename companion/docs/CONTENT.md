# 课程内容准备与准入

适用范围：仅用于合成案例或成年团队成员角色扮演的课程研究原型，研究情境面向中国大陆初高中生日常升学与评价压力。当前默认内容包（`content_manifest.yaml` `version: course-2.0`）包含 **9 张支持策略卡**、**3 段 `< 90s` 可中止短练习**、**固定危机支持文本**，以及 **19 篇可追溯学术与公共卫生文献**（详情与全套对照表见 [双语系统规格与实测手册](reference-pack/SYSTEM_SPEC_AND_BENCHMARKS_ZH.md)）。

## 内容与证据

`cards/*.yaml` 的 `protocol` 保存机制、适配限制、版本、证据索引、最少信息门槛、适用与排除情境（`excluded_contexts` / `required_contexts`）、单步许可模板、行动步骤（共 8 张含 3 步，`worry_parking` 含 2 步，运行时受 `min(max_action_turns=4, len(steps))` 约束）、随时退出条件及反馈边界。当前全部 9 张启用策略 ID 为：

- `concrete_step`（从反复想转向具体的一步）
- `exam_steadying`（考前紧绷稳住身体信号）
- `kind_self_talk`（把全盘苛责换回平实的说法）
- `comparison_reframe`（从榜单横向比回到自己的基线）
- `expectation_boundary`（把父母的焦虑和自己节奏分开）
- `safe_communication`（顺一句低压力的沟通说法）
- `safe_support`（挑一个让你放心的现实支持入口）
- `values_exploration`（挑一个目前好奇的方向小问题）
- `worry_parking`（睡前把一件担心先存我这儿）

`exercises/*.yaml` 保存文本、句后停顿与 `ExerciseProtocol`：自然呼吸不屏气（`breathing_60s`，5 句 / 13s 停顿 / 实测 43.5s）、外部注意可睁眼（`grounding`，4 句 / 11s 停顿 / 实测 41.7s）、睡前暂停要求明确睡前情境（`bedtime`，4 句 / 10s 停顿 / 实测 39.0s）。哭声触发共情与安全评估；策略邀请、具体练习邀请与单步执行许可均由确定性状态机分别仲裁。

`content_manifest.yaml` 分开维护 19 项文献来源与实际阅读范围、逐条 SHA-256 自动核查记录，以及整包验收回执（`package_digest: ff5ff4205060847bd9ec7cbfeb24361cc45ff48837eff8b4d0f04f8bbbfafbe1`）。`status: enabled` 表示可供校验后的 `development` 使用，不替代专业临床或人工审核。修改任意策略卡或角色提示词须同步更新对应哈希与验收回执。

## 准备部署副本

在仓库根目录执行（自动读取 `.env` 中的 `AIHUBMIXKEY`）：

```powershell
.venv/Scripts/python.exe -m companion.tools.upgrade_config data/course-config
.venv/Scripts/python.exe -m companion.tools.prepare_audio --env-file .env --config-dir data/course-config --output data/fixed_audio --bind-config
./scripts/run.ps1 live --config-dir data/course-config --db data/course.db
```

配置升级工具会先校验完整副本并保留备份，对 `settings.yaml` 按“旧默认 / 现有值 / 新默认”三方合并；自定义提示词冲突会显式报错不静默覆盖。固定音频工具为 3 段短练习与固定接管共生成 **24 段音频** 并将真实 WAV 路径、实测时长（均 `< 90s`）与校验摘要写入部署副本的 `audio_manifest.json`（参见 [fixed-audio.json](evidence/fixed-audio.json)）。

## demo 放行条件

`--mode demo` 启动前强校验全部启用条目的协议完整性、19 项文献绑定、内容 SHA-256 摘要、24 段固定音频存在性与时长哈希，以及对应整包摘要的 22 场景真实模型多轮回放回执（`acceptance`）。缺失、失败、重复或过期回执均在边界处拒绝启动。最新基准与多轮回放汇总见 [`evidence/course-2.0-bench.json`](evidence/course-2.0-bench.json)（2026-11-21），来源蕴含记忆专项核验见 [GROUNDED_MEMORY.md](GROUNDED_MEMORY.md)。

## 修改后的验证

```powershell
# 运行静态检查与全量离线 pytest
./scripts/run.ps1 test

# 运行真实模型多轮回放验收（会调用配置模型并生成新证据目录）
.venv/Scripts/python.exe -m companion.tools.course_acceptance --config-dir data/course-config --final --output artifacts/course-replay-new
```

线上推理严禁直接读取研究全文或用语义相似度绕过策略资格条件；中文概念簇与关键词仅负责排序合格候选或边界防漏查，无匹配卡片时默认温和倾听。音频播报完成仅代表执行事件已发生，不直接推断干预有效性。
