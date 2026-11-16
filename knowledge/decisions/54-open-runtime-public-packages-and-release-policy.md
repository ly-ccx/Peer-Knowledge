# ADR 54：开放 Runtime 公开包与发布策略

> [!NOTE] 2026-11-16 局部取代与退场决定（[ADR 133](133-unified-rust-core-and-dual-host-architecture.md) 方案 B）
> 终局架构已由 [ADR 133](133-unified-rust-core-and-dual-host-architecture.md) 定案为 **Peer Rust Core 单核架构（彻底去除 JS/TS 运行库包）**：
> - `@peer-agent/runtime-core` 与 `@peer-agent/runtime-sdk` 此前已随 `0.1.0-rc.*` 列车发布至 npm，现正式触发下文 **§5「回退条件」**：过渡期仅作遗留兼容维护（禁止扩建 `createRuntimeGoalController` 等旧接口），并在 `1.0.0` 前走显式 deprecation 公告后全面退出公开产品面；**不另行发布或维护“外面包一层 JS 壳 / N-API 调用 Rust Core”的嵌入式 npm Runtime SDK**；
> - npm 长期一等公开包彻底收敛为两项：**`@peer-agent/cli`**（安装/下载原生 Rust `peer` 与 `peer-credential-helper`）与 **`@peer-agent/protocol`**（跨语言契约/Schema 真源）；外部程序集成统一使用 `peer acp` / `peer exec --output-format json` 或 Rust crate。

创建时间：2026-07-24
最后更新：2026-11-16（关联 ADR 133 触发 runtime-core/runtime-sdk 正式退场、不留 JS 薄壳 SDK；原版本 2026-07-24）
状态：Accepted / Implementation in progress  
关联代码仓：`/Users/liangyin/Documents/DEV/github/peer_agent`

## 关联文档

- `knowledge/architecture/22-tui-desktop-shared-runtime-and-host-governance.md`
- `knowledge/specifications/runtime-sdk-boundary-architecture.md`
- `knowledge/specifications/06-version-management.md`
- `knowledge/decisions/48-cli-first-class-release.md`

---

## 1. 背景

npm scope 目前公开存在：

- `@peer-agent/protocol`
- `@peer-agent/runtime-core`
- `@peer-agent/runtime-sdk`
- `@peer-agent/cli`

此前前三个库包以 `0.1.0` 发布，但产品线已经推进到 `0.0.1-beta.N`；monorepo 内部消费者通过 `workspace:*` 使用本地源码，CLI 用户通过 `@peer-agent/cli` 下载预编译 `peer` 二进制，因此公开库没有被产品发布流水线持续更新。

这造成三个问题：

1. npm 页面看起来像正式 SDK，但版本与仓库实际代码不一致；
2. 外部消费者安装到的是旧实现，无法代表当前 Runtime；
3. 缺少“不安装 Desktop/CLI，也能只装库跑宿主”的验收证据。

如果这些库仅为 monorepo 内部复用，它们应当 `private`；既然已经以公开 host-neutral Runtime 定位发布，就必须成为真实、可验证、持续维护的产品面。

---

## 2. 决策

### 2.1 公开产品面

| 包 | 公开 | 角色 | 外部消费者 |
|----|------|------|------------|
| `@peer-agent/protocol` | 是 | 跨宿主消息、工具、Goal、Evidence 等契约与类型 | 自定义宿主、集成层、SDK |
| `@peer-agent/runtime-core` | 是 | Capability / Projection / Permission / Evidence 等 host-neutral 纯逻辑 | 自定义 Runtime、测试与策略层 |
| `@peer-agent/runtime-sdk` | 是 | Runtime SDK、Session Controller、Pipeline 编排端口 | 外部 Node 宿主、IDE/服务集成 |
| `@peer-agent/cli` | 是 | `peer` 产品安装器；下载预编译二进制 | CLI 最终用户 |

### 2.2 非公开产品面

| 包 / 路径 | 公开 | 原因 |
|-----------|------|------|
| `@peer-agent/runtime-node` | **否（private）** | Node 本地能力与宿主适配包含文件、Shell、Hook、Provider 等实现，不是稳定 host-neutral API |
| `@peer-agent/tui` | **否（private）** | CLI/TUI 构建面；对外安装面是 `@peer-agent/cli` |
| `apps/desktop/**` | 否 | Electron 宿主实现，不是可嵌入 SDK |
| `chat-kernel` / `ui` 等 | 暂不公开 | 缺少独立消费契约与外部验收；保持内部 workspace 包 |

### 2.3 版本策略

公开 Runtime 库 **跟随产品根 `VERSION`**，与 Desktop / CLI 同一 release train：

```text
VERSION = 0.0.1-beta.41
@peer-agent/protocol     = 0.0.1-beta.41
@peer-agent/runtime-core = 0.0.1-beta.41
@peer-agent/runtime-sdk  = 0.0.1-beta.41
@peer-agent/cli          = 0.0.1-beta.41
```

