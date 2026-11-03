# ADR 118 交互结果实施与验证

创建时间：2026-11-03
最后更新：2026-11-03

状态：实施中，未完成。七项文档补充已交付，用户现已明确恢复“完整实现并测试完成”的目标，继续完整代码实施与提前验证。既有实施、验证和未提交工作均保留。ADR 118 仍保持 Proposed；实现及单项测试不构成决策接受、运行时授权或产品验收。

## 范围与依据

后续范围由 [ADR 118](../../knowledge/decisions/118-openui-interactive-results-and-runtime-boundaries.md) 的首期 IUI-00—04、IUI-T01—29 及 §22 定义，尚待设计评审接受。既有代码起点为 Peer-Agent `4a58e2846875f85de69915764a127096721c5b0d`（RC35），分支 `codex/openui-interactive-results`；知识分支 `codex/openui-interactive-results-adr`。不以单个模块、静态 Demo 或某组测试通过代替完整交付。

当前完整目标覆盖 Protocol、Provider、材料/版本/状态存储、Context Source、界面与多入口及测试，继续推进原范围。实施与测试来自用户恢复的明确目标，不能从 Proposed 文档、阶段表或历史实施/测试记录推导能力开放。公开接口、脚本准入、按需加载和原 Provider encoder、授权、Evidence、任务内核继续作为边界。

## 实施阶段

| 阶段 | 必须交付 | 当前事实 |
| --- | --- | --- |
| IUI-00 | 固定 SDK 脚本/AST/状态/纯求值与副作用审阅，公共接口验证；材料源、事务及逐存储兼容方案 | 公共 AST/严格 token 覆盖、共享预算与纯求值已用于独立 Worker；Bun 单文件探针已从空目录运行。SDK bootstrap 禁用、生产/开发 bundle 的真实 React 挂载和状态适配已有专项验证；产品 CLI、完整宿主接线及其余共享存储兼容尚待完成，未退出 |
| IUI-01 | Protocol/InteractiveContent/MaterialSource、受治理发布与只读检查、只读 worker 例外、版本 CAS、事务与 Evidence 对账、首次新写入前兼容保护 | 已提交 `b7b429ef`、`ea7e5afd`、`94ef2e92`、`9f3e0a7a`、`aabeaef4`、`5f9953ca`。真实 Desktop/TUI Provider、投影/准入/执行闸、规范工具及用户上传材料、启动/查询对账、持久准备身份/修复预算与授权分类已接线并验证；功能默认关闭。`f5eaa173` 补实际旧草稿写者/已打开队列/Conversation 重写的材料保留与准入链；其余共享存储、留存及完整能力验收继续待完成，未退出 |
| IUI-02 | Frost 组件、资源引用/会话、状态 CAS/单写者、恢复与冻结条件经原草稿链交回 | `8b3ffbcf` 后，`f5eaa173` 接独立冻结/草稿准备回执、实际主窗口 claim/ack 与宿主读回、原 Composer CAS、明确发送、队列/规范消息及委托材料；真实 Electron 主区/独立窗口与实际草稿/队列/Conversation 联通。`c85b3a42` 补接管前原保存结算与本地输入保留。`4d33ae4e` 补固定初始控件标签与异步冻结；真实文档/浏览器混合场景及其余产品验收尚未完成；功能默认关闭，未退出 |
| IUI-03 | 显式 Context Source、预算/修复、按角色能力准入、Bot 引用和固定版本语义核验 | 显式 L5 目录 Source 已接入两宿主，按真实投影/角色准入，规则和工具来自同一次投影；目录由公共规格生成，specHash 包含资源限制。委托先核对 Verifier inspect 库存。`fd4fce5a` 接固定目标、临时核验绑定、规范检查 Evidence、完整分页/条件覆盖和 SessionVerification，Desktop/TUI 实际模型循环已有控制传输验证；Bot 结果引用与真实模型生成/修复效果待完成，未退出 |
| IUI-04 | 多入口文本、包体/按需加载、兼容和完整功能验证 | 待实现 |

## 验证与完成标准

七项文档补充提交只做内容、引用及 diff 审阅。恢复后的完整实施目标明确包含测试，提前验证与改动相关的模块和宿主链；完成后执行完整 build/test/type/architecture/IPC 及产品 capture → AI 审阅 → verify，逐项记录实际覆盖。只使用隔离临时数据，不安装或重启日常应用，不创建版本/RC 或发布标签。

