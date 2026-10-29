# ADR 112：运行时模块与功能加载边界

创建时间：2026-10-28
最后更新：2026-10-29

状态：Accepted（用户要求按结构审查的建议顺序完成实施）；本批源码实现及内容审阅已完成，未经发布验收。

级别：A（共享包公共出口），B（宿主资源所有权、运行时职责及订阅），C（按需展示）。

依据：[审查报告](../experience/peer-code-structure-and-loading-audit.md)、[架构治理](../architecture/20-architecture-governance.md)、[ADR 111](111-project-agent-duplex-supervision-and-continuity.md)。

## 决策

保留现有 apps/packages、统一能力链、物理 journal/blob 存储 seam 与权威事实来源。ADR 111 的新记录另按该决策启用 schema 2、最小 reader/writer 5 的读写门槛，不能将本条理解为允许旧 writer 处理新记录。按真实职责分离领域规则、持久化、执行、宿主装配和视图，不以文件长度或平均切割为完成条件。既有导出继续兼容。

1. 隐藏视图保留状态与轻量事件接收，暂停昂贵读取，保留 pending 标记；恢复可见补读最新事实。此开关不暂停后台任务、系统通知或权限治理。IPC 读模型以稳定行身份做结构共享，不依靠全量 JSON 字符串比较。
2. 非必要页面和设置分区通过真实动态导入加载，局部 loading/error/retry 不使整个壳挂起；重试只重载界面，不重做业务操作。低频高亮语言异步加载期间源码保持纯文本可读。
3. TUI 在加载交互界面之前完成 argv/help/version 分流；exec/ACP/交互模式各自加载必要依赖。
4. GoalPlan 的领域规范化与变换离开文件 I/O Module；GoalRunner 的规划和核验规则形成可独立消费的领域 Module。写入、权限、Evidence 和未知副作用顺序保持原契约。现有随机 ID/时间语义不在本次搬迁中悄悄改变。
5. `@peer-agent/runtime-node` 保留根出口，增补 `/project-agent`、`/storage`、`/providers`、`/models` 稳定子路径，供消费者按领域依赖；内部文件不是公共 API。子路径分别指向构建后的领域入口并生成对应类型声明，不从根出口再次转发，否则不能缩小依赖。
6. Provider 的非必要 SDK 在实际适配操作内加载，保持错误、取消与超时可追踪；不能通过懒加载绕过 Provider 注册或执行准入。
7. Desktop 资源在既有 composition root owner/start/dispose seam 中拥有唯一生命周期；具体 OAuth 回调等资源实现不继续放在 main 装配文件。聊天组件与服务沿现有 kernel/adapter seam 拆出完整职责，不建立第二个执行器。

## 兼容与实施

新子路径是同一 package 的加法 Interface，根出口不删除。生产入口迁移后仍通过现有构建/打包清单分发 dist，不能只在源码开发模式可用。迁移顺序为视图读取、按需加载、领域拆分、子路径/宿主所有权、ADR 111 监督闭环；每步保留独立 diff 与交接记录。

不改写历史存储，不删除用户数据，不重启/安装当前应用。本决策不声称新的加载策略已经改善了现场延迟。性能前后对照、构建/类型/架构/IPC、测试与产品回归均按用户约定留到发布，除非用户明确要求提前验证。

## 自测后的资源所有权补充（2026-10-28）

200 Bot 夹具暴露出协调存储恢复会同时创建大量 Worker。恢复仍属于原存储 Module：以进程内共享 FIFO 队列限制同时重建为 4 个，排队后重新校验 lease，Worker 结束后释放配额。该配额只限制派生索引重建，不限制执行权限、不跳过恢复、不重置预算、不减少 fsync 或 Evidence。迁移耗时与已迁移数据的冷进程启动分列测量；不能放大原启动预算来掩盖迁移成本。

冷恢复 profile 又暴露出空工作账本也执行多轮恢复扫描。恢复选择可以在当前同步调用的权威快照确认为空时直接判定无可续工作；这些修复器只变换既有 work，不能凭空创建 work。待处理事件和 prepared delivery 仍走各自准入。该优化不跨 await 缓存事实，下次选择重新读取存储并保留 writer fence、lease、预算和未知副作用检查。这是 B 级的既有恢复 Module 内部调整，不改变存储格式或恢复授权。

协调存储 v2 的同步 recover 返回本次经过 owner/fence/完整性检查的只读快照，宿主直接使用其中的恢复状态；不再恢复完后立即为同一结果重复读盘。该返回仅供当前同步启动分支消费，不延长到异步执行或免除后续准入。

恢复链对未变化元数据的重复解析由存储 Module 收束为有界版本缓存。每次读取仍 stat 核对 dev/ino/size/mtimeNs/ctimeNs，读取前后版本不一致立即拒绝；fence、manifest、head、pointer 的外部替换不能沿用旧内容。物理 writer fence、日志锚点、完整性证明及 lease 校验保持原路径，不能缓存执行许可或跨版本接受旧事实。缓存只减少小型元数据解析，不改变 journal/Evidence 或 durable 写顺序。

输入队列消费在无待投递输入时只读返回，不创建锁目录、owner 文件再删除；有输入时仍进入原锁并重新读取全部当前待投递项，按原顺序持久化消息与 cursor。空读不承诺未来没有输入，新输入由原唤醒或下次同步消费，不能将空结果缓存成停止读取。无会话/未持 lease 等结果保持原契约。

Inbox 对成功读完的空批次保留最多 256 项轻量提示，键同时包含文件强版本与当前已消费 cursor。后续调用仍读取 cursor、核对文件版本；追加、替换、cursor 回退或读取失败均不能沿用空批次。提示不缓存事件正文、不跳过首次完整读取，不修改归档、去重、合并窗口或消费提交。

列表摘要只携带实际存在的可选事实，避免为每条消息分配大量 undefined 字段及空 meta 后反复复制；preview、question、unread、附件名与历史计数语义保持原投影。搜索索引同步只归一化每份文档一次，保留增量同步与全量重建等价、更新和删除语义。

presentation history projection 增补显式 `immutableOutput` 选择，供列表摘要共享深冻结的派生值；默认仍返回调用方副本。启用者承诺只读，Module 以深冻结执行该约束，每次读取仍核对源版本，变化后重新投影。它不能用于执行准入、授权或 Evidence 判定。短预览文本直接返回已归一化字符串，长文本仍按 Unicode code point 截断，避免为短消息构造完整字符数组。

搜索 corpus 使用同一 presentation projection seam 的独立有界公共消息投影：最多 512 个会话／8 MiB，仅保留既有 `isVisibleBotMessage` 判定允许的 id、kind/role、完整公共正文与日期，不收私有过程或工具参数。每次查询仍校验文件版本，变化会话重新加载；严格历史 API、执行恢复和 Evidence 读路径不改变。该投影经 runtime-node 的既有根出口与 project-agent 子路径提供给 Desktop 装配和基准，避免在每次新消息或记忆变化后重读所有未变化会话正文。搜索仍对全量当前 corpus 同步，删除、索引重建和结果排序语义不变。

迁移到当前 dev 候选后，ADR 111 实际沿用 storage/schema 2 与既有物理 writer fence，新增记录要求最小 reader/writer 5；早期 manifest 3 草案已被替代。用户本轮已明确授权完成后自测并提 PR，验证结果随最终实施回执登记。
