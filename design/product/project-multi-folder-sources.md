# 项目多文件夹方案：主文件夹 + 附加源

> 创建时间：2026-08-13
> 最后更新：2026-08-13
> 文档状态：目标方案 / 按本文实施
> 适用范围：Peer Desktop 侧栏项目、工作区设置、Agent 可读根与写路由
> 关联代码仓：`peer_agent`
> 关联文档：
> - `design/product/workspace-sandbox-evolution-comparison.md`
> - `design/product/task-worktree-delivery-product-design.md`
> - `knowledge/decisions/27-workspace-switch-and-cross-workspace-running.md`
> - `knowledge/decisions/49-cancel-path-hard-sandbox.md`

## 1. 一句话

对外一个「项目」可以挂多个文件夹；对内仍是「一个主执行世界 + 若干附加源」，不把两个 Git 仓合成一个 Workspace。

## 2. 为什么现在做

用户从知识库发起、去改代码仓，是最常见的跨项目路径。Codex 的做法是：一个项目（如 `peer-knowledge`）可以同时挂：

- `~/Documents/MiaoYan/peer-knowledge`（主要）
- `~/Documents/DEV/github/peer_agent`（附加）

这解决的是**入口和可见性**：同一会话里同时看见两个相关目录。

它解决不了、也不该假装解决的是：

- 这次写到哪个仓
- 会话、记忆、Skill 属于谁
- 两个任务同时改同一仓时如何隔离
- 跨仓原子提交（明确不做）

所以本方案借 Codex 的产品壳，保留 Peer 已有的 origin / target 执行契约。

## 3. 当前事实

代码审计基线：`peer_agent` 工作区服务仍是单根。

| 层 | 现状 |
|---|---|
| 设置 | `workspaces: [{ path, name, addedAt }]`，另有 `activeWorkspace` |
| IPC | `list` / `ensure-default` / `add` / `set-active` / `remove` / `info` |
| 侧栏 | 每个工作区一行芯片；右击只有「在 Finder 中显示」「移除」 |
| Agent 可见根 | 系统上下文只写 `Current workspace: <path>` |
| Goal 绑定 | 已有 `originWorkspacePath` + `targetWorkspacePath` |
| 可读 / 可写 | Goal 下 `readableRoots = origin + target`，`writableRoots = target` |
| 路径硬沙箱 | 已取消（ADR 49）；跨仓绝对路径可进执行链，审批门仍在 |

结论：跨仓读写在运行时已经可能；缺的是项目级的多文件夹入口，以及把附加源稳定露给 Agent。

## 4. 概念

| 用户看到的词 | 对内含义 |
|---|---|
| 项目 | 侧栏里的一条工作区记录。会话、记忆、Skill、默认 cwd 都挂在这条记录上。 |
| 主文件夹 | 这条记录的 `path`。它是执行世界：默认写入根、Git / AGENTS.md / 项目 Skill 的归属。 |
| 附加源 / 源文件夹 | 同一项目上额外挂的绝对路径。默认只读可见，不另开一套会话世界。 |
| 编辑项目 | 改项目名、设主要、添加或移除文件夹、移除整个项目。 |
| origin | 这次任务从哪发起。通常是当前项目的主文件夹。 |
| target | 这次任务写到哪。可以是主文件夹，也可以是某个附加源（需显式）。 |

不改的词：

- Workspace 仍是执行世界，不是「多个根的并集」。
- 一个执行型任务最多写一个 Git 仓。
- 附加源不是第二个 Workspace，不自动拥有自己的会话列表、记忆和 Skill 作用域。

## 5. 产品规则

### 5.1 一个项目必须有且只有一个主文件夹

- 新建项目：用户选的第一个文件夹就是主文件夹。
- 设主要：把某个附加源提升为主文件夹；原主文件夹降为附加源。
- 不能删除当前主文件夹，除非先指定新的主要，或移除整个项目。
- 项目显示名可改，默认仍是主文件夹 basename。

### 5.2 附加源是「这件事相关的目录」，不是第二个家

- 附加源出现在项目弹出层和编辑弹窗里。
- Agent 可以把附加源当可读上下文（读文件、搜索、引用路径）。
- 默认写操作仍落在主文件夹。
- 只有用户把某附加源设为主要，或当前 Goal 显式把 target 指到该路径时，才允许往那里写。

