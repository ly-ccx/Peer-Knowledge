# R9/R10：正文草稿、版本和受治理修改

当前验证更新（2026-10-27）：用户明确要求的 R1–R10 组合已运行，R9/R10 的模块、深浅色实际保存/授权/写入/拒绝/取消/冲突/只核对及原生关闭保留输入均通过，发现问题已修复复跑。见[本轮验证记录](resource-workspace-r1-r10-validation.md)。下文“未运行”为各实现子包当时状态，不覆盖新回执；仍非完整 G8 发布验收。

日期：2026-10-27
状态：R9-01/02/03 协议、存储、宿主/IPC 与编辑恢复界面，R10-01 条件 Provider/运行时 Adapter、R10-02a 原始执行日志与核对 Module、R10-02b 主应用授权/提交接线、R10-03 局部提交/授权/结果核对界面均已接源码；已完成本轮跨阶段连线审阅并补正原生关闭检查点，详见[源码覆盖表](resource-workspace-source-coverage.md)。未运行当前候选验证，不代表 G7/G8 动态验收。
依据：ADR109 §38；A/B/C，知识库契约先于代码。

## 分段与边界

1. R9-01：严格目标/草稿/写者/操作回执协议；纯状态 kernel，固定基础版本、revision CAS、写者接管和不重复启动的操作准备。只存意图，不能由其生成授权或 Evidence。
2. R9-02：本机 manifest/blob 存储、限额/显式清理、真正 sender/writer Registry、崩溃和未知结果恢复，索引元数据与正文分开。
3. R9-03：主窗口/原生只读视图的草稿发现、恢复、受控编辑与冲突比较，IME/读位/焦点保护；未经真实端到端接线不显示提交入口。
4. R10：明确用户提交/反馈经现有 Provider/Manifest/Projection/Tool Call/PermissionGrant/Evidence 写入；条件版本、实际 Diff、结果待核对、失败/取消和独立验证/签收。

## R9-01 已落源码（未运行）

- protocol/resource-edit：ResourceEditTarget、ResourceTextDraft、ResourceEditWriter、ResourceEditOperation/Receipt，当前绝对文件/明确 Bot/观察基础严格规范化。历史 Git、相对猜测、目录和授权字段拒绝；UTF-8 每正文 1MiB、NUL/不成对 surrogate 拒绝，保留 CRLF 与实际 Unicode，不静默替换字节。
- runtime-core/resource-edit-state：无 fs/任务/授权/工具端口的纯状态转移。打开同资源同基础返回旧草稿并保留后来文字；不同基础隔离；保存核 writer token/lease 和草稿 revision，显式接管使旧写者失效。写者不写入 manifest，恢复后不能用旧视图自动续写。
- 稳定 requestId 先 reserve prepared，固定 target/draftRevision/provider/新内容摘要。相同请求查询旧记录，异内容拒绝；start 的 fresh 标记只有在后续宿主持久确认并通过原能力链时才可实际开始，不是执行许可。同操作不会再次返回 fresh；旧 host running 恢复为 uncertain，不能自动重跑。
- 宿主提供的实际 ToolCall/Evidence 关联才允许 applied 收口，观察版本必须匹配 proposedVersion；矛盾回执拒绝，重复回执幂等。结束操作不清空或重基用户后来输入。删除草稿不忘记操作 ID，仍有待办操作时不允许删除；同 draftId 不得在删除后冒充另一个资源。
- 恢复严格拒绝未来/损坏 schema、错误 Bot、重复身份/基础、正文版本不符、操作摘要或 target/revision 关联不符，不能为“恢复成功”覆盖旧数据。

以上目前只是协议和纯 kernel，尚未建立资源正文存储目录，也没有 IPC/编辑器/原文件写入接线。resourceEditManifest 是 kernel 的水合序列化接口；R9-02 才补真正的 blob 引用 manifest 与原子保存/物理限额，不把它误称已持久化。尚无可用的文本编辑或提交按钮。

已编写协议/Unicode/字节/非法目标/回执，基础版本复用/隔离、写者接管、CAS、同 ID 异请求、重复启动、重启待核对、后续文字保留、损坏恢复和删除不复用身份用例，加入资源组合清单。仅内容/diff 自审；未运行单元/集成测试、build/typecheck/架构/IPC 检查、截图或原生联调。未提交/推送、未重启、未碰原个人任务/成果、未发布。


