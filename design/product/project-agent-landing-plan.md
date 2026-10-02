# 项目代理落地计划

创建时间：2026-09-25
最后更新：2026-09-26

2026-10-02 当前交付补记：Beta1–5已实现，RC1及RC2已预发布。PR99–104均通过两平台CI并合入；rc.2固定be65fb73，Release36960577284全成功。20项源码矩阵、完整回归、9壳/11可访问性/7诊断通过；实际macOS签名公证、六次安装轮换、归档与npm CLI默认助手读文件/回复通过。多入口复验通过（实际安装Desktop＋源码TUI后端＋本机远程网关夹具，非实体手机/生产OIDC）；严格安装双任务仍失败。Astra两文件和新鲜证据正确，A因计划拆分及缺批准历史被核验拒绝，未签收/合回；批准事实补修中。GPT61机器人仍空响应，尚未Ready。GA仍等负责人195用例、6流程、七天日用及明确批准。 [RC自测报告](../../playbook/v0.1.0/rc-self-test-report.md)记录证据与边界。下文保留历史设计。

> **2026-09-26 起，版本节奏与任务卡以 `design/product/v0.1.0-release-plan.md` 和 `playbook/v0.1.0/` 为准。** 用户决定把整套落地做成 0.1.0 大版本（开发线 `PeerAgent/dev/0.1.0`，中途发 `0.1.0-beta.N`），范围扩大到原第 4、5 阶段全部内容。本文保留阶段划分的思路与风险分析作为背景；下文「阶段」表中的 0.0.19–0.0.26 版本号、§1 的代码事实（32 个在制文件、已知失败）与 §3 的 PR 清单均已过时，不再作为执行依据。

> 状态：计划（随发版修订）；不是发布认证，也不批准 ADR 80–84 以外的新能力或权限  
> 覆盖决策：ADR 80（项目代理委托模型）、81（记忆体系）、82（项目目标与定时 / 事件驱动）、83（模型分工）、84（机器人列表壳）  
> 执行手册（派给其他模型时必须遵守）：`playbook/project-agent-implementation-handbook.md`  
> 关联：`project-agent-workbench.md`（产品稿与 demo）、`knowledge/architecture/project-agent-capability-layers.md`（M / MM / OB 步骤）、`peer-product-roadmap.md` 中景 #0、`peer-transformation-charter.md` 阶段 F、`peer-delivery-status.md` D10  
> 代码基线：`PeerAgent/dev/0.0.18` 的 `f12e15d8`，`VERSION=0.0.17`，工作区另有 32 个未提交文件（自动更新、引用消息等 0.0.18 在制改动）

---

## 0. 结论

先地基、后壳层；全程功能开关；每个版本都可正常发布。第一块地基是执行宿主去掉窗口依赖（M2，B 级，可以不等 ADR 评审先做）；项目代理本身（第 2 阶段起）要等 ADR 80–84 转 Accepted 后再开工。节奏按版本排：每个阶段占 1–2 个版本。

---

## 1. 决定节奏的代码事实

