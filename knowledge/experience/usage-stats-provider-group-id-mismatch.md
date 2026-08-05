# 用量统计 Provider 分组重复行：ID 双轨制在统计路径的复发与修复

创建时间：2026-08-03
最后更新：2026-08-03

## 一句话结论

`cli-desktop-model-binding-id-mismatch.md` 记录的「模型条目 uuid vs 渠道 groupId」双轨制，这次在**用量统计**路径复发：请求级快照落的是模型条目 uuid，「按 Provider」聚合只拆复合 id，于是同一渠道（如 Qoder CLI）的每个模型条目各占一行、全显示渠道名，看起来像重复了十几条。修复按 A+B 双保险落地：写入层落渠道 groupId（B），聚合层用 provider 索引把历史裸 uuid 归一到渠道（A）。

## 现象

设置页「用量统计」按 Provider 表里出现十几条同名的 "Qoder CLI" 行（各自 token 量不同），Gemini OAuth 只有 1 行。数字本身没错，错在分组粒度：行键是模型条目 uuid，行显示名却取了渠道名。

## 根因链

1. 主数据源 `~/.peer-agent/usage/requests.jsonl`：每个 Runtime turn 落一条快照，`modelProviderId` 写的是 Desktop 请求时的**模型条目 uuid**（实测 2081 条、23 个不同值、全部不含 `::`）。
2. 聚合层 `usage-stats.mjs` 的 `providerKey` 只处理复合 id：`splitCompositeProviderId(...).groupId || 原值`。裸 uuid 原样成行 → 同一渠道 N 个模型条目 = N 行。
3. 行的显示名取快照里的 `providerName`（渠道名），同名行叠加造成「重复」观感。
4. 这恰是 ID 双轨制文档里「Desktop 写 uuid / 归组应认渠道」的同一结构性错位在统计消费端的体现：上次修 CLI 崩溃时，三形态索引只用在了会话绑定恢复路径；会话 lifetimeUsage 回退路径接了索引，但**请求级主路径没接**。

## 修复内容（`peer_agent` 代码仓，未提交）

| 层 | 文件 | 改动 |
|---|---|---|
| 写入层 B | `apps/desktop/electron/main/usage-request-log.mjs` | `append` 落 `groupId`：显式值优先 → 复合 id 拆解 → 裸 uuid 留 `null`（不猜） |
| 写入层 B | `apps/desktop/electron/main/llm-chat-service.mjs` | `recordConversationUsage` 用 providers 反查实际渠道 `groupId`（id / groupId / `groupId::model` 三形态），注入 `recordRuntimeTurnUsage` attribution 与 legacy `append` |
| 写入层 B | `packages/conversation-store/src/index.mjs` | ledgerRow 落 `groupId`（显式优先，复合 id 拆解回退） |
| 聚合层 A | `apps/desktop/electron/main/usage-stats.mjs` | `providerKey` 归组优先级：写入层 groupId > 复合 id 拆解 > provider 索引（byId/byGroupId）归一裸 uuid > 原值回退；`buildUsageStatsSnapshot` 主路径注入 `buildProviderIndex(providers)`；`buildProviderIndex` 导出 |

设计要点：
- **写入时落当次真值**符合现有「写入时落当次实际模型 + 当时单价」的归因原则，渠道后续改名/重组不串账。
- **裸 uuid 不在写入层猜**：留给聚合层用当前 provider 索引归组；渠道已删除时回退原 key，不丢行不串账。
- 模型维度（byModel）仍按条目拆分，不受渠道归组影响。

## 验证

- 单测：`usage-stats.test.mjs` + `usage-request-log.test.mjs` 19/19 通过（含 uuid 归组、写入 groupId、索引缺失回退、snapshot 端到端收敛）；conversation-store 4 套件与 llm-chat-service usage 断言通过（3 个既有失败与本次无关，干净 HEAD 上同样失败）。
- 真实数据冒烟（`scratch/usage-group-smoke.mjs`，只读）：2081 条真实记录，provider 行 23 → 6；**Qoder CLI 17 行 → 1 行**；input/output/cacheRead token 总量逐项与修复前一致。

## 经验教训

- **同一 ID 语义错位会在每个消费端独立复发**：会话绑定恢复、lifetimeUsage 回退、请求级聚合三条路径先后都踩了同一个坑。凡消费 `modelProviderId` 做分组/解析的路径，都要显式选择「三形态索引归一」或「优先读 groupId 字段」，不能默认形态一致。
- **分组键与显示名分离是这类 bug 的放大器**：键是 uuid、名字是渠道名时，数据正确但视觉上"重复"。排查统计表异常先看行键（key）再看标签（label）。
- **写入层落真值 + 聚合层兜历史**是处理存量脏数据的标准组合：只做聚合归一（A）依赖当前渠道配置还在线；只写入 groupId（B）救不了历史行。两者都做才闭环。

## 关联

- 同一根因首次暴露：`knowledge/experience/cli-desktop-model-binding-id-mismatch.md`（CLI 崩溃修复，commit `4e7da07`）。
- 三形态索引参照实现：`apps/desktop/electron/main/usage-stats.mjs` 的 `buildProviderIndex` / `resolveProviderRecord`。