验收清单是 ADR §22 的 IUI-T01—29，以及两种实际已配置 Provider 编码路径的真实模型生成/修复/降级记录。需要实际配置或外部条件的项目若无法完成，明确登记缺失，目标保持未完成；不以脚本模型夹具替代真实模型、不把源码自审称为独立验收。最终回执列明实际代码提交、测试结果、产品证据、真实模型/安装包/多入口/无障碍覆盖。

## 当前验证记录

- `ea7e5afd`：Protocol 构建与 runtime-node 依赖链构建通过；材料/事务/状态/Worker 共 26 项测试在 Node 25.9.0 与 Bun 1.4.2 通过。
- `94ef2e92045e651e80fbc5dbb9543ab3b09ef050`：五包依赖链构建通过；Protocol、Runtime Core/SDK/Node 四包 typecheck 通过；`node scripts/check-architecture-governance.mjs` 通过（未以此代称含 UI 的完整 architecture 门禁）。
- 同一代码的定向组合共 109 项 Node 测试通过，覆盖协议/内容、交互运行时、EvidenceIndex 缓存/桌面预览证据、SDK Hook 和真实 Desktop 文件 Provider；runtime-node 全包 1805 项与 runtime-sdk 全包 41 项通过；交互运行时 52 项在 Bun 1.4.2 通过。Node 为 25.9.0，无 skip/cancelled。
- 固定 RC35 normalizer 与已打开追加描述符实测保留原始发布行；丢确认的持久登记不重复追加。同一 wire call ID 跨子会话互不冲突；校验时钟不制造无变化版本，分类提高不会因 unchanged 降级。真实 Node/Desktop 文件读取改写当前源文件后，快照仍为原字节；完整 sideband 不进入序列化事件。
- 最新代码生成的 Bun 单文件校验/求值探针在无 node_modules 的空目录运行，help 与 Worker 求值通过；二进制 62,672,754 字节，SHA-256 `9905092a1ee95fdb0ed125c41ea550d840d898c36627a8ab3bee9c08abbfcfbc`。这是隔离测试探针，不是产品 TUI/CLI 的安装、包体或入口验收。
- `9f3e0a7a`：依赖链构建、Runtime Node/TUI 类型检查及 `check-architecture-governance.mjs` 通过；228 项 Node 定向组合测试与 95 项 Bun TUI 宿主/回合/模型适配测试通过，均无 skip/cancelled。覆盖真实 Desktop/TUI 文件 Provider → 固定材料 → 受限发布 → 持久索引、Verifier 实际只读求值、角色/租约/旧 epoch、原调用参数固定、跨实例修复预算与索引追加后失去所有者的恢复责任。不是完整仓库门禁或产品回归。
- 同一提交的目录 Source 为约 6 KiB，现有宿主保守估算约 1490 token；这不是 Provider tokenizer 实测。Source 只从可信目录生成，不准入程序/材料内容；普通问答、Explorer、无投影和不完整发布/检查能力组合不开放语言。生成的 specHash 与实际公共适配同源，并包含统一资源限制。
- `aabeaef4`：规范 user_upload 仅从当前工作 canonical 用户消息的有界内联正文建立固定引用；观察时间来自真实消息，密钥字段同时从文本和 JSON 投影脱敏，不伪造 Tool Evidence。190 项 Node 定向组合与 63 项 Bun 交互运行时测试、依赖链构建、Runtime Node/TUI 类型及治理检查通过，均无 skip/cancelled；不代表完整产品验收。
- `d3643cf7`：SDK 变换只作用于通过公开根入口定位的 SDK 模块；实际 Vite 配置测试确认开发 bootstrap 不进入该产物，应用其他模块不受影响。3 项定向测试通过，尚未以 React 实际挂载证明运行期无副作用。
- `5f9953ca`：授权前只读核对实际来源等级，scope 绑定最高分类；来源或 owner 分类在授权期间提高时拒绝旧 scope 提交。真实成功观测即使正文过大不能固化，也保留 owner 单调隐私底线；关闭功能不会清除此底线，首次关闭状态不创建结果子域。新冻结反馈继承当前底线，历史冻结值及分类保持不变。68 项 Node 与同样 68 项 Bun 交互运行时测试、依赖链构建、Runtime Node/TUI 类型及治理检查通过，无 skip/cancelled。
- `9c726072`：106 项 Node 定向组合、98 项 Bun 定向组合、依赖链构建、Desktop/Runtime Node/TUI 类型及完整 `architecture:check` 通过，无 skip/cancelled。共享 `prepareEvaluator` 只编译固定公开 AST，一次核对目录/状态 schema 后同步检查候选；Set/Reset 只执行当下真实已准入的 SDK plan，展开后最多 16 步，失败不部分修改输入。该限制包含在 specHash。
- 同一提交的 `interactive-renderer.test.mjs` 在独立临时数据的 Electron 41.7.1 中实际挂载固定 SDK 与 Peer 组件，分别构建 production/development bundle；在 SDK 加载前拦截网络，未观察到 HTTP/WebSocket 请求、页面异常或 devtools 自动挂载。实际覆盖输入 DOM/焦点、合成 composition、除零时隐藏结果、恢复计算、Select、Checkbox 键盘/标签点击、分页及无关参数变化保持页码、局部 Reset、宽窄及两主题。四张组件截图逐图实现者自审；窄图与前次已审图片逐字节相同，宽图再次检查。不是系统 IME、真实模型、安装版、完整产品 packet 或原生资源窗口验收。组件夹具的状态端口仅为隔离内存适配；真实 SQLite/sender/CAS/冻结链由上述独立领域测试验证，尚未接成正式产品链。
- `518420a4`：130 项 Node、115 项 Bun 定向组合和 46 项既有资源/可信窗口/返回状态组合通过，无 skip/cancelled；Desktop 构建（含依赖与 IPC catalog）、Desktop/Runtime Node/TUI 类型和完整 `architecture:check` 通过。这是本批模块与入口验证，不是完整仓库门禁。隔离 worktree 的 Electron npm 安装不完整，Node 宿主测试借用既有 dist 定位，GUI 测试直接选择既有 Electron 41.7.1 可执行文件；未安装或重启日常应用。
- 同一提交的原生专项通过实际 `NativeResourceWindow`、生成 preload、catalog 授权、应用服务、结果/状态 SQLite 和阅读记录运行；已发布结果及 Grant 为确定性领域夹具，不是真实模型或任务发布验收。覆盖确认保存、合成 composition 阻止关闭、保存后再次关闭、重开恢复同值/固定版本/读位、只读摘要降级保留损坏检查点及旧读位；同时核对无文件读取、旧 Settings 写入、重复版本/发布操作、HTTP/WebSocket 和页面异常。3 张原生图逐张自审；关闭失败提示已改为“上次关闭”的历史事实，避免保存后仍声称当前未保存。
- 最新生产/开发 SDK 组件专项也重新通过，4 张图的两种构建输出按主题分别逐字节一致；实际再次查看两张唯一图片并核对全部指纹。原生与组件证据均为实现者自审（independent=false），不是完整产品 packet、安装版、系统 IME、读屏或真实模型验收。原生返回测试的主窗 ack 为宿主夹具；正式混合标签返回消费者仍待接入。
- 交互 SQLite 当前内部 schema 为 5，内容规范编码为 `peer-interactive-content-1`；在准备记录、候选预算与 owner 分类底线之外加入有界阅读历史和布局 metadata。早期分支 schema 1—4 拒绝读写，不做静默迁移或空库重建。首次关闭功能不创建新子域，旧 Settings 写者不会接触 interactive 记录；布局仅已有发布结果的 owner 可首次建立，服务端 revision CAS 已落实，UI 消费者尚未接入。该设备本地新子域未在日常产品中启用；现有 Conversation/草稿兼容保护仍待接线。
- 下一步兼容工作须保留实证差异：输入草稿现有未知 schema 拒写，但旧输入队列会跳过不认识的 ResourceFeedback，不能只扩展联合类型就宣称兼容。冻结条件目前仍停留本机结果子域；需先补齐草稿/队列/消息/委托同值同版的保护及明确发送链，再开放交还入口。SDK chunk/挂载异常的局部降级与重试也尚待接线，不能用普通计算错误和目录不兼容测试代替。
- `98693645`：复用共享延迟加载错误边界，原生控件 chunk 缺失时保留固定摘要、源码入口和领域会话。实测同 URL 的直接重试仍失败，因此原生恢复明确先确认保存，再重载该隔离视图；主工作区备用动作只打开独立视图，不刷新整个应用。后者待正式标签消费者接线后验证。显式恢复中断的 composition 仅把原文本作为草稿保存，不改有效值，也不能冻结成新条件。8 项 Node 会话用例、13 项 Bun 会话/registry 用例与真实 Electron 原生专项通过，4 张原生图逐图自审；缺文件、恢复文件、确认重载、同值同版/旧读位恢复均实际运行，零新发布/取数/外部网络。Desktop 构建、类型及 `architecture:check` 通过；不是系统 IME、主工作区故障或完整产品验收。
- `30cb612b` / `11e2a617`：混合布局 formatVersion=2，包含独立交互表现会话（最多 32 个同 owner 固定引用与读位），参数/草稿/writer 不得进入其中；保留文档、Diff、浏览器和最近描述符。规范化后再次限制 URL/整体字节，避免 canonical URL 膨胀产生自身不可读的行。格式 1 只按已知结构保留升级，旧请求缺少交互会话字段时拒写。固定 `518420a4` 写者在同一已打开存储中先成功写格式 1，再证明格式 2 的旧 order/recent 投影仍合法、但实际旧写者因未知行字段拒绝读写，原行保持；不是靠新增 Diff key 让测试偶然失败。134 项 Node、118 项 Bun 组合与最终 15 项 Node/7 项 Bun 定向用例通过，依赖链构建、Desktop/Runtime Node/TUI 类型与治理/UI 检查通过。SQLite schema 仍为 5；布局有独立行版本，尚未接 UI 消费者。
- `8b3ffbcf01a9b9a14ac6969a9e67a1918876b528`：布局 API 固定预期完整 owner，并在主进程核对真实归属。纯表现会话按固定引用重放迟到读期间的意图，接受真实 CAS 回执；丢确认先读真实行，冲突保留两份候选，显式采用远端前确认输入并换代阅读回调。关闭仅从打开顺序移除，保留有界读位提示；满额只淘汰已关闭提示。旧 Settings 不保存交互种类/引用，旧 localStorage 适配器拒绝覆盖已有新字段/引用、未知或损坏记录。
- 同一提交经规范 EvidenceIndex 的 worker 发布元数据投影交付卡片，使用独立 `interactiveReference`；核对当前 Bot owner、真实 plan/session/conversation、capability/tool 与 Evidence/Artifact 身份。助手文本、普通文件 URI 和跨 owner 元数据不能升级为交互产物。主资源区首次打开仍经实际视图入口重新核对；该卡片不表示任务、计算或验证通过。
- 62 项 Node、同样 62 项 Bun 定向契约用例、23 项既有资源/可信窗口/返回状态用例、两个隔离 Electron 场景通过，均无 skip/cancelled。Desktop 完整构建、Desktop/Runtime Node/TUI 类型、`architecture:check`（含 UI）和 Desktop `ipc:check` 通过。这是本批验证，不是全仓测试/完整产品门禁；构建仍提示既有大 chunk，产品包体与性能验收未完成。
- 主区专项使用实际 `WorkbenchProvider` / `BotResourceLayout`、交付卡片、生成 preload、catalog 授权、领域应用服务、原生控制器及 SQLite；已发布内容和 Grant 为确定性夹具，外壳/非本域草稿索引为夹具。实测同版关后重开/读位、独立窗口接管与正式返回 ack、不覆盖原会话草稿、显式布局冲突恢复并拒绝旧读位回调、组合输入阻止关闭、离开视图后复制/保存中断原文而不改有效值。真实移走 Surface chunk，再恢复文件，确认保存后打开独立视图，未刷新主应用或新增发布/取数。原生专项同步复测缺模块重载、状态损坏摘要及旧读位保留，并在截图前加强终态断言。
- 8 张图逐图实现者自审，`independent=false`。最新主区组 `HhCsGk`、原生组 `tEmfu4`；三张主区图、三张原生图与此前已查看输出逐字节一致，其余两张实际重新查看。联合截图指纹 `c21087433effc26e68b03f7432fee26a420664ff4cf0cc03e5c8ec11cd4b70ac`。主区关闭自动化包含 Playwright 对 beforeunload dialog 的 dismiss，断言实际关闭尝试后窗口仍在及原输入可恢复；不是系统 IME 或手动安装版验收。仍未实际联跑文档/浏览器混合标签、全部缩放/减少动效/读屏/性能，也不是标准产品 packet。
- 上述均为实现者验证，未做独立审查、完整仓库门禁、真实模型或完整产品回归，不构成 IUI-00—04 完整交付；最新后续结果随接线补充。