### 5.3 origin / target 继续分开

典型路径（本仓库日常）：

1. 用户站在 `peer-knowledge` 项目里说话。
2. 该项目主文件夹是知识库，附加源是 `peer_agent`。
3. 普通问答：origin = 知识库，写默认仍是知识库。
4. 执行型 Goal：若目标仓是 `peer_agent`，则 origin = 知识库，target = `peer_agent`。
5. Agent 两边都能读；检查、改文件、收证据默认在 target。

禁止：

- 因为项目里挂了两个文件夹，就默认两个仓都能写。
- 把两个 Workspace 的会话、运行指示、记忆合成一份。
- 一个 Task 同时提交两个 Git 仓。

### 5.4 侧栏交互

对齐 Codex 的壳，不照搬它的内部模型。

1. 侧栏仍按「项目」列出，一行一个项目（主文件夹那条记录）。
2. 点击项目名：仍打开该项目工作台 / 切到该主文件夹。
3. 右击项目：打开菜单。
   - 「查看项目文件夹」弹出文件夹列表（项目名、主文件夹路径可标「主要」、附加源路径、「编辑项目」）
   - 「在 Finder 中显示」
   - 「编辑项目」
   - 「移除」
4. 项目行不放三点按钮；文件夹总览只从右键进入。
5. 「在 Finder 中显示」打开主文件夹；弹出层里的每一行也可以各自在 Finder 中显示。

### 5.5 编辑项目弹窗

字段：

- 项目名
- 源文件夹列表
  - 每一行：文件夹名、路径、是否主要
  - 非主要行可「设为主要」或移除
  - 主要行只显示「主要」，不可直接叉掉
- 「添加文件夹」：系统选目录；已是本项目主根或附加源则忽略；若该路径已是另一个项目的主根，应提示用户，本阶段不自动合并两个项目
- 「移除项目」：只从侧栏列表拿掉，不删磁盘
- 取消 / 保存

## 6. 数据模型

向后兼容：旧记录没有 `linkedFolders` 时视为 `[]`。

```ts
type WorkspaceFolder = {
  path: string;       // 绝对路径
  name: string;       // 默认 basename，可随后改项目名但不改文件夹名
};

type WorkspaceRecord = {
  path: string;                 // 主文件夹，也是这条记录的稳定身份
  name: string;                 // 项目显示名
  addedAt: string;
  linkedFolders?: WorkspaceFolder[];
};
```

约束：

- `path` 仍是主键。会话、`activeWorkspace`、Skill 作用域继续按主路径索引。
- `linkedFolders` 去重，且不得等于主路径。
- 同一绝对路径不要同时作为两个项目的主文件夹。
- 同一绝对路径允许作为 A 的主文件夹、B 的附加源；本阶段不做反向同步。
- 设主要时：新 `path` = 原附加源路径；旧 `path` 进入 `linkedFolders`；调用方必须同时把 `activeWorkspace`、会话索引策略讲清楚（见 6.1）。

### 6.1 设主要时的身份迁移

这是唯一高风险写操作。

- 项目身份跟着主路径走：设主要后，这条记录的 `path` 变成新主文件夹。
- 旧主路径上的会话仍按旧 `workspacePath` 存在。本阶段**不批量改写历史会话的 workspacePath**。
- 切换后，侧栏「当前项目」的会话列表跟新主路径走；旧主路径若不再是任何项目的主根，其会话只在搜索 / 原会话里可回访。
- 因此：日常「知识库为主、代码仓为附加」不要轻易对调；对调是显式的「把家搬到代码仓」。

第一期若实现成本过高，编辑弹窗可以先支持：改名、添加附加源、移除附加源；「设主要」放到第二期，并在弹窗里禁用或提示。

**本期取舍：第一期先做改名 + 增删附加源；「设主要」可以先做出 UI，但服务端必须有明确迁移语义后再打开。** 为避免半成品，第一期服务端实现「设主要」时采用最小语义：改 `path` / `linkedFolders` / `activeWorkspace`，不迁移历史会话。产品文案需写明「会话仍留在原主文件夹」。

