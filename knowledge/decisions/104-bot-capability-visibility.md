# ADR 104：机器人设置里的已安装 MCP 与 Skill 开关：默认全开、按机器人记关掉名单

创建时间：2026-10-22
最后更新：2026-10-24
状态：Proposed（「本机目录 + 按机器人关掉名单」方向已确认，实现与验收事实另记，不以本文代替验收）
级别：A（能力投影边界与设备本地存储）
依赖：ADR 101（主 Bot 授权主体与子 Agent 动态继承）；ADR 15（Plugin / Skill / MCP 系统）；统一能力链 Provider → Manifest → Runtime Projection → Tool Call → PermissionGrant → Evidence

## 1. 用户问题与目标

今天「这台电脑装了什么」和「这个机器人能不能用」是同一个答案：装上的 MCP 服务器和 Skill，对所有机器人一样可见，没有按机器人收窄的位置。

用户要的是：在机器人设置里给某个机器人收窄已安装的扩展——这个机器人不要挂那个 MCP，那个机器人不要带这个 Skill。收窄应当表现为「看不见」（投影里没有这个工具、没有这段提示），而不是「看得见但每次都要问你」。

本文只解决一件事：**某个机器人能不能看见这台电脑上已经装好的某个 MCP 服务器或某个 Skill**。

明确不在本文范围：装什么、装在哪（外部 MCP / Skill 页）、本机注册表内容、安装/卸载/凭据、工作区级 Skill 总开关、ADR 101 的访问档位、内置能力清单。

关键区分：

- 外面的 MCP 页与 Skill 页是**本机目录**，回答「这台电脑装了什么」。
- 机器人设置里新增的一页回答「这个机器人看得见哪些已装项」。
- 两者是不同问题，不能合成一个开关。

### 1.1 已核对代码事实（基线 4da96f69）

- 内置能力来自根目录 `capabilities/*.json`（`local.shell.*`、`local.web.*`、读写文件等），由 `capabilities:list` 暴露。它们是设备内置能力，不是「装上的东西」。
- MCP：本机注册表由 runtime-node 的 `createMcpRegistry` 持有，`apps/desktop/electron/main/mcp-registry.mjs` 只是兼容 seam。安装/卸载/列已装走 `mcp:install` / `mcp:uninstall` / `mcp:list-installed`；设备级开关已有 `mcp:set-enabled` 与 `mcp:set-tool-visibility`。工具 capabilityId 形如 `local.mcp.<serverId>.<toolName>`（`packages/runtime-node/src/mcp-registry.mjs:353`），模型可见名为 `mcp__<server>__<tool>`。
- Skill：已装目录走 `skills:list-available` / `skills:link`；`skills:list({ workspacePaths })` 与 `skills:enable({ skillId, workspacePath })` 的入参里**只有 skillId 和 workspacePath，没有 bot**（`apps/desktop/electron/main/ipc/register-skills-ipc.mjs:43`），即 Skill 开关目前按工作区记。已启用的 Skill 被投影成 `skill__<id>` 工具（`packages/runtime-node/src/skill-tool-definitions.mjs`）。
- `BotProfile`（`packages/protocol/src/project.ts:64`）没有任何 MCP / Skill / 能力字段；它是可导出、可分享的机器人档案。
- 投影入口 `createRuntimeProjection`（`packages/runtime-core/src/projection.ts`）按工具定义列表生成；Desktop 侧经 `apps/desktop/electron/main/tools/runtime-projection-tool-materializer.mjs` 把 `local.mcp.*` 归为 mcp 类工具。

这些事实给出两个结论：现有开关全是「设备级」或「工作区级」，缺的是「机器人级」的位置；而机器人档案不是这类事实的正确落点。

## 2. 决策与不变量

