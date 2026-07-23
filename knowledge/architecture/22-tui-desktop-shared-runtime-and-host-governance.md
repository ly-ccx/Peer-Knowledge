# TUI 与 Desktop 共享运行时与宿主治理

创建时间：2026-07-23  
最后更新：2026-07-23  
状态：架构总览 / 长期治理基线  
关联代码仓：`peer_agent`（本地 `/Users/liangyin/Documents/DEV/github/peer_agent`）

> **硬约束（发布与依赖）**  
> CLI **必须**可单独通过 npm 安装并独立运行，**完全不依赖 Desktop 客户端**是否安装。  
> 公开安装面：`@peer-agent/cli`（`npm install -g @peer-agent/cli` → `peer`）。  
> monorepo 源码允许为共享内核暂时嵌入 Desktop Main 切片（编译进 `peer` 二进制），但 **运行时/发布物不得要求 Electron 或桌面 App 已安装**。

## 关联文档

- `knowledge/specifications/runtime-sdk-boundary-architecture.md` — Runtime 分层边界
- `knowledge/architecture/20-architecture-governance.md` — 全局架构治理准则
- `knowledge/architecture/desktop-cli-local-capability-parity.md` — 本地能力对齐矩阵
- `knowledge/architecture/tui-desktop-provider-wire-gap-map.md` — Provider wire 分叉映射
- `knowledge/architecture/19-system-prompt-context-architecture.md` — System Context / 提示词组装
- `knowledge/architecture/21-auto-context-compaction-run-resume.md` — 压缩与 run 续接
- `knowledge/specifications/tui-and-hook-design-standard.md` — TUI 与 Hook 设计规范
- `knowledge/specifications/15-goal-plan-lifecycle-governance.md` — Goal 生命周期
- `knowledge/decisions/35-mode-scoped-tool-projection.md` — 模式工具投影
- `knowledge/decisions/37-provider-channel-and-wire-protocol-separation.md` — channel / wire 分离
- `knowledge/decisions/51-unified-desktop-cli-file-tools.md` — 文件工具统一

---

## 1. 一句话结论

Peer Agent 的产品意图是：

```text
同一套 Agent Runtime 内核 + 两个一等宿主（Desktop / CLI·TUI）
```

**不是**「两套独立 Agent」。  
**也不是**「只差工具注入的双前端」。

更精确的现状是：

```text
共享内核（契约、Pipeline、本地能力、会话数据面、Goal 状态机）
  + 宿主分叉适配层（Provider wire、Prompt 组装深度、压缩算法、审批 UX、进程模型）
  + 少量 Desktop-only 能力（可视 browser_*）
```

心智模型：

| 错误记法 | 正确记法 |
|----------|----------|
| 共用 Runtime，只差工具 | **共享内核 + 分叉适配层** |
| TUI 是 Desktop 的精简壳 | TUI 是一等宿主，但部分模块仍寄生 Desktop Main |
| 配置共享 = 行为一致 | 配置可共享，**请求路径 / 组装路径 / 压缩路径**仍可分叉 |
| CLI 是客户端的附属品 | **CLI 可独立 npm 安装**；与 Desktop 是对等宿主，不是插件 |

---

## 2. 治理原则（不可破坏）

延续 `20-architecture-governance.md` 与 `runtime-sdk-boundary-architecture.md`：

```text
Runtime 拥有认知边界
Capability Provider 拥有执行边界
Evidence 拥有事实边界
Prompt Assembly 拥有上下文准入边界
Host 只负责授权交互、环境适配、结果表达
```

主链路（两端必须遵守）：

```text
Capability Provider
  -> Manifest
    -> Runtime Projection
      -> Tool Call
        -> PermissionGrant
          -> Evidence
```

**禁止：**

