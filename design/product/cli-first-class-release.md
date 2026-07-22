# CLI 一等发布方案（Desktop 与 CLI 同仓、同版本、安装独立）

创建时间: 2026-07-20  
最后更新: 2026-07-20（**阶段一代码已落地**；补 Bun env 前缀通配 + 直接 `process.env` 内联修复）

> 阶段一目标：让「只想用 CLI、不想装客户端」的用户，能从正式 Release 拿到与 Desktop 同版本的 **可运行 CLI 包**，而不必 clone 源码自建。  
> 代码改动落地在 `peer_agent`；本文为方案与验收边界，并回写实现状态。  
> 关联：`design/product/release-auto-update.md`（现有 Desktop tag 发版）、ADR `knowledge/decisions/48-cli-first-class-release.md`。

## 0. 实现状态（2026-07-20）

| 项 | 状态 |
| --- | --- |
| 版本门禁纳入 `apps/tui` | **已落地**（check/stamp + package version 对齐 `VERSION`） |
| `peer --version` / `-v` | **已落地**（`apps/tui/src/cli-version.ts`）；输出 `peer <semver>` |
| Bun 版本注入 | **已落地并修复**：`--env=PEER_CLI_*`；模块级直接读 `process.env.PEER_CLI_VERSION` |
| `release.yml` `build-cli` | **已落地**（`macos-14` → `peer-darwin-arm64.tar.gz`，needs 阻断） |
| README / release notes | **已落地**（CLI-only + 双文件同目录） |
| 本地完整 build 验收 | **已通过**：`pnpm --filter @peer-agent/cli build`；`peer --version` → `peer 0.0.1-beta.37`；归档含双文件 |
| 正式 GitHub Release 挂载 | **待下次 `v*` tag** 由 CI 产出（workflow 已具备） |
| 多平台 / brew / npm / SHA256 | **未做**（阶段二+） |

### 0.1 Bun 注入踩坑（实现时实锤）

1. `--env` 是**前缀通配**，必须 `--env=PEER_CLI_*`。写 `--env=PEER_CLI_VERSION` **不会**匹配变量 `PEER_CLI_VERSION`。  
2. 只有**直接**属性访问 `process.env.PEER_CLI_VERSION` 会被 compile 内联；经参数 `env.PEER_CLI_VERSION` 读取在产物中仍为空，最终落到 `0.0.0-dev`。

## 1. 背景与问题

### 1.1 代码事实（落地前 → 落地后，2026-07-20）

| 维度 | Desktop | CLI / TUI（落地后） |
| --- | --- | --- |
| 源码位置 | `apps/desktop`（`@peer-agent/desktop`） | `apps/tui`（`@peer-agent/cli`，`private: true`） |
| 当前版本 | 与根 `VERSION` 对齐（例：`0.0.1-beta.37`） | **已进门禁**，与 `VERSION` 对齐（例：`0.0.1-beta.37`） |
| 正式发版 | `.github/workflows/release.yml`：`meta → build(mac/win) → release` | **`build-cli`**（Bun+Rust）→ 上传 `peer-darwin-arm64.tar.gz`；`release` needs `build-cli` |
| 版本脚本 | `check-version` / `stamp-version` 含 desktop + packages | **含** `apps/tui/package.json` |
| 构建产物 | electron-builder → `dist-electron/*` | `dist/peer` + `dist/peer-credential-helper`（≈65MB + helper） |
| 后处理 | electron-builder / after-sign | `finalize-binary.mjs`：chmod + **mac ad-hoc codesign** |
| 运行时依赖 | extraResources 带 helper + capabilities | helper：`PEER_CREDENTIAL_HELPER_PATH` → 可执行文件同目录 → resourcesPath → repo target |
| CLI 入口参数 | n/a | **`peer --version` / `-v`** → `peer <semver>`，不进 TUI |
| 用户数据 | `~/.peer-agent/*` | 同左（可与 Desktop 互通） |
| 本地发布脚本 | `apps/desktop/scripts/publish.sh` 走 Desktop 链路 | 本地可用 `pnpm --filter @peer-agent/cli build`；publish.sh **仍不**构建 CLI |

结论：

