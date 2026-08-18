# CLI 脚本化 / 无头发起：Claude Code、Codex 对照与 Peer 缺口

创建时间：2026-08-18
最后更新：2026-08-18
文档状态：调研与分期建议 / 尚未立项实现
代码审计基线：`peer_agent` / `PeerAgent/0.0.5` / `5e3074ce`（`apps/tui/src/index.tsx`、`cli-version.ts`）
对照来源（外部，以各官方文档当时页为准）：
- Claude Code：[CLI reference](https://code.claude.com/docs/en/cli-reference)、[Headless / Agent SDK CLI](https://code.claude.com/docs/en/headless)
- Codex：[Non-interactive mode](https://developers.openai.com/codex/noninteractive)（`codex exec`）
适用范围：Peer CLI/TUI 产品面、Harbor / Pier 评测接入、CI 无头任务
关联：
- `knowledge/decisions/48-cli-first-class-release.md` — CLI 一等发布（安装面已有，脚本面未做）
- `knowledge/architecture/22-tui-desktop-shared-runtime-and-host-governance.md` — 双宿主共享内核
- `knowledge/architecture/desktop-cli-local-capability-parity.md` — 本地能力对齐（工具面，不是 argv）
- `knowledge/architecture/20-architecture-governance.md` — 主链不可旁路
- `playbook/change-intake.md` — 入口与提交纪律

---

## 1. 结论先讲

**第一步确实要补 CLI 的「无头发起任务」能力。** 这不是锦上添花，而是评测、CI、Harbor 适配的前置条件。

现状一句话：

| 产品 | CLI 现在是什么 |
|---|---|
| Claude Code | 交互 TUI **加上** `claude -p` 脚本 SDK |
| Codex | 交互 TUI **加上** `codex exec` 非交互子命令 |
| Peer | **只有**交互 TUI + `peer --version` |

Peer 的运行时、工具链、权限、Evidence 已经在 TUI 里。缺的是**命令行契约**：一条命令吃题面、不弹审批、跑完退出、用退出码和 stdout 交差。

不要把 Claude / Codex 的整份旗标抄过来。他们已经是「操作系统级 CLI」。Peer 先补 **评测最小集（P0）**，再按 P1/P2 长。

---

## 2. Peer 当前事实（以代码为准）

入口：`apps/tui/src/index.tsx`

```text
peer            → 启动 OpenTUI 交互会话
peer --version  → 打印版本并退出
peer -v         → 同上
其它 argv       → 一律当交互会话启动（包括 --help）
```

已有、但不是「发起任务」的面：

| 已有 | 说明 | 够不够评测 |
|---|---|---|
| `PEER_WORKSPACE_ROOT` | 工作区根，默认 `cwd` | 能指定仓，不能发起 |
| `PEER_USER_DATA_PATH` | 默认 `~/.peer-agent` | 能隔离数据，不能发起 |
| TUI `/` 命令 | 模型、模式、权限、resume、Goal、Skill、MCP | 必须有人在终端里 |
| `ask` / `session` / `full` 权限档 | 与 Desktop 同语义 | 无头时 `ask` 会挂死 |
| `@peer-agent/runtime-sdk` | 宿主可嵌运行时 | 库，不是 `peer` 命令 |
| `examples/external-host` | 证明 SDK 能转 | 不是解题 agent |

**没有的（P0 直接挡住评测）：**

- 位置参数或 `-p/--print` 传入 prompt
- 从 stdin 读题面
- 跑完退出（非 TTY 也开 TUI）
- 稳定退出码（0 成功 / 非 0 失败）
- `--output-format text|json`
- 命令行指定 `--access` / `--model` / `--effort` / `--mode`
- 命令行裁剪工具面（只要 bash + 文件）
- `--help`（现在会误开 TUI）
- `--max-turns` / 预算上限
- 会话 resume 的非交互形式

---

## 3. Claude Code 命令面（按能力族，不是抄旗标清单）

官方把无头叫做 Agent SDK CLI：`claude -p`。

### 3.1 发起与生命周期

| 能力 | 典型命令 | 作用 |
|---|---|---|
| 交互开场并带第一句 | `claude "explain this"` | 进 TUI，但已有首条 user |
| 无头一问一答后退出 | `claude -p "fix the bug"` | 脚本 / CI 主入口 |
| stdin 管道 | `cat log \| claude -p "explain"` | 把文件当题面 |
| 续最近会话 | `claude -c` / `claude -c -p "..."` | 同目录接着干 |
| 按 ID/名恢复 | `claude -r auth-refactor "..."` | 指定会话 |
| 指定 session UUID | `--session-id` | 评测可复现 |
| 恢复时分叉 | `--fork-session` | 不污染原会话 |
| 不落盘 | `--no-session-persistence` | 一次性容器 |
| 后台开跑立刻返回 | `claude --bg "..."` | 与 `-p` 互斥 |
| 退出码 | 成功 0，失败非 0 | 脚本可分支 |

### 3.2 权限与工具面

| 能力 | 典型命令 | 作用 |
|---|---|---|
| 跳过全部审批 | `--dangerously-skip-permissions` | 沙箱里无头刚需 |
| 权限模式 | `--permission-mode plan\|auto\|dontAsk\|bypassPermissions` | 比「全开/全关」细 |
| 预批准工具 | `--allowedTools "Read,Edit,Bash"` | CI 白名单 |
| 限制可见工具 | `--tools "Bash,Edit,Read"` | 对齐 Minimal 两工具 |
| 拒绝规则 | `--disallowedTools` | 去掉危险工具 |
| 额外可读目录 | `--add-dir ../lib` | 多根 |
| 独立 worktree | `claude -w feature-auth` | 任务隔离 |

### 3.3 输出与预算（无头才有意义）

| 能力 | 典型命令 | 作用 |
|---|---|---|
| 输出格式 | `--output-format text\|json\|stream-json` | Harbor 要 json |
| 输入格式 | `--input-format text\|stream-json` | 流式喂后续消息 |
| JSON Schema 终局 | `--json-schema '{...}'` | 结构化交差 |
| 限制回合 | `--max-turns 3` | 防跑飞 |
| 美元上限 | `--max-budget-usd 5` | 防烧钱 |
| verbose / 部分流 | `--verbose` `--include-partial-messages` | 轨迹 |

### 3.4 上下文与可复现

| 能力 | 典型命令 | 作用 |
|---|---|---|
| 精简启动 | `--bare` | 不自动发现 hooks/skills/MCP/CLAUDE.md；脚本推荐 |
| 替换/追加 system | `--system-prompt` `--append-system-prompt` | 评测固定人设 |
| 设置覆盖 | `--settings` `--setting-sources` | 容器内可控 |
| 指定模型 / effort | `--model` `--effort` | 对齐官分口径 |
| MCP 配置 | `--mcp-config` `--strict-mcp-config` | 显式接入 |

### 3.5 产品级子命令（Peer 现阶段不必齐）

`claude auth`、`claude mcp`、`claude plugin`、`claude doctor`、`claude agents`、`claude attach/stop/logs`、`claude update`、`claude ultrareview`、`claude --cloud`、Remote Control、self-hosted runner。

这些是「CLI 操作系统」。评测 P0 用不到。

---

## 4. Codex 命令面（按能力族）

Codex 把交互和脚本拆开：`codex` 进 TUI，`codex exec` 专门无头。

### 4.1 发起

| 能力 | 典型命令 | 作用 |
|---|---|---|
| 非交互执行 | `codex exec "fix failing tests"` | 对标 `claude -p` |
| stdin 题面 | `codex exec`（无 prompt 则读 stdin）或显式 stdin 开关 | 可喂 `instruction.md` |
| 默认沙箱只读 | `codex exec` 默认 read-only | 比「默认全开」更安全 |
| 允许改工作区 | `--sandbox workspace-write` | 编码题必需 |
| 整机（仅容器） | `--sandbox danger-full-access` | 对标 CC bypass |
| 不弹审批 | `--ask-for-approval never`（`-a never`） | 无头刚需 |
| 显式组合（现推荐） | `codex exec -s workspace-write -a never "..."` | `--full-auto` 已弃用 |
| 忽略用户配置 | `--ignore-user-config` `--ignore-rules` | 评测可复现 |
| 不落会话 | `--ephemeral` | 一次性 |
| 终局 schema | `--output-schema file.json` | 结构化交差 |

### 4.2 和 Claude 的差异（对 Peer 有用）

- Codex **子命令拆分**更干净：`exec` 不会和 TUI 旗标缠在一起。
- Codex **默认只读**，写文件必须显式开 sandbox；Claude `-p` 更依赖 `--allowedTools` / permission-mode。
- 两边都强调：全开权限只给一次性容器。
- Codex 官方文档对「从脚本跑」的叙事更短，旗标比 Claude 少，但 **exec + sandbox + approval** 三件套已经够 Harbor。

---

## 5. 对照矩阵

图例：有 = 产品命令已支持；部 = 能力在运行时/TUI 有、命令没有；无 = 没有。

| 能力族 | Claude Code | Codex | Peer CLI | 评测优先级 |
|---|---|---|---|---|
| 交互 TUI | 有 | 有 | 有 | 已有 |
| `--version` | 有 | 有 | 有 | 已有 |
| `--help` 不进会话 | 有 | 有 | **无**（会开 TUI） | P0 |
| 位置参数首条 prompt（交互） | 有 | 有 | 无 | P1 |
| 无头跑完退出 | `claude -p` | `codex exec` | **无** | **P0** |
| stdin 题面 | 有 | 有 | 无 | **P0** |
| 退出码交差 | 有 | 有 | 无（TUI 进程） | **P0** |
| `--output-format json` | 有 | 有（exec 输出） | 无 | **P0** |
| stream-json 轨迹 | 有 | 部 | 无 | P1 |
| 命令行权限/沙箱 | permission-mode / skip | sandbox + approval | 仅 TUI/设置 | **P0** |
| 命令行裁剪工具 | `--tools` | 配置/默认工具集 | 仅 mode projection | **P0** |
| `--model` / effort | 有 | 有 | 环境变量 + TUI | **P0** |
| `--workspace` / cwd | cwd + `--add-dir` | cwd + `--add-dir` | 仅 env | P0 可用 env |
| `--max-turns` / 预算 | 有 | 部 | 无 | P0（防飞） |
| resume / continue | 有 | 有 | 仅 TUI picker | P1 |
| 不落盘 / ephemeral | 有 | 有 | 无 | P1 |
| `--bare` 可复现启动 | 有 | `--ignore-user-config` | 无 | P1 |
| 追加/替换 system prompt | 有 | 配置 | System Context 源，无 CLI 旗标 | P1 |
| worktree 启动 | `--worktree` | 部 | Goal worktree 在产品内，无 CLI 旗标 | P2 |
| 后台 agent / attach | 有 | 部 | 无 | P2 |
| auth / mcp / plugin 子命令 | 有 | 有 | 无（TUI 内管理） | P2 |
| 云端会话 / remote | 有 | 有 | 无（刻意本地） | 不做 |
| 程序 SDK | Agent SDK | 应用/协议 | `runtime-sdk` 已有 | 库已有、CLI 未接 |

---

## 6. Peer 缺什么（按评测排序）

### P0 — 没有这些就无法自动评测

目标形态（名称可再议，语义必须有）：

```bash
peer exec \
  --access full \
  --tools bash,file \
  --model <id> \
  --effort max \
  --max-turns 80 \
  --output-format json \
  --workspace /task/workspace \
  "$(cat instruction.md)"
```

或 Codex 风格子命令等价：

```bash
peer exec --access full --tools bash,file --output-format json < instruction.md
```

P0 清单：

1. **`peer exec`（或 `peer -p`）**  
   不启动 TUI。读 prompt（argv 或 stdin）。跑 agent loop。打印结果。退出。

2. **`--help`**  
   打印用法后退出。现在 `peer --help` 会进 TUI，是事故。

3. **退出码**  
   `0` = 运行时正常结束（不等于题集 pass）。  
   非 0 = 认证失败、参数错、被取消、内部错误、触到 `--max-turns`。  
   **题过没过仍由 Harbor/Pier verifier 判**，不要让 Peer 当裁判。

4. **`--output-format text|json`**  
   json 至少含：`sessionId`、`ok`、`result`（最终助手文本）、`error`、`turns`、`usage`（若有）、`durationMs`。  
   不要把 Evidence 全文糊进默认 json；可加 `--include-evidence` 以后再做。

5. **`--access ask|session|full`**  
   映射已有 `ask_before_local` / `session_local` / `full_local`。  
   无头且 TTY 不存在时，`ask` 必须失败退出，不能挂起等按键。  
   评测容器用 `full`。不要引入名为 skip-permissions 的旁路；权限仍走 PermissionGrant，只是自动 grant。

6. **`--tools`**  
   限制 Runtime Projection 可见工具。评测最小集：`bash,file`（或现网 capability 名）。  
   这是对标 Claude `--tools` 和 DSH Minimal，不是换核。

7. **`--model` / `--effort`**  
   覆盖本轮，不写进用户全局设置（或明确 `--persist` 才写）。评测要对齐 `max` + 固定模型。

8. **`--workspace`**  
   覆盖 `PEER_WORKSPACE_ROOT`。容器里比改 env 更直观。

9. **`--max-turns`**  
   无头必须有硬上限。默认给一个保守值，评测可加大。

10. **非 TTY 默认走 exec 语义或直接拒绝开 TUI**  
    CI 里误调 `peer` 不应卡在全屏渲染。

### P1 — 评测稳定之后、日常脚本需要

- `--continue` / `--resume <id>`
- `--output-format stream-json`（轨迹给 Harbor）
- `--ephemeral` 或不写 `~/.peer-agent` 会话
- `--bare`：不自动挂用户 Skill/MCP/额外指令，只保留投影工具 + 本轮 prompt（可复现）
- `--append-system-prompt`（走 System Context 源，禁止拼接旁路）
- `--json-schema` 或等价终局校验
- 位置参数 `peer "首条消息"` 进交互（体验，非评测阻塞）

### P2 — 产品 CLI 操作系统，可晚

- `peer auth` / `peer mcp` / `peer doctor`
- `--add-dir` 多根
- `--worktree` 启动隔离
- 后台会话 attach/logs
- 云端/远程控制（与 Peer 本地优先冲突，默认不做）

---

## 7. 推荐命令草图（实现时再立 ADR）

建议学 **Codex 的子命令拆分**，不要学 Claude 把几十个旗标全挂在同一个 `peer` 上。

```text
peer                  交互 TUI（现状）
peer --version
peer --help
peer exec [options] [prompt]
```

`exec` 内部必须：

```text
System Context 组装
  → Runtime Projection（受 --tools / --mode 裁剪）
    → Tool Call
      → PermissionGrant（--access 只影响是否自动批准）
        → Evidence
          → stdout 摘要 + 退出码
```

禁止：

- exec 另开一套 bash/文件执行
- `--access full` 跳过 Evidence
- renderer/TUI 状态当权限真值
- 把题集 pass/fail 写进 Peer 退出码（那是 verifier 的事）

实现落点优先复用 `@peer-agent/runtime-sdk` + 现有 TUI host 的 provider/tool 装配，而不是从 Desktop 抄一条 IPC。这是 B 级：CLI 表面 + 权限在无头下的默认策略。若 `exec` 改变 Projection/权限语义，升 A 级并先改 ADR。

---

## 8. 和评测怎么接

Harbor / Pier 要的是 **installed agent**：容器里一条命令，吃 `instruction.md`，改工作区，退出。

有 P0 之后：

```text
# 容器内
peer exec --access full --tools bash,file \
  --output-format json --max-turns 80 \
  --workspace /workspace \
  --model "$MODEL" --effort max \
  - < /instruction.md
```

外层（人、Codex 或脚本）只负责起容器和跑 verifier。  
Peer 不判卷。

没有 P0 之前，用 runtime-sdk 写一次性 runner 也能评，但那是旁路产品面，评完还是要回到 `peer exec`。

---

## 9. 分期建议

| 阶段 | 交付 | 完成定义 |
|---|---|---|
| **P0** | `peer exec` + help + json + access + tools + model/effort + max-turns + 非 TTY | 同一道 Terminal Bench 或 DeepSWE 题，容器里能跑完并被官方测试打分 |
| **P1** | resume、stream-json、bare、ephemeral | 5 题 × 3 次可复现，轨迹可归档 |
| **P2** | 子命令生态 | 不阻塞评测 |

**第一步就是 P0。** 不要先做 auth 子命令、不要先做云、不要先对齐 Claude 全旗标表。

---

## 10. 明确不抄的东西

- 不把权限改名叫 `dangerously-skip-permissions`。Peer 已有 `full_local`，无头只是自动 grant，Evidence 还在。
- 不把 Agent loop 做成可卸插件来换 DSH 核。
- 不用 LLM（含 Codex）替代题集 verifier。
- 不把 Desktop 浏览器工具塞进 CLI exec 冒充对齐。

---

## 11. 给实现者的验收清单（P0）

- [ ] `peer --help` 打印用法，退出 0，不开 TUI
- [ ] `peer exec --help` 打印 exec 旗标
- [ ] `echo "list files in cwd" | peer exec --access full --tools bash,file --output-format json` 在无 TTY 下结束
- [ ] json 可被 `jq .ok` 解析
- [ ] `--access ask` 在无 TTY 下非 0 退出，并说明不能挂起
- [ ] `--tools bash,file` 时模型看不到 web/mcp/skill（有测试）
- [ ] 工具调用仍有 PermissionGrant + Evidence（有测试）
- [ ] 触达 `--max-turns` 非 0 退出
- [ ] Harbor 或手工容器：一题 `instruction.md` → exec → 官方测试能跑

---

## 12. 参考命令（外部，便于对照，不是 Peer API）

Claude（官方 headless）：

```bash
claude --bare -p --output-format json \
  --allowedTools "Read,Edit,Bash" \
  --permission-mode bypassPermissions \
  --max-turns 80 \
  "Fix the failing tests"
```

Codex（官方 noninteractive）：

```bash
codex exec --sandbox workspace-write --ask-for-approval never \
  "Fix the failing tests"
```

Peer 目标（本文建议，尚未实现）：

```bash
peer exec --access full --tools bash,file \
  --output-format json --max-turns 80 \
  "Fix the failing tests"
```
