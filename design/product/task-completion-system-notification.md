# 任务完成系统通知方案

创建时间：2026-07-21
最后更新：2026-07-21
状态：Draft（产品方案，待实现）

关联文档：

- `design/product/status-bar-task-center.md`（状态栏任务中心：投影、未读、attentionVersion）
- `design/product/quick-chat-floating-window.md`（Quick Chat：后台任务卡与回流）

---

## 一、方案摘要

Peer Agent 在后台推进 Goal / 会话任务时，用户经常不在主窗口前台。若任务完成、失败或需要用户处理时没有任何系统级提示，用户只能靠主动切回应用查看，体验不可接受。

本方案定义 **任务完成系统通知（Task Completion System Notification）**：

> 当任务进入需要用户知晓的终态或阻塞态，且用户当前不在对应任务上下文前台时，主进程弹出 OS 系统通知；用户点击通知后回流到对应工作区 / 会话 / Goal，并与状态栏任务中心、Quick Chat 共用同一套未读与去重语义。

一句话原则：

- **系统通知是“打断式提醒”**，不是任务列表，也不是状态栏数字的替代品。
- **状态栏 / Dock Badge 是常驻感知**；系统通知只在关键状态跃迁时触发一次。
- **所有入口共享 `attentionVersion` 与阅读回执**，杜绝重复提醒和状态不一致。

---

## 二、问题与现状

### 2.1 用户问题

1. 任务在后台跑完了，用户在别的应用里工作，没有任何提示。
2. 任务失败或等待用户确认时，用户不知道需要回来处理。
3. 若后续同时做状态栏任务中心、Quick Chat 任务卡，容易出现：
   - 同一事件弹多次通知；
   - 看过了仍反复提醒；
   - 点通知进错会话。

### 2.2 知识库现状

| 文档 | 相关结论 | 缺口 |
|---|---|---|
| `status-bar-task-center.md` §8 | 已定义何时只更新图标 / 何时发系统通知、`attentionVersion` 去重、短时合并 | 仅为任务中心章节内的策略摘要，不是独立可实现规格 |
| `quick-chat-floating-window.md` §9.2 | 主窗口隐藏时可系统通知“任务已完成”，点击打开对应会话 | 未定义去重、权限、失败/等待、与任务中心一致性 |
| 代码仓 `peer_agent` | 存在 `goalPlans:changed`、`goalRunner:*` 事件与主窗口生命周期 | **未使用 Electron `Notification` / Tray 任务通知**；`main.mjs` 未 import `Notification` |

结论：产品意图已有，但 **缺一份可落地的通知专用方案**；代码侧尚无系统通知实现。

---

## 三、目标与非目标

### 3.1 目标

1. 后台任务 **完成 / 失败 / 首次等待用户** 时，在合适条件下可靠弹出系统通知。
2. 同一任务、同一 `attentionVersion` **最多通知一次**。
3. 点击通知 **深链回流** 到对应工作区 + 会话（+ Goal 若有），并推进阅读回执。
4. 与状态栏任务中心、Quick Chat 任务卡 **共享投影与已读语义**，避免重复提醒。
5. 尊重 OS 通知权限与用户设置；权限关闭时静默降级，不反复弹授权。

### 3.2 非目标（首版不做）

- 不在通知上直接批准权限、重试、取消任务。
- 不做富交互通知按钮（macOS Actionable Notification 的批准/拒绝）。
- 不做跨设备通知同步。
- 不替代状态栏任务中心或 Dock Badge。
- 不把进度百分比、排队、工具中间步骤变成通知。
- 首版不强制实现“多任务短时合并为一条汇总通知”（可预留接口，见 §8.3）。
- 首版不覆盖 Windows / Linux 托盘与通知差异（文档预留扩展点）。

---

## 四、角色边界

