# E11–E12 实施交接：跨入口一致性与有界恢复

创建时间：2026-10-24
最后更新：2026-10-24

> 状态：**当前路径实现已审阅，候选验证待发布**。按用户授权落实 E11–E12、更新计划与三体系覆盖并独立提交推送；测试、构建与产品回归留到发布前。内容/diff 自审不是独立评审或候选验收。

## 来源、允许范围与边界

代码分支 `codex/experience-entry-recovery`，head `427d9041ecaced77cf6863ace83099c4d765f025`；[PR211](https://github.com/ly-ccx/Peer-Agent/pull/211) 为叠加 E09–E10 [PR210](https://github.com/ly-ccx/Peer-Agent/pull/210) / `df25f859b71025a2173096d6a0bdda0c1fdfa4ee` 的 draft。知识父提交 `73faf96679306977acbbaa6b666986532e70bb83` / [PR71](https://github.com/ly-ccx/Peer-Knowledge/pull/71)。实现提交 `51c693da`，随后 `427d9041` 将可见轮询统一归 ProjectApp、关闭 client 自动计时器；两仓干净隔离 worktree 承接本批；原主工作区的 HEAD、分支、index 与未提交内容没有作为代码来源或提交内容。

通过真实 merge `546a81bf855e198b947ec35d9010695d859a7929` 接入 [PR198](https://github.com/ly-ccx/Peer-Agent/pull/198) 精确 head `86eb3fbbd055a4225ac4b74ac8dc6bcb3e1312d3`，保留其原提交身份，复用 Enter、草稿恢复、经典切换卸载、公共对话与诊断；冲突保留此前 E02/E10 的 durable recovery、真实回执及失败快照。未合并 GitHub PR；没有接入 PR206 的 Markdown/System Context 改动或复制其他工作区 dirty。卡片 focus helper 是本批独立、局部实现，不宣称已集成 PR206。

允许文件：Desktop App/bootstrap/pager/conversation 反馈与对应 i18n；TUI index/ProjectApp/client/cardFocus 及相关用例；Gateway 两套已有网页模板、browser client/history seam 与相关用例。UI 继续 Frost/现有远程原生表单/终端主题原语，不增加组件库或物理参数。

B 级影响限 TUI client 的读取、在途合并与关闭生命周期；Desktop/Gateway 为 C 级表达。沿已有 host/directory、HTTP 与输入恢复接口，不增加协议、IPC、持久路径、Capability、PermissionGrant、Evidence、触发器或 System Context 来源。没有迁库、重写全量数据、操作个人运行目录、发布、安装、重启或改变 [ADR104](../../knowledge/decisions/104-progressive-interaction-and-coordination-storage.md)/[ADR105](../../knowledge/decisions/105-portable-coordination-baseline-integrity.md) 的恢复与内容证明边界；下面源码事实不替代恢复实测。

## 同一目标在各入口怎样表达

| 入口 / 用户目标 | 事实来源与状态 | 控制、恢复与限制 |
|---|---|---|
| Desktop Bot / Quick Chat 委托与查看 | 既有 shared input recovery、实际 input/public echo、approval/current card、任务核验与验收投影；本批 App 消费 bootstrap reader | 正文/引用/附件仍沿本机恢复；只以事实确认。bootstrap 失败可重读，已有 session 时保旧壳层；背景目录预取不挡主界面，不接受卸载/换源后的迟到结果；Quick Chat/托盘原生窗口行为仍发布待验 |
| TUI Bot 继续编辑或选卡 | 原 textarea、shared recovery 的 ready/error/pending/flush 与 host receipt；card-actions 再核对宿主和作用域 | Tab 显式进入卡片，方向键选择，Enter 执行动作，Esc/Tab 回编辑；普通方向键留给输入。按原 cardId 保持焦点，卡消失回输入，不把后继索引当原卡；自由回答回编辑，重复/释放 Enter 不激活，IME 信号优先 |
| TUI 切经典或退出 | `client.close` 先 await 各已有 recovery session 的 flush；成功后停止轮询、使旧读无效，随后卸载/关闭 host | 保存失败不卸载，原编辑器可继续保存；切换 single-flight。退出仍 finally 关闭 host/runtime，错误走原退出失败路径；只承诺已成功落盘内容。closed client 不再提交/决定，旧轮询不发布 |
| TUI 经典 | PR198 的普通 composer-submit/runtime-controls、既有队列与权限真源 | Enter/return/LF/kpenter 统一；失败保正文，模式切换卸载旧 root，避免旧编辑器夺焦点。普通 composer 与 Bot 输入各有恢复链，不能以一个修复替代全部终端支持 |
| CLI headless/帮助/更新 | 既有 cli-argv/exec/output/exit/update；exec 的 Runtime、Goal outcome 与 controller 状态 | 保留 text/json/stdout/stderr、非 TTY 的 ask 拒绝、SIGINT/SIGTERM 请求 controller cancel、退出码与 runtime.dispose；无图形 hover/motion，语义 N/A。没有本批新增 CLI 指令或重写安装/更新；部分结果/实际取消/安装仍发布待验 |
| ACP | 既有 stdio/agent/permission/updates adapter | 只接受有效且及时的 allow-once；取消/超时/无效回复依既有 deny，不由文本或动画授权。机器协议不是图形页面；断开/取消/更新顺序仍候选待验，本批不变更 ACP 契约 |
| 远程查看/发消息 | 原电脑授权的项目与 canMessage、原 HTTP response/requestId/result.status；批准继续回电脑 | Enter 换行、Ctrl/⌘Enter 发，composition/229 优先。每 bot 的 session draft/pending 保存原目标/inputId/body，只有匹配 requestId+ok+received 才清空；未知锁原正文、手动同 ID 重试。断联不自动重发，4000 字/无附件，页面全量重载仍无持久化保证 |
| 远程读任务/返回 | 独立 list/chat/task/auth ticket，成功读取才更新；preview 只显示已有任务状态与摘要 | 详情先 loading，失败有重读；关闭/Escape 回原入口或稳定按钮，换 bot/退出/页面隐藏使旧请求失效。JSON 解析之后再次核对；认证失效清私有视图。传统只读任务保实际 device/workspace 选择，改目标使旧结果失效；授权列表失败不作空 |

## 启动、大历史与恢复观察

| 问题 / 源码 seam | 本批行为 | 不越过的边界 / 发布责任 |
|---|---|---|
| G10 / App 与 useDesktopBootstrap | 删除 useBrandStartupMinHold，session 真实就绪立即进入；品牌仍表达真实等待，沿原 reduce/static fallback。失败与重读、可用壳层与可选目录预取分开 | 不等待动画创造“就绪”；没有实测冷启动耗时、内存或帧率。品牌 JS/CSS 原效果没有整体重写 |
| conversationPager/useBotConversation | 最新消息与旧窗口衔接每批最多 4 页，未重叠就保发布消息/原旧页游标，显示“继续读取”；继续从未完成游标，不每次重启尾页。真实失败保旧窗口；旧页读取/定位与新记录衔接分开，卡片事实期间独立刷新 | 不发布假连续缺口，不在未完成/失败时 markRead；旧来源/停止后的结果失效。恢复中的旧 snapshot 不覆盖更新的 activity/decision。每页沿既有 50 条投影，引用查找默认也有界 |
| tui-project-client | 移除每秒递归 stat projects/conversations/project-runtime/memory/goal-plans 的 fingerprint；沿原 directory 索引读取 50 条公共页与当前卡片；同目标在途请求合并，关闭/换目标后的结果不发布 | 不为性能绕过 runtime projection、不把私有日志塞进 UI；索引维护仍归宿主。快照稳定时保对象身份；失败保消息/区分不可用，不由失败宣告已读 |
| project-web-state/client | 会话内按消息 ID 去重/保节点；一次一页，增量没有重叠时显示缺口并继续读取，游标不前进或尾部仍未衔接明确失败；更早页保当前可见锚点，按 bot 记读位，用户回“已加载最新”才恢复跟随 | 不伪称已加载全历史；无 smooth 或布局事件自动恢复跟随。普通读失败保已授权快照，撤权清原私有预览；页面恢复可重读，旧回执不清 pending |
| 原 recovery/checkpoint/portable seal | 本批沿原宿主恢复卡与诊断入口观察，没有改变执行准入；原 input/任务/检查点身份不重新分配 | execution_outcome_unknown 不自动重放；原检查点缺失、内容证明不符、损坏索引与备份一致性仍由 ADR104/105 和现有恢复实现负责。本批不修复/迁移/重写个人数据，真实恢复包在最终候选取证 |

## 覆盖、审阅与下一步

同步 [改造计划](../../design/product/peer-product-renovation-plan.md)、[交互矩阵](../../design/product/peer-interaction-standardization-matrix.md)、[UI/动效/过渡覆盖表](../../design/product/peer-ui-motion-transition-matrix.md)。主要 P01/P06/P56–P77、C001/C008/C137/C138 及新增登记的 TS/MJS seam；U05/U06/U10/U11/U12/U15/U16、M09/M13、T01/T06/T08/T10。Desktop 非测试 TSX 209、TUI 13，本批未新增 TSX。CLI/ACP、原生窗口、未触及设置/列表等仍保留各自 V，没有按源码将全产品标 Pass。

已做内容/diff 自审、提交文件清单与空白审阅。已补写/更新 `conversationPager.test.ts`、`startupTransition.test.ts`、`cardFocus.test.ts`、`tui-project-host.test.ts`、`project-web-state.test.mjs`、`project-web-surface.test.mjs`、`web-surface.test.mjs`，覆盖分批衔接/关闭后不发布/保存失败不卸载/卡片显式焦点/远程未知原请求/IME/晚 JSON/旧详情关闭/页面恢复；**均未运行**。没有 unit/integration、build/type/architecture/IPC、截图/交互回归、真实模型/安装包/辅助技术验证或独立评审。

E11/E12 与 G10 的当前实现进入发布待验；后续 E16/E17 优先 G11 粒子减少动效的 JS 短路、G12 问题折叠 API/finished 降级，E15 继续迁移未触及消费者。E13 必须先重新盘点并正常合并所有开放 PR，再对最终组合候选执行完整门禁、逐图审阅与 verify。重点保留：大历史多批/失败/游标停滞、冷暖索引、终端 IME 与重复键/读历史/失败保存/切换退出、移动软键盘与锚点/认证恢复、未知副作用不重放、安装包重启与备份身份、浅深/实色/reduce/200%/读屏/原生跨窗口。
