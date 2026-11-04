# ADR 118 交互结果实施与验证

创建时间：2026-11-03
最后更新：2026-11-05

状态：实施中，未完成。七项文档补充已交付，用户现已明确恢复“完整实现并测试完成”的目标，继续完整代码实施与提前验证。既有实施、验证和未提交工作均保留。ADR 118 仍保持 Proposed；实现及单项测试不构成决策接受、运行时授权或产品验收。

## 范围与依据

后续范围由 [ADR 118](../../knowledge/decisions/118-openui-interactive-results-and-runtime-boundaries.md) 的首期 IUI-00—04、IUI-T01—29 及 §22 定义，尚待设计评审接受。既有代码起点为 Peer-Agent `4a58e2846875f85de69915764a127096721c5b0d`（RC35），分支 `codex/openui-interactive-results`；知识分支 `codex/openui-interactive-results-adr`。不以单个模块、静态 Demo 或某组测试通过代替完整交付。

当前完整目标覆盖 Protocol、Provider、材料/版本/状态存储、Context Source、界面与多入口及测试，继续推进原范围。实施与测试来自用户恢复的明确目标，不能从 Proposed 文档、阶段表或历史实施/测试记录推导能力开放。公开接口、脚本准入、按需加载和原 Provider encoder、授权、Evidence、任务内核继续作为边界。

## 实施阶段

| 阶段 | 必须交付 | 当前事实 |
| --- | --- | --- |
| IUI-00 | 固定 SDK 脚本/AST/状态/纯求值与副作用审阅，公共接口验证；材料源、事务及逐存储兼容方案 | 公共 AST/严格 token 覆盖、共享预算与纯求值已用于独立 Worker；Bun 单文件探针已从空目录运行。SDK bootstrap 禁用、生产/开发 bundle 的真实 React 挂载和状态适配已有专项验证；独立 CLI/TUI 归档已读同版固定结果。生产清理需要的旧读写者兼容方案尚未确定，未退出 |
| IUI-01 | Protocol/InteractiveContent/MaterialSource、受治理发布与只读检查、只读 worker 例外、版本 CAS、事务与 Evidence 对账、首次新写入前兼容保护 | 已提交 `b7b429ef`、`ea7e5afd`、`94ef2e92`、`9f3e0a7a`、`aabeaef4`、`5f9953ca`。真实 Desktop/TUI Provider、投影/准入/执行闸、规范工具及用户上传材料、启动/查询对账、持久准备身份/修复预算与授权分类已接线并验证；功能默认关闭。`f5eaa173` 补实际旧草稿写者/已打开队列/Conversation 重写的材料保留与准入链；`ecb77e0d` 补有效值/原始草稿的受保护材料准入、真实 Worker 和旧检查点拒绝；三类清理事务和真实六来源已接，`8d49fbde` 补执行租约切换后的只读清理对账。生产旧读写者兼容守卫和公开清理入口尚待，未退出 |
| IUI-02 | Frost 组件、资源引用/会话、状态 CAS/单写者、恢复与冻结条件经原草稿链交回 | `8b3ffbcf` 后，`f5eaa173` 接独立冻结/草稿准备回执、实际主窗口 claim/ack 与宿主读回、原 Composer CAS、明确发送、队列/规范消息及委托材料；真实 Electron 主区/独立窗口与实际草稿/队列/Conversation 联通。`c85b3a42` 补接管前原保存结算与本地输入保留。`4d33ae4e` 补固定初始控件标签与异步冻结；`0af50095` 接宿主确认的 head/predecessor 主区/独立窗口导航并保留旧条件与未完成输入。临时目录包已实测结果、文档、浏览器混合资源区和持久布局。正式 macOS 公证安装及完整读屏待验，功能默认关闭，未退出 |
| IUI-03 | 显式 Context Source、预算/修复、按角色能力准入、Bot 引用和固定版本语义核验 | 显式 L5 目录 Source 已接入两宿主，按真实投影/角色准入，规则和工具来自同一次投影；目录由公共规格生成，specHash 包含资源限制。委托先核对 Verifier inspect 库存。`fd4fce5a` 接固定目标、临时核验绑定、规范检查 Evidence、完整分页/条件覆盖和 SessionVerification，Desktop/TUI 实际模型循环已有控制传输验证；`8140ce58` 接共享报告/回复固定引用，真实 Desktop ToolHost 与 TUI composition root 已验证；两条真实 Provider 编码路径的首发及固定内容计算已有专项证据；`c7e83b28` / `ece95b44` 已提交可重跑命令，两条实际模型路径的首发、驱动种子修复和主动拒绝降级已有证据；隔离 Desktop Responses 与 TUI Anthropic Messages 均已有两次正式回复的整案证据。Desktop 样本跨隔离包升级恢复，TUI 样本绑定 `3365486f`，当前组合候选的同提交真实模型整案尚未重跑，未退出 |
| IUI-04 | 多入口文本、包体/按需加载、兼容和完整功能验证 | CLI/TUI/Remote 文本入口和 Desktop 按需加载已有实现及专项取证。Desktop 与 TUI 的真实模型整案均取得第二次正式回复。`8d49fbde` 标准产品包完成逐图自审和 verify，临时独立 CLI/TUI 归档通过固定结果读取，最新 Linux `.deb` 通过隔离安装、Orca 路径及状态重启恢复，AppImage 在 Debian x64 虚拟机通过 FUSE 和自解包启动与恢复。生产旧端兼容守卫、正式 macOS 公证安装及完整读屏尚待验，未退出 |

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

## 输入队列引用守卫（f1208008）

- ADR §17.2.1 先由 `e39b84c` 定义。队列在实际共享追加/游标锁下只读扫描完整的有界 JSONL，校验游标、载体及冻结回执，保护所有可按 inputId 恢复的记录。新版写者不因活 PID 锁变旧而抢占；提交前复核文件修订、锁身份及 owner token。队列内容不因扫描而推进、重写或消费。
- 165 项 Node 测试、Runtime Node 构建、架构/UI 检查通过。独立新版写者尊重人工老化的锁，固定旧写者则仍可抢占实际新版守卫，守卫检测到失效。截断和已消费载体均覆盖。macOS 上目录时间调整会影响 birthtime，最终采用 owner token 校验。
- 恢复死锁时串行检查恢复权。进程在回收目录期间硬退出可能留下待显式恢复的锁，尚未覆盖此崩溃窗。旧写者跨存储隔离及生产清理组合仍待交付。

## 六来源清理组合（e4fe0749）

- ADR §17.2.1 先由 `9141370` 定义。InteractiveRuntime 按固定顺序取得兼容、草稿、队列、规范消息、委托与核验守卫，逆序释放。视图由同一结果事务扫描真实 pin。固定版本和冻结 ID 去重，全部来源在清理过程中复核。普通运行缺真实旧写者兼容守卫时继续拒绝清理。
- 使用真实 SQLite、草稿、队列、Conversation、委托计划、核验及只读视图的组合测试，通过六类阻断、兼容失效无提交、持锁失败回收和无引用结果的真实清理。兼容端口使用隔离目录的控制夹具，生产跨版本排他、锁恢复及用户清理入口仍待交付。168 项 Node 测试、Runtime Node 构建、Desktop/TUI 类型、架构/UI 检查通过。

## 新版队列锁崩溃恢复（7b375b7f）

- ADR §17.2.1 先由 `8389fd1` 定义。新版输入、游标和引用读取共用设备本地 SQLite 互斥事务与原目录锁；互斥只承担锁生命周期，队列与游标保持原格式。进程终止自动释放 SQLite 锁，实际死 PID 的原目录锁可由后续新版写者回收。上一版遗留的恢复目录已不参与锁判定。
- 独立持锁进程被 SIGKILL 后，两名新版写者并发成功追加且无重复；固定旧写者抢走目录时，新守卫失效，另一个新版写者仍受 SQLite 互斥限制。167 项 Node、17 项 Bun、Runtime Node 构建及架构/UI 检查通过。旧写者仍可绕过新版互斥，跨版本隔离和生产清理仍待交付。

## 两条真实 Provider 线路的语义核验（45102335）

- ADR §22.2 先由 `551ac9b` 定义。`--scenario verify` 在隔离 Bot 工作会话实际发布，经保存和冻结形成合成预算 80，再进入实际 GoalHost → TUI Executor → Provider → 独立核验回合。驱动器建立会话、提供合成条件和精确目标参数；模型实际发出检查调用、读取输出并提交 verdict。未通过的新输入不由驱动器修正为通过。
- 最终干净代码 `45102335` 的 Anthropic Messages / deepseek-flash 与 OpenAI Chat / deepseek-v4.1-flash 均通过。各 4 次真实 HTTP 请求（2 worker、2 Verifier），全部四类检查回执可核对且未截断，两个语义报告各引用四条规范检查 Evidence。固定数据 A=20/B=35，两行完整，初始 100 → 45、冻结 80 → 25。每条线路的 worker 与 Verifier 共用同一配置模型，回合、身份与可见工具独立。
- 运行用量（输入 / 输出 / 缓存读取）分别为 Anthropic 7,621 / 2,843 / 24,448 与 OpenAI 8,739 / 3,156 / 22,912；账单不可取得。证据目录 `peer-interactive-live-TeWViX`，实现者核对源码、请求、报告和规范回执。首次真实运行 `peer-interactive-live-deKUuQ` 两线均发布成功，Anthropic 有完整检查回执但宿主未判通过，OpenAI 在原预算内缺两次求值。随后提供精确检查参数、要求只引用规范检查 ID，并记录逐回合诊断，预算与宿主判定未放宽。更早一次凭据 helper 未解析，实际 HTTP 请求为零。
- 12 项 Bun 测试、TUI 类型及架构/UI 检查通过。完整主 Bot 自主委托和最终交付、生产清理与标准验收仍待完成；当前结论限于合成结果的语义核验。


## 真实主 Bot 任务故事增量（66b8bfe1）

- 新增显式 `qa:interactive:live --scenario story`，复用 TUI 项目宿主及其规范输入队列。第一条输入委托只读工作发布固定预算；确认发布 Evidence 与任务记录后，驱动器经实际状态保存和冻结端口提交第二条用户输入。该输入通过既有材料准入进入新的核验委托。成功判据包含独立 Verifier 通过、四类固定检查回执、主 Bot 规范回复引用两个任务和同一个产物，以及任务文本入口能够读取。
- 该专项只投影合成案例所需的委托、协调、结果与 Goal 工具。模型、工具和物理 HTTP 分别设限；最多 32 次模型/HTTP 请求，45 秒/请求，240 秒/整案。两项任务由真实主 Bot 建立；驱动器不建立子会话、不预填结果或 verdict。桌面 Composer 交互仍由单独原生专项覆盖。
- `8c27c98e` 的首轮真实 Anthropic Messages 已观察到主 Bot 委托、worker 读取 Goal 并发布成功。驱动器把同一次发布的规范 Evidence 和工具调用别名重复计数，提前终止；证据目录 `peer-interactive-live-NPTAYz`。代码 `66b8bfe1` 按规范 Evidence 计数，并等待原任务记录该发布后再提交冻结条件。TUI 类型检查与原专项 11 项 Bun 测试通过，修正后真实重跑仍需核对完整结论。
- `66b8bfe1` 重跑再次完成实际委托和发布，但 `goal_get_plan` 回执超出通用内联预算，工具返回的首尾预览省略了真实 taskId；worker 猜测的 ID 被宿主拒绝，未触发第二条输入。主 Bot 后续回合也收到 Anthropic 400，要求把原有 thinking 传回 API。完整报告待该进程结束后核对，目录 `peer-interactive-live-WPI1pR`。
- 上述超长回执还暴露 TUI 材料化未向编码器传入实际宿主数据根，合成工具输出落入默认用户 artifacts 目录。代码 `e642fa3d` 在 TUI 实时模型与持久回合两个编码调用处沿既有 `baseDir` 绑定宿主数据根，两种专项也显式绑定其隔离根。TUI 类型及 43 项 Bun 测试通过，新增超长结果落盘路径和原文回读用例。先前生成的诊断材料仍保留；Goal 读取的预算内叶子身份与 Anthropic 续接待修。此处没有把本次结果视为完整任务通过。

- 代码 `8dcb2028` 调整 TUI Goal 读取回执的序列化顺序，把真实 planId 与任务放在长 brief 前。完整计划字段保持可回读，原 Evidence 和状态更新约束沿用。TUI 类型与 Goal Bridge 的 10 项测试通过，新增超长计划经生产工具结果编码器材料化并同时核对预览 taskId 与完整原文的用例。干净代码已在 OpenAI Chat 真模型复跑中完成原 worker 任务，第二条输入带同一份冻结条件进入规范消息，并由真实主 Bot 创建后续核验任务。观察时后续 worker 正在执行，已在该隔离数据根看到工具材料化文件。目录 `peer-interactive-live-THLjZZ`，独立核验和最终回复仍无结论。

- OpenAI Chat 的 `8dcb2028` 复跑最终用完 32 次请求，并在整案时限终止。后续 worker 已真实读到固定程序、绑定数据、初始求值和冻结求值，但后续任务未完成，无该任务独立 verifier 通过或最终规范交付。仍按真实失败记录；未调整原预算。
- 代码 `d2ba0137` 复用 TUI Provider encoder，实际 Anthropic 原生 thinking/signature 只随同一 Provider、模型的活消息身份续接；序列化检查点和规范历史保持普通消息。DeepSeek 强制回放时，缺失原生数据的历史助手和配对工具结果作为有标签事实处理。TUI 类型及两个适配器文件 39 项 Bun 测试通过，覆盖实际工具循环和恢复历史；真实 Anthropic 复跑目录 `peer-interactive-live-n6XylB`，仍需核对终态。

- Anthropic 原生续接修复后的真实样本完成原任务、提交冻结输入，进入后续回复链。在 24 次请求内无 thinking 相关 HTTP 400；主 Bot 使用完自己的 16 次额度，期间多次直接读取结果，没有建立第二个任务。该样本没有端到端通过证据。
- 代码 `15878144` 细化两条合成用户输入，原 worker 负责发布与记录，后续 worker 读取一次冻结求值，四类完整覆盖由独立 Verifier 负责。请求或工具额度到限时记录角色并结束等待；整案、单角色和 HTTP 额度均沿用。TUI 类型及专项 11 项 Bun 测试通过，OpenAI Chat 重跑目录 `peer-interactive-live-kZQHuN`。

- OpenAI Chat 的 `15878144` 样本在 24 次实际请求后明确返回 `story_request_limit:bot`。最后两次第二委托分别遗漏规范锚点和结构化 `successCriteria`，由原宿主拒绝。验证输入在 `31890f1c` 给出真实锚点和数组形状，仍由模型调用生产工具，额度未变。
- Anthropic 样本的 Goal Runner 日志另发现既有恢复缺陷。模型引用未登记的工具结果别名时，宿主原已判定未通过，随后把无效引用提交给严格存储，导致修复链抛错。代码 `7c818c52` 按现有任务 Evidence Index 持久化真实引用并保留结构化缺证原因，让 worker 可修复后重审。两个共享 Goal 测试文件共 30 项通过，包括真实持久存储下的失败、修复与再次通过。该变更仍需新源码全仓复跑和真实模型验证。

## 独立冻结材料回收（599993fc）

- ADR §17.2.2 先由 `1db324c` 定义。代码 `599993fc` 在现有六来源与兼容守卫下增加单份冻结快照预览、确认清理及回执读取。活视图、活写者和受保护固定引用或 followupId 阻断，守卫或快照变化使预览失效。事务仅替换该快照内容为有界墓碑，保留真实原请求身份及清理回执，不把旧请求重建为新快照。
- Runtime Node 构建和 47 项留存/状态/核验测试通过，覆盖引用、写者、过期摘要、提交前中断与重试。另以固定 `ecb77e0d` 的旧 StateStore 源码（SHA-256 `fe4def99ad683e6567d748aafe0df8f24c36d0ec77ee1dee766e115fedb542ca`）配合实际旧 ResultStore，在同一已打开的连接验证清理前读取原值，清理后拒绝读取和重复冻结，墓碑保留。该验证只覆盖该存储协议，生产全局旧写者隔离和用户入口仍待交付，材料快照回收仍为独立工作。
- 正式工作树的 Desktop 尾段 9 项通过，包括真实原生窗口、SDK 和主工作区。两种真实模型路径在干净代码 `31890f1c` 上按原额度复跑，证据目录 `peer-interactive-live-imodeB`，终态待核对。

## 独立规范材料回收（d83ae47a）

- ADR §17.2.3 先由 `6ad5402` 定义。代码 `d83ae47a` 以固定 source 及版本、六来源守卫与独立材料责任守卫核对预览、提交和回执。可用版本的 provenance、未决发布或仍有责任的规范源阻断；只在同一事务提交墓碑后回收无其它实际引用的对象。原材料唯一键和版本身份保留，不恢复旧材料，也不改写发布正文或 Evidence。
- Runtime Node 构建与 51 项存储/材料/发布测试通过，覆盖缺守卫、责任仍在、provenance、失效预览、提交中断、同请求重试、共享对象及固定旧 ResultStore 的已打开读取/写入。该材料责任守卫仍使用受控夹具，生产根组合、跨版本全局排他和用户入口仍待交付。
- 两线样本 `peer-interactive-live-imodeB` 已结束。OpenAI Chat 在后续 worker 超限；Anthropic 用 28 次请求完成后续任务及计划级独立核验（四条引用），主 Bot 重复查状态后超过工具额度，未产生会话级 verdict 或最终规范回复。代码 `ec841a4e` 在合成目标明确要求使用实际 `verify_session` 并记录有界脱敏工具参数，TUI 类型通过。下一次真实 Anthropic 样本继续沿同一预算。