| 事实 | 位置 | 对节奏的影响 |
|---|---|---|
| 当前开发线有 32 个未提交文件，改到 `main.mjs` | `PeerAgent/dev/0.0.18` 工作区 | 0.0.18 先收口发版，重构从干净的 dev 拉分支，避免互相踩 |
| 后台 Goal 回合要拿主窗口，没窗口直接 blocked | `main.mjs` `getRunnerWebContents()`、`runGoalTurn` | 项目代理的后台推进依赖「不依赖窗口」，M2 是第一块地基 |
| Explorer / Verifier 各自伪造 `webContents` | `main.mjs` `createCollectingWebContents()` | 收拢成 `TurnSink`，否则第四、五套执行入口会继续复制 |
| 大文件：`main.mjs` 4232 行、`ChatSurface.tsx` 3305 行、`llm-chat-service.mjs` 2029 行，`sendMessage` 二十多个参数 | 同左 | 新逻辑进新模块（application service / `ProjectAgentSurface` / TurnExecutor 包装），不再往里加 |
| Goal Runner 与 Automation 调度器已在 `runtime-node`，TUI 共用 Goal Runner | `packages/runtime-node/src/goal-runner.mjs`、`automation-scheduler.mjs`、`apps/tui/src/goal-runner-adapter.ts` | 调度与编排可以直接复用；OB1 的共享 Scheduler 成本低 |
| 划词子会话已有 `parentConversationId` 与继承背景快照 | `packages/conversation-store` | 「带快照的子会话」原语可以抽出复用 |
| 模型按会话绑定，子 agent 继承；视觉复核不能看图时直接报错 | `conversation-model-binding.mjs`、`desktop-visual-review.mjs` | M2.1 模型分工与 M2 同批做，顺带修掉视觉复核报错 |
| 工作区按路径识别，没有稳定 id | `workspace-application-service.mjs` | 记忆、目标、项目代理都要挂在稳定 `workspaceId` 上，第 1 阶段补 |
| 已有开发者设置 IPC | `register-settings-ipc.mjs` `developer-settings:*` | 功能开关 `projectAgentMode` 挂这里，不另造机制 |
| 仓库记录的已知失败：desktop 5 个测试、`protocol` 1 个类型错误、`architecture:check` 2 处 | 代码仓 `AGENTS.md` | 大重构前先修掉或隔离，保证回归基线干净 |
| 发版密度：0.0.13–0.0.17 约两周 5 版 | git 记录 | 以版本为节拍，而不是以周为节拍 |

---

## 2. 阶段

| 阶段 | 版本 | 内容（步骤编号见分层文档 §12） | 用户感知 | 进入条件 |
|---|---|---|---|---|
| **0 收口** | 0.0.18 | 收口在制改动并发版；ADR 80–84 待评审点过一遍并转 Accepted；已知失败修掉或隔离 | 无 | — |
| **1 地基** | 0.0.19 | M2 执行宿主；M2.1 模型分工核心与设置页；M1 协议契约与纯函数；稳定 `workspaceId`；开关 `projectAgentMode` | 关掉窗口后台任务照跑；视觉复核自动选能看图的模型；可以配置模型分工 | 阶段 0 完成（M2 本身是 B 级，可先行） |
| **2 骨架**（开关后） | 0.0.20–0.0.21 | M3 派发；M4 通讯；M5 编排；验证结论与策略签收；MM1 记忆存储与「记住」；首次「熟悉项目」；机器人列表、对话与按需滑出的档案；新建机器人（绑定文件夹 / 受管文件夹） | 开关打开后内部使用 | ADR 80、81、83、84 Accepted |
| **3 可日用** | 0.0.22–0.0.23 | M6 需要你冒泡、插话、引用限定范围、按需披露、追加核验；M5.1 主动性与今日小结；MM2–MM3 记忆进上下文与自动提取；M8 基础（失败唤醒、停滞检测） | 可以作为 beta 开放 | 阶段 2 在真实项目上跑满一个版本周期 |
| **4 并行与主动** | 0.0.24–0.0.25 | M7 槽位、优先级、依赖、取代与恢复、自动 worktree；OB1–OB3 项目目标；M8 熔断与重启恢复；MM4 记忆过期与冲突 | beta | ADR 82 Accepted |
| **5 默认开启** | 0.0.26 起 | 旧工作区迁移为机器人、旧会话归为历史任务；旧侧栏与工作台页面退场；代理输入框退掉模式切换器；TUI 与远程入口接入项目代理；MM5、M9 | 全量 | 阶段 3–4 的验收证据齐全 |

关键路径：M2 → M3 → M5（骨架跑通）。MM1 必须进第 2 阶段，因为「熟悉项目」要写记忆。TUI 在第 5 阶段前保持现有任务模式，运行时都放在 `runtime-node`，届时直接复用。

---

## 3. 第 1 阶段 PR 清单

每个 PR 可单独合入、单独回退。

