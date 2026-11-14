# 工作区沙箱演进对比：硬沙箱多根 vs full=machine

创建时间: 2026-07-21  
最后更新: 2026-11-14（仅修正架构文档引用；2026-07-21 取消硬沙箱的决策不变）

## 状态

**Accepted / 已按用户决策落地取消路径硬沙箱**（2026-07-21）。

产品决策：不要路径硬沙箱，允许跨工作区读写（接近 Claude Code）；`full` 语义覆盖本机路径访问，审批门与 Goal boundary 仍保留。

历史对比（方案 A 多根硬沙箱 vs 方案 B full=machine）保留作决策记录；**最终采纳的是「取消 path/cwd 硬拦截」**，见 `knowledge/decisions/49-cancel-path-hard-sandbox.md`。

## 1. 问题陈述

### 1.1 用户感知到的矛盾

1. Composer / 设置显示 **Full access**（`full_local`）
2. 工具调用跨到关联代码仓（如 `peer-knowledge` 会话读 `peer_agent`）仍报：
   - `path_outside_workspace`
   - `cwd_outside_workspace`

用户直觉：`full` = 本机全权限。  
当前实现：`full` = **当前工作区内** 本地能力免审批，**不等于** 放开路径边界。

### 1.2 根因：两轴被揉成一个词

| 轴 | 含义 | 当前实现 |
|---|---|---|
| **Approval（审批轴）** | 要不要弹窗 / 能否自动 grant | `ask_before_local` / `session_local` / `full_local` |
| **Filesystem scope（路径轴）** | 路径 / cwd 可以到哪 | 固定单 `workspaceRoot` 硬沙箱 |

两轴正交；`full_local` 只动审批轴。

### 1.3 触发场景（产品级）

- 知识库会话驱动代码仓改动（`peer-knowledge` → `peer_agent`）
- Goal plan 声明了 `targetWorkspacePath`，但底层 file/shell provider 仍按会话 `workspaceRoot` 硬校验
- CLI 用户从 Claude Code 迁来，期望「绝对路径就能读」
- 工具文案（如 search 类）暗示 access level 可跨仓，与 `read_file` / `bash` 硬限制不对齐

## 2. 现状实现锚点（证据）

### 2.1 路径硬沙箱（runtime-node）

| 组件 | 路径 | 行为 |
|---|---|---|
| `resolveWorkspacePath` | `packages/runtime-node/src/provider-utils.ts` | `resolve(root, candidate)` 后若 `relative` 为 `..` 或越界 → `path_outside_workspace` |
| file provider | `packages/runtime-node/src/file-provider.ts` | 读/写二次 `realpath` 校验，防 symlink 逃逸 |
| shell cwd | `packages/runtime-node/src/shell-classifier.ts` → `normalizeNodeShellCwd` | cwd 不在 root 内 → `cwd_outside_workspace` |

特点：**fail-closed**，与 access level **无关**。

### 2.2 权限门（Desktop chat-runtime）

| 组件 | 路径 | 行为 |
|---|---|---|
| permission gate | `apps/desktop/electron/main/chat-runtime/permission-gate.mjs` | `full_local` → `local_access_level_full` 自动 grant |
| 架构说明 | `knowledge/architecture/20-architecture-governance.md` | `full_local` 自动批准文件写入与低/中风险 shell；**不写「放开任意路径」** |
| 哲学 | `knowledge/architecture/20-architecture-governance.md` | 用 schema / permission / projection **执行前收敛**，而非提示词兜底 |

### 2.3 Goal 已有「多根意图」，未贯通 provider

| 组件 | 路径 | 行为 |
|---|---|---|
| tool context | `chat-runtime/tool-orchestrator.mjs` → `createToolContext` | 已有 `originWorkspacePath` / `targetWorkspacePath` / `readableRoots` / `writableRoots` |
| goal-runner | `apps/desktop/electron/main/goal-runner.mjs` | 读取 plan 的 `targetWorkspacePath` 并绑定 |
| goal-mode-gate | `chat-runtime/goal-mode-gate.mjs` | `isInsideWorkspace` + inScope/outOfScope；缺信息时不硬阻断，交 permission |
| 产品边界 | `design/product/goal-mode-codex-cc-workflow.md` | 「Goal mode cannot write outside workspace or **explicit boundaries**」 |

结论：上层已开始表达「关联工作区 / 可读写根」，**底层 runtime-node 仍单 root**。这是方案 A 的天然接缝。

### 2.4 CLI

- 会话 root：`PEER_WORKSPACE_ROOT ?? process.cwd()`
- 与 Desktop 共享 runtime-node 路径策略（ADR `48-cli-first-class-release`：同仓一等发布，运行时共享）
- CLI 没有 Desktop 那套 permission UI，但 **路径沙箱一样硬**

## 3. 方案定义

### 方案 A — 保持硬沙箱 + 多根 / 关联工作区

**一句话**：路径轴永远是显式 roots 的并集；审批轴继续独立。`full` 仍不等于整机。

#### 语义