1. **对象是「已安装的东西」**：这一页列出这台电脑上已安装的 MCP 服务器和 Skill。内置能力（`local.shell.*`、`local.web.*`、读写文件等 `capabilities/*.json`）不进这一页，也不被这份名单关闭。
2. **默认全开**：没有做过任何设置的机器人，已安装的 MCP 与 Skill 全部可见；用户再关掉不想给的。
3. **记关掉的名单，不记当时打开的快照**：持久化只存「用户显式关掉的那些 id」。因此以后新装一个 MCP 或 Skill，对已有机器人默认可见，不会被漏掉。
4. **关掉只是看不见**：不卸载、不改外面的 MCP / Skill 目录、不改工作区级 Skill 总开关。同一台电脑上另一个机器人不受影响。
5. **真源在设备本地**：这份记录属于这台电脑，放在 project-runtime，按机器人身份版本化；不写入可导出的 `BotProfile`。
6. **子任务动态继承，不各开一套**：只有主机器人有写入口；子任务在执行时解析最外层机器人的同一份名单，不能各自维护。
7. **先裁剪，再授权**：投影时先按名单裁掉该机器人的 MCP 工具与 Skill 工具/提示，剩下的才进入现有 PermissionGrant 与 ADR 101 档位判断。
8. **不改 ADR 101**：档位管「要不要问你」，这份开关管「这个机器人能不能看见这项已安装的 MCP 或 Skill」。两者正交。
9. **裁剪不是唯一闸门**：执行侧按同一份名单再校验一次；不可见能力的调用直接结构化拒绝，不弹审批。
10. **粒度是整项**：一个已安装的 MCP 服务器整体开/关，一个已安装的 Skill 整体开/关。这一页不拆到工具级（工具级已有设备级 `mcp:set-tool-visibility`）。

## 3. 开关语义

### 3.1 三种「不可见」要分清

| 原因 | 谁决定 | 宿主表现 | 本文是否改变 |
| --- | --- | --- | --- |
| 这台电脑没装 / 已卸载 | 外部 MCP / Skill 页 | 根本不在列表 | 否 |
| 设备级关掉（`mcp:set-enabled`、工具可见性、工作区未启用该 Skill） | 外部页或工作区设置 | 不进投影 | 否 |
| 这个机器人被关掉 | 机器人设置新页（本文） | 只在那个机器人的投影里消失 | 是 |

三层是与关系：三层都通过，工具才会出现在那个机器人的投影里。把「设备级关掉」和「机器人关掉」混成一个开关，会让用户分不清「卸载了」和「没给这个机器人」。

### 3.2 缺省与清理

- 无记录 = 全可见。不是「全关」，也不是「按当天的安装快照」。
- 名单只保留「用户显式关掉、且当前仍安装」的 id。读到已装列表时，已卸载的 id 视为过期。
- 重新安装同一个 id 时，第一版采用「卸载即清掉条目」，因此重装后默认可见，需用户重新决定。
- 改名或换 id 的服务器按新 id 处理，默认可见。
- 空记录与空名单语义等价，都表示「没有关掉任何东西」。

## 4. Module、设备本地真源与迁移

### 4.1 BotInstalledCapabilityVisibility Module

共享实现放 runtime-node，Desktop / TUI 只装配可信数据根与「已装目录」端口（与 ADR 101 的 BotAccessPolicy 同构）。Interface：

- `read({ workspaceId, agentConversationId })`：返回 `{ revision, updatedAt, denied }`；`denied` 是 `{ kind: 'mcp_server' | 'skill', id }` 的数组。只读投影，不代表审批。
- `update({ workspaceId, agentConversationId, expectedRevision, denied })`：仅本地用户入口调用。整表替换 + 乐观并发（CAS），陈旧 revision 返回冲突与当前事实；严格校验 kind 白名单、id 非空、去重、稳定排序。
- `filterInstalled({ workspaceId, agentConversationId, mcpServers, skills })`：把已装目录裁成「这个机器人可见的」，供设置页展示与投影使用。
- `resolveForExecution({ conversationId, workspaceId?, planId?, sessionId?, role? })`：按 ADR 101 的身份解析规则定位主机器人并返回其名单；普通独立会话返回「不适用」；无效委派结构化拒绝。

这个 Module 不持有「装了什么」。它只回答「关掉了哪些」；已装目录仍来自 `mcp:list-installed` 与 `skills:list-available`。它也不做执行、不授权、不发 IPC，避免第二条能力通道。

### 4.2 设备本地真源

