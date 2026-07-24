# 右下角上下文占用圆环失准根因分析

创建时间:2026-07-24
最后更新:2026-07-24(同日二次复核:RC1 已修复,RC2 半修复,见文末状态表)
状态:根因已钉死 / 修复路线并入 `23-compaction-path-root-governance.md` Phase 1
关联代码仓:`peer_agent`(本地 `/Users/liangyin/Documents/DEV/github/peer_agent`)
关联文档:

- `knowledge/decisions/52-unified-next-request-context-accounting.md` — nextRequestInputTokens 唯一口径(本文是其落地缺口清单)
- `knowledge/decisions/42-context-display-vs-trigger-accounting.md` — 已被 ADR 52 取代的双口径历史
- `knowledge/architecture/23-compaction-path-root-governance.md` — 压缩路径根治理(共享估算器下沉即本问题的修复载体)

## 现象

右下角上下文占用圆环长期与真实占用不符(例:显示 8%,实际下一请求占用远高于此);切模型、abort、跨端(CLI↔Desktop)续接后尤其明显。

## 显示链路(2026-07-24 代码核实)

```text
分子取值链(renderer):
  authoritativeContext(权威快照)
    ?? historyContextTokens(renderer 本地估算 tokenEstimate.ts)
  + draftContextTokens(renderer 草稿估算)

权威快照来源:
  a) 会话打开时恢复持久化 contextSnapshot(conversation-store meta)
  b) 发送瞬间 seedAuthoritativeContextOnSend(旧权威 + 草稿估算)
  c) chat:stream:done / chat:compaction 事件携带的 nextRequestInputTokens
     (kernel getContextInfo → computeContextInfo,含 system + tools 投影)

持久化写回:
  llm-chat-service done 分支(仅正常终态且投影>0)
  conversation-compaction-persistence(压缩完成)
  TUI conversation-persistence(idle 且有 requestProjection,source:'tui')
```

## 根因(按影响排序)

### RC1 renderer 兜底估算器成分表错误(系统性偏低)

`apps/desktop/renderer/src/chat/state/tokenEstimate.ts` 与主进程权威投影成分不一致:

| 成分 | 主进程投影 | renderer 兜底 |
|------|-----------|---------------|
| system context(Prompt Assembler 全量) | 计入 | **不计** |
| tools schema(每请求全量发送) | 计入(estimateToolsTokens) | **不计** |
| 图片 | 2000 tokens | 800 tokens |
| 消息框架开销 | 4/条 + 块开销 8 | 固定 10/条 |
| 工具结果 | 实际发送内容 | UI 展示切片 |

Desktop 的 system context + tools schema 通常 20k~40k tokens;分母 200k 时仅漏计部分即造成 10%~20% 固定偏差。直接违反 ADR 52「Renderer 不得自行重建另一套 token 预算」。新草稿会话在首个 done 之前只能用该口径,首屏百分比必然偏低。

### RC2 快照失效面 ≫ 写回面,经常跌回 RC1

`packages/conversation-store/src/index.mjs` 中 append / replaceMessages / patchMessage / updateLastMessage / 切模型 **5 处**均 `contextSnapshot = null`;写回点仅一个(正常 done 且投影 > 0)。abort、stream error、Goal handoff 强制收尾(`llm-chat-service.mjs` 1208 行注释自证曾有「contextSnapshot 永久 null」竞态)、进程退出后,会话重开即无权威值。

### RC3 发送 seed 混口径 + midturn 只升不降

`seedAuthoritativeContextOnSend` = 旧权威值(主进程估算器)+ 草稿(renderer 估算器),两套估算器相加;`mergeAuthoritativeContextSnapshot` midturn 模式 `Math.max` 只升不降,final done 丢失时虚高值残留至下一轮。

### RC4 分母漂移

分母优先权威快照 `contextWindow`;切模型后 store 置 null 只影响下次 load,renderer 内存中 `authoritativeContext` 仍持旧模型窗口,直到下一轮 done 才接管,期间百分比按旧分母计算(`ChatSurface.tsx` ~1429)。

### RC5 双端写同一快照字段但口径不同(CLI 一致性缺口)

TUI 投影 = TUI 轻量 system prompt + 手抄估算器(`context-pressure.ts`,无 microcompact、无 hard 线);Desktop 恢复 TUI 写入的快照后,圆环显示的是「TUI 的下一请求」而非「Desktop 的下一请求」。快照已带 `source: 'desktop' | 'tui'` 字段,但恢复端未按宿主重投影。

### RC6 估算残差(可接受,非主因)