| 表面 | 职责 | 与通知的关系 |
|---|---|---|
| **系统通知** | 关键跃迁的一次性打断提醒 + 回流入口 | 本方案主体 |
| **状态栏任务中心** | 常驻感知、分组列表、数字 | 消费同一 `TaskCenterSnapshot`；不单独再发一套通知逻辑 |
| **Quick Chat 任务卡** | 高频接续、轻量状态 | 不独立发通知；可展示同一未读任务 |
| **主窗口会话** | 完整上下文与高风险操作 | 前台且正在查看对应会话时，抑制完成类通知 |
| **主进程聚合器** | 状态归一、`attentionVersion`、阅读回执、通知决策 | 唯一决策点，禁止 renderer 各自 `new Notification` |

硬约束：

1. **renderer 禁止直接调用系统通知 API**。
2. 通知决策只读 `TaskCenterSnapshot`（或与之等价的任务投影事件），不从 UI DOM 反推。
3. 阅读回执与通知去重键绑定同一 `attentionVersion`。

---

## 五、触发模型

### 5.1 关注事件（Attention Events）

对每张任务卡（`taskId` 稳定，通常对应 Goal Plan 或可归一的后台会话任务），当归一状态发生下列 **跃迁** 时，生成新的 attention 事件：

| 跃迁 | `attentionReason` | 默认是否通知 | 优先级 |
|---|---|---|---|
| → `waiting_user`（首次进入该次等待） | `input` / `confirmation` / `permission` | **是** | P0（最高） |
| → `failed` | `failed` | **是** | P0 |
| → `completed` | `completed` | **条件是**（见 §5.2） | P1 |
| → `cancelled` | — | **否** | — |
| `queued` ↔ `running`、进度变化 | — | **否** | — |
| 短暂断网后自动恢复且未失败 | — | **否** | — |

每次进入上表“是 / 条件是”的状态时：

```text
attentionVersion := attentionVersion + 1
```

说明：

- 从 `waiting_user` 恢复执行后，该次等待视为已处理；**再次**进入 `waiting_user` 会生成 **新的** `attentionVersion`。
- `completed` / `failed` 各算一次终态 attention；失败后重试再失败，产生新版本。

### 5.2 何时发系统通知（Send）

满足 **全部** 条件才发送：

1. **事件类型允许**：`waiting_user` | `failed` | `completed`（见上表）。
2. **去重通过**：该 `taskId + attentionVersion` 尚未成功发送过（见 §6）。
3. **权限允许**：OS 通知权限为 granted / 未拒绝；用户产品设置“任务系统通知”为开启（默认开启）。
4. **前台抑制规则通过**（见 §5.3）。
5. **应用生命周期允许**：主进程仍在运行；非“正在主动退出应用”的收尾阶段。

### 5.3 何时不发送（Suppress）

以下情况 **不发送**（仍可更新状态栏 / 未读）：

| 条件 | 说明 |
|---|---|
| 用户正在主窗口前台，且当前会话 == 该任务会话 | “看着完成”不打扰；`completed` 与低优先级 `failed` 均抑制；`waiting_user` 若 UI 已明确展示阻塞控件，也可抑制 |
| 用户正在主窗口前台，但当前会话 ≠ 该任务会话 | **仍发送**（用户在看别的事） |
| 主窗口隐藏 / 最小化 / 其他应用前台 | **发送** |
| Quick Chat 浮窗打开且正展示该任务卡完整内容 | 可抑制同版本通知，避免“浮窗上已看见还弹系统条” |
| 通知权限 denied | 不发送、不循环请求授权 |
| 用户关闭“任务系统通知”设置 | 不发送 |
| 同一 `taskId + attentionVersion` 已发送或已标记已读 | 不发送 |
| 历史迁移默认已读的旧任务 | 启动重算时不回放历史通知 |
| 任务被取消 | 不发送 |
| 应用冷启动全量重算 | **不回放**启动前已存在的终态；仅订阅启动后的新跃迁（见 §9） |

前台判定（macOS 首版）：

```text
isAppForeground =
  app 为当前 active 应用
  && 存在主窗口 isVisible && !isMinimized
  &&（可选）主窗口 isFocused 或最近 N 秒内获得过焦点

isViewingSameTask =
  isAppForeground
  && activeConversationId === task.conversationId
```

