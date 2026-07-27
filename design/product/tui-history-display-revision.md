# TUI 历史展示修订方案：压缩点连续可见

创建时间：2026-07-25
最后更新：2026-07-27
状态：Draft（产品方向已定，待实现）
变更级别：B 级（调整 TUI 渲染窗口策略与文案，不改变模型上下文语义）
关联代码：`peer_agent/apps/tui/src/conversation-render-window.ts`、`app.tsx`
关联原方案：`design/product/tui-conversation-render-window.md`

---

## 1. 问题与反馈

用户反馈：

> 现在动不动就隐藏了，太傻了。之前说的是**从上一次压缩点一直展现到现在**。

当前 UI 顶部常见：

```text
↑ 4 earlier messages hidden · /history earlier
```

这与“连续可读会话”预期冲突。

### 1.1 当前实现（现状）

默认 `latest` 投影逻辑（`projectLatest`）：

1. **有最近一次完成的 compaction**（`system` + `compact.phase === 'done'`）  
   - 起点 = `max(compactionIndex, emergencyGuardStart)`  
   - reason = `latest-compaction`  
   - 若 emergency 再裁，会 `emergencyTruncated=true`，并仍显示 hidden 条数

2. **没有 compaction**  
   - 起点由 `fallbackMaxMessages=120` + `fallbackMaxChars=160_000` 从尾部回扫  
   - reason = `fallback-tail`  
   - 超过阈值就直接 `hiddenBefore > 0` → 显示 “earlier messages hidden”

3. **字符预算估算偏激进**  
   - `estimateMessageChars` 把 tool payload / thinking / images 全算进预算  
   - 几次大工具调用就容易触达 160k，导致“才聊一会儿就 hidden”

4. **历史翻页**  
   - `/history` 以 80 条 / 160k 分页；支持参数 `later` / `latest`（无独立 `/history-*` 命令）  
   - 这是主动浏览，可以保留

### 1.2 根因一句话

阶段 1 把“终端性能防护”做成了**默认体验主路径**，而不是**极少触发的 emergency 护栏**。  
结果是：没有压缩点时也会频繁裁剪；有压缩点时仍可能被 emergency 二次裁。

---

## 2. 主流 CLI 怎么做

| 产品 | 默认历史展示 | 压缩 / 长会话 | 是否“earlier hidden”分页 |
|---|---|---|---|
| **Claude Code** | 连续 transcript，终端 scrollback 可上翻 | compact 是上下文动作；UI 仍以当前会话流为主；Ctrl+O 控制细节展开 | 否（不以“隐藏 N 条”作为主交互） |
| **OpenAI Codex CLI** | 连续对话流 + scrollback | 长会话靠 resume / 新线程，不靠中途藏消息 | 否 |
| **Aider** | 终端原生 scrollback | 依赖终端缓冲；不做应用层消息窗口分页 | 否 |

共性：

1. **默认连续可见**，不让用户感觉“系统偷偷藏了对话”。
2. **压缩是语义边界**（模型上下文变短），不是 UI 分页理由。
3. **性能问题用 scrollback / 折叠细节 / 虚拟化**解决，而不是先把消息砍掉。
4. 只有导出、搜索、审计这类“全量浏览”才需要显式 history 命令。

结论：Peer Agent 应回归“压缩点 → 当前”连续展示；分页只服务**压缩点之前**的归档浏览。

---

## 3. 修订目标

### 3.1 默认可见范围（必须）

```text
[ 压缩点之前的归档 ... ]  [ COMPACTED 边界 ]  [ 压缩后全部消息 ... 当前 ]
         ↑ 可隐藏/按需加载                      ↑ 默认完整连续可见
```

规则：

1. **有最近完成压缩点**：默认从该压缩消息起，**一直展示到最新消息**，中间不因 120 条 / 160k 再藏。
2. **无压缩点**：默认展示**整段会话**（从第一条到最新）。
3. **只有 emergency 护栏**才允许裁最近窗口；触发阈值必须远高于正常会话（见 §5）。
4. 顶部提示语义改变：
   - 压缩点之前有归档：`↑ 压缩前归档 · /history`
   - 不再把“压缩后正常增长”说成 “earlier messages hidden”

### 3.2 非目标

- 不改模型上下文构造 / compaction 语义
- 不改 `ChatSnapshot.messages` 全量持有
- 不删 history 浏览能力：仅保留统一 `/history`，用参数 `later|latest` 切换窗口；Esc 回最新；不注册独立 `/history-*` 别名

---

## 4. 新策略（Latest 模式）

### 4.1 决策树

```text
projectLatest(messages):
  if empty → empty

  compactionIndex = lastCompletedCompactionIndex(messages)

  if compactionIndex >= 0:
      start = compactionIndex          # 默认从压缩点起连续到现在
      reason = 'latest-compaction'
  else:
      start = 0                        # 无压缩点：整段可见
      reason = 'full-session'

  # Emergency only：极端大 transcript 才裁
  if rangeTooLarge(start..end, emergencyPolicy):
      start' = scanBackwardStart(end, emergencyMax*)
      start' = max(start', compactionIndex if any else 0)
      if start' > start:
          emergencyTruncated = true
          start = start'

  return [start..end]
```

### 4.2 与现状差异

| 场景 | 现状 | 修订后 |
|---|---|---|
| 无压缩，消息 30 条但 tool 大 | 可能因 160k 被裁 → hidden | **全展示** |
| 无压缩，消息 200 条 | 只留最近 120 条 | **全展示**（除非 emergency） |
| 有压缩，压缩后 20 轮 | 从压缩点展示（OK）但文案仍像“藏了历史” | 从压缩点展示；文案改为“压缩前归档” |
| 有压缩，压缩后极大 | emergency 可能从压缩点后再裁 | 保留 emergency，但阈值极高，并明确 warning |

