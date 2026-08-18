# 66. 会话级持久 Shell

创建时间：2026-08-18
最后更新：2026-08-18

状态：Proposed（先立契约，再改 `runtime-node` / Desktop adapter）

级别：A 级（能力执行形态、权限粒度、Evidence 切分、进程生命周期）

关联：

- `knowledge/architecture/20-architecture-governance.md` — 主链不可旁路
- `knowledge/architecture/22-tui-desktop-shared-runtime-and-host-governance.md` — 双宿主共享内核；UserTurn / ModelStep / ToolCall
- `knowledge/architecture/desktop-cli-local-capability-parity.md` — 本地能力对齐
- `knowledge/decisions/35-mode-scoped-tool-projection.md` — 模式投影
- `knowledge/decisions/49-cancel-path-hard-sandbox.md` — 无路径硬沙箱；审批轴仍在
- `knowledge/decisions/51-unified-desktop-cli-file-tools.md` — 文件工具是独立能力，不并进 Shell
- `knowledge/decisions/65-cli-headless-exec.md` — `peer exec` 是第三宿主适配，不是第三套 Runtime
- `playbook/change-intake.md` — 入口与提交纪律

---

## 程序位置

本决策是「请求循环 + 工具工作面」三切片里的 **切片 2**。三切片一起推进，但契约分开写：

| 切片 | 级别 | 改什么 | 本文是否立约 |
|---|---|---|---|
| 1. Inner-loop 卫生 | B | UserTurn 内钉死 System/tools 前缀；整批只读文件工具可并行；远离压缩线时跳过 exact count | 只记录不变量，不另开 ADR |
| **2. 持久 Shell** | **A** | 同会话前台 `local.shell.exec` 默认进入同一只活着的 shell | **本文** |
| 3. `read_file` 行范围 | A | manifest 增加 `start_line` / `end_line` | 另文，不在本次范围 |

切片 1 不新增能力、不改 PermissionGrant / Evidence 形状。切片 2 改的是 **同一 capability 的进程模型**，所以必须先写本文。

---

## 背景

当前 `local.shell.exec` 每次前台调用都是新进程：`spawn(shell, ['-lc', command])`。`cd`、虚拟环境、`export`、工作目录在下一步全部丢失。模型只能把包装命令写进每一条 `command`。

对照同一模型、同一题面的 DeepSeek official harness：一只持久 bash 跨 150+ 次调用保持 cwd / env。Peer 评测里多出来的大量 model step，有一部分是在重做「进入目录、激活 venv、再跑 pytest」。

已有的 Desktop login-env snapshot（为 `-lc` 注入用户环境）**不是**持久会话。它只让每个新进程长得像登录后的环境，下一步仍然是新进程。

文件工具已经按 ADR 51 独立存在（`read_file` / `edit_file` 等）。本文不把编辑器并进 Shell，也不为评测另开一条 bash。

---

## 决策

### 1. 不换工具名，换执行形态

公开契约保持：

```text
toolName: bash
capabilityId: local.shell.exec
```

`local.shell.stop` 继续只停 **后台任务**（`background: true` 那条已有 spawn）。持久会话不是后台任务，不复用 `shell_<uuid>` 任务 id 语义。

禁止：

- 新增 `persistent_bash` / `bash_session` 等第二套投影给模型选
- 只给 `peer exec` 开持久会话、交互 TUI / Desktop 仍用一次性 `-lc`
- 用宿主拼 `cd && export` 假装持久（假持久）

### 2. 会话键与寿命

一只前台会话对应：

```text
(conversationId, workspaceRoot)
```

- 第一次前台 `local.shell.exec` 创建进程；默认 cwd 为该会话的 `workspaceRoot`
- 同键后续前台调用进入同一进程
- 会话结束、UserTurn 被 abort、宿主退出、工作区切换：必须杀掉进程组
- Goal / exec 各自有自己的 `conversationId`，不跨会话共用一只 shell

Windows：本决策先覆盖 POSIX。未实现前允许该宿主继续走一次性 `-lc`，但不得因此长出第三条能力 id。

### 3. 主链不缩短

每一条命令仍然走：

```text
Capability Provider → Manifest → Runtime Projection → Tool Call → PermissionGrant → Evidence
```

持久不是站立授权：

- classifier 仍按 **本条 command** 分级（allow / ask / deny）
- PermissionGrant 仍按 **本条** 记录
- 用户拒绝本条：命令不进入会话 stdin；**不**因此杀掉会话
- 创建进程本身不是一次额外授权

`full_local` / `session_local` / `ask_before_local` 语义不变。ADR 49 的「无路径硬沙箱」仍然适用：会话里 `cd` 到工作区外是允许的，风险仍由审批与 deny 规则承担。

### 4. 进程协议

用长寿命交互式 shell（非每条 `-lc`），以 **不出现在用户命令里的结束标记** 框住一次调用的 stdout / stderr：

1. 把本条 `command` 交给同一进程
2. 等到约定标记，或碰到本条 `timeoutMs`
3. 标记之前的输出写入 **本条** Evidence / artifact，不是整段会话录像

`cwd` 参数：

- 省略：在会话当前目录执行
- 提供且与会话 cwd 不同：先在同一调用内 `cd`，再执行 `command`；`cd` 与命令共一份 Evidence
- 模型也可以在 `command` 里自己 `cd`；两种写法都必须让下一步看见新目录

超时与卡死：

1. 先向会话进程组发 SIGINT
2. 仍不结束则 SIGTERM 并 **丢弃该会话**（下一步前台调用重建）
3. 不得留下一只半死、标记错乱的进程给后续工具调用

`background: true` **不**进入持久会话，仍走现有 task manager + `local.shell.stop`。

