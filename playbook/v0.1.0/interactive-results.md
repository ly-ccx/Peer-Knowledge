# ADR 118 交互结果实施与验证

创建时间：2026-11-03
最后更新：2026-11-04

状态：实施中，未完成。七项文档补充已交付，用户现已明确恢复“完整实现并测试完成”的目标，继续完整代码实施与提前验证。既有实施、验证和未提交工作均保留。ADR 118 仍保持 Proposed；实现及单项测试不构成决策接受、运行时授权或产品验收。

## 范围与依据

后续范围由 [ADR 118](../../knowledge/decisions/118-openui-interactive-results-and-runtime-boundaries.md) 的首期 IUI-00—04、IUI-T01—29 及 §22 定义，尚待设计评审接受。既有代码起点为 Peer-Agent `4a58e2846875f85de69915764a127096721c5b0d`（RC35），分支 `codex/openui-interactive-results`；知识分支 `codex/openui-interactive-results-adr`。不以单个模块、静态 Demo 或某组测试通过代替完整交付。

当前完整目标覆盖 Protocol、Provider、材料/版本/状态存储、Context Source、界面与多入口及测试，继续推进原范围。实施与测试来自用户恢复的明确目标，不能从 Proposed 文档、阶段表或历史实施/测试记录推导能力开放。公开接口、脚本准入、按需加载和原 Provider encoder、授权、Evidence、任务内核继续作为边界。

## 实施阶段

| 阶段 | 必须交付 | 当前事实 |
| --- | --- | --- |
| IUI-00 | 固定 SDK 脚本/AST/状态/纯求值与副作用审阅，公共接口验证；材料源、事务及逐存储兼容方案 | 公共 AST/严格 token 覆盖、共享预算与纯求值已用于独立 Worker；Bun 单文件探针已从空目录运行。SDK bootstrap 禁用、生产/开发 bundle 的真实 React 挂载和状态适配已有专项验证；产品 CLI、完整宿主接线及其余共享存储兼容尚待完成，未退出 |
| IUI-01 | Protocol/InteractiveContent/MaterialSource、受治理发布与只读检查、只读 worker 例外、版本 CAS、事务与 Evidence 对账、首次新写入前兼容保护 | 已提交 `b7b429ef`、`ea7e5afd`、`94ef2e92`、`9f3e0a7a`、`aabeaef4`、`5f9953ca`。真实 Desktop/TUI Provider、投影/准入/执行闸、规范工具及用户上传材料、启动/查询对账、持久准备身份/修复预算与授权分类已接线并验证；功能默认关闭。`f5eaa173` 补实际旧草稿写者/已打开队列/Conversation 重写的材料保留与准入链；`ecb77e0d` 补有效值/原始草稿的受保护材料准入、真实 Worker 和旧检查点拒绝；`3bf95a40` 补清理事务内核及固定旧写者证明，但真实六来源/保护未接齐，删除入口保持不可用；其余留存及完整能力验收继续待完成，未退出 |
| IUI-02 | Frost 组件、资源引用/会话、状态 CAS/单写者、恢复与冻结条件经原草稿链交回 | `8b3ffbcf` 后，`f5eaa173` 接独立冻结/草稿准备回执、实际主窗口 claim/ack 与宿主读回、原 Composer CAS、明确发送、队列/规范消息及委托材料；真实 Electron 主区/独立窗口与实际草稿/队列/Conversation 联通。`c85b3a42` 补接管前原保存结算与本地输入保留。`4d33ae4e` 补固定初始控件标签与异步冻结；`0af50095` 接宿主确认的 head/predecessor 主区/独立窗口导航并保留旧条件与未完成输入。真实文档/浏览器混合场景及其余产品验收尚未完成；功能默认关闭，未退出 |
| IUI-03 | 显式 Context Source、预算/修复、按角色能力准入、Bot 引用和固定版本语义核验 | 显式 L5 目录 Source 已接入两宿主，按真实投影/角色准入，规则和工具来自同一次投影；目录由公共规格生成，specHash 包含资源限制。委托先核对 Verifier inspect 库存。`fd4fce5a` 接固定目标、临时核验绑定、规范检查 Evidence、完整分页/条件覆盖和 SessionVerification，Desktop/TUI 实际模型循环已有控制传输验证；`8140ce58` 接共享报告/回复固定引用，真实 Desktop ToolHost 与 TUI composition root 已验证；两条真实 Provider 编码路径的首发及固定内容计算已有专项证据；`c7e83b28` / `ece95b44` 已提交可重跑命令，两条实际模型路径的首发、驱动种子修复和主动拒绝降级已有证据；完整真实委托/核验/交还故事仍待完成，未退出 |
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

## 任务报告与主 Bot 回复固定引用增量（8140ce58）

