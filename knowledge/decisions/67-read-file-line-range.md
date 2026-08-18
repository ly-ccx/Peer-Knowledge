# 67. `read_file` 行范围

创建时间：2026-08-18
最后更新：2026-08-18

状态：Accepted

级别：A 级（能力输入 schema、模型可见契约、读快照语义）

关联：

- `knowledge/decisions/51-unified-desktop-cli-file-tools.md` — 文件五件套基线；本文只扩展 `read_file`
- `knowledge/decisions/66-persistent-shell-session.md` — 切片 2；本文是同程序的切片 3
- `knowledge/architecture/20-architecture-governance.md` — 主链不可旁路
- `knowledge/architecture/desktop-cli-local-capability-parity.md` — 两端同一公开名

---

## 背景

ADR 51 的 `read_file` 只有 `path`。读大文件时模型只能退回 `bash` + `sed -n`，把文件能力又绕回 Shell。DeepSeek official harness 的 editor `view` 带行号和行范围；Peer 要对齐的是这个工作面，不是再做一个超级工具。

切片 2 的持久 Shell 解决 cwd / env，不解决「按行读源码」。两件事必须分开：文件仍走 `local.file.read`。

---

## 决策

### 1. 只扩展 `read_file`，不新增 capability

公开名仍是 `read_file` / `local.file.read`。新增可选参数：

| 参数 | 语义 |
|---|---|
| `start_line` | 1-based，含 |
| `end_line` | 1-based，含 |

规则：

- 都不传：行为与 ADR 51 相同，返回全文，**不**加行号（兼容已有测试与编码器）
- 只传 `start_line`：从该行到文件末尾
- 只传 `end_line`：从第 1 行到该行
- `start_line < 1`、`end_line < 1`、`start_line > end_line`、非整数：失败，`invalid_line_range`
- `start_line > total_lines`（文件非空）：失败，`start_line_out_of_range`
- 空文件且请求从第 1 行起：成功，空 content，`total_lines = 0`

行计数：按 `\n` 拆；末尾单独的空段不另算一行。`a\nb\n` 与 `a\nb` 都是 2 行。

### 2. 有范围时 content 带行号

范围读取的 `content` 使用 `cat -n` 风格：右对齐行号、制表符、该行正文。方便模型写 `edit_file` 的 `old_string` 时对得上。

输出额外字段（两端都要有，形状可以按宿主包装，语义相同）：

```text
start_line
end_line
total_lines
```

`bytes` / `contentHash` 仍描述 **整文件**，不是切片。编码器继续按 `path + content` 做 working-set inline。

### 3. 读快照仍是整文件

实现必须读完整文件再切片。`contentHash` 是全文哈希。Desktop 的 `fullRead` / runtime-node 的 read snapshot **仍视为已完整读取**： ranged read 之后允许 `edit_file` / `write_file`，不要求再读一次全文。

理由：磁盘上已经读过全文；范围只限制模型看见的窗口，不降低冲突检测。

### 4. 两端同一 schema

Desktop 与 CLI/TUI 的 `inputSchema` 必须带上这两个可选字段。禁止只给 `peer exec` 开行范围。

不把行范围并进 `bash`，不新增 `view` / `str_replace_editor` capability。

---

## 非目标

- 不按字节 offset 读（二进制另议）
- 不改 `list_files` / `search_files` / `edit_file` schema
- 不把行号写进无范围的全文读取

---

## 验证

- 无范围：现有 read / edit / hash 测试不变
- `start_line=2, end_line=3`：content 含行号 2、3，hash 仍是全文
- 非法范围失败
- 范围读取后可以直接 `edit_file`
- Desktop 与 runtime-node schema 字段名一致

---

## 实现锚点

| 组件 | 职责 |
|---|---|
| `runtime-node` `file-read-range` | 解析范围、切片、行号格式（两端共用） |
| `runtime-node` `file-provider` | manifest + 执行 |
| Desktop `local-file-provider` | 同一参数，preview 用切片 |

代码已合入 `runtime-node` `file-read-range` / `file-provider` 与 Desktop `local-file-provider`，两端 schema 字段名一致。本文改为 Accepted。