## R9-02 存储子集（2026-10-27，源码完成，未运行）

先补 ADR109 §38.5，再实现 runtime-node/resource-edit-storage，使用已有 SQLite connection seam，不使用损坏时自动重建的缓存 openSqlite。当前仍未实例化进主应用，因此不会读写个人运行数据。

- 每 Bot 的 resource-edits/store.sqlite 保存 schema v1 的正文引用 manifest、内容寻址 UTF-8 blob、操作正文保留关系、固定交付元数据和宿主占有。事务同时提交/回滚，FULL 同步，私有目录/文件，拒绝路径软链接/文件硬链接；未来/损坏版本不重建覆盖。
- metadata 索引不水合所有正文；只读取选定草稿或历史版本，正文验证大小、UTF-8 可逆与 sha256。用户连续自动保存只回收已被替代且无任何引用的旧 blob；当前基础、草稿、待办操作及留存快照继续保留。16 草稿、64 活跃操作、1024 retired receipt、1MiB 正文、64MiB blob 和 2MiB manifest 限额均在事务内核对；pending 操作每项预留 32KiB 回执空间。
- 真实 PID + 随机 epoch 的事务宿主占有区分仍活跃宿主与已退出宿主，不用年龄/定时器推定死亡。另一活跃宿主可读已保存意图但不能取得写者；旧运行记录在宿主恢复时呈现 uncertain，读取/恢复/重复 start 不重跑任务或原文件写入。每 view 的 token/lease 仍只在内存，不从数据库复活。最后一个写者退出且无待办操作时释放 idle workspace。
- reserve 保存的基础与提议正文不随后来编辑变化。明确归档只处理 settled，保留稳定 ID 和回执；新请求与旧事实冲突拒绝，归档后查询/重试不再启动。归档或清理从不删除项目原文件，也不取消 prepared/running/uncertain。
- 成功操作的前后版本从实际 applied 回执与已留存 blob 投影；分页索引每页最多 64。固定交付仅提供宿主内部入口，要求准确 Evidence/Artifact、目标和正文摘要；最多同时留存 32 份正文，清理元数据至多 1024/2MiB。UI 不可随意调用其制造交付事实。
- 显式清理保存“正文已清理”和原始关联；即使同一 sha256 因另一个草稿仍存在，也不会自动恢复这份历史可见性。明确重新捕获才建立新 snapshotId，旧已清理记录不被改写。原 Evidence 不删除、不改写、不作为原文件权限。

新增未运行的存储用例覆盖双宿主/恢复、writer 接管与 CAS、草稿值隔离、原提议正文保留、running→uncertain/不重放、真实回执投影与清理、70 次自动保存回收、未来/损坏/软链接保护、固定交付、操作/草稿上限、归档后去重及 idle workspace 释放，并补协议快照和 kernel 归档用例。已纳入组合清单。只完成内容/diff 自审，未运行测试、构建、类型/架构/IPC 检查、截图/前后端/原生联调；不能称运行通过。

剩余仍是 R9-02 的真实 sender/原生 lease/受控来源 Reader/IPC 接线，以及 R9-03 的编辑、恢复、冲突与 IME/焦点/读位；R10 的条件提交/权限/实际 ToolResult/Evidence/核对仍待实现。无编辑/提交假按钮。未提交/推送、未重启或恢复原个人任务、未重跑成果、未发布。


## R9-02 宿主与 IPC 接线（2026-10-27，源码收口，未运行）

先补 ADR109 §38.6，再接 ResourceEditApplicationService / ResourceEditSources / NativeEditSource 和 typed protocol/preload。该节更新前面的“尚未实例化/没有 IPC”历史状态：主应用现在组合了延迟打开的本机 store 和服务，但本轮没有启动/重启应用，个人运行数据没有被这些源码触发。