```
Filesystem scope =
  session.workspaceRoot
  ∪ plan.targetWorkspacePath（若声明）
  ∪ linked / associated roots（AGENTS.md / plan / UI 绑定）
  ∪ 临时用户授权的 extra roots（可选）

Approval =
  ask | session | full   （只决定 grant 是否自动）
```

#### 分层模型（推荐对外文案）

| Scope 档 | 可读 | 可写 | 默认 |
|---|---|---|---|
| `workspace` | 当前 root | 当前 root | 默认 |
| `workspace+linked` | 当前 + 关联仓 | 关联仓需 plan/boundary 声明 | Goal / 知识库驱动改代码 |
| `machine` | 整机（显式高危） | 整机写仍强制审批或禁止 | 默认 **不** 因 full 开启 |

> 注：`machine` 可作为后续可选档，**不**绑定到今天的 `full_local` 标签，避免心智回潮。

#### 关键改动面（落地时）

1. **runtime-node**：`resolveWorkspacePath` / shell cwd 从单 `workspaceRoot` 升级为 `allowedRoots[]`（或 readable/writable 分列）
2. **tool context 贯通**：`readableRoots` / `writableRoots` 从 goal-runner / llm-chat-service 传到 file/shell/search provider
3. **读 vs 写不对称**：
   - 读关联仓：可在 `session_local+` 自动
   - 写关联仓：必须在 `writableRoots` 或显式 boundary 内
4. **Goal**：`targetWorkspacePath` 真正扩大 sandbox，而不只是元数据
5. **CLI**：支持 `--workspace` 多根 / `PEER_WORKSPACE_ROOTS` / 从 AGENTS.md 解析关联仓
6. **文案**：Full =「当前允许范围内免审批」；跨仓提示「添加关联工作区」而非「再开更高权限」

#### 优点

- 与现有 fail-closed 哲学一致
- Goal 自治安全：默认边界可审计
- 知识库 / 代码仓解耦模型可产品化，而不是靠「切会话」
- 不把 `full` 语义炸成「整机 agent」
- 可渐进：先贯通 `targetWorkspacePath`，再做 UI 多根

#### 缺点 / 成本

- 实现与测试面大于「一刀切放开」
- 多根 realpath / symlink / Windows 路径边界要补齐
- CLI 体验仍不如 Claude Code「随便读」，除非用户显式加根
- 需要产品入口：关联工作区管理

---

### 方案 B — `full` 真正等于 machine 级本机访问

**一句话**：当 access level = `full_local` 时，runtime 关闭（或极大放宽）路径沙箱；行为接近 Claude Code CLI。

#### 语义

```
if accessLevel == full_local:
  filesystem scope = 本机用户可见路径（或 home+ 可配置）
else:
  保持现有单 workspace 硬沙箱
```

#### 关键改动面

1. `resolveWorkspacePath` / `normalizeNodeShellCwd` 读取 access level 或 `scopeMode`
2. `full_local` 下允许绝对路径、跨盘符（平台约束内）、任意 cwd
3. permission-gate 与 provider 语义对齐（文案终于自洽）
4. Goal 边界可能被架空：plan 的 inScope/outOfScope 变成软约束，除非另加强制 gate

#### 优点

- 立刻消解「full 却 outside」的悖论感
- 跨仓 / monorepo / dotfiles 开发摩擦最低
- 对标 Claude Code 的默认生产力心智
- 实现路径短（改校验谓词 + 传 access level）

#### 缺点 / 风险

- **Goal 自治 + full = 高爆破半径**（扫家目录、误写配置、误删）
- 知识库会话默认可写代码仓，边界糊掉
- Desktop 多会话隔离被削弱
- Evidence / 审计变难：「在哪个 root 下做的」不再显然
- 与 `20-architecture-governance` 的「执行前机械化收敛」张力大
- 高风险 shell 即便仍 review，**文件读写已无路径监狱**
- 一旦上线，再收回是 breaking UX

## 4. 影响面矩阵

| 维度 | 方案 A（硬沙箱 + 多根） | 方案 B（full=machine） |
|---|---|---|
| **Chat 日常改单仓** | 无感（与现状同） | 无感或略松 |
| **知识库驱动改代码** | 一等公民：关联 root / `targetWorkspacePath` | 靠 full 硬闯，能干活但无结构 |
| **Goal 自治** | 边界可验证；DoD 与 scope 一致 | 需额外强制 scope gate，否则危险 |
| **CLI** | 需多根/关联配置；默认同现状 | full 后接近 Claude Code |
| **权限 UI 心智** | 拆成 Approval × Scope，需一次文案升级 | Full 字面自洽，但隐藏爆炸半径 |
| **安全默认** | 保持 fail-closed | 默认在 full 下 fail-open（路径维） |
| **与现有代码接缝** | toolContext 已有 roots 字段，接缝清晰 | 改 provider 谓词即可，但污染 Goal 契约 |
| **可回滚性** | 高（roots 列表可收） | 低（用户依赖整机访问后难收回） |
| **对标 Claude Code** | 不在路径上对标，在「显式项目边界」上差异化 | 路径体验对齐，产品差异化削弱 |

