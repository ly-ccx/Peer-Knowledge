# ADR 55：Desktop 与 TUI 统一 System Context Assembler

创建时间：2026-07-25
最后更新：2026-08-18
状态：Accepted / Implemented
关联代码仓：`/Users/liangyin/Documents/DEV/github/peer_agent`

> 2026-07-25 补充：本 ADR 只统一 System Context。持久化历史到 active provider
> history 的唯一解释由 ADR 57 `57-canonical-conversation-history-projector.md`
> 继续治理；两者共同构成完整 Request Projection，不能以共享 System Context
> 代替共享 History Projector。

## 关联文档

- `knowledge/architecture/19-system-prompt-context-architecture.md`
- `knowledge/architecture/21-auto-context-compaction-run-resume.md`
- `knowledge/architecture/22-tui-desktop-shared-runtime-and-host-governance.md`

---

## 1. 背景

Desktop 当前通过完整 `PromptAssembler + PromptSourceRegistry` 构造 System Context；TUI 则使用一段轻量 `BASE_SYSTEM_PROMPT`，并在 provider adapter 内追加 mode 与 continuity 文本。

同一会话在两个宿主恢复时，即使消息历史、工具投影和模型上下文窗一致，下一请求的真实输入仍不一致，进而造成：

- 上下文占用率明显不同；
- project instructions、Goal、MCP、provider、continuity 等认知规则跨端漂移；
- compaction / restore 只能修正消息历史，不能修正 System Context；
- 新 Source 默认只在 Desktop 生效，TUI 长期滞后。

这不是显示层误差，而是 System Context 存在两套 Implementation。

---

## 2. 决策

### 2.1 唯一 Interface

新增共享 `@peer-agent/system-context` Module，唯一公开 Interface 为：

- `PromptSource`
- `PromptSourceRegistry`
- `assembleSystemContext(input, { registry })`
- `renderSystemContext(context)`
- `createDefaultPromptSourceRegistry()`

Module 统一负责 L0-L7 分层、Source observe/render 生命周期、稳定排序、section checksum、rendered hash 和 snapshot。

Desktop 与 TUI 不再拥有各自的 assembler 或基础 system prompt。

### 2.2 默认 Source 统一

共享默认 registry 包含 core、brainstorming、adaptive planning、construction falsification、diagnosis gate、workspace、provider/model、attachments、project instructions、controlled extensions、runtime/mode reminders、Goal plan/runner/checkpoint、task acceptance、MCP host、Explorer、Verifier 和 continuity Source。

Source 根据输入事实自行决定是否产生 section；宿主不通过删减 Source 来维护另一套认知策略。

### 2.3 Host Adapter 边界

Desktop 与 TUI Adapter 只负责把宿主事实投影为 assembler input：

| 事实 | Desktop Adapter | TUI Adapter |
|------|-----------------|-------------|
| workspace | conversation workspace | `PEER_WORKSPACE_ROOT` / cwd |
| provider/model/effort | Desktop selection | TUI selection |
| reply language | configured instruction | configured instruction |
| Goal | Desktop `goalPlanStore` | TUI `goalBridge.store` |
| MCP | Desktop `mcpRegistry` | TUI `skillMcpBridge.mcpRegistry` |
| continuity | Desktop compaction context | TUI controller turn context |
| task acceptance | 首条 user 消息（压缩后回退会话正文） | `send()` 钉住的首条 user 正文 |

Adapter 不改变 layer、priority、section id、render 或 hash 规则。

### 2.4 Provider 发送与占用率

Provider adapter 接收已经装配完成的单一 system prompt，不再自行拼接 Plan/Goal prompt 或 turn system blocks。

上下文占用率必须投影真实的下一次请求：

```text
assembled System Context
+ active provider history
+ projected tool schemas
```

恢复会话时必须重新装配当前宿主事实；不得信任另一个宿主保存的旧 numerator，也不得忽略本宿主即将发送的 System Context。

---

## 3. 模块深度

该改造形成一个 deep Module：

- Interface 小：registry、assemble、render；
- Implementation 深：Source 发现、分层、排序、净化、指纹、快照；
- Seam 清晰：宿主只注入事实句柄与 Context Items；
- Locality 提升：新增认知规则只修改一个 Source；
- Leverage 提升：Desktop、TUI、restore projection 和测试复用同一实现。

禁止：

- TUI import Desktop Main 的 prompt assembler；
- Desktop/TUI 再引入独立 `BASE_SYSTEM_PROMPT`；
- provider adapter 隐式追加 mode system prompt；
- 为追求字节一致而伪造不存在的宿主事实。

---

## 4. 迁移与兼容

- Desktop 原 prompt 路径保留薄 re-export Adapter，降低一次性调用面迁移风险；
- canonical Implementation 位于共享 package；
- TUI 直接消费共享 package，不依赖 Electron；
- 旧 `buildTuiSystemPrompt` 降级为兼容 helper，内部必须调用共享 assembler，后续可删除。

---

## 5. 验收

1. Desktop 与 TUI 的默认 registry source ids 完全一致；
2. 相同 assembler input 产生相同 section 顺序、checksum 与 rendered hash；
3. TUI provider 请求只有一个由 assembler 产生的 system message；
4. Plan/Goal/continuity 不再由 provider adapter 旁路拼接；
5. 两端 context pressure 都包含同一 assembled System Context 与实际工具 schema；
6. Desktop prompt tests、TUI controller/provider tests、typecheck、build、architecture gate 全部通过；
7. 同一会话、同一模型、同一宿主事实下，占用率只允许存在 tokenizer 舍入误差。

---

## 6. 后果

### 正向

- System Context 成为真正的跨宿主 Runtime 能力；
- 新 Source 默认同时覆盖 Desktop/TUI；
- restore、compaction 与占用率基于同一请求事实；
- CLI 仍可独立安装运行，不依赖 Electron。

### 成本

- 共享 package 暂时是 Node runtime Module，因为 project instruction Source 需要文件系统；
- Goal/MCP Source 通过只读句柄观察宿主事实，Interface 必须保持最小；
- 旧路径兼容层需要在后续版本清理。