- 主窗口和专用原生只读窗口共享本机草稿 Interface，实际角色/顶层 app-origin 由 catalog 核对；document 或 native 来源必须有完整实际读入的 resourceId/contentVersion。renderer 无 baseText/owner/root/事实回执入口，宿主沿 FileAccess 或原生现有 Reader 取得原始完整文本与规范路径，核 UTF-8/字节/hash/媒体/当前版本；不是格式化正文或新版本的偷偷替代。
- native 沿原 Registry/readBinding/scopes 校验真实 sender/window/generation、task/revision 和目录后代；历史版、Diff、图片、目录本身不变为文本编辑源。读取返回后再次核同一 scope/lease，来源失效的迟到结果拒绝。主 Bot 归属直接读现有 Profile 元数据，不汇集完整会话/任务，不调用 host.sync。
- 宿主 view handle 由真实 BrowserWindow/sender 铸造，固定 draftId；按原请求 ID 合并待办、跨来源同 ID 拒绝。每窗口待办 16/视图 32，全局待办/视图 64；已完成请求仅保留有限句柄与指纹，不缓存整份正文。30 秒读取截止、显式取消或 sender 销毁使旧结果失效，不重试或重放写入。
- acquire/save/discard 按真实视图串行。token 在宿主生成，显式 takeover 才转移写者；成功后立即退休同草稿旧视图的 writer 缓存。旧 sender/handle/generation/lease 的保存或关闭不能冒充新写者。保存只回 draftId/revision/time/text digest，不每次回传两份完整正文，也不清掉后来的文字。
- 本机保存意图可以在原文件离线/已改时继续保留；main 明确恢复同一 Bot 的本机草稿不需要重读原文件，也不获得原路径权限。native 恢复仍需原租约合法来源和同 resourceId。收件会话变化清楚拒绝并保留原记录，不自动迁移。关闭只释放该呈现/写者，草稿保留；删除草稿退休同对象视图，但不删除项目文件或原 Evidence。
- 历史 metadata 分页有界并过滤不可访问来源；历史正文先核原 Bot、真实原生资源与当前受控来源范围，再读取本机留存正文。清理、归档、固定快照清理只作用于合法本机记录；没有 UI start/settle/retained-delivery-fact 或 Provider 执行入口。
- 宿主只对该 Bot 已登记视图发不带正文/token 的 changed 事件，表达实际接管、保存、删除或历史变动，不代表新权限。main/resource 的最小 preload 已接 14 个 intent invokes 和一个状态事件；按目录重新生成三个 sandbox preload，当前 379 canonical channels。生成工具的 registration pattern 差异已按既有 owner 结构修正后生成成功；这不是测试/构建/运行验收。

新增未运行用例覆盖真实宿主读源、跨 sender/代次/伪造 token、显式接管与旧只读视图关闭、取消/超时/销毁后的迟到读取、源/归属/版本变化、离线本机意图恢复、原生限制、保存摘要回执、历史范围过滤/正文读取前复核、IPC actual sender/role/origin/top-frame 与无执行事实写入入口。协议/NativeEditSource/SourceReader 用例及组合清单同步。

仅源码内容/diff 自审，未运行单元/集成测试、构建/typecheck/架构/IPC 检查套件、截图/前后端/原生联调。R9-03 的真正编辑器、输入/自动保存、关闭前 flush、冲突比较/新基础恢复仍待继续；R10 的受治理原文件提交、ToolResult/Evidence 和未知结果核对未实现。尚无编辑/提交假按钮。原工作树/任务/成果保留，未提交/推送/重启/发布。


## R9-03 编辑与恢复呈现（2026-10-27，源码接线，未运行）

先补 ADR109 §38.7，再落 renderer/editing session、Registry、编辑器/草稿索引/历史正文与主窗口、独立窗口接线。目标是用户在原对话旁边编辑本机意图，尚未提交原文件；范围不扩展到另一套工具或模型执行。