- **产品与架构上**，CLI 已是可独立运行的入口（不依赖 Desktop 进程）。  
- **分发上**，阶段一代码/CI 已具备；**对外资产**待下次 tag 发布。  
- **打包上**，CLI 不是「单二进制即可用」：凭证链路依赖同目录 helper。

### 1.2 对标 OpenCode（`anomalyco/opencode`，样例 Release `v1.18.3`）

| 点 | OpenCode 做法 | Peer 应对齐的 |
| --- | --- | --- |
| 仓库 | 单 monorepo：`packages/cli` + `packages/desktop` + 大量共享包 | 保持 monorepo，不拆仓 |
| 同 tag 多资产 | 同一 Release 同时挂 **CLI 归档** 与 **Desktop 安装包** | 同 tag 双产物 |
| CLI 形态 | `opencode-darwin-arm64.zip`、`opencode-linux-*.tar.gz`、`opencode-windows-*.zip` 等 | **归档包**，不是裸二进制 |
| Desktop 形态 | `opencode-desktop-mac-*.dmg/zip`、win exe、linux deb/AppImage 等 | 继续现有 electron-builder 命名 |
| 安装体验 | 另有 curl 安装脚本 / 多通道（更成熟） | **二期**再做；一期先有 Release 资产 |
| 发布说明 | Core / Desktop 分节 | Release notes 增加 **CLI** 小节 |

### 1.3 要解决的用户问题

1. 只想在终端用 Agent，不想装 Electron。  
2. 不应被要求 clone + 配 Bun/Rust + 本地 compile。  
3. 已装 Desktop 再装 CLI（或反过来）时，会话/设置/凭证继续共享 `~/.peer-agent`。  
4. 下载后能在**干净机器**上启动，而不是缺 helper 才发现半残。

## 2. 目标态

```text
peer_agent monorepo
├── apps/desktop  → 安装包 / electron-updater
├── apps/tui      → peer CLI 包（一等发布物）
└── packages/*    → 共享 Runtime / 会话 / 设置 / credential-helper

同一 git tag（如 v0.0.1-beta.38）
        │
        ├─► Desktop: Peer-Agent-*.dmg / .exe + latest|beta 更新清单
        └─► CLI:     peer-<os>-<arch>.zip|.tar.gz
                     └── peer
                     └── peer-credential-helper[.exe]

用户路径：
- 只用 CLI     → 解压 CLI 包，把目录或软链放进 PATH，不装 Desktop
- 只用 Desktop → 装客户端
- 两者都用     → 共享 ~/.peer-agent
```

### 2.1 成功标准（阶段一）

1. 推 `v*` tag 后，GitHub Release **同时**包含 Desktop 安装包与 **至少一个** CLI 归档包。  
2. `apps/tui/package.json` 版本与根 `VERSION` / Desktop **一致**（check + stamp 强制）。  
3. CLI 归档内含 **`peer` + `peer-credential-helper`**；解压后同目录可运行。  
4. `peer --version` 输出与 tag 版本一致（稳定、可脚本解析）。  
5. README 写清：可只装 CLI、如何下载/解压/运行、与 Desktop 关系、mac 未公证提示。  
6. **不**要求安装 Desktop 才能使用 CLI。  
7. 文档区分：**已决策 / 实施建议 / 待定**（见 §10）。

### 2.2 非目标（阶段一明确不做）

| 不做 | 原因 |
| --- | --- |
| 拆成两个 Git 仓库 | 同步成本高，对标也不拆 |
| brew / npm 公包 / curl 安装脚本全套 | 二期安装体验 |
| Desktop 安装包强制捆绑 CLI | CLI-only 不依赖 Desktop；捆绑是可选增强 |
| CLI 自动更新（`peer update`） | 一期手动从 Release 升级 |
| 完整 TUI i18n | 与「能装能发」正交 |
| 第二套会话/设置目录 | 必须继续共享 `~/.peer-agent` |
| 正式 Apple Developer ID / 公证（CLI） | 与 Desktop 阶段二签名同级后置；一期 ad-hoc + 文档说明 |
| Windows CLI 必发 | 默认定阶段二（见 §10） |
| 把 `@peer-agent/cli` 改 `private: false` 并 npm publish | 一期只走 GitHub Release 二进制/归档 |

