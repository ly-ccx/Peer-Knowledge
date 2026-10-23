# E02–E04 P0 实施交接

创建/更新：2026-10-23

状态：**实现已审阅，候选验证待发布**。本轮用户授权 E02–E04 P0 合并为一个实施批次，并要求提交推送、不混入其他未提交改动、测试与回归留到发布前。没有把这份记录当成运行验收或发布许可。

代码评审：[Peer-Agent PR207](https://github.com/ly-ccx/Peer-Agent/pull/207)（draft，未合并）。

## 分支与来源

- 代码分支 `codex/experience-p0-input-decisions`；提交 `b64337f3329539ac2fcc2a16220b62842cdf1ae0`；父提交 `7f900bdb24345f32f755aed622511539ec42c1c3`（RC26 与已授权规范/矩阵指令提交）。
- 知识分支同名；本轮父提交 `9126ed53873a5c4eac0397136bcb2828846ea7fc`。两库均从干净 worktree 实施，原代码/知识工作区的未提交内容没有被搬入提交。
- 原矩阵 `cb2f5695` 是较广的本地 PR 组合；本次没有把该组合、TUI/Goal/Git/模型面板在途代码或主工作区其他修改一起带入。最终集成以开放 PR 的精确 head 为准，不以旧 merge 标题代替。

## 交付范围

| 工作包 | 用户目标、状态、控件与恢复 | 事实来源与主要 seam |
|---|---|---|
| E02 | Bot/Quick Chat/TUI 按目标和 surface 保存正文；Bot 保存 quote 与已读附件；发送先转入持久 pending 再提交，新草稿不受迟到回执清空。unknown 手动重试原 ID；重开只恢复，不自动重发 | `protocol/project-input-recovery.ts`；`runtime-core/project-input-recovery.ts`；`runtime-node/project-agent/input-draft-store.mjs`；Desktop service/IPC/preload；useInputRecovery/useBotConversation/BotComposer；QuickChatWindow；TUI client/useProjectInputDraft/ProjectApp |
| E03 | IME 优先于 Enter/Escape/补全/退格/方向；确认 Enter 到 keyup 后下一次可正常提交；补全 Escape 保住正文；菜单/浮层/全局动作让给 IME；不设 500ms 吞键窗口 | 纯 compositionGuard + hook；BotComposer/ComposerDraftControls/Quick Chat；共享菜单/Overlay/App；TUI composerEnterAction 的真实键名、press/repeat/release 与宿主可用 composition 信号 |
| E04 | 请求处理中、已接收决定、执行、核验、签收、交回各自表达；generic ok 不制造 done；拒绝/取消/过期有独立回执；unknown 不显示执行中。TUI cancel 不转换成 deny 或 allow | cardDecisionReceipt/当前 readBotCards；CardView/ApprovalReceipt；runtime-node card-projection；TaskVerification；TUI host/card-actions；AttentionSheet/列表/详情继续消费既有宿主投影 |

对应主矩阵：G01–G03，P05/P06/P07/P12/P17/P21/P22/P24/P26/P58/P59/P61/P65/P66；C012/C017/C030/C031/C035/C079/C134/C136/C137/C142/C155/C170/C202 与 TUI 两个恢复消费者。UI/M/T：U06/U08/U12/U15、M07、T01/T06/T07。消费者已有事实路径的静态审阅不等于每个 P 行都增加了代码或已实测。

## 架构影响与范围限制

新增 device-local 表达连续性存储/类型化 IPC 是 A 级边界补充，已先写[项目输入恢复契约](../../knowledge/architecture/project-input-recovery.md)再实现；输入编排属 B，控件/文案属 C。沿 ADR85 和既有 projectRuntime 目录，附件摘要 blob 与小 manifest 分离；CAS+原子替换防覆盖，损坏/写失败可见。没有第二执行通路、模型可见工具、权限真源、Evidence 或 System Context 注入。许可 gate 仍只以显式 allow 才可执行；cancel 保留独立事实。

30 秒是界面等待上限，未知不等于宿主失败；真实迟到回执仍确认原输入。最多 32 pending、每条 8 个附件及既有限额、引用内容总计 96 MiB。附件未读完/IPC 未完成时硬退出不承诺恢复；磁盘损坏不静默重置；并发冲突提示复制保留再重开。孤立 blob 暂不自动回收，空间维护另卡。Quick Chat bot/TUI 仍沿已有文本入口限制，经典草稿沿原持久 seam；不扩远程附件或批准。

## 实现审阅和发布前验证

本轮仅完成内容/diff 审阅，并同步生成 preload（生成命令不带 check）。没有运行测试、构建、typecheck、architecture/IPC check、截图或交互回归；未操作个人数据、已安装应用或运行实例。测试、回归及所有门禁均留到发布前，不能写为通过。

已编写未运行的针对性测试覆盖：草稿/quote/附件重开、目标隔离、blob 复用、CAS/损坏/锁/无效请求；写失败不 dispatch；未知同 ID/并发 retry；迟到不清新草稿；30 秒等待与迟到真实回执；generic ok/外部目标不能确认；问题回答重试身份；IME 物理 Enter/229/Process/keyup；实际 approval 对象绑定/过期优先；旧 resolution 不盖当前授权与验收；TUI cancel 不执行且持久 cancelled、IPC/service enabled 和 bot 边界。新增测试不是已获得的执行证据。

发布前 E13 必须在合并全部开放 PR 的最终候选执行全量构建、测试、类型/架构/IPC 检查和完整产品回归，另补以下人工/宿主证据：

1. 主 Bot 的跨目标/关窗/重开、quote/8 个附件、并发读入和写失败恢复；Quick Chat 换 bot 时迟到回执不隐藏新现场；TUI 真终端重开与失败恢复。
2. 未收到回执、界面超时、确认落盘失败、同 ID 手动重试、公共同步先到/迟到回执以及不同窗口 CAS 冲突；无自动重发、无重复副作用。
3. 各 OS 中文等 IME、补全与浮层嵌套、快速第二次 Enter、Shift+Enter、终端 LF/kpenter/repeat/release；终端不能上报 composition 时明确限制。
4. 列表/需要你/原卡/任务详情同一决定；批准与过期/策略撤回竞态、拒绝/取消、计划决定重放；核验部分/失败/未知/旧 attempt、用户签收和 Git 交回分别取证。
5. 与 PR197 模型控件、PR198/206 TUI、PR203 Goal 契约等精确 head 的合并后对照；本轮不合并或排除开放 PR。G04–G12、E05–E17 继续原排程，没有顺带标完成。

实施者内容自审不称独立评审；没有真实模型、安装包、读屏/辅助技术、全产品截图或日用覆盖的完成声明。
