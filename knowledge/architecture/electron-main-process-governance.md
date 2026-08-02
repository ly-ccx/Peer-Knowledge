# Electron Main Process 架构治理方案

创建时间：2026-08-01  
最后更新：2026-08-02（实施完成与最终验证）  
状态：治理方案 v2 / 已实施  
关联代码仓：`peer_agent`（本地 `/Users/liangyin/Documents/DEV/github/peer_agent`）  
治理对象：`apps/desktop/electron/main/main.mjs`

## 摘要

当前 `main.mjs` 的底层模块化方向基本正确，但入口层仍同时承担应用装配、Electron 生命周期、安全 IPC、桌面交互和部分共享运行时编排。治理目标不是机械拆文件，而是把它收敛成可读、可测试、可替换的 **Desktop Composition Root**：Electron Main 只保留宿主装配与生命周期，IPC 按领域注册，共享业务流程进入 Runtime/Application Service，协议与 Evidence 继续作为跨宿主事实源。

目标形态：

```text
main.mjs（生命周期 + 装配）
  ├─ composition/create-desktop-host.mjs
  ├─ ipc/register-*.mjs
  ├─ host-adapters/*.mjs
  └─ shared runtime / application services
```

本方案只定义治理，不在知识库中修改代码仓。

## 问题诊断

### problem_rewrite

问题不是“单文件行数难看”，而是 **Electron 宿主组合层的职责边界失焦**：同一入口既创建依赖、管理窗口和生命周期，又直接注册大量 IPC，并承载 Goal/Explorer/Verifier、Runtime Projection、会话恢复等可跨 Desktop/CLI 共享的应用编排。可观察症状是改动扩散、测试依赖源代码文本、入口冲突概率升高，以及双宿主逻辑发生分叉的风险。

### constraints

- Desktop 与 CLI/TUI 是同一 Agent Runtime 的两个一等宿主。
- CLI 必须独立安装和运行，不能依赖 Electron 或 Desktop 安装物。
- IPC 通道名、preload API、参数和返回结构在迁移中默认保持兼容；但补齐 caller-role 授权属于安全收紧，可在 characterization tests 证明合法调用不变后分批启用，不要求保留越权能力。
- Permission、Evidence、会话、Goal 状态机和 Runtime Projection 必须保持单一事实源。
- Electron 专属能力只能停留在 Desktop Host，不得进入共享 packages。
- 迁移必须可分批合并、可回滚，不接受一次性重写。
- 不使用“换文件名”“加注释”“只压行数”等方式掩盖边界问题。

### root_cause_hypotheses

主假设：业务增长持续以“在 `main.mjs` 增加 import、函数和 `ipcMain.handle`”为最低阻力路径，而缺少强制的注册器边界、依赖方向检查、caller-policy 模型和入口预算，最终让组合根变成应用服务容器，并让共享 preload 的能力面大于各窗口实际所需。

证伪方式：如果抽离 IPC 注册后仍必须在 `main.mjs` 中理解并实现领域状态转换，说明根因不只是注册位置，而是共享 Application Service 尚未建立；如果注册器拆出后仍无法明确哪个窗口可调用哪个通道，说明 transport catalog 和受信 window-role registry 尚未形成。两种情况都不能停留在文件搬运。

### source_of_truth

治理后的事实源分别是：

- 工具、参数和结果：protocol/tool contracts；
- 权限：PermissionGrant 与本地受治理执行链；
- 会话、Goal 和 Evidence：共享 store/runtime；
- IPC 通道标识与安全元数据：由唯一的 Desktop IPC channel catalog 导出；registration modules 和 preload 共同消费它，catalog 只描述 transport 名称、方向、owner、允许的 window role、frame/origin policy 与同步语义，不复制 protocol payload schema；
- Renderer 可调用面及 TypeScript 形状：`apps/desktop/electron/preload/preload.cjs` 与 `apps/desktop/renderer/src/preload/contracts/**`；
- Electron 生命周期和窗口实例：Desktop Host context；
- 依赖创建：唯一 composition root。

这里明确区分三类契约，避免再造第二事实源：`@peer-agent/protocol` 管跨宿主领域数据，Desktop channel catalog 管 Electron transport 字符串，preload contract 管 Renderer 暴露 API。三者通过测试校验对应关系，但不得相互复制整套 schema。

### causal_chain

本次改变的链路节点是：

```text
入口预算
  → 依赖装配
  → HostContext
  → 领域 IPC 注册
  → Application Service / Shared Runtime
  → Store / Provider / Local Tool Host
  → Contract / Evidence
  → 架构检查与测试
```

优先修复依赖与调用链，再优化命名和文件组织。

### success_checks

- `main.mjs` 只出现生命周期、装配和注册器调用，不出现领域状态机。
- 一次性迁移 inventory 在迁移前后零丢失；catalog 中每个通道只有一个 registration owner，并具备方向与 caller policy。
- shared packages 不 import `electron`，Desktop adapter 不被 CLI 依赖。
- `pnpm architecture:check`、Desktop tests 和 typecheck 通过。
- Chat、Goal、权限、会话恢复、窗口和更新流程通过 smoke checks。
- 指标按阶段持续下降，而不是在最后一次 PR 才集中达标。

### non_goals

- 不为追求某个行数立即重写整个 Main Process。
- 不改变产品功能、IPC 命名或 renderer 交互。
- 不把所有模块强行搬进 packages；Electron 专属代码继续留在 Desktop。
- 不建立第二套 Goal、Permission、Evidence 或工具执行实现。
- 不以依赖注入框架替代清晰的普通 JavaScript 工厂和显式参数。