- 契约先在 `7888c10` 的 ADR §9.5 明确，代码 `8140ce585b7e981068ebb621b44a12c5d6852d9b` 已提交并推送。共享 PublicationSource 仅从实际 task/call、已发布操作、固定 manifest 与规范索引取得结果身份；对外报告替换可证明的别名，内部完成审查、原 Plan 和 sourceRevision 保持原事实。元数据投影不读程序/数据正文，不经完整报告递归取数。
- Desktop/TUI 的实际报告和 post_reply 接同一来源 Module；回复在原锚点、sources、statusClaims 校验后由宿主填入既有 meta.evidenceRefs。模型自报 URI/产物无效，原 objective refs 优先保留，共用 20 条上限；完整报告不被截成 20 条。达到上限仍核对后续被引用任务的归属。未确认结果不制造卡片，旧无 parent 任务的普通进展仍可回复；head 推进及 unchanged 均保留原固定身份。
- 279 项 Node 通过，覆盖整个交互运行时、完整 SessionSupervisor、报告/回复和 Renderer 元数据归一化；28 项 Bun 通过，包含实际 TUI composition root → Provider 模型循环 → get_session(report) → post_reply → canonical Bot 消息，以及共享来源/默认 Desktop ToolHost 集成。实际工具宿主测试保留原授权/核验门，不从未验证结果制造通过标记。最初 TUI 夹具使用 inputId 而非 canonical 锚点、把所有叶任务标为完成触发原核验门，以及新增测试的可选方法/ES lib 类型错误，均已修正；最终组合无失败/跳过/取消。
- Runtime Node build、Desktop 全 build、Runtime Node/Desktop/TUI typecheck、architecture/UI 与 IPC check 通过；IPC 仍为 403 channels、435 preload operations、352 main registrations。Desktop 构建保留既有大 chunk 警告，未以提高阈值消除。
- 实际 Electron 专项 1 项通过，先用真实 ReplyComposer 生成并持久化固定引用，再由原 EvidenceView/ApplicationService、正式 preload/授权 IPC 打开；主区/独立窗口、原草稿/人工发送、读位、两种接管、中断输入与 chunk 降级继续通过。最初该夹具缺少已完成叶任务的 result 文本，按原报告契约补齐，未放宽生产收集条件。`peer-interactive-workspace-O3NXhM` 的 8 张原 PNG 已逐张实现者自审，review.json 绑定上述提交，independent=false，审阅指纹 `b21f3530bb79decad9a8e1accc9b9ef64c66bb2e8bf02e69f06926e080642003`。
- Electron 的发布/Grant、Plan/Session 端口与外围壳仍为控制夹具；真实 Desktop/TUI 模型循环使用控制传输，没有实际模型请求。已同步两份体验矩阵及改造计划。本批不代表 head/predecessor 新版本入口、完整留存、多入口、系统 IME/无障碍/性能、最终全仓门禁或标准全产品 packet 完成，IUI-02/IUI-03/IUI-04 与完整目标仍未退出。

## 固定版本导航与原视图连续性增量（0af50095）

- 契约先在 `ef46121` 的 ADR §11.4.1 明确，代码 `0af500950a2c32a79092f9085e9829fcc37e9a5d` 已提交并推送。新增可选 typed readVersions/openVersion；共享 Store/ViewService 仅核对同 owner/resultId 的固定 manifest/head、原发布操作及确认状态，不读程序/数据或求值。待登记、错绑/损坏来源、失效视图与不匹配目标明确失败，不从标题或模型 URI 猜测版本。
- 主资源区调用原 openInteractive 打开固定标签，旧版本的值、原始草稿和阅读责任保留；新版本首次打开取自身初始条件，已访问版本按自己的检查点恢复。独立窗口的宿主从真实原主窗口 sender 打开另一受控窗口，前后重核 owner/view/source；只接受原固定目标与 head/predecessor 关系，不开放通用主窗口 API、路径或模型执行。两条新 IPC 仍沿原 catalog 授权，未新增能力、Grant、Evidence 或持久格式；main.mjs 为装配替换，净增 0。
- C229 版本控件复用 Frost 按钮/静态状态，手动查询、打开与失败各有真实回执，窗口/标签切换或生命周期清理后丢弃旧响应；重订阅不复活旧请求，也不留下永久 loading。既有资源区焦点查询原来把选中标签与任意按钮放在同一选择器中，实际 Electron 新断言先失败；已改为先取已选项再回退按钮，明确打开目标时聚焦实际新标签。
- 最终 172 项 Node、32 项 Bun 通过，无失败/跳过/取消，覆盖 Protocol、整个交互运行时、Desktop ApplicationService、Renderer 交互/版本会话，以及真实 TUI 宿主回归。Protocol/Runtime Node/Desktop/TUI 类型通过；最终 Desktop 全 build、architecture/UI 与 IPC check 通过，IPC 为 405 channels、439 preload operations、354 main registrations。测试最初修正了新测试的 sha256 格式/原生 ready 前置、控制器局部变量遮蔽及生命周期重订阅状态；未放宽生产边界。
- 实际 Electron 专项 1 项通过：保存/草稿/人工发送和旧恢复流程继续成立；发布修订后明确检查并打开新标签，初始 Divisor: 9，返回旧标签仍为未完成的“-”，旧有效值仍为 3；独立窗口实际打开新版本及其上一版本，原窗口保留，旧版本按自己的确认检查点恢复。夹具重载后沿真实证据按钮重新激活资源；不把夹具固定的 activeTab 设置当成已恢复活跃表面。
- `peer-interactive-workspace-LCrKMW` 最终 10 张原 PNG 已逐张实现者自审，review.json 绑定上述源码，independent=false，指纹 `5ed3d6039b4bb34640a904e4e0f14d40c4331ce88ba985a3f827329e10e48bd7`。新版本主区图保留真实 Layout changes are not saved 中间态；窄标签依原 title/可访问名称保留完整身份。发布/Grant、Plan/Session 与外围壳仍为控制夹具，没有实际模型请求。该专项不是标准全产品 packet、安装版、系统 IME、完整缩放/减少动效、读屏或性能验收。
- 已同步 C229/P06/P14 两份矩阵及改造计划。固定引用与版本导航已接，不关闭完整留存、多入口、真实模型、其余恢复/组件/无障碍/性能及最终组合验证缺口；ADR Proposed/default-off 和完整目标未完成的状态不变。

