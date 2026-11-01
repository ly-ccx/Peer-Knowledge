# ADR 117 四工作包：源码实施与自测回执

创建时间：2026-11-01
最后更新：2026-11-01

状态：四包源码实施与自测完成（交付分支；按既有一次文件复测规则完成验证）。架构入口：[ADR 117](../../knowledge/decisions/117-intent-driven-coordination-and-goal-closure.md)；分包顺序与验收标准：[IC-01—IC-04](intent-driven-coordination.md)。

## 授权、候选与交付位置

最初只获授权写方案，之后用户明确要求“按 ADR 117 的四个工作包顺序开始实施，全部完成并且自测完成”。本回执记录该后续任务的实际源码实现与自测；不授权或宣称自动合并、发布、安装、迁移用户数据或重启现有应用。

代码交付分支为 `codex/adr117-intent-coordination`，从已整合开发线 `0f68f281` 建立隔离工作树。四包按顺序独立提交、推送后进入下一包；未在用户当前日常代码工作树实施。知识交付分支为 `codex/bot-intent-coordination-plan`。

| 工作包 | 代码提交 | 交付 |
| --- | --- | --- |
| IC-01 | `420d90f0` | Protocol、纯 intent kernel、journal/reducer/派生索引与门槛 8 |
| IC-02 | `ab84f7e8` | 原 coordinate_work 判断、阶段持续承接、根覆盖核验与唯一关闭 |
| IC-03 | `35aa41fd` | 分列交付/签收、局部补偿、公平调度、work/Provider/宿主故障隔离 |
| IC-04 | `3c7ef152` | 有界 DecisionFrame、统一进展事实、真实回复绑定及四包组合恢复 |