## 现状基线

2026-08-01 的只读审计结果：

| 指标 | 当前值 |
|---|---:|
| 物理行 | 4,548 |
| 非空行 | 4,324 |
| 文件大小 | 187,047 bytes |
| import | 80 |
| 本地 import | 67 |
| 顶层具名函数 | 77 |
| 字面量 IPC 通道 | 173 |
| IPC 家族 | 36 |
| 顶层 `ipcMain.handle` | 154 |
| 顶层 `ipcMain.on` | 4 |
| 全文件 `ipcMain.handle` 调用 | 169 |
| 全文件 `ipcMain.on` 调用 | 4 |
| preload 字面量 IPC 操作/唯一通道 | 205 / 205（168 invoke、33 on、3 sendSync、1 send） |
| Main 生产代码子树字面量 outbound send 操作/唯一通道 | 55 / 19（仅作 inventory 基线） |

“158 个顶层直接注册”只用于描述入口形态；治理全量必须以 **173 个 Main 注册调用**（169 handle + 4 on）和 173 个字面量通道为准，不能漏掉 `whenReady` 内缩进注册。IPC 最大家族包括 `llm` 19、`conversations` 18、`mcp` 17、`browser` 14、`goalPlans` 10、`skills` 9、`updater` 7、`chat` 7。数量本身不是错误，但 36 个领域同时在入口注册，说明变更面没有被领域边界隔离。

当前已具备的正确基础：

- Store、Provider Adapter、Chat Runtime、Local Tool Host 等已有独立模块；
- Renderer 没有直接获得 Node/Electron 全能力；
- 主进程仍承担本地能力和安全边界；
- 已有 `architecture:check`、Main 单测、Desktop typecheck 等治理设施；
- `goal-runner.mjs` 本身不 import Electron，并且 TUI 当前已经反向 import 该 Desktop 路径复用 Runner。这说明共享抽取缝已经存在，但物理归属和发布边界仍错误；
- `@peer-agent/runtime-sdk` 已存在 `createRuntimeGoalController()`，但当前 Desktop 没使用它，TUI 主执行路径仍通过 `goal-runner-adapter.ts` 复用 Desktop Runner；抽取前必须先判定二者是收敛、分层还是淘汰关系，禁止再创建第三套 Goal 状态机；
- main、quick-chat、quick-chat-popover 三个窗口均启用 `nodeIntegration: false`、`contextIsolation: true`、`sandbox: true`，这是正确安全基线；但三者共用同一 `preload.cjs`，所以治理还必须补上按受信 window role 的 Main-side caller policy。

主要偏差：

1. **组合根过重**：创建依赖的同时实现运行流程和状态转换。
2. **IPC 注册集中**：新增能力天然倾向继续修改同一文件。
3. **共享代码归属倒置**：TUI 当前有 13 条跨应用 import、分布在 5 个文件（含 tests），直接引用 `goal-runner.mjs`、Goal store/MCP/skill 等 Desktop 源码；虽然复用了实现，却违反 CLI 独立发布边界。
4. **Goal 抽象存在双轨风险**：`runtime-sdk` Goal Controller 与实际共享的 Desktop Goal Runner 同时存在，治理不能只把后者“搬进 package”而不先定义统一语义。
5. **测试耦合源码形态**：至少 6 个 Main 测试直接读取 `main.mjs`，治理脚本也有 3 处直接读取它，阻碍安全搬迁。
6. **Preload 同样集中**：`preload.cjs` 当前 387 行，包含 205 个字面量 IPC 操作/唯一通道；只拆 Main 不治理 transport catalog 和窗口调用权限，会把通道漂移与最小权限风险留在另一侧。
7. **缺少增长预算**：没有自动阻止入口行数、import 和内联 handler 回涨。

## 治理原则

1. **先分职责，再分文件**：只有依赖方向改变才算治理完成。
2. **Host 负责适配，Runtime 负责语义**：Electron 处理窗口、系统权限交互、菜单、托盘、更新和生命周期；共享层处理与 UI 无关的状态机和流程。
3. **IPC 是协议适配器，不是业务层**：handler 只校验、调用服务、转换错误和返回结果。
4. **组合根只创建和连接对象**：不得包含领域算法、持久化细节或长流程。
5. **显式依赖优于隐式全局**：注册器接收最小 capability object，不直接读取庞大模块全局状态。
6. **契约迁移零漂移**：抽离文件不能顺便改变通道语义。
7. **每一步可验证、可回滚**：一个 PR 迁移一个边界，并保留对等测试。

## 目标架构

### 分层模型

```text
┌──────────────────────────────────────────────────────────┐
│ main.mjs                                                 │
│ app lifecycle / create host / register domains / dispose │
└──────────────────────────┬───────────────────────────────┘
                           │
┌──────────────────────────▼───────────────────────────────┐
│ Desktop Composition & Host Context                       │
│ stores, services, windows, adapters, disposer            │
└───────────────┬──────────────────────────┬───────────────┘
                │                          │
┌───────────────▼──────────────┐  ┌────────▼───────────────┐
│ Domain IPC Registrations     │  │ Electron Host Adapters │
│ authorize → validate → call  │  │ window/dialog/menu/... │
└───────────────┬──────────────┘  └────────┬───────────────┘
                │                          │
┌───────────────▼──────────────────────────▼───────────────┐
│ Application Services / Shared Runtime                    │
│ chat, goal, conversation, projection, tool orchestration │
└──────────────────────────┬───────────────────────────────┘
                           │
┌──────────────────────────▼───────────────────────────────┐
│ Contracts / Stores / Providers / Evidence / Permissions  │
└──────────────────────────────────────────────────────────┘
```