## 两条真实 Provider 编码路径的首次生成（2026-11-04）

- 源码 `0af500950a2c32a79092f9085e9829fcc37e9a5d`，隔离合成任务与设备本地存储。调用既有 CredentialHelper 的只读 API-key 接口，没有复制或更新个人配置/凭据，也未启动日常应用。使用真实 TUI TurnExecutor → Pipeline → 受白名单约束的 ToolHost → 受限 worker Provider；headless runtime 外围与 owner/profile/任务数据为隔离夹具，模型 transport 为真实 API。System Context 由原 TUI assembler 和实际投影目录 Source 组装；模型仅见 publish/inspect 两项能力。
- Anthropic Messages 的已配置 `deepseek-flash` 与 OpenAI Chat 的已配置 `deepseek-v4.1-flash` 各以 2 次真实请求完成一个结果：首次模型发布均通过，无自然修复，实际 Grant/固定结果/规范 interactive 索引已确认。实际生成程序使用 model-data 两行成本 20/35、初始 budget 100、预算控件、Remaining 和表格；共享可终止 Worker 独立读实际固化内容，核对 budget 100 → 45、budget 80 → 25、两行完整且文本投影未截断。该机械检查不等于独立语义 Verifier 或原目标签收。

| 编码路径 / 模型 | 实际 runtime 用量（input / output / cache-read） | 价格与成本限制 |
|---|---|---|
| Anthropic Messages / deepseek-flash | 899 / 1023 / 15360；总 17282，2 请求 | 沿原 usage-pricing 按本机 models.dev-reference 单价估算 USD 0.00079473；不是网关账单 |
| OpenAI Chat / deepseek-v4.1-flash | 8707 / 1344 / 7296；总 17347，2 请求 | 本机该条价格全为 0，可信价格/账单未确认；不能宣称免费或实际成本为 0 |

- 先前 OpenAI 配置中的 `deepseek-flash` 请求未完成，后续单独诊断明确得到 HTTP 400 / Model is unavailable；仅改选已经配置的 v4.1 模型，未修改通道或放宽请求/权限规则。最早隔离夹具缺 active Bot owner profile，真实宿主返回 access_identity_invalid，Anthropic 模型如实给出受阻文字、未发布；补齐真实所需 profile 后成功。该早期拒绝只证明真实模型面对身份拒绝会说明受阻，不能代替主动用户拒绝的完整回归。
- 成功原报告为 `peer-interactive-real-models-PzCSJk/report.json`（Anthropic）及 `peer-interactive-real-models-ShJUj8/report.json`（OpenAI）；机械内容/用量自审在 `peer-interactive-live-review-zbvAE8/review.json`，independent=false。早期诊断的 textFallback 布尔曾仅依据“未发布”填充；按实际模型正文和请求结果核对，OpenAI HTTP 400 没有模型正文，属于 provider failure，不能计作已验证的文本降级。
- 当前 opt-in harness 仍为外部诊断脚本，尚未提交可跨设备重跑的命令；这些结果不构成最终测试交付。后续将真实失败 Tool Result 作为明确的故障种子验证模型修复，沿原 native approval 受控拒绝验证文本降级，并保留每条请求预算和实际来源；不伪造模型首发失败、Grant 或 Tool Result。实际账单不可取得的限制单列。
- 完整目标仍未完成：这不是主 Bot 委托→实际独立核验→交还的完整真实模型故事，也不覆盖最终全仓或标准产品 packet。继续处理完整留存/多入口、其余产品恢复/无障碍/性能以及上述真实修复、拒绝和可复现命令，不因两次首发通过退出 IUI-03/IUI-04。

