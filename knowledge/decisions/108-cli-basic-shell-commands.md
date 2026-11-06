# ADR 108：CLI 基础壳命令

创建时间：2026-11-06
最后更新：2026-11-06

状态：Accepted（2026-11-06 用户要求按本文实现；实现未发布验收）

级别：A（新增壳命令，以及会话删除要沿用既有存储级联）

关联：

- `knowledge/decisions/48-cli-first-class-release.md` — 安装面与版本查询；本文收窄其中「CLI 自动更新可缓做」
- `knowledge/decisions/65-cli-headless-exec.md` — `peer exec` 契约；本文不改它的权限、退出码和 P0 旗标
- `knowledge/decisions/34-conversation-delete-goal-plan-cascade.md` — 删除会话时级联目标计划
- `knowledge/decisions/76-peer-acp-agent.md` — `peer acp` 保持独立入口
- `knowledge/architecture/20-architecture-governance.md` — 主链不可旁路
- `knowledge/architecture/22-tui-desktop-shared-runtime-and-host-governance.md` — 双宿主共享 `~/.peer-agent`

代码事实（起草时，`PeerAgent/dev/0.1.0`）：壳入口有交互会话、`bots`、`--classic`、`exec`、`result`、`result-cleanup-receipt`、`acp`、`--version`、`--help`。经典界面有 20 条 `/` 命令，机器人界面另有 19 条。`peer update` 只有候选实现，未进入已发布 CLI。没有 `peer login`。

---

## 背景

CLI 已经能安装、进会话、无头执行和打印版本。缺的是不打开全屏界面也能完成的基础操作：升级已安装的 `peer`、查看本机会话、列出已配置模型、检查本机是否能跑、生成 shell 补全、导出一份会话文本。

这些缺口不是另一套运行时。模型通道的 OAuth 和 API Key 继续是模型服务的凭据；Gateway 的 OIDC 继续是远程接入的外部身份源。Peer 没有自己的账号、用量或订阅登录。

---

## 决策

基础壳命令只有这六条：

```text
peer update [--check]
peer sessions [list|resume|delete]
peer models
peer doctor
peer completions <bash|zsh|fish>
peer export <session-id>
```

命令在加载交互界面之前分流。没有 TTY 也可以运行，除了 `sessions resume`。帮助、版本和未知旗标沿用 ADR 65：帮助退出 0，用法错误退出 2。诊断走 stderr，可管道读取的正文走 stdout。

六条命令都不新开能力链，不读 renderer 的权限状态，不用助手文本充当执行结果或 Evidence。

### 1. `peer update`

安装当前通道里更新的已发布版本。

| 规则 | 含义 |
|---|---|
| 通道 | `x.y.z` 只看正式版，`-beta.N` 只看 beta，`-rc.N` 只看 rc。不跨通道，也不把 rc 降到旧正式版 |
| `--check` | 只报告当前版本、目标版本和来源，不下载、不替换 |
| 节流 | 显式命令每次都检查。24 小时记录和 `PEER_AGENT_NO_UPDATE_CHECK=1` 只作用于经典界面的后台提示 |
| 安装来源 | npm 全局包装执行 `npm install --global`；pnpm 执行 `pnpm add --global`；发行包归档替换同目录的 `peer` 与 `peer-credential-helper` |
| 失败 | 非 0 退出，已安装版本保持不变 |
| 完成 | 打印目标版本，并说明需要重新打开 `peer`。本命令不重启正在运行的 Desktop、CLI 或 Gateway |

发行包路径只替换文件名是 `peer` 或 `peer.exe` 的当前可执行文件。当前进程是 `bun`、`node` 或其他宿主时拒绝替换。

经典界面里已有的后台提示可以保留：它仍然先确认再安装。默认机器人界面不因为本文新增自动安装。无人值守升级、切换通道、指定任意版本、同时升级 Desktop 或 Gateway，都不在本文。

ADR 48 里「阶段一可不做 CLI 自动更新」收窄为：仍不做无人值守安装。显式 `peer update` 属于基础命令。

### 2. `peer sessions`

读写现有 conversation-store 和 `~/.peer-agent`，不建第二套会话目录。