### 建议目录

目录名是目标边界示例，可在实施时按现有命名微调；**不预设新建笼统的 `packages/runtime`**。共享逻辑必须先根据现有 package 责任放入 `runtime-core`、`runtime-sdk`、`runtime-node`、`conversation-store`、`task-thread` 等既有边界；只有现有边界都不成立且 ADR 说明发布语义后，才允许新 package。

```text
apps/desktop/electron/
├── main/
│   ├── main.mjs
│   ├── composition/
│   │   ├── create-desktop-host.mjs
│   │   ├── create-desktop-services.mjs
│   │   └── desktop-host-context.mjs
│   ├── ipc/
│   │   ├── register-all.mjs
│   │   ├── register-bootstrap-ipc.mjs
│   │   ├── register-settings-ipc.mjs
│   │   ├── register-workspace-ipc.mjs
│   │   ├── register-conversation-ipc.mjs
│   │   ├── register-chat-ipc.mjs
│   │   ├── register-goal-ipc.mjs
│   │   ├── register-provider-ipc.mjs
│   │   ├── register-mcp-skill-ipc.mjs
│   │   └── register-desktop-system-ipc.mjs
│   ├── host-adapters/
│   │   ├── window-host.mjs
│   │   ├── dialog-host.mjs
│   │   ├── notification-host.mjs
│   │   ├── updater-host.mjs
│   │   └── browser-host.mjs
│   └── ...现有 Electron 专属实现
├── ipc/
│   └── channels.mjs
└── preload/
    ├── preload.source.cjs
    └── preload.cjs          # sandbox-compatible 单文件生成物

packages/
├── runtime-core/          # host-neutral primitives / projection / Evidence
├── runtime-sdk/           # public orchestration and Goal/session contracts
├── runtime-node/          # reusable Node host adapters
├── conversation-store/    # canonical conversation persistence
└── task-thread/           # task/thread domain（仅在语义匹配时承接）
```

`channels.mjs` 是 Desktop 私有 canonical transport catalog，由 Main 直接消费；它不应放入 `@peer-agent/protocol`，避免把 Electron IPC 泄漏为跨宿主领域协议。由于三个窗口均启用 `sandbox: true`，不要假设 sandboxed preload 可在运行时任意 `require` 本地 catalog。推荐在 Desktop 构建前用 bundler/codegen 将 `channels.mjs` 和 `preload.source.cjs` 合成为单文件 `preload.cjs`，并由 CI 检查生成物无漂移。若构建实验确认目标 Electron 版本支持另一种受治理加载方式，可用 ADR 替代，但必须保持 sandbox 和单一事实源。

### 职责矩阵

| 能力 | `main.mjs` | IPC 注册器 | Host Adapter | Shared Runtime / Service |
|---|---|---|---|---|
| `app.whenReady` / quit | 负责 | 禁止 | 可被调用 | 禁止依赖 Electron |
| 创建并连接服务 | 负责调用工厂 | 禁止 | 提供实例 | 提供工厂/服务 |
| Sender/window-role 授权、参数校验与错误映射 | 禁止 | 负责（统一 wrapper） | 提供受信 role registry | 可提供 schema |
| 窗口、托盘、菜单、dialog | 只装配 | 只转发 | 负责 | 禁止 |
| Chat / Goal 状态机 | 禁止 | 只转发 | 禁止 | 负责 |
| Store 持久化语义 | 禁止 | 禁止直接拼流程 | 注入环境路径 | 负责 |
| Permission / Evidence | 禁止复制状态 | 调用统一入口 | 展示授权交互 | 唯一事实源 |
| dispose 顺序 | 负责触发 | 返回 disposer | 负责资源释放 | 提供 disposer |

### 注册器接口

注册器采用显式、可测试接口。每个模块导出静态 `channels` 元数据和 `register*Ipc()`；catalog 是 transport 字符串的唯一来源，注册器元数据负责声明 owner，测试可在不启动 Electron 的情况下聚合注册面：

```js
import { CHANNELS } from '../../ipc/channels.mjs';

export const channels = [CHANNELS.conversations.list];

export function registerConversationIpc({ ipc, conversationService }) {
  ipc.handle(CHANNELS.conversations.list, async (_event, input) =>
    conversationService.list(input));

  return () => {
    ipc.removeHandler(CHANNELS.conversations.list);
  };
}
```

约束：

- 不直接 import `ipcMain`，由 composition 模块注入，以便单测；
- 只接收当前领域所需依赖，禁止把完整 `host` / `serviceContainer` 当成 service locator 传入；
- 返回幂等 disposer，支持测试隔离和应用退出清理；
- channel 常量只来自 Desktop channel catalog；跨宿主 payload/result 类型才来自 `@peer-agent/protocol`；
- 所有 renderer→main 注册默认经过统一 caller-policy wrapper；高权限 handler（文件、Shell、凭据、MCP、Provider OAuth、外部打开、会话导入导出）必须声明允许的 window role；不得信任 payload 或 URL query 自报身份；
- `register-all.mjs` 只聚合注册器和 disposer，不持有业务状态；
- handler 超过约 15 行或直接协调两个以上 stateful services 时，必须评审是否应下沉 Application Service；15 行只作 review signal，不作可通过压行规避的 CI 指标；
- 跨领域事务由 Application Service 编排，不由注册器互相调用。