## 冻结条件交回与传输增量（f5eaa173）

- 代码 `f5eaa17340bb56a094f403364fecf41f76713473` 已推送原实现分支。新增 typed prepareDraft 与生成 preload/catalog 接线；私有 viewHandle 只解析同 owner/固定结果的真实冻结材料，独立视图从实际 registry 找原主窗口，不接受 Renderer 自报接收者、反馈正文或 sender。冻结成功与原草稿准备成功分开；claim/ack 后宿主读回持久草稿或待发材料，不能只凭 Renderer ack 显示成功。
- 原 Composer 保留正文、quote 和附件，准备前预留传输附件额度；超额拒绝且不编辑原草稿。只有明确发送才调用原输入队列。准备确认丢失时复用原 followupId；稍后编辑、保存及接管不改变原冻结值。IME/无效的新候选不能退回上次冻结值，未知或不匹配回执不显示已准备。
- 逻辑 ResourceFeedback 增 interactive 分支，实际草稿首次写入格式 3 并保持门槛。队列/规范消息/委托使用旧端已知的有界文本附件承载完整冻结 JSON，新端在准入/消费/委托/结果访问时匹配真实冻结记录；不建立第二队列，不生成工具 Evidence 或授权。模型历史只在原 user 材料槽投影一次，界面显示未验证引用；损坏/未来版本保留原文，不跳行推进新端游标。
- 固定 `8b3ffbcf` 的真实旧草稿写者、旧上传 normalizer、已打开旧队列对象及实际 Conversation 重写/重开证明材料保留。对照用例也证明把新联合类型直接写旧队列确会被跳过并推进游标，不能用 marker 冒充兼容。真实 SessionSupervisor 将明确锚点转为子消息，原附件与冻结版本完整保留；篡改材料在创建子任务前拒绝。原结果访问与 followup 准入只接受实际记录，不借助手文本或 schema 标记取得权限。
- 295 项 Node 定向组合、55 项 Bun 定向组合及 1 条真实 Electron 主区/原生/Composer/输入链专项通过，无 skip/cancelled；新增 prepare-draft 的来源/顶层 frame 政策另在 6 项宿主组合中复核。Desktop 完整构建、Protocol/Runtime Core/Runtime Node/Desktop/TUI 类型、architecture:check（含 UI）和 Desktop ipc:check 通过。构建仍有大 chunk 提示；本轮不是全仓测试或完整发布门禁。
- Electron 专项使用真实 BotComposer/useInputRecovery、prepare/claim/ack、SQLite、输入队列及 ConversationStore。主区冻结 5、独立窗口冻结 4，原正文/quote/上传均保留；准备不提交、不抢原 Composer 焦点，人工点击发送后 canonical 消息才同时携带 5/4。关后重开、接管/正式返回、布局冲突、关闭拦截、中断草稿与缺 chunk 恢复继续通过。发布/Grant、外壳和非本域索引仍为夹具，没有真实 Provider 模型回合。
- 6 张最终截图逐图实现者自审，independent=false，目录 `peer-interactive-workspace-wGz5ql` 的 review.json 绑定上述代码；审阅指纹 `5d1c3ca2d5e1766d56552db4d6e2a9ad25a5a51535a95fbacd41cad338184ceb`。初次发现测试入口缺正式 Composer CSS 已修正并重采；冻结摘要去掉内部 ID/变量名，存储不保留表现树时暂用稳定条件序号，精确控件标签映射仍须完成。6 图不是标准全产品 packet，也没有真实模型、安装版、系统 IME、读屏、完整缩放/减少动效或性能验收。