- ADR `0d32cfd` 与代码 `34e56a53` 将材料责任证明接入现有持锁根组合。规范消息保留真实工具调用和附件；草稿及输入队列保留附件身份；尚可恢复的委托及正在核验的目标保守阻止回收。材料守卫沿原生命周期复核，不重复取得同一把锁。Runtime Node 构建及 56 项测试通过，其中实际 Runtime 组合核对未结束委托、规范工具记录、草稿/队列附件、过期预览与孤立对象清理。生产跨版本排他和用户入口仍未开放。
- Anthropic 样本 `peer-interactive-live-tkbve4` 用 30 次请求走到真实 `verify_session`，后续计划核验的四条有效回执中另有未登记引用，宿主记录缺证，后续修复触及 worker 上限，最终回复未交付。还发现规范失败回执采用了模型的 “Verifier passed” 摘要。代码 `aaf3fb82` 以实际宿主判定为准写入缺证摘要，并在现有 Verifier 提醒明确区分规范检查引用、工具别名和其他任务引用；原证据门槛不变。Runtime Node 构建与 27 项测试通过，已启动新源码实连。

- ADR `4500b61` 和代码 `e3ed3262` 将 Desktop/TUI 的实际草稿和队列实例交给共享清理 Module；Desktop ApplicationService 与 TUI 客户端复用这些实例。TUI 20 项及 Desktop 46 项宿主组合测试通过，另以受控兼容守卫和实际 TUI 草稿锁验证 busy 阻断及释放。代码 `74176e0a` 将材料责任证明收口到持锁根快照，删除独立覆盖入口，30 项留存与核验测试通过。正式源码已同步并启动全仓复跑。生产没有可证明的旧写者兼容权威，公开清理仍未开放。
- Anthropic 样本 `peer-interactive-live-9N0Ebu`（`aaf3fb82`）用 29 次请求完成原发布和冻结后续任务。两个计划的独立核验均通过，后续计划引用四条规范回执；该样本的主 Bot 在会话级核验前达到请求上限，已有回复是进度而非最终交付，未计整案成功。

- 代码 `bbbfea4a` 统一会话级语义核验的证据约束。模型回执含越界引用时，计划级和会话级均只写已登记引用，保留结构化缺证原因并采用宿主失败结论，不推进验收。29 项 SessionVerification、核验恢复/投影和交互核验测试通过。
- 代码 `97157726` 让真实故事在原发布任务已可交付后才发送冻结反馈，避免两次模型核验同时运行导致旧进度覆盖新用户选择；验收仍要求真实第二次委托、`verify_session` 与最终回复。TUI 类型与 11 项专项测试通过，最新完整实连待跑。受控排查确认原 TUI 可收到任务结束唤醒，未保留额外订阅试验。
- `74176e0a` 全仓构建、类型、架构/UI 与 Desktop IPC 检查通过。全仓测试仍遇并发下 Desktop 输入预测凭据 helper 超时；已在相同源码对完整 Desktop 套件限并发复跑，日志目录 `peer-adr118-desktop-controlled.vP5MEJ`，未修改生产凭据时限。

- 相同源码 `74176e0a` 限并发 Desktop 复跑结束。主段并发 4，6,210 通过、5 跳过、0 失败；尾段并发 2，9 项通过。其他包与工程门禁沿本轮记录。默认并发 `pnpm test` 的凭据 helper 超时仍保留为首次失败。
- 干净代码 `97157726` 的真实故事样本 `peer-interactive-live-F7vsCm` 两线均已结束。两线实际发布原任务，经规范输入冻结条件并建立第二次委托。Anthropic Messages 在 26 次实际请求时返回 `story_request_limit:bot`，OpenAI Chat 在 30 次时返回 `story_request_limit:worker`。两线均无最终规范交付，整案失败，原预算与成功判据沿用。

- 追查 `F7vsCm` 的 Anthropic 原始工具记录，前五次委托均因 criterion 描述为 713–763 字符被拒。输入均已有一个条目，宿主旧诊断只提示条目数量。代码 `cf952c80` 让投影 schema、验证及错误提示共用 500 字符限额，保留严格拒绝；Delegation Provider 27 项通过。
- 代码 `67733c27` 缩短两条真实样例的结构化 criterion，验收显式要求会话级已持久化通过 verdict 和可读、完整的任务文本计算值，避免计划级核验或不可用文本被计为成功。TUI 类型和原专项 11 项测试通过。干净源码两线复跑目录 `peer-interactive-live-csREZG`，整案终态待查。

- `csREZG` 的 Anthropic 首次委托已成功，原发布核验通过。后续自动核验虽取得四条规范回执，模型同时引用了未登记的引用，宿主按规则拒绝。主 Bot 曾在自动核验仍活跃时调用显式复核，随后在 32 次实际请求时以 `story_request_limit:worker` 结束，无最终交付。OpenAI 样本随后建立第二个后续委托，26 次实际请求时也以 `story_request_limit:worker` 结束，无最终交付。
- 代码 `47dc72e5` 让显式复核入口复用宿主的活跃核验事实。自动核验仍占用任务时，返回有 Tool Result 的等待状态，且不登记第二次复核或清除原占用。核验结束后可再调用。49 项复核、委托 Provider 和宿主事实测试通过。真实样本 `csREZG` 使用修复前源码。

- 代码 `09e37381` 将样例的 worker 单次冻结计算与独立 Verifier 四类检查分别写入委托契约，要求在核验活跃时等待。验收拒绝重复创建的后续任务，仍要求已持久化的会话 verdict 和最终结构化交付。Runtime Node 构建、TUI 类型及原专项 11 项通过。新源码两线复跑目录 `peer-interactive-live-Lb3Oh8`。
- 标准产品基线本轮逐图核对 7 张窗口材质图，涵盖宽窗工作现场和设置抽屉、浅色窄窗及减少透明度，原图哈希绑定至 review；实际透明度数值从机器记录核对。累计 42/255，整包 verify 待完成。

- 样本 `Lb3Oh8` 的 Anthropic 在 30 次实际请求后返回 `story_request_limit:verifier`。原发布任务有已持久化的显式通过 verdict，后续冻结任务无通过结论，未交付整案。OpenAI 在 32 次实际请求后同样耗尽 Verifier 额度。后续独立核验取得四条规范回执，但模型因看不到叶子写入的单独执行快照而报告缺证，宿主未判通过。
- 本轮逐图核对标准产品基线中的 8 张对话失败、重试和完全访问范围截图，核对重试入口、保留的历史、主输入框范围标记及子工作区返回入口，原图哈希绑定至 review。累计 50/255。

- 代码 `a30ebea9` 在既有核验事实消息中提供有界的宿主叶子状态及已记录引用计数，供 Verifier 判断保存状态。引用有效性和四类计算覆盖仍由独立检查回执确定。样例要求只有正式回复门禁明确要求时才对原发布补做显式复核。核验消息、核验通信和交互核验共 23 项通过，Runtime Node 构建与 TUI 类型检查通过。新实连目录 `peer-interactive-live-m978qa`。
- 标准产品基线新增核对 10 张诊断、外观、自动化列表、编辑和回执画面，涵盖深色宽窗及浅色窄窗，逐张绑定原图哈希。累计 60/255。

## 原生缩放与完整首版组件目录（ee029f64）

- Electron 专项 1 项通过，开发与生产实际 SDK 夹具覆盖首版 16 个组件和柱形、折线图。生产原生 150% 缩放及减少动效下，CSS 窄窗无横向溢出，中文输入保持焦点，折线图与配套表有可访问名称，表格可访问树可读取精确值。
- 实现者目检两个原生视口截图。控件图可见保存状态、输入焦点和完整控件宽度，SHA-256 `a876d689eb75cb281e7c2287ead6989a0f71951ff97e564bdce2b80f2641bc90`。图表图可见折线及对应 id 和 Cost 列，SHA-256 `cd0a3444d47c5c871a8734789152b4c8b1dd6a0d4f39792bec4715b4dae27913`。本轮覆盖 Electron 可访问树，系统读屏、系统 IME 和安装版仍待核验。

- 代码 `417fd8db` 用真实 Electron 挂载生产 `InteractiveResource`，仅在测试构建注入 SDK 内容渲染异常。专项通过，异常后显示明确标注未验证的固定摘要，保留程序入口并隐藏计算；模拟保存失败时保留草稿且不打开视图，重试在保存回执后调用打开端口。该用例使用受控保存和打开端口，实际独立窗口导航仍由其他原生用例覆盖。

## 固定版本后台卸载与性能初样（ad701997）

- 主工作区原生专项通过。在两个固定版本标签间切换，两侧各自保留已确认值和草稿，任一时刻只挂载一个 SDK 内容树，非选中标签保留但无 SDK 内容。仍需验证更多同时打开结果和隐藏期间的资源占用。
- 生产 Electron 组件专项通过。120 行合成数据及两张图表，八次 DOM 输入事件到预期结果首个可观察帧为 7.0–8.5 ms，含除零隐藏及恢复；观察区间没有 Long Tasks 条目。Renderer（Tab）结束快照 working set 为 215,088 KiB。CPU 瞬时读数全为 0，不能据此判断负载。记录位于本机 `peer-interactive-renderer-dbuq6r/production-interaction-sample.json`。该样本为自动化 DOM 输入和隔离开发机器测量，仍缺 500 行上限、持续负载 CPU、正式包体及完整真实故事成本。

- 代码 `cd43566c` 扩到 500 行上限，分别断言柱形图、折线图完整包含 500 点，并核对普通数据表的第二页在无关输入变化后仍留在该页。Electron 开发与生产同一专项通过。生产样本中 62 次 DOM 输入耗时 515.7 ms，首个可观察帧 3.6–14.8 ms，无 Long Tasks 条目；Tab CPU 累积用时增加 0.536 s，working set 从 233,744 增至 290,128 KiB。记录在本机 `peer-interactive-renderer-cKxr88/production-interaction-sample.json`。短窗口内的内存变化仍需长期/回收采样；正式包体与实际设备覆盖仍待验收。
- `m978qa` 的 OpenAI 样本完成原发布和后续冻结任务，后续计划与显式会话核验均通过，已持久化会话 verdict。最终回复之前曾被宿主以 `status_claim_mismatch` 拒绝，并返回两个任务的当前状态；完成显式复核后，下一次主 Bot 请求触及整案上限，32 次实际请求终止，其中主 Bot 15 次、worker 8 次、Verifier 9 次，无最终交付。同批 Anthropic 共 23 次请求，其中主 Bot 16 次达到角色上限，原发布已通过计划级核验，后续委托未创建。

- 代码 `c3873cd1` 将整案请求、角色请求和角色工具额度分开记账，持久化命中范围、资源、角色及计数。HTTP 门禁拒绝的尝试不计为已发请求，样本汇总保留已脱敏失败原因。TUI 类型及专项 12 项通过，新增超额工具批次被拒且未建立委托的真实隔离宿主用例。
- 标准产品基线新增核对 8 张经典对话、本地图灯箱、产物和差异预览，逐张绑定原图哈希。累计 68/255。

## CLI 独立安装验证（c3873cd1）

- 干净源码构建 macOS arm64 CLI 与凭据 helper，走仓库正式归档脚本，在临时路径解包。随后用本地 npm 包和 loopback 归档服务执行实际 postinstall，把同样的两个二进制装到临时 npm prefix，两份文件逐字节一致。未使用日常安装或发布远程包。
- 解包版和 npm 入口分别通过 1 项 CLI 集成测试，各含 16 条断言，覆盖 help/version、固定版本 JSON 与文本、未登记发布、越界 owner、终端控制字符及清理摘要。运行未提供 DISPLAY 或 WAYLAND_DISPLAY。解包版在仅系统 PATH 与隔离数据根的空环境下也通过 help/version；动态链接列表只有 macOS 系统库。
- CLI 二进制 73,602,736 B，归档 28,097,193 B，归档 SHA-256 `d44090c4e260f079942dbb73e56eb0446f699ceb994a33a9b44cd8d2bcdaeb6a`，日志在本机 `peer-adr118-cli-archive.lqEMsn`。覆盖 macOS arm64 的非交互入口。Linux、终端交互界面、安装版 Desktop 及其正式包体仍待核验。

## macOS Desktop 归档运行时（8718d193）

- Desktop 构建与 IPC 检查通过。第一次本地 macOS arm64 打包的旧归档门禁通过，但用包内 Electron 导入交互运行时时因 `interactive-content/src/limits.mjs` 被通用打包规则排除而失败。代码 `8718d193` 将该包的运行时 ESM 纳入归档，并检查四个公开运行时 export。新门禁对旧归档明确失败，对重打包归档通过。
- 重新打包后，在 Electron 41.7.1 的 Node 模式实际从 asar 导入模块，隔离 Worker 求值、禁用节点拒绝、SQLite 关闭后重开及原固定引用的文本读取均通过。工作目录 `peer-adr118-desktop-package.hmmbLQ`。临时 ad-hoc 包占用 396,800 KiB，asar 为 99,898,866 B，SHA-256 `a59ef98c3e0c5c5cd6efc1ef8a43e4eae3540dfb32514e6255181afaf8a6042c`。本次覆盖包内运行时，正式签名公证与已安装 GUI 仍待验收。
- 独立既有 `verify-verification-runtime.mjs` 的接管夹具缺少 `store.enableSupervision`，本轮执行在该断言前终止，保留原失败日志。已运行的交互归档探针使用隔离数据，日常 Desktop 进程仍在运行。

- 代码 `734346c5` 将接管探针换成包内真实 SessionSupervisor、GoalPlan、Conversation 和协调日志，受控 runner 只记录收到的执行意图。原包重跑四项全部通过，覆盖只修复格式时禁用工具、核验停滞、空闲核验结算，以及从暂停的 verify 意图交接到 execute；实际协调日志与计划均记录接管完成。源码同场景测试通过。日志 `peer-adr118-desktop-package.hmmbLQ/verification-runtime-updated.log`。仍为包内 Node 模式，未覆盖已安装 GUI。

## 旧写者竞态复核（8b75a66f）

- 用固定旧队列实现在 SQLite 清理提交前接管老化目录锁并实际写入。当前锁守卫检测到失效，清理返回 `interactive_retention_stale`，原正文和已保存参数仍可读，无清理回执，旧写入保留。两组测试共 27 项通过。该用例用受控根组合注入竞态，只证明最后一次检查前可观测的失效会回滚。最后检查至提交之间仍需要跨版本排他证明，生产清理入口继续关闭。
- 标准产品基线新增核对 8 张停止、结果待核实、取消和接手截图，覆盖宽窄窗及明暗主题，逐张绑定原图哈希。累计 76/255。

- `5a178ca6` 将已有生产 `wait_for_sessions` 补入真实故事的投影。仅背景唤醒且子任务仍推进时使用，当前用户输入仍经正式回复确认。原样本多次用复杂协调评估等待，出现失效 revision 和无效参数。该修改只修正验收驱动器的投影和样例文本，角色及总额度、证据和交付判据均沿用。TUI 类型及 12 项专项、24 项等待和连续性测试通过。新实连目录 `peer-interactive-live-7mrADw`。
- 标准产品基线新增核对 8 张活动、核验详情、快速对话和证据画面。快速对话透明原图用明暗背景辅助查看，review 绑定原图哈希。累计 84/255。

- 样本 `7mrADw` 的 OpenAI 在 32 次实际请求后触及整案请求额度，未完成显式通过 verdict 和最终交付。等待工具已真实投影，但模型未调用。核验多次对 evaluate 传入仅适用于 data 的 selector/bindingId，之后还有未准入读取导致拒绝。代码 `273f6588` 在既有模型可见 schema 字段与核验提醒说明 data、evaluate 和 publication 的适用范围，权限、请求归一化与证据门槛沿用。17 项核验测试通过；本批实连使用修改前源码。
- 标准产品基线新增核对 10 张历史与缺失依据、回复进行中、人工选择发送前后截图，逐张绑定原图哈希。累计 94/255。

## 全仓工程与产品采集基线（45102335）

- 干净代码 `45102335` 通过 `pnpm build`、全仓 `pnpm typecheck`、`pnpm architecture:check`、Desktop 正式 `ipc:check`、产品包工具 8 项测试及 TUI 835 项测试。Marketplace、Changelog、Upgrade 三个根测试套件也分别通过。
- 首次 `pnpm test` 在 Runtime Node 的并发输入抢占断言失败，导致下游 Desktop/TUI 和三个根测试套件未执行。用 Node 25 单独重跑原文件，9 项全部通过；保留首次失败，后续分别补跑未执行的套件。工程日志位于本机临时目录 `peer-adr118-engineering.Z5MTSu`。
- 独立 Desktop 首段执行 6,214 项，6,205 通过、5 跳过、4 失败，尾段未启动。失败分别来自旧设置默认值断言和未接入交互条件注册表的原生关闭测试夹具。代码 `5a356cf6` 修复两份测试夹具，并新增导航落盘期间有新交互条件时阻断关闭的用例；两文件在独立检出运行 15 项全部通过。Desktop 尾段在临时检出试跑时受到构建目录和 Vite 根目录的跨工作树链接限制，正式工作树仍需重跑全套。
- 标准产品回归对同一源码启动隔离 Electron 采集，输出位于本机 `peer-adr118-product.A4UhGM/packet`。采集已产生 runId `fc8dddeb-d0f1-41f9-b738-35ec1a89218a` 和 255 张必查图，状态 awaiting-ai-review。目前 199 张已逐图核对并写入该包的 `review.json`，其余标记 not_checked；verify 待审查完整后执行。原始采集源码已在独立检出复现相同指纹，正式实现工作树已快进至 `15878144` 并启动新一轮全仓检查。此次工程检查不证明完整真实任务故事或安装版回归。

- 干净代码 `273f6588` 再次通过全仓 `pnpm build`、`pnpm typecheck`、`pnpm architecture:check` 与 Desktop `ipc:check`，日志 `peer-adr118-current-engineering.LGtSFi`。同提交的 `pnpm test` 整体退出 0。TUI 841 项通过；Desktop 主段 6,210 通过、5 跳过，尾段 9 项通过。根 Marketplace、Changelog 与升级矩阵均运行成功。
- 标准产品基线新增逐图核对 8 张更新最小化与任务报告加载、缺失、陈旧状态截图，绑定原图哈希。累计 102/255，整包 verify 待完成。