> 同步 IPC 是显式例外。当前 `settings:get-sync` 和 `browser:start-app-drag` 具有启动/原生拖拽时序语义，迁移时必须保留 `sendSync` / 同步 `ipcMain.on` 行为；不得为了统一成 Promise 而改变调用时序。

### 依赖方向

唯一允许方向：

```text
main entry
  → desktop composition
    → IPC registrations
    → Electron host adapters
    → shared application services
      → contracts / stores / providers / evidence
```

禁止：

- shared package import `electron` 或 Desktop 路径；
- registration module import `main.mjs`；
- adapter 调用 renderer store 作为事实源；
- CLI/TUI import `apps/desktop/**`（现存反向依赖作为待清理基线，不允许新增）；
- 两个注册器通过彼此内部函数形成隐式领域耦合；
- 新增仅在 Desktop Main 存在的共享状态机分支；
- 未经语义 ADR 同时保留 `createRuntimeGoalController()` 与另一套 Goal Runner 状态机并让两个宿主各走一套。

## 分阶段治理路线

### Phase 0：建立可执行迁移护栏

交付：

- 从当前 Main 与 preload 抽取 Desktop 私有 canonical `channels.mjs`；Main 直接消费，preload source 在构建时 bundle/codegen 进 sandbox-compatible 单文件 `preload.cjs`；catalog 只定义 transport/security 元数据，不复制 payload schema；
- 生成一次性的迁移前 channel inventory：至少覆盖 Main 的 173 个入站注册通道、preload 的 205 个操作/唯一通道，以及 Main 生产代码子树当前 19 个唯一字面量 outbound 通道；用于证明迁移零丢失，inventory 是生成式审计产物，不是长期第二份手写清单；
- 建立 owner aggregation test：聚合每个 registration module 导出的 `channels`，检查全量、唯一和无孤儿；
- 将 preload 的调用/监听集合与 catalog、Renderer preload contracts 做一致性检查，并显式区分 Main-only、renderer→main、main→renderer 三种方向；
- 盘点所有使用该 preload 的 BrowserWindow role（至少 main、quick-chat、quick-chat-popover），为每个通道定义允许 caller；注册器通过统一 `authorizeIpcSender(event, policy)` 校验受登记 `webContents`/window role、顶层 frame 和允许 origin，而不是让每个 handler 自己猜；对高权限通道默认只允许 main window 的受信顶层 frame；
- 评估是否按 window role 拆分 preload；若短期保留单一 preload，则必须在 Main 侧强制 caller policy，query 参数不能作为可信身份，window role 必须由 BrowserWindow/webContents registry 赋予；
- 为拥有 preload 的应用窗口建立 navigation/window-open policy：只允许预期 dev origin 或 packaged file/app origin，外链交给受治理 `shell.openExternal`，防止已获 preload 的窗口导航到非受信页面；
- 记录 `main.mjs` 行数、import、顶层 handler 基线；
- 先改造至少 6 个直接读取 `main.mjs` 的 Main 测试，以及治理脚本中 3 处对 `main.mjs` 的源码断言：行为规则迁到 service/registration tests，真正的入口约束才保留入口断言；
- 建立 fake IPC harness，覆盖 `handle/on/removeHandler/removeListener`、重复注册、同步事件和 disposer 幂等性；
- 建立 startup trace，标记 `app.whenReady`、协议/权限初始化、IPC ready、`createWindow`、`ready-to-show`，先得到可重复基线再谈性能阈值；
- 写清 Goal 统一决策：比较现有 `runtime-sdk` Goal Controller、`goal-runner.mjs` 和两个宿主调用面，决定复用层次与迁移终点，禁止边搬边发明第三套抽象。

退出条件：无产品行为变化；catalog 只有一个；所有 renderer→main 通道已有方向和 caller-role policy，统一 sender wrapper 的 allow/deny/unknown-role 测试通过；基线检查进入 CI；6 个源码形态测试和 3 处治理脚本锚点有明确迁移结果；Goal 统一决策通过 ADR/设计评审；后续搬迁不会因测试绑定旧文件位置而失败。

### Phase 1：抽离低耦合 Desktop IPC

先迁移 `updater`、`locale`、`shortcuts`、`appshot`、quick chat、系统窗口类 IPC。这些能力宿主属性明确，适合验证注册器模式。`settings` 虽然领域简单，但含 `settings:get-sync` 启动时序，应在 fake IPC 同步测试就绪后再迁，不作为第一个样板。

退出条件：相关通道集合、方向、同步/异步语义和返回结构不变；注册器具有单测；`main.mjs` 不再出现对应内联 handler；异常发生时能够按领域回滚而不会影响其他注册器。

### Phase 2：按领域拆数据与能力 IPC

迁移 workspace、conversation、provider、MCP、skills、shell/fs 等领域。此阶段不重写现有 service，只把协议适配和现有实现连接起来；发现长 handler 时，先建立 Application Service 再搬迁。`conversations:delete` 这类跨 store 级联必须保持在明确的应用服务/事务边界，不能为了“一个 family 一个文件”而拆散一致性。

退出条件：每个通道恰好属于一个 owner registration module；注册器不直接组合跨 store 事务；同步通道和 event sender allowlist 均被测试；权限和 Evidence 路径无旁路。

### Phase 3：先统一 Goal/Chat 语义，再下沉共享编排

