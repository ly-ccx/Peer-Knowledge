# 65. CLI 无头发起（`peer exec`）

创建时间：2026-08-18
最后更新：2026-08-18（`exec` 默认不再设 `--max-turns` 上限）

状态：Accepted（P0 已落地；补充提供商/模型消歧；默认无回合上限）

级别：A 级（新增命令面、无头权限默认策略、Runtime Projection 裁剪入口）

关联：

- `design/product/cli-scripting-and-headless-gap.md` — 调研与分期；本文收成实现契约
- `knowledge/architecture/20-architecture-governance.md` — 主链不可旁路
- `knowledge/architecture/22-tui-desktop-shared-runtime-and-host-governance.md` — 双宿主共享内核
- `knowledge/architecture/desktop-cli-local-capability-parity.md` — 本地能力对齐（工具面，不是 argv）
- `knowledge/decisions/26-agent-loop-termination.md` — 回合预算耗尽是错误，不是成功
- `knowledge/decisions/35-mode-scoped-tool-projection.md` — 模式投影；`--tools` 叠在其上
- `knowledge/decisions/48-cli-first-class-release.md` — 安装面已有；本文补脚本面
- `knowledge/decisions/51-unified-desktop-cli-file-tools.md` — 文件工具公开名
- `playbook/change-intake.md` — 入口与提交纪律

代码审计基线（起草时）：`apps/tui/src/index.tsx` 仅 `peer --version` / `-v` 快路径；其余 argv 一律开 OpenTUI。

---

## 背景

CLI 安装面已经一等（ADR 48）。TUI 已能走完整主链：

```text
Capability Provider → Manifest → Runtime Projection → Tool Call → PermissionGrant → Evidence
```

缺的是命令行契约：一条命令吃题面、不弹审批、跑完退出、用退出码和 stdout 交差。

没有这条契约时：

- Harbor / Pier / CI 无法把 Peer 当 installed agent
- Cursor 等外部 Agent 没有正经驱动面，只能点 Desktop 窗口
- `peer --help` 会误开 TUI，非 TTY 会卡在全屏渲染

本文只立 **P0 评测最小集**。不抄 Claude / Codex 全旗标，不把 Desktop Computer Use 做成替代方案。

---

## 决策

### 1. 命令形态学 Codex，不学 Claude 单入口堆旗标

```text
peer                 交互 TUI（现状，TTY 专用）
peer --version / -v  打印版本，退出 0（已有）
peer --help          打印用法，退出 0，不开 TUI
peer exec [options] [prompt]
peer exec --help     打印 exec 旗标，退出 0
```

不采用 `peer -p` 作为主入口。实现期可把 `-p` / `--print` 收成 `exec` 的隐藏别名，但不写进 P0 验收。

`peer` 在非 TTY 且未给出 `exec` / `--help` / `--version` 时：**拒绝开 TUI**，非 0 退出，并提示改用 `peer exec`。不把裸 `peer` 自动解释成 exec（避免 CI 误调、无 prompt 空跑）。

### 2. `exec` 是第三宿主适配，不是第三套 Runtime

`exec` 与 Desktop / 交互 TUI 共用同一套内核。它是 CLI 宿主的无头适配：

```text
argv / stdin
  → System Context 组装（现有源，禁止字符串旁路拼接）
    → Runtime Projection（模式投影 ∩ `--tools` 允许集）
      → Tool Call
        → PermissionGrant（`--access` 只影响是否自动批准）
          → Evidence
            → stdout 摘要 + 退出码
```

实现落点：

- 解析与帮助：`apps/tui` 新增小型 argv 模块，不要把 `index.tsx` 做成神模块
- 装配：复用现有 `createTuiHost`、provider bundle、`@peer-agent/runtime-sdk` Pipeline、会话存储
- 禁止：另开 bash/文件执行；从 Desktop 抄一条 Electron IPC；为评测写一次性 runner 当产品面

`@peer-agent/runtime-sdk` 与 `examples/external-host` 继续是库/嵌入证明，不是 `peer` 命令。

### 3. Prompt 来源

优先级：

1. `peer exec` 后的位置参数，按空格拼接为一条 user 文本
2. 若无位置参数，且 stdin 不是 TTY，则读完 stdin
3. 两者都空：用法错误，退出码 `2`

P0 不做：把 stdin 当附件、多轮 `--input-format stream-json`、`--prompt-file`。

### 4. 退出码：Peer 交差运行时，不判题

| 码 | 含义 |
|---|---|
| `0` | 运行时正常结束（模型给出终局回复）。**不等于**题集 pass |
| `2` | 参数 / 用法错误（含无 prompt、未知旗标、无 TTY 的 `--access ask`） |
| `3` | 认证或模型配置不可用 |
| `4` | 被取消 |
| `5` | 触达 `--max-turns`（`agent_loop_exhausted`） |
| `1` | 其它内部 / provider / 工具运行时错误 |

题过没过由 Harbor / Pier verifier 判。禁止把测试绿/红写进 Peer 退出码。

与 ADR 26 一致：耗尽回合预算是错误，不是 `chat:stream:done`。