- 样本 `7mrADw` 的 Anthropic 在首个请求遇到 socket 中断，未进入委托。干净代码 `273f6588` 已按原预算启动两线实连复跑，目录 `peer-interactive-live-cbTDSZ`，结果待核对。
- 标准产品基线新增核对 8 张流式回复进度和结束态、任务说明、追问草稿及人工问题画面，逐张绑定原图哈希。累计 110/255。

- `cbTDSZ` 的 Anthropic 完成原发布与冻结后续任务，两个计划的独立核验均通过。显式会话复核取得四类规范回执，同时引用了任务索引外的引用，宿主保存失败 verdict。主 Bot 三次在用户回合调用等待工具，宿主按背景唤醒约束拒绝。32 次实际请求触及整案上限，无最终交付。OpenAI 同批样本在 31 次请求后触及主 Bot 角色上限（16 次），两个计划均通过独立核验，未持久化显式会话 verdict，也未最终交付。
- 标准产品基线新增核对 8 张任务详情截图，涵盖运行、等待跟进、签收和失败，以及四组宽窄窗明暗视图。运行中摘要显示 Markdown 源标记，状态和主要操作仍可辨，已记录于该图观察。累计 118/255。

- `57ae67fa` 收紧真实故事的验收关联。只核对最后一次显式会话复核实际引用的固定检查回执；最终回复须由该次复核结束后产生、锚定冻结用户输入且通过正式回复持久化。较早的进度消息、降级回复和计划级核验回执不能混入成功证据。TUI 类型与既有 12 项专项通过，完整实连通过样本仍缺。

- ADR `c3a4bb9` 和代码 `fedec053` 把已有等待资格接进 Desktop/TUI 的 Runtime Projection。用户回合不会向模型提供等待工具；有 workId、有事件且无当前用户锚点的后台唤醒才可见，Provider 仍检查实际任务推进与归属。Runtime Node 构建、TUI 类型、34 项 Provider 适配、4 项等待及 23 项 Desktop 模式/恢复测试通过。新实连样本 `peer-interactive-live-sQsz1j`。

- 标准产品基线新增逐图核对 16 张运行与等待、Bot 概况和记忆、过程详情、取消失败及成功、长错误、工作现场不可用与并行任务截图，绑定原图哈希。累计 134/255，尚未执行整包 verify。

- `sQsz1j` 两线终态均已核对。OpenAI 两个计划均通过，30 次实际请求时触及主 Bot 角色上限 16 次，无显式复核 verdict 或最终交付。Anthropic 完成后续计划及显式会话复核，并持久化通过 verdict；下一次主 Bot 请求触及 32 次整案上限，原发布确认回复之外未发出最终回复。用户回合的等待工具隔离已从 OpenAI 实际请求确认。
- 标准产品基线新增逐图核对 12 张备用视觉模型、服务商、Composer 空态/多行/附件及回复截图，绑定原图哈希。累计 146/255。

- ADR `d963275` 与代码 `b2255861` 让显式复核在 verdict 落盘并释放占用后附上实际 sessionState。回复仍按实时任务状态重新核对，读取失败保留既有 verdict。Runtime Node 构建及 42 项 Provider、复核与完成门禁测试通过，实际宿主通过/失败两种复核均核对了状态及 revision。两线实连目录 `peer-interactive-live-lgwO8R`。

- 代码 `66e78230` 在复核后的可选状态读取中复核调用工作区。读取失败或返回其他工作区的任务时省略 sessionState，已记录的 verdict 仍可返回。30 项 Provider 与复核表面测试通过，新增两种状态缺失路径。
- `lgwO8R` 的 Anthropic 共 30 次请求，触及主 Bot 角色额度，无显式会话 verdict 与最终交付。OpenAI 同批样本在会话级核验阶段用完 32 次整案请求，未产生通过 verdict 或最终交付；该批使用 `b2255861`，未取得成功返回 sessionState 的真实模型样本。
- 标准产品基线新增逐图核对 10 张引用、发送后状态、问题待答与结束、Bot 消息配色截图，绑定原图哈希。累计 156/255。

- 标准产品基线新增逐图核对 12 张 Bot 消息配色、引用发送与长回复、选区引用和草稿连续性画面，绑定原图哈希。累计 168/255。

- `52120424` 将独立 `verify` 专项接到实际 TUI ToolHost、委托 Provider 和 SessionSupervisor。驱动器显式调用复核工具，模型执行实际独立检查；通过要求 Grant、固定检查回执、持久化 verdict 与释放复核占用后的 sessionState 一致。TUI 类型及 12 项专项通过。两种真实模型编码的专项均通过，目录 `peer-interactive-live-9IMJD3`。该专项仍由驱动器构造会话和发起复核，完整 Bot 任务故事另验。

- `9IMJD3` 中 Anthropic Messages 与 OpenAI Chat 各 4 次实际 HTTP 请求（worker 2、Verifier 2），均取得 program、facts、初始 evaluate 与冻结 evaluate 四条未截断回执。委托工具返回持久化通过 verdict、`result_ready` 与两个 revision。输入 / 输出 / 缓存读取 token 分别为 8,270 / 2,801 / 23,936 和 17,960 / 3,009 / 14,336，账单金额未取得。
- 标准产品基线新增逐图核对 8 张待确认报告、图片授权等待、完全访问及已授权回执画面，逐张绑定原图哈希。累计 176/255。

- 标准产品基线新增逐图核对 12 张图片拒绝、取消、停止、过期、独立授权、回复过程空态、对话正文和授权历史画面，逐张核对原图哈希。累计 188/255。

- 标准产品基线再确认 7 张窄窗正文与授权历史、回复时长、宽窗预算耗尽和手动唤醒画面，累计 195/255。另已检查的浅色窄窗预算截图没有拍到预算提示与计数，保留 not_checked 并记录重采原因；脚本对 DOM 的断言无法替代该截图。

- 标准产品基线新增确认 4 张深浅色缺恢复记录与自动续接画面，累计 199/255。
- 干净源码 `52120424` 两个真实 Provider 复跑完整故事，报告目录 `peer-interactive-live-p5OQCK`。两路均完成发布及冻结，最终回复验收均未通过。Anthropic 用完 32 次总请求（Bot 16、worker 9、Verifier 7），两工作会话为 `result_ready`，最后一次 Bot 请求连接关闭；OpenAI 用 29 次（Bot 16、worker 8、Verifier 5），达到 Bot 角色上限时复核工作仍为 `verifying`。早期回复、检查工具调用或 `result_ready` 不作为主 Bot 引用持久化通过复核的最终交付证据。

- `a290a86c` 修复预算截图脚本。首次重采在新可见性断言中复现虚拟消息挂载却越出视口，第二次在打开详情前用实际滚轮定位并核对可见边界。隔离 Electron 已生成两张截图并逐图确认宽窄窗均显示预算耗尽、256/256 与限制来源。标准包 `peer-adr118-product-recapture.xBTxQP` 仍在采集，旧包保留原审阅结论。采集以相同文件字节启动于提交前，最终以 sourceFingerprint 核对。
- 从 `p5OQCK` 的持久 Bot 回合进一步确认两路均遭遇 `status_claim_mismatch` 及 `verifier_in_progress`。Anthropic 在独立核验已运行之后发起显式复核，得到持久化 failed verdict。OpenAI 的早期 `post_reply` 工具回执虽有成功项，保留的对话中未出现可供验收的 canonical 最终回复。这些证据把下一步定位到用户回合续接、复核职责和交付收敛，不能只按请求上限解释。

- `d068d7bc` 修复 TUI 执行器将成功的 `project_agent_wait` 终止回执标记为错误的问题。新增回归先在原执行器复现：能力 Grant 与等待回执均成立，执行器仍返回 ok=false。修复后保留单次请求和真实工具回执，完成后台回合且不发可见回复。执行器 19 项和 TUI 类型检查通过。为保全正在采集的产品源码指纹，本次在独立 checkout 实施和测试后推送至同一实现分支。

- `d0d87100` 修复共享 runner 的后台唤醒收尾。旧实现将之前被拒的进度回复覆盖在随后获准的等待上，错误生成不可用卡片。回归在旧实现观察到宿主校验失败卡，修复后保留两条工具事实，记录静默等待且重启不轮询，随后结果事件仍触发实际交付。Runtime 的连续性、等待、回复收尾与失败投影共 38 项通过。
- 在干净源码 `d068d7bc` 复跑 OpenAI 完整故事，目录 `peer-interactive-live-CQqjT7`。发布和冻结完成；31 次请求中 Bot 16、worker 10、Verifier 5，达到 Bot 角色上限。没有请求获得等待工具投影，且协调日志没有 canonical 回复交付记录；成功的早期 `post_reply` 工具回执仍停在用户回合。该结果继续指向用户回合的意图决议与交付路径，无法证明后台等待修复足以完成故事。

- 标准重采包 `peer-adr118-product-recapture.xBTxQP/packet` 已完成全部自动采集，runId `fe909d4d-3ffc-4721-b783-b97ba41c3b45`，255 张，awaiting-ai-review。文件指纹 `6e8f500b9feef0ea42a0fd0628b21861de80387b18b7eba9165e7d67ce7b4c04` 与 `a290a86c` 独立 checkout 一致。实现者已确认 56 张，其中 42 张经同 ID 与原图 SHA-256 核对，字节完全相同，复用旧包的逐图记录；另 14 张为本次目视核对。新包尚未完成审阅或 verify，后续实现提交另验。
- `CQqjT7` 的持久会话显示前置发布用户回合中的成功 `post_reply` 后以 `work_disposition_required` 终止，协调日志无交付记录。旧故事驱动可在索引和任务准备好后立即发出冻结输入，而首个用户可见结果仍可能缺席。`aced60e0` 令真实故事先要求带已就绪会话状态和固定产物引用的 canonical 首次交付，再编辑并提交冻结条件；同时明确首个回复须先按现有协调契约提交当前决议。未扩大请求上限，TUI 类型和 12 项现有专项通过。

- 标准重采包新增逐图确认 13 张窄窗恢复、启动及宽窄窗四种核验结论与主对话画面，逐张匹配包内 SHA-256。累计 69/255。
- `aced60e0` 的 OpenAI 故事 `peer-interactive-live-cStvos` 已发布并进入首次交付，28 次请求（Bot 16、worker 4、Verifier 8）达到 Bot 角色上限。未收到 canonical 首次交付，驱动按用户路径保留冻结输入。持久回合中多次 assess 把字段放在顶层，另一次嵌套对象缺 `assessment.reason`。`4f3f770f` 在共享工具说明、schema 和结构化拒绝中明确层级及缺字段路径，保持原输入校验和宿主权威。49 项协调、委托与角色投影测试通过；更新后在原请求预算下启动 OpenAI 复跑。

- 重采包又审阅 12 张窗口材质、会话失败恢复和子会话图，9 张通过，累计 78/255。三张宽窗深色图的回到最新按钮遮挡回复末尾，保留 not_checked 与逐图描述；涉及设置抽屉、玻璃材质和实色材质。
- 干净源码 `4f3f770f` 的 OpenAI 故事 `peer-interactive-live-S29RTH` 成功提交 assess，首条 canonical 进度回复引用 running 会话。发布任务之后达到独立计划核验通过并按现有 policy 签收，进度回复未交付固定结果。两个背景唤醒均产生空工具输出后以 `work_disposition_required` 结束。共 15 次请求（Bot 8、worker 4、Verifier 3），用例到时仍在首次交付。修复 `b94f971e` 对齐已准入的 System Context Source 和唤醒提醒，区分结构化等待、可结束的无责任唤醒及须处理的结果事件。38 项上下文、唤醒和连续性测试通过，OpenAI 已按原限额复跑。

- `b94f971e` 的 OpenAI 故事 `peer-interactive-live-NDYoxf` 完成结果发布，26 次请求（Bot 16、worker 4、Verifier 6）到达 Bot 限额，仍在首次交付。前两次等待分别使用来源版本和查询返回的观察版本，均被宿主判定 `wait_source_stale`；随后 continue 决议通过，但结果就绪后的两次协调输入未通过。尚未提交冻结条件。等待拒绝当前只给错误码，需核对当时可披露的版本和状态回执。
- `80d64c94` 将 Desktop 回到最新按钮放在阅读视口下方的普通布局中，保留原滚动控制、按钮语义与 SVG。针对重采发现的三张覆盖问题加入实际几何断言，新标准包 `peer-adr118-product-latest.DuoG3A` 采集中。该包以提交前相同文件字节启动。

- `c33c6e0b` 让 `wait_source_stale` 通过原 Tool Result 回传本目标可见的会话状态、来源版本和观察版本。提示区分仍可等待时的版本刷新与任务已离开等待状态。不存在、非当前 mandate 或引用越权的会话不回传事实；拒绝也不写决议。47 项协调、委托与等待测试通过；保留 Desktop 采集源码，在独立 checkout 对同分支运行原限额 OpenAI 故事。

- `80d64c94` 的隔离 Desktop 主采集机器报告成功，包含回到最新与阅读区不相交的断言。逐图确认 4 张新材质截图，包括原三张问题图，按钮均在视口之外；原图 SHA-256 已记录，等待标准包完成后绑定审阅。
- `c33c6e0b` OpenAI 故事 `peer-interactive-live-rIQOtT` 共 17 次请求（Bot 9、worker 4、Verifier 4），完成发布并产生 canonical 进度回复，发布任务后来由 policy 签收。三个唤醒无实际工具调用并以 `work_disposition_required` 结束，首次正式交付到时。该样本未触发 stale wait，不能作为新回执真实使用证据。
- `e1b9c40e` 补齐 TUI 的计划提醒接线。原实际 Provider 请求复现缺少计划生成的唤醒提醒；Desktop 已沿现有 Runtime Reminder Source 转发，TUI 现在沿同一 Source 转发并保留显式提醒。TUI 类型检查及执行器和 live 专项合计 31 项通过。两种实际 Provider 已按原限额启动故事复跑。

- `80d64c94` 标准重采已完成全部机器场景，runId `db2c5605-1171-4437-917b-2a494b67d9e3`，255 张，awaiting-ai-review。源码指纹 `82968b9600b106f8b1276a7e3bce8c27da5040df5684746787291f0ada578f52` 与独立检出一致。当前自审 55/255，41 张与前两包已审阅图同 ID 且 SHA-256 相同，另 14 张逐图核对，含回到最新的原三张问题画面和十张恢复画面。
- `e1b9c40e` 两个实际 Provider 故事 `peer-interactive-live-Dcjeed` 均完成发布，均在首次正式交付达到 Bot 角色上限（每路 23 次，Bot 16、worker 4、Verifier 3）。OpenAI 实际获取 `wait_source_stale` 的 `result_ready`、来源版本与观察版本；最后两次 assess 参数在 assessment 字段开始处截断，Provider 计量两次均为 1800 输出 token。未提交冻结条件。
- `fadda300` 只把完整故事驱动的 Bot 单请求输出上限从 1800 调到 3200，以容纳完整协调决议。整案仍最多 32 次请求，Bot 仍最多 16 次，单次/整案仍 45/240 秒，worker 和 Verifier 保留 1800。TUI 依赖构建、类型及 12 项专项通过，已启动 OpenAI 单路复跑。

- `80d64c94` 标准包新增 12 张逐图核对，含浅色启动、宽窄窗各类核验结论和减少透明度场景。逐图核对包内 SHA-256，累计 67/255。
- `fadda300` 的 OpenAI 故事 `peer-interactive-live-UU6KKO` 共 25 次实际请求（Bot 16、worker 4、Verifier 5），已发布并取得显式复核回执，首次交付前达到 Bot 限额。该轮拿到完整 assess 参数，宿主拒绝把尚未发布的回复标记为已覆盖且证据为空的条目。`1c2a72b0` 在共享协调提示和无证据拒绝回执中区分既有工作证据与当前 return 预留，保留全部准入条件。43 项委托与意图生命周期测试通过，已启动新实测。

- `80d64c94` 标准包再核对 8 张玻璃材质、会话失败/恢复、访问策略、子会话和诊断，逐张匹配包内 SHA-256，累计 75/255。
- `1c2a72b0` OpenAI 故事 `peer-interactive-live-fmkkvJ` 完成发布，23 次请求（Bot 16、worker 4、Verifier 3）达到 Bot 限额，首次正式交付未发生。return 使用第一执行切片的回复引用，后来切片被宿主按 `reply_reference_out_of_scope` 拒绝。`39ab7e49` 在现有 L7 决策帧随每一执行切片投影其当前引用，工具 query 复用同一字段。旧引用仍按原条件拒绝。52 项协调、委托和上下文测试通过，OpenAI 已启动复跑。

- `80d64c94` 标准包新增 8 张诊断、自动化列表/编辑/回执及经典对话画面，逐图匹配 SHA-256，累计 83/255。
- `39ab7e49` OpenAI 故事 `peer-interactive-live-2Voulr` 再次完成发布，23 次请求触及 Bot 16 次上限，首交付未发生。持久记录中连续三个 return 调用引用前一切片的具体预留，均按原规则拒绝。ADR `4456d44` 与实现 `4bcb31ce` 增加 `current_turn_reply`，由宿主将输入绑定到当前切片，持久化仍只保存具体引用。实际运行路径测试覆盖旧具体引用拒绝、字面量获准、核验及最终交付，56 项相关测试通过。OpenAI 已在原整案预算下复跑。

- `80d64c94` 标准包新增 8 张经典对话、深浅图片预览和协调状态画面，逐图匹配 SHA-256，累计 91/255。
- `4bcb31ce` OpenAI 样本 `peer-interactive-live-NVbU9h` 在真实回合使用 `current_turn_reply` 并有一次获准 return；根核验返回 `goal_coverage_incomplete`，不是引用过期。样本最终以 25 次请求（Bot 16、worker 4、Verifier 5）达到 Bot 限额，未完成首次交付。持久输入有覆盖项缺 sources，且把下一条用户消息的预算选择列入当前任务 openQuestions。`80751f26` 明确拒绝回执的覆盖字段路径，并将初始合成任务明确限定为交付独立核验过的示例，预算选择仅在后续显式输入中出现。保留两阶段验收，Runtime 构建、TUI 类型和 55 项相关测试通过，OpenAI 已启动复跑。

