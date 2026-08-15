# Peer Agent 发布流程

创建时间：2026-07-27
最后更新：2026-08-15

> 用途：记录 Peer Agent Desktop、CLI 和开放 Runtime 的人工发版 SOP、职责边界与检查清单。
> 执行型 Skill：`/Users/liangyin/Documents/DEV/github/peer_agent/skills/release-process/SKILL.md`

## 一、仓库职责

Peer Agent 发布涉及两个解耦仓库：

| 仓库 | 本地路径 | 发布职责 |
|---|---|---|
| `peer_agent` | `/Users/liangyin/Documents/DEV/github/peer_agent` | 代码、版本戳、测试、构建、release notes、CHANGELOG、根 README 漂移检查、用户文档站、tag、CI 与 GitHub Release |
| `peer-knowledge` | `/Users/liangyin/Documents/MiaoYan/peer-knowledge` | 架构决策、版本规范、人工发布 SOP、故障经验与运维知识 |

原则：

- 所有可执行代码改动必须落在 `peer_agent`。
- `release-process` Skill 属于 `peer_agent` 工作空间，不能安装为全局 Skill。
- 本文是人工可读 Playbook，不替代代码仓中的 Skill 和 CI。
- `peer-knowledge` 的更新通常与产品发布准备一起完成，但不进入产品构建产物。

## 二、事实源

发布时按以下事实源工作：

| 信息 | 事实源 |
|---|---|
| 发布版本 | `v<version>` git tag |
| 工作区版本 | `peer_agent/VERSION` 与受管 package 清单 |
| 版本一致性 | `peer_agent/scripts/check-version.mjs` |
| 版本回写 | `peer_agent/scripts/stamp-version.mjs` |
| 产品发布说明 | `peer_agent/release-notes/v<version>.md` |
| 累积变更记录 | `peer_agent/CHANGELOG.md` |
| 产品入口说明 | `peer_agent/README.md`（定位 / 安装 / 入口面 / 能力；**不是**变更日志） |
| 用户文档站 | `peer_agent/docs/` |
| 架构、规范和 SOP | `peer-knowledge/knowledge/`、`peer-knowledge/playbook/` |
| 发布流水线 | `peer_agent/.github/workflows/release.yml` |

详细版本规则见：

```text
knowledge/specifications/06-version-management.md
```

Skill 范围规则见：

```text
knowledge/decisions/58-local-skill-scope-and-workspace-mounting.md
```

## 三、开始前确认

1. Peer Agent 当前活动工作空间应为：

   ```text
   /Users/liangyin/Documents/DEV/github/peer_agent
   ```

2. Skills 页面中的 `release-process` 应出现在“工作空间 · peer_agent”，不得出现在“全局”。
3. 确认目标版本与通道：
   - Beta：`x.y.z-beta.N`
   - Stable：`x.y.z`
4. 确认当前分支、远端和工作树状态。
5. 明确本次发布是否包含：
   - Desktop
   - CLI / TUI
   - 开放 Runtime packages
   - 用户文档站
   - 根 `README.md` 更新（仅在触发条件命中时）
   - 架构/规范/Playbook 更新
6. 高风险动作（推送 tag、发布包、覆盖 Release）必须获得用户明确确认。

## 四、发布准备

### 4.1 汇总变更

在 `peer_agent` 中比较上一发布 tag 与当前提交：

```bash
git tag --list 'v*' --sort=-v:refname
git log <previous-tag>..HEAD --oneline
git diff --stat <previous-tag>..HEAD
```

按用户可见功能、修复、工程变化和已知问题分类。

### 4.2 更新产品发布资料

必须检查：

- `release-notes/v<version>.md`
- `CHANGELOG.md`
- `docs/changelog.html`（**硬门禁**：见下）
- `docs/docs.html`
- `docs/index.html`

产品行为变化后，文档不能继续描述已删除的命令或过期流程。

#### `docs/changelog.html` 硬门禁（禁止 stamp / tag 前跳过）

`release-notes/v<version>.md` 写了**不等于**站点已更新。站点数据是**生成式**的：`pnpm build:changelog` 从 `release-notes/` 解析出 `docs/changelog-data/manifest.json` 与各版本 JSON；`docs/changelog.html` 只是按需加载的页面外壳，禁止手工维护数据（旧的 `var ENTRIES = [...]` 内嵌结构已废弃，`check:changelog` 会拒绝其回归）。

发版前必须同时满足：

1. `CHANGELOG.md` 含本版标题（如 `## 0.0.4-beta.N`）
2. `pnpm build:changelog` 成功，随后 `pnpm check:changelog` 通过
3. 本版中英段落与 notes 事实一致
4. `docs/changelog-data/manifest.json` 的 `generatedAt` 为真实时间戳：生成器从 `release-notes/` 最近一次提交派生；`check:changelog` 拒绝 epoch 占位 `1970-01-01T00:00:00.000Z`（2026-08-15 前的旧生成器曾写死 epoch 0，线上曾长期携带该坏值）

本地核验失败则**禁止**进入 stamp / tag。不要用“先发版再补站点”绕过。