实现时以主进程可观察状态为准，不依赖 renderer 自报“我在看”。

### 5.4 决策伪代码

```text
onTaskAttention(task, prevStatus, nextStatus, attentionVersion):
  if not isNotifiableTransition(prevStatus, nextStatus): return
  if wasNotified(taskId, attentionVersion): return
  if isHistoricalReplay: return
  if settings.taskSystemNotificationEnabled == false: return
  if notificationPermission != granted: return
  if shouldSuppressForForeground(task): return

  payload = buildNotificationPayload(task, attentionReason)
  ok = showSystemNotification(payload)
  if ok: markNotified(taskId, attentionVersion, at=now)
```

---

## 六、去重与 `attentionVersion` 规则

### 6.1 核心键

```text
dedupeKey = `${taskId}#${attentionVersion}`
```

- **同一键最多成功弹出 1 次**系统通知。
- 阅读回执：`lastReadAttentionVersion >= attentionVersion` 表示该版本已读。
- 已读 **不要求** 必须先弹过通知；用户从状态栏或主窗口看过同样清未读。
- 若已读发生在通知弹出前（极端竞态），则 **取消待发 / 不发**。

### 6.2 `attentionVersion` 生命周期

| 事件 | attentionVersion | lastReadAttentionVersion | 未读 | 可通知 |
|---|---|---|---|---|
| 任务创建 / running | 0 | 0 | 否 | 否 |
| 首次 waiting_user | +1 → 1 | 0 | 是 | 是（若未抑制） |
| 用户在主窗口处理并继续 | 仍为 1 | 更新为 1 | 否 | 否 |
| 再次 waiting_user | +1 → 2 | 1 | 是 | 是 |
| completed | +1 | 旧值 | 是 | 条件是 |
| 点击通知进入会话并展示结果 | 不变 | 更新为当前 | 否 | 否 |
| failed 后重试再 failed | 再 +1 | 旧值 | 是 | 是 |

与 `status-bar-task-center.md` 对齐：

- 一张任务卡对 `unreadCount` 最多贡献 1；
- `unread` 判定：`attentionVersion > lastReadAttentionVersion`；
- 阅读回执按任务持久化，应用重启保留；
- 升级迁移：历史任务缺版本时 **默认已读**，避免海量旧通知/红点。

### 6.3 通知发送记录

主进程持久化（可与阅读回执同 store 或分文件）：

```ts
type NotificationReceipt = {
  taskId: string;
  attentionVersion: number;
  reason: 'waiting_user' | 'completed' | 'failed';
  notifiedAt: string; // ISO
  clickedAt?: string;
  // 可选：系统通知 id，便于替换/关闭
  notificationId?: string;
};
```

约束：

- 发送成功才写入 `notifiedAt`；
- 发送失败（API 抛错）**不**写入，允许后续一次重试；
- 不因 OS 用户手动清掉通知横幅而重发。

### 6.4 与状态栏数字的关系

- 状态栏 `unreadCount` / `actionRequiredCount` **不依赖**是否弹过通知。
- 通知关闭或忽略 ≠ 已读。
- 只有深链到达并满足“已展示对应版本内容 / 成功提交动作”的规则时，才更新 `lastReadAttentionVersion`（与任务中心 §10 一致）。

---

## 七、通知文案与载荷

### 7.1 文案模板（中文首版）

| reason | title | body |
|---|---|---|
| completed | 任务已完成 | `{taskTitle}` |
| failed | 任务失败 | `{taskTitle}`{可选：`: {shortError}`} |
| waiting_user / input | 需要你的回复 | `{taskTitle}` |
| waiting_user / confirmation | 需要你的确认 | `{taskTitle}` |
| waiting_user / permission | 需要你的授权 | `{taskTitle}` |

规则：

- `taskTitle`：Goal 标题或会话标题，截断至约 40–60 字，避免系统截断难看。
- `shortError`：单行、脱敏、不超过约 80 字；无可靠摘要则省略。
- 不在 body 中堆完整日志、token、绝对路径密钥。
- 应用名由 OS 展示，title 不必再写 “Peer Agent：”。

### 7.2 载荷（主进程）

```ts
type TaskSystemNotificationPayload = {
  // 展示
  title: string;
  body: string;
  silent?: boolean; // 默认 false；后续可跟随系统“专注模式”

  // 回流
  taskId: string;
  conversationId: string;
  goalPlanId?: string;
  workspacePath?: string;
  attentionVersion: number;
  attentionReason: 'input' | 'confirmation' | 'permission' | 'completed' | 'failed';

  // 去重
  dedupeKey: string; // taskId#attentionVersion
};
```

Electron 映射建议：

- `new Notification({ title, body, silent })`
- 通过闭包或 `notification` 实例映射表保存 `dedupeKey` / 回流字段（Electron 通知无稳定自定义 data 字段时的做法）
- `toastTimeout` / urgency：失败与 waiting 可用更高紧急度（平台允许时）

---

## 八、点击回流

### 8.1 统一深链

点击系统通知与点击状态栏任务项 **走同一深链处理器**，例如：

```text
peer-agent://task/{taskId}
  ?conversationId=...
  &workspacePath=...
  &goalPlanId=...
  &attentionVersion=...
  &source=system-notification