- 当前真实已读文本在 1MiB/有效 UTF-8 范围内提供“编辑草稿”。主窗口使用实际 Bot/观察版本和规范路径，独立窗口仅传真实 view/window/generation 三元身份及原目录合法后代；不能把完整 context 当租约对象。历史 Git、Diff、图片、目录本身不提供编辑入口；格式化预览内容不成为编辑基础。宿主仍重读并核原文摘要/版本。
- DocumentSession 只增加显式 draftId 导航定位；草稿与当前文件/历史/Diff 分开去重、标明“草稿”，不把正文、writer/token 存进导航。非法/相对/历史混合草稿定位拒绝，失效草稿不降级打开当前文件。主 Bot 起始页列本机草稿，独立窗口在原 view 范围比较页列同一资源的其他基础；打开已保存意图仍由宿主核归属。
- session kernel 长于 React 挂载，分离当前输入、最后确认保存文字、基础原文和实际 view/writer。自动保存350ms 只存本机草稿；保存时后来输入保留并串行继续保存，不以旧回执覆盖新输入。摘要/revision 不匹配或 ack 丢失先沿同 view 的串行 read 屏障核对，已持久保存不重复写，没有确认则停下并保留输入。明确接管后若另一处正文不同，仍须用户选择自己的缓冲或已保存稿，不能接管即覆盖。
- 复用 compositionGuard，组合输入期间不 flush 或消费保存快捷键；Cmd/Ctrl+S 只保存草稿，不发送、不提交原文件。textarea 的 LF 展示与原始源文本分离，公共前/后缀之外的实际编辑才重建，未编辑部分的 CRLF/混合换行和 Unicode 保持。超限/非法字符留在可恢复缓冲并阻止持久保存，不静默截断。
- 编辑/Markdown 正文/基础与我的草稿比较复用安全 Adapter；当前文件比较是明确动作，保留 resourceId、原 Bot/task/根，只去内容版本条件，核原始 UTF-8 摘要。另建新基础使用宿主新读观察版本，旧稿保留，不把后来输入偷偷重基。保存/错误反馈局部表达，没有原文件提交假按钮。
- 草稿源光标/选区/滚动、正文和比较各自读位存于同 session。主工作区继续右侧非模态形态，异步打开、另建草稿返回时重核活跃来源/触发焦点，切 Bot 或卸载后的迟到返回不抢面板。独立窗口回阅读恢复原文档读位；原文件仍明确只读。
- 关闭草稿标签先 flush，失败保留标签。React 重挂载或另一份实际消费者在 flush 中重新使用同 session 时，不释放新用到的 view。Bot 切换/外层卸载保留未确认缓冲并尝试原 Bot 保存；32 项 renderer registry 只回收安全关闭且无未保存输入的项，满后明确拒绝新增。失败的卸载缓冲有非模态恢复带，可选中复制，不自动发给模型。
- 原生 checkpoint 同时等待阅读位置和所有本机草稿安全 flush；失败不 acknowledge。返回/关闭动作同样检查结果，beforeunload 遇未保存/组合输入保留窗口，尝试保存并解释如何重试；通用 unload 不自动调用 window.close，因为用户可能正在刷新。关闭呈现不取消任务，不恢复/重放已完成的写入。
- 草稿删除与采用保存稿用现有确认组件；删除请求发出后又输入的文字继续保留为待恢复缓冲，不被迟到删除回执清掉。留存历史只读、分页、保留原 Evidence/ToolCall/Artifact 关联，正文清理或来源不可用明确说明，不拿当前文件填历史。仅用户明确整理 settled 操作/固定交付；未结算/未知结果不在界面提供清理执行责任的入口。

本段新增/扩展未运行用例：同 view 排队 read 等 save 屏障；迟到保存与后来输入；已提交但丢 ack 的只核对不重放；未提交保存失败停自动重试；IME/超限缓冲；写者接管/正文冲突明确选择；重挂载不释放新消费者；取消后的迟到 resume；删除中后来输入；错 view writer 回执；光标和独立读位；重复打开合并/定位不匹配；容量上限不驱逐未保存缓冲；CRLF/混合换行/Unicode；导航不存正文/token 及失效 draftId 不降级。加入资源组合清单，未执行。

### 待运行前后端验收场景

| 场景 | 前端检查 | 后端检查 |
|---|---|---|
| 主/独立窗口编辑当前文件 | 右侧/原视图草稿，原阅读位置保留，明确未提交 | 实际 sender/lease/原文 hash 与 observed 同一来源 |
| 独立目录子文件 | 仅合法当前文本能建草稿 | 目录根后代约束；跨资源/历史/错代次拒绝 |
| 正常输入与中文输入法 | 不误发、不吞正常按键；局部保存；光标/换行不乱 | 有效 UTF-8/1MiB/revision CAS；组合未完成不提交 |
| 快速输入和延迟 ack | 旧回执不覆盖后来输入 | 保存串行；read 屏障核对而非重复操作 |
| 双窗口接管 | 旧窗口保留缓冲并只读，显式内容选择 | token/lease 退休，旧写者不覆盖 |
| 切 Bot/隐藏/重挂载/关闭 | 草稿/读位保留；保存失败可恢复；迟到打开不抢焦点 | 原收件对象重核，无任务队列/重跑端口 |
| 刷新/退出/checkpoint | 失败不静默卸载；可继续工作后重试 | 未确认 flush 不 acknowledge；最后已确认 revision 保留 |
| 新基础与文件变化 | 明确读取当前、比较、另建草稿，旧稿仍在 | resourceId 不变，版本变化拒绝旧条件，不扩大根 |
| 恢复离线草稿 | 草稿和当前文件分开，失效定位给明确提示 | main 可恢复本人意图；native 仍核原来源租约 |
| 清理/删除及迟到事件 | 明确确认；后来输入保留；历史已清理不补当前 | pending 不清理，原文件/Evidence 不删除，去重身份保留 |

