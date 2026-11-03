# ADR 118 交互结果实施与验证

创建时间：2026-11-03
最后更新：2026-11-03

状态：实施暂停，未完成。按用户最新要求，本次仅把七项评审问题补入 ADR 118、明确契约与实施阶段并提交推送，先不改代码。ADR 118 保持 Proposed；以下保留既有分支的实际进度与历史验证，不作为继续实施、运行时授权或发布认证。

## 范围与依据

后续范围由 [ADR 118](../../knowledge/decisions/118-openui-interactive-results-and-runtime-boundaries.md) 的首期 IUI-00—04、IUI-T01—29 及 §22 定义，尚待设计评审接受。既有代码起点为 Peer-Agent `4a58e2846875f85de69915764a127096721c5b0d`（RC35），分支 `codex/openui-interactive-results`；知识分支 `codex/openui-interactive-results-adr`。不以单个模块、静态 Demo 或某组测试通过代替完整交付。

完整实施的既定范围覆盖 Protocol、Provider、材料/版本/状态存储、Context Source、界面与多入口，目前暂停推进；不删除或回滚既有分支工作。后续恢复实施须以明确任务为依据，不能从 Proposed 文档、阶段表或历史测试记录推导授权。公开接口、脚本准入、按需加载和原 Provider encoder、授权、Evidence、任务内核继续作为边界。

## 实施阶段

| 阶段 | 必须交付 | 当前事实 |
| --- | --- | --- |
| IUI-00 | 固定 SDK 脚本/AST/状态/纯求值与副作用审阅，公共接口验证；材料源、事务及逐存储兼容方案 | 公共 AST/严格 token 覆盖、共享预算与纯求值已用于独立 Worker；Bun 单文件探针已从空目录运行。React SDK 开发工具禁用、产品 CLI 及其余共享存储兼容尚待完成，未退出 |
| IUI-01 | Protocol/InteractiveContent/MaterialSource、受治理发布与只读检查、只读 worker 例外、版本 CAS、事务与 Evidence 对账、首次新写入前兼容保护 | 已提交 `b7b429ef`、`ea7e5afd`、`94ef2e92`；共享发布/检查 Provider、宿主事实准入、规范快照、版本/状态/冻结条件及 EvidenceIndex 恢复已具备测试证明。真实 Desktop/TUI 投影与回传装配、只读 worker 执行闸、准备阶段身份/修复次数、用户材料和完整兼容链尚未接通，未退出 |
| IUI-02 | Frost 组件、资源引用/会话、状态 CAS/单写者、恢复与冻结条件经原草稿链交回 | 待实现 |
| IUI-03 | 显式 Context Source、预算/修复、按角色能力准入、Bot 引用和固定版本语义核验 | 待实现 |
| IUI-04 | 多入口文本、包体/按需加载、兼容和完整功能验证 | 待实现 |

## 验证与完成标准

本次文档补充只做内容、引用及 diff 审阅，不运行测试、构建或产品回归。以下历史验证保留其原提交与覆盖范围。后续若明确恢复完整实施及测试，完成后执行完整 build/test/type/architecture/IPC 及产品 capture → AI 审阅 → verify，逐项记录实际覆盖。只使用隔离临时数据，不安装或重启日常应用，不创建版本/RC 或发布标签。

验收清单是 ADR §22 的 IUI-T01—29，以及两种实际已配置 Provider 编码路径的真实模型生成/修复/降级记录。需要实际配置或外部条件的项目若无法完成，明确登记缺失，目标保持未完成；不以脚本模型夹具替代真实模型、不把源码自审称为独立验收。最终回执列明实际代码提交、测试结果、产品证据、真实模型/安装包/多入口/无障碍覆盖。

## 当前验证记录

- `ea7e5afd`：Protocol 构建与 runtime-node 依赖链构建通过；材料/事务/状态/Worker 共 26 项测试在 Node 25.9.0 与 Bun 1.4.2 通过。
- `94ef2e92045e651e80fbc5dbb9543ab3b09ef050`：五包依赖链构建通过；Protocol、Runtime Core/SDK/Node 四包 typecheck 通过；`node scripts/check-architecture-governance.mjs` 通过（未以此代称含 UI 的完整 architecture 门禁）。
- 同一代码的定向组合共 109 项 Node 测试通过，覆盖协议/内容、交互运行时、EvidenceIndex 缓存/桌面预览证据、SDK Hook 和真实 Desktop 文件 Provider；runtime-node 全包 1805 项与 runtime-sdk 全包 41 项通过；交互运行时 52 项在 Bun 1.4.2 通过。Node 为 25.9.0，无 skip/cancelled。
- 固定 RC35 normalizer 与已打开追加描述符实测保留原始发布行；丢确认的持久登记不重复追加。同一 wire call ID 跨子会话互不冲突；校验时钟不制造无变化版本，分类提高不会因 unchanged 降级。真实 Node/Desktop 文件读取改写当前源文件后，快照仍为原字节；完整 sideband 不进入序列化事件。
- 最新代码生成的 Bun 单文件校验/求值探针在无 node_modules 的空目录运行，help 与 Worker 求值通过；二进制 62,672,754 字节，SHA-256 `9905092a1ee95fdb0ed125c41ea550d840d898c36627a8ab3bee9c08abbfcfbc`。这是隔离测试探针，不是产品 TUI/CLI 的安装、包体或入口验收。
- 交互 SQLite 当前内部 schema 为 2，内容规范编码为 `peer-interactive-content-1`；早期分支 schema 1 拒绝读写，不做静默迁移或空库重建。该设备本地新子域未在日常产品中启用；现有 Conversation/草稿兼容保护仍待接线。
- 上述均为实现者验证，未做独立审查、完整仓库门禁、真实模型或产品回归，不构成 IUI-00—04 完整交付；最新后续结果随接线补充。
