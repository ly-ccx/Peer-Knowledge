# ADR 96：任务执行期间的响应性与有序持久化

创建时间：2026-10-18
最后更新：2026-10-18
状态：Accepted / Implemented（按负责人授权顺序实施；本地、真实模型与产品回归结果见 §8）
级别：A。关联：ADR 85、86、88、91、94、95；工程治理、产品理念与产品回归流程继续生效。

## 1. 问题与实测基线

RC16 正式包的相关模块与安装中的模块哈希相同。排查只读取运行现场；数据计时使用权限 0700 的隔离副本，测后移除副本。产品代码和真实任务没有修改。

| 热点 | 基线证据 |
|---|---|
| 每次卡片读取新建 Coordination Store，全量重放 journal | 约 75.6MB / 5000 条记录；新读取器重放中位 291ms，复用相同读取器约 0.51ms |
| 会话投影包含上述重放 | 使用生产投影 Module、空子任务端口的隔离下界测量：最近 50 条 336ms；仅保留读取器后约 35ms |
| 历史头像持续动画与 SVG 阴影滤镜 | 正式包合成窗口 28 个头像，3.2 秒窗口：GPU 进程 CPU 时间约占单核 63%；仅暂停头像动画约 3%。这是进程 CPU，非 GPU 硬件利用率 |
| 终态同步读、解析、序列化、整文件替换 | 46.2MB 对话读取约 132ms，终态更新约 251ms；流式 sidecar 写约 0.15ms |

每秒 20 次受控 Activity 推送未产生超过 50ms 的渲染长任务，不能据此把全部真实场景归因于流式，也不能据此宣布任意内容流畅。上一轮原始测量的首次头像对照脚本因空 CSS 参数被拒；修正测量脚本后重新运行，失败与成功均保留。

## 2. 目标与不变量

1. 执行期间的状态读取成本随新增 journal 字节增长，不能随累计历史反复增长。
2. 当前工作之外的历史头像保持静止；活动身份仍能表达工作状态，减少动态效果、隐藏窗口与离屏仍停止动画。
3. 大对话终态的全文解析、序列化、临时文件写入离开 Electron 主线程；终态公开和 Runtime 释放等待真实提交。
4. JSONL、现有 stream sidecar、PermissionGrant、Evidence、协调日志和任务状态的真源不变。缓存、worker 消息、动画和模型正文均不能代替它们。
5. 未知执行结果不能重放，拒绝/取消/超时保留原语义；不靠降低正确性、丢弃最后一片或关闭流式来提速。
6. 已发布版本数据无需批量迁移；最终 JSONL 继续由旧版本读取。用户日常安装、凭证和正在执行的任务不作为破坏性测试现场。

## 3. 顶层 Module 与 Interface

### 3.1 Coordination Journal Reader

Interface 保留 `createWorkCoordinationStore(...).read()` 返回独立快照，写方法继续验证 lease/epoch。Implementation 记住已提交的文件身份、已消费 byte offset、revision 和完整行边界；相同文件无变化直接返回隔离副本，追加只读取尾部。

- 采用 byte offset，保留 UTF-8 分片正确性；不以 JavaScript 字符数定位文件。
- 只有完整且通过 reducer/schema/revision 校验的记录才推进缓存。尾部半行和内部坏行不被静默当作成功事实；写者既有 recover 路径继续治理损坏尾部。
- 缩短、替换、同长度改写使缓存失效；增大时核对文件身份、已消费前缀的首尾边界锚点及行边界，再重放追加记录。此优化依赖既有 append-only 写入契约，边界锚点不是任意内部篡改的密码学证明；重建与新实例结果一致。重建失败不能返回旧的“成功”快照。
- writer append 后将同一已校验 next 状态和新的文件身份交给 reader；不能先推进缓存后 fsync。
- 不把已有 `coordination-snapshot.json` 直接当作可信状态。它缺少可验证的 journal checkpoint，仍是可丢弃缓存；本修复不通过盲信快照加速。

Project Facts 复用当前租约宿主登记的 store；无宿主时保持有界、按项目隔离的只读 reader。不能每次投影都构造空缓存读取器。LRU 逐出只丢缓存，不丢 journal；项目清退后旧 writer 的 epoch 不能被新的 reader 复活。

冷重建仍须验证全量历史；正常执行复用宿主已恢复状态。后续若将冷重建移到 worker，须保持相同校验语义，不以本 ADR 宣称首次恢复已经没有成本。

