# Unified Desktop and CLI File Tools（桌面端与 CLI 文件工具统一）

创建时间: 2026-07-22
最后更新: 2026-07-23
状态: Accepted

## Context

Desktop 与 CLI/TUI 都通过受治理的本地 Capability Provider 暴露文件能力，但此前基线分裂：

- Desktop 有 `read_file`、`write_file`、`edit_file`、`search_files`，并维护读快照与内容哈希，避免在文件被外部修改后静默覆盖。
- CLI 的 `runtime-node` 有读取、目录列举和整文件写入，但缺少安全增量编辑与内容搜索。
- 两端相同意图使用了不同或不完整的工具名、参数说明和副作用分类，导致模型在 CLI 中退回 Bash 完成文件编辑与搜索。

文件工具仍必须遵循统一运行链：

```text
Capability Provider
  -> Manifest
    -> Runtime Projection
      -> Tool Call
        -> PermissionGrant
          -> Evidence
```

## Decision

1. Desktop 与 CLI/TUI 的共同文件能力基线统一为：
   - `local.file.read` → `read_file`
   - `local.file.list` → `list_files`
   - `local.file.write` → `write_file`
   - `local.file.edit` → `edit_file`
   - `local.file.search` → `search_files`
2. 参数语义统一：
   - 所有路径参数接受绝对路径或相对 workspace 的路径。
   - `read_file`、`list_files`、`write_file` 使用 `path`；`write_file` 另有 `content`。
   - `edit_file` 使用 `path`、`old_string`、`new_string`、可选 `replace_all`；空 `old_string` 无效；默认要求唯一匹配。
   - `search_files` 使用 `query`、可选 `path`、`case_sensitive`、`max_results`。
3. 副作用等级统一：读取、列举、搜索为 L1；写入、增量编辑为 L2。宿主仍负责其本地授权 UX 与策略。
4. 已存在文件在覆盖或编辑前必须由同一工具上下文完整读取；执行写入前比较内容哈希。文件发生变化时拒绝操作并要求重新读取。
5. CLI 补齐安全增量编辑和内容搜索；Desktop 补齐目录列举。两端对同一能力使用相同公开工具名和输入 schema。
6. 共享的是文件操作、安全和 manifest 语义，不强制共享宿主输出形状。Desktop 可保留卡片预览与 diff 输出适配，runtime-node 可保留结构化 `RuntimeToolResult.output`，但都必须返回 PermissionGrant 与 Evidence。
7. 不新增 Bash、renderer `fs` 或绕过 Runtime Projection 的文件执行路径。Bash 仍是独立通用能力，不再作为缺失文件能力的默认替代。

## Consequences

### 正向

- 模型在 Desktop 和 CLI/TUI 可依赖相同的文件工具集合和参数。
- CLI 编辑获得读取前置与冲突保护，减少 `sed` 或整文件覆盖导致的误改。
- Desktop 获得明确目录列举能力，不必借搜索或 Shell 模拟。
- 权限与 Evidence 继续由既有 Capability Provider 链路治理。

### 代价

- 在两种宿主实现并存期间，需要一致性测试防止 manifest 与行为再次漂移。
- 读快照是宿主会话上下文状态；不同进程或不同工具上下文之间不共享该状态。
- 内容搜索采用受控文本遍历，需要限制结果数并跳过不可读或非普通文件；它不替代专业索引服务。

## Migration boundary

本次只统一本地文件能力、schema、安全语义、投影和测试。不迁移 Desktop 整个 runtime gateway，不改变 renderer 边界，不改变 Shell 权限模型，也不引入新的跨进程协议负载。后续若需要消除两份 Provider 实现，应以共享深层文件语义 Module 为 seam，而不是让 Desktop 直接依赖 CLI/TUI 宿主。

## Verification

- `@peer-agent/runtime-node` 文件 provider 测试覆盖五项能力、读取前置、冲突拒绝、唯一匹配与搜索上限。
- Desktop 本地文件 provider 测试覆盖新增列目录及现有读写编辑搜索回归。
- runtime-node、TUI、Desktop 类型检查通过。
- 架构治理检查通过。
