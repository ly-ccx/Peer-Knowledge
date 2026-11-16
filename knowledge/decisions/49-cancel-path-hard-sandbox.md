# 49. 取消路径硬沙箱（允许跨工作区读写）

创建时间: 2026-07-21
最后更新: 2026-11-15（跨 ADR 对齐：明确被 ADR 90 / 92 / 101 / 106 部分取代的范围）

## 状态

**Accepted（已被后续 [ADR 90](90-local-image-capability-and-product-review.md)、[ADR 92](92-scoped-permission-inheritance.md)、[ADR 101](101-bot-owned-access-policy.md)、[ADR 106](106-readonly-git-and-delegation-capability-admission.md) 部分取代，2026-11-15 补注）**（原用户产品决策 2026-07-21：不在普通聊天里以硬路径牢笼阻断经用户授权的跨工作区操作）。

> [!NOTE] 部分取代说明（2026-11-15）
>
> 本文保留“经典对话与常规工具不无故假设唯一工作区死牢”的初衷，但下列机制已被后续架构与安全 ADR **部分取代**：
>
> 1. **Symlink / `realpath` 校验已恢复**：原 §实现锚点 中“去掉 `file-provider.ts` `realpath` 二次 assert”的做法已被 [ADR 90](90-local-image-capability-and-product-review.md)、[ADR 92](92-scoped-permission-inheritance.md)、[ADR 101](101-bot-owned-access-policy.md) 与 [ADR 106](106-readonly-git-and-delegation-capability-admission.md) 取代——现在读/写与 Git 查询必须先 `realpath` 解析真实路径并防范 symlink 逃逸。
> 2. **工作区外访问受显式闸门约束（不再依赖 `full_local` 无条件免审）**：工作区外读取/写入需经宿主 `PermissionGate` / 范围授权（如会话外图片须先过 [ADR 90](90-local-image-capability-and-product-review.md) / [ADR 92](92-scoped-permission-inheritance.md) 的 `imageReadGrant`），且 Project Bot 下“工作区外访问与子任务继承”改由 `bot-access.sqlite`（[ADR 101](101-bot-owned-access-policy.md)）与委派作用域继承（[ADR 92](92-scoped-permission-inheritance.md)）控制，`Full` 不覆盖角色边界与作用域保护。

## 背景

历史上 runtime-node / Desktop shell classifier 在 file path 与 shell cwd 上做了硬沙箱：

- `path_outside_workspace`
- `cwd_outside_workspace`

即使用户把 Local access 设为 `full_local`，跨工作区绝对路径仍会在 provider 入口硬失败。  
这与「Full = 本机可干活」的直觉冲突，也阻碍知识库会话驱动关联代码仓、CLI 跨目录工作流。

## 决策

**取消 runtime 路径硬沙箱。**

| 层 | 新语义 |
|---|---|
| **路径解析** | 相对路径仍相对会话 `workspaceRoot`；**绝对路径可落在本机任意位置** |
| **Shell cwd** | 默认仍为会话 workspace；**允许 cwd 在工作区外** |
| **权限门** | 仍走 `ask_before_local` / `session_local` / `full_local` 与 PermissionReview |
| **Goal** | 仍尊重 plan `writableRoots` / `outOfScope` / 不可逆确认；**不再依赖 path_outside 硬错误码** |
| **Full 语义** | Full = 本地能力免审批（在权限模型内），路径维不再额外 fail-closed |

明确 **不** 做：

- 不引入 OS 级 container / seatbelt 作为本决策的替代
- 不把「取消路径沙箱」写成「取消一切权限审批」
- 不删除会话 `workspaceRoot` 作为默认相对路径锚点

## 实现锚点（peer_agent）

| 组件 | 变更 |
|---|---|
| `packages/runtime-node/src/provider-utils.ts` | `resolveWorkspacePath` 不再抛 `path_outside_workspace` |
| `packages/runtime-node/src/file-provider.ts` | 去掉 realpath 二次 workspace assert |
| `packages/runtime-node/src/shell-classifier.ts` | `normalizeNodeShellCwd` 不再抛 `cwd_outside_workspace` |
| `apps/desktop/.../runtime-gateway/shell-classifier.mjs` | `normalizeShellCwd` 对齐 |
| 工具 prompt / schema 文案 | 声明绝对路径可出会话工作区 |
| 测试 | 跨工作区读/写/cwd 由拒绝改为允许（仍可走审批） |

## 边界（仍在）

1. **审批轴不变**：写文件 / 中高风险 shell 仍按 access level 与规则审批。  
2. **Goal 契约边界**：`outOfScope`、不可逆动作确认、Evidence 完成门仍生效。  
3. **高风险 shell deny 规则**仍生效（如 `rm -rf` 类 L5）。  
4. **相对路径默认锚**仍是会话 workspace，避免无锚点的相对路径漂移。

## 后果

- 正面：跨仓读写、知识库驱动代码仓、CLI 体验对齐 Claude Code；Full 不再被路径硬错误打脸。  
- 风险：误写工作区外文件的半径变大；依赖审批与 Goal boundary，而非 path 监狱。  
- 文档：`design/product/workspace-sandbox-evolution-comparison.md` 结论改为采纳「取消硬沙箱」。

## 验证

- runtime-node file/shell 测试：工作区外绝对路径不再 `path_outside` / `cwd_outside`  
- Desktop shell-system：outside cwd 的 allow rule 可添加  
- 手动/集成：`full_local` 下跨仓 read/write/bash 可进入权限/执行链