1. 在 TUI `chat-controller` 或 Desktop renderer 里旁路执行文件 / Shell / 网络
2. 用 UI state 充当 PermissionGrant 或会话事实源
3. 为 CLI 复制一套脱离 Runtime Projection 的“快捷工具”
4. 用 prompt 摘要代替 Tool Result / Evidence
5. 让 Desktop Main 与 packages 形成长期双向依赖环（TUI 可暂时静态嵌入 Desktop 模块，但必须有迁出路线）
6. **让 CLI 运行时依赖 Desktop 客户端已安装**（Electron App、IPC 到桌面主进程、必须先启动 GUI 等）
7. **把仅 Desktop 才能交付的路径写成 CLI 的唯一实现**（除非明确 Desktop-only 能力，如可视 `browser_*`）

---

## 3. 目标分层

```text
@peer-agent/protocol
  跨宿主契约：消息、工具、Goal、Evidence、系统上下文类型

@peer-agent/runtime-core
  Manifest / Projection / Permission / Evidence 纯逻辑

@peer-agent/runtime-sdk
  RuntimePipeline / Session / Hook Port / Device Port

@peer-agent/runtime-node
  Node Provider Bundle：file / shell / hook / 部分 model / web_fetch / batch_search

@peer-agent/conversation-store
  会话落盘、contentRevision、contextSnapshot、request projection

@peer-agent/credential-helper
  凭证与本地安全材料

        │
   ┌────┴────┐
Desktop Adapter              TUI Adapter
apps/desktop                 apps/tui
Electron UI / IPC            OpenTUI / 终端审批
llm-chat-service 编排        chat-controller 编排
完整 Prompt Assembler        轻量 system prompt
LLM compaction 路径          structural compact 路径
multi-wire providers         偏 OpenAI-compatible
browser_*                    web_fetch 等非可视路径
```

### 3.1 包依赖事实（2026-07 代码仓）

**两端共同依赖：**

- `@peer-agent/protocol`
- `@peer-agent/runtime-core`
- `@peer-agent/runtime-sdk`
- `@peer-agent/runtime-node`
- `@peer-agent/conversation-store`
- `@peer-agent/credential-helper`

**Desktop 额外依赖：**

- `@peer-agent/chat-kernel`
- `@peer-agent/ui`
- `@peer-agent/i18n`
- `@peer-agent/task-thread`

**发布面（必须牢记）：**

| 包 / 产物 | 角色 | 是否依赖 Desktop App |
|-----------|------|----------------------|
| `@peer-agent/cli` | 公开 npm 安装器；postinstall 拉 GitHub Release 的 `peer` 二进制 | **否** |
| `apps/tui` → `peer` 二进制 | CLI/TUI 实际可执行文件（`bun --compile` 等） | **否**（可含共享内核源码） |
| Desktop Electron App | GUI 宿主 | 自身即客户端 |

用户可仅执行：

```bash
npm install -g @peer-agent/cli
peer
```

无需安装或启动 Desktop。数据面仍可共用 `~/.peer-agent`（可选互通，不是硬依赖）。

**结构风险：**

TUI 除 packages 外，仍 **静态 import** `apps/desktop/electron/main/` 下多份模块（goal-plan-store、goal-runner、skill/mcp provider、部分 prompt source、data-store）。  
这使 CLI **源码树**嵌入 Desktop Main 切片——**共享更深，边界更糊**。  
注意：这是 **构建时源码耦合**，不是「用户必须装客户端」。长期治理必须把这些模块下沉到真正的 shared package，使 CLI 发布与 Desktop 源码路径解耦，同时保持 **npm 独立安装** 不变。

---

## 4. 分域共享矩阵

评分含义：

- ★★★★★ 契约与实现路径基本统一
- ★★★★☆ 契约统一，实现入口两端各有适配
- ★★★☆☆ 事实面统一，算法 / 管线仍分叉
- ★★☆☆☆ 理念统一，代码入口未统一
- ★☆☆☆☆ 基本不共享