## 3. 决策摘要

| 决策点 | 选择 | 性质 |
| --- | --- | --- |
| 仓库 | 保持 monorepo | **已决策** |
| 版本 | 与 Desktop 同 tag / 同 `VERSION` | **已决策** |
| 发布触发 | 继续 tag 驱动（`v*`），复用 `release.yml` 主链路 | **已决策** |
| 安装关系 | Desktop 与 CLI **安装独立** | **已决策** |
| 数据 | 继续共享 `~/.peer-agent` | **已决策** |
| CLI 产物形态 | **归档包**（内含 peer + helper），挂同一 Release | **已决策（复审后）** |
| 裸 `peer` 单文件上传 | 不做默认；若上传必须同时有 helper 或完整归档 | **已决策** |
| 阶段一平台 | 见 §10；默认至少 **darwin-arm64** | **待定（有默认建议）** |
| CLI job 失败策略 | 见 §5.5；默认 **CLI 关键平台失败 → 整次 release 失败** | **待定（有默认建议）** |
| checksum | 阶段一.5 起提供 `SHA256SUMS` | **实施建议** |
| brew/npm/脚本 | 阶段二 | **已决策延后** |

## 4. 用户旅程（阶段一）

### 4.1 CLI-only 用户

1. 打开 GitHub Releases，找到与 Desktop 相同的 tag。  
2. 下载 `peer-darwin-arm64.zip`（或文档写明的平台包）。  
3. 解压到例如 `~/bin/peer-agent/`（**保持两文件同目录**）。  
4. `chmod +x peer peer-credential-helper`（若 zip 未保留权限）。  
5. 将 `peer` 链到 PATH，或把该目录加入 PATH。  
6. 运行 `peer --version` 核对版本；再运行 `peer` 进入 TUI。  
7. 配置模型/密钥后开始对话；数据写入 `~/.peer-agent`。  
8. 升级：下载新版归档覆盖同目录文件（或换目录并改 PATH）。

**macOS 未公证预期**：首次运行可能被 Gatekeeper 拦截 → 文档写明「系统设置 → 隐私与安全性 → 仍要打开」，或 `xattr -dr com.apple.quarantine <解压目录>`（文档给出推荐一种，避免散落多种黑科技）。

### 4.2 Desktop-only 用户

无变化：继续装 dmg/exe，走 electron-updater。**不强制**安装 CLI。

### 4.3 双端用户

- 可同时安装；**不要**为 CLI 另设数据根。  
- 会话列表按 workspace 过滤等既有语义不变。  
- 版本建议：尽量使用同一 tag 的 Desktop + CLI，降低「一端新协议、一端旧」风险（阶段一不做强制互检）。

### 4.4 开发者本地

```bash
# 在 peer_agent 仓
pnpm install
pnpm --filter @peer-agent/cli build   # 或 apps/tui 的 build 脚本
./apps/tui/dist/peer --version
./apps/tui/dist/peer
```

## 5. 技术设计（阶段一）

### 5.1 版本门禁

**改动文件（代码仓）：**

- `scripts/check-version.mjs`：`packageJsonFiles` **增加** `apps/tui/package.json`  
- `scripts/stamp-version.mjs`：同上  
- 将 `apps/tui/package.json` 的 `version` 从 `0.1.0` **对齐**当前 `VERSION`

**不改：** Cargo / 其它未纳入门禁的 package 策略（除非另案）。

**验收：** `node scripts/check-version.mjs` 在 stamp 后通过；漏改 tui 版本则失败。

### 5.2 `peer --version`（净新增）

**现状：** `apps/tui/src` 无稳定 CLI 参数解析；直接跑 `dist/peer --version` **不会**按产品契约打印版本。

**要求：**

| 项 | 约定 |
| --- | --- |
| 触发 | **已实现** `peer --version` / `peer -v`（选定 `-v`，非 `-V`） |
| 输出 | 单行：`peer <version>`（例：`peer 0.0.1-beta.37`） |
| 退出码 | `0` |
| 副作用 | **不得**启动 TUI、不得写会话、不得要求 TTY |
| 版本来源 | 构建时注入：`build-peer.mjs` 设 `PEER_CLI_VERSION` + Bun `--env=PEER_CLI_*`；源码侧模块级 `process.env.PEER_CLI_VERSION` 捕获；回退 package.json |

