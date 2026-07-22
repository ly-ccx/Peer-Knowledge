# 49. 取消路径硬沙箱（允许跨工作区读写）

创建时间: 2026-07-21  
最后更新: 2026-07-21

## 状态

**Accepted**（用户产品决策 2026-07-21：不要路径硬沙箱，接近 Claude Code）。

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