- `80d64c94` 标准包逐图核对 8 张窄窗协调、宽窄窗 Agent 活动与核验详情、回复依据图。逐张匹配 SHA-256，累计 99/255。
- `80751f26` OpenAI 故事 `peer-interactive-live-XW0fgr` 发布并取得独立会话核验通过；已准入的 return 根核验仍因模型保留了一个待交付的实质要求而返回 `goal_coverage_incomplete`。本轮 openQuestions 已为空。后续删除该要求的尝试被原解释修订规则拒绝，最终在首次交付前用尽 Bot 16 次（合计 25 次）。`b679c57d` 在真实故事输入中明确实质证据覆盖与规范交付的分工，验收继续要求两次真实规范交付和实际冻结输入。TUI 类型与 12 项专项通过；OpenAI 按原限额复跑。

- `80d64c94` 标准包再逐图核对 8 张待回复、历史、历史预览及选项发送画面，逐张匹配 SHA-256，累计 107/255。
- `b679c57d` OpenAI 故事 `peer-interactive-live-7yV2Ha` 完成发布并发起真实会话复核。首次正式交付前主 Bot 耗尽 16 次，整案 26 次（worker 4、Verifier 6）。已保存初次 assess，后续提交重新写了既有 interpretation，被 `intent_revision_required` 拒绝。`3eb270e9` 保留修订保护，在 Tool Result、schema 与工具提示明确同目标更新应省略 interpretation、沿用已保存的 requirementId；测试核对拒绝不推进 revision。43 项生命周期与委托测试通过，OpenAI 已启动按原限额复跑。

- `80d64c94` 标准包逐图确认 8 张选项提交、更新收起及任务报告加载画面，逐张匹配 SHA-256，累计 115/255。
- `3eb270e9` OpenAI 样本 `peer-interactive-live-ECqvMU` 首次经根核验、return 和实际 `post_reply` 完成首个固定产物交付。规范对话包含原输入锚、实际会话状态、固定引用及绑定决议。随后驱动确认保存并冻结 80，通过输入队列追加第二条规范消息。交付前积累的四个旧结果/报告/核验事件紧接着触发一次唤醒，模型两次空工具输出后以 `work_disposition_required` 结束。冻结输入进入回合时 Bot 的 16 次额度已耗尽，尚无第二工作或最终回复。整案为 26 次（worker 4、Verifier 6）。应核对已交付覆盖和剩余事件责任后再调整调度，不能从已发布推断已交付。
- 已在干净 `3eb270e9` 启动全仓构建、类型、架构、Desktop IPC 及测试串行工程复跑，目录 `peer-adr118-engineering-3eb270e9.gVTAk4`。结果待完成。

- `3eb270e9` 全仓构建、类型、架构和 Desktop IPC 通过。全仓测试在 runtime-node 的前台抢占用例失败，150ms 后检查时尚未到达前台，错误对象随后已观察到该输入。相同用例隔离复跑通过。修复 `67548984` 保持后台响应阻塞，等待真实前台同步完成，5 秒仅作死锁看门狗；9 项 runtime-host 测试通过，最新全仓测试已重新启动。
- `67548984` 同时修正完整故事驱动的冻结提交唤醒。真实 TUI 输入提交会在后台唤醒期间调用宿主 tick；旧驱动只依赖自动轮询且串行去重，令新输入在旧唤醒结束后才进入调度。冻结输入现在走原输入队列并立即触发同一个宿主 tick，原前台抢占、挂起操作保护和正式交付验收沿用。TUI 类型和 12 项专项通过，OpenAI 在隔离检出按原限额复跑。

- `67548984` 的全仓 `pnpm test` 退出 0。Runtime Node 1,918 通过，TUI 843 项，Desktop 主段 6,210 通过与 5 跳过、尾段 9 通过，根项目附加套件完成。此证据绑定该提交；后续 UI 变更由新采集验证。
- 同提交 OpenAI 故事 `peer-interactive-live-qfbnvn` 发布后仍在首次交付触及 Bot 16 次上限，整案 24 次（worker 4、Verifier 4），未到冻结提交，无法据此确认前台抢占改动的真实模型结果。
- `80d64c94` 标准包审阅任务报告和流式回复等 8 张，7 张通过，累计 122/255。另在 `task-main-note.png` 确认工作现场默认展示原始状态和内部模型 ID，保留待修。实现 `8907cb5e` 使工作摘要采用已有本地化状态、移除默认行的模型 ID，保留详情诊断；回归脚本在原场景新增断言，隔离标准包 `peer-adr118-product-work-row.vK5tP5` 已启动。

- 复查 `peer-interactive-live-qfbnvn` 的根核验拒绝时，会话版本仍为当前版本，覆盖声明混入了未登记在该任务证据索引中的 Bot 查询回执。`1bf74f5a` 保持原拒绝条件，在原 Tool Result 中按需求和会话返回版本变更或引用未登记两类原因，最多 16 条，不公开索引与被拒绝引用。44 项生命周期和委托用例通过；真实 OpenAI 故事 `peer-interactive-live-UJEe7H` 在干净提交上按原限额复跑，结果待核对。

- `1bf74f5a` 真实 OpenAI 故事 `peer-interactive-live-UJEe7H` 完成发布，首次交付前用尽 Verifier 10 次（整案 26 次，Bot 12、worker 4）。请求记录显示自动会话核验完成一轮工具读取，Bot 又显式请求会话核验，随后根核验再次读取；样本没有进入冻结提交。下一步按会话核验与根核验分别追查当前版本结论的复用和重复读取，保留原成本限额。
- 在 `8907cb5e` 隔离标准采集的原图中复查 `task-main-note.png`，工作现场行显示本地化的“状态暂不可用”，没有内部模型标识，核查未通过的回复正文及独立展开入口可见。已保存原图 SHA-256 对应观察，待标准包完成后核对并登记，未作为整包通过。

- `a6cceb12` 明确会话核验工具的调度指引：存在活动核验时等待，当前宿主结论已覆盖所需检查时引用其索引证据，缺检查、来源变化或用户明确要求时可显式重查。保留原宿主准入、独立核验、重查与根核验职责。29 项委托工具测试通过，真实样本 `peer-interactive-live-nHg6rc` 在干净提交上按原限额复跑。
- `8907cb5e` 标准包 Bot Shell 机器采集已返回通过。另逐图核对跟进草稿和宽暗/窄亮任务详情 3 张，原图 SHA 已记录；主对话追问选项轮廓待核对终态。余下标准采集与整包审阅继续。

- `a6cceb12` 的真实 OpenAI 样本 `peer-interactive-live-nHg6rc` 完成发布与自动核验，宿主会话为 accepted；共 15 次请求（Bot 8、worker 4、Verifier 3），未再次调用显式会话核验。唯一公开回复是执行中的进度说明，未携带固定产物引用，首次正式交付阶段以 AbortError 结束，未触及角色请求上限。驱动继续要求正式交付后才能冻结。测试提交 `1c026db6` 明确执行期间等待和完成后交付，移除后续输入无条件要求重复会话核验的旧测试指令，仍要求全部固定结果及检查回执。TUI 类型及 12 项专项通过，按原限额复跑。
- `8907cb5e` Electron 标准包机器采集退出 0，runId 为 `c19e4b30-bb8a-415c-8843-6d80d5eb92b6`。新包 `review.json` 已按截图名与 SHA-256 导入 38 张与旧包逐字节一致的已核对截图，登记本轮实际审查的 8 张通过，合计 46/255。其余 209 张待核对，包括主对话追问选项的疑似裁切；审阅由实现者自审，整包 verify 尚未达到执行条件。

- `1c026db6` OpenAI 样本 `peer-interactive-live-gTrHhQ` 完成固定发布，首次正式交付前用尽 Verifier 10 次，整案 26 次。Bot 查询结论后仍提交同范围显式核验，根核验随后再次读取，未进入冻结；已有复用指引尚未保证本样本收敛。未调整验收条件或限额。
- 标准包再审 8 张，6 张登记通过，合计 52/255。深浅两张修复态的详情状态使用弱化颜色，保留待重采。`ca9c0705` 让“由主 Bot 跟进”沿用其他重要任务状态的主文字 token 与字重，并在原深浅场景加入 computed style 断言。修复已推送，Electron 工作现场专项隔离运行。

- `ca9c0705` Electron 工作现场专项退出 0，无页面或宿主授权错误。两张实采修复态由实现者逐图确认，宽暗 `afbcac71…`、窄亮 `947af5e3…`，跟进状态可辨认，任务详情、取消和原证据入口保留。此为独立专项，旧标准包不沿用新图的通过结果。
- `peer-interactive-live-gTrHhQ` 的持久 Tool Result 证实：Bot 查询核验细节时，只看到 `partial` 且没有已完成的核验记录；下一次会话查询仍是 `verifying`。随后显式核验启动并通过，原计划里也保留两次通过记录。`13b1b681` 让核验详情从同一宿主活动状态额外投影 `verificationInProgress`，让调用者区分进行中和当前已存证据结论。核验的授权、判断、持久化与验收条件不变；31 项委托/核验专项通过。按原限额启动新的真实故事。

- `13b1b681` 真实故事完成自动核验且 Bot 未发起显式重复核验；首次正式交付前用尽 Bot 16 次，整案 27 次。持久 Tool Result 记录 `input_disposition_required` 与 `source_not_admitted`，模型在后台事件回合重复给历史输入附加处置。`57e697ea` 在原拒绝中返回当前可用来源，明确事件回合不重复处置历史输入；拒绝仍不写入决议。`db4576ac` 在真实协调夹具验证两类拒绝不推进 revision，修正后原交付及延迟结算仍通过。23 项相关用例和新增断言通过，按原限额复跑。
- 旧标准包注意事项四张审查通过，累计 56/255。追问选项原图确认焦点轮廓在裁切容器边缘消失。`71e9d841` 将原 2px 焦点线内收，Electron 任务详情专项退出 0，无页面或授权错误；新图 `77c28b99…` 的选项四周完整可见，定位仍未触发回答或继续执行。此为实现者自审的独立专项，旧标准包不沿用新图的通过结果。

- `db4576ac` 的 OpenAI 故事 `peer-interactive-live-vDbNUR` 取得首次固定结果正式交付，确认保存并冻结 Budget 80，经原队列进入第二条规范输入。Bot 创建第二个只读工作，实际以同一固定版本和 `story-freeze` 读取冻结求值并更新任务。原会话为 accepted，后续会话为 result_ready；整案 32 次耗尽（Bot 16、worker 9、Verifier 7），未取得第二次正式交付。记录显示后续 worker 读取了额外的 program、data 和初始条件。保持相同验收和限额，用已配置 Anthropic encoder 在同源码另跑一案。
- 旧标准包授权、用户回执和预算列表再逐图审查 4 张，累计 60/255。包含跟进状态可读性和追问焦点修复的干净 `db4576ac` 已在独立源码目录启动标准采集，输出 `peer-adr118-product-focus.VUS6Y2/packet`，原包结果独立保留。

- 同源码 Anthropic encoder 的真实故事完成发布，首次正式交付前耗尽 Bot 16 次，整案 28 次（worker 4、Verifier 8），后续冻结任务未进入。标准 Electron 新采集仍在运行。
- ADR `043b7b6` 与实现 `8163323d` 区分原调用重放和新候选修复。校验失败且准备记录已确认结清时，由原 SQLite 候选事务返回剩余修复次数；实际修复仍须通过同一存储准入。重放、待对账或未证实的状态不出具新的修复额度提示。Node 与 Bun 各 25 项 Provider、准备记录与 Worker 测试通过。旧代码中 `unsupported_node` 的反馈缺口由此收口。

- `5954dc37` 补发布准备的故障收口。原尝试结清失败、读取不到确认或已有 prepared 时返回 `publication_unknown` 与原调用引用；重放不重新申请授权或执行。另一个存储连接也不能以相同参数重复取得准备权。用实际 SQLite 与故障注入核对零 Evidence、原调用可只读检查且无修复提示，Node/Bun 各 26 项通过。未提交的遗留 prepared 项仍需要有可核对的原执行已结束证明，不能凭超时释放。
- 新标准包的 Bot Shell 主采集在干净 `db4576ac` 返回通过。已逐张查看新包原图里的暗色追问焦点、宽暗和窄亮两种 Bot 跟进状态，绑定三张原图 SHA-256。其余采集仍在运行，待包生成后按校验值登记。

- ADR `21b085d` 与实现 `cd6e0af5` 收口已提交却遗留 prepared 的窗口。新建和同内容修订都在原 SQLite 提交里写操作回执并结清准备，候选计数或活动指针异常会使同一事务回滚。旧已提交记录保留原对账路径。故障注入在事务退出、返回响应前核对准备已 committed，随后按原引用对账；Node/Bun 各 30 项通过。纯准备且未提交的恢复仍需对原执行终止的权威证明。

- `db4576ac` 标准采集退出 0，runId `1ebe921d-aaf5-4ba2-a373-cd107ef72dbf`。审阅文件实际登记 40/255 张通过，含 37 张与旧审阅逐字节一致的原图及三张本轮逐图复核的修复场景。剩余 215 张仍未核对，整包等待审阅。

- `7598dc68` 增加正式提交前中断回归：原 SQLite 事务同时撤回操作回执和成功结清，返回后可确认失败，零 Evidence，下一合法调用可发布。Node/Bun 各 31 项通过。
- `db4576ac` 标准包新增审阅六张生命周期画面，四张详情通过，累计 44/255。宽暗与窄亮的预算列表状态使用弱化文字，留待修复后重采。`15f800f3` 将“需要你”分组的状态改用原主文字 token，并加入深浅主题的列表断言，隔离 Electron 生命周期专项已启动。

- `15f800f3` Electron 生命周期专项通过深浅主题的预算、追问列表和详情四组，无页面或宿主授权错误。逐图查看宽暗 `abe22ef0…` 和窄亮 `57042b4a…` 两张预算列表，状态可辨认。单独保存证据，旧标准包不复用新图结论。干净 `15f800f3` 已启动全仓工程复跑。
- 已在 ADR §13.3 明确未提交准备的终止证明与 SQLite 结清边界。已有 session-control 回执区分物理停止与未明调用，恢复可复用其同执行证明，不能把计划终态或协调回执本身当作发布结果。实现及并发验证待接线。

- `bcd4941a` 增加结果库的停止恢复事务。只有原准备仍在、原操作不存在且宿主证明回调返回真，才记录中断并释放候选，不扣内容修复额度。两个 SQLite 连接实测无证拒绝、可核对证明后结清、重复请求幂等以及原内容修复额度完整保留。Node/Bun 各 31 项通过。Desktop/TUI 仍待把实际 session-control 停止回执接到该入口。
- 此轮工程复跑绑定此前 `15f800f3`，Runtime Node 1,921 项通过，其余宿主和根项目测试仍在运行。恢复存储提交的验收另以本轮专项记录为准。

- `795d198e` 接通 Desktop/TUI 已用的共享 workspace 恢复入口。按 Bot owner 分页读取原准备，只消费当前协调日志中与计划、会话和执行代际一致的停止回执，事务内重核；lease 丢失、只有计划终态、回执代际不符均不结清。Node/Bun 各 32 项测试、Runtime Node 构建与 TUI 类型通过。专项使用真实 SQLite 与受控协调日志读端，仍待覆盖两宿主真实停机/重启以及已换执行代际后的旧回执恢复。
- `15f800f3` 全仓工程复跑退出 0，构建、类型、架构、测试与 Desktop IPC 均通过。Runtime Node 1,921、TUI 843、Desktop 主段 6,210 通过与 5 跳过，尾段 9 通过，根附加套件完成。该结果绑定当时源码，新增恢复接线使用本轮专项证据。

- `8dfaf50f` 将共享恢复专项改用实际 v2 协调日志。真实写入 recorded → draining → settled 停止回执，关闭并重开协调日志与 SQLite，再经 `recoverWorkspace` 验证无停止证明、代际变化、lease 失效均不结清，恢复原代际与 lease 后只结清一次。Node/Bun 各 2 项通过。此次覆盖共享入口和真实存储重开，桌面与终端的进程级复跑仍需单列。
- `db4576ac` 标准包逐图复核任务说明、跟进草稿、追问详情和核验中状态，三张新增通过，一张复核已登记。按原图校验值累计 47/255。

- `499b1543` 把两宿主的发布恢复接到 SessionSupervisor 原恢复顺序，协调控制回执处理之后、恢复旧会话执行之前，再按当前宿主拥有的工作区核对准备记录。顺序回归验证先核对发布再恢复 handoff；107 项 Runtime Node、18 项 TUI、11 项 Desktop 宿主专项、Runtime Node 构建与 TUI 类型通过。完整进程重启和旧执行回执已被新代际替换的场景仍需单列。

- ADR `1b53433` 与实现 `4f0bb2ef` 补当前控制头被 resume 替换后的准备恢复。原执行由 v2 协调日志精确匹配计划、会话、epoch、代际和目标版本；只有已换代才读取历史停止回执，同代际仍核当前控制头及活跃执行。真实日志专项在重开后写入 resume 并验证只结清已证明停止的旧准备，不动另一未匹配代际。3 项 Node、2 项 Bun、Runtime Node 构建及架构/UI 检查通过。该结果未覆盖两宿主实际进程重启。

- `0b30145c` 同步历史停止读取改动对应的仓库内置协调 Worker。`b8e47e67` 将历史停止恢复扩至独立子进程。父进程落盘并关闭，子进程从实际 v2 日志与 SQLite 恢复并退出，父进程重开确认只结清有匹配停止证明的原调用。Node 与 Bun 各 2 项通过。子进程使用共享恢复入口、固定计划事实和受控 lease，未运行完整 Desktop 或 TUI 进程启动流程。
- `db4576ac` 标准包新增逐图确认四张宽窄及深浅主题任务详情，累计 51/255。