本轮只做源码内容/diff 自审，没有运行测试、构建、类型/架构/IPC 套件、截图或前后端/原生联调，不称测试通过或产品验收。没有重启、提交推送或发布。R10 的条件提交、原 Provider/PermissionGrant/ToolResult/Evidence、未知结果只核对仍待实施。


## R10-01 条件文件 Provider 与运行时 Adapter（2026-10-27，源码完成，未运行）

先补 ADR109 §39，再落 `resource-file-replace` 协议、单次人提交专用 Manifest/Projection、条件 Provider 和 SDK Adapter。仍未接主应用提交 IPC/日志/授权事实，也没有启动实际写入；不能把这个底层包称为可用提交功能。

- `local.file.replace` / `replace_file_if_version` / `local.file.conditional` 专用 Interface，固定 requestId、已规范化原目标、正文和 proposed 摘要；当前 UTF-8 1MiB 上限、非法目标/扩权字段/正文超限拒绝。结果分 applied/conflict/denied/cancelled/failed/uncertain；结构化 preview 规范化拒绝观察摘要不匹配的 applied、已触及文件却宣称无副作用取消，以及在结果里伪造 grant。
- 专用 Manifest L2_local_write / D2_sensitive，仅由资源 Runtime Adapter 构造局部 registry/projection，不加入普通模型工具列表。Adapter 从实际 running journal 操作核 providerId、固定 payloadHash 和提议正文摘要，复用纯 kernel 的 canonical payload 序列化；prepared/uncertain/settled 不能由该入口启动。作用中的源/意图事实仍由宿主 port 核，不是 renderer 字段。
- 实际执行沿共享 Runtime SDK → Node Host Adapter → Registry → Provider，保留 Hook、取消、实际 PermissionGrant 和 Evidence。每次条件修改都要求宿主授权，即便目录内；只有真实匹配 scope/toolCall 的 Grant、有效期限类型和仍有效的 host validate 才可写。权限预览只传目标/版本/字节数，不传完整正文。此处仅定义 port，主应用的真实授权/审批存储桥待 R10-02。
- Provider 在权限等待后重解来源，核 Bot/根/path/resourceId/原 UTF-8/hash/nlink/file descriptor；拒绝 symlink 终端、多个硬链接、非法正文和超限源。使用实际原描述符写入/截断/fsync 并再次核路径/inode/提议摘要，保留原 inode、mode、ACL/xattr。外部写者仍有竞争窗口；不承诺跨进程 CAS，也不把同宿主文件队列误称能约束 Shell/MCP 或另一进程。
- 同宿主条件文件和原 edit_file/write_file 共用按 canonical path 的有界互斥（256 路径、每路径 64）。排队取消及时回交，但不提前释放别人的实际写者，已取消的队列项稍后只退出、不执行。原文件能力也在等待授权返回后重新核 read snapshot；新文件等待中出现同名文件就拒绝，不覆盖。范围内其他行为不改。
- 开始触及原文件后任意写/截断/fsync/读回失败都返回 uncertain；不会包装成“失败且原文件未动”。取消在真实写入完成后才被观察时，保留实际 applied 观察。无变更明确 no_change；有限 Diff 来自实际 before/proposed 文本，保留无结尾换行语义，截断明确标记 previewOnly，不是可执行 patch 或 Git 状态。