该阶段不是直接把文件从 Desktop 搬进任意 package，而是按以下顺序做纵向切片：

1. 以一条真实 Goal 路径建立 Desktop/TUI characterization fixtures，覆盖 accepted → running → task update → Evidence gate → completed/failed/cancelled/recovery；
2. 采用唯一 GoalPlan 执行链：`createGoalRunner()` 是 Desktop/TUI 共用的唯一 GoalPlan pump；`createRuntimeGoalController()` 只保留为不理解 GoalPlan store、Explorer、Verifier、Evidence gate 和 checkpoint recovery 的低层通用执行原语，不得再由任一产品宿主把它装配成第二条 GoalPlan 路径；
3. 将已经无 Electron import、却被 TUI 反向引用的 `goal-runner.mjs` 及其必要 ports/Node store 实现迁入现有 `@peer-agent/runtime-node`；跨宿主类型和最小接口留在 `@peer-agent/runtime-sdk`，Desktop/TUI 分别注入窗口广播或终端展示、授权交互和 chat runtime ports；
4. 再迁移 Explorer、Verifier、会话恢复、Runtime Projection 和 Chat 生命周期编排；
5. Desktop 只注入窗口通知、授权交互、系统通知等 ports，TUI 注入终端展示/授权 ports。

退出条件：共享服务测试不启动 Electron；TUI 不再为 Goal/Chat 路径 import `apps/desktop/**`；Desktop 与 TUI 使用同一 Goal pump/controller 组合，对同一 fixture 得到一致状态转换和 Evidence 形状；`main.mjs` 不再包含 Goal/Chat 状态机辅助算法。

### Phase 4：收口 Composition Root

建立 `createDesktopHost()` 和统一 `registerAllIpc()`；明确启动顺序、ready gate、dispose 顺序和故障策略。`main.mjs` 最终只完成进程策略、`app` 生命周期、host 创建、窗口启动和退出清理。

目标示意（重点是阶段和 ownership，不要求逐字采用）：

```js
const host = await createDesktopHost({ app, electron });
const disposeIpc = registerAllIpc({
  ipc: ipcMain,
  bootstrap: host.bootstrapApi,
  settings: host.settingsApi,
  conversations: host.conversationApi,
  chat: host.chatApi,
  goals: host.goalApi,
  desktop: host.desktopPorts,
});

await host.start();

app.once('before-quit', async () => {
  disposeIpc();
  await host.dispose();
});
```

实际实现必须定义并测试状态机：`created → registering → started → stopping → stopped`。部分初始化失败时按反序 dispose 已完成步骤；重复 `before-quit`/测试清理不产生二次副作用；`host.start()` 何时创建窗口、何时允许 Renderer 首次 IPC 必须由 startup trace 证明，而不是依赖源码排列猜测。

退出条件：入口可在一次代码评审中完整理解；新增领域能力只修改 catalog、对应注册器/服务和 `register-all` 聚合清单，不修改生命周期入口；所有有状态依赖只有一个 owner，启动失败与正常退出都能完成确定性清理。

### Phase 5：清理兼容层与固化预算

删除临时转发、重复 channel 常量和迁移期 adapter；更新架构图、代码地图及开发模板；把预算与依赖规则升级为 CI 阻断。

退出条件：无双实现、无过期例外、无测试继续绑定旧源码位置。

## 迁移优先级与 PR 粒度

推荐顺序：

1. Desktop channel catalog + 一次性 inventory + fake IPC harness；
2. 修复 6 个 Main 源码形态测试、3 个治理脚本锚点，并建立 startup trace；
3. updater/locale/shortcuts/appshot 等异步低耦合注册器；
4. settings 同步通道、quick chat/window/browser 等时序敏感 Desktop adapter；
5. workspace/conversation；
6. provider/MCP/skills/local tools；
7. Goal 双轨决策及一条 Desktop/TUI 共享纵向切片；
8. chat lifecycle、Explorer/Verifier 和剩余 Goal 迁移；
9. composition root、反向依赖清理和预算固化。

每个 PR 应满足：

- 只迁移一个领域或一个基础设施边界；
- 通道清单前后 diff 为零，除非另有协议 ADR；
- 搬迁与功能修改分开提交；
- 新旧入口不能长期双注册；
- PR 描述列出依赖方向变化、测试证据和回滚点。

## 测试策略

### 静态治理测试

- Desktop channel catalog 与 registration owner 聚合集合一致；一次性 inventory 只用于迁移前后对比，不长期手工维护；
- 通道名唯一，并按 Main-only、renderer→main、main→renderer 声明方向；preload 只能消费批准方向的通道；
- 每个 renderer→main 通道声明允许 caller role、frame/origin policy，所有注册通过同一 sender-policy wrapper；未知 webContents/role、非受信 frame/origin 默认拒绝，高权限通道默认只允许 main window；拥有 preload 的窗口还必须具备 navigation/window-open allowlist；
- preload contract 的方法/事件与 preload source/生成物一致，生成物可复现且 freshness check 通过；跨宿主 payload/result 类型引用 `@peer-agent/protocol`，不在 catalog 重写 schema；
- `main.mjs` 不允许新增直接 `ipcMain.handle/on`；完成 Phase 4 后数量必须为 0；
- shared packages 禁止 import `electron` 和 `apps/desktop`；
- `apps/tui` 不允许新增 `apps/desktop` import，并用递减 allowlist 清除当前存量；
- 注册器禁止 import `main.mjs`，也禁止接收未裁剪的 service container；
- 新增 IPC 必须伴随 owner 元数据、注册器测试、preload 对应检查；只有跨宿主领域契约变化时才要求修改 `@peer-agent/protocol`。

