# 会话运行时状态按 conversationId 分桶（消灭跨会话串内容）

日期：2026-07-01
最后更新：2026-11-15（规范标注 Accepted，并标明后续向 [ADR 87](87-user-turn-live-process-presentation.md) 与 [ADR 121](121-desktop-session-windowing-contract.md) 的演进）
分支：`dev/0.0.1`
状态：Accepted（自动化验证通过；按 `conversationId` 分桶与跨流路由原则已由 [ADR 87](87-user-turn-live-process-presentation.md) 的多路过程表达及 [ADR 121](121-desktop-session-windowing-contract.md) 的有界会话窗口进一步扩展）

本文记录一次架构级根治：把「新建会话/切换会话时串入其他会话内容」的 bug，从反复打补丁转为从状态形态上根除。

## 背景与现象

用户反馈两类串扰：

- 新建一个会话，界面却带入了其他会话的消息/用量。
- 在会话之间快速切换，前一个会话的内容会短暂或持续出现在后一个会话里。

尤其在有后台流式（某会话正在逐字输出时切走）场景下更明显。

## 根因：两份状态各自独立，没有原子绑定

渲染层当时**没有任何状态库**（无 zustand / jotai / redux / valtio，也未用 `useSyncExternalStore`）。会话运行时状态是 `ChatSurface` 组件内的一大堆并列 `useState`/`useRef`：`messages`、`isStreaming`、`isCompacting`、`compactionPercent`、`streamError`、`tokenUsage`、`activeUsage`、`authoritativeContext`、`providerRecoveryNotice`、`toolProgress`、`pendingPermissionCalls`、`streamId` 等十几份。

真正的病根不是「切换时忘了清空 messages」，而是更深一层：

> **会话身份（`conversationId`）与会话内容（十几份 state）是两份互相独立的状态，彼此之间没有原子绑定。**

于是任何「切会话」都退化成「先把 id 改掉，再用一串 `setState` 去追平内容」。十几个 `setState` 不可能与 id 变更真正原子化，因此**架构上必然存在一个「id 已是新的、内容还是旧的」中间态**；`messages` 还要等异步 IPC 加载完才追平，窗口尤其大。

此前评估过的三个方案——切换时抢先清空（治表现）、发送时加判断（治污染）、`key={conversationId}` 重挂载（粗暴隔离且丢流订阅）——都只是在和这个中间态赛跑，没有动病根。

## 决策：按 conversationId 分桶的外部 store + 应用级单例流路由器

把会话运行时状态全部移出组件，进入一个以 `conversationId` 为 key 分桶的外部 store。组件按 `conversationId` 订阅对应切片。**切会话 = 换订阅 key，物理上不存在「一份被复用的 messages 槽位」，跨会话串内容在架构层面不可能发生。**

配套引入一个应用级单例流路由器：主进程流事件只携带 `streamId`，路由器按 `streamId → conversationId` 反查归属桶后落桶，从根上杜绝「事件落到当前前台会话」的盲写。

### 关键不变式

- 流事件真值仍在主进程（发送/账本/reattach 不变），renderer 只做投影。
- 每一类流事件都先 `resolveConversation(streamId)` 解析出 `cid`，再 `setState(cid, ...)`。
- 解析不出归属的流一律 `if (!cid) return` 丢弃，**绝不盲写前台桶**。
- `activeRef`（当前前台会话）只用于「要不要走前台打字机动画/浏览器联动」的展示分支，**不参与落桶归属判定**。
- 前台会话 delta 走打字机逐字动画；后台会话 delta 直接整段写桶（1A 取舍：后台不做逐字动画，换取实现简单与低风险）。

## 落地改动（代码仓 `peer_agent`）

| 文件 | 说明 |
| --- | --- |
| `apps/desktop/renderer/src/chat/state/conversationStore.ts`（211 行，新增） | `Map<conversationId, ConversationRuntimeState>` + `streamId→conversationId` registry + 不可变快照 + actions（`setState`/`routeStream`/`resolveConversation` 等） |
| `apps/desktop/renderer/src/chat/hooks/useConversationState.ts`（71 行，新增） | 基于 `useSyncExternalStore` 的订阅 hook，返回当前会话切片与稳定 action 句柄 |
| `apps/desktop/renderer/src/chat/hooks/useConversationStreamRouter.ts`（533 行，新增） | 应用级单例流路由器：13 类流事件全部按 `streamId→cid` 落桶 |
| `apps/desktop/renderer/src/chat/components/ChatSurface.tsx`（改造） | 策略甲「薄适配」：移除会话级 `useState`，改从 `useConversationState` 读、经 actions 写；保留纯 UI-local state（draft/attachments/imagePreview/slash/scroll 等）。约 200+ 调用点零改动，改造收敛到约 12 处声明 + 切会话路径 |
| `apps/desktop/renderer/src/chat/hooks/useChatStreamSubscription.ts`（477 行，删除） | 旧「单 streamIdRef 过滤」订阅被路由器取代 |

### 为什么路由器挂在 ChatSurface 而非重挂载

切会话只改 `conversationId` prop、**不重挂载** ChatSurface，因此路由器的 `useEffect` 订阅「挂载一次、永不重绑」，是**全应用唯一**的流订阅。这既避免了 `key` 重挂载丢失后台流订阅的老问题，也保证订阅生命周期与任何单个会话解耦。

6 个流起点/reattach 点（submit / retry / goal-runner / compact / compact 续接 / live 续接）在起流时统一登记 `routeStream(streamId, cid)` 并写桶 `{streamId, turnStartedAt}`，路由器据此把后续事件准确归桶。

## 验证

- 全 monorepo `typecheck`：6/6 项目 Done，EXIT=0。
- 桌面端 `node --test` 全量：150 tests / 150 pass / 0 fail（含 conversationStore 分桶隔离与 streamId 路由的新增测试）。
- 静态回归审计：路由器 13 类流事件全部 `resolveConversation → setState(cid)`；12 处 `!cid` 早退守卫；全文件无 `setState(activeRef)` 盲写。
- 人工运行时回归（待在实际 Electron 应用确认）：新建会话空白 / 快速切换无串扰 / 后台流式切走再切回只落自己桶 / 压缩·权限·provider·connection 恢复·token 用量·reattach 无回归。

## 取舍与后续

- **1A 取舍**：后台会话不做逐字动画（delta 整段写桶），换取实现简单、避免多套打字机缓冲的复杂度与风险。若未来需要后台也逐字，可在桶级增加每会话打字机缓冲（成本更高）。
- **策略甲取舍**：ChatSurface 用「薄适配」而非全量改名（200+ 处直引 `state.*`/`actions.*`）。薄适配爆炸半径最小、对根治无额外收益损失；彻底改名留待后续渐进重构。
- 本次根治顺带为「后台会话边跑边更新、前台随时切」打好了基础：多会话并发、后台流式在新架构下天然受益。

## 经验教训

- 「切换时串内容」这类 bug 的补丁（抢先清空 / 发送时判断 / 重挂载）都在和一个**架构必然存在的中间态**赛跑，治标不治本。
- 当「身份」和「由身份派生的内容」是两份可独立漂移（drift）的状态时，正确解法是让内容**由身份派生、按身份分桶**，而不是每次切换用一串 `setState` 去手动追平。
- 把「事件归属」交给 `streamId→conversationId` 的确定性路由，比「默认落到当前前台」这种隐式约定安全得多——后者在并发/后台场景下必然出错。