## 固定目标核验增量（fd4fce5a）

- 先在知识提交 `88caab0` 定义 ADR §10.2.1，再于代码 `fd4fce5af81a08e8766a13fa30a66ab1e31bac51` 实现。目标来自真实任务的规范发布记录/本工作原调用别名及 canonical 用户提交的完整冻结材料；不把其他结果、未提交选择或最新 UI 状态纳入核验。初始条件与各冻结条件分别保留；owner、执行换代、租约、功能或目标摘要变化会使原回合失效。
- 宿主持有有生命周期的私有核验绑定，衔接实际 conversationId 为空的 Verifier；Desktop profile 正规化保留并核对 execution identity。私有 token 不进入模型请求或 System Context，结束后失效。临时回合的真实观测仍可记录 owner 的保守隐私等级，不因此开放正文读取或恢复执行。
- 每次真实 inspect 在原 EvidenceIndex 持久追加并读回 `interactive-inspection://` 规范记录，只含固定请求、范围、状态/目标/输出摘要与执行事实。正式 EvidenceBundle.refs 负责传播。固定旧 normalizer、已打开追加描述符和重开后的读端证明原规范记录及来源保留；不建立另一套 Evidence 索引。
- 完整程序、每个完整绑定的连续分页，以及初始/各冻结状态的完整求值，是交互语义通过的事实覆盖前提。缺页、重复页、selector 子集、未返回完整计算、只给发布/文本回执均不能满足；业务判断仍归模型。语义缺证返回失败，不进入 JSON 格式修复。实际模型投影同时修正 Verifier 使用的 explorer 模式和大快照超过 64 KiB 后的分页声明。
- Node 223 项通过，无失败/跳过/取消；范围为 Protocol、Core Evidence、整个 interactive-results、核验/criterion 系列、Desktop profile/投影/GoalHost 及连续核验。Bun 61 项通过，无失败；包含 TUI 实际 GoalHost → Executor → Pipeline → Provider、原 TUI 回合/模型测试及共享核验用例。Desktop 的实际 Responses loop → 投影 → Tool Host → Provider 取得 4 份规范检查回执，SessionVerification 持久语义事实通过。上述模型响应使用控制传输，未调用真实模型。
- Desktop 全 build、Protocol/Core/Node/Desktop/TUI typecheck、architecture/UI conventions 与 IPC check 通过；IPC 为 403 channels、435 preload operations、352 main registrations。最初两项 Desktop 测试因隔离依赖缺 Electron 开发二进制而导入失败；复用已有同版本 41.7.1 开发二进制后重跑及最终组合批次均通过，日常应用未安装或重启。本批没有改界面，没有新截图验收。
- 本机配置元数据已确认存在 OpenAI/Anthropic 两种可用工具/结构化格式声明的编码路径；这只是配置清点，尚无真实请求、修复、降级或成本记录。未运行最终全仓及标准全产品 packet，本批不构成 IUI-03/IUI-04 退出或完整目标完成。

