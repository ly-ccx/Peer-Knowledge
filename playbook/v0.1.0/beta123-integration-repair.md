# Beta 1–3 桌面集成补修

创建时间：2026-09-30
最后更新：2026-10-01

来源：负责人要求复核前 3 个 Beta，并补齐发现的遗漏。

## 卡片

Beta 1–3 已接受能力的集成补修。范围包含生产装配、回复与任务事实、生命周期、卡片交互和机器人策略设置，不开启 Beta4 能力。

## 分支与提交

- 代码与知识分支：`PeerAgent/pa/beta123-integration-repair`。
- 代码目标分支：`PeerAgent/dev/0.1.0`；知识目标分支：`main`。
- 代码 PR：[Peer-Agent #74](https://github.com/ly-ccx/Peer-Agent/pull/74)；知识 PR：[Peer-Knowledge #4](https://github.com/ly-ccx/Peer-Knowledge/pull/4)。
- 代码提交（按顺序；原 228 / 6456 测试结果对应 `abc4ee76`，本文 6463 全量结果对应 `abb2f5af`）：
  - `abc4ee769ce6b26fa95ce7901f093b883a1dfcb7` — `fix(project-agent): complete Beta 1-3 desktop integration`
  - `aaf2b1374f6ec24e5127a9fa7d7b09c7250a0df4` — `fix(project-agent): recover queued inputs and expose anchored Goal criteria`
  - `3ea49ce4b8401a9443dbbb022a5239c3299649e2` — `fix(goal): retain criterion IDs and checks in plan readback`
  - `abb2f5af2259a40bfd9880db6944d7bbf77eb5f1` — `fix(project-agent): drain persisted inbox after lease recovery`
  - `a6a2c7f862ddc84d390ebd895a031bd861aa6525` — `fix(project-agent): keep projected cards out of pagination cursors`

## 合并前 Review 补修（2026-10-01）

- 代码 PR 的分页评论已复现：未落盘的未解决卡片追加到首页后，`nextCursor` 错指该卡片，下一页找不到持久化消息编号而重复首页。现在在追加投影卡片前从持久化分页切片计算游标。
- 新回归覆盖首页提示卡、已解决卡片不投影、下一页历史不重复及末页游标为 null；改动前失败，修复后通过。
- `a6a2c7f8` 本地检查：受影响 runtime-node 包构建通过，完整测试 826 通过、0 失败、0 取消、0 跳过；`pnpm typecheck`、`pnpm architecture:check` 通过。该补修为 C 级局部错误修复，未改变协议、权限、上下文或存储边界。
- 知识 PR 的时间字段已齐全；运行时架构文档已标注最后更新为 2026-09-30；本次补齐了交接文档的具体提交、消息和 PR 链接。GitHub 原 review threads 尚未标记 resolved，内容修复与界面状态需区分。

## 改了什么

| 审查遗漏 | 补修与回归 |
|---|---|
| 正式宿主缺模型解析 | 项目代理和任务都使用现有 ModelRouter，传入项目策略并冻结任务选择 |
| 默认调度 Provider 未接监督者 | 安装调用时解析的监督者与持久化账本，实测 Projection → Grant → Evidence |
| 拒绝的 post_reply 仍可变成回复 | 只接受成功 Tool Result，使用宿主校验后的结构化消息 |
| 任务名册与唤醒事实没有进模型上下文 | 进入 turnProfile.context，经已注册的 project-roster Source 放入 L7 |
| 熟悉项目、空项目职责、README、verified 记忆没有生产调用 | 调度只读 research；保存 stated 职责；用户接受后创建 docs；核验通过且有来源才写 verified 记忆 |
| 错误终态变成空成功回复 | error / aborted / interrupted 与流错误进入失败；无有效用户回复生成可重试卡 |
| 回合与回复 id 重启冲突 | 回合 UUID；重启恢复原输入，不重复用户消息 |
| 确认结果、README、重试卡缺操作链 | 补 IPC、preload、应用服务、Renderer；检查归属、状态和重复点击 |
| 批准、签收、模型策略缺保存与界面 | 更新档案前整体校验；自定义下拉、模型范围和本地限制；列表保留完整档案，保存后立即刷新 |

额外发现并修复：任务完成不等于已签收；复核结束退出 verifying；小结保留任务、结论与 Evidence 引用；来源归属覆盖模型列表 50 条以外的任务；宿主退出释放安装端口。下拉的字符勾号替换为 SVG。

## 真实验收继续发现的缺口

- 启动租约取得前收到的持久输入没有被后台巡检再次消费：巡检恢复队列消费、游标与既有去重路径。
- 代理拿不到当前输入的稳定消息编号：把限长输入锚点与任务来源编号作为 L7 事实，执行仍校验持久化原消息。
- `spawn_session` 只接受字符串标准，全部归为 manual，阻断 auto 签收：补既有 GoalSuccessCriterion 对象入口，保留旧字符串的人工确认约束。
- 重启后旧收件箱事件不被巡检唤醒：持租约巡检检查既有待确认批次，不只依赖新发布事件；空收件箱无模型调用。
- Goal L7 与 `goal_get_plan` 丢掉标准编号、检查参数，任务有 Evidence 仍卡在 criterion_unverified：保留白名单读回字段；L7 超长参数提示回查，完成门不变。

## 与卡片的偏差

这次由负责人直接授权补审查遗漏，跨越原来的多张卡，不按单卡文件范围拆开。新增独立的项目事实、策略校验、生命周期效果 Module，集中装配逻辑；`main.mjs` 净增 0 行，无新依赖、无新 sendMessage 参数。

## 验证

- `pnpm build`、`pnpm typecheck`、`pnpm architecture:check`、桌面 `ipc:check` 通过。
- 定向命令：`node --test apps/desktop/electron/main/project-agent/*.test.mjs apps/desktop/electron/main/agent-host/agent-turn-executor.test.mjs packages/runtime-node/src/project-agent/*.test.mjs`；原补修 228 通过，0 失败、0 取消、0 跳过。
- 全量 `pnpm test` 通过：6463 通过、0 失败、0 取消、5 个既有跳过。新增用例无跳过。该自动化命令使用隔离目录和脚本模型服务；真实模型验收另列。
- 新增契约 / 恢复回归：Goal Source 与 Goal Provider 定向 28 通过；Project Agent Host 定向 6 通过。
- 新增测试：`beta-integration.test.mjs`、`desktop-integration.test.mjs`；补取消桥接和小结引用持久化测试。
- 隔离 Electron 源码实例：实际点击计划批准、签收、固定模型、范围与本地限制，检查磁盘档案，并关闭、重开档案验证显示值；检查无原生 select、勾号为 SVG。

![隔离实例的策略设置](evidence/beta123-policy-settings.png)

## 真实项目与重启记录

- 模型为 `glm-5.3-flash`，项目是 Peer-Agent、Peer-Knowledge、SillyTavern 的 tracked git archive 隔离副本。三者完成文件读取、结构化标准回写、独立核验、带来源回复、宿主 `acceptedBy: policy` 签收；每条标准的 Evidence 引用都能在宿主索引查到。
- 首轮时间上限内两个已签收，一个已核验但尚未收尾。第一次重启暴露旧收件箱未唤醒，补修 `abb2f5af` 后的本地安装包自动恢复，未增加用户消息或新任务，三个原 sessionId 全部已签收。
- Source 实例关窗区间中 BrowserWindow 数量为 0，Peer-Knowledge 的 Goal 在该区间建立并启动；文件读取 Evidence 在恢复窗口后入索引。不能把这个记录扩写成“整段任务全程无窗口完成”。
- 三个隔离副本的 tracked 文件逐项与原提交的 Git blob 比较，内容无变化。原 Knowledge 仓在测试期间收到本轮自身的交接编辑；模型任务只读隔离副本。测试进程均经 owned registry 确认退出，隔离凭据副本已移除。
- 记录：[三个真实项目与恢复](evidence/beta123-real-projects.json)。回放过程使用既有开发 credential helper；安装包通过既有 `PEER_CREDENTIAL_HELPER_PATH` 配置选择该 helper。临时 ad hoc 签名 helper 的钥匙串超时仍单独记录，不能据此宣称默认签名包凭据路径通过。
- 额外一次新建安装包任务中，Goal verifier 没有返回结构化报告，Goal 保持 blocked；即使另一轮独立核验通过、助手文本声称签收，宿主也没有写入 resultAcceptance。这个失败样本不计入成功链路，文本措辞与宿主状态存在偏差，需要后续收口。

## 架构影响

沿用 Provider → Manifest → Projection → Tool Call → PermissionGrant → Evidence。Renderer 只经契约 IPC 交互，权限与执行留在本地宿主；L7 只接收事实，L6 只保留行为提醒。新策略字段属于既有 BotProfile，旧档案读取默认值，不批量重写。完整项目事实集合是宿主内部查询，模型 list_sessions 仍限 50 条。

## 文档偏差

前三个 Beta 的模块与标签已经发布，但生产装配并未形成完整可用链路。本文记录补修证据，不把已发布标签等同于真实场景验收通过。

## 未完成与后续

- Beta1 已补关窗期间建立并启动 Goal、待批准计划重启回读、macOS 安装应用冒烟；完整无窗口任务交付与真实视觉复核仍未补证。
- 空目录职责声明的实际 UI 已补证：用户输入 → stated / pinned 记忆 → 档案回查 → 撤销 → 恢复。见 [记忆 UI 记录](evidence/beta123-memory-ui.json)。非空项目熟悉任务 → verified 事实记忆的真实模型链仍未补证。
- Beta3 已补实际历史升级保留与来源 Evidence 查验；真实插话 / 按档位送达以及负责人连续日用 5 天仍未补证。
- macOS arm64 的实际安装应用冒烟已补：0.0.18 → beta.1 → beta.2 → beta.3 → 候选包 → 0.0.18 → 候选包；历史会话、档案和记忆 SHA256 一致。Beta2 缺自动建档，后续步骤显式用了夹具继续数据保留检查，不能把 Beta2 判为全通过。候选包首启、已有目录建档与待批准计划重启可回读已通过。见 [安装迁移记录](evidence/beta123-installed-migration.json)。Linux / Windows 安装矩阵仍未补证。
- 补修提交 `abb2f5af` 的 [macOS / Linux CI](https://github.com/ly-ccx/Peer-Agent/actions/runs/36738410014) 均通过。合入由负责人决定，本次不打新 tag、不改发布状态。
