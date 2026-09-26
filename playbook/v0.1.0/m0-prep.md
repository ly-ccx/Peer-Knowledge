# M0 准备（不发版）

创建时间：2026-09-26
最后更新：2026-09-26

> 版本计划：`design/product/v0.1.0-release-plan.md` §5、§6  
> 退出条件：开发线建好；CI 上线；基线更正；ADR 80 / 81 / 83 / 84 / 85 为 Accepted（ADR 82 可在 beta.4 开工前）

---

## P0-1 开 0.1.0 开发线与分支保护

- **状态**：已完成（2026-09-26）。分支 `PeerAgent/dev/0.1.0` 从 `main` a087988c 拉出；保护规则为必须走 PR、禁止强推、禁止删除，管理员也不例外。CI 必过留到 P0-5。
- **原步骤**：
- **目标**：从 `main`（a087988c）拉 `PeerAgent/dev/0.1.0` 并推到远端；设置分支保护。
- **步骤**：
  1. `git switch main && git pull && git switch -c PeerAgent/dev/0.1.0 && git push -u origin PeerAgent/dev/0.1.0`。
  2. GitHub 分支保护：禁止 force push；要求 PR；P0-5 上线后要求 CI 通过。
  3. 不改 `VERSION`（第一次改在 B1-R）。
- **退出条件**：远端存在该分支；保护规则生效。

## P0-2 ADR 80–85 评审

- **状态**：已完成（2026-09-26）。
- **结果**：ADR 80、81、83、84、85 为 Accepted。ADR 82 仍为 Proposed，留到 beta.4 开工前。
- **关闭的点**写在各 ADR 状态节，以及运行时契约 §13、分层文档 §13、记忆文档 §16。与任务卡数字不一致的地方（熔断 5 次、事件合并 2 秒、简报 6000 字符、不投影外网）以 ADR 评审结论和任务卡为准。

## P0-3 回归基线核对与 `AGENTS.md` 更正

- **级别**：C。**规模**：S。
- **依赖**：P0-1。
- **目标**：让仓库记录的「已知失败」与现实一致，作为 0.1.0 的回归基线。
- **代码锚点**：代码仓 `AGENTS.md`「Known pre-existing failures on `main`」一段。
- **事实**（2026-09-26，macOS）：`pnpm build`、`pnpm typecheck`、`pnpm architecture:check`、`pnpm test` 全部通过；记录的 5 个失败测试单独运行全部通过；`goal.test.ts` 类型错误与 2 处 `@keyframes` 违规都已不存在。
- **允许改动**：代码仓 `AGENTS.md`（只改这一段）。
- **实现要点**：
  1. 在 Linux（Cursor Cloud 快照或 `ubuntu-latest` 容器）上跑 `pnpm build && pnpm test`、`pnpm typecheck`、`pnpm architecture:check`，记录真实结果。
  2. 把该段改为按平台记录：macOS 全绿；Linux 若仍有失败，逐项列出测试名与原因。没有就删掉该段对应条目。
  3. 保留「计时敏感测试在并行下可能 `cancelledByParent`，单独重跑」的说明。
- **退出条件**：`AGENTS.md` 与两个平台的真实结果一致；PR 描述贴两个平台的测试摘要。

## P0-4 代码仓入口指向 0.1.0 计划与手册

- **级别**：C。**规模**：S。
- **依赖**：P0-1。
- **允许改动**：代码仓 `AGENTS.md`（只新增一段）。
- **实现要点**：新增「进行中的专项：0.1.0 机器人列表与项目代理」一段，内容：
  - 基线分支 `PeerAgent/dev/0.1.0`；
  - 必读 `peer-knowledge/design/product/v0.1.0-release-plan.md`、`peer-knowledge/playbook/project-agent-implementation-handbook.md`、`peer-knowledge/playbook/v0.1.0/README.md`；
  - 执行方只做被派发的卡，遵守手册 §2 铁律。
  - 不写任何本机绝对路径。
- **退出条件**：合入开发线并 push。

## P0-5 PR CI 工作流

- **级别**：B（改 `.github/workflows/`，手册 §2.1 第 6 条的例外，需负责人在派卡时明确授权）。**规模**：S。
- **依赖**：P0-1。
- **目标**：每个 PR 自动跑构建与测试，替多模型并行派活兜底。
- **代码锚点**：`.github/workflows/release.yml`（复用其 Node 22 / pnpm 10.22.0 / Rust 设置步骤）；根 `package.json` 的 `build`、`test`、`typecheck`、`architecture:check`。
- **允许改动**：新建 `.github/workflows/ci.yml`。
- **实现要点**：
  - 触发：`pull_request` 到 `PeerAgent/dev/**` 与 `main`；`push` 到 `PeerAgent/dev/0.1.0`。
  - 矩阵：`macos-14`、`ubuntu-latest`；Node 版本用 `22.x` 最新（需 ≥ 22.18，测试直接跑 `.ts`）；安装 Bun（TUI 测试）；Linux 安装 `libdbus-1-dev pkg-config`（keyring crate）。
  - 步骤：`pnpm install --frozen-lockfile` → `pnpm build` → `pnpm typecheck` → `pnpm architecture:check` → `pnpm test`。
  - 并发：同一 PR 新提交取消旧运行。
  - 计时敏感测试偶发失败：失败时对失败的单个文件自动重跑一次，仍失败才判失败（在工作流里用脚本实现，不改测试）。
  - 不注入任何发布密钥。
- **必须新增的测试**：无（工作流本身在 PR 上跑一次作为验证）。
- **退出条件**：本卡 PR 上 CI 两个平台都绿；负责人把 CI 设为开发线必过检查。

## P0-6 补 ADR 75 文件

- **状态**：已完成（2026-09-26）。补记为 `knowledge/decisions/75-remote-read-preflight.md`，只记录 0.0.18 已实现的只读预检，不包含尚未实现的扫码方案。ADR 85 的关联已改为正式链接。