最终代码提交：[`3c7ef152`](https://github.com/ly-ccx/Peer-Agent/commit/3c7ef1526d197855a8667122bc52ab3f02ebe998)，已推送交付分支；源码 tree：`2651c23d36ccc42ecd724697750df44152244284`。包间提交是串行实施证据，不是独立部署版本或活跃格式 8 数据的降级目标。

## 实际验证

环境：macOS、Node 25.9.0、pnpm 10.22.0；构建使用当前依赖与本机 Rust/Bun 工具链。所有执行在隔离代码工作树进行，生产对话、任务、设置及运行实例未重置。TUI 用例最初经原通用编码器生成过测试工具缓存；已清理确认属于本次 fixture 的缓存，并在该用例设置/恢复 `PEER_AGENT_HOME`，使后续材料化与临时数据根一起隔离清理。

| 命令 / 范围 | 本候选结果 |
| --- | --- |
| `pnpm build` | 通过；包含全部 workspace、Desktop、凭据 helper 和 TUI 的本地构建，不是安装包验收 |
| `pnpm typecheck` | 通过 |
| `pnpm architecture:check` | 通过，含 UI SVG/radius 约束 |
| 恢复扫描/责任/意图组合阶段复核 | 32 项通过、0 失败、0 取消；此后继续补强原生续接，最终由 runtime-node 全套再次覆盖 |
| `pnpm test` | 首跑退出 1：Desktop 一项凭据 helper 超时；其余已执行用例无失败。按仓库 CI 规则只重跑失败文件一次，通过；被短路的后续脚本全部补跑，具体分项如下 |
| 原生 yield / 意图与实际回复绑定组合复核 | 14 项通过，含匹配模型延续判断、模型切换/身份缺失拒绝承接 |
| TUI 实际委托组合定向复核 | 1 项通过，含真实本地文件/Evidence、一次根复核和实际 fulfilled；最终 TUI 817 项整包回归再次通过 |
| 源码、生成产物与 staged diff 审阅 | 通过；提交 tree 与上述冻结 tree 一致，非独立审阅 |

最终候选分项结果：

| 范围 | 实际报告 |
| --- | --- |
| UI convention 脚本 | 8 通过 |
| credential-helper / npm-cli / Protocol | 分别 10 / 20 / 311 通过 |
| chat-kernel / runtime-core / conversation-store | 分别 27 / 144 / 111 通过 |
| gateway / task-thread / system-context / runtime-sdk | 分别 209 / 1 / 46 / 41 通过 |
| runtime-node | 1,674 通过，0 失败，0 取消，0 跳过 |
| TUI | 817 通过，0 失败；包括实际委托闭环组合 |
| Desktop 主批 | 6,134 项：6,128 通过、1 失败、0 取消、5 跳过；IPC 检查已先通过 |
| Desktop 失败文件一次复测 | `node --test apps/desktop/electron/main/input-prediction/credential-resolver.test.mjs`：1 通过；初次错误为 `CREDENTIAL_UNAVAILABLE:credential_helper_timeout`，文件不属于本次改动 |
| Desktop 被短路的末批 | `node --test apps/desktop/scripts/check-project-agent-i18n.test.mjs apps/desktop/scripts/bot-cancel-fixture.test.mjs`：3 通过 |
| 根脚本补跑 | `pnpm marketplace:test` 6 通过；`pnpm changelog:test` 27 通过；`pnpm upgrade:test` 1 通过 |

原始 `pnpm test` 命令本身未绿，不把独立复测后的结果改写成“首跑全过”。复测遵循当前 `.github/workflows/ci.yml` / AGENTS 的失败文件一次重跑规则，没有改宽超时或删除断言。Desktop 报告的跳过包括主题/键盘、隔离 Electron、已替代的 ADR42 行为及不需要后续 text-verifier 的 completed-plan 组合；这不构成产品截图或交互验收。升级项是源码 tagged upgrade/downgrade/recovery/updater 矩阵，不能替代已安装应用或真实用户数据的升级验收。

首次全量测试在 runtime-node 的 1,674 项中出现 6 项失败，未将其称为通过：新增 Bot 归属校验使缺少明确归属的旧测试样本不再可领取；pending 选择还在无事件时读取 roster。补齐样本归属并保持运行时校验后，组合复核又发现普通历史交付无条件读取聚合账本，修正为仅有真实 digest 引用时读取。上述 32 项复核通过。后续发现旧时序用例的 150 ms 竞争断言失败，独立文件复测 9 项通过；TUI 全量用例还暴露实际原生模型身份与跨 yield 判断承接缺口，已在原恢复 seam 修正，并使组合用例证明一次根复核和真实 fulfilled。相应最终候选重新构建并验证，不把早期快照结果当作最终通过，也没有用重跑掩盖断言失败。

## 验收故事与证据覆盖

以下均为生产 Module 配合受控模型/宿主 port 的确定性用例；不等于真实模型语义能力或发布产品验收。

| 故事 | 实际可证明的行为 | 主要用例（相对 Peer-Agent） |
| --- | --- | --- |
| A1 / A8 阶段签收与根责任 | 调查 accepted 后根仍 active；持久 continue 在没有新用户输入/事件时承接下一阶段；实际交付、原目标核验和无未决义务后唯一关闭；重建不重复关闭 | `packages/runtime-node/src/project-agent/intent-lifecycle.test.mjs` |
| A2 讨论及限制 | 轻量讨论不创建 mandate/GoalPlan；无子任务 work 也可查询；原有能力和授权规则仍控制执行。对自然语言“不改代码”的理解质量仍需真实模型验证 | `intent-lifecycle.test.mjs`、原 delegation/Runner 用例 |
| A3 修订与多目标 | 当前 canonical 输入可修订原 work；局部失败后保留原责任，不恢复已完成阶段的 native checkpoint；同一真实回复对两个明确根分别绑定/CAS，不扩大子任务归属；旧 goal 回复不关闭新目标 | `intent-lifecycle.test.mjs`、`intent-reply-bindings.test.mjs` |
| A4 问题及人工门 | 保留原双向监督/人工门；伪造 wait 被拒，真实用户请求按事实等待；模型不能虚构物理故障或借用其他 work 故障；无方法可用保留 active 的语义阻塞 | 原监督/恢复用例、`intent-lifecycle.test.mjs` |
| A5 交付隔离 | canonical/签收/综合回执分开；签收抛错或一直不返回期间实际 Runner 仍准入独立输入；同 work 保序、跨 work 推进、稳定重试/退避、单一在途回调；暂存小结不冒充已公开交付 | `delivery-isolation.test.mjs`、`intent-lifecycle.test.mjs` |
| A6 进展与故障范围 | reason/随机回执/请求 ID 不刷新失败；只有宿主返回的实际对象身份参与进展；单 work 失败不熔断其他目标，渠道 B 成功不抹去渠道 A 的故障；原预算与无默认累计上限保留 | `decision-frame.test.mjs`、`reply-failure-facts.test.mjs`、原 continuation/watchdog/熔断用例 |
| A7 中断、迟到及归属 | canonical/acceptance/settled 与 digest hold 两侧故障注入；重启按原幂等回调读取事实补偿，不重放 Worker；来源失效后根责任保留；共享 workspace 不领取其他 Bot 的工作/输入/事件/重试/交付 | `delivery-isolation.test.mjs`、`intent-lifecycle.test.mjs`、原存储恢复用例 |
| A9 事实视图与回查 | 24 KB UTF-8 上限、当前事件的旧目标优先、错误/真实问题/unknown/拒绝原因保留；秘密/私有字段及跨 Bot 排除；session、129 条输入处置及 canonical 长文本分页；历史读取不造新授权 | `decision-frame.test.mjs`、`intent-lifecycle.test.mjs`、`packages/system-context/src/sources/project-roster-source.test.mjs` |
| A10 版本与重建 | 来源、双 CAS、幂等冲突、字段顺序无关摘要、真实交付证明；丢索引/manifest 后门槛不降；旧 writer 拒写；显式拒绝未集成的格式 7 | `intent-coordination-kernel.test.mjs`、原 coordination-v2 用例 |

TUI 组合入口为 `apps/tui/src/project-agent/tui-project-host.test.ts`，受控 Provider 配合真实本地能力、Evidence、核验和宿主签收；不对真实网络模型的意图理解质量作推断。

表中未写完整路径的文件均在 `packages/runtime-node/src/project-agent/`。完整命令会运行原工程回归；表格只列直接定位入口，不将一个新增断言扩大为所有产品故事均已真实体验验收。

## 接口、兼容与剩余整合边界

- 原 Provider → Manifest → Runtime Projection → Tool Call → PermissionGrant → Evidence 链保留；模型判断、公开文本和 Context 不成为权限/Evidence。宿主对来源、版本和闭环事实校验，语义正确性仍需模型验证。
- 不新增任务/意图/交付数据库或本机目录。新事实沿原 coordination-v2 journal/blob 与派生 bucket；L1 稳定规则、L7 有界事实，未新增系统注入入口。
- 格式 8 是本完整特性的门槛，支持既有 2–6 与 8；ADR116 在途格式 7 的 reducer、Session Control/资源账本尚未集成。资源 wait 明确返回 Adapter 不可用；后续合并必须整合正式接口，不能按数字推定兼容。
- 包间旧提交不得接管格式 8 活跃责任；回滚不得删除字段或降低 durable head/manifest 门槛。待交付/unknown/原始 Evidence 历史保持。
- 暂存小结沿既有队列与定时器，引用由 journal 原件核对。已知跨 Bot 聚合保留待办并返回 scope conflict；未实现跨 Bot 责任迁移或完整多 Bot 聚合重设计。

## 未执行与审阅边界

自测为实现者自审，**没有独立审阅**。未发起真实模型请求，未进行安装版/用户现有运行实例验证、产品截图/交互包、跨平台、辅助技术或发布升级验收。构建产生本地 Desktop/TUI/helper 产物和签名，不等于安装或已发布。

四包源码与上述自测已交付，可审阅；真实模型语义故事、安装/升级和最终组合发布门禁仍须单独执行。当前未合并发布分支，未创建版本/tag；未因本任务清理其他工作树或把他人未提交改动纳入交付。下一次版本/RC 仍按 AGENTS 清点合入全部开放 PR，在最终组合候选重新跑完整检查和产品回归；本回执不替代该门禁。