CJK 1.7 / 英文 4 chars-per-token 启发式与真实 tokenizer 有 ±10~20% 残差;ADR 52 有意选择本地估算(`lastActualInputTokens` 仅诊断)。此项解释「永远差一点」,不解释「一直不准」。

## 深层根因

```text
「下一请求投影」没有单一所有者:
主进程有权威投影,renderer 保留自制估算器兜底,TUI 又一套;
三个分子来源 + 两个分母来源,靠 null-guard 与 Math.max 缝合。
与 23 号文档 R2(下沉不完整)/ R4(一致性靠手抄)同源。
```

## 修复方向(并入 23 号文档 Phase 1,不单独开线)

1. **失效即重投影,而非跌回 renderer 口径**:快照带 `contentRevision`(已存),恢复/失效时 revision 不匹配 → 经 IPC 请求 Runtime 按当前宿主重算投影;renderer 删除 `tokenEstimate.ts` 的历史估算,仅保留草稿增量。
2. **草稿增量口径统一**:草稿估算改用下沉后的共享估算器,分子基线必须来自 Runtime。
3. **跨端恢复守卫**:`snapshot.source ≠ 当前宿主` 时不直接采信,触发本宿主重投影。
4. **midturn 乱序保护改 sequence**:用事件序号丢弃过期快照,替代数值 `Math.max`,消除只升不降的虚高锁定。
5. **分母随快照失效一并失效**:切模型立即回退 provider 配置窗口,不等下一轮 done。

## 验收标准

1. 新会话首屏与首个 done 后的占用差 < 估算残差(不再出现成分表级跳变)。
2. abort / error / 强制收尾后重开会话,圆环经重投影显示有效值,而非未知或偏低估算。
3. Desktop 打开 TUI 压缩/续写过的会话,圆环反映 Desktop 下一请求投影。
4. 切模型后分母立即正确,百分比无旧窗口残留期。
5. 仓内历史消息 token 估算实现只剩共享包一份(`tokenEstimate.ts` 历史估算删除)。

## 修复状态(2026-07-24 二次代码复核)

| 根因 | 状态 | 说明 |
|------|------|------|
| RC1 renderer 兜底估算器成分表错误 | ✅ 已修复(删除式) | `tokenEstimate.ts` 只剩草稿增量;`contextOccupancy` 不再接受 history 估算;圆环 = 权威投影 ?? 未知,不再显示伪值 |
| RC2 快照失效面 ≫ 写回面 | ✅ 已修复 | `chat:context:restored` IPC:快照缺失/失效时 renderer 自动请求 Runtime 按完整成分(system+tools+active 历史)重算并回写共享快照;未知期间不渲染伪值 |
| RC3 seed 混口径 + midturn 只升不降 | ✅ 基本修复 | seed 只剩草稿增量;投影事件路径改用 streamId+revision 序合并(`applyContextProjectionEvent`),`Math.max` 仅剩 legacy done/compaction 兼容路径 |
| RC4 分母漂移 | ❌ 未动 | 切模型后到下轮 done 前仍用旧窗口;可在切模型时触发 restored 重投影顺带解决 |
| RC5 跨端同字段不同口径 | ✅ 已修复 | renderer 对 `source ≠ desktop` 快照不再采信,自动触发本宿主重投影;TUI 分子算法已同源 runtime-core |
| RC6 估算残差 | — | 接受,不修 |

新增注意:~~runtime-core `hardRatio 0.92` 与 Desktop `CONTEXT_BUDGET_GUARD 0.95` 双 hard 线分叉~~ 已于 2026-07-24 同日收敛(0.92 单值)。另:流式期间圆环不动的问题已解决——双端 stream_preview 叠加已接线(Desktop `streamPreviewTokens` + 稳定投影事件;TUI delta flush 重算),圆环随 delta 增长、工具落库/回合结束时回到稳定投影。

## 修订记录

| 日期 | 变更 |
|------|------|
| 2026-07-24 | 初版:显示链路普查、RC1–RC6 根因、修复并入 23 号文档 Phase 1 |
| 2026-07-24 | 二次复核:RC1 已修复(删除式)、RC2/RC3/RC5 部分缓解、RC4 未动;新增双 hard 线分叉风险 |
| 2026-07-24 | 三次复核:双 hard 线已收敛;投影事件 revision 序合并落地(RC3 基本修复);双端 stream_preview 接线,流式期间圆环随 delta 增长 |
| 2026-07-24 | 四次复核:RC2/RC5 已修复——restored 重投影 IPC + 跨宿主 source 守卫落地;仅剩 RC4(切模型分母残留期)待修 |