```

主进程步骤：

1. `app.focus()` / 激活应用。
2. 确保主窗口存在：`show` + `restore` + `focus`。
3. 切换到 `workspacePath`（若当前不同）。
4. 打开 / 聚焦 `conversationId`。
5. 若存在 `goalPlanId`，确保 Goal/Plan 面板或对应任务上下文可见（实现细节跟随现有 Goal UI）。
6. 满足“已展示对应版本内容”条件后，写入阅读回执：
   `lastReadAttentionVersion = max(lastRead, attentionVersion)`。
7. 记录 `NotificationReceipt.clickedAt`。

### 8.2 失败与降级

| 情况 | 行为 |
|---|---|
| 会话已删除 | 打开主窗口 + 友好提示“任务已不可用”；不静默清未读直至用户确认 |
| 工作区不可访问 | 打开主窗口并提示工作区问题 |
| 深链参数残缺 | 仅激活主窗口；打日志 |
| Quick Chat 更适合短选择（低风险 waiting） | 首版仍 **优先主窗口** 以保证上下文完整；V1.1 可按任务中心规则分流到 Quick Chat |

### 8.3 合并通知（预留，首版可不做）

若短时间（如 3s）内多个 **completed** 事件：

- 首版：各发各的（受 OS 折叠策略影响）。
- V1.1：合并为一条 “3 个任务已完成”，点击打开任务中心面板而非单一会话。
- **waiting_user / failed 永不与 completed 合并**。

---

## 九、权限与设置

### 9.1 OS 权限

- 使用 Electron `Notification.isSupported()` 与权限查询（macOS 关注系统通知中心授权）。
- **首次需要通知时**再请求 / 引导，不在安装后立即弹系统授权轰炸。
- 权限为 denied：
  - 状态栏任务中心与 Dock 数字仍可用；
  - 设置页展示“系统通知权限未开启”与跳转系统设置指引；
  - **不反复**弹出授权对话框。

### 9.2 产品设置（建议）

| 设置项 | 默认 | 说明 |
|---|---|---|
| 任务系统通知总开关 | 开 | 关闭后全部不发 |
| 任务完成通知 | 开 | 仅 completed |
| 任务失败通知 | 开 | failed |
| 需要处理时通知 | 开 | waiting_user |
| 主窗口前台且同会话时静默 | 开 | 对应 §5.3 |

首版可只做 **总开关 + 完成/失败/等待三类**，其余用默认策略。

### 9.3 静音与专注模式

- 尊重 OS 勿扰 / 专注模式（由系统决定是否展示）。
- 产品层不强制 `silent: true`，除非用户设置“仅横幅无声音”（后续）。

---

## 十、与状态栏任务中心 / Quick Chat 对齐

### 10.1 单一事实源

```text
Goal / Chat 运行时
    ↓ 事件