## 保存结算与接管增量（c85b3a42）

- 契约先在 `9f32918` / `102d512` 明确，代码 `c85b3a428a82e23c6b1154bc667f91dec7de69bc` 实现。领域 save 保持原快照返回，宿主使用同一事务内的 saveOutcome；沿原 typed save IPC 返回 writerCurrent 或可信 not_committed，不新增通道、存储格式、权限或 Evidence。原请求先按 identity/writer/revision/值及草稿摘要核对；历史回执的 schema、原身份、revision 和正文也重新校验。
- 原写者失效后可查回真实历史提交；无原记录且写者已隔离或当前 revision 严格超过原 CAS 基础，才能证明未提交。未来 revision、旧端只有 stale、参数冲突、读盘或回执损坏保持未知。Renderer 不在 writer_lost 时跳过原请求，也不在 acquire 时清空未知责任；明确接管保留原待确认值、后续编辑和未完成数字草稿，新提交使用新 requestId。没有待确认输入的干净视图仍采用实际当前状态。
- 153 项 Node 通过，无失败/跳过/取消，范围为 Protocol、整个 interactive-results、Renderer 会话/registry 与 Desktop ApplicationService/资源会话。46 项 Bun 通过，包含状态、视图、会话/registry 及两条 TUI Provider/实际核验回归。Desktop 全 build、Protocol/Node/Desktop/TUI typecheck、architecture/UI conventions 与 IPC check 通过；IPC 仍为 403 channels、435 preload operations、352 main registrations。
- 真实隔离 Electron → 正式 preload/授权 IPC → 应用服务 → SQLite 专项通过：分别让原窗口的保存已提交丢回执/尚未提交，另一窗口写入 7/9，再明确接管恢复原值 6/8。保留原 Composer 草稿与人工发送、关后重开、布局读位、中断输入及 chunk 失败恢复；产物版本/发布操作仍各 1，无额外发布。发布/Grant 和外围壳仍是控制夹具，没有真实模型调用。
- `peer-interactive-workspace-MHDUO8` 的 8 张图已逐张实现者自审，review.json 绑定上述源码；independent=false，字节审阅指纹 `0df87f3ffdb172d176e6aa5f06d64f8b91133887055de06fdb803058377d24a0`。已同步两份体验矩阵和改造计划。此专项不包含标准全产品 packet、真实模型、安装版、系统 IME、完整缩放/减少动效、读屏或性能，完整目标仍未完成。

