# 发布与自动更新（GitHub Releases，tag 驱动）

> 阶段一文档：跑通「推 tag → GitHub Actions 自动出包 → 客户端按通道收到更新」。
> 代码签名 / 公证为阶段二增量，本文末尾列出。
>
> **CLI 一等发布（方案已复审、代码未落地）**：同 tag 另挂 **CLI 归档**
> （如 `peer-darwin-arm64.zip`，内含 `peer` + `peer-credential-helper`），
> 版本门禁纳入 `apps/tui`、安装与 Desktop 独立、数据仍共享 `~/.peer-agent`。
> CLI job 需 Bun + Rust；细节与验收以
> `design/product/cli-first-class-release.md` 与 ADR
> `knowledge/decisions/48-cli-first-class-release.md` 为准。
> **本文仍以 Desktop 安装包 / electron-updater 为主**；勿在本文复制第二套 CLI 矩阵。

## 1. 总览

```
本机: ./scripts/publish.sh beta|stable
        │  计算版本 → stamp 版本事实源 → commit → tag → push tag
        ▼
GitHub Actions (.github/workflows/release.yml, 由 v* tag 触发)
        │  按 tag 名分流通道 → 矩阵构建 mac+win → electron-builder --publish always
        ▼
GitHub Releases  (latest*.yml / beta*.yml 更新清单 + 安装包)
        ▼
客户端 electron-updater (auto-updater.mjs)
        │  按当前版本号语义选 channel(beta/latest) → 检查/下载/提示重启
```

## 2. 通道分流规则（单一约定，三处一致）

| Tag 形态 | 版本号 | 通道 | GitHub Release | 更新清单 |
| --- | --- | --- | --- | --- |
| `v0.0.1` | `0.0.1` | latest | 正式 | `latest-mac.yml` / `latest.yml` |
| `v0.0.1-beta.1` | `0.0.1-beta.1` | beta | prerelease | `beta-mac.yml` / `beta.yml` |

- workflow 从 tag 名推导 `version`/`channel`。
- electron-builder 对含 `-` 的版本自动标记 prerelease，并经 `generateUpdatesFilesForAllChannels: true` 生成对应通道清单。
- 客户端 `resolveUpdateChannel()` 用同一语义（含 `-beta/-alpha/-rc` → beta）选择读取哪个清单。

## 3. 版本事实源与 stamp

仓库内 `VERSION` 是唯一基线版本，`scripts/check-version.mjs` 强制
`VERSION` 与门禁列表内的 `package.json` / Cargo 清单一致。

> **现状缺口（CLI 方案落地前）**：门禁列表**尚未**包含 `apps/tui/package.json`
> （CLI 仍可能停在 `0.1.0`）。CLI 一等发布阶段一要求把该文件纳入 check/stamp；
> 详见 `cli-first-class-release.md` §5.1。落地前「所有 package.json」表述不成立。

发布时 **tag 才是权威版本**。`scripts/stamp-version.mjs` 把 tag 版本回写到门禁
列表内文件（check-version 的“写”对偶），从而：

1. 产物版本 == tag 版本；
2. 一致性校验仍通过（beta 后缀不再冲突）。

## 4. 本机发布入口

```bash
# 正式版（取 VERSION，如 v0.0.1）
./apps/desktop/scripts/publish.sh stable

# 测试版（自动递增 beta 号，扫描已有 git tag）
./apps/desktop/scripts/publish.sh beta

# 指定 beta 号
./apps/desktop/scripts/publish.sh beta 3

# 演练（改版本文件但不 commit/tag/push）
DRY_RUN=1 ./apps/desktop/scripts/publish.sh beta
```

脚本只负责 **打 tag 并推送**，构建在 CI 完成，本机不出包。

## 5. 客户端集成

- 模块：`apps/desktop/electron/main/auto-updater.mjs`
- 挂载：`main.mjs` 的 `app.whenReady()` 内、`createWindow()` 之后。
- 行为（阶段一）：检查 → 自动下载 → 下载完成弹原生框让用户选择「立即重启更新」/「稍后」（退出时自动安装）。
- provider（owner/repo）来自打包进产物的 `app-update.yml`（由 electron-builder publish 配置生成），客户端不硬编码，避免双事实源。
- 开发态默认跳过；联调可设 `PEER_AGENT_FORCE_UPDATER=1`。

## 6. 验证清单（推真实 tag 前后）

本机静态验证（已通过）：
- `node --check` auto-updater.mjs / main.mjs
- `pnpm --filter @peer-agent/desktop typecheck`
- `DRY_RUN=1 ./apps/desktop/scripts/publish.sh beta` → 版本 stamp + check-version 通过
- workflow YAML 可被解析

真实发布验证（交由用户执行）：
1. 推一个 beta tag：`./apps/desktop/scripts/publish.sh beta`
2. 打开 Actions 看 Release workflow 跑通：https://github.com/ly-ccx/Peer-Agent/actions
3. 确认 Releases 出现 **prerelease**，资产含安装包 + `beta-mac.yml` / `beta.yml`：https://github.com/ly-ccx/Peer-Agent/releases
4. （CLI 方案落地后）同一 Release 另含 CLI 归档（如 `peer-darwin-arm64.zip`），解压后有 `peer` + `peer-credential-helper`，且 `peer --version` 与 tag 一致；清单见 `cli-first-class-release.md` §8
5. 推一个正式 tag：`./apps/desktop/scripts/publish.sh stable`
6. 确认生成 **正式 Release**，资产含 `latest-mac.yml` / `latest.yml`（及落地后的 CLI 归档）
7. 安装一个旧版本客户端，发布更高版本 tag，确认客户端按对应通道弹出更新提示

## 7. 阶段二（增量，未在阶段一实现）

- macOS 公证：`electron-builder.yml` 改回 `notarize: true`，CI 注入
  `APPLE_ID` / `APPLE_APP_SPECIFIC_PASSWORD` / `APPLE_TEAM_ID` + Developer ID 证书。
- Windows 代码签名：配置签名证书 secrets。
- Windows arm64 native binary：当前 arm64 安装包打包 x64 的 `cu-proxy-core.exe`
  （emulation 运行），阶段二增加 Rust `aarch64-pc-windows-msvc` 交叉编译。
- 渲染层更新 UI：用 `auto-updater.mjs` 的 `onEvent` 回调桥接到渲染进度条/通知。
  ✅ **已落地（2026-06-25）**：下载从霸屏模态改为「弹窗动画退场 → 后台静默下载
  → 徽标 mini 环形进度 → 右下角完成卡片（立即安装 / ✕ 收起）」。详见
  ADR `knowledge/decisions/39-updater-download-ux.md`。该改造仅动渲染层 +
  i18n + CSS，未触及主进程 `auto-updater.mjs` 与 protocol。