- 位置：`project-runtime` 数据根下（与 ADR 101 的 bot-access 同族），按 `workspaceId + agentConversationId` 分区。
- 结构：每个机器人一条当前版本 + 追加式历史版本；`revision` 单调递增，用于 CAS。
- 内容：只有 `kind + installed id`，不存服务器 URL、凭据、Skill 路径。凭据仍在 MCP credential store。
- 不写入 `BotProfile`，不进导出包，不随机器人复制或分享流动。换一台电脑按缺省全开。
- 与 ADR 101 共享同一个身份键，便于 `resolveForExecution` 在同一次身份解析里同时取到档位与可见性，不引入第二套 bot 定位逻辑。

### 4.3 迁移

现有机器人没有任何记录 → 全部可见。因为缺省就是全开，不需要迁移脚本，历史机器人与新机器人行为一致。

## 5. 投影与执行链

顺序固定，不可颠倒：

```text
已装目录（mcp:list-installed / skills:list-available）
  -> 设备级开关（mcp:set-enabled / 工具可见性 / 工作区 Skill 启用）
    -> 机器人关掉名单（本文：local.mcp.* / local.skill.*）
      -> Runtime Projection（createRuntimeProjection）
        -> Tool Call
          -> PermissionGrant（ADR 101 档位）
            -> Evidence
```

- MCP：按 serverId 命中 `local.mcp.<serverId>.*` 整组裁掉。某个服务器被关掉时，它名下全部工具一起消失，不需要逐个工具判断。
- Skill：按 skillId 命中 `local.skill.<skillId>` 与对应 `skill__<id>` 工具；该 Skill 的提示也不进 System Context。工具与提示共用同一份可见性，避免「模型读到提示却调不到工具」。
- 被裁掉的能力不在投影里，模型看不到也发不出调用，因此不会产生空的审批请求或「点了同意才发现没有」的体验。
- 执行侧二次校验：`apps/desktop/electron/main/chat-runtime/projected-tool-executor.mjs` 在路由 `mcp__*` / `skill__*` 之前按同一份名单复核，不可见即结构化拒绝 `capability_not_visible`，不进入 PermissionGrant 询问。用于兜住旧 transcript 回放、回合执行中名单已变、缓存投影未刷新三种情况。
- Evidence 仍由既有链产生；本文不新增 Evidence 类型。「没被调用」本身不产生 Evidence。

## 6. 变更生效、继承与竞争

- 写入成功 = 设备本地事实已更新。下一个请求按新名单生成投影；正在跑的回合不中途重算（与 ADR 101 6.1 的生效边界一致）。
- 子任务：从主机器人解析、执行时读取，不在派发时做快照。主机器人关掉某 MCP 后，已在运行的子任务在下一次工具投影时即失去该组工具。
- 并发：两个窗口同时改，用 `expectedRevision` 做 CAS；失败方拿到当前事实与冲突提示，不静默覆盖。
- 撤销：重新打开某一项只删除对应条目，不需要「恢复默认」——缺省本来就是全开。
- 卸载竞态：用户在外面卸载时，名单里的残留条目在下一次读取已装目录时清理；清理失败不阻塞卸载本身。

## 7. 产品交互与多入口

- 机器人设置新增一页（暂定名「已安装的 MCP 与 Skill」）。列表来自本机已装目录，每项一个开关，默认全开；顶部一句话说明「关掉只是这个机器人看不见，不会卸载」。
- 空态：这台电脑还没装任何 MCP 或 Skill → 指到外面的 MCP / Skill 页，不在这里安装。
- 本页不提供安装、卸载、凭据、工具级可见性的入口；这些仍在外面的页。
- 子任务现场只读展示「继承自主机器人」，不提供写入。
- TUI / 远程：第一版只读，读到的是同一份设备本地事实；是否提供写入见 §8 的后续卡。

## 8. 实施顺序与逐文件评审

1. protocol：新增 `BotInstalledCapabilityRef` 与名单快照类型（不触碰 `BotProfile`）。
2. runtime-node：`BotInstalledCapabilityVisibility` + 存储适配 + CAS + 单测（含 §9 反例）。
3. 投影接入：在 materializer 之前按名单裁剪 `local.mcp.*` / `local.skill.*`；单测覆盖整组裁掉、不误伤内置能力。
4. 执行侧二次校验：`projected-tool-executor` 增加 `capability_not_visible` 分支 + 单测。
5. IPC / preload：`bot-capability-visibility:read` / `:update`，仅本地用户入口可写。
6. 设置页：新一页 + 空态 + 开关 + 文案。
7. 视觉与产品回归：按 `peer-knowledge/playbook/product-regression.md` 出截图包并写 `review.json`；UI 交付前不得用「测试通过」代替产品验收。

