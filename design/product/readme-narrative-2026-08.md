# README 产品叙事主线（2026-08 重写）

> 目的：沉淀 peer_agent 双语 README 重写（2026-08-14）采用的叙事结构与事实依据，供后续文档（docs 站点、changelog 文案、功能页）沿用同一主线，避免产品口径漂移。  
> **产品理念以 `design/product/peer-product-alignment.md` 为准。** 本文只锁 README 章节结构；与对齐文档冲突的旧口径（云端派发、圆桌当品类）不要再写进对外叙事。

## 叙事主线

用户看不到「能干嘛」的根因不是功能缺失，而是旧 README 以工程视角罗列特性。新版叙事按「定位 → 理念 → 能力」三层递进：

1. **完全开源（MIT）定位先行** —— 差异化不是「本地执行」（多数 coding agent 已做到），而是整条链路（Desktop/TUI/CLI/运行时/协议/能力清单）同一 MIT 许可：可审计、可 fork、可嵌入，无「开源壳 + 闭源核」。
2. **理念主线：任务流 = 流转 · 继承 · 追问** —— 任务是一等公民，有自己的目标、边界、成功标准与生命周期。
   - **流转**：签收（目标+边界+成功标准）→ 澄清 → 规划（L0–L3 深度缩放）→ 执行 → 验证 → 验收关闭。
   - **继承**：Goal 状态持久化、暂停/恢复/`waiting_user`、压缩摘要 + 上下文 checksum；摘要是连续性上下文而非证据。
   - **追问**：`request_user_input` 结构化选项提问，回复为持久化状态转移；只问关键歧义/高风险/缺权限。
3. **能力三板块**（回答「能干嘛」）：
   - **多渠道接入**：界面渠道（Desktop/TUI/CLI/Quick Chat）× 模型渠道（官方 API/OAuth/Coding Plan/自定义端点）× 集成渠道（Automation/MCP/浏览器）。
   - **丰富的插件化**：MCP 一等公民、插件与技能 marketplace、声明式能力清单（manifest）、Open Runtime SDK、受治理上下文准入。
   - **任务派发与验收**：派发需确认（同意/拒绝）→ `dispatching → acked → running → result_received` 显式状态链 → 质量自检 → 待用户验收 → 交付；隔离 worktree 运行；圆桌协同。

## 版本口径

- npm dist-tags 为版本唯一事实源：`latest=0.0.3`、`beta=0.0.4-beta.3`（2026-08-14 查证）。
- README 版本表述模板：`当前正式版：0.0.3（npm latest），beta 通道 0.0.4-beta.3`；仓内 VERSION 文件（0.0.4-beta.2）是工作区开发版本，不代表发布事实，文档引用以 npm/changelog 为准。
- changelog 数据：`docs/changelog-data/v0.0.3.json`（官方叙事含「签收、追问、执行、验收和恢复主链路」）。

## 主张-实现对照（写文档前必查）

| 产品主张 | 代码证据（peer_agent 仓内） |
| --- | --- |
| 派发确认（同意/拒绝） | `packages/i18n/src/index.ts` `chat.dispatch.*`（同意派发/拒绝派发/给云端调度的确认反馈） |
| 派发状态链 | `packages/protocol/src/execution.ts` `dispatching → acked → running → result_received` |
| 验收闭环 | `packages/i18n/src/index.ts` 质量自检过线 → 待用户验收 → 已验收交回 |
| 结构化追问 | `request_user_input` 工具 + `packages/runtime-node/src/intake.ts`（选项、契约保留、持久化状态转移） |
| 任务继承 | `packages/runtime-node/src/goal-plan-store.mjs`（计划图持久化）、压缩摘要 + 上下文 checksum、continuity source |
| 圆桌 | `chat.channel.roundtable` / `chat.governance.roundtable`（聊天渠道 + 治理模式） |
| 多渠道 | `packages/protocol/src/index.ts` LlmChannelId / ChatChannelId / 更新通道三层 |
| 插件化 | `capabilities/*.json` 声明式清单 + `marketplace/`（reviews/sources 治理）+ `skills/` + Open Runtime SDK 包 |

## 双语 README 结构契约

- H2 章节（10 个）中英一一对应：Why / Philosophy / Task Flow / What You Can Do / Quick Start / Architecture / Vision / Roadmap / Contributing / License。
- Task Flow 章节标题双语锚点：中文 `#-任务流流转继承追问`，英文 `#-task-flow-handoff-continuity-follow-up`。
- 「多端统一」限定语：同一台机器、同一用户数据目录；不宣称密钥跨设备云端同步 —— 双语保持一致。

## 本次重写遗留（后续可选）

- `docs/` GitHub Pages 站点（index.html/docs.html）仍是旧叙事，未与 README 新主线同步。
- en README 的 Quick Start「Option A」下载说明仍指向 GitHub Releases，如后续有官网下载入口可更新。
