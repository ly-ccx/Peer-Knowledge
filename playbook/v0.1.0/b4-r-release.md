# B4-R 发布实施契约

创建时间：2026-10-01
最后更新：2026-10-01

负责人明确授权完成全部 B4、必要路径、Review 修复、合入与发布。

## 基线与分级

B4-01 至 B4-08 已合入代码 dev `30496b04`；知识 PR #15 已合入 main `4f58bd0`。分支 `PeerAgent/pa/b4-r-release`。发布版本 `0.1.0-beta.4`。

发布前真实模型与桌面验收发现重复结果汇报、签收后的合回卡片未显示；本机并行 build 发现两个应用同时清理 conversation-store dist 的竞态。按 A 级先登记回复事实连续性契约；界面 / 构建 / 版本与发布材料属 B/C 级。

## 回复事实连续性

沿现有 canonical agent_reply.meta 增加宿主事实指纹，不新增存储路径、不重写旧消息；仅既有 onReplied 更新本次新回复的最终签收状态时同步事实键。指纹只由实际项目任务状态 / 独立核验引用及实际目标观察 Evidence 得出；模型文本、statusClaims 与任意引用不能生成事实。沿 ReplyComposer / post_reply 的既有 Provider / Grant / Evidence 路径执行。跨回合 / 重启读取已落盘回复，同一回合读取已成功工具结果；同一批事实只汇报一次，新状态 / 新观察 / 新用户输入仍可回复。无可核对事实时不做文本相似去重。

重复 post_reply 返回成功的 suppressed 回执并保留实际 Tool Result；finishAgentTurn 将其作为安静收尾，不生成假回复或“代理不可用”。不改变签收权限、不压制用户当前问题、不把模型 prose 当交付真值。普通事件唤醒不得借用历史用户锚点新开任务；只有当前用户输入或实际目标信号 / 已确认提议可授权。宿主已处理的合回卡片回答是具体任务的决策，不能再次作为新任务授权；Provider 在当前 canonical 输入全为合回回答时拒绝任务变更工具，查询 / 汇报仍可用。目标事件与普通任务事件同批唤醒时，普通任务的独立核验依据该批真实 session 事件仍可运行；无任务事件仍按目标范围拒绝。

## 实施路径

- runtime-node/project-agent：新的回复事实纯模块、delegation-provider 决策授权闸、llm-chat-service 既有 turnProfile 事件投影（不增参数）、reply-composer / agent-turn-plan 与定向测试；objective-tool-specs 校验失败返回具体字段路径以便模型修正，不接受坏字段或放宽权限。
- Desktop project-agent：reply-composer-port / project-facts / project-lifecycle-effects / 集成测试；renderer state/useBotConversation 与纯刷新协调模块、BotMessageList / ReplyBubble / CardView / ui/icons 的必要表达路径。既有 changed 与 conversation-changed 通道触发真实最新投影，虚拟卡片不得作为 canonical 游标，已解决卡片及时更新。证据默认有界显示，可展开全部；SVG 与自定义控件。
- i18n 必要中英文键；root package build 顺序修复，不新增依赖；main.mjs 净增 0。
- VERSION / package / Cargo / pnpm lock / README 标记 / release-notes / CHANGELOG 及既有发布脚本要求的文件。
- companion knowledge：本契约、交接 / 实际证据、ADR 80 回复连续性补充、版本计划 §5.2/§12.1、交付状态 D10。

## 验证与发布

先红后绿回归：重启 / 同回合 / 新用户不抑制 / 新事实可达 / suppressed 安静收尾；实际卡片更新与分页。全仓 build、test、typecheck、architecture、协议、版本、changelog/readiness。本机实际模型三条写任务独立隔离并签收 / 合回、取代恢复、真实观察与关窗；强杀恢复用已有真实生产宿主集成，不冒充真实模型。隔离 macOS arm64 安装首启、beta3 → beta4 → 0.0.18 → beta4 数据保留。最终双平台 CI / Review 后合入、tag、实际 prerelease 与 npm beta 验证。

未跑项目 / 跨平台交互安装 / 连续日用时长如实记入发布说明，不用自动测试代替。

## 2026-10-01 真实运行补充：文本任务的 UI 交付误判

候选 c556fb52 的三个文本写任务实际各改一个文件且三条并行。Goal 说明里的“用户会在界面上确认并合回”被现有 UI intake 分类器当成界面交付，导致错误武装视觉门并停在 judgment-missing。此处属于 B 级：在既有 goal-intake-ui-delivery 纯分类模块中排除明确的签收 / 合回操作语句，再分类真实交付物；不关闭已武装的门、不替模型产出核验、不改变 Evidence 或授权规则。涉及该模块与测试，既有真实 UI 目标及其 fail-closed 门仍须通过回归。旧样本的持久标记保留，修复后使用新的隔离样本重验，不人工篡改其核验状态。

真实 CI 失败送达验收使用仓库独立临时分支 `PeerAgent/pa/b4-r-ci-probe` 与专门的 `Beta4 probe fixture` workflow（明确标注故意失败），随后改为成功；不把夹具的失败写成产品 CI 回归。模型在本机隔离项目创建 failure_only 目标，既有只读 gh Provider 读取实际 Actions 结果。文件事件重复触发同一失败观察应只送达一次，成功结果应安静保留。该临时分支验证后删除，不合入开发线。

生产真实取代成功后恢复返回 supervisor_unavailable，发现 Desktop 的 liveDelegationSupervisor 适配器只转接旧五个方法，漏接 B4-03 已实现的 resume / reprioritize。补入既有 delegation-port.mjs 和生产 SDK 集成回归（实际 LocalToolHost / Grant / Evidence），无新协议、IPC 或权限。修复后重启同一个隔离样本，恢复实际已取代任务，沿保留的原计划 / worktree / 历史重验，不重建历史事实。