- `8a6b24d5` 补实际 TUI 启动进程验证。原 TUI 宿主通过 SessionControl 生成停止回执并关闭，独立 Bun 进程重建原 TUI 宿主、取得 lease、执行生产 tick，从真实日志和结果库结清原准备。断言没有发布回执、零模型回合。TUI 类型和 18 项宿主测试通过。Desktop 的进程级启动验收仍待补。

- `eb8ecdab` 补 Desktop 主进程宿主跨进程恢复。父进程经 Desktop 注册入口和实际 SessionControl 写停止回执，关闭后独立 Node 测试进程重新注册 Desktop 宿主并 sync，原准备结清为中断，零模型调用、零发布回执。37 项 Desktop 集成测试通过。该测试用受控桌面依赖与 lease，未启动已安装 GUI。
- 标准包再逐图确认运行、等待、窄亮等待详情和正在回复共四张，累计 55/255。当前源码已启动隔离 macOS arm64 本地打包和包内运行时检查，目录 `peer-adr118-desktop-current.hvnNr5`。

- `eb8ecdab` 的 macOS arm64 本地应用包完成，包内运行时检查及 `codesign --verify --deep --strict` 通过。应用为临时 ad-hoc 包，398,444 KiB；asar SHA-256 `6e454c5b520750f672159794d0732c7847f2dc985c50afd8c57f74b4a8967908`。包内 Electron 41.7.1 实跑隔离 Worker 求值、拒绝禁用节点、SQLite 重开和固定引用文本读取，四项通过。
- 用独立 HOME、Electron userData 与 Peer 数据根直接启动该 .app，通过本地 CDP 读取实际 asar 主页面，从加载态进入无机器人、接入模型的初始界面。只结束此次启动的子进程，日常实例 PID 保持。记录在 `peer-adr118-desktop-current.hvnNr5`。本地目录包缺少 updater 元数据，探针结束时出现 IPC 清理日志；覆盖 GUI 启动与包内运行时，正式签名公证、安装版完整交互故事仍待验收。

- 同一 `eb8ecdab` macOS arm64 临时签名包完成原生交互窗口专项。隔离 Bot 与固定版本用真实结果库和 EvidenceIndex 预置；包内主窗口经真实 preload/IPC 打开原生结果，Divisor 从 2 改为 5，派生 Ratio 为 2，保存回执出现。关闭重开原生窗口以及结束、重启整个临时应用后，条件仍为 5、Ratio 仍为 2；原生 Renderer 未暴露通用 Node 或主窗口桥。证据位于 `peer-adr118-desktop-current.hvnNr5` 的两份 result JSON。此项从预置固定结果开始，经主窗口 IPC 打开，尚未覆盖安装包内实际模型发布、任务报告入口、冻结草稿和最终回复。

- 同一 `eb8ecdab` 隔离包补冻结、原草稿与明确提交专项。原生窗口点击“将当前条件放入草稿”后，包内主窗口 preload 读取到原文、相同固定引用和 Divisor 5，pending 及输入队列没有新增。重启整个包后原草稿和冻结材料仍可读；探针显式调用原 preload 提交入口，真实宿主消费为规范用户消息，协议解码确认同值同版。报告位于 `peer-adr118-desktop-current.hvnNr5`。此项的明确提交由探针调用原 IPC，未点击 Composer 发送按钮；预置固定结果、无真实模型最终回复，正式签名公证仍未覆盖。

- 同一 `eb8ecdab` 本地包补真实 Composer 按钮路径。重启后在实际 Bot 页面看到原草稿与 Divisor 5，编辑正文并点击发送，Composer 清空且仅新增一条对应的规范用户消息。用协议解码确认其中的冻结回执、固定版本及值与之前冻结的材料一致。隔离 Bot 无配置模型，覆盖实际 UI 提交与规范落盘，未覆盖真实模型回复或正式签名公证。输出为本机包验证目录的 `composer-send-result.json` 与 `canonical-composer-send.json`。

- macOS 本机隔离探针核对文件旗标能否成为旧写者排他证明。为老化 60 秒的活 PID 目录锁和队列文件加 `UF_IMMUTABLE` 后，独立固定旧 `legacy-input-queue` 进程仍无法取得锁，返回 EEXIST；新打开的追加描述符也被拒绝。然而加旗标前已打开的追加描述符实际写入了 14 字节。因此排除此方案作为跨存储保护。仅在临时目录运行，清理前撤除旗标，生产清理仍等待真实排他端口。日志 `peer-adr118-macos-fence-probe.9nJdWd/report.json`。
- 用代码 `37fe6442` 的实际协调存储在独立临时目录完成 v2→v3 路径切换。切换完成后原路径新打开追加返回 `EISDIR`，切换前已打开的描述符仍向归档 inode 写入 15 字节，受保护的规范 baseline 逐字节不变。该实验验证协调存储隔离后旧写入的实际去向；输入队列若复用路径切换，可能把已受理的用户输入留在归档，因此不能将此隔离当作输入队列旧写者排他或清理准入。记录 `peer-adr118-coordinate-fd.BJwatD/report.json`。
- 当前干净源码 `eb8ecdab` 已启动 OpenAI encoder 整案复跑，沿用原角色与整案限额，输出 `peer-adr118-story-latest.lTiZM5`。

- `eb8ecdab` OpenAI 故事 `peer-interactive-live-1KN7ou` 完成发布、独立核验、首次正式交付以及 Budget 80 冻结规范输入。Bot 16 次额度耗尽，整案 25 次（worker 4、Verifier 5），第二委托尚未创建。持久回执可见等候版本冲突及无诊断的 `work_revision_conflict`。`b9281b48` 对已在范围内的工作或目标版本冲突返回重新读取的当前版本，依旧拒绝陈旧请求且不推进版本，52 项专项通过。
- `db4576ac` 标准包新审阅宽暗任务核验四种状态，区分通过、未通过、部分核验、无法核验与任务签收，累计 59/255。

- `b9281b48` 的 OpenAI 故事 `peer-interactive-live-gHJo5H` 完成首次正式交付与 Budget 80 冻结输入，首次会话 accepted。第二委托尚未创建，整案 29 次（Bot 16、worker 5、Verifier 8）耗尽 Bot 限额。检查规范 checkpoint 可见一次缺 assessment.reason、两次提交已经 result_ready 的旧等待，以及一次试图对仍在运行的 Verifier 请求重查。宿主均拒绝并提供相应事实；本案没有再出现工作版本冲突。按同一成本门槛继续处理模型回合收敛问题。
- `db4576ac` 标准包逐图检查宽暗与窄亮的历史恢复五种状态共十张，包括检查、保全、单项确认、批量确认与结清。截图哈希一致，累计 69/255。

- `9f21ecc5` 同步根目标复核与正式回复的顺序，44 项专项及 Runtime Node 构建通过。OpenAI Responses 故事 `peer-interactive-live-3TyMwx` 完成首次规范回复、冻结输入和第二轮显式通过 verdict。根复核也取得 program、facts、初始和冻结四类完整检查，但返回 `goal_review_failed`，重试达到 Verifier 16 次上限（整案 50 次），没有第二条正式回复。检查发现根复核事实输入缺少显式 verdict 本身，模型的具体拒绝理由未留存。

- `b5a85e08` 以当前计划和规范报告摘要匹配显式 verdict，把受版本约束的宿主事实提供给根目标复核。46 项专项、Runtime Node 构建、全仓类型及架构/UI 约束通过。OpenAI Responses / gpt-6-astra 的 `peer-interactive-live-lyZsdt` 通过完整任务故事。规范首次回复、同版本冻结输入、独立显式通过 verdict、四类完整检查、第二轮根目标通过、正式回复及固定结果文本读取均已核对。初始余额 45，冻结余额 25。共 51 次实际请求（Bot 28、worker 8、Verifier 15），离整案上限仅差一次请求。报告汇总输入 517,856、输出 13,184、缓存读取 153,856 tokens，账单金额未取得。此条覆盖 TUI 隔离宿主和一条完整真实编码路径，其他编码的整案、安装包真实模型交付和完整产品包验收仍分别跟踪。

- 同一 `b5a85e08` 的 Anthropic Messages / deepseek-flash 故事 `peer-interactive-live-YF8A7M` 已取得首次正式回复及冻结输入。第 42 次实际请求返回第 33 个 Bot 工具调用，触及 32 次 Bot 工具上限，正式 `verify_session` 调用尚未执行，第二条正式回复未交付。15 次协调调用和 6 次核验详情读取占用主要额度。相同编码在独立 `verify` 场景 `peer-interactive-live-BuqfIm` 以 4 次真实请求通过，覆盖固定检查与显式 verdict 子链。

- `b5a85e08` 的全仓构建、类型、架构/UI 与 Desktop IPC 检查通过。默认并行全仓测试的会话提交计时断言在独立文件复跑 9 项全过。按工作区串行复跑时 Runtime Node 1,922 项及其余先运行的工作区通过，Desktop 凭据测试发生 helper 超时。该文件隔离通过，完整 Desktop 套件以四路并发复跑 6,220 项通过、5 项跳过。TUI 单独复跑 846 项通过。保留两次初跑计时失败与后续复跑的区别。

- `3a838689` 收紧隔离故事对当前宿主回执的使用，保留预算和交付判据，14 项控制测试通过。Anthropic Messages / deepseek-flash 的 `peer-interactive-live-1uDwva` 在首次回复和冻结输入后用了 49 次请求，第 34 个 Bot 工具调用触发 32 次上限，仍未取得第二轮显式 verdict。相同编码换用已配置 glm-5.3 后，首次请求用尽 3,200 输出 token，返回无可用文本或工具的结果，整案到时退出。该样本位于 `peer-adr118-story-anthropic-glm.N6IjMA`。

- `b5a85e08` 标准产品包 `peer-adr118-product-root-verdict.LtR9dP/packet` 生成 255 张必查图，runId `d4a9f6b6-e772-4232-b360-695c07faa09c`。47 张通过自审，其中 35 张按截图 ID 和实际 SHA-256 匹配原审阅，12 张直接目视。Quick Chat 补采 macOS 原生合成，发现普通模型/思考强度标签深色约 3.41∶1、浅色约 2.85∶1。C 级修复 `93656f0f` 将选择器、附件图标和输入提示接到现有主题主文字色。Vite 构建及隔离原生两主题复测通过，所测普通文字约为 12.04∶1 和 14.14∶1。复测使用受控背景和真实原生窗口，专项日志 `peer-adr118-quick-chat-contrast-fixed.dFyyO3`，独立完整候选仍待重采。

- `3a838689` 构建隔离 macOS arm64 目录包，包内 7 项主进程导入、4 项交互内容导出及严格临时签名检查通过。app.asar SHA-256 `6301b55da865e19c99be0b1cc834951a810fc218a9b4672a2f2751baad1307ae`，目录 `peer-adr118-packaged-story.lFWOSQ`。

- 隔离的 `3a838689` 应用包经实际 Composer 写入规范输入，8 次 OpenAI Chat 请求均由既有配置真实转发，模型发起的只读发布委托被宿主拒绝。原因是 Desktop 运行时设置投影漏读已有的 `projectAgent.interactiveResults` 布尔值。B 级修复 `7847a2bd` 将该值加入现有投影，由原设置归一化提供默认关闭。新增断言在修复前以 undefined 复现，修复后 Desktop 设置、原生端口和集成共 47 项通过。应用包复测另记真实交付。

- `7847a2bd` 目录包复测通过临时签名及包内导入检查。app.asar SHA-256 `456f565c4cd3a331dcc600a704edf0e618050545714b182eaaece7a6257cc0e9`。两个隔离样本分别使用 15、31 次真实 OpenAI Chat 请求，经环回代理把既有配置的真实凭据限制在测试进程内。修复后真实只读委托通过准入，合成数据调用经正式审批入口取得单次 Grant，并写入固定发布索引。第二样本 `peer-adr118-packaged-approval.HPWdCE` 的自动和显式任务核验均通过，检查包括程序、数据与初始计算。根目标评估把有效固定引用与未进入该任务索引的 Bot 工具回执混用，宿主以 `goal_evidence_stale` 拒绝，限时内未写首次规范回复。包内冻结与最终交付仍未证实。

- 同一源码全仓类型、架构/UI 和 Desktop IPC 检查通过。最新标准包重采启动于干净 `7847a2bd`，目录 `peer-adr118-product-policy-fixed.kVKEK0/packet`。上一候选的 Quick Chat 对比度问题保留在原审阅，新候选需绑定新的源码指纹和截图。

- ADR `73ba6e7` 和实现 `093237e2` 为根目标覆盖退回补来源和未索引引用的位置。复现混用索引内外引用的断言在原实现失败，修复后按返回位置保留有效引用、纠正并重新通过根复核。36 项协调/核验专项、Runtime Node 构建、全仓类型、架构/UI、Desktop IPC 均通过。

- 同一候选的 OpenAI Chat / deepseek-v4.1-flash TUI 故事 `peer-interactive-live-4FL4zl` 完成发布和独立检查。16 次真实请求后因整案到时结束。Bot 的三次响应分别用满 3,200 输出 token 且未发工具调用，未取得附固定引用的规范首次回复。

- `093237e2` 的隔离目录包通过包内导入和临时签名验证。包内故事 `peer-adr118-packaged-ref-diagnostic.OumWzE` 走 31 次实际 OpenAI Chat 请求及一次真实单次审批，取得固定发布索引及程序、数据、初始计算检查。一次返回评估被拒为 `source_not_admitted`，其后宿主接收返回评估，根复核以 `verifier_permission_denied` 结束。记录无首次规范交付、冻结输入或最终交付。本次真实尝试没有触发新加的混用引用诊断。

- 独立旧队列进程验证 `peer-adr118-legacy-carrier-race.JN8KZl` 使用固定旧 writer，在清理末次提交检查前抢占老化目录锁并实际追加已签发的冻结选择载体。旧端保留载体，新解码恢复完整原选择。清理返回 `interactive_retention_stale`，原结果和状态未删。此证据只覆盖末次检查前，不提供生产排他保护。原工作区留存与冻结传输测试 27 项通过。

- `7847a2bd` 的 `peer-adr118-product-policy-fixed.kVKEK0/packet` 完成全部 255 图的自动采集，runId `a918bac1-a9b7-4ca3-8a29-1e37850abbb6`。实现者自审已通过 70 图，其中 28 图经 ID 与实际哈希匹配复用，42 图直接目视，包含 Quick Chat、回复悬停、核验与恢复状态。新候选 `093237e2` 开始重采，目录 `peer-adr118-product-ref-diagnostic.Hq3hbq/packet`。

- `093237e2` 的 OpenAI Responses 故事 `peer-interactive-live-LPBa4Q` 完成固定发布和独立检查，25 次实际请求后整案到时。唯一一条引用固定结果的规范 Bot 回复记录了 `verifying`，且正文仍承诺完成核验后汇报。根目标复核随后通过，任务却已代签为 `accepted`，没有落盘真正汇报结果的正式回复。证据保存在隔离目录 `peer-adr118-story-responses-diagnostic.VK1gwj`。

- ADR `3cf472e` 与实现 `a80813b0` 将代签依据绑定为正式回复持久化的任务状态和当前两项 revision。新回归在原实现复现进度回复误触发代签，修复后当前版本的进度回复与已过期的结果回复均无法触发代签，引用当前结果的规范回复可以。126 项回复、签收及任务主管专项、Runtime Node 构建、全仓类型、架构/UI、Desktop IPC 检查通过。旧历史回复沿原兼容路径读取，既有已持久签收不改写。

- `093237e2` 的 255 张标准截图完成采集，runId `e6509b73-0fef-41cf-a541-e176eb1a4229`。当前实现者自审通过 45 张，其中 35 张按 ID 与实际原图 SHA-256 匹配复用，10 张直接核对主对话及任务详情的核验状态。候选 `a80813b0` 另行采集，目录 `peer-adr118-product-current-acceptance.RfoPI9/packet`。

- `a80813b0` 的 OpenAI Responses 故事 `peer-interactive-live-YHe5kV` 再次产生引用固定结果的 `verifying` 回复。真实独立核验结束后，两次宿主读取及最终样本均保留 `result_ready`，证实没有因进度回复代签。根复核报告 `goal_review_failed`，首次交付阶段在 25 次真实请求后到时，未进入冻结和第二次交付。目录 `peer-adr118-story-current-acceptance.nj7KYY`。

- 同候选的本地 macOS arm64 目录包通过严格临时签名、包内 7 项主进程导入与 4 项交互内容导出检查。app.asar SHA-256 `9ff8d37be47f968570783b9ee6c9736d98d34df45aa3308250bcec0654cbccbb`，目录 `peer-adr118-packaged-current-acceptance.Hfy48W/package`。这项验证覆盖包与依赖完整性。

- `a80813b0` 的两个真实包内 OpenAI Chat 样本均经 Composer、正式单次审批、固定发布及程序、数据和初始计算检查。首样本 13 次请求，测试审批守卫延迟识别合成列名，消耗了首次回复等待时间。相同二进制隔离复跑 `peer-adr118-packaged-current-retry.gKHbFc` 对合成 A=20、B=35 的已核对结构准入，21 次请求含一次传输失败。任务已到 `result_ready`，Bot 在事件回合重复旧用户输入 disposition，宿主按契约返回 `input_disposition_required`，首次正式回复、冻结及最终交付均未取得。包内测试驱动只将含 `result_ready` 或 `accepted` 结构化状态和双 revision 的规范回复计为首轮交付。

- `a80813b0` 的标准包 `peer-adr118-product-current-acceptance.RfoPI9/packet` 全部 255 张完成采集及实现者自审，runId `6ab21f45-38be-426e-89e0-f189e339c2f4`。219 张直接目视通过，33 张按 ID 与原图 SHA-256 匹配复用，另有 3 张目视不通过。自动化列表深浅色搜索提示对比不足，深色约 1.66∶1。已保存记忆正文约 2.93∶1。实际 `qa:product:verify` 退出 1，报告第一处拒绝为深色自动化列表。保留原包与审阅，不以单项机器通过替代产品验收。