### 4.3 文案

**默认（压缩点边界，非 emergency）：**

```text
↑ Earlier conversation compacted · /history
```

中文：

```text
↑ 更早对话已压缩 · /history
```

不要再写：

```text
↑ 4 earlier messages hidden · /history earlier
```

除非：

1. 用户在 history 分页模式；或  
2. emergency 真的裁掉了压缩点之后的部分。

**Emergency：**

```text
⚠ Recent history capped for terminal performance · /history
```

---

## 5. 阈值建议

### 5.1 默认 latest（主路径）

| 参数 | 现状 | 建议 | 说明 |
|---|---:|---:|---|
| 无压缩默认窗口 | 120 msgs / 160k chars | **无限（整段）** | 主路径不再分页 |
| 有压缩默认窗口 | 压缩点 → now（可被 emergency 再裁） | **压缩点 → now** | 与用户预期一致 |
| emergencyMaxMessages | 600 | **2000**（可再调） | 真护栏，不日常触发 |
| emergencyMaxChars | 800_000 | **2_000_000** 或改为“渲染成本”口径 | 见 §5.2 |
| historyPageMessages | 80 | 80~120 | 仅浏览压缩前归档 |
| historyPageMaxChars | 160_000 | 放宽到 400_000 或按页消息数 | 减少半页感 |

### 5.2 估算口径要改

现状 `estimateMessageChars` 把完整 tool JSON 计入，导致预算虚高。

建议拆成：

1. **renderCost（用于窗口）**：可见摘要 / 折叠后 UI 成本  
   - user/assistant 正文  
   - thinking 可按折叠态计低成本  
   - tool 按展示摘要计，而不是 raw payload
2. **rawChars（仅诊断）**：完整 JSON 体积

窗口裁剪只看 renderCost。

---

## 6. History 命令语义（修订）

| 命令 | 语义 |
|---|---|
| `/history` | 统一入口：从默认 latest 进入压缩前归档第一页；再执行则继续翻更早 |
| `/history later` | 向更新一页（`/history` 的参数，不是独立命令） |
| `/history latest` / `Esc` | 回到默认：压缩点→现在 / 无压缩整段 |

默认 latest 下：

- palette 只暴露一个 `history`；不注册 `/history-earlier|later|latest`
- `canLoadEarlier` 仅当 `startIndex > 0`（即存在压缩前归档，或 emergency 裁切）
- 压缩后连续区**不再**被当成“上一页”
- history 分页模式下 `Esc` 一键回最新

---

## 7. 实现边界

### 7.1 改动文件（代码仓）

1. `apps/tui/src/conversation-render-window.ts`
   - `projectLatest`：无压缩 → start=0；有压缩 → start=compactionIndex
   - fallback 120/160k 退出主路径
   - emergency 仍保留
2. `apps/tui/src/conversation-render-window.test.ts`
   - 覆盖：无压缩长会话全展示
   - 覆盖：压缩点后全展示
   - 覆盖：emergency 才裁
3. `apps/tui/src/app.tsx`
   - 顶部文案按 §4.3 改
4. 可选：`estimateMessageChars` 改为 renderCost

### 7.2 不改

- controller / persistence 全量 messages
- provider history 构造
- compaction 执行逻辑

### 7.3 性能护栏（保留，但退后）

若 emergency 触发：

1. 仍展示连续最近段
2. 顶部 warning 明确是性能护栏
3. `/history` 可回看被裁部分

后续阶段再做真正的虚拟列表 / 折叠 tool 详情，而不是靠砍消息。

---

## 8. 验收标准

1. 新会话、无压缩：连续输入远超 120 条前，**不出现** “earlier messages hidden”（除非 emergency）。
2. 发生一次 compact 后：默认从 **COMPACTED 边界** 连续展示到最新；压缩后的轮次全部可见。
3. 顶部若有提示，语义是“压缩前归档/性能护栏”，不是“系统随便藏了 4 条”。
4. `/history` 仍可浏览压缩前内容；`Esc` / `/history latest` 一键回默认。
5. 既有单测更新并通过；补齐上述场景测试。

---

## 9. 分阶段落地

### Phase A（立刻，纠正体验）— 推荐先做

1. `projectLatest` 改为“压缩点→现在 / 无压缩整段”
2. 文案改为压缩归档语义
3. 提高 emergency 阈值
4. 测试更新

### Phase B（稳妥增强）

1. renderCost 估算替代 raw JSON 预算
2. tool/thinking 默认折叠，降低真实渲染成本
3. 记录 emergency 触发 telemetry，验证是否还会误伤

### Phase C（长期）

1. 真虚拟窗口 / 按需挂载
2. 终端 resize 与可见区联动
3. 压缩前归档的更好导航（按压缩点列表，而不是纯页码）

---

## 10. 决策摘要

| 决策 | 选择 |
|---|---|
| 默认可见范围 | **最近压缩点 → 当前**；无压缩则**整段** |
| 120/160k fallback | **退出默认主路径** |
| earlier hidden 文案 | 仅用于归档/emergency，不用于正常增长 |
| 与主流 CLI 对齐 | 连续 transcript；压缩是语义边界 |
| 性能 | emergency 护栏 + 后续虚拟化/折叠 |

一句话：

> **UI 默认应像聊天记录，而不是像分页阅读器。压缩点是唯一自然的“以上为归档”边界。**