## 条件标签与异步冻结增量（4d33ae4e）

- 契约先在 `7a92823` / `b9cedf7` 的 ADR §12.5.2 明确，代码 `4d33ae4e63a3f6da695c3f8a1ba2f6b6cd2a8cbf` 实现。InteractiveContent 的 describeState 经同一公开 SDK 校验固定内容并重建初始标签，StateStore 经独立 2 秒/64 MiB 可终止 Worker 调用；不采用 Renderer 渲染树，不持久化另一份派生树，不改变协议、数据库格式、权限或 Evidence。
- prepareFollowup 在 Worker 前后分别核对真实 owner/view、原 writer、revision/digest、字段及合法输入；等待期间不持有 SQLite 事务，提交继承实际最新分类底线。已存在的 canonical followup 仍幂等返回原文；同一视图重复请求共享一次投影，不同并发请求明确 busy，真实视图关闭/销毁中止原请求。状态/写者/归属变化、取消或不匹配摘要均不生成冻结行。
- 初始命名控件使用固定标签；当前合法值导致除零等试算失败仍可讨论，不重新求值该失败分支或取默认参数替代。没有初始命名控件的字段采用稳定条件序号。原检查点在冻结前已变化时，显式重试以新的 save requestId 确认原点击候选；后续编辑继续留在原视图，原冻结材料不漂移。
- 174 项 Node 通过，涵盖 InteractiveContent、整个 interactive-results、Renderer 会话/registry 与 Desktop ApplicationService。54 项 Bun 分两批通过，覆盖 Worker、状态/视图/会话与两条 TUI 实际 Provider/核验链。Desktop 全 build、Protocol/Node/Desktop/TUI typecheck、architecture/UI 与 IPC check 通过；IPC 仍为 403 channels、435 preload operations、352 main registrations。新增测试最初有一处异步时序等待及一处预期错误码不符，已按真实服务入口及现有 incompatible_catalog 契约修正，最终组合无失败/跳过/取消。
- 隔离真实 Electron 专项 1 项通过：主资源区及原生窗口将带 Trial name / Divisor 的 5/4 条件加入原 Composer，正文/引用/附件与人工发送链保持；接管保存、布局/阅读位置、中断输入及 chunk 失败恢复继续通过。发布/Grant 与外围壳是控制夹具，未运行实际模型。`peer-interactive-workspace-ApPG3l` 的 8 张 PNG 均逐张实现者自审，review.json 绑定上述源码，independent=false；审阅指纹 `3b73d50e71b3259dbe9c7c8035e0f40a32dbecd97011f05cbf6d217f206bc8d4`。已同步两份体验矩阵和改造计划；这不是最终标准产品 packet、安装版、系统 IME、完整缩放/减少动效、读屏或性能验收。