### 3.2 Avatar Motion Policy

Interface 在现有 SVG BotAvatar 增加明确的展示动效资格，默认静态。历史消息、引用、列表普通行、设置预览均不启动循环动画。当前 Bot 顶栏/当前活动回复可获得资格；交互反馈用有界动效，不给所有同名历史头像传播“正在工作”。

可获得资格也不代表必须循环：默认 idle 不呼吸、不眨眼；工作/思考优先使用轻量 transform/opacity。循环动画节点不叠加动态阴影滤镜，不将 `will-change` 常驻施加到全部头像。沿用共享可见性注册表，不给每个头像建立轮询时钟。

无障碍名称、机器人颜色、SVG 形状、上传图片和键盘焦点保持可读；不以“减少动态效果”全局开关作为唯一性能修复。

### 3.3 Conversation Terminal Committer

在 Conversation Store 内新增深 Module，提供异步 `commitStreamingMessage(conversationId, messageId, patch)`；返回轻量提交回执，不把整份历史跨 worker 传回主线程。旧同步 API 保留给兼容调用方，生产流终态接入新接口。

Implementation 分为 prepare 与 commit：

1. 同一会话按调用顺序排队；worker 数与积压有界，按需创建，空闲不维持活动句柄。
2. worker 在本地 Store 边界内读取历史、定位消息、合并 patch、序列化并写同目录唯一临时文件。只发送小型 patch 与 file-version token，不 structuredClone 整份历史。
3. worker 不直接覆盖真源文件。主线程拿到 prepared receipt 后，在既有写入锁顺序下重新检查文件身份/版本和会话仍存在；只有版本一致才原子替换并更新 contentRevision/index，再清理匹配的 sidecar，广播变更。
4. preparation 期间发生 append/replace/update 时丢弃旧临时文件、按最新历史重新准备；不得覆盖新用户输入、重复消息或复活已删除会话。重试有界，冲突持续发生则返回明确错误，不重跑模型或工具。
5. 触及的同步消息写路径遵守一致的 index → conversation 锁顺序。异步提交等待锁时通过异步退避，不在 Electron 主线程自旋等待 worker；长时间准备期间不持有主线程会请求的锁。
6. Worker 退出、超时、损坏历史、写入失败或最终提交失败均拒绝 Promise；临时文件由该提交清理。失败不清除最后一个可恢复的流式 sidecar，不发布伪造 done。
7. 未提交前崩溃：原 JSONL + 既有 sidecar 仍可恢复；提交后崩溃：原子 JSONL 可被旧 reader 正常读取。没有新增终态 overlay 真源，也没有延迟到将来才可被旧版本读到的完成记录。

主线程只负责小回执、版本检查、短临界区原子替换与 index 元数据更新。同步兼容方法的成本不被宣称已消失；运行中的 Desktop 流终态不再调用该方法重写历史。

### 3.4 Stream Terminal Barrier

沿既有 TurnSink / Chat Service seam 接入，不增加跨进程工具执行路径：

```text
最后一个 Tool Result / 文本分片
  → 标记本轮终态待提交，拒绝迟到分片
  → await Conversation Terminal Committer
  → 发布 done / error / aborted
  → 结算 Runtime / release turn / 交给下一切片
```

- 普通 delta / thinking / tool-progress 仍即时走既有 Activity 合并与 sidecar 节流，不等待磁盘全文提交。
- done、error、aborted、复读保护、handoff 和 finally 兜底共享同一 terminal barrier；重复终态不得重复提交或抢先释放。
- 用户取消只停止认知/能力执行，仍提交已得到的真实文本及 Tool Result，提交后返回 aborted；不能取消持久化来换取“停止得快”。
- 提交失败转为可诊断的本地持久化失败；保留原始原因/已有结果，不冒充 Provider 失败并自动重发任务。
- 兼容测试 executor / 旧 store 没有新接口时保留旧同步分支；正式包必须证明命中新接口。

## 4. 变更边界与实施顺序

### P1：日志读取

Runtime Node 的 coordination store、Project Facts 及聚焦测试；必要的新 reader Module 与导出/构建清单。先红后绿验证重复读取、外部追加、unicode、半行、同长度改写、替换/截断、损坏、lease 替换与 caller mutation 隔离。真实日志隔离副本记录读次数、读取字节与延迟，不能只测空文件。

### P2：头像