| 维度 | 共享度 | 共用什么 | 分叉什么 |
|------|--------|----------|----------|
| 协议 / 类型 | ★★★★★ | `protocol` | — |
| 工具契约 / 模式投影 | ★★★★☆ | `runtime-core` 契约与 projection | 工具集合、Desktop-only、历史命名漂移 |
| Runtime Pipeline 内核 | ★★★★☆ | `createRuntimePipeline` / Session | 宿主如何喂消息、如何挂 provider |
| Node 本地能力 | ★★★★☆ | file/shell/hook/web_fetch 等 | Shell 任务管理深度、审批 UX |
| 会话存储 | ★★★★☆ | `conversation-store` + `~/.peer-agent` | 宿主读写时机与 UI 同步 |
| 压缩持久化 / 连续性 | ★★★★☆ | `_compaction`、revision、contextSnapshot | — |
| 压缩算法 | ★★☆☆☆ | marker 与恢复语义 | Desktop LLM compact vs TUI structural compact |
| System Context / 提示词 | ★★☆☆☆ | 规范、部分 source | Desktop 完整 assembler vs TUI 轻量拼装 |
| Provider wire | ★★☆☆☆ | `llm-providers.json` 配置 | Desktop multi-wire vs TUI 兼容层压扁 |
| Goal store / runner | ★★★★☆ | goal-plan-store + goal-runner | 宿主 adapter / 面板 / worker 接线 |
| 权限 / Hook 语义 | ★★★★☆ | grant / evidence 语义 | UI 确认交互 |
| UI / 会话渲染 | ★☆☆☆☆ | — | OpenTUI vs Electron React |
| 可视浏览器控制 | — | — | Desktop-only `browser_*` |

---

## 5. 分域详解

### 5.1 运行时

**共用：**

- `runtime-core`：工具契约、模式投影、权限决策合并、Evidence 形状
- `runtime-sdk`：`createRuntimePipeline`、Session 控制器
- `runtime-node`：File / Shell / Interaction / Hook / 部分 Model / 共享本地工具内核

**入口：**

| 宿主 | 入口 |
|------|------|
| TUI | `apps/tui/src/chat-controller.ts` 直接建 pipeline |
| Desktop | `apps/desktop/electron/main/chat-runtime/runtime-pipeline-adapter.mjs` 包一层 `runDesktopRuntimePipeline` |

**分叉：**

| Desktop | TUI |
|---------|-----|
| `llm-chat-service` + 多 provider agent-loop | `provider-chat-model` + runtime-node 兼容层为主 |
| `tool-orchestrator` / `permission-gate` / projected executor | host bundle + 终端审批 |
| 更厚的流式 / UI 事件编排 | 更薄的 controller + OpenTUI 状态 |

**治理要求：**

1. 新能力必须先进入 `runtime-core` 契约与 `runtime-node` provider，再由两端投影
2. 禁止在任一宿主新增第二套 agent loop 语义
3. Desktop 会话编排向 Pipeline 迁移时，不得削弱 TUI 已共用的端口契约

### 5.2 工具投影与本地能力

以 `desktop-cli-local-capability-parity.md` 为准。

**必须共享（非可视语义）：**

- 文件五件套
- `bash` / `shell_stop`
- `batch_search`、`web_fetch`
- Goal：`goal_create_plan` / `goal_update_task` / `goal_get_plan` / `request_explorer`
- `request_user_input`
- Skill / MCP（注册表共享，生命周期可适配）

**Desktop 专属：**

- `browser_navigate` / `browser_click` / `browser_type` / `browser_screenshot` / `browser_read_dom`  
  语义依赖可视 Workbench webview，CLI 不得用无头浏览器冒充

**适配允许：**

- 同一 capability 两端实现路径不同（例：Desktop Shell 任务管理器 vs TUI 前台 shell）
- 结果表达不同（Desktop 卡片 vs TUI 文本时间线）
- 但 **模型看到的工具名、capabilityId、Schema、模式可见性** 必须一致

**治理检查清单（工具变更）：**

1. 是否写入 `SHARED_LOCAL_TOOL_CONTRACTS` 或等价公开契约？
2. 两端 projection 是否同名同 schema？
3. 是否误把 Desktop-only 能力标成共享？
4. 是否出现“摘要支持但未注册可调用”的假能力？

### 5.3 会话、上下文占用与压缩

**共用数据面：**

- `@peer-agent/conversation-store`
- 共享 home：`~/.peer-agent`
- 压缩 marker：`_compaction`
- 连续性字段：`contentRevision`、`contextSnapshot`、request projection