## 可重跑的真实生成、驱动修复与原生拒绝（c7e83b28 / ece95b44）

- 代码 `c7e83b28` 提交 opt-in 命令，`ece95b4427349a197ca098d6917caae855e4bd3b` 修正失败种子的事实层传输，均已推送原实现分支。复用实际 TUI TurnExecutor/Pipeline、受白名单约束的 ToolHost、共享 Provider/Grant/存储、Context Source 和既有两类 encoder；仅头部终端 UI、owner/Plan/合成任务为夹具。正常启动和日常测试不调用真实模型，生产功能默认关闭。
- `--list`/`--help` 不读取凭据或请求模型；`--run` 必须显式选择已配置的 model entry ID，最多 4 个模型。每模型每场景最多 4 次请求、每请求 1800 输出 token/45 秒、每场景 150 秒/4 次工具调用，物理 HTTP 另有上限并关闭本命令的 transport recovery。输出只创建外部目录中的独立临时子目录；读取既有 API-key credential helper，不修改个人配置/凭据、项目或日常实例。其他 provider wire 与 OAuth 不属于这个验证命令的已覆盖范围。

```sh
pnpm --filter @peer-agent/tui qa:interactive:live --list
pnpm --filter @peer-agent/tui qa:interactive:live --run --model ENTRY_ID_1 --model ENTRY_ID_2
```

从 `--list` 选择实际 entry ID；仓库 helper 尚未构建时可用既有 `PEER_CREDENTIAL_HELPER_PATH` 指定已构建 helper。默认逐个运行 publish/repair/denied，也可用重复 `--scenario repair --scenario denied` 选择。报告包含精确源码及 dirty 标志、实际用量、逐请求结果、原生拒绝、持久版本/操作计数、固定正文与机械计算检查，失败不计成文本降级。模型正文仅保留有界脱敏摘录，账单未暴露，不宣称实际成本为零。

- 修复种子由测试驱动调用真实 ToolHost，取得实际 Grant 及 `unsupported_node / not_committed` 的失败 Tool Result；种子单列为 driverGenerated，不混入模型首发成功率。最初把种子装成 assistant/tool 历史时，Anthropic thinking API 真实返回 HTTP 400，要求原生 thinking block。`ece95b44` 将原候选及真实编码结果作为明确用户事实材料，不伪造模型思考/签名、不提升为 System Context，不关闭实际模型思考来掩盖问题。
- `c7e83b28` 的 `peer-interactive-live-i8rcY9/report.json` 保留两条首发通过及早期失败；Anthropic 的一次拒绝后请求真实连接中断，不能计作完成降级。OpenAI 当批生成/修复/拒绝通过。修正种子后，`ece95b44` 在 `peer-interactive-live-rDm57e/report.json` 实际重跑两模型的 repair/denied，4/4 通过，各 2 次模型/HTTP 请求；原失败报告不覆盖。
- 两个修复各只产生 1 个版本及 1 个已发布操作，规范 interactive 索引已确认，实际固化内容经共享可终止 Worker 检查：100→45、80→25、两行完整且未截断。两次主动拒绝均来自正常 worker 的 `ask_before_local` 原生回调，持久 `denied / local_ui`，版本/已发布操作皆 0；实际模型文字明确未发布、停止且不要求扩权。`restricted_local` 的自动拒绝或 ephemeral 无 approver 不算主动用户拒绝，受控测试已明确这一区别。

| 实际 wire / 场景 | input / output / cache-read | 请求数 |
|---|---|---|
| Anthropic Messages / repair | 1057 / 1163 / 15744 | 2 |
| Anthropic Messages / denied | 363 / 1279 / 15360 | 2 |
| OpenAI Chat / repair | 1284 / 1230 / 15104 | 2 |
| OpenAI Chat / denied | 774 / 1273 / 14848 | 2 |

模型分别为已配置 deepseek-flash / deepseek-v4.1-flash。报告中的 token 来自实际 runtime 用量；网关账单仍不可取得。`peer-interactive-live-rDm57e/review.json` 为事实/正文摘录的实现者自审，independent=false，不是独立语义 Verifier、完整委托故事或目标签收。命令受控测试连同既有 TUI 回合/Provider 回归共 61 项通过，TUI 类型和架构/UI 检查通过。

## 受保护状态准入与原始编辑保留（ecb77e0d）

