# CLI First-Class Release（CLI 与 Desktop 同仓一等发布）

创建时间: 2026-07-20  
最后更新: 2026-07-23（对齐包名与 npm 安装面：`@peer-agent/tui` 构建 vs `@peer-agent/cli` 安装）

## Status

**Accepted（阶段一 + npm 安装面已落地）**。

代码仓 `peer_agent` 当前事实（以仓库为准，示例版本 `0.0.1-beta.41`）：

| 包 / 路径 | npm name | private | 角色 |
|-----------|----------|---------|------|
| `apps/tui` | `@peer-agent/tui` | **true** | CLI/TUI **构建面**：`pnpm --filter @peer-agent/tui build` → `dist/peer` + helper |
| `packages/npm-cli` | `@peer-agent/cli` | **false**（公开） | CLI **安装面**：`npm install -g @peer-agent/cli` → `peer` shim，postinstall 拉 GitHub Release 二进制 |

硬约束（与 `knowledge/architecture/22-tui-desktop-shared-runtime-and-host-governance.md` 一致）：

> 用户可**仅**安装 CLI，**完全不依赖 Desktop 客户端**是否安装。  
> monorepo 源码可暂时共享 Desktop Main 切片（构建时嵌入），**运行时/发布物不得要求 Electron App**。

本地/CI 已具备：

- 版本门禁：`check-version` / `stamp-version` 含 `apps/tui/package.json` 与 `packages/npm-cli/package.json`
- `peer --version` / `-v`（构建注入 `PEER_CLI_*`）
- GitHub Release：`build-cli` 产出平台归档（`peer` + `peer-credential-helper` 同目录）
- npm：`release.yml` 的 `publish-npm` 发布 `@peer-agent/cli`（依赖 Release 资产就绪；`NPM_TOKEN` 未设则跳过 npm，不阻断 GitHub Release）

## Context

Peer Agent 在 monorepo 中同时存在：

- Desktop：`apps/desktop`（`@peer-agent/desktop`）
- CLI/TUI 源码与构建：`apps/tui`（`@peer-agent/tui`，`private: true`）
- CLI 公开 npm 包装：`packages/npm-cli`（`@peer-agent/cli`）

二者（Desktop / CLI）共享 Runtime、会话存储与 `~/.peer-agent` 设置，**运行时不互相依赖**。

**早期阶段一之前**：正式发版几乎只产出 Desktop（版本门禁不含 TUI、无 `build-cli`、无稳定 `peer --version`）。

**阶段一落地后**：同 tag 挂 CLI 归档 + Desktop 安装包；`peer --version` 可用。

**当前（2026-07）**：在阶段一之上增加 **npm 全局安装通道**，用户可：

```bash
npm install -g @peer-agent/cli
peer
```

无需安装或启动 Desktop。包装包从 GitHub Release 下载与 `build-cli` 对齐的平台二进制，而不是把 Electron 打进 npm。

对标 OpenCode：单仓；同一 Release 同时挂 CLI 平台归档与 Desktop 安装包；安装通道可另建，源码不拆仓。

## Decision

1. **保持 monorepo**，不拆 CLI / Desktop 为两个 Git 仓库。  
2. **CLI 与 Desktop 同为产品一等入口**：同 git tag、同根 `VERSION` 发版；**安装彼此独立**。  
3. **数据继续共享** `~/.peer-agent`（会话、设置、凭证）；不为 CLI 单独数据根。  
4. **命名拆分（必须牢记）**：  
   - **构建包** `@peer-agent/tui`：仓库内 private，CI/本地构建 `peer` 可执行文件与 helper。  
   - **安装包** `@peer-agent/cli`：npm 公开包，`bin.peer` → 下载/启动预构建二进制。  
   - **禁止**再写「`apps/tui` 的 package name 是 `@peer-agent/cli`」。  
5. **交付物分两层**：  
   - **Release 归档**（阶段一核心）：如 `peer-darwin-arm64.tar.gz`，内含 `peer` + `peer-credential-helper` 同目录。  
   - **npm 包装**（已落地）：`@peer-agent/cli` 不把巨型二进制塞进 npm tarball，而在 install 时拉取对应 Release 资产。  