### 4.2.1 根 `README.md` 漂移检查（每次必做，条件更新）

**检查必做；完整重写不默认。** 根 README 是产品入口页，不是 `CHANGELOG` / `release-notes` 的替代品。

每次发版至少扫：

1. 版本表述（是否仍写过时 early-development / 旧版本号；**不得引用尚未发布的版本**——无 git tag 且无 release note 的版本只能写「开发中」，不能写「当前 beta 通道」）
2. 安装路径（`@peer-agent/cli`、`peer`、Desktop 开发/打包命令）与 **CLI 平台矩阵**（README 表述必须与 `packages/npm-cli/lib/platform.mjs` 的 `supported` 矩阵一致；当前仅 darwin-arm64 一等支持）
3. 入口面（Desktop / TUI / CLI）
4. 核心能力（Agent / Plan / Goal / Quick Chat / Browser·Workbench / MCP / Skills 等）
5. 链接存活（相对链接与文档入口；禁止代码仓内 architecture 死链）
6. 站点版本与发布态文案（`docs/docs.html` / `docs/index.html` 不得残留旧版本示例如 `v0.0.1-beta.*`，或未发布态文案如 `install (when published)`）
7. 新用户可见能力闭环（本轮 CHANGELOG / notes 新增的能力必须显式决策：进 README 与落地页，或记录为有意暂不写）

仅在命中触发条件时更新 README：

| 触发条件 | 动作 |
|---|---|
| 纯 bugfix / 内部重构 / 文案微调 | 通常 **no-op**（记录已检查） |
| 安装方式、入口面（Desktop / TUI / CLI）变化 | **更新** |
| 主能力上线/下线或对外叙事变化 | **更新** |
| Roadmap 大项完成态变化 | **建议更新** |
| 文档结构迁移导致 README 死链 | **更新** |
| 正式版（非 beta）或重大定位调整 | **更新** |

结果只允许：

- `README: no-op` — 已检查，无需改
- `README: updated` — 本轮已改并随发版准备提交

非目标：不要把每条 bugfix 写进 README；不要把 README 当 CHANGELOG 用；不要在发版流程里维护 `peer-knowledge` 架构长文。

### 4.2.2 开启开发线（与「发布」严格区分）

开启 `x.y.z` 开发线（如 stamp `0.0.5-beta.1`）不是发布，只允许最小动作集：

- `node scripts/stamp-version.mjs x.y.z-beta.1` 回写 `VERSION` / manifests；
- `CHANGELOG.md` 顶部写 `## x.y.z-beta.1 - <date>` 段并注明「开启开发线」。

禁止：

- 写 `release-notes/vx.y.z-beta.1.md`；
- 运行 `build:changelog` / 提交 `docs/changelog-data` 变更；
- 把该版本写进 README / 站点任何「当前 beta 通道 / latest」表述（只能写「开发中（尚未发布）」）。

「当前 beta 通道」只允许引用**已有 tag 且已有 release note**的版本。2026-08-15 曾因未定义本动作，出现「README 称 beta 通道为 0.0.5-beta.1、站点 manifest `latest.beta` 仍为 v0.0.4-beta.4」的分裂，已随本次修订记录。

### 4.3 更新知识库

如果本次发布改变了以下内容，应同时更新 `peer-knowledge`：

- 架构边界或关键数据流。
- 对外协议和版本策略。
- Skill、Plugin、MCP、权限或运行时治理规则。
- 发版流程、回滚方式或故障处理方法。
- 经验证可复用的开发经验。

知识库文档要求：

- 文件名使用 kebab-case。
- 文件开头包含“创建时间”和“最后更新”。
- 记录为什么这样设计，不复制大量代码实现。
- 可执行步骤应与代码仓真实脚本保持一致。

如果知识库和代码仓都发生改动，两边分别提交；不要把知识库文件复制进产品仓。

### 4.4 版本戳与一致性

在 `peer_agent` 中执行：

```bash
node scripts/stamp-version.mjs <version>
node scripts/check-version.mjs
```

版本脚本的受管文件列表优先于本文中的静态示例。

## 五、发布门禁

发版前至少检查：

- 版本一致性检查通过。
- 受影响包的 typecheck 通过。
- 受影响测试通过。
- Desktop renderer 可构建。
- CLI 产物与 npm 安装路径可验证。
- Runtime 公开包的 tarball 内容与外部宿主 smoke 通过。
- release notes、CHANGELOG 和用户文档站已同步。
- **硬门禁**：`pnpm build:changelog && pnpm check:changelog` 通过；manifest 的 `generatedAt` 非 epoch 占位且 `latest.<channel>` 与本版一致；核验失败不得 stamp/tag。
- 根 `README.md` 已完成漂移检查；若命中触发条件已更新，否则记录 `README: no-op`。
- 若有「开启开发线」动作：仅做了 4.2.2 允许的最小动作，未伪造发布态。
- 本轮架构或流程变化已同步到 `peer-knowledge`。

失败时停止后续 tag，不得用“先发布再补文档”绕过门禁。

## 六、提交、Tag 与 CI

