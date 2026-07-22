# CLI First-Class Release（CLI 与 Desktop 同仓一等发布）

创建时间: 2026-07-20  
最后更新: 2026-07-20（代码已落地：版本门禁 / `--version` / release `build-cli` / Bun env 内联修复）

## Status

**Accepted（阶段一代码已落地）**。

本地已验证：`pnpm --filter @peer-agent/cli build` 成功；`peer --version` / `-v` 输出 `peer 0.0.1-beta.37`；`dist` 与 tar 归档同时含 `peer` + `peer-credential-helper`。  
正式 GitHub Release 资产需下次推 `v*` tag 后由 CI 产出（workflow 已含 `build-cli`）。

## Context

Peer Agent 在 monorepo 中同时存在：

- Desktop：`apps/desktop`（`@peer-agent/desktop`）
- CLI/TUI：`apps/tui`（`@peer-agent/cli`，`private: true`，构建产物 `dist/peer` + `dist/peer-credential-helper`）

二者已共享 Runtime、会话存储与 `~/.peer-agent` 设置，**运行时不互相依赖**。

**落地前**正式发版链路几乎只产出 Desktop：

- 版本门禁不含 `apps/tui`（CLI 曾停在 `0.1.0`）
- `release.yml` 无 Bun / 无 CLI job
- 无稳定 `peer --version`

**落地后（peer_agent 当前代码）：**

- `check-version` / `stamp-version` 含 `apps/tui/package.json`（与 `VERSION` 对齐，例 `0.0.1-beta.37`）
- `release.yml`：`build-cli`（Bun + Rust）→ `peer-darwin-arm64.tar.gz`；`release` needs 含 `build-cli`（关键 CLI 失败阻断）
- `apps/tui/src/cli-version.ts` + `scripts/build-peer.mjs`：`peer --version` / `-v`；Bun 使用 `--env=PEER_CLI_*`，且必须**直接**读取 `process.env.PEER_CLI_VERSION` 才会被 compile 内联
- helper 仍按可执行文件同目录解析

对标 OpenCode（`anomalyco/opencode`，样例 `v1.18.3`）：单仓；同一 Release 同时挂 CLI 平台归档（zip/tar）与 Desktop 安装包；安装通道可另建，但源码不拆仓。

用户问题：只想用 CLI 的人没有正式「下载即用」路径；且若只发 `peer` 不发 helper，干净机器上凭证能力不完整。

## Decision

1. **保持 monorepo**，不拆 CLI / Desktop 为两个 Git 仓库。  
2. **CLI 与 Desktop 同为产品一等入口**：同 git tag、同根 `VERSION` 发版；安装彼此独立。  
3. **数据继续共享** `~/.peer-agent`（会话、设置、凭证）；不为 CLI 单独数据根。  
4. **阶段一交付「可运行 CLI 归档」**，不是裸单文件：  
   - 资产名如 `peer-darwin-arm64.zip`  
   - 内含 `peer` + `peer-credential-helper`（Windows 为 `.exe` 后缀）  
   - 用户解压后两文件保持同目录  
5. **版本门禁**：`check-version` / `stamp-version` 纳入 `apps/tui/package.json`。  
6. **新增** `peer --version`（构建注入版本；不启动 TUI）。  
7. **CI**：在既有 tag 驱动 `release.yml` 上增加 `build-cli`（需 **Bun + Rust**），产物与 Desktop 一并挂到同一 GitHub Release。  
8. **阶段一不做**：brew / npm 公包 / 安装脚本全家桶、CLI 自动更新、Desktop 强制捆绑 CLI、完整 i18n、CLI 正式 Apple 公证、默认 Windows CLI 矩阵。  
9. **签名**：阶段一沿用本地 finalize 的 **ad-hoc** codesign；正式签名与公证后置，与 Desktop 签名阶段可对齐推进。

## Consequences

### 正向

- CLI-only 用户可从正式 Release 获取与 Desktop 对齐的可运行包。  
- 版本号不再长期停在 `0.1.0`。  
- 与 OpenCode「同仓多入口、同 tag 多资产」一致，避免拆仓同步税。  
- 双文件归档避免「下载了 peer 却无凭证 helper」的半残分发。

### 成本与风险

- Release CI 增长：Bun 安装、可能的多 OS CLI matrix、归档步骤。  
- 关键 CLI 平台失败策略需明确：默认建议 **阻断整次 release**，避免假完整发版。  
- mac 未公证时 Gatekeeper 需文档说明。  
- 本地 `publish.sh` 仍可能只覆盖 Desktop，维护者需知「完整 CLI 发版以 CI 为准」（直至脚本补齐）。  
- 二进制体积较大（peer 约数十 MB 级），接受为阶段一成本。

### 明确不采用

| 选项 | 原因 |
| --- | --- |
| 拆双仓 | 共享 Runtime/协议演进成本高 |
| 只上传 `peer` 单文件 | helper 同目录契约被破坏 |
| 阶段一 npm publish `@peer-agent/cli` | `private: true`；原生/打包复杂度高 |
| 阶段一完整安装生态 | 范围膨胀，阻塞「先能发」 |

## 待决策（实现前建议确认）

1. 阶段一 CLI 平台最小集：默认 **仅 darwin-arm64 必出**。  
2. 关键 CLI 构建失败是否 **fail 整个 Release**：默认 **是**。  
3. Windows CLI：默认 **阶段二**。  
4. `SHA256SUMS`：默认 **阶段一.5**。  
5. `peer --version` 输出格式：建议单行 `peer <semver>`。

（产品方案 §10 同步列出；拍板后改 Status 旁注或转 Accepted。）

## Implementation notes（非规范，指向方案）

实现细节、CI 伪步骤、用户旅程与验收清单见：

`design/product/cli-first-class-release.md`

代码仓已触点（摘要，2026-07-20）：

- `scripts/check-version.mjs` / `scripts/stamp-version.mjs` — 纳入 `apps/tui/package.json`
- `.github/workflows/release.yml` — `build-cli` + release 上传 `peer-darwin-arm64.tar.gz`
- `apps/tui/scripts/build-peer.mjs` — `--env=PEER_CLI_*` + 注释（完整变量名不会匹配）
- `apps/tui/src/cli-version.ts` — 模块级 `process.env.PEER_CLI_VERSION` 捕获 + `--version`/`-v`
- `README.md` / `release-notes/TEMPLATE.md` / `release-notes/v0.0.1-beta.37.md` — CLI-only 与双文件约束

### Bun 版本注入踩坑（已修）

1. `--env` 是**前缀通配**：必须 `--env=PEER_CLI_*`，不能写 `--env=PEER_CLI_VERSION`。  
2. 只有**直接** `process.env.PEER_CLI_VERSION` 会被 rewrite；经函数参数 `env.PEER_CLI_VERSION` 读取**不会**内联，编译产物会落到 `0.0.0-dev`。

## References

- 产品方案：`design/product/cli-first-class-release.md`  
- Desktop 发版：`design/product/release-auto-update.md`  
- 代码仓：`VERSION`、`scripts/check-version.mjs`、`scripts/stamp-version.mjs`、`.github/workflows/release.yml`、`apps/tui/package.json`、`apps/tui/scripts/finalize-binary.mjs`、`packages/credential-helper`  
- 对标：https://github.com/anomalyco/opencode （Release 资产同时含 `opencode-<os>-<arch>.zip|.tar.gz` 与 `opencode-desktop-*`）