### 单元与契约测试

- fake IPC 测试每个 handler 的注册、输入、输出、错误映射和 dispose，并单独覆盖 `sendSync` / 同步 `ipcMain.on`；
- registration aggregation test 检测重复 owner、漏注册和错误方向；
- Application Service 测试状态转换、幂等、取消、恢复和 Evidence；
- Goal characterization fixtures 同时运行在 Desktop 与 TUI adapters 上，直到二者使用同一 pump/controller；
- Host Adapter 测试 Electron API 调用，不重复测试领域规则；
- Composition lifecycle 测试正常启动、部分启动失败、反序清理、重复 dispose 和 ready gate；
- Desktop 与 CLI 共享 contract fixtures，防止双宿主语义分叉。

### 集成与 Smoke Tests

至少覆盖：

- 冷启动、窗口创建、退出与重启；
- 新建/切换 workspace 和会话；
- Chat streaming、cancel、reattach、restore；
- Goal 执行、Explorer、Verifier、跨重启续传；
- Permission ask/allow/deny 与 Evidence 落盘；
- MCP/skills/provider 配置；
- updater、快捷键、托盘、quick chat 和 browser 宿主能力。

推荐验证命令以代码仓实际 scripts 为准，当前已存在：

```bash
pnpm architecture:check
pnpm --filter @peer-agent/desktop test
pnpm --filter @peer-agent/desktop typecheck
```

## 验收标准

### 架构验收

- `main.mjs` 只保留生命周期、组合根调用、窗口启动和 dispose；不得实现领域状态机。
- 100% Desktop IPC 通道进入唯一 catalog，100% registration owner 唯一；Main-only、renderer→main、main→renderer 方向明确。
- 100% renderer→main 通道有 caller-role + frame/origin policy，并由统一 wrapper 执行；未知/非受信 caller 默认拒绝，高权限通道不向 quick-chat/popover 暴露，拥有 preload 的应用窗口禁止导航到非 allowlist origin。
- 100% `ipcMain.handle/on` 注册调用从 `main.mjs` 移除，包括 `whenReady` 内的缩进注册。
- 每个 IPC 通道有唯一 owner registration module；family 只是命名分组，若一个 family 跨越多个安全/事务边界，可以有多个模块，但 owner 不得重叠；跨领域流程有明确 Application Service。
- shared runtime 对 Electron 的直接依赖为 0；CLI 对 Desktop 源码依赖为 0。
- Chat、Goal、Permission、Evidence 和会话恢复没有 Desktop 私有第二实现。

### 规模预算

行数是趋势指标，不是阶段退出门。原始方案中的 `3,500 / 2,200 / 1,200 / 600` 与 import 固定数缺少按领域盘点的推导，容易诱导压行和空壳搬运，因此二次评审后取消这些预设硬阈值，改为以下可执行预算：

| 指标 | 基线 | 每阶段规则 | 最终规则 |
|---|---:|---|---|
| `main.mjs` 物理行 | 4,548 | 不得高于阶段开始基线；合并阶段后冻结新低水位 | 只保留生命周期/装配；行数仅观察 |
| `main.mjs` 全部 IPC 注册调用 | 173（169 handle + 4 on；其中 158 个在顶层） | 只减不增；迁出的 family 不得回流 | 0 |
| 字面量 Main IPC 通道 | 173 | catalog 覆盖率单调上升 | 100% 来自 catalog |
| registration owner | 0（待建立） | 每迁一通道即获得唯一 owner | 100%，无重复/孤儿 |
| TUI → Desktop 源码 import | 13 条跨应用 import / 5 个 TUI 文件（含 tests） | allowlist 只减不增 | 0 |
| `main.mjs` 源码形态测试锚点 | 6 个 Main tests + 治理脚本 3 处读取 | 行为断言迁出后只减不增 | 仅保留入口自身规则 |

Phase 4 完成后再根据真实 composition root 评审可读性；若仍异常庞大，针对剩余职责治理，而不是先定行数再切文件。任何 CI 规模规则都必须统计语义事件（直接注册、反向依赖、owner 覆盖），不得以 minify、合并行或无语义代理文件规避。

### 质量验收

- `pnpm architecture:check` 通过；
- Desktop Main/renderer tests 通过；
- Desktop typecheck 通过；
- 一次性迁移 inventory 对比为零丢失；catalog/owner/方向/caller policy 检查通过；
- 关键 smoke matrix 全部通过；
- 无新增未登记架构例外；
- 每个迁移 PR 都能独立回滚，不要求数据回滚。

### 性能验收

治理不得引入可感知退化。原始方案直接规定“P50/P95 不劣化超过 5%”，但当前没有固定硬件、样本量、冷/热缓存和噪声处理方法；该数字不可复现，二次评审后不作为 CI 硬门禁。

Phase 0 先建立测量协议：同一机器/构建模式，分别记录冷/热启动，至少 30 次样本，采集 `app.whenReady → IPC ready → createWindow → ready-to-show → bootstrap complete` 各段；workspace/conversation 查询使用固定 fixture。随后：