**算法路径分叉（当前允许，但必须接口化）：**

| 宿主 | 压缩实现 | 约束 |
|------|----------|------|
| Desktop | `compaction-coordinator` 可走 LLM 摘要 | 必须写共享 marker / snapshot |
| TUI | `context-compact.ts` 本地结构化压缩 | 不得发明私有恢复格式 |

**目标态：**

```text
CompactionStrategy (interface)
  ├─ LlmSummaryStrategy      (Desktop 默认)
  └─ StructuralStrategy      (TUI 默认 / Desktop 可降级)
        │
        ▼
Shared persistence: marker + revision + contextSnapshot + continuity
```

**治理要求：**

1. 压缩算法可变，**恢复后的会话事实形状不可私有**
2. 首次打开已有会话时，未知占用不得显示伪百分比（见 `contextReady` 一类保护）
3. 压缩失败语义与 run 续接遵循 `21-auto-context-compaction-run-resume.md`

### 5.4 提示词 / System Context

**理念（共用）：**

系统提示词不是一个静态字符串，而是 Runtime 在安全边界内组装的系统上下文。  
见 `19-system-prompt-context-architecture.md`。

**现状：**

| 宿主 | 状态 |
|------|------|
| Desktop | 完整 Prompt Assembler + source registry（identity / workspace / attachments / continuity / project instructions…） |
| TUI | 轻量 `getSystemPrompt` / mode prompt / turn system context；仅复用部分 Desktop source（如 explorer/verifier） |

**目标态：**

```text
packages/* 中的 PromptAssembler + PromptSource
        │
   ┌────┴────┐
Desktop 注入宿主 source      TUI 注入宿主 source
（browser/workbench…）      （cwd/tty/cli flags…）
```

**治理要求：**

1. 新增 system context section 必须先成为共享 source 契约
2. 禁止仅在 Desktop `llm-prompts.mjs` 增加“只有桌面知道”的关键行为指令（除非明确 Desktop-only）
3. TUI 不得长期旁路拼装与 Desktop 冲突的身份/安全基线

### 5.5 Provider / 模型请求路径

核心现状一句话（见 `tui-desktop-provider-wire-gap-map.md`）：

> **配置共享了，请求路径没共享。**

| 层 | 共享？ |
|----|--------|
| `~/.peer-agent/llm-providers.json` | 是 |
| channel / auth 解析 | 部分 |
| wire protocol adapter | 否（Desktop 多 wire；TUI 常压成 OpenAI-compatible） |
| agent-loop 实现 | 否 |

**后果：** 同一模型可能 Desktop 可用、TUI 报兼容层 HTTP 错误——属于架构缺口，不是用户配错。

**治理要求：**

1. 新 provider 必须同时声明 Desktop wire 与 TUI wire，或明确 “TUI unsupported”
2. 禁止只修 Desktop adapter 而让 TUI 静默走错误兼容层
3. 长期：wire 解析与请求执行下沉到 `runtime-node` / 独立 provider 包，宿主只选 channel

### 5.6 Goal

**共用：**

- 磁盘 `goal-plan-store`（计划是 Evidence/artifact）
- `goal-runner` 状态机与 pump
- intake → accepted 闸门
- Goal 工具与 evidence 回写规则

**适配：**

| Desktop | TUI |
|---------|-----|
| 主进程 + IPC + 右侧面板 | `goal-bridge` + `goal-runner-adapter` + 终端侧栏 |
| Explorer/Verifier worker 接线成熟 | worker adapter + 独立 pipeline（需持续对齐） |

**治理要求：**

1. 禁止复制第二套 Goal Runner pump
2. 失败时必须同步 **plan + runner + 活跃叶子任务** 状态（避免 plan failed 而 task 仍 running）
3. 失败默认 **停机给人看**，不静默无限 resume；可恢复错误走显式 resume 策略

---

## 6. 宿主职责边界

### 6.1 Desktop 负责

- Electron 窗口、IPC、preload 契约
- Workbench / 可视 browser 控制
- 完整 Appearance / 多面板 UX
- 与 `chat-kernel` / `task-thread` 绑定的会话表现
- 更深的 LLM compaction 与 multi-wire provider 运营面