理由：

- 当前仍是 beta，API 还在随产品共同演进；独立 semver 会制造无法兑现的兼容承诺；
- 外部用户可以用一个 tag 对应一套已验证的协议 / core / sdk / CLI；
- monorepo `workspace:^` 在 publish 时由 pnpm 重写为同版本 registry 依赖。

稳定性规则：

- `0.0.1-beta.N` 阶段：允许破坏性 API 调整，但必须随 release notes / README 更新；
- 进入 `1.0.0` 前：另开 ADR 定义 public API 稳定级别、deprecation 窗口与独立 major 策略；
- 不允许公开库再次脱离 `VERSION` 单独停在旧版本，除非新 ADR 明确采用独立 semver。

### 2.4 发布顺序

同一 tag 的 npm 发布顺序：

```text
@peer-agent/protocol
  -> @peer-agent/runtime-core
    -> @peer-agent/runtime-sdk
      -> @peer-agent/cli
```

实际依赖关系以 package manifest 为准；顺序采用“基础包先发布，依赖包后发布”。

预发布 dist-tag：

| 版本 | npm tag |
|------|---------|
| `*-alpha.N` | `alpha` |
| `*-beta.N` | `beta` |
| `*-rc.N` | `rc` |
| 稳定版 | `latest` |

### 2.5 发布门禁

发版前必须通过：

1. `scripts/check-version.mjs`：公开库版本与 `VERSION` 一致；
2. `scripts/check-runtime-packages.mjs --contents`：tarball 只含 `dist`、README、LICENSE、package manifest；
3. `scripts/check-runtime-packages.mjs --smoke`：在干净临时目录从打包 tarball 安装并运行外部宿主；
4. `runtime-node` 必须保持 `private: true`；
5. 公开 tarball 不得泄露 `apps/desktop`、源码测试或 host-only 文件。

---

## 3. 外部宿主消费边界

外部宿主只需要：

```bash
npm install @peer-agent/runtime-sdk
```

`runtime-sdk` 会带入它声明的公开依赖；若需要直接使用 capability registry，也可显式安装 `runtime-core`。

宿主负责：

- 实现 provider / local capability 执行端口；
- 给出授权与 blocked execution 结果；
- 选择 UI、存储、模型、文件/Shell 实现。

开放 Runtime 负责：

- 事件与调用契约；
- Runtime SDK execute 生命周期；
- Session / turn 状态机；
- Pipeline 的模型轮次与工具结果回灌顺序；
- host-neutral capability / permission / evidence primitives。

开放 Runtime **不承诺**：

- 自带 Desktop UI；
- 自带 `peer` CLI；
- 自带 Node 文件/Shell 能力；
- 自动读取 `~/.peer-agent`；
- Electron / IPC / Keychain 等宿主设施。

最小示例：代码仓 `examples/external-host`。

---

## 4. CLI / Desktop 的关系

三者是并列产品面：

```text
Open Runtime libraries  → 嵌入自定义宿主
@peer-agent/cli         → 安装 peer CLI 产品
Desktop release         → 安装 Electron GUI 产品
```

它们共享源码与版本，但安装关系不是嵌套：

- CLI 不依赖 Desktop；
- 外部 Runtime 宿主不依赖 CLI 或 Desktop；
- Desktop / TUI 在 monorepo 内可通过 workspace 消费同一 Runtime 源码。

---

## 5. 后果

### 正向

- 公开 npm 包终于与仓库真实 Runtime 同步；
- 外部开发者可只安装库写宿主；
- npm 页面与产品 tag 具有明确对应关系；
- tarball 和 smoke test 防止“包能发但不能用”。

### 成本

- 每次产品发布都要同时维护三个库的 API / README / tarball；
- beta 期间发布频率较高；
- 公开 API 改动必须被当作产品变更，而不是内部重构。

### 回退条件

如果未来确认没有外部 Runtime 产品需求，应另开 ADR：

- deprecate npm 公开库；
- 将包设为 private；
- 保留 monorepo workspace 复用。

不得继续维持“公开但不更新”的中间状态。

> **2026-11-16 执行注记**：上述退场 ADR 条件已由 [ADR 133](133-unified-rust-core-and-dual-host-architecture.md) 正式触发并确认采用干净架构收口（`runtime-core` / `runtime-sdk` 于 `1.0.0` 前完成 deprecation 并退出 npm，不设 JS 薄壳运行库替代层，npm 长期只留 `@peer-agent/cli` 与 `@peer-agent/protocol`）。

---

## 6. 验收

- 公开包 package.json 与根 `VERSION` 一致；
- release workflow 按依赖顺序发布三个库；
- `examples/external-host` 在无 Desktop / CLI 环境运行；
- `runtime-node` 保持 private；
- npm 安装路径与 CLI 安装路径在文档中明确区分。
