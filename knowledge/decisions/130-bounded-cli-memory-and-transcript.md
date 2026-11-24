# ADR 130：CLI 有界内存、历史驻留与流式背压

创建时间：2026-11-14
最后更新：2026-11-14
状态：Accepted（2026-11-14 用户接受评审稿 117；正式编号 130；预算为已接受验收门槛，未实测）
级别：A（历史读取 Interface、请求准入与资源耗尽结算）
依赖：[ADR 129](129-native-rust-cli-and-ratatui.md)、[ADR 131](131-native-cli-contract-storage-and-recovery.md)

## 1. 目标

用户可以持续对话、查看完整历史和大输出，CLI 常驻内存不随累计对话正文线性增长。资源上限覆盖整个内置执行栈，不能只限制屏幕上显示的消息数，也不能靠删除历史、清空 Evidence、缩短对话能力或定时重启制造通过。

本 ADR 保留 ADR 57 的 canonical history、ADR 74 的混合存储、ADR 86 的读取事实边界、ADR 98 的查询范围 / 失效 / 不缓存授权准则；新增的是原生 CLI 每层资源所有权与可执行预算。

## 2. 三种历史必须区分

| 对象 | 所有者 | 生命周期 / 形态 |
|---|---|---|
| 持久会话 / Tool Result / Evidence | Store / Provider | 既有文件与引用；保存完整事实，不因 UI 逐出而删除 |
| 活跃模型请求历史 | Runtime Context Admission | 由 canonical projector 与压缩策略按当前窗口准入；按回合、revision 和模型绑定校验 |
| 展示历史 | UI read model | 可见区域、邻近预取、稀疏位置索引、有限解析块；可从 Store 重新读出 |

不得把三者各复制一份完整长期正文。`Arc` 共享也不能让旧 revision、订阅闭包或等待任务永久钉住全部历史。

## 3. 历史和渲染 Interface

- Store 提供按 conversation / revision / 稳定 message 或 block anchor 的有界读取，结果携带 cursor、sourceRevision、缺失 / 不稳定事实。跨进程变更后失效，持续冲突按既有错误结算，不能默默沿用旧权限或旧执行事实。
- 连续 transcript 是用户体验；内存实现采用 viewport virtualization。向上滚动按需读取，离开视口可逐出，回到底部是用户命令。不能把分页变成“只剩最后 N 条”的历史丢失。
- 单条超长消息也按块 / 行范围读取与渲染；禁止构造包含百万行的 Paragraph 后只设置 scroll。Markdown 语法状态与 wrap checkpoint 有界；索引为派生缓存，不是新的会话真源。
- 冷启动允许对旧 JSONL 作流式索引，不能为了建索引整文件 read_to_string。单个超大 JSON 记录需流式扫描 / spill；未知字段保持原文，不以反序列化后整文件覆写解决分页。超出解析能力时返回可诊断限制，不偷偷截断为完整结果。
- 缓存键为身份、content revision、终端宽度、主题 / 高亮版本；按分配字节和条目共同限额。正文不作无限增长的 cache key；长度不能代替容量，序列化前后与解析节点都须纳入统计。
- wrap / highlight、磁盘索引和模型编码不在 draw / input reducer 内运行；阻塞工作池、并发、队列和中间结果同样受限。

## 4. 流式队列与持久化

1. 所有 channel 同时限制条目和字节；Tokio bounded mpsc 只解决条目数量，载荷大小需字节 semaphore / admission 另外约束。
2. 输入 / 取消 / 审批控制与文本展示分通道，取消不能排在海量 delta 后面，也不能被持锁的阻塞发送饿死。
3. 文本展示 delta 合并为当前 revision 的有限缓冲，UI 落后时读取最新投影。合并不得丢失最终文本；事实写入 / checkpoint / 完成确认与 UI 帧率分离。
4. 工具 lifecycle、批准、最终结果、失败与 Evidence 引用不得静默丢弃。事实通道满时停止新准入，持久化 / drain 或明确失败；不能转为无限队列，也不能在未写成功时通知“已保存”。
5. 单次 SSE frame、工具参数、模型输出、MCP message、剪贴板粘贴及附件预览各有载荷上限。需要完整大输出时使用已治理的落盘 artifact 与有界 preview。若原工具契约不允许 ref 代替正文，先做契约变更或明确报超限，不能悄悄换返回类型。
6. stderr/stdout 泵持续排空并 spool，不能等渲染完成才读子进程，以免管道死锁。磁盘满 / 配额耗尽必须结算失败并保留已有证据；不无限堆到内存。
7. 活跃会话 / Provider 回合 / MCP 连接 / 文件 watcher / trace 标签总数有限；不能只有单队列有界，而按每个历史会话新增一个队列。

## 5. 初始预算

以下是原生 CLI 的工程目标，不是 Ratatui / Rust 的保证，也不是本次已测结果。P0 固定机器、负载与统计口径，按本次接受的预算实施；失败不得事后放宽以制造通过。