## 7. 服务与 IPC

在现有 `workspace-application-service` 上扩展，不另开一条项目系统。

新增 / 扩展：

| 能力 | 行为 |
|---|---|
| `updateWorkspace({ path, name?, linkedFolders? })` | 改显示名；整表替换附加源（调用方提交完整列表） |
| `addLinkedFolder({ path, folderPath })` | 把目录挂到该项目 |
| `removeLinkedFolder({ path, folderPath })` | 从该项目拿掉附加源，不删磁盘 |
| `setPrimaryFolder({ path, folderPath })` | 把附加源提升为主文件夹 |
| `list` 投影 | 每条记录带上 `linkedFolders`（缺省 `[]`） |

IPC 建议：

- `workspace:update`
- `workspace:add-linked-folder`
- `workspace:remove-linked-folder`
- `workspace:set-primary`

选目录继续复用现有 `chooseDirectory`。Renderer 不直接碰 `fs`。

`removeWorkspace` 语义不变：移除整个项目记录，不删磁盘，也不自动删除附加源目录。

## 8. Agent 可见性

### 8.1 系统上下文

当项目有附加源时，在 runtime 上下文里补一段事实，而不是把多个根写成「当前 Workspace = 它们的并集」。

建议文案：

```text
Current workspace: <primary>
Project additional source folders (readable):
- <linked-1>
- <linked-2>
Write, edit, and default command cwd stay in the current workspace unless a Goal target or an explicit path says otherwise.
```

附加源是 factual / runtime 上下文，不是新的系统指令源。不要把附加源里的 `AGENTS.md` 自动提升为当前项目指令。

### 8.2 读 / 写根

普通会话（无 Goal target）：

- `readableRoots` = 主文件夹 + 附加源
- `writableRoots` = 主文件夹
- 工具仍可走绝对路径（ADR 49）；写附加源应被视为跨默认写根，需 Goal target 或用户在参数里显式指向，并继续走既有权限链

有 Goal 且 origin ≠ target：

- 维持现有绑定：读 origin + target，写 target
- 若 origin 项目还挂了其他附加源，只把它们加进 `readableRoots`，不加进 `writableRoots`

### 8.3 不在本期做

- 附加源自己的 Workspace Memory / 项目 Skill 自动合并
- 多根硬沙箱
- 跨仓单一 Worktree / 单一提交
- 把两个并列项目自动折叠成一个多文件夹项目

## 9. 分期

### P0（本文实施范围）

1. 写出本方案（本文）。
2. 工作区记录增加 `linkedFolders`，服务可更新。
3. 侧栏项目可看到多个文件夹，并有「编辑项目」。
4. 编辑弹窗：改名、添加 / 移除附加源；设主要按 6.1 的最小语义实现。
5. Agent 能读到附加源路径；默认写仍在主根。

### P1

- 设主要时的会话归属策略说清楚并做迁移或「保留旧世界」开关
- 弹出层展示任务数（若产品需要）
- 从附加源一行直接「在 Finder 中显示」

### P2

- 与 Task Worktree / 跨仓交付方案对齐：附加源若被选为 target，仍一仓一个执行环境
- 项目模板：打开知识库时询问是否挂关联代码仓

## 10. 验收

1. 旧设置里没有 `linkedFolders` 的项目仍能列出，行为与现在一致。
2. 给 `peer-knowledge` 挂上 `peer_agent` 后，侧栏弹出层能看到两个路径，且只有知识库带「主要」。
3. 编辑弹窗能改名、添加、移除附加源；移除项目仍不删磁盘。
4. Agent 上下文能看到附加源；未设 Goal target 时，写文件默认仍落在主文件夹。
5. 不出现「两个主文件夹」或「无主文件夹」的持久化状态。

## 11. 非目标

- 不要把 Desktop 做成 VS Code multi-root：那是把多个执行世界合成一个编辑器根。
- 不要用 prompt 代替写路由。附加源可见 ≠ 默认可写。
- 不要在 renderer 里存一份项目文件夹真相。
- 不要为此在 `peer_agent` 的 `docs/architecture/*` 再写一套知识树；架构说明以本文和后续 ADR 为准。
