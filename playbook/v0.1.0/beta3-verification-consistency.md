# Beta3 核验与签收一致性补修

创建时间：2026-10-01
最后更新：2026-10-01

## 卡片

负责人授权修复核验结构化报告兼容与错误签收措辞。A 级，基于已 Accepted 的 ADR 80；前置补修 PR #74 已合入。只做这一项，不开启 Beta4，不修改发布标签与版本。

## 实现边界（实施前约束）

1. 核验只读取最终助手段，不把工具结果、思考或早期助手输出当成报告。允许完整 JSON、单个 JSON 代码块及文字包裹的单个完整报告；多份候选、字段类型错误、空输出均为格式失败。格式解析不能把字符串 `"true"` 或普通完成文字变成通过。
2. 格式失败最多再运行一次同样只读的 Verifier；原文本只作为限长用户事实回传，规则仍通过已登记的 Verifier Source / 临时 runtime reminder adapter 进入。合法的核验失败不重试；提供方失败、拒绝、取消、中断不通过格式重试掩盖。
3. 第二次仍不合法时返回明确失败，既有 Goal 闸门继续阻塞；不得补造 Evidence、criterionResults 或签收记录。
4. `post_reply` 引用任务时必须提供结构化 `statusClaims[{sessionId,status}]`，恰好覆盖 sources。宿主以当前任务投影逐项校验；不一致或缺失返回结构化错误及当前状态，不生成可见回复。`accepted` 投影仍只来自持久化 `resultAcceptance`，通过验证或未来可代签均不等于已经签收。
5. 回复携带宿主生成的 `sessionStates`；回复持久化后仍按既有流程尝试签收，再以持久化真值更新状态快照。模型正文用于发现和解释，不承担签收声明；L1 明确此规则，L7 提供当前状态。Renderer 只表达快照，不计算签收。
6. 被拒绝的 `post_reply` 不允许经用户回合最终文本 fallback 重新显示。正常未调用 post_reply 的既有 fallback 保留；自由正文的所有语义无法由结构化状态校验全面证明，不宣称能消除全部模型幻觉。

## 允许改动

- 桌面 `agent-host/goal-runner-host.mjs` 及测试、新报告解析 Module 与测试；`agent-turn-executor.mjs` 仅处理现有 signal/abort seam，必要时补测试。
- `project-agent/project-facts.mjs`、`reply-composer-port.mjs`、`project-lifecycle-effects.mjs` 及相关集成测试。
- 既有 `tools/prompts/delegation/post_reply.md` 工具说明，沿用已登记的工具提示准入。
- runtime-node `project-agent/reply-composer.mjs`、`tool-specs.mjs`、`agent-turn-plan.mjs`、`delegation-provider.mjs`（透传已校验的状态错误事实）及相关测试。
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
- 实现与检查结果待补；没有把历史真实样本计作本补修通过。

## 架构影响

收紧既有报告准入与回复状态声明，不新增能力与执行路径。权限、Evidence 和签收闸门不变；状态声明是模型请求，状态快照是宿主事实。`main.mjs`、sendMessage 参数、依赖、真实用户数据均不扩展。