### 5. `--output-format text|json`

默认 `text`：只把最终助手文本打到 stdout；诊断走 stderr。

`json` 一行或一块可被 `jq` 解析的对象，字段至少：

| 字段 | 含义 |
|---|---|
| `sessionId` | 本轮会话 id |
| `ok` | 是否运行时正常结束（与退出码 `0` 对齐） |
| `result` | 最终助手文本；失败时可为 `null` |
| `error` | 失败时的稳定错误码 / 短消息；成功时 `null` |
| `turns` | 实际模型回合数 |
| `durationMs` | 墙钟 |
| `usage` | 若本轮已有用量账本则带上；没有就省略或 `null` |

禁止把 Evidence 全文、工具 stdout、密钥打进默认 json。`--include-evidence` 列为 P1，不在本文实现。

### 6. `--access ask|session|full`

只是现有 `LocalAccessLevel` 的命令行别名，不发明第四档，不引入 `dangerously-skip-permissions`。命令行发起 ≠ `full_local`。

分层默认：

| 入口 | 默认权限 | 原因 |
|---|---|---|
| 交互 `peer` | `ask`（现网不变） | 人在终端，可以审批 |
| `peer exec` | `session` | 无审批人，但不能把「开跑」当成「任意高风险」 |
| Harbor / 评测容器 | 必须显式 `--access full` | 解题常含破坏性/特权命令；默认不得静默全开 |

| 旗标 | 协议值 | 无头行为 |
|---|---|---|
| `ask` | `ask_before_local` | **无 TTY 必须立刻失败（退出码 `2`）**，不能挂起等按键 |
| `session` | `session_local` | 沿用现网 `createTuiHost` 自动批准：`file-write` 放行；`shell-exec` 在风险 ≤ `L3_external_write` 时放行。`L4_privileged` / `L5_destructive`（如 `sudo`、`rm`）在无 TTY 下对该次调用 **deny + Evidence**，不得阻塞进程 |
| `full` | `full_local` | 自动 grant；仍走 PermissionGrant + Evidence |

`exec` 未传 `--access` 时用 `session`。评测脚本必须自己写 `--access full`，帮助文本要写明这一点。

`--access` **只覆盖本轮**，默认不写用户全局设置。P0 不做 `--persist`。

`restricted_local` 不出现在 P0 旗标里。

### 7. `--tools` 是 Projection 允许集，不是换核

`--tools` 在 **Runtime Projection** 上再裁一刀，与 ADR 35 的模式投影取交集。模型看不到的工具不能被调用。

P0 别名（对外短名 → 现网 capability）：

| 别名 | 放入允许集的 capabilityId |
|---|---|
| `file` | `local.file.read` `local.file.list` `local.file.search` `local.file.edit` `local.file.write` |
| `bash` | `local.shell.exec` `local.shell.stop` |

也接受规范 tool 名或 capabilityId（`read_file`、`local.file.read`）。未知 token：用法错误，退出码 `2`。

未传 `--tools`：沿用当前 TUI 在该 `--mode` 下的投影（含已注册 Skill/MCP）。评测必须显式 `--tools bash,file`。

Desktop-only `browser_*` **不得**因 `--tools` 被投影进 CLI exec。CLI 读网页继续用 `web_fetch`。

`request_user_input` 在无 TTY 下即使被投影，调用也必须失败退出该 tool（deny + Evidence），不得挂起。

### 8. `--model` / `--effort` / `--mode` / `--workspace` / `--max-turns`

| 旗标 | 语义 |
|---|---|
| `--provider <id>` | 只覆盖本轮；匹配目录里的 `providerId`（Desktop groupId / credential id）或 `entryId` |
| `--model <id>` | 只覆盖本轮。可以是裸 `modelId`，或协议复合名 `providerId::modelId` |
| `--effort <level>` | 只覆盖本轮；取值走现网 provider 已支持的 effort |
| `--mode chat\|plan\|goal` | 默认 `chat`；投影仍受 ADR 35 约束 |
| `--workspace <path>` | 覆盖 `PEER_WORKSPACE_ROOT`；必须是已存在目录 |
| `--max-turns <n>` | 可选无头硬上限。未传则不设回合上限，跑到模型终局、取消或运行时错误为止。传入正整数时，触达即退出码 `5`。 |

未传 `--provider` / `--model`：沿用现有 TUI 模型解析（环境变量 + Desktop 默认）。

模型身份与协议一致：`providerId::modelId`（`contextAccountingModelKey`）。**不要用 `/` 拼接**——OpenRouter 等模型 id 本身含斜杠。

同 `modelId` 被两家提供商共用时：

- 裸 `--model gpt-4o` 必须失败（退出码 `2`），并列出 `providerId::modelId` 候选
- 消歧用 `--provider openai-1 --model gpt-4o`，或 `--model openai-1::gpt-4o`
- `--provider` 与 `--model provider::model` 指向不同提供商时，用法错误