## 任务证据别名与规范来源增量（c57f603b）

- 契约先在 `37f41bc` / `a9ff20d` 的 ADR §9.5 明确，代码 `c57f603be72542ca63c462da688601faa46c44c4` 实现。共享 PublicationSource 按真实任务 context、Plan/Session/report、当前 owner 及工作 conversation 查同一次发布回执；随后核对固定版本与规范索引的 capability/tool/call、时间、artifactRef、标题及 specHash。Store 提供只读 getVersionMetadata，先核对来源身份再读程序/数据正文，正文读回后的描述再次一致核对。人读取沿原 ApplicationService，模型仍沿 inspect Provider；没有新能力、IPC、存储格式、权限或 Evidence。
- 真实 Desktop composition root 将服务接入原 EvidenceReader。具有明确任务 context 的工具别名可以打开原规范发布；无任务 context 不猜测同名工具调用。unchanged 修订只在真实回执及两边任务身份确认后沿原发布 context 投影，原来源不改绑。固定引用读取提供明确标为未验证的原模型摘要，不能借用文件读取或当前 head。来源缺失、索引待登记/冲突均保持不可用，不触发发布或恢复执行；metadataOnly 仍只查原索引，不读取正文。
- 178 项 Node、9 项 Bun 通过，覆盖整个交互运行时、Desktop ApplicationService/证据读取及既有应用服务、两条 TUI Provider/核验链。包括同 owner 两工作与跨 Bot 同名 call、缺失/错绑索引、待登记操作、unchanged 来源及正文读取前身份拒绝。新增旧 Plan 无 parent 绑定的普通文件回归先真实失败，随后修正为原文件投影继续可用，不能将交互来源要求扩大到所有旧证据。Node/Bun 最终无失败/跳过/取消；Runtime Node/Desktop/TUI typecheck、Desktop 全 build、architecture/UI 与 IPC check 通过，IPC 仍为 403/435/352。
- 实际 Electron 专项改用正式 EvidenceView、ProjectAgentApplicationService 和同一 PublicationSource，经生产 preload/授权 IPC 从 `tool-result://publication` 打开固定结果，原主区/独立窗口、条件草稿与人工发送、布局/接管/中断/chunk 恢复继续通过。一次重载因真实未保存保护超时；测试已改为等待确认并明确重试重载，没有绕过保护。逐图检查发现夹具缺 Evidence CSS，补导入正式 bot-drawer.css 后重采最终 8 图。`peer-interactive-workspace-umOyTs` 的 review.json 绑定上述源码，independent=false，指纹 `4304b254f0c897dec4bf531986d19722eec4114b0ce13ca6ef8280a1c03d0fa6`；浅色读位截图保留真实布局待保存中间态。发布/Grant、Plan/Session 端口及外围壳仍为控制夹具，未据此声称整机任务或真实模型完成。
- 已同步 P14/P06 两份体验矩阵与改造计划。本批完成受控任务证据到固定发布的消费；主 Bot 报告/回复引用、head/predecessor 新版本入口、完整留存、多入口与实际模型效果仍未完成，不能关闭 IUI-02/IUI-03/IUI-04 或全目标。