TaskCenter Aggregator（主进程）
    ├─ TaskCenterSnapshot → Tray / Popover / Dock Badge
    ├─ Attention 跃迁 → Notification Broker（本方案）
    └─ 阅读回执 store ← 主窗口 / 通知点击 /（未来）面板已读
```

### 10.2 防重复提醒矩阵

| 用户动作 | 系统通知 | 状态栏未读 | Quick Chat 任务卡 |
|---|---|---|---|
| 后台 completed，用户未看 | 弹 1 次 | unread+ | 可显示最近完成未读 |
| 用户点通知进入会话 | 不重弹 | 清该版本未读 | 卡片移除或降级 |
| 用户只点开状态栏面板浏览标题 | 不重弹 | **不清**未读（与任务中心一致） | 不变 |
| 用户在主窗口同会话看完成 | 不弹 | 清未读 | 同步 |
| 同版本失败已弹过 | 不重弹 | 保持未读直至查看 | 可显示 |

### 10.3 文案一致性

- 状态栏卡片标题、通知 body 中的任务名、Quick Chat 任务卡标题均来自同一 `task.title`。
- 状态文案语义一致：完成 / 失败 / 等待你处理。

### 10.4 实现分工建议（代码仓落地时）

| 模块 | 职责 |
|---|---|
| `task-center-aggregator`（可新建） | 归一状态、snapshot、attentionVersion |
| `task-notification-broker`（可新建） | 订阅 attention、去重、调用 `Notification`、点击回流 |
| `goal-runner` / chat runtime | 只发领域事件，不直接弹通知 |
| renderer | 展示 UI；通过 IPC 上报“当前会话 / 已展示结果”以更新回执 |

---

## 十一、首版范围

### 11.1 必须包含（MVP）

1. 主进程 `Notification` 发送路径（macOS 优先）。
2. 触发：`completed` / `failed` / `waiting_user` 三类跃迁。
3. 前台同会话抑制规则。
4. `taskId + attentionVersion` 去重与发送回执持久化。
5. 点击回流：激活主窗口 → 工作区 → 会话。
6. 与阅读回执联动（点进并展示后已读）。
7. 权限 denied / 用户关闭设置时的静默降级。
8. 启动不回放历史通知。
9. 与 `TaskCenterSnapshot` 字段对齐（即使 Tray 尚未上线，通知 broker 也按同一模型工作）。

### 11.2 明确不做（MVP）

- 通知内联操作按钮（批准/重试）。
- 多任务合并汇总通知。
- Windows/Linux 专项适配。
- 自定义通知声音包。
- 基于邮件/IM 的远程推送。
- renderer 侧任意 `new Notification`。

### 11.3 后续

- V1.1：completed 短时合并；低风险 waiting 点击进 Quick Chat。
- V1.2：通知设置细分；失败摘要质量提升。
- V2：跨平台；可行动通知按钮（需严格安全边界）。

---

## 十二、验收场景

### 12.1 发送与抑制

1. **后台完成应通知**  
   主窗口隐藏，Goal 跑至 `completed` → 弹出“任务已完成”系统通知，body 含任务标题。

2. **同会话前台完成不通知**  
   主窗口前台且正查看该会话，任务 `completed` → **不**弹系统通知；会话内状态正常更新。

3. **前台但不同会话应通知**  
   主窗口前台查看会话 A，会话 B 的任务完成 → **应**弹通知。

4. **失败应通知**  
   后台任务 `failed` → 弹出“任务失败”通知。

5. **等待用户应通知**  
   任务首次进入 `waiting_user` 且主窗口未展示该阻塞 → 弹出“需要你的…”通知。

6. **取消不通知**  
   用户取消任务 → 不弹通知。

7. **进度不通知**  
   running 进度从 10%→80% → 不弹通知。

### 12.2 去重与 attentionVersion

8. **同版本只弹一次**  
   同一 `taskId + attentionVersion` 在事件重复投递 / 聚合重算时 → 仍只成功弹出 1 次。

9. **再次等待可再通知**  
   waiting → 用户处理继续 → 再次 waiting → `attentionVersion` 递增 → 允许再弹 1 次。

10. **已读后不重弹**  
    用户已在主窗口看过该完成结果后，聚合器重放同一版本 → 不弹通知。

11. **启动不回放**  
    退出前已有未读完成任务，重启应用 → **不**为旧终态补发通知；状态栏未读可仍显示（若任务中心已实现）。

### 12.3 点击回流

12. **点击打开正确会话**  
    点击完成通知 → 应用激活，进入对应 `workspacePath` + `conversationId`。

13. **点击后未读清除**  
    深链进入并展示对应版本结果后 → 该任务 `lastReadAttentionVersion` 更新，未读消失；不再就该版本弹通知。

14. **会话已删**  
    点击通知但会话不存在 → 主窗口打开并提示，不崩溃。

### 12.4 权限与设置

15. **权限关闭**  
    系统通知权限关闭 → 不弹通知、不死循环要权；应用内其余任务状态仍可用。

16. **产品开关关闭**  
    用户关闭“任务系统通知” → 任何 completed/failed/waiting 都不弹。

### 12.5 跨入口一致

17. **与状态栏一致**  
    通知弹出后，状态栏（若已实现）未读/待处理数字与 snapshot 一致，不出现“通知说完成了但列表没有”的分叉。

18. **与 Quick Chat 一致**  
    Quick Chat 任务卡展示的标题与通知 body 任务名一致；在主窗口已读后，Quick Chat 不再把该任务当未读完成卡。

---

## 十三、风险与开放问题

| 风险 | 缓解 |
|---|---|
| 无 Tray 时仅靠通知，忽略后难找回 | 尽快落地任务中心；MVP 通知点击必须可靠回流 |
| OS 合并/折叠通知导致体感“没弹” | 验收以发送 API 成功 + 系统权限为前提；文档注明系统行为 |
| 前台判定不准导致误打扰或漏通知 | 主进程统一判定；宁可“不同会话前台仍通知” |
| 与 Goal 子任务粒度混淆 | 通知粒度 = 任务中心卡片粒度（通常一个 Goal Plan / 会话任务），不对每个 leaf subtask 弹 |
| 安全：通知体泄露敏感路径 | 标题脱敏截断；错误摘要白名单字段 |

开放问题（实现前可再定）：

1. Chat 模式非 Goal 的长工具运行是否完全同一套？（建议：**是**，统一进 TaskCenter 投影后再通知。）
2. `waiting_user` 在主窗口已显示权限气泡时是否绝对抑制？（建议：**是**。）
3. Dock Badge 是否与通知同步加一？（属任务中心范围；通知方案不单独维护 badge。）

---

## 十四、落地检查清单（给工程）

- [ ] 主进程引入 `Notification`，集中在 `task-notification-broker`（名称可调整）。
- [ ] 订阅任务归一跃迁，禁止业务模块直接 `new Notification`。
- [ ] 持久化 `NotificationReceipt` + 复用 `lastReadAttentionVersion`。
- [ ] 实现 §5.3 前台抑制与 §8 深链。
- [ ] 单元测试：去重键、抑制矩阵、启动不回放。
- [ ] 手动验收：§12 场景 1–16（17–18 依赖任务中心/Quick Chat 进度）。

---

## 十五、总结

任务完成系统通知解决的是 **“后台结果无人知晓”**，不是再造一套任务 UI。

首版抓住三条线即可上线：

1. **该不该弹**：完成 / 失败 / 等待 + 前台同会话抑制 + 权限设置。  
2. **弹几次**：`taskId + attentionVersion` 一次。  
3. **点了去哪**：主窗口正确工作区与会话，并写回同一阅读回执。

状态栏负责任知与清单，Quick Chat 负责轻量接续，系统通知只做关键打断——三者共用投影，用户就不会被重复打扰，也不会漏掉真正需要处理的事。