- C 级修复 `2fdaf1b1` 仅将自动化列表搜索提示及记忆条目正文接到现有主题正文色。新候选标准包已在 `peer-adr118-product-contrast-current.DAIPug/packet` 另行采集。

- `2fdaf1b1` Desktop 构建和架构/UI 检查通过。标准包完成 255 张采集，runId `a23b42ee-95b3-476e-9159-2ab7fed5a570`。上一候选未通过的三张截图已在本轮原图重新检查，自动化搜索提示深浅色分别约 12.33∶1、14.16∶1，已保存记忆正文约 10.36∶1，三项均通过此专项。实现者自审累计 92 张通过，其中 41 张按 ID 与实际原图哈希相同复用，51 张直接目视。整包仍需余下 163 张审阅及 `qa:product:verify`。

- 继续逐图核对 `2fdaf1b1`，累计 163 张通过，1 张失败，91 张待查。失败图 `task-cancel-failed-dark.png` 的关联任务已展开且重试可用，但提示文字被折叠区裁掉。此前脚本只等文字进入 DOM。专项复采分别捕获部分裁切和可读提示，确认结果随截图时序变化。
- C 级修复 `4cbf4724` 将关联任务和更多任务接入共享 MotionDetails，展开结束释放裁切。回归在截图前核对展开区、错误文字逐行可见及重试可用。旧构建在展开后释放裁切断言处失败，新构建通过该断言和文字可见性、重试防重、无关任务保留、延迟回执及键盘焦点检查。实现者已目视新版专项截图，完整失败提示与重试入口同屏；证据位于 `peer-adr118-cancel-red.RxULDD` 和 `peer-adr118-cancel-green.XtF7sJ`。Desktop 构建及架构/UI 检查通过。新标准包在 `peer-adr118-product-disclosure-current.ApxSPD/packet` 重采，待逐图验收。

- `4cbf4724` 的全仓 build、typecheck、test 退出均为 0，构建与测试包含 Desktop IPC 检查；日志 `peer-adr118-disclosure-engineering.17P3LK`。真实 SDK 在隔离 Electron 的 production/development bundle 中通过组件、状态、注入渲染异常、明确降级和保存后恢复专项；同批原生视图和工作区专项通过。标准 Electron 包 runId `609d41f1-fca7-4e20-976c-7c08bf5723fd` 采集 255 张，取消失败图复核通过；累计 53 张通过、1 张不通过、201 张待查。失败图中关联任务标题的“已取消”约 1.37∶1，折叠后状态难辨。
- C 级修复 `f4e5119b` 将关联任务摘要状态使用已有次级正文色。干净提交的标准 Electron 主流程已通过，保留取消反馈可见性断言。该次深色截图实测“已取消”约 5.16∶1，实现者目视确认完整。新包目录 `peer-adr118-product-readable-status.8yjsIj/packet`。全仓工程结果仍绑定上一提交，本提交已通过标准采集所用的 Desktop 构建。
- 隔离 Electron 探针 `peer-adr118-layout-read-timeout.X0vpRW` 使用固定结果和真实布局 IPC，延迟一次读取直到客户端超时。明确重试成功后，宿主持久读位为 440 px，用户没有移动时页面仍停在 0 px。已有 CAS 和迟到回执测试不覆盖实际 DOM 恢复。需同时核对主动滚动优先及原资源不重挂载。
- C 级修复 `3d314482` 在重试后的首次确认布局中恢复原读位。用户已滚动时保留当前几何并沿原保存流程持久化；迟到旧回执不改写读位。视图保持原实例，读取和保存失败分别说明。真实 Electron 主区专项通过两个分支及原交付、草稿、独立窗口和版本导航；Desktop 类型和 5 项共享读位测试通过。实现者目视 `workspace-layout-reading-recovered.png` 确认已恢复中段和原草稿。证据 `peer-adr118-layout-read-green.uRliYI`，最新标准包在 `peer-adr118-product-layout-read.AhoVh7/packet` 重采。
- `f4e5119b` 的标准包完成 255 张自动采集，runId `9ff470c4-5c98-4cc2-895c-2837f3f24478`。其中 43 张按 ID 和原图 SHA-256 相同复用，取消状态新图直接目视通过，余下 211 张未完成审阅。

- `3d314482` 全仓构建、类型、测试及架构/UI 通过，Desktop IPC 由原构建及测试门禁核对。标准包 runId `511fccbb-cfb3-41db-b73e-57058a87133a` 完成全部 255 张采集；43 张按 ID 与实际原图 SHA-256 一致复用，18 张直接目视通过，余下 194 张未完成审阅。取消失败与终态两张、深浅主题自动化搜索及本批历史恢复图均完成目视。
- 同提交 macOS arm64 临时目录包 `peer-adr118-packaged-final-chain.MS1Cik/package` 严格临时签名、7 项包内主进程导入和 4 项交互内容 export 检查通过。asar SHA-256 `18ccbe2140fb2214703138c0ac5b5498ca2d45c31d6105fbf7c5b9f8ca7a3f1c`。
- 同一目录包的真实 Chat 样本 GLM 5.3 在首个上游流中断后整案到时，未取得发布。Responses 样本 gpt-6-astra 经隔离环回代理透传 25 次完整上游流，取得一次原生单次审批、固定发布及独立程序、数据和初始计算检查。根返回评估在合法事件回合获得通过，回合随即让出。协调日志显示，重扫同一目标的旧进度回复把原工作从 runnable 改为 waiting_children；随后接入新的核验事件时启动了新切片，原 Provider 检查点没有被带入。首次规范结果回复、冻结及第二次正式交付未取得。证据 `peer-adr118-packaged-responses-chain.vwYdVF`。
- 同一目录包完成实际混合资源区专项，`peer-adr118-mixed-workspace-retry.0lAr8S`。用已索引的固定结果、真实工作区文档和环回网页，从同一资源标签区交替切换。固定值和试算读位、文档读位、网页 guest ID 与表单、Composer 草稿均保留；680 像素转换后复核固定结果和网页。宿主布局回读包含 interactive/document/browser 三种项，试算读位 420 px。两张图为实现者自审，画面保留布局保存中的说明，随后独立核对持久回执。固定发布是预置，网页使用环回站点。
- B 级修复 `c6b13a53` 补 ADR 中返回切片的回复恢复责任。旧进度回执重扫保持原当前工作状态和检查点；当前尝试及匹配当前根复核、同目标版本和正式状态的历史结果仍按原恢复逻辑结算。真实 v2 协调日志用例先复现 waiting_children，再验证原检查点可继续、后到核验事件保持待处理、正式回复仍经原绑定与结算。65 项 Node、46 项 Bun 专项通过。修复后的隔离包另在 `peer-adr118-packaged-return-replay.WkYjJb` 重建，真实整案待复测。

- `c6b13a53` 全仓构建、类型、架构/UI 和测试均通过，Desktop IPC 随构建及测试核对。日志 `peer-adr118-return-replay-engineering.JA2kqj`。同提交包内 7 项主进程导入、4 项交互内容 export 和严格临时签名通过，asar SHA-256 `fe0de000dd907f4b393f2507e0d98f5672f794cae61fcebaba9cc0d05f41a3f4`。
- 修复版目录包的 Responses 样本以同一 gpt-6-astra 完成首次规范结果回复。协调记录有真实让出恢复和该回复绑定，固定引用、当前任务修订和初始余额 45 均可核对。经实际回复详情的 Evidence 打开主资源区，再通过原控件打开独立视图。驱动为处理明确写者接管和显示单位的断言重启同一隔离包，保留首次回复、固定版本和已保存 Budget 80。独立视图确认余额 25 units，点击冻结只进入原草稿；明确点击 Composer 发送后，规范消息解码确认同版本、同冻结值 80。目视样本 `packaged-frozen-conditions.png` 显示来源限定、两行合成数据、保存及放入草稿回执。
- 同一隔离故事的第二委托和显式独立核验完成，规范 verdict 和四类完整检查均落盘。总计 52 次真实 Responses 流完整返回；达到本次驱动物理请求上限后，本机代理拒绝后续请求，期间没有第二次根目标复核和含固定引用的正式回复。报告保留首次失败前断言、重启、冻结输入和实际核验状态。待补最后回复及整案验收。
- `3d314482` 标准包继续自审至 97 张通过，其中 43 张按 ID 与原图 SHA-256 匹配复用，54 张直接目视，余下 158 张待查。最新 `c6b13a53` 标准包在 `peer-adr118-product-return-replay.iGLskQ/packet` 重采。

- `c6b13a53` macOS 目录包在保留原始 52 次请求样本后，用相同隔离数据重启并自动恢复原冻结输入。恢复驱动首启因内部函数导入路径错误提前退出，修正驱动后继续用同一目录包和原两条规范输入。额外上限 12 次，实际追加 11 个完整流和 1 次传输失败，合计 64 次转发及 63 个完整流。第二委托再次留下通过核验的记录。冻结输入对应的协调目标仍在原 revision，未取得第二次根目标复核或同时绑定同一固定结果和两项任务的规范结果回复。达到上限后按现有 rate-limit 路径记录阻断。证据 `peer-adr118-packaged-return-replay.WkYjJb`。
- `c6b13a53` 标准包 runId `5bfb84b7-bfdb-4240-8f56-9b51cd43a2f1` 完成 255 张采集。实现者自审 105 张通过（43 张同 ID 原图 SHA-256 复用，62 张直接目视），8 张核验详情图不通过，142 张待查。四种当前检查状态使用抽屉通用次级文字色，深浅主题中关键标签与检查值难读。原包 `peer-adr118-product-return-replay.iGLskQ/packet` 保留，整包未通过。
- C 级修复 `c53a27f9` 仅将核验检查标签及结果分别接入现有 Frost 次级正文和正文色。Desktop 构建及隔离 Electron 核验详情专项通过，覆盖四种核验状态、历史键盘展开、刷新失败后的重试及当前执行状态。实现者以同一场景的深浅原图比对，确认检查标签和结果比此前更清楚。证据 `peer-adr118-verification-contrast.WERT1p`，该专项构建含同样两行样式差异。干净提交标准包在 `peer-adr118-product-verification-contrast.woeQOj/packet` 重采。
- `c53a27f9` 的干净提交全仓构建、类型、架构/UI 和测试均退出 0，Desktop IPC 随原构建和测试门禁核对。日志 `peer-adr118-verification-contrast-engineering.GsFrAm`。隔离专项的八张核验详情截图均检查了当前结论、两项检查及历史记录的区别。
- 对照 `c6b13a53` 包内规范回合和持久化协调记录，第二次重启恢复原冻结 workId。恢复阶段实际调用 `coordinate_work query`、任务和核验读取，再次发起 `verify_session` 并收到通过；未调用 `coordinate_work assess` 或 `post_reply`。第二次正式交付缺在真实模型提交返回评估之前。界面预览中较长的工具结果会截断，但本轮恢复的 Provider 检查点仍保留 `verify_session` 的完整输出。现有证据不足以将未提交评估归因于宿主拒绝或预览截断。