## 后续接线与完成审计

- 主资源区标签、布局、最近项目和正式返回已接；继续覆盖实际文档/浏览器混合场景、布局超时后重试读取的读位、Bot 归属永久变化后的不可保存草稿退出恢复、SDK 挂载异常、全组件目录、缩放/辅助技术与性能，不把单结果隔离夹具算作全产品验收。
- 规范发布索引的交付入口及受控任务 context 中的 Tool Result 别名消费已接；继续完成主 Bot 报告/回复的固定结构化引用，以及宿主确认的 head/predecessor 新版本入口。没有任务 context 的别名不推断工作；不从助手正文、标题或 URI 文本推断产物或版本关系。
- 冻结条件到原 Composer、明确发送、输入队列、canonical 消息及委托的同值同版链已接；固定目标/完整条件/真实检查证据已接两宿主并通过控制传输用例，固定初始控件标签及异步冻结在本批补齐。继续覆盖完整留存与清理和其余存储重写者，不把控制模型测试当作真实任务语义验收。
- 完成留存/清理责任、TUI/CLI/Remote 实际文本和独立打包入口。另核对用户参数/原始草稿中已知凭据或权限 payload 的权威准入限制，不能只保护工具观测材料或依赖提示词。接管前原保存结算已在本批完成，继续覆盖永久 owner 变化等其余恢复责任。
- 完成两种实际 Provider encoder 的真实模型生成/修复/降级、全仓工程门禁及标准产品 capture → AI 逐图 review → verify。还需覆盖 SDK 挂载异常、主工作区故障恢复、完整组件/图表目录、减少动效/放大/辅助技术及性能；明确记录系统 IME、安装版和真实模型覆盖边界。所有已完成的本批用例只证明其实际覆盖，不代替这些缺口。