- 阶段 PR 比较各 segment 的中位数与 P95，并报告绝对毫秒差和百分比；
- 若中位数或 P95 超出基线噪声带（基线重复测量所得），必须定位或登记有期限例外；
- 在建立稳定 CI runner 后，再由测量数据设定数值 SLO；
- IPC 适配层不得增加额外持久化读写或重复服务初始化；
- service factory 在单次 host 生命周期只创建一次有状态实例；
- 启动关键路径中的新增 `await` 必须在 trace 中有名称、owner 和必要性说明。

## 防回退机制

### CI 硬门禁

在 `scripts/check-architecture-governance.mjs` 或独立脚本加入：

1. `main.mjs` 物理行低水位（趋势告警）和直接 IPC 注册硬预算（只减不增，最终为 0）；
2. Desktop channel catalog、owner aggregation、方向、caller-role policy 与 preload 消费的完整性和唯一性，并验证 sandbox preload 生成物 freshness；
3. sender-policy wrapper 覆盖全部 renderer→main 注册，未知/非受信 webContents、frame、origin fail-closed，并对拥有 preload 的窗口执行 navigation/window-open allowlist；
4. shared package 禁止 Electron/Desktop import；
5. `apps/tui` → `apps/desktop` 存量 allowlist 只减不增；
6. registration module 禁止反向 import entrypoint，禁止 service locator 参数；
7. 新增通道必须有 owner、注册器测试和 preload 对应检查；
8. Composition lifecycle 的 partial-failure/dispose tests 必须存在并通过；
9. Goal 统一完成前，禁止新增 Goal controller/pump 实现或扩大两套现有抽象的宿主分叉。

不使用“领域关键词扫描”判断是否存在业务逻辑：它误报高、可轻易改名规避。硬门禁应落在依赖边、注册点、owner、唯一性和行为测试上。预算应单调下降：完成一个 Phase 后冻结新的低水位，不得自动回到旧上限。

### CODEOWNERS 与评审清单

涉及以下路径至少需要一名架构 owner：

- `electron/main/main.mjs`；
- `electron/main/ipc/**`；
- shared runtime/protocol；
- preload 暴露面；
- architecture governance script。

评审必须回答：

- 这是 Electron 专属语义还是共享运行时语义？
- IPC handler 是否统一执行 authorize/validate/call/map，caller role 是否最小化？
- 是否创建了第二事实源或执行旁路？
- CLI/TUI 是否能复用无 UI 语义部分？
- 新通道由哪个 catalog 常量和 registration owner 管理？
- 测试是在验证行为还是绑定源码位置？

### 架构例外

临时例外必须记录：责任人、原因、影响、失效日期、移除条件和跟踪 issue。默认最长 30 天；到期未处理即 CI 失败。禁止使用“先放 main.mjs 以后再拆”但没有期限的例外。

### 变更观测

每次发版记录：

- `main.mjs` 行数/import/IPC 数趋势；
- 各领域注册器的通道数量；
- shared 与 Desktop 的非法依赖数；
- 启动和 bootstrap 延迟；
- Goal/Chat 恢复、权限和 Evidence 相关回归数。

趋势比一次达标更重要；任一指标连续两个迭代反向增长，应暂停新增入口职责并优先偿还。

## 风险与缓解

| 风险 | 表现 | 缓解 |
|---|---|---|
| 只搬文件不改边界 | 注册器仍操纵多个 store | 以依赖数量、跨 store 协调和行为测试触发 service 下沉；行数只作信号 |
| IPC 漂移 | renderer 调用失败 | 单一 catalog、owner aggregation、方向检查和 contract fixtures |
| Catalog 成为第二协议 | channel 文件重复 payload schema | catalog 只存 transport 标识/方向/owner/caller policy，领域类型仍来自 protocol |
| Sandboxed preload 无法加载 catalog | preload 启动失败或退回重复字符串 | 构建时 bundle/codegen 为单文件生成物，CI 做 freshness；不得关闭 sandbox 规避 |
| 窗口越权调用 | quick-chat/popover 通过共享 preload 调用高权限通道 | webContents role registry、统一 sender-policy wrapper、未知 caller 默认拒绝；必要时拆分 preload |
| 同步 IPC 被异步化 | 启动设置或原生拖拽失效 | 单列同步通道并保留 `sendSync`/同步事件测试 |
| 启动顺序改变 | ready 前访问 Electron API | 显式 host lifecycle、startup trace 和 integration test |
| 重复实例 | Store/Runner 状态不一致 | composition root 单例创建，依赖显式传入 |
| dispose 遗漏 | watcher/shortcut 泄漏 | 幂等 disposer、反序清理及 partial-start failure test |
| Goal 双轨扩大 | Desktop/TUI 使用不同 controller/pump | Phase 0 先作统一决策，共享 fixture，禁止第三实现 |
| 双宿主分叉 | Desktop 与 CLI Evidence 不同 | 共享 Application Service 与同一 fixture |
| 大 PR 难回滚 | 功能与重构混合 | 一领域一 PR，搬迁与行为修改分离 |
| 测试阻碍搬迁 | 测试读取 `main.mjs` 字符串 | Phase 0 先将行为断言迁到注册器/服务，入口测试仅验证入口规则 |

## 决策记录

本方案确定以下决策：

