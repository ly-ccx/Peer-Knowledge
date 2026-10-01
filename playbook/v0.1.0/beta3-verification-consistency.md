# Beta3 核验与签收一致性补修

创建时间：2026-10-01
最后更新：2026-10-01

## 卡片

负责人授权修复核验结构化报告兼容与错误签收措辞。A 级，基于已 Accepted 的 ADR 80；前置补修 PR #74 已合入。只做这一项，不开启 Beta4，不修改发布标签与版本。

## 实现边界（实施前约束）

1. 核验只读取最终助手段，不把工具结果、思考或早期助手输出当成报告。允许完整 JSON、单个 JSON 代码块及文字包裹的单个完整报告；多份候选、字段类型错误、空输出均为格式失败。格式解析不能把字符串 `"true"` 或普通完成文字变成通过。
2. 格式失败最多再运行一次同样只读的 Verifier；原文本只作为限长用户事实回传，规则仍通过已登记的 Verifier Source / 临时 runtime reminder adapter 进入。合法的核验失败不重试；提供方失败、拒绝、取消、中断不通过格式重试掩盖。
3. 第二次仍不合法时返回明确失败，既有 Goal 闸门继续阻塞；不得补造 Evidence、criterionResults 或签收记录。
   - 2026-10-01 真实候选运行两次复现了核验目录漏绑：无会话 Verifier 回退到全局活跃目录，读取另一个项目后误判。沿用既有 sendMessage.workspacePath 参数，将 Explorer / Verifier 绑定到计划的 worktree、target 或原会话目录，最后才允许既有 workspaceRoot 兜底；不引入新参数、不借此扩大任务权限。补范围覆盖及格式重试保持同根的回归，重跑真实样本。
4. `post_reply` 引用任务时必须提供结构化 `statusClaims[{sessionId,status}]`，恰好覆盖 sources。宿主以当前任务投影逐项校验；不一致或缺失返回结构化错误及当前状态，不生成可见回复。`accepted` 投影仍只来自持久化 `resultAcceptance`，通过验证或未来可代签均不等于已经签收。
5. 回复携带宿主生成的 `sessionStates`；回复持久化后仍按既有流程尝试签收，再以持久化真值更新状态快照。模型正文用于发现和解释，不承担签收声明；L1 明确此规则，L7 提供当前状态。Renderer 只表达快照，不计算签收。
   - 用户稍后确认或取消任务时，对话读取按当前宿主投影刷新状态，避免历史回复继续显示待确认。只改读取投影，不重写历史正文或历史快照；逐页缓存任务查询，并校验项目归属。
6. 被拒绝的 `post_reply` 不允许经用户回合最终文本 fallback 重新显示。正常未调用 post_reply 的既有 fallback 保留；自由正文的所有语义无法由结构化状态校验全面证明，不宣称能消除全部模型幻觉。

## 允许改动

- 桌面 `agent-host/goal-runner-host.mjs` 及测试、新报告解析 Module 与测试；`agent-turn-executor.mjs` 仅处理现有 signal/abort seam，必要时补测试。
- `project-agent/project-facts.mjs`、`reply-composer-port.mjs`、`project-lifecycle-effects.mjs` 及相关集成测试。
- 既有 `tools/prompts/delegation/post_reply.md` 工具说明，沿用已登记的工具提示准入。
- runtime-node `project-agent/reply-composer.mjs`、`tool-specs.mjs`、`agent-turn-plan.mjs`、`delegation-provider.mjs`（透传已校验的状态错误事实）、`bot-directory.mjs`（只读状态投影刷新）及相关测试。
- protocol `delegation.ts` 的回复状态快照类型；system-context 项目规则和任务名册 Source 及测试。
- Renderer `conversation/ReplyBubble.tsx`、相关消息类型及测试；仅显示宿主状态。既有 i18n 没有完整的任务签收状态键，补同一组中英文状态文案，不显示原始状态码。
- 本交接与 `knowledge/architecture/project-agent-delegation-runtime.md` 补修契约。

## 必须回归

- 多轮输出 / JSON 包裹 / 重复报告 / 错误布尔与集合类型 / 空报告。
- 格式恢复成功、两次仍失败、合法未通过不重试、提供方失败与取消不重试。
- 任务阻塞但独立核验已过、confirm 待确认、真实已签收；错误声明拒绝且不落盘。
- 回复落盘后签收成功 / 关闭门拒绝；UI 快照与持久化签收一致；被拒绝回复不经 fallback 冒充成功。
- 定向及受影响包测试、build、typecheck、architecture:check、开发线 CI。

## 分支与提交