- 契约先于代码在知识提交 `f1b3306` / `2fd5448` 的 ADR §12.1 定义，代码 `ecb77e0dde3cc446859070c5e21fb455bda8ebf0` 已推送。共享纯校验检查有效值和原始草稿中的可识别凭据签名、赋值、认证 URL 与有界结构化原生 Grant/审批/写者 token 形状，覆盖初始值、求值、宿主保存、检查点/保存回执读回和冻结。诊断仅为 `interactive_state_protected`，不携带匹配原文；不是读取 secret storage 或从任意无标识字符串推断秘密的通用检测器。
- 独立 validateEditingState 只检查内存形状/预算，不提供保存或计算准入。Renderer 保留被拒绝原文、原确认值和 SDK 最后合法状态，创建保存请求前先拒绝，用户修正后可正常保存；原始输入不被脱敏文字替换。宿主仍独立拒绝直接绕过客户端的请求，不写保存回执/冻结行。固定旧检查点触发政策后保持原行，不自动删改或重置为空。
- 最终 175 项 Node、82 项 Bun 通过，无失败/跳过/取消。含共享内容、整个 interactive-results、真实打包 Worker 的初始/求值/摘要校验、SQLite 直接保存/旧记录、Renderer 会话和 TUI 实际宿主/模型循环；Desktop/TUI 类型、Desktop 完整构建、架构/UI 检查通过。初始测试修正了不存在的 TextInput 名称，并实际发现 Renderer 缺少保存前准入而会建立无效 pending 请求；生产路径已补齐，最终测试没有放宽宿主断言。构建保留既有大 chunk 警告。
- 实际 Electron 专项在上述干净提交重跑通过：合成凭据样例保留在输入框，明确提示未保存，SQLite 原确认状态完全一致，修正后保存；原草稿、人工发送、接管、读位、版本导航、中断输入和缺模块恢复继续通过。`peer-interactive-workspace-9k5kHi` 的 11 张原图已逐张实现者自审，review.json 绑定上述源码，independent=false，指纹 `9fcfe380d01dc3bb059b4c0ad341d2b5ac2ec7c3e39a6680f2b341becb20186f`。已同步两份覆盖矩阵和改造计划。
- Electron 的发布/Grant 和外围壳仍为控制夹具，没有真实模型；真实模型命令的证据另按其固定源码记录。本批没有完整标准 packet、安装版、系统 IME、完整缩放/减少动效、读屏或性能验收，不退出完整目标。

## 清理事务内核与固定旧写者证明（3bf95a40）

- 先在知识提交 `32f2c7f` / `08a71d9` 定义 ADR §17.2.1，再实现并推送代码 `3bf95a40`。新增共享 InteractiveRetention 的 preview/cleanup/readReceipt；原状态/保存回执校验提到同一 `state-record` seam，正常读写及维护使用相同不变量。没有新模型工具、IPC、Renderer 删除入口或共享 schema；结果域仍为 SQLite schema 5。默认没有真实 acquireRetentionRoots，运行时清理明确返回 interactive_retention_unavailable，不因 Module 存在而开放删除。
- 私有同步引用守卫必须覆盖 views/drafts/inputs/messages/delegation/verification 六类，核对真实 owner/lease、固定引用、冻结 ID 和来源修订直到 finally release。内核拒绝缺失/异步/过期守卫、跨 owner 引用和缺少的冻结记录。当前正向测试的根集合是控制夹具，不是真实宿主六来源已经完整接线的证据；禁止为启用清理而注入空集合或 always-true current。
- 清理固定逻辑结果的全部版本，事务内重新核 head/版本集合、原真实操作、状态/保存回执、prepared 尝试、index_pending、活跃写者与根引用；摘要绑定来源修订、数据/状态和可回收对象集合。先标 cleaned 并保存带摘要校验的独立 presentation 墓碑，再删除该结果的状态/保存行及无其他可用版本或材料引用的对象，一起原子提交。任何提交前失败或配额失败全部回滚；丢确认仅查回同一实际回执，不重发发布。回收数是逻辑对象字节，不宣称 SQLite/WAL 文件缩小或安全擦除。
- 墓碑保留各固定版本的有界、明确截断的模型摘要、实际来源和数据等级，并核对原 metadata/operation；旧版本也能解析同一真实清理回执。原发布 metadata、操作、EvidenceIndex 及冻结值不改写。正文清理不删除 followup/material 行，不冒充已经完成这些对象的 GC。墓碑每 Bot 有上限，参数冲突、损坏或超过限额明确拒绝。只有全部版本真正不可用才释放逻辑结果配额；未知 availability、缺 head 或仅部分版本 cleaned 不制造空余。
- 固定 `ecb77e0d` 的 Store、SQLite storage 和 presentation writer 源码，仅适配 import 位置；测试将位置还原后重新核 SHA-256，辅助协议在本批未变。实际已经打开的旧连接及重开读端均拒绝 cleaned 正文，旧发布幂等重放不复活数据。独立旧进程在清理事务中真实写入被 SQLite 锁阻止；之后旧 writer 可创建不同结果，旧 history/layout 写入或删除只影响自身类别，清理墓碑保留。旧 writer 的原额度判断会保守拒绝，不能将这项数据保留证明描述为旧产品具备新清理体验。
- 最终 188 项 Node、114 项 Bun 通过，无失败/跳过/取消，包含整个 interactive-results、共享内容、Renderer 会话与真实 TUI 宿主/模型循环的控制传输回归。Runtime Node 构建、Desktop/TUI 类型及 architecture/UI 检查通过；第一条共享材料断言曾缺必需 expectedContentVersion，按实际契约修正测试，未放宽生产读取。没有新 UI、截图、真实模型请求、安装版或标准全产品 packet；本批不退出 IUI-01/IUI-04 或完整目标。
- 下一步先为六来源实现严格根读取与真实写入保护，覆盖已打开旧 writer 和回执/claim 中间态，再接显式清理及已清理文本投影。随后完成冻结材料/规范快照的独立引用保留与 GC。不能用当前内核的控制根测试代替跨存储保护，也不能仅因为已发布正文包含副本就删除原规范材料。