## 9. 必须验收的反例

每条都要有可复现步骤与断言：

1. 默认全开：新机器人无记录 → 已装 MCP 与 Skill 全部出现在投影，且能调用。
2. 关掉某 MCP → 该服务器的全部 `local.mcp.<serverId>.*` 从投影消失；其它 MCP 不受影响。
3. 关掉某 Skill → `skill__<id>` 与对应提示都不出现；其它 Skill 不受影响。
4. 新装默认可见：先关掉 A，再装 B，B 对同一机器人立即可见（不被旧快照漏掉）。
5. 只影响这个机器人：甲机器人关掉某 MCP，乙机器人仍可见且可调用。
6. 不卸载、不改外部目录：关掉后 `mcp:list-installed` / `skills:list-available` 与外部页状态不变；工作区级 Skill 开关不变。
7. 内置能力不被误伤：关掉任意 MCP / Skill 后，`local.shell.*` / `local.web.*` 仍在投影里。
8. 子任务继承：主机器人关掉后，子任务执行时同样看不见；子任务不产生自己的名单。
9. 执行侧兜底：旧 transcript 里残留的 `mcp__x__y` 调用，在名单已关掉时被拒 `capability_not_visible`，不弹审批、不产生 PermissionGrant。
10. 卸载清理：外部卸载后残留条目被清掉且不阻塞卸载；重新安装同一 id 不自动变成关掉。
11. 不进档案：导出的 `BotProfile` 不含这些字段；换机后全开。
12. 档位不变：关掉某 MCP 不改变 `ask_before_write` 等档位语义；反过来改档位也不改变名单。

## 10. 备选方案与代价

- **存打开快照（allow-list）**：装上新 MCP 后老机器人永远看不见，用户会以为坏了，每次都要回去改一遍。拒绝。
- **写进 `BotProfile`**：看着省事，但档案会被导出、复制到别的电脑，指向那台机器上不存在的安装项，还让「设备事实」混进「可分享身份」。拒绝。
- **子任务各存一份**：子任务生命周期短，并发与清理成本高，并且与「继承」语义冲突。拒绝。
- **用访问档位表达**（把关掉的 MCP 设成永不批准）：会把「看不见」和「要问你」混成一件事，破坏 ADR 101 的单一语义。拒绝。
- **一步做到工具级**：与设备级 `mcp:set-tool-visibility` 重叠，设置页也难以表达。第一版按整项，工具级等真实需求出现再谈。

## 11. 明确不做

- 不做机器人级 MCP 安装、卸载、凭据。
- 不做机器人级 Skill 总开关（工作区级 `skills:enable` 保持原样）。
- 不把内置能力纳入这一页或这份名单。
- 不改 ADR 101 的档位、身份解析、继承链长度与目标闸门。
- 不写入 `BotProfile`，不参与导入导出。
- 不因关掉而断开 MCP 连接或回收进程；连接仍由设备级管理。
- 不在 System Context 里新增「被关掉了哪些」的提示——关掉即不存在，不给模型一份反向暗示的可用清单。

## 12. 评审与验收状态

- 状态 Proposed：方向（本机目录 + 按机器人记关掉名单）已由用户确认并要求落成文件；实现与验收事实另记，不以本文代替验收。
- 尚未实现：`BotInstalledCapabilityVisibility` Module、存储与版本化、投影裁剪接入、执行侧二次校验、typed IPC / preload、设置页。
- 尚未验证：§9 的反例矩阵、真实已装目录与真实档位的联动、子任务继承的执行时解析、导出/导入的默认全开行为。
- 上述任一项的实际结论以对应实现卡与验收记录为准；本文不因文档存在而升级为 Accepted。
- 若实现中发现需要改变投影入口或新增协议对象，先更新本文再改代码。