| 子命令 | 行为 |
|---|---|
| `list`（默认） | 只读列出本机会话的 id、标题和更新时间。不打印消息正文、密钥或 Evidence |
| `resume <id>` | 有 TTY 时打开该会话的交互界面。无 TTY 退出 2，并提示使用 `peer exec`。不在此命令里跑一轮模型 |
| `delete <id>` | 删除这一条会话，并沿用 ADR 34 的目标计划级联。必须给出 id；默认不批量删除 |

`delete` 在 TTY 上先确认；非 TTY 必须显式 `--yes`，否则退出 2。它不清理凭据、权限授予、数据根或其他会话。找不到 id 时非 0 退出，不把空结果当成删除成功。

ADR 65 仍不给 `peer exec` 增加 `--resume`。恢复交互会话走 `peer sessions resume`。

### 3. `peer models`

只读打印本机已经配置、并且当前目录或全局设置能够选中的模型。字段至少包括 provider id、model id 和显示名。同名模型必须能区分 provider。

不访问网络，不刷新供应商目录，不打印 API Key、OAuth token 或刷新令牌。没有可用模型时退出 0，并在 stderr 说明尚未配置。选择和切换仍留在会话内的模型选择器，或 `peer exec --model`。

### 4. `peer doctor`

只检查，不修复，不安装，不登录，不改配置。

必查三项：

1. 当前 `peer` 与同目录的 `peer-credential-helper` 都存在且可执行。
2. 数据根 `~/.peer-agent`（或 `PEER_AGENT_HOME`）存在或可以创建，并且本次进程能写检查所需的位置。检查本身不写用户会话。
3. 报告当前版本号。

终端是否为 TTY、颜色和剪贴板只作为附加说明，不单独导致失败。必查失败时退出 1，并给出失败项。不把模型供应商的在线状态算进 doctor；那需要网络和凭据，不属于本命令。

### 5. `peer completions`

向 stdout 打印一份补全脚本，只接受 `bash`、`zsh`、`fish`。脚本覆盖本文的六条命令，以及已经存在的 `exec`、`bots`、`acp`、`result`、`--classic`、`--help`、`--version`。

不写 shell 配置文件，不探测当前 shell。未知 shell 退出 2。

### 6. `peer export`

把一条已存储会话的可见消息导出为 Markdown。来源是 conversation-store，不是一次新的模型生成。

```text
peer export <session-id> [--output <path>]
```

未给 `--output` 时写到 stdout。目标路径已存在则拒绝，除非显式 `--force`。导出不包含密钥、OAuth token、工具原始凭据。文件是阅读副本，不作为 Evidence，也不写回会话。找不到会话时非 0 退出。

---

## 明确不做

- `peer login`、`logout`、`usage`，以及任何 Peer 自有账号、计费或订阅命令。
- 把模型通道 OAuth 或 Gateway OIDC 包装成上述登录命令。
- `mcp`、`memory`、`plugin` 的壳管理。会话内已有入口的，继续留在会话内。
- Grok 宿主专有能力：`clone`、`worker`、`wrap`、`leader`、`setup`、`trace`、`du`、`dashboard`。
- 补齐 Grok 的 61 条内置 `/` 命令。
- 改变 `peer exec` 的默认权限、退出码、`--tools` 或回合上限。
- 改变 `peer acp` 的协议分流。

---

## 实现约束

1. argv 解析继续留在小型模块。`index.tsx` 只做分流，不堆积旗标。
2. `update` 复用现有安装来源判断和发行包替换，不另写下载器。
3. `sessions` 与 `export` 复用 `@peer-agent/conversation-store`。删除必须走与 ADR 34 相同的级联，不在命令里直接删文件树。
4. `models` 复用 CLI 现有模型配置读取。不把模型列表请求做成新的 Provider 执行路径。
5. 六条命令的测试覆盖：帮助与用法错误、通道不交叉、`--check` 不安装、发行包拒绝替换非 `peer` 可执行文件、会话删除需要确认或 `--yes`、导出拒绝覆盖、doctor 在 helper 缺失时失败、补全脚本只进 stdout。

建议落地顺序：`update`、`models`、`doctor`、`completions`、`sessions list`、`export`、`sessions resume`，最后才是 `sessions delete`。前一项未按上面的失败语义验证，不开始下一项里会写数据的命令。

`peer update` 的已有候选只说明命令形态可行。其余命令按本文约束实现；未做发布验收。