BotAvatar、资格纯策略、现有可见性 hook、调用点、bot-list CSS 与窗口检查。验证历史静态、当前工作可表达、隐藏/离屏/减少动态效果停止、SVG/颜色/图片不变。正式 Electron 同窗口做普通配置与仅暂停头像的对照；不能用全局禁用动画伪称产品已修复。

### P3：终态持久化

Conversation Store 新 committer/worker 与类型/构建清单、消息写锁接口、Chat Service 的 terminal seam 与聚焦测试；不在 main.mjs 增加业务。并发 append、replace、删除、跨进程写、worker 失败/超时、崩溃窗口、sidecar 恢复、旧版本读取及所有终态顺序进入回归。

每一阶段单独提交并立即 push。架构知识只存本知识库，不复制到产品代码仓。必要的实现细化只可在本 ADR 的 Interface 和不变量内进行；若出现新的存储格式或能力/权限边界，先修订 ADR。

## 5. 验收设计与预算

### 确定性正确性

- Runtime Node、Conversation Store、Desktop 受影响完整测试；types、architecture；worker 文件被包含在包内，打包后可正常启动。
- 所有取消/超时/失败保留；必须观察“持久提交先于终态通知和 Runtime release”。
- 原有标准产品 Capture → 每张必查图实施者审查 → review.json → Verify。实现者自审明确 `independent=false`，不称独立审查。

### 性能负载

至少 75MB 协调历史、46MB 对话，与历史基线同级；热读取与追加读取分开计时，记录 p50/p95/max、CPU、event-loop delay，不能用总完成时间代替输入流畅度。

目标：

- 协调无变化热读 p95 < 10ms；小追加读取不随旧历史线性增长，单次常规尾部更新 p95 < 25ms。
- 默认空闲窗口 GPU 进程 CPU 对基线显著下降，并与仅暂停头像对照接近；历史头像的 computed animation 必须为 none。
- 46MB 终态提交期间 Electron 主线程事件循环的存储新增阻塞 < 50ms；原子提交耗时与 worker 总耗时分别报告。不能仅报告异步函数立刻返回 Promise。
- 真实任务执行窗口：输入响应 p95 < 100ms，rAF 帧间隔 p95 < 32ms，单独列出 >50ms 长任务及最长停顿。未达标则定位剩余路径，不能靠放宽预算或缩小历史消除失败。

### 真实任务

从已配置真实 Provider 通过正常主 Bot 输入、派工、子 Agent 读/写隔离项目文件、运行检查、返回结果与主 Bot 交付。使用隔离数据根和测试项目；凭证仅沿现有 vault 读取/临时引用，报告不输出密钥或用户原文。

执行期间反复输入草稿、滚动、打开/关闭任务详情，记录帧、长任务、输入延迟、主/GPU/renderer CPU；至少一次大历史终态落盘与一次取消/恢复。不注入 Tool Results、不替代任务执行器、不旁路权限/Evidence。受控压力测试与真实模型任务分别标注；真实模型失败也保留，不以确定性测量代替真实任务验收。

## 6. 取舍、拒绝的方案与回退

- 不关闭流式、不隐藏问题卡、不删除旧任务、不清空协调日志来降负载。
- 不盲信现有 snapshot；不把缓存拿去越过 lease/授权或判定工具成功。
- 不把异步写盘改成“先显示完成、后台慢慢写”；失败必须在本次终态暴露。
- 不在 worker 准备期间长持互斥锁，不把多窗口一起自旋阻塞当作异步化。
- 不让 renderer 承担持久化或本地文件能力，不改变 Manifest → Projection → Tool Call → PermissionGrant → Evidence。
- 保持现有 JSONL 和 sidecar 格式；回退代码仍可读已提交文件。未提交任务仍按已有中断恢复流程收束，不能自动重演未知工具调用。
- 新 worker 异步接口和 reader cache 均有聚焦 seam 与诊断字段；若一项失败，可单独回退实现，不回退已通过的权限/恢复语义。

## 7. 实施与验收记录

待实施。此状态行不能作为已修复、已发布或真实任务流畅度达标的证据。


## 8. 2026-10-18 实施与测量记录

