# ADR 118 交互结果实施与验证

创建时间：2026-11-03
最后更新：2026-11-03

状态：实施中，未完成。七项文档补充已交付，用户随后明确恢复“完整实现并测试完成”的目标，继续完整代码实施与提前验证。ADR 118 仍保持 Proposed；实现及单项测试不构成决策接受、运行时授权或产品验收。

## 范围与依据

后续范围由 [ADR 118](../../knowledge/decisions/118-openui-interactive-results-and-runtime-boundaries.md) 的首期 IUI-00—04、IUI-T01—29 及 §22 定义，尚待设计评审接受。既有代码起点为 Peer-Agent `4a58e2846875f85de69915764a127096721c5b0d`（RC35），分支 `codex/openui-interactive-results`；知识分支 `codex/openui-interactive-results-adr`。不以单个模块、静态 Demo 或某组测试通过代替完整交付。

当前目标覆盖完整的 Protocol、Provider、材料/版本/状态存储、Context Source、界面与多入口及测试，继续推进原范围。实施任务来自用户恢复的明确目标，不能从 Proposed 文档、阶段表或历史测试记录推导授权。公开接口、脚本准入、按需加载和原 Provider encoder、授权、Evidence、任务内核继续作为边界。

## 实施阶段

| 阶段 | 必须交付 | 当前事实 |
| --- | --- | --- |
| IUI-00 | 固定 SDK 脚本/AST/状态/纯求值与副作用审阅，公共接口验证；材料源、事务及逐存储兼容方案 | 公共 AST/严格 token 覆盖、共享预算与纯求值已用于独立 Worker；Bun 单文件探针已从空目录运行。SDK bootstrap 禁用、生产/开发 bundle 的真实 React 挂载和状态适配已有专项验证；产品 CLI、完整宿主接线及其余共享存储兼容尚待完成，未退出 |
| IUI-01 | Protocol/InteractiveContent/MaterialSource、受治理发布与只读检查、只读 worker 例外、版本 CAS、事务与 Evidence 对账、首次新写入前兼容保护 | 已提交 `b7b429ef`、`ea7e5afd`、`94ef2e92`、`9f3e0a7a`、`aabeaef4`、`5f9953ca`。真实 Desktop/TUI Provider、投影/准入/执行闸、规范工具及用户上传材料、启动/查询对账、持久准备身份/修复预算与授权分类已接线并验证；功能默认关闭。Conversation/草稿等完整兼容链和结果打开等下游仍待完成，未退出 |
| IUI-02 | Frost 组件、资源引用/会话、状态 CAS/单写者、恢复与冻结条件经原草稿链交回 | `9c726072` 的编辑会话与 SDK 组件之后，`518420a4` 已接正式资源联合类型、typed IPC/preload、真实 sender/owner/窗口生命周期和原生呈现/保存/关闭/重开链；阅读历史与布局服务进入受版本保护的结果子域。原生链已在隔离 Electron 中联通真实 SQLite。Artifact/混合标签及布局消费者、返回标签消费端、原草稿链与按需模块故障降级仍待完成；功能默认关闭，未退出 |
| IUI-03 | 显式 Context Source、预算/修复、按角色能力准入、Bot 引用和固定版本语义核验 | 显式 L5 目录 Source 已接入两宿主，按真实投影/角色准入，规则和工具来自同一次投影；目录由公共规格生成，specHash 包含资源限制。委托先核对 Verifier inspect 库存。Verifier 固定目标/证据允许列表、Bot 结果引用与真实模型生成/修复效果待完成，未退出 |
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
- 上述均为实现者验证，未做独立审查、完整仓库门禁、真实模型或产品回归，不构成 IUI-00—04 完整交付；最新后续结果随接线补充。
