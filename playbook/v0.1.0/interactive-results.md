# ADR 118 交互结果实施与验证

创建时间：2026-11-03
最后更新：2026-11-03

状态：实施中。用户明确要求完整实现并测试 ADR 118；本记录不构成运行时授权或发布认证。

## 范围与依据

完整承接 [ADR 118](../../knowledge/decisions/118-openui-interactive-results-and-runtime-boundaries.md) 的首期 IUI-00—04、IUI-T01—29 及 §22 验收。代码起点为 Peer-Agent `4a58e2846875f85de69915764a127096721c5b0d`（RC35），实施分支 `codex/openui-interactive-results`；知识分支 `codex/openui-interactive-results-adr`。不以单个模块、静态 Demo 或某组测试通过代替完整交付。

本次为 A 级实施：Protocol、受治理 publish/inspect、材料快照、版本与状态存储、Context Source、Desktop 资源区及 TUI/CLI/Remote 文本链需要接线。允许引入 ADR 指定的共享内容包和固定 SDK 依赖，按公开接口、脚本准入和按需加载要求实施。main 仅做必要装配，原 Provider encoder、授权、Evidence 和任务内核保持其权威。

## 实施阶段

| 阶段 | 必须交付 | 当前事实 |
| --- | --- | --- |
| IUI-00 | 固定 SDK 脚本/AST/状态/纯求值与副作用审阅，公共接口验证；材料源、事务及逐存储兼容方案 | 已开始检查固定发布包；尚无退出证明 |
| IUI-01 | Protocol/InteractiveContent/MaterialSource、受治理发布与只读检查、只读 worker 例外、版本 CAS、事务与 Evidence 对账、首次新写入前兼容保护 | 待实现 |
| IUI-02 | Frost 组件、资源引用/会话、状态 CAS/单写者、恢复与冻结条件经原草稿链交回 | 待实现 |
| IUI-03 | 显式 Context Source、预算/修复、按角色能力准入、Bot 引用和固定版本语义核验 | 待实现 |
| IUI-04 | 多入口文本、包体/按需加载、兼容和完整功能验证 | 待实现 |

## 验证与完成标准

用户本次明确授权提前运行测试及产品回归；仅使用隔离临时数据，不读写日常用户资料，不自动安装/重启日常应用。Node 使用仓库要求的版本；完整构建先于依赖 dist 的测试。代码完成后运行适配的完整 build/test/type/architecture/IPC 检查及产品 capture → AI 逐图/交互审阅 → verify，并逐项登记真实结果及限制。未请求发版，不创建版本/RC、tag 或执行发布合并。

验收清单是 ADR §22 的 IUI-T01—29，以及两种实际已配置 Provider 编码路径的真实模型生成/修复/降级记录。需要实际配置或外部条件的项目若无法完成，明确登记缺失，目标保持未完成；不以脚本模型夹具替代真实模型、不把源码自审称为独立验收。最终回执列明实际代码提交、测试结果、产品证据、真实模型/安装包/多入口/无障碍覆盖。

## 当前验证记录

仅完成工作区/代码基线核对和无安装脚本的既有依赖准备；尚未运行实现测试或产品验收。SDK 静态审阅与后续退出证据随实施补充。