## 草稿引用守卫与队列旧写者实测（8aad821d）

- ADR 契约先以 `c843edd` 推送。代码 `8aad821d` 复用实际草稿写锁，保护三表面（含空路径），从当前草稿及待发恢复记录扫描类型化引用与旧传输附件，逐项核对真实冻结回执，核对上传 blob 哈希和再次读取的来源摘要；遇到冲突或损坏会释放已取得的锁。端口尚未装配到生产清理。
- 独立固定旧进程实际尝试写入三个表面，活 PID 的目录锁即使超过过期阈值仍返回 DRAFT_BUSY。测试还覆盖新写者、第二个 guard、已损坏记录和部分取得锁后的回收。固定旧队列则实际抢占过期活 PID 锁并成功追加；当前队列目录锁不可作为生产引用守卫。
- 37 项 Node 测试通过，覆盖草稿、输入队列及其缓存、反馈传输与清理内核。其余真实引用端口、队列兼容保护、用户清理入口和全量验收仍待交付。

## 活跃视图的跨进程引用（a754adca）

- ADR §17.2.1 先在 `ce894fa` 定义，再推送代码 `a754adca`。ViewService 在交付固定版本前通过同一 SQLite 写事务校验当前归属与固定版本，登记独立 presentation 类别。只读视图也登记；写事务失败时打开明确失败。实际关闭、取消、发送者销毁与打开失败释放 pin。瞬时释放失败时保留 pin，并在后续打开/关闭或服务释放时重试；持续失败会保守阻断到进程退出。
- 清理在同一事务读取活 PID 的固定版本 pin，纳入阻断与摘要；损坏记录失败，确定已退出的 PID 不阻断，后续视图打开清除遗留。固定旧 layout 写者保持 pin；旧 ViewService 自身没有 pin 登记，仍须单独证明隔离或退出才能打开生产清理。
- 162 项 Node 测试通过，覆盖共享交互结果和 Desktop 主进程交互模块。真实独立进程证明未取得状态 writer 的视图能使旧预览失效，正常关闭与强制退出后能清理，且损坏 pin 会阻断。Runtime Node 构建及架构/UI 检查通过。本批未完成其余根来源、用户清理入口或完整产品验收。

## 规范消息引用守卫（9065f271）

- ADR §17.2.1 先在 `4df2f9d` 定义。Conversation Store 复用规范消息写者的 index 目录锁，按宿主提供的显式会话集合扫描完整原始 JSONL，验证 UTF-8、文件身份、行数、大小与修订。反馈适配只输出经过真实冻结回执校验的固定引用与材料 ID。集合完整性与旧迁移写者仍需由宿主接线证明。目录锁沿用旧 Store 行为，硬退出遗留锁仍需显式恢复；生产清理保持关闭。
- 实际跨进程追加和重写均被阻断，释放后可继续写。测试加速旧写锁的等待计时，保留实际锁竞争。共享 Conversation 写者与固定旧源码逐字节一致，仅剔除新的独立 guard import 和返回端口后核 SHA-256。用例还证明背景读取裁掉的规范尾部仍纳入扫描，临时 sidecar 不参与；缺会话、坏 JSON 与未知载体版本失败并释放锁。
- 257 项 Node 测试通过，覆盖 Conversation Store 与共享交互结果模块。两个包构建及架构/UI 检查通过。完整会话集合、跨存储端口和生产清理尚未交付。

## 活跃核验引用守卫（52e79710）

- ADR §17.2.1 先由 `b97e96a` 定义。实际 Verifier service 从当前 review 生命周期收集固定版本和冻结材料 ID；同步持有期间阻止同 owner 建立新 review，结束 review、失去执行租约或 Bot 归属变化使旧守卫失效。保留生命周期中的引用，即使该 turn 已变旧。Desktop/TUI 现有组合根分别将本宿主的同一个 InteractiveRuntime 交给核验入口。
- 实际 review 测试证明结果及冻结引用能阻断清理，关闭后旧预览失效，新 review 可恢复。测试的其余来源为控制夹具。164 项 Node 测试通过，Runtime Node 构建及架构/UI 检查通过。跨进程历史核验、可恢复委托的持久引用和生产组合仍待实现。