编写但未运行：协议非法 target/UTF-8/限额/注入字段/回执状态；真实 Provider inode/mode/CRLF/Unicode、无真实授权、Projection 缺失、载荷变化、源/策略/文件在等待中变化、symlink/硬链接/非法字节、部分写入/失败 fsync、取消先后、原文件工具互斥与 stale read、600KiB 草稿/no-change；共享文件队列串行/独立路径/异常释放/取消不提前放行；有限实际 Diff/无换行/空正文；SDK Hook→permission→Provider→Evidence 顺序、Hook 拒绝、非 running/假 payload 不调度。加入资源组合清单。仅源码/diff 自审，未运行测试、构建、typecheck/架构/IPC 套件、截图或前后端/原生联调。

### R10 剩余实施包

1. **R10-02a**：原始执行日志与核对 Module 已接源码，见下节；**R10-02b** 仍需实际 submit requestId / reserve→start 接线、主/独立窗口安全授权等待与决定、实际当前 Bot/task/source/policy 绑定及受控实际 Evidence 读取。不能以文件恰好相同自行结算成功。
2. **R10-03**：局部明确提交、授权/执行/核对反馈，已提交 revision 与后来输入分离；未知结果只“核对”，不自动换 ID 重试；冲突三方比较、另建基础、真正写回后独立验证与签收表达。仅在 R10-02 实际接通后开放按钮。

## R10-02a 原始执行日志与恢复核对（2026-10-27，源码完成，未运行）

先补 ADR109 §39.4，再落严格原始记录/后置记录协议、本机 SQLite v2 事务迁移、执行事实存储与宿主 journal Module。当前没有把 journal 接入个人运行中的应用，也没有开放提交动作。

- 原始 ToolCall/input digest/Projection/session/实际 Grant/Provider Result/Evidence 同源绑定；宿主固定正文计算参数摘要，日志不重复存原参数正文。相同记录幂等、矛盾记录拒绝；归档/正文清理保留原事实。实际结算总是重读并校验原始记录摘要，不用内存索引缓存代替事实。
- v1 迁移不重建资料；旧进程活跃、资料损坏或未来版本时拒绝，原事务回滚。每份原始/后置记录32/16KiB，每个 Bot 合计8MiB；执行前为未完成记录预留容量，不挤占、清除历史实际结果。
- Runtime 在 Provider 返回和 PostToolUse 之间持久化原始事实，后置治理独立落盘。文件已经 applied 时不因后置 Hook 仍存活而继续展示文件执行中；治理尚未确认也不伪称完成。原始结果提交成功但确认丢失时只查原索引，不重复写入。
- journal 只对一次明确、固定 prepared 意图发起 Runtime；重复请求、查询、恢复和显式核对都不启动第二次。真实本机 Promise 与文件执行结果分别表达。写后落盘失败保留 uncertain；当前内容相同只是观察，不是成功 Evidence。后来输入保留。
- prepared 可明确撤回且不伪造 ToolCall；已运行只通过仍存活的真实句柄请求取消，真实 applied 不被迟到取消覆盖。未接通实际 view/source/policy/授权/读取范围前不开放任何提交 UI。

已编写并加入资源工作区用例清单：协议关联/注入拒绝、事务迁移/旧宿主占有/损坏保留、原始结果不可覆盖与正文清理、执行前容量预留、真实 Provider/SDK 持久化顺序、后置 Hook 挂起/异常、落盘失败/确认丢失、恢复只核对不重跑、后续输入和显式撤回。按当前 Validation Scope 只做内容/diff 自审；未运行测试、构建、类型/架构/IPC 套件、截图或前后端/原生联调。不是运行验收。

接下来为 R10-02b：实际 sender/view/writer/revision 的提交保留与授权接线；复用现有权限规则与实际 ApprovalStore，独立绑定资源提交，避免覆盖聊天 active gate；受控范围内读取原 Evidence。之后 R10-03 再接局部提交/授权/结果核对界面。原任务/成果不唤醒、不重跑；未提交/推送、重启或发布。

## R10-02b 主应用提交、授权与实际结果读取（2026-10-27，源码接线，未运行）

先补 ADR109 §39.5，再接宿主绑定/提交协调、独立资源授权桥和主进程组合。typed IPC 与主/原生 preload API 已接；提交 UI 仍未开放。本节更新前面的“主应用尚未接线”历史状态，不代表已在运行的个人应用中生效。