实现时注意：Bun 仅内联直接 `process.env.PEER_CLI_*` 读；经参数读取不会内联。

### 5.3 运行时双文件契约（关键）

本地 build 已证明产物为：

```text
apps/tui/dist/
  peer                      # bun --compile
  peer-credential-helper    # Rust，由 build-credential-helper copy
```

`finalize-binary.mjs` 对二者 chmod；在 darwin 上对二者 **ad-hoc codesign**。

`@peer-agent/credential-helper` 的 `resolveCredentialHelperPath` 候选顺序（摘要）：

1. `options.explicitPath` / env `PEER_CREDENTIAL_HELPER_PATH`  
2. `resourcesPath`（Desktop 打包用）  
3. **可执行文件同目录**（CLI 分发主路径）  
4. 开发树 `target/release` 等回退  

**阶段一分发硬约束：**

- Release 资产必须让用户解压后满足 **peer 与 helper 同目录**。  
- 文档可提及 `PEER_CREDENTIAL_HELPER_PATH` 作为排障手段，**不是**默认安装步骤。  
- CI 验收：归档内两文件都存在、可执行位正确（在对应 OS runner 上 smoke）。

> 若只上传 `peer` 单文件，干净机器上模型凭证能力会坏 —— 这是初稿最大漏洞。

### 5.4 归档命名与布局

**推荐（已决策默认）：**

| 平台 | 资产名 | 归档格式 | 归档内相对路径 |
| --- | --- | --- | --- |
| macOS arm64 | `peer-darwin-arm64.zip` | zip | `peer`, `peer-credential-helper` |
| macOS x64 | `peer-darwin-x64.zip` | zip | 同上 |
| Linux x64 | `peer-linux-x64.tar.gz` | tar.gz | 同上 |
| Windows x64（阶段二） | `peer-windows-x64.zip` | zip | `peer.exe`, `peer-credential-helper.exe` |

说明：

- 前缀用 `peer-`（产品命令名），避免与 Desktop 的 `Peer-Agent-*` 混淆。  
- **不要**把 helper 塞进另一个 URL 让用户二次下载。  
- 可选：额外上传未打包二进制仅供调试，**不能**替代归档作为主下载项。

对标 OpenCode：CLI 也是 per-platform 归档，而非「单文件 + 隐式依赖」。

### 5.5 CI / `release.yml` 集成

现有链路：

```text
meta → build(matrix: macos-14 mac, windows-latest win) → release(ubuntu 汇总 gh release)
```

Desktop build 已具备：pnpm、Node 22、Rust、cargo cache、`stamp-version`、credential-helper 的 cargo 构建。  
**缺少：** Bun（CLI `bun build --compile` 必需）。

**推荐结构（实施建议）：**

```text
meta
  ├─► build-desktop (现有 matrix mac/win)     ──┐
  └─► build-cli     (新 matrix，至少 darwin-arm64) ─┴─► release（汇总上传同一 Release）
```

**build-cli job 要点：**

1. `actions/checkout`  
2. `pnpm` + `Node 22`（与 Desktop 一致）  
3. **安装 Bun**（固定主版本，写入 workflow）  
4. **Rust toolchain** + cargo cache（构建 helper）  
5. `node scripts/stamp-version.mjs "${{ needs.meta.outputs.version }}"`  
6. `pnpm install --frozen-lockfile`  
7. `pnpm --filter @peer-agent/cli build`（内部：helper release copy + bun compile + finalize）  
8. 打包归档 + 计算可选 checksum  
9. `upload-artifact`：`cli-<os>-<arch>`  
10. Smoke：`./peer --version`；可选 helper `ping`（若已有协议）

**release job：**

- 除 Desktop 产物外，下载 CLI artifacts 并 `gh release upload` 到同一 tag。  
- Release body：沿用 `release-notes/v*.md`；**模板增加 CLI 下载说明小节**（见 §6）。

**失败策略（默认建议，待你拍板）：**