### 6.2 TUI / CLI 负责

- OpenTUI 交互、终端主题、键盘 leader / slash command
- 终端审批与紧凑时间线表达
- 单进程启动、打包二进制（`peer`）与 **npm 独立分发**（`@peer-agent/cli`）
- structural compact 与轻量 prompt 路径（在共享契约内）
- 无可视浏览器时的 `web_fetch` 路径
- **无 Desktop 客户端时的完整可用路径**（模型、工具、会话、Goal；Desktop-only 能力除外）

### 6.3 两端都不得负责

- 私自定义“另一套工具权限真相”
- 把 renderer / TUI React state 当 Evidence 库
- 绕过 projection 直接调用本机能力

---

## 7. 当前主要技术债（按风险排序）

| 优先级 | 债务 | 风险 | 目标修复方向 |
|--------|------|------|--------------|
| P0 | Provider wire 分叉 | 同配置两端行为不一致 | wire 下沉 packages；TUI 不再盲目 OpenAI-compatible |
| P0 | TUI **源码**静态依赖 Desktop Main | 包边界崩溃、**发布物与源码树耦合**（注意：不等于运行时依赖 App） | goal/skill/mcp/data-store 迁出 shared package；`peer` 构建不再 import `apps/desktop/**` |
| P0 | 任何使 CLI 必须先装 Desktop 的设计 | 破坏 npm 独立安装硬约束 | 评审直接否决；CLI 路径必须可无 GUI 闭环 |
| P1 | Prompt assembler 仅 Desktop 完整 | 安全/身份指令漂移 | assembler + sources 下沉，宿主只注入环境 source |
| P1 | Compaction 算法双轨无统一接口 | resume/占用口径回归 | Strategy 接口 + 共享 persistence |
| P2 | 工具集合与接线仍有历史缺口 | 假能力 / 不可调用 | 以 parity 矩阵持续契约测试 |
| P2 | Goal worker 接线成熟度不均 | Goal 在 TUI 半失效 | 共用 runner + 对称 worker port |
| P3 | UI 层完全分叉 | 体验不一致但可接受 | 只对齐语义 token 与状态文案，不强行共用组件 |

---

## 8. 长期治理路线图

### Phase A — 止住分叉（1–2 个迭代）

1. **契约测试**：同一工作区 / 同一 mode，两端投影工具名与 schema 快照 diff
2. **Provider 矩阵**：每个 channel 标注 Desktop wire / TUI wire / unsupported
3. **禁止新增** TUI → `apps/desktop/electron/main/*` 的新 import（只准减不准增）
4. **Goal 失败态**：plan/runner/task 三态同步成为硬门禁
5. **CLI 独立发布门禁**：`@peer-agent/cli` postinstall + `peer --version` 在无 Desktop 安装的干净环境可跑通（CI 或发版检查）

### Phase B — 内核下沉（中期）

1. 抽出 `@peer-agent/goal-store` / `@peer-agent/goal-runner`（或并入 runtime 包）
2. 抽出共享 PromptAssembler
3. CompactionStrategy 接口化，两端实现可替换
4. skill/mcp registry 与 provider 彻底离开 Desktop 路径

### Phase C — 宿主变薄（长期）

1. Desktop `llm-chat-service` 退化为 Pipeline + wire 的薄编排
2. TUI `chat-controller` 与 Desktop 共用同一 session/run 状态机语义
3. UI 只做 projection：Token 占用、Goal 面板、审批卡、时间线

完成判据：

```text
同一 conversation-store 记录
  + 同一工具契约投影
  + 同一 provider wire（或显式 unsupported）
  + 同一 prompt 基线
  + 同一 compaction 恢复形状
= 两端可互换继续同一会话（允许 UX 不同）
```

---

## 9. 变更评审问题单

任何跨 Desktop / TUI 的变更，评审至少回答：