- `ResourceEditApplicationService` 的宿主私有 seam 在实际 view 队列中检查 sender/window/Bot/source、writer 与保存 revision，仅用本机已保存正文 reserve 固定 requestId。随后释放队列，用户可以继续输入。相同 ID 只查询原记录，恢复的 prepared 要另一次明确继续；renderer 不传正文/root/Grant/Result。
- 提交绑定不能由 renderer 构造。主窗口草稿页关闭不等于取消提交；真正 sender 销毁、角色/窗口/Bot 变化或原生租约失效使未执行部分失去来源。取消只作用于资源提交，不调用任务恢复/重跑接口。
- 真实 root/path/resourceId 来自既有 Reader 或原生租约；目录只允许已选合法后代，当前核对只放开旧内容版本条件。实际 Root 传入 SDK/Hook 上下文，授权前后重解析；初始来源失败不能在同一次调用中恢复并跳过项目 Hook 配置，Root 变化也不会自动重定向。文件缺失、来源变化和范围拒绝保留具体原因。
- 资源授权使用实际 BotAccessPolicyAuthority/ApprovalStore 与既有 ChatPermissionGate，独立资源请求 Map，不注册为聊天 active gate，不构造/启动聊天流。Bot full_local 仍产生实际 Grant；Hook 额外确认必须实际决定，既有能力策略拒绝仍优先。scope/策略 stamp/期限/abort 在原 gate 中核验，正面 Grant 仍要精确 capability scope 和实时 validate。
- challenge 仅在原实际窗口/handle 返回，绑定固定操作、参数摘要、随机 challengeId 和期限。renderer 只能本次允许/拒绝，不能传 duration、scope 或 Grant。通知只发送有界元数据，不广播正文/票据，不抢焦点。
- SDK Hook 拒绝/超时的原 Grant 可带 `chat-permission:` 前缀和负面空 scope。实际原审批 ID 保留在 call.permissionCallId；规范原 ToolCall 关联但不改 Grant ID/决定/时点，空 scope 只允许负面事实，不能写入。避免把真实拒绝错留为 uncertain，也保留过期/拒绝原因。
- 原始执行和后置记录通过实际 view 与当前 Reader 范围复核后读取。应用关闭时先结束资源授权等待、收口本机实际 Promise，再关闭本机日志；不关闭/恢复/重放原任务，不把旧 Evidence 当作新的成功。

新增/补写回归源码：跨 sender/窗口和旧 writer 拒绝、排队固定版本与后续输入、显式 prepared 继续、实际 SDK/Provider/SQLite/ApprovalStore 组合、原始结果/外部版本核对不重写、取消与范围收回、原始 Evidence 读取范围、全访问/Hook 额外确认/策略优先、challenge 篡改/过期/abort、聊天 active gate 保留，以及 Hook 拒绝/空 scope 超时的真实关联。已加入组合清单；只执行必要的 IPC preload 代码生成和内容/diff 自审，未运行用例、构建/typecheck/架构/IPC 检查、截图或前后端/原生联调，不登记运行通过。

剩余 R10-03：固定 requestId 的局部提交、授权与结果核对控件，真实原始结果/Diff 展示、后来输入分离、未知结果只核对、冲突/另建基础及独立验证/签收表达。完成 UI 接线前仍隐藏写回按钮。未重启、提交推送或发布，原工作树和任务/成果继续保留。

## R10-03 局部提交、授权与结果核对（2026-10-27，源码接线，未运行）

先补 ADR109 §39.6 与同窗恢复澄清，再接独立前端控制器、主/原生编辑器局部控件和固定提交稿读取。当前源码已包含真正提交按钮，其操作仍完整沿 R10-02 的宿主 journal/权限/Provider 链；没有启动个人应用或提交任何个人文件。