| 场景 | 建议 |
| --- | --- |
| 阶段一「关键」CLI 平台（默认 darwin-arm64）构建失败 | **fail 整个 release**（避免发「假完整」版） |
| 非关键扩展平台失败 | `fail-fast: false`，允许缺席并在 notes 标明 |
| Desktop 成功 CLI 失败 | 不发布或标记 draft —— **不要**静默只发 Desktop |

备选（若更在意 Desktop 永不被 CLI 堵住）：CLI 失败仅 warning + Release 标注缺失；需在 ADR 明确接受「同 tag 可能无 CLI」。

### 5.6 签名与安全

| 项 | 阶段一 | 后置 |
| --- | --- | --- |
| mac CLI | 保持 `finalize-binary` **ad-hoc** codesign（与当前本地一致） | Developer ID + 公证 |
| checksum | 建议阶段一.5：`SHA256SUMS` 附在 Release | 强制校验的安装脚本 |
| 供应链 | 仍用 tag + GitHub Release 信任模型 | cosign / 独立签名密钥 |
| 权限 | 不在文档教用户关闭 SIP 等危险操作 | — |

Desktop 的 CSC / 公证策略**不**因 CLI 一期改变；两边可独立升级签名成熟度。

### 5.7 兼容与升级

| 主题 | 约定 |
| --- | --- |
| 数据目录 | 唯一：`~/.peer-agent`（可用 `PEER_AGENT_HOME` 若代码已支持；文档以默认路径为主） |
| 配置 / 会话 / 凭证 | Desktop ↔ CLI 共享；破坏性变更走统一 Runtime 版本纪律 |
| 跨版本 | 同 tag 最安全；允许短期版本差，但不做双写兼容层专项 |
| 卸载 CLI | 删除解压目录与 PATH 入口即可；**默认不**删除 `~/.peer-agent`（避免误伤 Desktop） |
| 卸载 Desktop | 同理不自动删共享数据 |
| beta / stable 通道 | CLI **无** updater 通道文件；用户按 Release（含 prerelease）手动选包。tag 语义仍：`vX.Y.Z` latest，`vX.Y.Z-beta.N` prerelease |

### 5.8 与 Desktop 发布文档边界

- `release-auto-update.md`：继续写 Desktop 安装包、electron-updater、通道 yml。  
- 本文：CLI 资产、双文件契约、CLI job、CLI-only 旅程。  
- 两边交叉链接；禁止在两篇文档复制两套互相矛盾的矩阵。

## 6. 文档与发布说明

### 6.1 README（代码仓，实现时改）

最小结构：

```markdown
## 安装

### 桌面客户端
- 从 GitHub Releases 下载对应平台安装包
- 支持 beta / stable 通道自动更新

### 仅使用 CLI（不需要桌面客户端）
1. 在同一 GitHub Release 下载 `peer-<os>-<arch>.zip` / `.tar.gz`
2. 解压，确认目录内同时有 `peer` 与 `peer-credential-helper`
3. chmod +x 后将 `peer` 加入 PATH（两文件保持同目录）
4. `peer --version` → `peer`
5. 数据目录：`~/.peer-agent`（可与桌面客户端共用）

macOS 若提示无法验证开发者：…（Gatekeeper 说明）
```

### 6.2 `release-notes/TEMPLATE.md`（代码仓）

增加：

```markdown
## CLI
- 资产：`peer-...` 归档（含 credential helper）
- 安装：解压后 PATH；详见 README
```

### 6.3 本知识库

- 发版总览：`design/product/release-auto-update.md`  
- 本方案 + ADR 48  
- **已回写**「代码已落地」状态与实际平台矩阵（阶段一：`darwin-arm64`；Release 资产待下次 `v*` tag）

## 7. 风险与缓解