- 分支：`PeerAgent/pa/beta3-verification-consistency`。
- 代码基线：`f67ea97b92392b19dc5d440c1f939ad69d1d906c`；知识基线：`bec2313e25bcc4a621d67887ccf83714f5621377`。
- 实施前契约提交：`9917556`。
- 代码提交：`cd3d1283e405dab74916011a99f4de2365206a93` — `fix(project-agent): govern verifier reports and reply acceptance states`。
- 代码 PR：[Peer-Agent #75](https://github.com/ly-ccx/Peer-Agent/pull/75)，目标 `PeerAgent/dev/0.1.0`；尚未合入。

## 实现与验证交接

- 新 Verifier 报告 Module 接收最终助手段中的单个合法 JSON，拒绝重复、非法或不完整候选；只对格式失败做一次同权限重试，保留提供方失败、取消、拒绝和真实未通过路径。
- `post_reply` 的引用任务声明逐项核对当前宿主状态；错误返回真实状态，拒绝回复不能经最终文本 fallback 冒充成功。宿主生成状态快照，Renderer 在来源按钮表达当前状态。
- 签收尝试后按持久化投影更新快照；签收写入失败保留未签收状态与已写入的记忆。后续用户确认由对话读取刷新状态，历史正文及快照不改写；校验项目归属并逐页缓存查询。
- `pnpm build`、`pnpm typecheck`、`pnpm architecture:check`：通过。
- `pnpm test`：6478 项 Node 测试与 712 项 TUI 测试通过；0 失败、0 取消，保留 5 项既有 skip，无新增 skip。
- `pnpm --filter @peer-agent/desktop test`：5134 通过、5 项既有 skip；`pnpm --filter @peer-agent/system-context test`：29 通过。
- 最后界面收敛后，`pnpm --filter @peer-agent/desktop build` 与 `pnpm --filter @peer-agent/desktop typecheck` 通过。
- 最后候选解析审查加入“非法对象 + 合法报告”用例；`node --test apps/desktop/electron/main/agent-host/verifier-report.test.mjs`：5 通过。`git diff --check` 通过。
- 新回归覆盖格式恢复与耗尽、类型错误、最终段准入、取消/拒绝、假签收、confirm/auto 策略、签收写入失败、后续确认刷新、跨项目来源、记忆保留与拒绝 fallback。
- 首个代码提交 `cd3d128` 的 [开发线 CI](https://github.com/ly-ccx/Peer-Agent/actions/runs/36805472170)：macOS 14 与 Ubuntu 全部通过，PR 无合并冲突。
- 初次交接用隔离数据和脚本化模型；当时真实模型、手动桌面视觉未重跑，没有把历史真实样本计作本补修通过；Beta3 真实日用验收仍需后续卡，不进入 Beta4。
- 与卡片偏差：无；自由正文全部语义不可由结构化声明全面证明，下一步保留真实模型验收。

## 架构影响

收紧既有报告准入与回复状态声明，不新增能力与执行路径。权限、Evidence 和签收闸门不变；状态声明是模型请求，状态快照是宿主事实。`main.mjs`、sendMessage 参数、依赖、真实用户数据均不扩展。

## 真实验收后补修交接（2026-10-01）

- 实施前目录绑定契约：`8cc1da0`，只改本卡及 delegation runtime §14.1；实现：`6a4c5ecd7477a951ba5bbda1c6c532551abe3c00`，只改允许的 goal-runner-host 与测试。
- Explorer、文本 Verifier（含格式恢复）与视觉复核统一使用 worktree → target → conversation → workspaceRoot，重用既有 workspacePath 参数。
- 新回归先在旧实现失败，补修后 host/report 14 passed；desktop 5135 passed / 5 existing skipped；`pnpm --filter @peer-agent/desktop build`、`pnpm typecheck`、`pnpm architecture:check`、`pnpm test` 通过（6479 Node + 712 TUI，0 failed / 0 cancelled）；`git diff --check` 通过。
- 最新 `6a4c5ecd` [macOS/Ubuntu CI](https://github.com/ly-ccx/Peer-Agent/actions/runs/36806599692) 全通过。此前自动 Review 对象为 `cd3d128`，不冒充最新提交已重审。
- 真实模型完整零窗口样本：85 个采样均为 0，任务在此区间创建并 policy 签收；项目副本无改动。详细证据与余下缺口见 [真实验收 PR #6](https://github.com/ly-ccx/Peer-Knowledge/pull/6)。
- 三个 P1 未修：同一输入重复派发相似任务、文件 Evidence 披露 NOT_FOUND、熟悉项目人工确认及 Goal 核验通过后仍未签收/写 verified 记忆。确认 UI 普通点击失败另记，不把 preload 接口通过当 UI 通过。
- 范围偏差：目录错误在本卡既有允许范围内补修，契约先于实现；真实验收卡只保留证据。Beta3 未全部通过，不进入 Beta4、不发版、未自行合并。