`exec` 默认不设回合上限。未传 `--max-turns` 时，无头入口向 RuntimePipeline 传入 `Infinity`，覆盖内核默认 64。需要防飞时由调用方显式传 `--max-turns`。交互 TUI 的默认循环策略仍以 ADR 26 为准，不因本文改成默认有界。

### 9. P0 明确不做

- `--continue` / `--resume` / `--ephemeral` / `--bare`
- `--output-format stream-json`、`--json-schema`
- `--append-system-prompt`（若做，必须走 System Context 源，另立修订）
- `peer auth` / `mcp` / `doctor` / 后台 attach
- 用无头浏览器冒充 Desktop `browser_*`
- 让 Cursor / Codex 点 Peer Agent.app（Computer Use 不是本契约）
- 用 LLM 替代题集 verifier

---

## 实现约束

1. 新 Module 只增加 Locality：argv 解析、exec 生命周期、stdout 编码器分开；不要在 `index.tsx` 里堆旗标。
2. 权限真值仍在 host / runtime，不在 TUI 组件 state。
3. `full` 自动批准仍要写 PermissionGrant 与 Evidence。
4. Provider 请求整形继续走现有 encoder，不在 exec 里分叉 OpenAI / Anthropic 消息形状。
5. 本 ADR 被接受后，实现按 B 级在代码仓落地；若实现时改了 Projection / 权限语义，先回写本文再改代码。

建议代码落点（实现时核对，不把本机路径写进仓）：

- `apps/tui/src/cli-argv.ts`（或同级）— 解析与帮助
- `apps/tui/src/cli-exec.ts` — 无头生命周期
- 复用 `tui-host.ts`、`tui-permission-policy.ts`、model-config、System Context 组装
- 测试：argv、默认 `session`、无 TTY `ask`、`--tools` 投影、退出码、json 形状、max-turns

---

## 验收（P0）

- [ ] `peer --help` 打印用法，退出 0，不开 TUI
- [ ] `peer exec --help` 打印 exec 旗标，退出 0
- [ ] 非 TTY 下裸 `peer` 非 0 退出，并提示 `peer exec`
- [ ] `echo "list files in cwd" | peer exec --access full --tools bash,file --output-format json` 在无 TTY 下结束
- [ ] json 可被 `jq .ok` 解析，含 `sessionId` / `result` / `error` / `turns` / `durationMs`
- [ ] 未传 `--access` 时 `exec` 使用 `session`（有测试）
- [ ] `--access ask` 在无 TTY 下退出 `2`，说明不能挂起
- [ ] 无 TTY + `session` 下，`L5_destructive` shell 被 deny 且进程不挂起（有测试）
- [ ] `--tools bash,file` 时模型看不到 web / mcp / skill / browser（有测试）
- [ ] 工具调用仍有 PermissionGrant + Evidence（有测试）
- [ ] 未传 `--max-turns` 时 `exec` 不因回合预算结束；显式传入后触达退出 `5`，`ok=false`
- [ ] Harbor 或手工容器：一题 `instruction.md` → exec → 官方测试能跑；Peer 退出码不表示题过没过

---

## 后果

### 正向

- 评测、CI、外部 Agent 有一条受治理的发起面
- Cursor 可用 `peer exec` 驱动 Peer，而不必点 Desktop
- 安装面（ADR 48）与脚本面分离：已安装的 `peer` 终于能当脚本 SDK

### 代价

- CLI 宿主要维护交互 / 无头两套入口，但必须共享同一 host 装配
- `--tools` 别名要保持与 `SHARED_LOCAL_TOOL_CONTRACTS` 同步
- 无头 `session` 档对「仍需人审」的调用是否算运行失败，实现时要在 stdout `error` 里写清；默认：**单次 tool deny 不自动把整轮打成退出码 `1`**，除非模型因此无法终局。此条若在实现中不够用，再修订本文

### 明确不采用

| 选项 | 原因 |
|---|---|
| `peer -p` 当唯一入口 | 和 TUI 旗标缠在一起，后续 P1 会炸 |
| `exec` 默认 `--access full` | 发起 ≠ 全开；`rm` / `sudo` 必须显式 `full` |
| `exec` 默认 `--access ask` | 无 TTY 下等于一开跑就失败，日常脚本不可用 |
| 无头跳过 Evidence | 破坏主链 |
| 退出码表示题集 pass | 越权当裁判 |
| 为 Harbor 写 SDK 旁路 runner 当产品 | 评完仍要回到 `peer exec` |

---

## 分期

| 阶段 | 本文 |
|---|---|
| P0 | 上述全部。接受本文后才在代码仓开工 |
| P1 | resume、stream-json、ephemeral、bare、system prompt 源；另开修订或后续 ADR |
| P2 | auth / mcp / doctor / worktree 启动；不阻塞评测 |

---

## 参考命令（目标形态，不是现网）

```bash
peer exec --access full --tools bash,file \
  --output-format json \
  --workspace /workspace \
  --provider "$PROVIDER" --model "$MODEL" --effort max \
  - < /instruction.md

# 等价复合写法。分隔符是 ::，不要用 /。
peer exec --model openai-1::gpt-4o "summarize this repo"
```