## 委托会话的规范消息范围（7e68836c）

- ADR §17.2.1 先由 `fc197ea` 定义。通过实际 Conversation Store index 写锁，在同一快照内验证 Bot 的角色及 workspace，从规范父子元数据扫描直属 work_session；不依赖 UI 列表、任务已提交或调用方预先枚举。重复、缺失或错误绑定的元数据阻断，守卫同时提供已覆盖的会话 ID 供后续持久计划对账。
- 真实 spawn 及重开测试移除父消息中的冻结附件后，仍从委托子消息找回真实固定引用；无计划的已创建子会话也覆盖，错误 workspace 拒绝。258 项 Node 测试、Conversation Store 和 Runtime Node 构建、架构/UI 检查通过。可恢复任务计划的独立 Evidence/控制引用、队列及生产组合仍待完成。

## 持久委托和核验续跑引用（7956b99a）

- ADR §17.2.1 先由 `2ba8bda` 定义。共享 runtime 接入按真实租约读取的委托引用适配。在持有规范消息 guard 时，直接读有界 plan JSON，绑定 Bot、直属会话和 session；检查固定版本、同任务发布别名及规范核验回执，复核冻结材料和文件/Evidence 修订。已完成、验收、交回及无未结束核验的计划保留历史证据。
- 实际发布与检查后，测试从没有索引项的已重开计划找回固定版本和冻结条件，写入新计划使快照失效，缺少检查回执时停止。历史验收分类用受控持久记录覆盖。259 项 Node 测试、Conversation Store/Runtime Node 构建、架构/UI 检查通过。
- 该适配依赖当前租约、文件修订检查及已持有的会话守卫；对可绕过租约的旧 plan/Evidence 写者还未建立排他证明。队列、跨存储组合、用户清理入口和全量验收仍未开放。

## CLI 固定结果文本与墓碑（42b96db8）

- ADR §19 先由 `148eb54` 定义。实际 `peer result <interactive-result://…> [--json]` 从当前本机 Bot profile 校验 owner，在只读存储连接上核对固定版本及已登记的原发布；清理后读取带摘要校验的固定墓碑。纯文本和 JSON 标出可用性、来源、摘要性质及截断，过滤终端控制字符。无模型回合、求值、GUI 或执行租约。
- 17 项 Bun CLI 测试、15 项 Node 清理/加载测试通过。另以独立 Bun 编译二进制，在无 DISPLAY、无 TTY、临时目录运行真实命令专项，覆盖 help/version、pending、JSON/文本、跨 owner、终端控制字符及清理后摘要。清理测试使用控制根，未开启生产删除。Runtime Node 构建、TUI 类型、架构/UI 检查通过。
- 已交付 CLI 显式读取。TUI 数据表、CLI exec 自动交付、Remote 及完整独立安装验收仍待交付。

## TUI 固定任务报告文本与表格（4e3d1cb7）

- ADR §19 先由 `e36d6c4` 定义。实际 TUI `/task N → /result N` 用当前 Bot 和任务报告绑定固定版本。复用静态摘要/墓碑与有界 worker 初始条件求值。读取过程不生成 Evidence，取消或离开后不展示迟到结果。纯计算与模型摘要分别标示，终端翻页由用户控制。
- 14 项 Bun 测试、Runtime Node 构建、TUI 类型及架构/UI 检查通过。OpenTUI 实际字符帧专项读取真实持久结果、滚到后续表格行并退出，覆盖错 session、AbortSignal 及 Evidence 保持。测试保留了既有 harness 的 React act 警告。已更新两份覆盖矩阵和改造计划；CLI exec、Remote、安装版与完整验收仍待完成。

## Remote 固定任务结果（03f0589a）

- ADR §19 先由 `e257ef1` 定义。原项目任务授权下，从实际报告固定引用读取发布/墓碑，每任务最多八项。D0/D1 返回脱敏有界摘要；D2 以上只含引用与可用状态。复核授权、任务和读取端口，纯文本展示，无新远程动作。
- 217 项 Gateway/Remote Node 测试通过，Protocol 构建、Desktop 类型、架构/UI 检查通过。真实配对 WebSocket、HTTP 及 Chromium 390 像素专项通过，公开摘要中的 HTML 字符按纯文本、私有标题及正文被抑制、退出清空；三图逐张实现者自审，列表、原会话和任务窄窗换行均检查。证据目录 `peer-mobile-browser-Kg2DrW`，无页面错误。专项使用控制输入及已登记发布，未覆盖实体手机、远程 cleaned 的实际浏览器样本或完整产品验收。
- 普通 `peer exec` 现明确关闭交互 Provider，CLI 已有本机显式读取；自动交付须接合规 Bot 运行入口，不能以普通会话或助手文本模拟。生产清理和全量验收仍待交付。