| 体验契约 | 本次落点 |
|---|---|
| 用户目的 | 在原文阅读旁编辑本机稿，明确选择当前稿写回原文件，查看本次固定提议与真实结果 |
| 行动权/事实源 | 委托、保存、授权、执行、后置治理分别表达；宿主状态、实际 Promise、challenge、原始 Result/Evidence 为事实源；用户点击不生成允许/成功/签收 |
| 默认/等待/错误 | 常驻局部状态条；正常反馈不插入会话或整组变灰。prepared 显式继续，live 才请求取消，unknown 仅核对；拒绝、过期、文件缺失、冲突与部分写入各有说明 |
| 输入/身份 | 提交前先确认保存版本；固定前输入变化则本次不提交，固定后新输入另存。双击同一次意图、未确认身份保留；IME 不提交，保存/授权不锁编辑器 |
| 窗口/焦点/读位 | 保留右侧/原生容器，不开遮罩；用户展开详情，复用 Frost token、ui-button 和 MotionDetails。无后台焦点/滚动命令；切换使旧读入失效，减少动效可静态完整使用 |
| 恢复 | 读取/通知/重连不执行写入；迟到旧状态不降级已知终态，不复活旧 challenge。保留实际未返回 Promise，真实回执先到时可继续决定/取消。未受理重连必须先确认旧 view 退休，再查新 view 下原 ID 不存在 |
| 边界/验证 | 只读固定稿是本机意图，不是 Evidence；实际 Diff/Evidence 另走当前源范围。手动写入不签收任务；原任务验证/签收继续由原模型提供。用例已写，运行验收未做 |

具体实现：

- `ResourceSubmissionController` 与 `ResourceEditSession` 分工：后者保存输入，前者只持有实际请求/状态呈现。首次分配 nonce 后不因失败/通知换 ID；重复命令、原始回执先于 IPC 返回、跨 view 迟到、无受理记录的安全重连各自有保护。实例最多32个未返回提交传输，已确认退休的本地未受理 ID 保留有界；没有 UI 定时器驱动重写。
- 实际状态索引分页读完后才允许新提交，已知原始状态/回执不被旧响应覆盖；未知或冲突不会变成虚假成功。原始实际记录在当前 Reader 范围内另读，以便第一层解释真实拒绝/超时原因；大段正文与调用细节保持折叠。
- 同窗恢复由宿主同时核新实际 view、原 sender/window、固定 op 与原来源；退休旧 handle 仍无效。其他窗口只得到“授权在发起窗口”提示，不能代批准，可明确取消资源请求。没有自动把窗口带前或迁移授权。
- 新增只读 `readSubmission` typed IPC/preload：从既有 operation_bodies 读取固定基础/提议，不使用后来输入冒充；留存正文清理后不从同 hash 当前草稿借回。整理历史使当前预览缓存失效，但不删除原始 Evidence。
- 宿主 kernel 拒绝同资源 prepared/running 新意图，以及 uncertain 的原 draft/相同基础换 ID。用户明确读取不同版本并另建草稿后，可以做独立新修改，原 unknown 不被抹掉或伪造结算；新基础已等于原提议时初始无差异，不产生重复写入。
- 冲突或已写回的旧基础保留，局部入口引导比较/另建基础；既有旧基础、当前输入、固定提交稿和当前文件分别可读，不自动合并/重基。原生新基础优先使用新 draft 的真实 source；明确返回阅读才调用原受控 Reader 加载当前版本，读位沿原对象保留。
- 真实 Provider 差异只称有限预览；保留 ToolCall、Grant、Evidence、后置记录原始关联。已写回、后置检查、独立任务验证和签收不合并，不新建验证/签收真源或按钮。

新增/补写源码用例覆盖：客户端自动读取不执行、prepared 显式继续、unknown 只核对、双击与固定稿/后续输入、IME/固定前输入变化、回执先到与迟到 running、原未受理 nonce 的已退休 view 恢复、跨目标响应拒绝、当前状态/权限展示的 live 与身份约束；后端固定稿受控读取/正文清理、同基础阻挡、不同基础独立修改保留旧 unknown、同窗恢复与跨窗口不代批。已经加入资源工作区组合清单。

本轮仅执行必要 IPC preload 代码生成、内容/diff 自审和保留性核对，未运行测试、build/typecheck/架构/IPC 检查、截图/交互或前后端/原生联调；不是产品验收。未重启/发布/提交推送，原工作树与任务/已有成果保持。后续本轮 R1–R10 源码连线审阅见[源码覆盖表](resource-workspace-source-coverage.md)，并按 ADR109 §38.8 补原生关闭的失败/超时保留、显式确认与一次性许可；G7/G8 运行验收仍依用户明确提前验证或发布要求执行。

本轮未提交推送/重启/发布，没有读取/恢复/重跑个人任务。原工作树和索引的保护检查单独记账；源码存在不等于功能通过。
