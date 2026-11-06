# ADR 123：超限工具结果先落本地文件，再进入模型请求

创建时间：2026-11-06
最后更新：2026-11-06

状态：Accepted（2026-11-06 用户要求按此实现。本文写在代码之后，用来补上当时缺的决策记录。实现未做发布验收，也不表示已安装的 CLI 已经带上这个行为。）

级别：A（进入模型请求的工具结果，以及本地事实文件）

关联：

- `knowledge/decisions/17-local-context-compaction.md` — 大文本留在本地，模型上下文只留索引和检索命令。本文收紧其中「最近若干条可以保留较完整正文」。
- `knowledge/architecture/23-compaction-path-root-governance.md` — 发送前的压缩管线
- `knowledge/architecture/20-architecture-governance.md` — 工具结果不是系统指令，也不能靠截断冒充 Evidence

代码事实（起草时）：单条工具结果进入下一次 provider 请求的上限是 32,000 字符（`MICROCOMPACTION_CONFIG.recentToolResultChars`）。超过上限时，`spillProviderToolResultContent` 把全文写入本地 artifact，请求里换成 `local_tool_result_ref`。Desktop 发送、压缩和流式落盘，以及 CLI 的 `buildRequest`，都走这一步。历史投影本身不丢正文，这样宿主还能在发送前落盘。

---

## 背景

CLI 一次失败请求里有 61 条工具结果，其中一条约 219 万字符。回放后的请求体约 3.1MB。原因是工具结果被原样放进历史，最近几条又不会被压缩，于是整段被反复发给模型。

只切掉中间正文能让请求变小，但模型随后无法读回被省略的部分。Grok CLI 对超限命令输出的做法是：全文留在 `output_file`，模型只看到已展示的大小、总大小和路径，再用终端工具自己取需要的片段。

---

## 决策

1. 不超过 32,000 字符的工具结果可以原样进入请求。文件读取等仍在这个上限内的工作集内容保持 inline。
2. 超过上限的工具结果，宿主先把全文写入本地 artifact。模型看到的是 `local_tool_result_ref`：`originalChars`、`artifactRef`、短预览，以及 `suggestedRetrieval` 里的 `rg`、`sed`、`tail`。
3. 新产生的大结果在进入 provider 历史时落盘。已经写在会话里的大正文不改写、不删除；下一次发送前再落盘。同一 `toolCallId` 和同一正文再次发送时写回同一个文件。
4. 写盘失败时，请求里只留带原始长度的预览，并标明没有可回读路径。失败不能把全文放回请求。
5. 预览、摘要和检索命令是导航。全文在本地文件里。模型用已有 shell 或读文件能力按路径读取，不为此新开执行旁路，也不把落盘路径当成 PermissionGrant 或 Evidence。
6. 不要求模型重跑原命令来恢复这次输出。
7. assistant tool call 与 tool result 仍然成对。投影可以保留已保存的全文，发送前再换成文件引用。

---

## 不在本次

- 不改变 shell 的工作区或权限边界。路径在 shell 当前策略下不可读时，检索命令会失败，那是权限事实，不是本文再授权。
- 不把 32,000 字符以下的结果改成文件。
- 不声明已安装 CLI 或某个历史会话已经被迁移。

---

## 验收

- 超过上限的工具结果，序列化后的请求不含全文，但含字符数、本地路径和 shell 检索命令。
- 该路径上的文件含有请求里看不到的中间内容。
- 上限以内的工具结果与原来相同。
- 同一正文再次发送不另建第二份文件。