## CLI Bot 规范回复自动交付（d8cf1b75）

- ADR §19 先由 `d62b155` 定义。显式 `peer exec --bot` 走工作目录已绑定 Bot 的输入队列和普通宿主租约；既有宿主可接收，CLI 不发起接管。只等本次 inputId 的第一条规范回复，从宿主 meta 中读取实际已发布的固定结果，文本和 JSON 独立分流。未收到回复时返回已入队状态、原 inputId 与专用退出码 8；退出其他宿主的客户端不会持久暂停该宿主的任务。
- 36 项 Bun 测试及 TUI 类型、架构/UI 检查通过。实际 CLI 子进程把输入交给已有租约的真实 TUI 宿主，在控制模型传输下走任务报告 → post_reply → 规范回复 → CLI JSON；同 ID 重试、冲突及超时通过。独立 Bun 编译二进制在无 DISPLAY/TTY 下重复验证。尚未以真实模型运行这条 CLI 交付，也未跑完整安装/标准产品包。
- 普通 exec 保持原模型和能力范围。生产清理所需旧写者隔离、完整恢复、多入口验收和真实模型的端到端任务仍待交付。

## Desktop 静态墓碑恢复（aac32860）

- ADR §17.2.1 先由 `8c8448b` 定义。原 Evidence 入口按固定发布、规范索引及 owner 核对墓碑；历史工具别名仍归原任务。独立资源窗口通过原 IPC 展示静态摘要，回执不携带视图 handle；损坏墓碑阻断。清理历史和布局复用正文/墓碑检查，保留读位。
- 166 项 Node 测试、Protocol/Runtime Node 构建、Desktop 类型/IPC、架构/UI 检查通过。实际 Electron 专项通过，人工自审本次新增 `peer-interactive-workspace-deNjTC/native-cleaned-summary.png`。前一版截图发现读位失败提示，最终图确认已消失。清理使用受控根，新增截图自审非独立，其他帧仅由本次自动断言覆盖；尚无生产清理或完整标准验收。

## 后续接线与完成审计

- 主资源区标签、布局、最近项目和正式返回已接；继续覆盖实际文档/浏览器混合场景、布局超时后重试读取的读位、Bot 归属永久变化后的不可保存草稿退出恢复、SDK 挂载异常、全组件目录、缩放/辅助技术与性能，不把单结果隔离夹具算作全产品验收。
- 规范发布索引的交付入口及受控任务 context 中的 Tool Result 别名消费已接；主 Bot 报告/回复的固定结构化引用已在 `8140ce58` 接线；宿主确认的 head/predecessor 新版本入口已在 `0af50095` 接线。没有任务 context 的别名不推断工作；不从助手正文、标题或 URI 文本推断产物或版本关系。
- 冻结条件到原 Composer、明确发送、输入队列、canonical 消息及委托的同值同版链已接；固定目标/完整条件/真实检查证据已接两宿主并通过控制传输用例，固定初始控件标签及异步冻结在本批补齐。继续覆盖完整留存与清理和其余存储重写者，不把控制模型测试当作真实任务语义验收。
- 清理事务内核已在 `3bf95a40` 提交；继续接真实六来源、逐存储/旧写者保护、明确清理和墓碑文本投影，以及冻结/材料独立 GC；CLI 显式读取、Bot exec 自动交付、TUI 任务报告数据表与 Remote 任务投影已接；完整独立安装验收仍待完成。用户参数/原始草稿的可识别凭据与原生权限载荷已在 `ecb77e0d` 接共享/宿主准入及内存修正恢复；其格式识别边界与测试覆盖单列，不依赖提示词。接管前原保存结算已在本批完成，继续覆盖永久 owner 变化等其余恢复责任。
- 两种实际 Provider encoder 的真实首次生成及固化计算已取得专项证据；可复现命令、驱动种子修复与主动拒绝降级已在本批覆盖；继续完成完整任务故事、成本限制核对、全仓工程门禁和标准产品 capture → AI 逐图 review → verify。还需覆盖 SDK 挂载异常、主工作区故障恢复、完整组件/图表目录、减少动效/放大/辅助技术及性能；明确记录系统 IME、安装版和真实模型覆盖边界。所有已完成的本批用例只证明其实际覆盖，不代替这些缺口。
- 核对发布诊断 retryable 与有限次新候选修复的 Interface：本批实际 unsupported_node 失败标记 retryable=false，但同一受限工作可用新调用提交修正候选；需要明确“原调用重发/对账”与“校验失败后新候选”的适用语义，不能从模型本次成功自行推出所有失败都可重试。