| # | 内容 | 退出条件 |
|---|---|---|
| PR1 | 抽出 `TurnSink` 接口与 `CollectingSink`，Explorer / Verifier 迁过去 | 纯重构；Explorer / Verifier / 视觉复核相关测试全绿 |
| PR2 | `BroadcastSink`；`runGoalTurn` 不再依赖窗口 | 新增测试：关闭所有窗口 Goal Runner 仍推进；打开窗口后按 ADR 22 重连流 |
| PR3 | Goal Runner 装配从 `main.mjs` 移到独立宿主服务 | `main.mjs` 行数下降；Goal / Automation 回归全绿 |
| PR4 | 稳定 `workspaceId`：工作区设置生成与迁移，远程访问复用 | 改名 / 换路径后 id 不变；旧数据迁移测试 |
| PR5 | `protocol/delegation.ts` 与新 `memory.ts`（替换旧遗留类型）；纯函数 `projectWorkSession`、`decideAcceptance`、`decideSurfacing`、`computeVerificationVerdict`、`projectMessageDispositions` | 只有类型与纯函数和单测，不接线 |
| PR6 | ModelRouter 核心：Explorer / Verifier / 视觉复核按角色解析；用量账本加角色维度 | 只有一个模型时行为与今天一致；视觉复核不再因任务模型不能看图而失败；不同源复核测试 |
| PR7 | 「模型分工」设置页（档位 + 角色 + 项目范围） | 设置读写走 main；renderer 不持有真值 |
| PR8 | 开发者开关 `projectAgentMode` | 默认关；关闭时界面与行为完全不变 |

---

## 4. 每个 PR 都守的规矩

1. 按 ADR 里的测试清单补测试；跑 `architecture:check`；Goal、Automation、划词子会话的回归保持全绿。
2. `main.mjs`、`ChatSurface.tsx`、`sendMessage` 参数表不再扩张：主进程新逻辑进 application service，界面新逻辑进 `ProjectAgentSurface` 等新模块，执行参数由 TurnExecutor 与角色画像包起来。
3. 所有调度、记忆、目标能力走 Capability Provider → Manifest → Runtime Projection → Tool Call → PermissionGrant → Evidence，不另开执行通道。
4. 第 5 阶段前旧壳原样可用；开关关闭即回到旧行为，出问题随时回退。
5. 分级流程：B 级（M2）可先行；A 级部分（第 2 阶段起）在对应 ADR 转 Accepted 后开工，边界若有变化先回写 ADR。
6. 本地 commit 同一轮 push（两个仓库都一样）。

---

## 5. 每阶段的验收证据

沿用交付状态清单的口径：代码存在 ≠ 进入开发线 ≠ 真实验收通过 ≠ 对外发布。

| 阶段 | 必须留下的证据 |
|---|---|
| 1 | 关窗口后台推进的测试与一次真实运行记录；单模型行为不变的回归；视觉复核自动选模型的一次真实截图复核 |
| 2 | 在真实项目上：一句话 → 锚定开任务 → 策略代签汇报；「熟悉项目」写入的记忆可查、可撤；代理全程无法写文件的测试 |
| 3 | 插话并入 / 停止、引用越界拒绝、按需披露到证据、主动性档位切换后的送达差异；记忆自动提取与防注入用例 |
| 4 | 三条任务并行互不污染工作区；取代后恢复原任务；目标触发只在变化时上报；重启恢复顺序的集成测试 |
| 5 | 老用户升级迁移（历史任务可见且未改写）；TUI 与远程入口走同一套运行时；一版以上 beta 反馈闭环 |

---

## 6. 风险

| 风险 | 应对 |
|---|---|
| 0.0.18 在制改动与重构冲突 | 阶段 0 先收口；重构从干净的 dev 拉分支 |
| 已知失败测试掩盖回归 | 阶段 0 修掉或显式隔离并记录 |
| 调用次数增加导致成本上升（代理 + 任务 + 后台） | 模型分工随第 1 阶段落地，代理与后台默认用快 / 省档；用量按角色记账 |
| 新界面与旧壳并存期的维护成本 | 新界面独立模块，旧壳只修 bug 不加功能；第 5 阶段一次性切换 |
| 本地 JSONL（收件箱、记忆）在长期使用后变慢 | SQLite 索引可重建；阶段 3 起观察体积与检索耗时 |

---

## 7. 回写规则

- 每发一版：更新本文「阶段」表的实际版本与完成情况；交付状态清单 D10 同步分类（未实现 / 未集成 / 未验收）。
- 某阶段顺序或范围变了：先改本文与分层文档 §12，再动代码。
- ADR 转 Accepted：在本文进入条件里勾掉，并在路线图中景 #0 更新状态。