发布准备文件应先提交到约定分支。推送 tag 前再次确认：

```bash
git status --short
git log -1 --oneline
node scripts/check-version.mjs
```

获得明确授权后，预发布 tag 可以从发布分支创建；**稳定版必须先合并 `main`，再创建正式 tag**：

```bash
git push origin HEAD
# 正式版：通过 PR 将发布准备提交合并到 main
git fetch origin main --tags
git switch main
git pull --ff-only origin main
RELEASE_TAG=v<version> RELEASE_COMMIT=HEAD pnpm release:source-check
git tag -a v<version> -m "<version>"
git push origin v<version>
```

`v*` tag 触发 `.github/workflows/release.yml`。不要在未知脏状态或未经验证的提交上打 tag。

来源规则与自动门禁：

- 预发布 tag（`alpha` / `beta` / `rc`）允许来自发布分支。
- 稳定版以 `main` 为正式代码事实源；`release:source-check` 会验证发布提交已被 `origin/main` 包含。
- tag 版本必须与仓库 `VERSION` 一致。
- Release workflow 在任何构建、GitHub Release 与 npm publish 前执行 `version:check` 和 `release:source-check`，失败则停止整条发布链。

## 七、发布后核验

依次检查：

1. GitHub Actions 对应 tag 的 workflow 成功。
2. GitHub Release 的标题、notes 和资产正确。
3. Desktop 安装包与更新清单可下载。
4. CLI 归档和 npm 安装面可用。
5. Beta/Stable 通道与版本格式一致。
6. `docs/` 用户站点展示新版本和更新日志；线上 `changelog-data/manifest.json` 的 `latest.<channel>` 为本版、`generatedAt` 非 epoch 占位。
7. 根 `README.md` 检查结果已明确（`no-op` 或 `updated`）；若已更新，入口/安装/能力描述与本轮产品一致。
8. 如修改了知识库，确认 `peer-knowledge` 的文档提交已推送。

## 八、失败处理

| 现象 | 处理 |
|---|---|
| 版本检查失败 | 修正 `VERSION` 与受管 package 版本，不打 tag |
| Tag 未触发 CI | 检查 tag 是否为 `v*`、是否已推送到正确 remote |
| Release 缺资产 | 检查对应平台 job、打包步骤和上传权限 |
| Pages 仍显示旧版本 / 「最新」仍是上版 | **硬门禁未过**：补 `CHANGELOG.md` + 重跑 `pnpm build:changelog && pnpm check:changelog`，再推 Pages 源分支；不要假设 notes 会自动进站点，也不要手工改 `docs/changelog-data/` |
| `manifest.json` 的 `generatedAt` 为 `1970-01-01` | 旧生成器曾写死 epoch 0：升级 `scripts/build-changelog.mjs` 后重跑 `pnpm build:changelog && pnpm check:changelog` |
| README 的 beta 通道与站点 manifest `latest.beta` 不一致 | 核对该版本是否有 git tag + release note；未发布开发线只能写「开发中」（见 4.2.2） |
| 根 README 仍写旧入口/死链 | 执行 4.2.1 漂移检查；命中触发条件则更新，勿用 notes 顶替 |
| Skill 在错误项目出现 | 检查是否错误安装到了 `~/.peer-agent/skills`，项目 Skill 应回到 `<workspace>/skills` |
| 当前项目看不到 `release-process` | 确认活动工作空间是 `peer_agent`，不是 `peer-knowledge` |

如果 tag 已经公开，禁止静默移动或覆盖 tag；应根据影响选择修复发布或显式撤回，并记录原因。

## 九、Definition of Done

- [ ] 版本号与通道已确认
- [ ] `release-notes/v<version>.md` 已更新
- [ ] `CHANGELOG.md` 已更新
- [ ] **硬门禁**：`pnpm build:changelog && pnpm check:changelog` 通过，manifest `latest.<channel>` 为本版且 `generatedAt` 非 epoch 占位
- [ ] 用户文档站已同步
- [ ] 已完成根 `README.md` 漂移检查（版本口径 / 安装与 CLI 平台矩阵 / 入口 / 能力 / 链接 / 站点版本文案 / 新能力闭环）
- [ ] 若命中 README 触发条件：已更新并随发版提交；否则记录 `README: no-op`
- [ ] 若有「开启开发线」动作：仅做了 4.2.2 允许的最小动作
- [ ] 相关架构、规范和 Playbook 已同步到 `peer-knowledge`
- [ ] 版本一致性检查通过
- [ ] 受影响测试、typecheck 和构建通过
- [ ] 发布准备提交可追溯
- [ ] 推送 tag 前获得明确授权
- [ ] CI、Release、产物和文档站完成发布后核验

## 十、关联资料

- `knowledge/specifications/06-version-management.md`
- `knowledge/decisions/48-cli-first-class-release.md`
- `knowledge/decisions/54-open-runtime-public-packages-and-release-policy.md`
- `knowledge/decisions/58-local-skill-scope-and-workspace-mounting.md`
- `/Users/liangyin/Documents/DEV/github/peer_agent/skills/release-process/SKILL.md`