- `c53a27f9` 标准包 runId `00571b35-543b-4592-9a31-ddaef700ab1d` 完成全部 255 张自动采集。实现者核对 59 张通过（41 张同 ID 和原图 SHA-256，18 张直接目视），含上轮全部八张核验详情问题图，剩余 196 张未审。证据 `peer-adr118-product-verification-contrast.woeQOj/packet`。
- ADR §12.2.1 由 `30aea21` 定义，`5b03de5c` 接 Desktop 主区和独立窗口。当前 Bot 明确换成另一有效身份时，ViewService 封存原视图，同一 sender 和页面只核对原 save outcome。StateStore 从同一存储及实际 pin 读回原回执，确认提交、确认未提交、未知分别处理。宿主不发快照或其他归属身份，原状态、冻结和版本入口均不能继续。Renderer 仅保留后续本地未确认输入供复制，确认放弃后用户自己再次关闭。
- 57 项 Node 宿主/领域和 33 项 Bun Renderer 专项通过，Desktop 类型及架构/UI 通过。隔离 Electron 使用真实主进程、IPC、preload、布局和条件存储，覆盖主区与独立窗口、原提交回执丢失及核对、未确认时阻止关闭、取消放弃保留、单独阅读位置的失败与再次关闭。为覆盖真实关闭检查点，`9f37d847` 调整最后一个场景的等待和断言。实现者目视两张恢复图，可读本地输入和明确放弃入口均可见，原 Composer 草稿保持。证据 `peer-adr118-owner-replacement.GiuaMk` 和 `peer-interactive-workspace-Hk75On`。
- 最新标准包按干净提交 `9f37d847` 在 `peer-adr118-product-owner-replacement.eVd7BU/packet` 重采。全仓检查使用相同运行时代码提交 `5b03de5c`，日志 `peer-adr118-owner-replacement-engineering.4hQwqV`。
- `5b03de5c` 全仓构建、类型和架构/UI 均退出 0。并行 `pnpm test` 因 Desktop 输入预测凭据查询的 fixture helper 超时退出 1，同一文件隔离复跑 1 项通过。整套复跑等待当前标准采集进程退出后，在 `9f37d847` 干净源码重新执行。
- `9f37d847` 干净提交复跑，全仓构建、类型、架构/UI 和测试均退出 0，日志 `peer-adr118-owner-replacement-engineering-retry.896K1O`。此前工作树在标准采集过程中开始了后续实现，指纹校验拒绝该轮，保留为失败采集，不进入逐图验收。
- 同一 `9f37d847` 全仓复跑的独立 SDK 专项含全组件、生产/开发 bundle、150% 实际 Electron 缩放、窄视口、减少动效、焦点和图表同值替代表。实现者目视深色窄视图的输入轮廓、范围提示、图形和数据行，自动化另核对辅助技术树包含表头及数据。500 行样本中 62 次 DOM 输入至可观察帧为 6.5–16.2 ms，未记录 Long Task。短窗 Tab CPU 增加 0.587 s，working set 从 242,016 增到 308,304 KiB。证据 `peer-interactive-renderer-xv0vzr`。持续及回收测量、系统读屏和正式安装版仍待验收。
- ADR §12.2.1 补充定义主区和独立窗口无条件会话时的表现恢复，`f4d7fb9d` 接线。主区由同页曾准入的预期 owner 和当前配置证明替换，独立窗口由原资源 sender、身份和 navigation 代次证明。确认后再次核对，原归属已恢复或状态未知时保留改动。退出只解除本地布局和读位阻断；已拒绝的旧读位须经新的宿主保存回执才可落盘。
- 23 项宿主/状态测试、Desktop 构建、类型、架构/UI 和 2 项隔离 Electron 专项通过，覆盖无原标签的主区旧布局、静态墓碑的独立读位、原 Bot 在确认期间恢复、再次确认、旧持久记录、新 Bot 记录和键盘焦点。实现者目视主区确认框，证据 `peer-adr118-presentation-only.phC7x1` 与 `peer-interactive-workspace-Fwh2eZ`。最新版 `f4d7fb9d` 在固定提交工作树重新采集标准包，再顺序跑全仓检查，输出 `peer-adr118-presentation-only-final.WRUItc`。
- `f4d7fb9d` 固定提交的全仓构建、类型检查、架构/UI 检查及测试均退出 0。标准包 runId `0691b845-dab5-4182-84ea-b258e5dd202d` 的 255 张截图均有自审通过记录，其中 38 张按同 ID 与原图 SHA-256 一致复用已目视记录，217 张本轮直接目视。快速输入窗两图保留 RGBA 原图，按对应主题背景复核控件布局与可读性。`qa:product:verify` 在相同固定提交上通过，指纹 `ff8964c6702dfcb3925100a987b1006895925a0b56645375d930bde790464164`。记录 `peer-adr118-presentation-only-final.WRUItc/packet`。此为实现者自审，覆盖源码 Electron 与脚本模型，系统桌面合成、真实模型端到端、正式安装版、完整读屏及持续负载仍分别验收。
- 在 macOS 临时目录用独立子进程持有已打开的可写描述符，普通进程对文件请求 `F_SETLEASE` 的读、写租约均返回 `EPERM`，旧描述符实际追加 7 字节。旧描述符关闭后，文件和目录的读租约仍返回 `EPERM`。Apple XNU 对该接口要求私有 entitlement，且冲突打开可触发限时降级或解除租约。此方案无法交付 §17.2.1 要求的生产兼容守卫，生产清理继续保持关闭。证据 `peer-adr118-darwin-lease.G9SjJ6/report.log`。[XNU 权限检查](https://github.com/apple-oss-distributions/xnu/blob/main/bsd/vfs/vfs_subr.c#L12734) · [冲突处理](https://github.com/apple-oss-distributions/xnu/blob/main/bsd/vfs/vfs_subr.c#L12980)
- ADR `b941621` 与实现 `e4a47144` 接入长任务回执的结构化续接。13 项材料化/编码测试、47 项 Desktop 编排和委托测试、34 项 Bun TUI Provider 测试、Runtime Node 和 Desktop 构建、架构/UI 检查均通过。用上轮真实主 Bot 检查点中四份完整回执走新旧编码对照。原结果 12,626–15,049 字符，新 Provider 回执 2,145–2,417 字节，两宿主保留同样的准确来源、修订、需求 ID 和引用，完整原文保留。证据 `peer-adr118-structured-provider-replay.TWV90i/report.json`。
- 同提交的 macOS arm64 临时目录包通过严格临时签名及包内导入检查。asar SHA-256 `deb47c499abfc81b53f0fd579eca7464248ed47fae2e9c283b5a81dd9b267135`。在原隔离数据的副本上启动，保留原两条规范输入和固定结果，沿宿主自然恢复及真实 Renderer 重试入口推进。实际 Responses 检查点包含新版查询、报告和任务列表的结构化续接字段。相对原样本新增 20 次转发及 20 个完整流，累计 84 次转发、83 个完整流。主 Bot 首次提交该冻结任务的 `coordinate_work assess`，两项需求均声明覆盖且通过宿主索引准入。根 Verifier 收到同修订的已通过显式复核，并实际完成无截断的程序、绑定数据、初始和冻结四次检查。最终返回 `goal_review_failed`，回执仅有通用错误，缺少可定位失败项。达到复测上限前无第二次 `post_reply`，保留原会话。证据 `peer-adr118-structured-live-recovery.qlwVxA/structured-delivery-audit.json`。下一步需留存并按当前评估范围回传有界根复核诊断，以区分语义缺证、模型格式与报告准入失败。
- `e4a47144` 的全仓构建、类型、架构/UI 和测试均退出 0，Desktop IPC 随原构建及测试检查。日志 `peer-adr118-structured-delivery-engineering.xTCxx3`。同提交独立工作树开始重采标准包，输出 `peer-adr118-structured-product.iaaGGa/packet`，待逐图审阅和 verify。
- macOS 测试进程的只读 `AXIsProcessTrusted()` 探针返回 false，未修改系统授权。系统读屏验收仍缺；前述 150% 与数据表证据限于 Electron 辅助技术树。记录 `peer-adr118-native-ax.tCFGIN/result`。
- ADR `182758d` 与代码 `f543cba9` 在现有 `assess` 回执保留有界根复核诊断。45 项协调/委托测试通过，覆盖格式错误、缺证、过滤、来源变化、旧操作重放及修正后复评。新版临时目录包在原隔离状态副本中两次取得根复核失败及修订绑定诊断，均完成四项实际检查，真实报告说未看到显式核验记录等宿主事实。证据 `peer-adr118-root-review-live.eUTndo/root-reviews.jsonl` 和 `assess-diagnostics-audit.json`。以原完整检查点做单请求旁路复放，实际 Responses 返回通过报告，引用四项既有检查；该诊断未执行工具或推进宿主状态。记录 `peer-adr118-root-review-replay.8vVJXR/report.json`。
- 对照实际发包前的 Layer 1，第四组 Tool Call/Result 之后，9,829 字符的当前根核验输入降为 905 字符预览，丢失 `explicitVerifications` 及需求字段。ADR `7447198` 与代码 `2732d443` 使 Desktop/TUI 请求投影及 Desktop 预算检查共用原当前输入保护。OpenAI/Anthropic 回归先复现，再确认保留当前完整输入、保留四组配对并仍压缩更早历史。47 项 Node、34 项 Bun、Runtime Core 和 Desktop 构建通过。对原检查点重新编码保留全部 9,829 字符。记录 `peer-adr118-root-review-live.eUTndo/wire-compaction-replay.json`、`peer-adr118-active-input-red.BEKtw2` 与 `peer-adr118-active-input-green.rHvIpR`。
- `e4a47144` 标准包先因缺 Conversation Store 构建中止，补构建后第一次采集因 Electron 更新器 Promise 被回收中止。相同固定提交独立重采退出 0，runId `14bc1f44-9e84-4581-a6f8-de877b09c9d1`，255 张待目视及 verify。当前 `2732d443` 独立工作树先执行全仓工程检查，再采集同一提交的标准包，输出 `peer-adr118-active-input-final.6UQpWk`。
- `2732d443` 的全仓构建、类型、架构/UI 和测试均退出 0，Desktop IPC 随原构建及测试检查。macOS arm64 临时目录包通过严格临时签名和包内导入，asar SHA-256 `d12dfe0c85f444761e54fc91ac237e60bf1ef592becb75fb9f64c4e853453e7a`。从已失败两次的后期数据副本恢复，额外转发 7 次、6 个完整流后出现连接重置，未进入新根复核。保留这份失败样本 `peer-adr118-active-input-live.HejbKl`。
- 使用同一新版目录包，从之前进入根复核的同一基线副本复测。经 Renderer 的实际重试，保留两条原规范输入、首次正式回复及同一固定版本。增加 11 次 Responses 转发，均完整返回。最后一轮根核验的实际发包在四组已完成调用之后仍含 9,829 字符、显式 verdict 和原需求。根核验通过并落盘，含四个规范检查引用。真实 `post_reply` 落盘 `reply:turn-141886f1-0bd9-412f-8a8b-a59c03722e7e:2`，绑定同一发布及两个带完整修订的任务，回报 45 与 25，区分独立核验和人工接受。规范对话仅保留两条原输入，索引中只有一个发布身份。协调日志含提交、结算、交付和同次 reviewRef 的 `fulfilled` 闭合。证据 `peer-adr118-active-input-reseed.JehtpQ/canonical-delivery-audit.json`、`root-wire.jsonl` 及 `root-reviews.jsonl`。此故事跨隔离包重启和升级恢复，最终交付使用 `2732d443`。

### 清理提交确认、标准采集与持续输入

- 在临时目录用真实 SQLite 清理事务和独立固定旧队列进程，将旧写入放到最后一次守卫检查之后、SQLite 提交之前。旧端抢回已老化目录锁并提交带原冻结材料的有效输入。原实现报 `interactive_retention_stale`，实际已提交墓碑与回执。ADR `efb62bc` 和代码 `67ff99b1` 区分提交前阻断及提交后确认失败。复测得到 `interactive_cleanup_outcome_unknown`，原回执、墓碑和旧队列输入均可核对，同一请求读回原回执。27 项 Node 清理专项、Runtime Node 构建与架构/UI 检查通过。证据 `peer-adr118-after-last-retention-check.P9uS6Z`、`peer-adr118-cleanup-confirmation.RIAUlD`。此实验使用受控兼容守卫，生产仍缺对已打开旧写者和旧视图的隔离证明。
- `67ff99b1` 全仓构建、类型、架构/UI 和测试均退出 0，Desktop IPC 随构建及测试门禁核对。证据 `peer-adr118-cleanup-outcome-engineering.GuzVAm`。
- `2732d443` 的标准包完成 255 张采集，runId `751109cb-ddde-440c-9fbf-e16857d7334a`。实现者自审通过 199 张，其中 44 张按同 ID 与实际原图 SHA-256 一致复用，155 张本轮目视；另有 1 张失败、55 张待查。`chat-process-summary.png` 在键盘关闭技术详情后的淡出阶段拍摄，仍可见原始参数，无法核对稳定终态。仅采集脚本提交 `3365486f` 等待原始技术文本隐藏后再截图，从固定提交重新采集。干净工作树首次采集缺预建依赖，补 Desktop 构建后重采。两次证据分别为 `peer-adr118-active-input-final.6UQpWk/packet` 与 `peer-adr118-settled-disclosure.3HIXHj`。
- `2732d443` 的生产 Renderer bundle 在隔离 Electron 中，以真实 SDK 和 500 行合成数据连续输入 114.64 秒。602 次 DOM 输入至可观察帧的 P50/P95/P99 分别为 9.2/13.7/16.4 ms，最大 22.1 ms，记录 0 次 Long Task；Tab CPU 增加 8.20 秒。working set 为 241,872 → 274,448 → 192,960 KiB，事件监听器为 184 → 455 → 182，末值在显式卸载、等待及 CDP 主动回收之后取得。证据 `peer-adr118-sustained-renderer.k502ch/test.log` 所指目录内的 `production-sustained-summary.json`。此样本使用 DOM 输入与测试状态接口，系统输入法、安装版性能和更长时段分别验收。
- `2732d443` 的 macOS arm64 目录包以本机 Developer ID 和 hardened runtime 签名，严格验签、7 项主进程导入、4 项交互内容 export 及 2 个 Dock 资源检查通过。asar SHA-256 为 `a70c579ce6df1babd1a6e1e914b64ba37efe98751227c5ca22285a751a70251f`。将本地 DMG 中的 app 拷入临时安装目录并再次验签。Gatekeeper 返回 `Unnotarized Developer ID`，正式公证安装待验。
- 从临时安装目录启动上述包，以隔离数据和预置固定结果验证原生视图将 Divisor 由 2 改到 5，Ratio 为 2，关闭窗口和重启整个包后仍可读。冻结放入原草稿，队列未新增；实际 Composer 按钮只发送一条规范输入，协议解码与宿主原冻结回执一致，保留同版本和数值 5。第一次发送探针在新规范日志尚未创建时提前结束，修正后重新冻结并实测通过。证据 `peer-adr118-developer-id-package.I6noKa` 内的包日志与 `isolated-install/canonical-audit.json`。该安装故事使用预置结果，真实模型最终交付证据另见前述临时目录包。

### 只读清理对账、Anthropic 整案与本机输入法

- ADR `998850b` 先定义三类清理的请求级只读对账。代码 `45a4cce1` 使回执读取核对当前 owner、原目标、请求 ID 和摘要。读取缺失回执不申请守卫或启动清理，冲突明确拒绝。历史固定版本单独读取有界墓碑摘要。Node/Bun 各 41 项专项、全仓构建、类型、架构/UI 和测试通过，Desktop IPC 随原门禁核对。证据 `peer-adr118-scoped-cleanup-receipts.WSO8E8`。
- 在 macOS 临时目录运行 `revoke()` 隔离探针。系统调用对同 UID 的普通队列文件返回 `ENOTSUP`，已打开描述符的独立进程仍读出原始内容并追加 9 字节。该接口无法成为生产兼容守卫。证据 `peer-adr118-macos-revoke.7Fky9G/report.json`。[Apple XNU 实现](https://github.com/apple-oss-distributions/xnu/blob/main/bsd/vfs/vfs_syscalls.c#L10499-L10502)
- 干净提交 `3365486f` 的隔离 TUI 宿主通过 Anthropic Messages / deepseek-flash 真实任务整案。47 次实际请求（Bot 27、worker 8、Verifier 12），记录输入 316,423、输出 30,759、缓存读取 479,360 tokens，未取得账单金额。规范对话两条原输入、两次正式回复，原发布与冻结 Budget 80 保持同一固定版本，余额分别为 45 和 25。原始存储复核了最终回复绑定的两个任务及其双修订、四类显式核验回执和可读 TUI 交付文本。证据 `peer-adr118-anthropic-latest-story.WoJy7R/peer-interactive-live-INgqKY/canonical-audit.json`。样本使用合成任务和已配置模型，覆盖隔离 TUI 宿主；Desktop 安装、公证及独立产品审查另计。
- `3365486f` 标准包 runId `b7c0f17f-915c-4bd4-bfbb-fc1b10e69d6b` 完成全部 255 张采集。当前实现者自审通过 79 张，43 张经同 ID 和实际原图 SHA-256 匹配复用，36 张直接目视。新回复过程截图中技术参数已完全收起，键盘焦点和当前状态仍可见。其余 176 张待审，整包 verify 待跑。证据 `peer-adr118-settled-disclosure.3HIXHj/packet`。
- 同提交的原生结果文本控件以隔离 Electron 副本和本机当前输入法实测。原生键盘输入拼音时记录可信组合开始及中间输入，界面保留草稿并禁用保存、冻结，结果标题与宿主检查点均仍是原值。空格选定“中”后，记录可信汉字输入及一次 `isTrusted=false` 的组合结束，随后界面标题、值和宿主持久状态一致。使用实际资源窗口、preload、IPC 和结果库，预置固定结果，隔离 Renderer 通过环回静态资源启动。覆盖此文本控件，Composer、正式公证安装及系统 VoiceOver 待单列。证据 `peer-adr118-native-ime.4NZH5A/canonical-ime-audit.json`。

### 原生 Composer 选词、草稿和发送

- 用 `2732d443` 原打包归档、隔离 Electron 壳及真实本机输入法复现。拼音组合中的回车只结清输入法，队列与规范对话均无新输入。再次组合并用空格选定“中”后，草稿和冻结值 5 可读。普通回车却插入换行，规范输入仍为空。实际事件为空格 keydown 229、keyup 32，之后为非组合 Enter 13；共享守卫把前者错误登记为 held Enter。原样本 `peer-adr118-composer-native-ime.zkO3iW/legacy-enter-swallowed.json`。
- C 级修复 `7e1a76c5` 按 Enter 键名或实际键位维持按住状态，保留 229/Process 的组合优先级。回归先失败后通过，含空格与实体小键盘 Enter 的不同释放顺序。13 项键盘/会话/表单专项、Desktop 构建和 macOS arm64 目录包严格临时验签及包内运行时检查通过。asar SHA-256 `661755c1f2a398f3e258574af1b2a5ac7b8781d67ee8cd52ed6f642829da4444`。
- 用同一修正归档的产品代码和预置固定材料在独立壳复测。组合回车及空格选词都保留草稿和原冻结条件，发送前无队列记录或规范输入。首次独立回车只产生一条规范用户消息，无额外换行，协议解码和 SQLite 原冻结回执一致，仍为同版、同值 5。证据 `peer-adr118-composer-ime-fixed.tYbY6G/canonical-composer-ime-audit.json`。这是实现者的真实系统输入法专项，使用独立 Electron 壳、环回静态资源、无配置模型和预置发布，公证安装及 VoiceOver 分别验收。
- `3365486f` 标准包自审至 139/255。干净提交 `7e1a76c5` 的全仓构建、类型、架构/UI 和测试均退出 0，Desktop IPC 随原构建和测试门禁核对。同提交标准包已启动重采，记录 `peer-adr118-composer-fixed-candidate.KX8Uxr`。逐图结论只绑定对应原图校验值。

### 固定候选整包、独立终端与旧队列切换验证

- `7e1a76c5` 的 `qa:product:test` 8 项均通过。标准包完成全部 255 张的实现者自审，其中 218 张本轮目视，37 张按同 ID 与原图 SHA-256 一致复用。`qa:product:verify` 退出 0，runId `f0e4df2c-b801-4ff0-9290-fee686ea1c1d`，源码指纹 `78c1fbf9ebff8eb2875299499c0c0c69472b05d535779b9b4eb857aee9899033`。证据 `peer-adr118-composer-fixed-candidate.KX8Uxr`。覆盖源码 Electron 和脚本模型，独立审查、系统 VoiceOver 与正式安装版另计。
- 同提交通过 IUI-T20 的临时 macOS arm64 独立归档专项。归档 SHA-256 `9e38783aaf5ef87380b40de39cecef4ff52e6d792d7c44cf05d15f2737054f5f`。仅使用系统 PATH，从解包二进制运行 help、version 与 `peer result <固定引用> --json`。独立 PTY 使用早前真实 Anthropic 任务的隔离合成数据，经 `/tasks`、`/task N`、`/result 1` 打开同一固定版本。终态显示完整固定引用、未验证的模型摘要及独立的“按初始条件计算”，包括 Budget 100、Remaining 45 和表格中的 A/20、B/35。括号粘贴和两组逐键输入均以退出码 0 完成。早期复测在上一轮保存的 `asks` 前插入 `/tasks`，干净草稿中未复现额外字符。证据 `peer-adr118-standalone-tui.nujFC5`、`peer-adr118-paste.PlVEi8/terminal-audit.json`、`peer-adr118-typed-fast.u0TMmm/terminal-audit.json` 与 `peer-adr118-typed-drained.xbCoYd/terminal-audit.json`。本地归档使用临时辅助程序，正式分发及各目标平台安装另计。
- 固定旧版 `8b3ffbcf` 的真实队列夹具在 `holdsLease=false` 时仍受理输入。独立进程在 `appendFileSync` 的真实描述符打开后暂停，测试进程换入复制自同一原内容的新 inode，再恢复旧端追加。旧 `submitInput` 返回受理 ID，旧 inode 有对应记录，当前权威队列及同一个旧端的按 ID 查询均找不到。基线输入在新权威仍可读。证据 `peer-adr118-queue-generation.sNjMkB/report.json`。该受控交错仅使用临时目录，证明替换路径会割裂已受理输入；生产清理保持关闭。
- `7e1a76c5` 的独立二进制在仅复制 `conversations`、`goal-plans` 和 `projects` 的临时数据根中，读取同一 Anthropic 故事的固定结果时退出 1。规范发布索引与对应工作会话仍保存同版发布 Tool Result 和 610 字符的模型摘要，结果 SQLite 缺失。`peer-adr118-portable-conversation.qrGwUv/report.json` 固定了复现。ADR §17.3 明确该摘要的本地人工读取与来源核对边界，接线与实际验证待续。

### 跨设备固定摘要 IUI-T19

- 设计提交 `fba2960`，实现提交 `fa9348e9`。在本机版本缺失时，复用迁移后的规范工作会话 Tool Result、原 EvidenceIndex、任务与当前 Bot 身份，返回同版 `origin_only` 摘要。Conversation 写者文件通过原固定版本校验，新增有界只读入口独立导出。局部回归覆盖正常文本、重复调用、流式未完成、错任务、归属更换和本地结果原状态。新提交的全仓检查和标准产品包在 `peer-adr118-portable-final.Q8ah8D` 运行，`7e1a76c5` 的既有整包通过记录继续绑定旧提交。
- 从 `fa9348e9` 编译的独立 macOS arm64 二进制对真实 Anthropic 合成任务的移植副本返回完整固定引用和 `origin_only`。610 字符摘要逐字节匹配原记录，CLI 前后导入目录文件 SHA-256 全部一致。相同二进制经独立 PTY 从任务列表打开同一固定版本，显示原设备与未验证摘要，终端退出码 0。证据 `peer-adr118-portable-summary-check.aPcC7S/portable` 与 `portable-pty-final/terminal-audit.json`。两次读取均未创建结果库。
- 隔离 Electron 的生产证据组件经受信任 preload 和正式 IPC 从同一数据副本读取。原设备提示和模型摘要在原证据阅读处可读，未出现交互入口、网络请求或页面错误。`peer-adr118-portable-summary-check.aPcC7S/desktop-final` 含截图和机器回执。截图由实现者目视，确认提示、摘要和技术详情的层级及正文换行。使用正式组件的最小隔离壳，整包、正式安装和 VoiceOver 单列。
- `fa9348e9` 全仓 build、typecheck、architecture:check、test 及 qa:product:test 均退出 0。进一步读取实际 Desktop Responses 可携带数据时发现其规范回执使用 `local_capability_result_ref` 与 success，和 TUI 的 completed 不同。代码 `74e0bae9` 分别核对两种格式及各自完成条件。23 项发布来源和旧传输测试通过。相同最新独立 CLI 二进制分别从两份实际来源的可携带副本读取，Desktop 的 167 字符和 TUI 的 610 字符均逐字节匹配，两个数据目录前后文件哈希一致，未创建结果库。证据 `peer-adr118-portable-two-formats.DpqCur/report.json`。
- `74e0bae9` 的隔离 Desktop 证据视图也从同一份 Desktop Responses 移植数据读取，实际正文逐字匹配独立 CLI。截图与机器回执在 `peer-adr118-portable-two-formats.DpqCur/desktop-evidence`，实现者目视确认提示与摘要可读，作用域内未出现交互控件、网络请求、页面错误或结果库。上一提交 `fa9348e9` 的整包在快速输入模型选择等待 30 秒后失败。最新提交的 build、typecheck、architecture:check、test 及 qa:product:test 均退出 0，Desktop IPC 随原门禁核对。同提交标准采集、255 张必查图目视复核与 `qa:product:verify` 已通过。runId `62bd43ab-5004-4f99-b9eb-b162eda7fbe0`，源码指纹 `0ecf9c195b69b5b3d39576c48e1d13ce22e93cc5f041babd8482e022e30c36bb`，证据 `peer-adr118-portable-two-formats-final.RqwGjj/packet`。为实现者自审，覆盖合成模型与源码 Electron，不含正式安装 RC、完整屏幕阅读器或长时回归。
- 最新独立 PTY 也从 Desktop Responses 的迁移副本打开原任务详情，显示同一完整固定引用和 `origin_only` 摘要。终端正常退出，未创建结果库。证据 `peer-adr118-portable-two-formats.DpqCur/desktop-origin-pty/terminal-audit.json`。

### 维护入口和规范消息索引的隔离边界

- `74e0bae9` 的隔离宿主进入实际协调维护，等待当前执行停稳，维护期间显式重启被拒绝。独立固定旧输入队列进程在无执行租约时追加输入并返回受理 ID。原队列仍可按该 ID 找到完整输入。维护解除后，原宿主只创建一条规范输入并执行一轮。证据 `peer-adr118-maintenance-input.0KUaJ5/report.json`。保留原队列时的排队恢复已验证，维护入口自身无法阻止旧写者。
- 同提交持有实际 `acquireMessageRetentionGuard`，独立进程使用当前 Conversation Store 的 `updateTitle`。锁目录一直存在，标题仍成功落盘，随后守卫的修订复核返回失效。证据 `peer-adr118-conversation-metadata-guard.o0OXqK/report.json`。这是当前索引元数据写入路径缺少排他的复现，尚无跨最后核对至提交的写入保护。ADR §17.2.1 明确元数据写者的锁范围及后续验收。
- `3568a04a` 将当前 Conversation Store 的元数据改写、消息计数回填及启动迁移接入同一索引锁。异步终态取得索引和历史锁后才提交，在历史锁冲突时先释放索引锁再等待。跨进程回归证明持守卫时标题、已读写者等待，释放后提交且规范输入载体完整。后台回填等待并保留最新标题。114 项 Conversation Store 测试与 158 项 Runtime Node 交互结果测试通过。固定旧版同步消息写入的相关源码段保留逐段校验。旧二进制仍可能绕过此规则，生产兼容守卫仍待。证据 `peer-adr118-message-index-work.lQmJHv`。

- `1da86e18` 使已经删除的会话根跳过后台计数回填，114 项 Conversation Store 测试再次通过。`3568a04a` 的第一次全仓测试中独立预测凭据 worker 发生超时，单文件隔离重跑通过。`1da86e18` 串行工作区重跑的全仓 build、typecheck、architecture:check、test 与 qa:product:test 均退出 0。Desktop IPC 目录新鲜度通过（405 channels、439 preload operations、354 main registrations）。同一提交的标准产品采集及 `qa:product:verify` 通过。255 张必查图中 210 张本轮目视复核，45 张按同场景原图 SHA-256 一致复用。runId `554a5cd5-e404-4a46-8dd7-67a30d5cee7b`，源码指纹 `faff7de965febd28948122cdc23378d7191b2ebd08f2f2707ea0919a190fbd05`，证据 `peer-adr118-index-candidate.kSucO9/packet`。这是实现者对源码 Electron 和合成模型的自审，正式安装、完整系统读屏与长时回归另计。
- macOS 临时 APFS 卷中的固定旧输入队列在打开追加描述符后暂停。强制卸载该临时卷后，已打开的读写描述符均返回 `EIO`，封闭旧挂载路径后新的旧端请求返回 `ENOTDIR`，两次请求均未受理。另处重挂同卷后可读取卸载前已确认的原输入。旧进程仍能访问事先已读入内存的字节。证据 `peer-adr118-disk-epoch.uGFw0u/report.json`。此探针仅覆盖预先独占挂载的临时根和固定旧队列，不构成日常数据根、跨平台或已打开旧视图的生产隔离。

- 独立进程从固定提交 `8b3ffbcf` 的原始 ViewService、Result Store 与 State Store 打开真实只读视图，未取得 writer，也没有写入新版视图 pin。仅在临时合成数据中用受控兼容守卫执行当前清理，预览没有视图阻断，事务提交墓碑。旧 sender 仍活着并持有原先交付的内容，使用同一固定引用重读得到 `interactive_content_cleaned`。证据 `peer-adr118-old-active-view.gQndUG/report.json`。生产守卫须核对旧视图的实际生命周期。

### Linux x64 独立归档 IUI-T20

- `3568a04a` 在隔离 Linux x64 容器中用仓库正式脚本构建并打包 CLI 和凭据 helper。首次构建因容器 bind mount 上 Bun 编译器无法重命名临时产物而失败。将同一源码归档解到容器原生文件系统后构建通过。归档 SHA-256 `d78d6ec92e63ee2d88e1355a35b10bc231dd31111b4e48dcd3dd1c37ed76e670`。
- 在断网、无 GUI、仅系统 PATH 的隔离 Linux x64 容器中解包执行 help、version 和 `peer result <固定引用> --json`。Desktop Responses 与 TUI Anthropic 的原固定引用和 167、610 字符摘要逐字节匹配，两个 CLI 数据副本的文件哈希均未变化。单独克隆 Desktop 来源数据并重绑容器工作区路径，真实 PTY 从 `/tasks`、`/task N` 到 `/result 1` 打开同版原设备摘要，退出码 0。证据 `peer-adr118-linux-standalone.81cOrp/receipt` 下 `linux-cli-audit.json`、`desktop-pty/terminal-audit.json`。容器使用 x86_64 仿真，覆盖归档解包与文本入口，正式分发和原生 Linux 主机另计。 同一归档从本地含结果库的隔离副本用 CLI 读到同一可用版本，再经断网 PTY 打开任务中的固定版本。显示 Budget 100、Remaining 45 及 A/20、B/35，正常退出。证据 `local-computation/terminal-audit.json`。

### 清理对账、Linux Desktop 安装和远程墓碑

- 发布仓库最新正式 RC tag `v0.1.0-rc.35` 不含交互视图 Module，但其 `input-queue.mjs` 与固定旧源码 `8b3ffbcf` 字节完全相同，SHA-256 `d6cbe49ea8dd13736cc17068a7fbd92e429838a022d964ee3914303e4da27cd5`。此前真实旧队列的维护受理风险覆盖这份已发布队列实现；旧交互视图生命周期证据来自固定开发提交，分开记录。
- 基线 `1da86e18` 复现切走执行租约后当前 Bot 无法只读核对已提交的清理回执。ADR `4ab8437` 明确两类权限，代码 `8d49fbde` 在 Desktop/TUI 保留当前活跃 Bot 的本机只读对账。专项实际覆盖结果、孤立冻结、独立材料三种持久回执及历史墓碑，禁用或失租约时预览/清理调用拒绝，归属替换或停用后对账也拒绝。基线先失败，修复后 159 项 Runtime Node 专项通过，证据 `peer-adr118-cleanup-reconcile.bzTHtZ`。
- `8d49fbde` 全仓 build、typecheck、architecture:check、test 和 qa:product:test 均退出 0，Desktop IPC 目录核对通过。同一提交的标准产品采集和 `qa:product:verify` 通过。255 张必查图中 208 张本轮目视复核，47 张沿用同场景原图 SHA-256 一致的已审记录。runId `296e9bc3-e076-4f2a-8c44-af4339724af4`，源码指纹 `1eab612efb05dc688e58c0477df4494c35432e9144759b8dfb566bc5f298d5aa`，证据 `peer-adr118-reconcile-candidate.MlKQsx/packet`。这是实现者对源码 Electron 与合成模型的自审，安装、完整系统读屏与长时回归另计。
- `1da86e18` 的 Linux x64 `.deb` 与 AppImage 由仓库正式打包脚本生成，包内 7 项主进程导入、4 项交互内容导出和 2 项 Dock 资源核对通过。归档哈希见 `peer-adr118-linux-desktop.qf3IHk/artifacts.sha256`。`.deb` 在断网容器经 `dpkg` 安装并成功启动。真实固定结果窗从 Divisor 2 改到 5，显示 Ratio 2，关闭重开和整个进程重启后仍读取同一固定引用和数值。实际 AT-SPI 树读到结果标题、标签和 `entry` 的值 5；实现者检查 `verification/result-linux.png` 的保存回执与试算值。使用 x86_64 仿真、Xvfb 和预置结果。
- 同一 `.deb` 在断网容器补测 Orca、Speech Dispatcher 与 eSpeak。保存前后分别播报区域 `Packaged trial` 和 `Divisor entry 2`、`Divisor entry 5`，按 Tab 后播报下一项操作 `Add current conditions to draft push button`。`peer-adr118-linux-desktop.qf3IHk/orca-verification/orca-debug.log` 记录实际语音派发，音频路由至容器虚拟输出。本项覆盖固定结果窗、保存后重开和键盘焦点移动。macOS VoiceOver 与其他控件的读屏流程单列。
- 同 Linux AppImage 的外层 ELF 无法在本机 x86_64 仿真中直接执行，解出原 SquashFS payload 后 `AppRun` 正常启动，Renderer 的主窗口和 Quick Chat 页面均来自该 payload 的 `app.asar`。与 `.deb` 中的 `app.asar` 逐字节一致，SHA-256 `5cdd3f5f8c7a76d627c8ac9b3f53c4f33643dcc47318ce16c904f9988ccc353f`。实际 x64 主机上的 AppImage 外层启动待验。
- `8d49fbde` 的 Remote 环回 HTTP、真实配对 WebSocket 与 390px Chromium 浏览器试验覆盖实际 SQLite 墓碑。D1 墓碑显示原固定身份、清理状态与脱敏模型摘要，原 HTML 字符按纯文本呈现；D3 墓碑只返回固定身份和可用状态。已核对列表、会话和任务三张原图，任务列表的长引用正常换行，未暴露私有标题或摘要，退出后清空。证据 `peer-adr118-remote-cleaned.GwINAn/output`。试验使用合成项目与受控清理守卫，不构成真实旧端隔离或实体手机验收。

### 已发布队列与最新 Linux 安装包

- 校验 GitHub Releases 的 `v0.1.0-rc.35` Linux x64 `.deb`，SHA-256 `93e76c5bae029eb499d5c2de9cd42835c43b4bd27061a0829d63798f0354fa5a`。在断网容器中分别使用已发布包和 `8d49fbde` 的真实 Electron Node 运行时，从各自 `app.asar` 直接导入队列和 ProjectAgentHost。旧端无执行租约，现有维护窗口已排空且禁止重启。对照输入仍获受理，维护期间未执行，退出维护后按原 ID 恰好生成一条规范输入。
- 同一次实验在系统调用层暂停旧 Electron 对已打开队列描述符的第一次写入，换入同内容新 inode 后恢复。旧端返回第二条原始受理 ID，记录仅存在于旧 inode，新队列按 ID 找不到，退出维护也没有消费该记录。证据 `peer-adr118-rc35-artifact.969t7P/runtime-report.json`。这把此前的源码夹具结论推进到真实发布安装包，实验只在合成数据上控制写入时序。生产仍需覆盖旧进程重新接入与已打开描述符的兼容守卫。[正式 RC 产物](https://github.com/ly-ccx/Peer-Agent/releases/tag/v0.1.0-rc.35)
- `8d49fbde` 用仓库正式打包脚本生成 Linux x64 `.deb` 和 AppImage，通过 7 项主进程导入、4 项交互内容导出及 2 项 Dock 资源检查。新 `.deb` 的 SHA-256 为 `fd4b562bd83288e0ebca194ad552f1d4db12425adda16e5122bd00ba480ffdc1`。断网容器实际安装后，结果保存、关闭重开及整个进程重启均恢复原固定版本和数值 5。Orca 实际派发了标题区域、`Divisor entry 2`、`Divisor entry 5` 和 Tab 后的下一项按钮名称。实现者目视核对保存提示、数值、试算与焦点。证据 `peer-adr118-appimage-vm.YrN0d0/orca-verification`。该项使用预置固定结果、x64 用户态仿真、Xvfb 和虚拟音频输出。

- 同一 `.deb` 通过 IUI-T22 双固定结果窗口持续样本。每个结果包含 500 行、柱形图和折线图，分别核对完整 500 点。303.37 秒内运行 22 轮打开、试算和关闭，共 528 次 DOM 输入，每次保持焦点。试算可观察延迟 P50/P95/P99 为 15.9/30.1/39.8 ms，最大 129.2 ms，观测到 1 次 131 ms 的 Long Task，无页面错误。所有轮次均回到 3 个页面，进程树从开启两视图时的 9 个进程回到原来的 7 个。进程树 PSS 为初始 820,711 KiB、开启最高 1,270,340 KiB、关闭稳定后 794,328 KiB。证据 `peer-adr118-appimage-vm.YrN0d0/soak/soak-report.json`。使用预置数据、自动化 DOM 输入、x64 用户态仿真与 Xvfb，耗时与 PSS 只对应此样本。
- 同提交的 AppImage SHA-256 为 `965c163f24dca42bbb9b7ad526343182bcbd3e1b5b2fecbf80c79f62dece596d`。 AppImage 与 `.deb` 中 `app.asar` 的 SHA-256 同为 `17db56f5c6353a9108c5a19f7b42a247ab59585d37f971d28bd51ddd7e583ac9`。QEMU 全系统仿真的 Debian x64 6.1.0-54 内核在断网环境直接执行原外层启动器，由 FUSE 挂载的 `app.asar` 实际启动非 root 窗口。保存 Divisor 5 后关闭重开并整个进程重启，固定引用和 Ratio 2 保持。默认沙箱样本的四个 Renderer PID 由 Chromium CDP 报告，内核均为 `Seccomp: 2`、`NoNewPrivs: 1`，进程命令行均无 `--no-sandbox`。实现者检查原截图的保存提示和数值，证据 `peer-adr118-appimage-vm.YrN0d0/sandbox/result`。此环境支持非特权用户命名空间。包内 `AppRun` 在命名空间探针失败时会自动加 `--no-sandbox`，其他发行版策略及实体 x64 硬件另计。
- 同一 AppImage 的 `APPIMAGE_EXTRACT_AND_RUN=1` 路径在另一断网 Debian x64 虚拟机复测。两次均从启动器自解包路径加载，恢复同一固定引用与 Divisor 5、Ratio 2，虚拟机回执为 0。首轮探针在启动器的进程收尾处停住，改为同时核对和终止应用进程与测试进程组后完成。该样本使用测试专用 `--no-sandbox`，系统隔离证据来自独立默认 FUSE 样本。两模式结果截图逐字节相同。证据 `peer-adr118-appimage-vm.YrN0d0/extract-process-group/result`。[AppImage 自解包运行说明](https://docs.appimage.org/user-guide/troubleshooting/fuse.html)

## 后续接线与完成审计

- 主资源区标签、布局、最近项目和正式返回已接。隔离 Electron 已验证布局超时后读取、旧回执隔离、SDK 渲染异常、静态恢复、Bot 替换后保留输入及无原视图的旧布局恢复。本机目录包已验证混合文档、浏览器和固定结果标签及宽窄连续性。全组件、150% 缩放、辅助技术树及 500 行持续输入和卸载回收有专项证据，隔离 Linux 已补固定结果窗的 Orca 读屏路径。
- 规范发布索引的交付入口及受控任务 context 中的 Tool Result 别名消费已接；主 Bot 报告/回复的固定结构化引用已在 `8140ce58` 接线；宿主确认的 head/predecessor 新版本入口已在 `0af50095` 接线。没有任务 context 的别名不推断工作；不从助手正文、标题或 URI 文本推断产物或版本关系。
- 冻结条件到原 Composer、明确发送、输入队列、canonical 消息及委托的同值同版链已接；固定目标/完整条件/真实检查证据已接两宿主并通过控制传输用例，固定初始控件标签及异步冻结在本批补齐。继续覆盖完整留存与清理和其余存储重写者，不把控制模型测试当作真实任务语义验收。
- 共享清理 Module 已接两宿主真实六来源及结果、孤立冻结和独立材料清理事务。仍缺覆盖已打开描述符和旧只读视图的生产兼容守卫，公开清理入口保持关闭。CLI 显式读取、Bot exec 自动交付、TUI 任务报告数据表与 Remote 任务投影已接，临时独立 CLI/TUI 归档已验证，正式独立分发验收单列。用户参数/原始草稿的可识别凭据与原生权限载荷已在 `ecb77e0d` 接共享/宿主准入及内存修正恢复，格式识别边界与测试覆盖单列。接管及明确归属替换时可核对原保存结果，损坏回执或缺少明确新归属保持未确认。
- OpenAI Responses 与 Anthropic Messages 已有隔离宿主的真实整案证据。Desktop 真实 Responses 目录包取得两次正式回复、冻结后的独立核验、根复核及规范闭合。原生结果字段及 Composer 均有系统 IME 专项。最新 `8d49fbde` 的全仓工程检查及标准产品整包已通过。正式 macOS 公证安装、VoiceOver 和完整系统读屏仍须单列。