1. **落在哪一层？** protocol / runtime-core / runtime-sdk / runtime-node / host adapter / UI
2. **契约是否两端可见？** 还是 Desktop-only / TUI-only？
3. **事实存在哪里？** store / evidence / grant，而不是 React state
4. **是否引入新的 TUI↔Desktop 源码耦合？**
5. **压缩 / resume / 上下文占用口径是否仍一致？**
6. **provider 配置共享后，请求路径是否仍正确？**
7. **失败时 plan / task / runner 是否同步终态？**
8. **CLI 是否仍可无 Desktop 客户端独立安装与运行？**（`@peer-agent/cli` / `peer`）

只要答案依赖“另一端暂时不用”“先在 Desktop 做、TUI 以后再说”或“用户反正会装客户端”且影响共享契约 / CLI 独立发布，就必须升级为显式 ADR 或本文件修订。

---

## 10. 与专项文档的分工

| 文档 | 管什么 | 不管什么 |
|------|--------|----------|
| **本文** | 总览、共享/分叉边界、长期治理优先级 | 单个工具字段细节、单个 wire 的 HTTP 表 |
| `desktop-cli-local-capability-parity.md` | 工具/capability 对齐矩阵与实现切片 | Provider 协议细节 |
| `tui-desktop-provider-wire-gap-map.md` | channel/wire 缺口与现象 | 工具集合 |
| `runtime-sdk-boundary-architecture.md` | 包分层与 Pipeline 边界 | 产品能力清单 |
| `19-system-prompt-context-architecture.md` | Prompt/Context 组装 | 宿主 UI |
| `21-auto-context-compaction-run-resume.md` | 压缩与 run 续接协议 | 工具 parity |
| `20-architecture-governance.md` | 全局不可破坏原则 | 双宿主落地细节 |

发生冲突时：

1. **治理原则**以 `20-architecture-governance.md` 为准  
2. **分层边界**以 `runtime-sdk-boundary-architecture.md` 为准  
3. **双宿主总览与路线**以本文为准  
4. **专项细节**以对应专项文档为准，并回写本文矩阵评分

---

## 11. 代码锚点（便于评审定位）

| 主题 | 主要路径 |
|------|----------|
| TUI pipeline | `apps/tui/src/chat-controller.ts` |
| TUI host / tools | `apps/tui/src/tui-host.ts`, `skill-mcp-bridge.ts`, `goal-bridge.ts` |
| TUI goal runner 接线 | `apps/tui/src/goal-runner-adapter.ts` |
| TUI compact | `apps/tui/src/context-compact.ts` |
| CLI npm 安装面 | `packages/npm-cli`（`@peer-agent/cli` → `peer`） |
| Desktop pipeline 适配 | `apps/desktop/electron/main/chat-runtime/runtime-pipeline-adapter.mjs` |
| Desktop 会话编排 | `apps/desktop/electron/main/llm-chat-service.mjs` |
| Desktop compact | `apps/desktop/electron/main/chat-runtime/compaction-coordinator.mjs` |
| Desktop prompt | `apps/desktop/electron/main/llm-prompts.mjs`, `.../prompt/` |
| Goal store/runner | `apps/desktop/electron/main/goal-plan-store.mjs`, `goal-runner.mjs` |
| 会话存储 | `packages/conversation-store` |
| 运行时内核 | `packages/runtime-core`, `runtime-sdk`, `runtime-node` |

---

## 12. 修订记录

| 日期 | 变更 |
|------|------|
| 2026-07-23 | 初版：汇总共享内核、宿主分叉、专项文档分工与长期治理路线 |
| 2026-07-23 | 硬约束：CLI 可单独 npm 安装、运行时不依赖 Desktop 客户端；区分源码耦合 vs 发布依赖 |

---

## 13. 结语

Desktop 与 TUI 的成功标准不是“UI 一样”，而是：

```text
同一大脑（契约、投影、证据、会话事实、Goal 状态机）
两套皮肤（Electron / OpenTUI）
少量宿主专属器官（browser_* 等）
```

当前阶段允许适配层分叉，但 **不允许分叉侵蚀内核**：  
工具契约、权限真相、Evidence、会话恢复形状、Goal 状态机必须保持单一事实源。  
所有新工作都应推动架构从「共享内核 + 偶然分叉」走向「共享内核 + 显式 adapter」。