同批多条 `local.shell.exec`：对同一会话键 **串行**（互斥）。切片 1 的并行只适用于只读文件能力；Shell 永不并行进同一只会话。

### 5. Evidence 按命令切

每条前台调用的 Evidence / artifact 只包含：

- 本条 command（及因 `cwd` 参数插入的 `cd`）
- 本条 stdout / stderr / exit
- 执行后的 cwd（若能观测）
- 会话仍存活或已重建的事实

禁止把整段会话历史当作这一次 Tool Result。大输出仍按现有 shell artifact / 预览上限回捞，不回退到把普通输出二次材料化成 `tool-tui-tool-*.txt`。

### 6. 实现落点

新 Module，不要把 `shell-provider` 做成神模块：

```text
runtime-node Shell Session
  → shell-provider（前台 exec 默认走 Session）
    → TUI / exec 共用
Desktop adapter 接同一语义；能共用实现则共用，不能则只做适配
```

Desktop 现有 login-env snapshot 可以用来 **播种** 会话的初始环境，不能代替会话本身。

### 7. 切片 1 必须遵守的不变量（B 级，与本文同时生效）

这些不是新能力，但是落地持久 Shell 之前就要锁住，否则前缀抖动会把会话收益吃掉：

1. **三层循环**（两端同一 `RuntimePipeline`）：

   ```text
   UserTurn    一次用户提交 / 一次 peer exec
     ModelStep 一次 provider.stream（runTurn）
       ToolCall 受治理执行
   ```

2. **前缀钉死**：一次 UserTurn 内，System Context 字节与 tools schema 字节不得重算、重排、重写。Compaction 可以丢历史、换 handoff，但必须复用本次已钉住的 system 消息，不得重新 assemble。
3. **只读并行**：当且仅当同一 ModelStep 的全部 ToolCall 都属于 `local.file.read` / `local.file.list` / `local.file.search` 时，可以并行执行；结果仍按模型给出的 calls 顺序回灌。任何 Shell、写文件、编辑、MCP、未知 capability 都让整批回到串行。
4. **增量记账**：上一请求的 observed percent 加上本步新增 tool 文本的估算，仍明显低于压缩触发线时，允许跳过 exact `countRequest`，直接 send，仍以本次 provider usage 为权威观察。接近触发线、首次请求、window 未知时不得跳过。
5. **禁止**服务端 tool loop（模型在云上自己执行工具）。PermissionGrant 与 Evidence 必须留在本地。

切片 3（`read_file` 行范围）另开 ADR，不在本文授权改 manifest。

---

## 非目标

- 不把 `vim` / 交互式 REPL 做成一等 TTY 产品
- 不引入 OS container / seatbelt 作为本决策的替代
- 不删除文件五件套，不把 `str_replace_editor` 做成新 capability
- 不靠加长 System Context 弥补「每步都是新 shell」
- 不把持久会话做成跨 conversation 的用户级全局 bash

---

## 后果

### 正向

- 模型可以 `cd`、`source .venv/bin/activate`、连续 `pytest`，不必每步重写包装
- Desktop / TUI / `peer exec` 看见同一只 `bash`，评测不是旁路
- 权限与 Evidence 仍按命令可审计

### 代价

- 会话内残留状态（被改掉的 cwd、导出的密钥、被 `cd /` 带跑的下一步）是刻意换来的工作面，不是缺陷；审批按命令看，不按「会话看起来还在 workspace」
- 超时要能拆掉并重建会话，实现比 `-lc` 重
- 同批两条 bash 必须排队，不能和只读文件并行混用同一把锁的错误实现

### 风险与缓解

| 风险 | 缓解 |
|---|---|
| 标记碰撞或二进制输出打乱协议 | 标记对用户命令不可预测；二进制按字节边界收集到超时 |
| 卡死的 `yes` / 分页器 | 本条 timeout → SIGINT → 重建 |
| 实现只进 exec | 契约写明三宿主同一 capability；缺 Desktop/TUI 不算落地 |
| 并行切片误伤会话 | 并行白名单不含 `local.shell.*` |

---

## 验证

落地时至少覆盖：

- 连续两条前台 `bash`：第二条看见第一条的 `cd` / `export`
- 拒绝一条高风险命令后，会话仍在，下一条仍能执行
- abort / 会话结束 / 工作区切换后无残留进程组
- 超时后下一前台调用能重建并执行
- `background: true` 仍走 task id + `local.shell.stop`，不进会话
- 同批两条 `bash` 串行且顺序稳定
- Evidence 只有本条输出，不含上一条
- TUI 与 Desktop（或共享 Module 的契约测试）行为一致
- 不存在第二条模型可见的 bash 工具名

切片 1 同步验证：

- UserTurn 内连续 ModelStep：system 与 tools 的稳定指纹不变（未发生 compaction epoch 前进时）
- 整批 `read_file`×N 并行，回灌顺序与 calls 一致
- 只读+`bash` 混批保持串行
- 远离压缩线时 exact count 被跳过；接近触发线时仍计数

---

## 实现锚点（代码仓）

| 组件 | 职责 |
|---|---|
| `packages/runtime-node` 新 Session Module | 进程、标记、互斥、teardown |
| `packages/runtime-node` `shell-provider` | 前台默认进 Session；background 仍走 task manager |
| `packages/runtime-sdk` `RuntimePipeline` | 切片 1：只读整批并行 |
| TUI `provider-chat-model` | 切片 1：钉前缀、复用 system、按阈值跳过 exact count |
| Desktop shell adapter | 同一会话语义；可用 snapshot 播种初始 env |

代码未合入前，本文保持 Proposed。合入并通过上表验证后改为 Accepted。