代码审阅：[Peer-Agent #165](https://github.com/ly-ccx/Peer-Agent/pull/165)。知识审阅：[Peer-Knowledge #45](https://github.com/ly-ccx/Peer-Knowledge/pull/45)。依次提交日志读取、头像动效、终态 worker/barrier；随后根据本轮新反馈补齐 ADR 83 的冻结强度投影。main.mjs 净减少 15 行。

### 已通过的验证

- 全仓 build/test/typecheck/architecture 通过；后续强度投影改动的受影响 112 项测试、Provider 编码/执行器测试、类型与架构检查通过。存储/聊天聚焦批次 183 项通过。
- ASAR 内运行实际 Conversation Store worker，而非以普通 Node 文件路径代替打包环境；Electron 41.7.1 / Node 24.15.0。46,697,583 字节历史的 5 次终态提交，总耗时中位 104ms、最慢 112ms；主线程入队 p95 0.11ms，主事件循环最长停顿 4.43ms。
- 同样的 75,522,325 字节 / 5000 记录合成协调历史，30 次无变化热读：读取正文 0 字节，p95 0.13ms；30 次外部小追加共读 26,330 字节（含边界锚点），p95 0.16ms。冷重建约 51ms 仍保留，不将它称为零成本。
- 当前真实历史的受限隔离副本：协调日志增长至 99,938,883 字节，冷重建 346ms、热读 p95 0.88ms；46,233,417 字节对话、约 200KB 实际末条 patch，5 次 worker 提交总耗时中位 300ms，主事件循环最长间隔 4.00ms。副本在 finally 中删除，日常数据未被改动。
- 相同合成 28 头像窗口：候选正常空闲 GPU 进程 CPU 约单核 3.51%，仅暂停头像对照约 3.22%，减少动态效果约 3.42%。RC16 对应正常窗口约 63%。这些是短窗口进程 CPU 时间，非 GPU 硬件利用率。

### 真实 Provider 执行

使用已配置 GPT-6.1 Sol、独立数据根与测试项目，经主 Bot 正常派工。子 Agent 冻结 worker=max、其他角色 medium，实际调用 list_files/read_file/edit_file/bash、运行 node --test、与父 Bot 通讯，模型复核 passed 后主 Bot 返回结果，宿主签收 accepted。20 个持久化工具段都有结果；8 个复核 Evidence 引用。测试未注入 Tool Results 或替换执行器。

随后经正常输入启动另一只读子任务，调用既有取消入口，观察到 cancelled；再输入新的继续对话请求，获得 CANCEL_RECOVERY_OK，旧任务保持 cancelled。子任务读接口实际返回 worker=max / conversation=max，验证冻结强度传递。

整个执行及取消/继续窗口 241,753ms：459 次交互，500 个输入绘制样本 p95 7.7ms、最长 9.5ms；29,011 个 rAF 帧间隔 p95 9.9ms、最长 16.19ms；>50ms 渲染长任务 0。窗口可见且有焦点，执行期间打开/关闭任务详情、滚动和输入草稿。该窗口 GPU 进程 CPU 约单核 26%、主进程约 4.85%、渲染约 25.86%，工作动效仍有成本，不能套用空闲 CPU 数字。

首轮真实任务本身已成功交付并签收，但测量脚本错误检查 WorkSession 上不存在的 accepted 布尔字段，等到 8 分钟窗口结束而记为未通过；修正为结构化 status 与 canonical reply/verdict 关联后重跑通过。保留首轮失败记录，不将其误报成 Provider 或产品执行失败。ASAR 压测脚本也保留初次导出导入、启动等待和 evaluate 动态导入失败记录，修正后重跑实际包内 worker 通过。

### 剩余范围说明

标准产品 Capture 已生成 180 张必查截图，实施者逐张检查并写入 review.json，Verify 通过。RunId：549c767f-b9e4-4d24-a90e-94d00ac7c248；源码指纹：0c0649f976b8bb5141942d95856d4b932534484bc02cdcb1a7ddd1941080dd01。记录了原生透明快捷窗口截图不含系统合成底色的轻微验收范围限制；未以截图宣称实际桌面合成色彩覆盖。最终双平台 CI 仍在运行 Electron smoke，前序 build/test/typecheck/architecture 步骤已通过。真实测量与当前 PR 的产品代码一致，之后提交仅补充测试与验收脚本；具体源 HEAD、模型和作用域保留在各测量 JSON。实现者自审不称独立评审。真实修复窗口不代表任意项目、任意网络或任意输出内容；冷恢复及旧同步读写 API 仍可能阻塞。未替换日常安装、未发布新 RC，也未进行完整读屏或长期使用验收。