1. `main.mjs` 的最终角色是 Desktop Composition Root，而不是 Desktop Application Service。
2. IPC 按领域拆注册模块，但领域语义不留在注册模块。
3. Desktop channel catalog 只管理 transport 标识、方向、owner、caller policy 和同步语义，不复制 `@peer-agent/protocol` 或 preload API schema；sandbox preload 通过构建时 bundle/codegen 消费同一 catalog，不以关闭 sandbox 或复制常量解决加载问题。
4. 所有 renderer→main IPC 必须由 Main 侧基于受信 webContents role、顶层 frame 和允许 origin 做授权；共享 preload 不等于共享权限，query/payload 自报身份不可信。
5. 无 Electron UI 语义的 Chat/Goal/Projection/恢复流程优先进入现有共享 Runtime 边界；是否新建 package 必须另有 ADR。
6. GoalPlan 采用唯一执行链：`@peer-agent/runtime-node` 的共享 `createGoalRunner()` 是唯一 pump；`createRuntimeGoalController()` 仅是低层通用执行原语，不得由 Desktop 或 TUI 装配成并行 GoalPlan 状态机，也禁止第三套实现。GoalPlan store 的跨宿主 contract 进入 `runtime-sdk`，Node 持久化与 checkpoint/recovery adapter 进入 `runtime-node`，宿主只注入 ports。
7. Electron 专属能力通过 Host Adapter 暴露为 ports，不进入 shared packages。
8. 兼容性以 catalog/owner aggregation、sender-policy tests、preload contract tests、双宿主 fixtures 和 Evidence 形状证明。
9. 行数只作趋势信号；直接 IPC 注册、反向依赖和 owner 覆盖才是硬预算。
10. 迁移采用渐进式 strangler 路线，不进行一次性重写。

## 实施结果（2026-08-02）

本方案已在 `peer_agent` 代码仓完成实施，最终事实源如下：

- `apps/desktop/electron/ipc/channels.mjs` 是唯一 Desktop IPC catalog；`apps/desktop/electron/preload/preload.source.cjs` 是 sandbox preload 的可维护源码入口，`apps/desktop/scripts/sync-ipc-catalog.mjs` 负责生成同步；
- `apps/desktop/electron/main/ipc/register-all.mjs` 是唯一 IPC owner aggregation 链，负责 registrar 同步约束、owner 唯一性、启动失败反序回滚和正常退出聚合清理；
- `apps/desktop/electron/main/desktop-composition-root.mjs` 负责命名启动 phase、fatal/optional 语义、反序 rollback、幂等 dispose 和 Electron 生命周期绑定；
- `main.mjs` 的启动顺序固定为 `recovery-and-appearance → local-runtime → desktop-ipc → first-main-window → desktop-affordances → background-work`，确保共享服务先于 registrar 就绪、IPC 先于首个 Renderer 窗口可用；
- `nativeTheme` listener、Local Tool Host runtime-event subscription、Desktop IPC host、首窗、Tray、Shortcut、Quick Chat、Updater、MCP OAuth callback、catalog IPC、trusted-window registry 与 Full Disk Access drag-float controller 均有明确 owner 和清理入口；
- Windows 已下载更新通过 Composition Root 的专用 shutdown continuation 恢复 `quitAndInstall()`；disabled/not-ready 路径保留原 no-op 语义；
- Desktop 与 TUI 共同使用 `@peer-agent/runtime-node` 的共享 Goal/Chat/Explorer/Verifier/Provider 流程，TUI 生产源码不再反向引用 Desktop，shared package 不引入 Electron；
- `scripts/check-architecture-governance.mjs` 的默认 `all` scope 与聚焦 `desktop-main` scope 均能阻止直接 IPC 注册、生命周期回退、phase 顺序回退、关键 owner 遗失和跨宿主反向依赖。

最终验证结果：

- `pnpm -r typecheck`：通过；
- `pnpm --filter @peer-agent/desktop test`：通过；
- `pnpm --filter @peer-agent/runtime-node test`：通过；
- `pnpm --filter @peer-agent/desktop build`：通过；
- `pnpm --filter @peer-agent/runtime-node build`：通过；
- `pnpm --filter @peer-agent/desktop ipc:check`：通过；
- `node scripts/check-architecture-governance.mjs`：通过；
- Composition Root、IPC aggregation、Quick Chat owner 与源码顺序聚焦回归：37/37 通过；
- `git diff --check`：通过。

## 实施完成定义

当以下条件同时满足，Electron Main 治理才算完成：

- 新增普通领域能力不再需要编辑 `main.mjs`，只更新 catalog、聚合清单、对应注册器/服务和测试；
- 入口文件可在一次评审中完整理解启动、注册、失败回滚和退出链路；
- 所有 IPC 有唯一 owner、方向、caller-role policy、契约和行为测试，同步通道语义被显式保留，sandbox preload 生成物可复现；
- TUI/CLI 对 Goal/Chat 等共享流程不再 import `apps/desktop/**`；
- Desktop 与 CLI/TUI 共用无 UI 语义的运行时流程，Goal controller/pump 不存在双轨；
- Permission、Evidence、会话和 Goal 状态仍只有一个事实源；
- CI 能阻止直接注册、反向依赖、owner 缺失和生命周期清理回退；
- 性能有可复现基线，核心产品流程验证无回归。

治理的最终判断不是“文件是否变短”，而是：**Electron 是否只负责成为 Electron，Runtime 是否仍然只有一个。**

## 关联文档

- `knowledge/architecture/00-engineering-philosophy.md`
- `knowledge/architecture/01-project-structure.md`
- `knowledge/architecture/20-architecture-governance.md`
- `knowledge/architecture/22-tui-desktop-shared-runtime-and-host-governance.md`
- `knowledge/architecture/desktop-cli-local-capability-parity.md`
- `knowledge/specifications/runtime-sdk-boundary-architecture.md`