6. **版本门禁**：根 `VERSION` 对齐 `apps/tui`、`packages/npm-cli` 与 Desktop 等受管 package。  
7. **CLI 版本查询**：`peer --version` / `-v`（不启动完整 TUI 会话亦可）。  
8. **CI**：tag 驱动 `release.yml` 含 `build-cli`（Bun + 必要工具链）与可选 `publish-npm`。  
9. **阶段一仍可不做**（与 npm 安装面正交）：brew 全家桶、CLI 自动更新、Desktop 强制捆绑 CLI、完整 i18n、CLI 正式 Apple 公证、默认全平台矩阵一次到位。  
10. **签名**：可先 ad-hoc / 后置正式签名；不与「必须先装 Desktop」挂钩。

## Consequences

### 正向

- CLI-only 用户可从 **npm 或 GitHub Release** 获取可运行 CLI，无需 Desktop。  
- Desktop 用户仍走既有安装包；两端可共享 `~/.peer-agent` 数据（可选互通）。  
- 构建失败（`build-cli`）默认阻断整次 Release，避免「桌面发了、CLI silently 缺失」。

### 代价 / 风险

- 必须持续维护 **构建包 vs 安装包** 两套 package 元数据与 stamp 列表。  
- npm 包装依赖 GitHub Release 资产 URL/平台矩阵正确；Release 未就绪时 install 失败信息要清晰。  
- monorepo 内 TUI **源码**仍可能静态 import Desktop Main 切片（构建时嵌入）——这是包边界技术债，**不是**用户安装 Desktop 的运行时依赖。见 `22` 结构风险与 Phase B。

### 明确不采用

| 选项 | 原因 |
| --- | --- |
| 拆双仓 | 共享 Runtime/协议演进成本高 |
| 只上传 `peer` 单文件、不要 helper | helper 同目录契约被破坏 |
| 把 `@peer-agent/tui` 直接 `npm publish` | private 构建面；体积与原生依赖不适合当安装面 |
| 运行时要求先装 Desktop / 连 Electron IPC | 破坏一等 CLI 硬约束 |
| 用 npm 安装 Desktop 客户端代替 CLI | 产品形态错误 |

## 与双宿主架构的关系

- 总览与长期治理：`knowledge/architecture/22-tui-desktop-shared-runtime-and-host-governance.md`  
- 本地能力对齐：`knowledge/architecture/desktop-cli-local-capability-parity.md`  
- Provider 分叉：`knowledge/architecture/tui-desktop-provider-wire-gap-map.md`  

本 ADR **只规范发布与安装面**；共享内核 / 宿主分叉细节以 `22` 为准。

## Implementation notes（摘要，指向代码仓）

- `apps/tui` — `@peer-agent/tui` build → `dist/peer`  
- `packages/npm-cli` — `@peer-agent/cli` publish + postinstall 拉二进制  
- `scripts/check-version.mjs` / `scripts/stamp-version.mjs` — 含 tui + npm-cli  
- `.github/workflows/release.yml` — `build-cli` + `publish-npm`  
- 产品方案（若仍存在）：`design/product/cli-first-class-release.md`

### Bun 版本注入踩坑（历史，已修）

1. `--env` 是前缀通配：必须 `--env=PEER_CLI_*`。  
2. 只有直接 `process.env.PEER_CLI_VERSION` 会被 rewrite；经函数参数读取不会内联。

## References

- 双宿主总览：`knowledge/architecture/22-tui-desktop-shared-runtime-and-host-governance.md`  
- 工程结构：`knowledge/architecture/01-project-structure.md`  
- 版本规范：`knowledge/specifications/06-version-management.md`  
- Desktop 发版：`design/product/release-auto-update.md`（若存在）  
- 代码仓：`VERSION`、`apps/tui`、`packages/npm-cli`、`scripts/check-version.mjs`、`scripts/stamp-version.mjs`、`.github/workflows/release.yml`  
- 对标：https://github.com/anomalyco/opencode  