## 5. 推荐路径

### 5.1 最终决策：**取消路径硬沙箱**（用户拍板 2026-07-21）

用户明确选择：**不要路径硬沙箱，允许跨工作区读写（接近 Claude Code，full 才像 full）**。

因此对比结论更新为：

1. **runtime path/cwd 硬拦截删除**：不再抛 `path_outside_workspace` / `cwd_outside_workspace`。
2. **审批轴保留**：`ask` / `session` / `full` 与 PermissionReview 仍决定是否自动执行。
3. **Goal 契约边界保留**：`outOfScope`、不可逆确认、Evidence 完成门仍生效（不依赖 path 监狱）。
4. **workspaceRoot 仍作相对路径默认锚**，不是「禁止出界」的墙。
5. 方案 A（多根硬沙箱）**不再作为默认推荐**；多根/`targetWorkspacePath` 仍可用于默认 cwd / Goal 写根提示，但不是硬失败条件。

### 5.2 分阶段落地（建议）

| 阶段 | 做什么 | 成功标准 |
|---|---|---|
| **P0 语义止血** | 文案：Full = 免审批 ≠ 出工作区；错误码旁路提示「添加关联工作区 / 切换 workspace / 设置 targetWorkspacePath」 | 用户不再认为是 bug |
| **P1 Goal 贯通** | plan.`targetWorkspacePath` → toolContext.`writableRoots`/`readableRoots` → runtime-node 多 root 校验 | 知识库 Goal 可改关联代码仓且 evidence 可解释 |
| **P2 关联工作区产品化** | AGENTS.md / UI 绑定 linked roots；读默认扩、写需在 writable | 非 Goal 会话也能稳定跨仓 |
| **P3 CLI 对齐** | `PEER_WORKSPACE_ROOTS` 或重复使用关联配置 | CLI 与 Desktop 同语义 |
| **P4（可选）machine 档** | 独立 scope 档，**不**复用 full 标签；默认关；写操作仍强审批 | 少数 power user 需求，不污染默认 |

### 5.3 明确不推荐（历史保留）

- ~~不推荐直接做方案 B~~ → 用户已选择取消路径硬沙箱；落地的是「路径放开 + 审批保留」，不是无审批 machine 模式。  
- **不推荐**只改 prompt 而不改 provider。  
- **不推荐**恢复 `path_outside_workspace` / `cwd_outside_workspace` 硬失败作为默认安全策略。

### 5.4 若必须给 Claude Code 迁移用户一条「松」路径

作为 **P4 可选 machine scope**，满足：

1. 显式二次确认（不是 Full 下拉的同义词）
2. 会话级开关，默认关
3. Goal 模式默认拒绝 machine，或强制缩小到 plan roots
4. 写路径仍可要求 session 审批 / 高风险规则

这是「方案 A 的可选扩展」，不是方案 B 的默认化。

## 6. 决策问题清单（拍板用）

1. Full 的对外定义：免审批 + 本机路径可访问（路径硬沙箱已取消）。
2. 知识库驱动改代码：直接允许跨仓绝对路径；`targetWorkspacePath` 仍作默认写锚/提示，不是硬墙。
3. Goal：不再因 outside workspace 硬拒；仍强制 `outOfScope`、不可逆确认与权限门。
4. CLI：与 Desktop 同语义（无 path/cwd 硬沙箱）。
5. 读/写：路径维对称放开；写仍走 permission / Goal 边界。

## 7. 结论（一句话）

**取消 runtime 路径硬沙箱：跨工作区绝对路径与 cwd 允许进入执行链；安全靠权限审批 + Goal 边界 + 危险命令规则，而不是 path_outside 硬失败。**  
决策记录：`knowledge/decisions/49-cancel-path-hard-sandbox.md`。

## 8. 参考锚点

- `packages/runtime-node/src/provider-utils.ts` — `resolveWorkspacePath` / `path_outside_workspace`
- `packages/runtime-node/src/file-provider.ts` — realpath 二次校验
- `packages/runtime-node/src/shell-classifier.ts` — `normalizeNodeShellCwd` / `cwd_outside_workspace`
- `apps/desktop/electron/main/chat-runtime/permission-gate.mjs` — `full_local` 自动 grant
- `apps/desktop/electron/main/chat-runtime/tool-orchestrator.mjs` — `readableRoots` / `writableRoots`
- `apps/desktop/electron/main/goal-runner.mjs` — `targetWorkspacePath` 绑定
- `apps/desktop/electron/main/chat-runtime/goal-mode-gate.mjs` — workspace / scope 判定
- `knowledge/architecture/20-architecture-governance.md` — local access mode 说明
- `knowledge/architecture/20-architecture-governance.md` — 执行前机械化收敛
- `design/product/goal-mode-codex-cc-workflow.md` — Goal 不可写越界除非 explicit boundaries
- `knowledge/decisions/48-cli-first-class-release.md` — CLI 与 Desktop 同仓共享 runtime
