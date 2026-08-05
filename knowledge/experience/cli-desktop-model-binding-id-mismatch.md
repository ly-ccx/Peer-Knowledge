# CLI/Desktop 会话模型绑定 ID 双轨制导致 CLI 崩溃的修复

创建时间：2026-07-30
最后更新：2026-07-30

## 一句话结论

模型**目录**双端确实同步（共读 `~/.peer-agent/llm-providers.json`），但会话 meta 里 `modelProviderId` 的 **ID 语义从未被定义成跨端契约**：Desktop 写"模型条目 uuid"，CLI 只认"渠道 groupId"。每个渠道第一个模型恰好 `id == groupId`，掩盖了问题——直到在桌面端选中"组内后加的模型"（如 Qoder CLI 的 Ultimate），CLI 恢复会话时严格 `setSelection` 直接 throw，在 React effect 里裸调无兜底，整个 TUI 崩溃。

## 现象

CLI 启动/恢复会话时红色堆栈崩溃：

```
Error: Selected model or reasoning effort is unavailable.
    at setSelection (...)
    at react_stack_bottom_frame (...)
```

`react_stack_bottom_frame` 说明抛错点在 useEffect——即"外部会话变更恢复"路径（Desktop 或另一 CLI 实例写了同一会话文件后触发）。

## 根因：三种 ID 形态，两端各认一种

Desktop 自己的 `usage-stats.mjs` 注释已承认真实会话里 `modelProviderId` 存在三种形态：**模型条目 id（uuid）**、**渠道/组 groupId**、**复合 id `groupId::model`**（legacy）。

| 端 | 会话绑定写什么 | 读取时认什么 |
|---|---|---|
| Desktop | 模型条目 uuid（`ChatSurface.handleModelChange` 写 `provider.id`） | 三形态全兼容（`resolveProviderRecord` 建 byId/byGroupId/byComposite 三索引），发送时不可用还会自动回退 |
| CLI | groupId（`credentialIdOf = groupId ?? id`） | 只认 groupId + legacy 复合后缀剥离；找不到就 throw |

两个关键叠加因素：

1. **巧合掩盖**：Desktop `addProvider` 不传 groupId 时 `groupId = newId = id`，所以每个渠道的**主模型行** uuid 恰好等于 groupId，CLI 碰巧能解析。单模型渠道（如 Grok）永远不炸；只有多模型渠道的非主行模型（Ultimate/Auto、订阅渠道的 gpt-5.5/terra/luna 等）才触发。
2. **容错策略不对称**：conversation-store 明确注释"强绑定校验不在存储层做，发送时校验+自动回退"——Desktop 全链路宽松回退，CLI 却在恢复路径用严格 throw 消费同一份"如实存取"的数据，把 Desktop 能容忍的历史脏数据（如绑定指向订阅组、model 快照却是 grok-4.5 的漂移行）全变成崩溃点。

## 本机实锤数据（2026-07-30）

```
✅ modelProviderId: "f5ab0732…"  model: grok-4.5    ← groupId 形态（主行巧合），CLI 认识
✅ modelProviderId: "4cbe42eb…"  model: gm51model   ← groupId 形态（主行巧合），CLI 认识
❌ modelProviderId: "222ad20f…"  model: ultimate    ← Ultimate 模型行 uuid（属 Qoder CLI 组 4cbe42eb…），CLI 目录无此 key → 崩溃
```

## 修复内容（`peer_agent` 代码仓，commit `4e7da07`，dev/0.0.1）

数据通路：共享元数据 → CLI 目录 → 解析函数 → 两处恢复调用点。

| 层 | 文件 | 改动 |
|---|---|---|
| 共享元数据 | `packages/runtime-node/src/shared-model-config.ts` | `SharedModelMetadata` 新增 `entryId`（Desktop v2 `models[].id`），`metadataFromSelected` 落值 |
| 目录契约 | `packages/runtime-node/src/model-catalog.ts` | `RuntimeModelCatalogEntry` 新增可选 `entryId` |
| CLI 目录构建 | `apps/tui/src/model-config.ts` | catalog entry 透传 `entryId` |
| 解析函数 | `apps/tui/src/tui-model-selection.ts` | 新增 `resolvePersistedModelSelection`：精确 `groupId+model` → entryId（uuid 绑定）映射回 groupId 条目 → 组内回退（兜漂移脏数据）；effort 不支持钳制到该模型默认档；全失败返回 `null` 而非 throw |
| 恢复调用点 | `apps/tui/src/app.tsx` | 外部变更 effect 与 `/resume` 均先解析再应用；解析失败保持当前模型（`/resume` 给 notice） |

行为边界：

- 恢复时**不回写**会话 meta（避免误清 Desktop 的 context snapshot）；用户主动切模型时 `syncModel` 照旧写 groupId 规范形态。
- picker 路径的 `setSelection` 严格 throw 语义保留（其输入本身来自 catalog，合法）。

## 验证

- runtime-node：81/81 通过（含新增 entryId 透传断言），typecheck 绿。
- TUI：新增用例覆盖真实炸点（uuid 绑定 → 映射回组条目、effort 钳制、漂移回退、不可用返回 null）；全套 544 测试 542 过，2 个失败为存量问题（`composer-status-view.tsx` 裸色值违反主题治理、系统外观翻转监听环境相关），与本次无关。

## 经验教训

- **共享存储文件 ≠ 共享契约**。`llm-providers.json` 的读写协议有 shared-model-config 明确承载，但会话 meta 里 `modelProviderId` 的 ID 语义从没写成跨端契约，两端各自"合理"地选了不同解读。跨进程/跨端共享的每个字段，都要明确"谁写、写什么形态、谁读、怎么解析"。
- **"巧合相等"是最危险的对齐假象**：主模型行 `id == groupId` 让大部分场景正常工作，把结构性错位藏到了低频路径（多模型渠道的非主行模型）里。验证跨端一致性时要专门构造"标识不巧合"的用例。
- **宽松写入 + 严格读取 = 定时炸弹**：存储层"如实存取不校验"的设计必须配套所有消费端的容错解析。任何一端用 throw 消费共享持久化数据，就要求全体写入方永远规范——这个前提在多写者体系里不成立。
- **useEffect 里裸调可 throw 的 API 会放大故障半径**：一次解析失败从"该会话换不了模型"升级成"整个 CLI 崩溃"。恢复/同步类 effect 内的严格校验 API 一律需要显式失败路径。
- 排查时**先看真实数据再下结论**：本次直接读用户本机 `llm-providers.json` 与会话 index，用实际 uuid/groupId 对照实锤了理论分析，避免了"理论上应该同步"的来回拉扯。

## 关联

- 同主题背景：`knowledge/experience/anthropic-output-effort-xhigh-降级修复.md`（effortLevels 透传断流，同属"能力/标识声明未透传到消费端"一类）。
- Desktop 参照实现：`apps/desktop/electron/main/usage-stats.mjs` 的 `resolveProviderRecord`（三形态索引）。
- **同一 ID 双轨制在用量统计路径的复发与修复**：`knowledge/experience/usage-stats-provider-group-id-mismatch.md`（2026-08-03，请求级快照裸 uuid 导致「按 Provider」每模型条目一行；A 聚合归一 + B 写入落 groupId 双修复）。