| 层 | 全局初始预算 / 行为 |
|---|---|
| 展示消息页及预取 | 16 MiB；每页同时限制消息数和正文 / AST 字节 |
| Markdown / 高亮 / wrap 缓存 | 合计 32 MiB，字节 LRU；长消息分块 |
| 流式展示缓冲 | 合计 8 MiB；超限先 flush / spool / 合并，不复制全历史 |
| 控制 + 事实事件内存队列 | 合计 8 MiB，控制预留；另设单载荷 / 条目上限 |
| 当前请求组装与 encoder | 合计 64 MiB；并行回合共用总预算，超过则等待、走既有压缩或明确 context-pressure 错误 |
| Store / 查询派生缓存 | 合计 32 MiB；不缓存 grant 或命令准入 |
| 子进程输出 preview / 网络解码 / 其他应用缓冲 | 合计 32 MiB；完整数据落盘，解码前检查尺寸 |

这些预算是对可核算 payload / 分配的约束，不等于整个 RSS；框架、allocator、线程栈、TLS、SQLite、终端缓冲与临时编码峰值另外测量。超大终端尺寸需有 cell 数准入，不能按未经检查的 rows × cols 分配。权限参数无法装入预算时拒绝该操作，不生成部分参数的 grant。

## 6. 内存验收

固定 release 构建、终端尺寸（至少 120×40 与窄窗）、同源合成工作负载；每个短场景至少五次，长期场景至少三次，保留每次原始曲线和失败。macOS 分别报告 RSS 与 physical footprint，Linux 报 RSS / PSS；不能将活动监视器单值与另一平台 RSS 作严格等价比较。

| 场景 | 已接受初始门槛 |
|---|---|
| 启动并空闲 60 秒 | 内置 CLI 进程 RSS ≤ 100 MiB |
| 1,000 轮持续对话、累计至少 100 MiB 正文，含工具 / 长代码 / 审批 | 稳态 RSS ≤ 256 MiB；编码 / 压缩等短时峰值 ≤ 512 MiB |
| 4 小时同规模稳态循环，包含会话切换 / resize / 历史读取 / 取消 | 第 2–4 小时稳态 RSS 回归斜率 ≤ 1 MiB/小时；周期谷值不阶梯上升；活跃对象 / 连接 / 句柄计数有界 |
| 1 GiB 历史、单消息 10 MiB、单工具 100 MiB 或百万行输出 | 不全量加载；仍守上述稳态 / 峰值预算；完整产物可按引用检索 |
| 100 次创建 / 关闭会话与 MCP 连接 | 回到暖态后内存与资源计数进入同一稳态包络，无订阅 / task / 子进程残留 |

内置 CLI、凭证 Helper、受管 Shell / MCP / 外部 CLI 分别列曲线；同时给出进程树总量，不只展示 Rust 主进程而隐藏旁路代价。外部程序的任意内存不能靠 Rust 自动约束，超额时按已有取消 / 隔离能力处理，不擅自杀用户其他进程。

输入到可见 p95 ≤ 50ms、p99 ≤ 100ms；取消命令进入 Runtime p95 ≤ 100ms，工具实际停止另列。固定工作负载下 UI 最大停顿 < 500ms；终端写出、调度延迟和后台解析分别归因。空闲无装饰动画时按需等待，不以 60Hz 忙循环制造工作。

RSS 不立即下降不单独等于泄漏。必须同时观测 live allocation、retained / high-water、task / FD / child counts 和缓存容量；也不能以“allocator 留存”解释持续正斜率而无证据。

## 7. 资源耗尽与恢复

内存预算耗尽首先逐出可重建缓存并停止预取；当前正文与证据不能被丢弃。请求不能准入则报告资源压力，保留已持久化输入、草稿与检查点。硬分配失败 / OOM kill 的恢复按 ADR 131 对未知效果处理，不承诺 Rust 能捕获所有 OOM。

新的页读取接口、资源压力错误与 artifact preview 契约需要协议与 fixture 登记。不得借“性能优化”变更默认权限、回合预算、签收或把事实提升为 System Context 指令。

## 8. 官方依据

有界 channel 的背压能力见 [Tokio mpsc](https://docs.rs/tokio/latest/tokio/sync/mpsc/index.html)。Rust 仍可能因引用环等原因泄漏，不能以语言替代上述门禁。[Rust Book：Reference Cycles](https://doc.rust-lang.org/book/ch15-06-reference-cycles.html)

## 修订记录

- 2026-11-14：新增原生 CLI 的三类历史、字节预算、队列背压、全进程树测量和资源耗尽恢复提案。保留完整持久事实和现有权限 / 签收政策。

## 接受与编号校正（2026-11-14）

用户明确接受三份原生 CLI 迁移 ADR 并要求先完成 P0/P1、自测后持续推进，最终无 Bun/Node sidecar。评审稿来自落后的知识 checkout，误用主线已有编号；核对全部 origin 分支后，将原 116 / 117 / 118 按同一内容分别登记为 129 / 130 / 131。既有同号其他 ADR 未被覆盖。接受不等于实现、性能、恢复或发布验收。