| 风险 | 影响 | 缓解 |
| --- | --- | --- |
| 只发 `peer` 不发 helper | 凭证/模型配置半残 | **归档双文件**硬约束 + CI 清单校验 |
| CI 无 Bun | CLI 编不过 | build-cli 显式 setup Bun |
| bun compile 跨平台 | 矩阵复杂 | 阶段一先锁关键平台；原生 runner 优先于交叉 |
| CLI 未进 stamp | 版本漂移 | check/stamp 同步 |
| 关键 CLI 失败仍发版 | CLI-only 断供却显示发版成功 | 默认 fail release（§5.5） |
| 用户以为必须装客户端 | 转化差 | README 首屏 CLI-only |
| mac 未公证 | Gatekeeper | 文档说明；阶段二签名 |
| 二进制体积大（~65MB+） | 下载慢 | 接受；二期再谈压缩/分包 |
| `private: true` 被误 npm publish | 混乱 | 一期明确只走 GH Release |
| 本地 `publish.sh` 仍只发 Desktop | 维护者漏 CLI | 文档标明；二期再改本地脚本或统一 `scripts/publish` |

## 8. 验收清单（阶段一）

### 8.1 静态 / 本地

- [ ] `apps/tui/package.json` 版本 == `VERSION`  
- [ ] `node scripts/check-version.mjs` 通过（含 CLI）  
- [ ] `node scripts/stamp-version.mjs <ver>` 会改写 `apps/tui/package.json`  
- [ ] 本地 `pnpm --filter @peer-agent/cli build` 成功  
- [ ] `dist/` 同时存在 `peer` 与 `peer-credential-helper`  
- [ ] `peer --version` 与 stamp 版本一致且不进 TUI  

### 8.2 CI / Release

- [ ] `release.yml` 含 build-cli（Bun + Rust + stamp + 归档）  
- [ ] 某次 beta tag 的 Release 同时出现：Desktop 安装包 + CLI 归档  
- [ ] 归档内双文件齐全  
- [ ] 干净机器（无 Desktop、无源码树）仅用归档可启动并读写 `~/.peer-agent`  
- [ ] 关键平台 CLI 失败时的行为符合 §5.5 选定策略  

### 8.3 文档

- [ ] README 有 CLI-only 段落（含双文件与 mac 提示）  
- [ ] release notes 模板含 CLI 小节  
- [ ] 本方案、ADR 48、`release-auto-update.md` 交叉链接一致  

## 9. 建议落地顺序（代码仓 PR 切片）

> **状态：阶段一代码已在 peer_agent 落地（2026-07-20）**；下表保留为变更地图。

1. **版本门禁 PR**：check/stamp + tui version 对齐（纯治理）。  
2. **`peer --version` PR**：注入版本 + 单测。  
3. **CI CLI 构建 + 归档 + Release 上传 PR**：主交付（含双文件校验）。  
4. **README + release-notes 模板 PR**：话术与 Gatekeeper。  

不要把 brew/npm/正式签名塞进第一个实现 PR。

## 10. 开放问题（待拍板）

| # | 问题 | 默认建议 | 阻塞阶段一？ |
| --- | --- | --- | --- |
| 1 | 阶段一 CLI 平台最小集？ | **仅 darwin-arm64 必出**；有余力再加 darwin-x64 / linux-x64 | 否（有默认） |
| 2 | Windows CLI 是否与 Desktop win runner 顺带构建？ | **阶段二** | 否 |
| 3 | 关键 CLI 失败是否阻断整个 Release？ | **是，阻断** | 建议实现前确认 |
| 4 | 是否阶段一就上传 `SHA256SUMS`？ | **阶段一.5** | 否 |
| 5 | `peer --version` 输出格式？ | `peer <semver>` 单行 | 否 |
| 6 | 是否改本地 `publish.sh` 一并打 CLI？ | 阶段一可只靠 CI；文档注明 | 否 |

## 11. 阶段二预告（不实施，仅占位）

1. 安装脚本 / Homebrew /（可选）npm 包装。  
2. `peer update` 或等价。  
3. Windows CLI 正式矩阵。  
4. mac 正式签名与公证。  
5. 可选：Desktop 安装时「附带 CLI 到 PATH」。  
6. checksum 校验进入安装脚本默认路径。

## 12. 一句话收束

> **同仓、同 tag、同 `VERSION`；Desktop 与 CLI 都是一等入口；安装彼此独立，数据彼此共享。阶段一交付的是「可运行的 CLI 归档（peer + helper）+ 版本门禁 + 文档」，不是单文件链接，也不是完整安装生态。**
