# 用户首次使用引导（情境式 Onboarding）产品方案

创建时间：2026-07-27  
最后更新：2026-08-23  
状态：落地中（空任务是首启主路径；设置只是闸门）  
范围：Peer Agent Desktop 主窗口首启与早期使用路径  

关联文档：

- `knowledge/specifications/14-product-design-language.md` §4.1 新任务首屏、§7.2 首屏空状态
- `design/product/desktop-cold-start-brand-startup-loader.md`（冷启动品牌页，非产品引导）
- `design/product/peer-2-0-workbench-flow.md`（工作台是跨任务雷达，不是唯一入口，也不是默认落地页）
- 代码现状锚点：
  - `apps/desktop/renderer/src/chat/components/ChatSurface.tsx`（`hasProvider`、`chat-empty-state`、starter cards）
  - `apps/desktop/renderer/src/chat/components/ComposerDraftControls.tsx`（未配置时 placeholder / disabled）
  - `apps/desktop/renderer/src/app/components/McpSettingsPanel.tsx`、`capabilities/components/SkillsInstalledPanel.tsx`（能力空态）

---

## 一、一句话结论

**不做全屏多步 Wizard，做「情境式引导」：**  
在用户真正需要的那一刻，用主界面内的强提示 / 空态 / 一次性轻 tip 把路径走通；先保证「能发出第一条有价值的任务」，再逐步露出 MCP / Skills / Goal 等进阶能力。

---

## 二、问题与目标

### 2.1 当前问题

| 阶段 | 用户感知 | 现状 |
|---|---|---|
| 冷启动 | 品牌启动页停留 | 有 `BrandStartupLoader`，属于性能/bootstrap 门闩，**不是**产品引导 |
| 首次进入主界面 | 能否立刻干活 | **无**独立 first-run onboarding；无 coachmark / 一次性 tip 框架 |
| 未配置模型 | 发不出去 | 空态文案「请先配置模型」+ Composer placeholder 禁用；可点进设置，但缺少「首启强路径」与完成反馈 |
| 已配置、空会话 | 不知道写什么 | 已有欢迎标题 + 3–4 张 starter cards，基本可用，可再对齐设计语言（任务邀请感、文案层级） |
| 进阶能力 | MCP / Skills / Goal | 仅面板内 empty state（「还没有 MCP 连接」「暂无本地技能」等），首次触达无轻提示 |
| 系统权限 | 麦克风 / 辅助功能等 | 走情境式 `PermissionGateStrip` 等运行时门闩；**不应**在安装后立刻轰炸 |

### 2.2 目标（用户结果）

1. **5 分钟内完成「接通模型 → 看清工作区 → 发出第一条任务」**，无需阅读说明文档。
2. 首屏**不空、不营销、不像 demo**，符合 Peer Frost「高端、简约、克制、强大」。
3. 进阶能力按需露出，可跳过、只出现一次，不打断主任务流。
4. 引导状态可持久化、可重置（设置里「重置引导」可选，P1）。
5. **空任务是首启主路径**。任务是家，工作台是雷达，不是唯一入口；整页设置只是闸门。首启**不再自动打开整页设置**。

### 2.3 非目标（本方案明确不做）

- 全屏 / 模态多步安装向导（账号注册、选套餐、连插件大礼包）。
- 安装后立刻请求系统权限（麦克风、辅助功能、全盘访问等）。
- 强制绑定工作区才能开始（工作区可后续绑定；无工作区时 starter 文案降级为通用任务）。
- 本轮**不改代码**；实现排期见文末 P0/P1。

---

## 三、引导原则

1. **情境触发，不预演**  
   只在状态成立时出现：未配置模型、空会话、首次打开某面板、首次触发某能力。

2. **一条主路径优先**  
   首启唯一主 CTA：**配置模型（或验证已有配置）→ 回到空态发出第一条消息**。  
   MCP / Skills / Goal / 工作区切换均为支线。

3. **嵌入主界面，不盖住工作台**  
   优先：空态文案、Composer 状态、设置内联引导、一次性轻 tip。  
   避免：遮罩式 tour、连续弹窗、右下角堆叠 toast。

4. **可跳过、可恢复、只出现一次**  
   非阻塞提示必须有「知道了 / 不再提示」；状态写入本地偏好（建议 key 见 §六）。

5. **文案是任务邀请，不是产品广告**  
   对齐设计语言：标题像「接下来做什么？」，禁止「欢迎使用某某」「连接插件开启 AI 之旅」类话术。

6. **权限与高风险延后到真实需要**  
   系统权限、不可逆操作、扩大写范围等，继续走现有 permission / Goal 确认链路，不塞进首启。

---

## 四、用户状态机（首启相关）

```text
[冷启动 BrandStartupLoader]
        │ bootstrap 完成（不教育）
        ▼
[主界面 · 空会话]          ← 首启唯一落点；工作台零任务时让路
        │
        ├─ !hasProvider  ──────────────►  Gate A：空会话内嵌窄路径接通模型
        │                                      │ 接通成功后留在空会话
        │                                      ▼
        ├─ hasProvider && messages==0  ─►  Gate B：任务邀请 + 可见工作区 + starter
        │                                      │ 发出第一条消息
        │                                      ▼
        └─ 已有消息 / 已有会话列表 ─────►  正常使用
                                               │
                    首次打开 MCP / Skills / 切入 Goal 模式等
                                               ▼
                                         Gate C：一次性能力 tip（弱）
```

判定锚点（与现实现一致，方案沿用）：

- `hasProvider = providers.some(p => p.apiKeyConfigured)`
- 空会话：`messages.length === 0`
- 「首次」：本地偏好 `onboarding.*` 未 dismiss（见 §六）

---

## 五、情境式引导方案（核心）

### 5.1 Gate A — 未配置模型（P0，阻塞主路径）

**触发**：主界面可见且 `!hasProvider`（含首次安装、清空全部模型配置后）。

**落地裁决**：Gate A 发生在空会话里，不跳整页 Settings。用户手动打开设置仍可用；首启**不再自动打开整页设置**。

**体验**：

| 区域 | 行为 |
|---|---|
| 空态标题 | 保持任务邀请语气，例如「先接通模型，再开始任务」；避免纯错误页 |
| 空态正文 | 一句说明 Agent 会自驱规划并执行，必要时才打断 |
| 空态主路径 | 内嵌窄路径：选一个常用服务、填密钥或登录、接通后留在空会话 |
| 次要出口 | 「打开完整设置」才进入整页 Settings / 服务商 |
| Composer | 继续 disabled；placeholder「请先接通模型」；点击输入区聚焦内嵌接通，不弹整页设置 |
| 关闭设置回到主界面 | 若已 `hasProvider`，空态自动切到 Gate B（starter cards 出现，Composer 可用） |

**不要**：

- 自动打开整页设置 / 服务商。
- 同时推销 MCP / Skills。

**验收**：

- 全新安装 → 留在空会话内嵌引导中接通模型 → 看清工作区 → 无需重启即可发出第一条任务。

### 5.2 Gate B — 已配置、空会话欢迎态（P0，增强现有）

**触发**：`hasProvider && messages.length === 0`。

**现有基础（保留并打磨）**：

- 标题：有工作区时「接下来在 {workspace} 做什么？」；无工作区时「接下来做什么？」
- 副文案：「描述任务，或从下面选一个开始」
- Starter cards：当前实现为卡片式（梳理现状 / 等）；设计语言倾向「3–5 个轻量建议行」。产品取舍：

| 方案 | 说明 | 建议 |
|---|---|---|
| B1 维持轻卡片 | 与现网一致，点击填入 prompt | **P0 维持**，降低改动面 |
| B2 改为建议行 | 更贴 §4.1 / §7.2 | **P1** 视觉收敛 |

**Starter 内容原则**：

- 贴近真实任务（代码仓 / 业务工作台），不要「写一首诗」类玩具示例。
- 有 `workspaceLabel` 时 prompt 带入工作区名；无工作区时用通用表述。
- 建议默认 3–4 条（现网已有），超过 5 条不做。

**可选增强（P0 文案 / P1 交互）**：

- 空态下方一行弱辅助：「可在侧栏切换工作区 · 设置里管理模型」（纯文字，无第二主按钮）。
- 点击 starter → 填入 Composer 并 **focus**（现网 `applyEmptyStarter`）；P1 可提供「填入并发送」。

**验收**：

- 已配置用户新开对话，3 秒内理解「直接输入或点建议」；点建议后输入框有对应文案。

### 5.3 Gate C — 一次性能力提示（P1，弱引导）

仅在用户**主动进入**相关表面，或**首次满足能力前提**时出现；全部可 dismiss，默认只出现一次。

| Tip ID | 触发 | 文案方向 | 形态 |
|---|---|---|---|
| `tip.mcp_empty` | 首次打开 MCP 设置且列表为空 | 「连接 MCP 后，可在对话里调用外部工具」+ 添加入口 | 面板内 banner，非 modal |
| `tip.skills_empty` | 首次打开 Skills 且本地为空 | 「安装技能可复用专项工作流」+ 市场 / 上传入口 | 面板内 banner |
| `tip.goal_mode` | 首次切换到 Goal 模式或首次看到 Goal 计划卡 | 「Goal 会自驱推进并要你确认高风险步骤」 | 会话内一条可关闭说明条 |
| `tip.workspace` | 首次发送且当前无工作区（可选） | 「绑定工作区后，文件与命令默认落在该目录」 | Composer 上方弱提示 |
| `tip.permission` | **不**做首启 tip；维持运行时 PermissionGate | — | 现状保留 |

**规则**：

- 同时最多 1 条 tip 可见。
- 用户点「知道了」→ 永久 dismiss；升级大版本若能力模型变更，可用新 tip id，不复活旧 id。
- 不在用户打字 / 流式输出中插入 tip。

### 5.4 侧栏与其它空态（P1 对齐）

| 表面 | 现状方向 | 引导要求 |
|---|---|---|
| 会话列表空 | 「No chats yet」类 | 一句 + 「新建会话」主按钮即可，不讲模型配置（配置已在主区处理） |
| MCP 空 | 「还没有 MCP 连接」 | 保留；叠加 Gate C banner |
| Skills 空 | 「暂无本地技能」 | 保留；叠加 Gate C banner |
| Workbench / 计划空 | 「暂无计划」等 | 不纳入首启主路径；零任务时只保留一个「发起任务」入口，不讲 0/0/0 |

### 5.5 与冷启动的边界

- `BrandStartupLoader` 只表达「正在就绪」，**不承载**产品教育。
- 引导从 `session` 就绪、主界面首帧之后开始。
- 冷启动过久是性能问题，见冷启动文档；不在本方案用更长动画「假装引导」。

---

## 六、状态持久化（实现契约，供后续开发）

建议本地偏好命名空间（示例，实现时可并入现有 preferences store）：

```text
onboarding.v1
  setupModelAutoOpened: boolean     // 历史字段；现实现不再用它自动打开整页设置
  dismissedTips: string[]           // tip id 列表
  firstMessageAt: number | null     // 首次成功发送时间（分析用，可选）
  completedAt: number | null        // 视为完成首启（hasProvider 且发送过）
```

- 存储位置：与现有 desktop preferences / user settings 同级，避免只写 `localStorage` 导致多窗口不一致（具体以代码仓既有偏好方案为准）。
- 「重置引导」：清除 `dismissedTips`（设置 → 高级，P1）。不再依赖 `setupModelAutoOpened` 抢首启。

---

## 七、关键用户旅程（脚本）

### 旅程 1：全新用户（主路径）

1. 安装并打开 → 冷启动页 → 主界面空会话。  
2. 看到 Gate A：空会话内嵌接通模型；Composer 不可用。不再自动弹出整页设置。  
3. 在空会话里选一个服务并接通。  
4. 留在空会话：Gate B，工作区可见，starter 可见，Composer 可用。  
5. 点 starter 或自写任务，发出第一条消息。  
6. 首启完成；之后不再强引导。

### 旅程 2：已有模型配置（重装或同步配置）

1. 启动后 `hasProvider === true` → 直接 Gate B。  
2. 无强制弹设置。

### 旅程 3：探索 MCP（支线）

1. 用户打开 MCP 设置，列表为空 → 一次 banner。  
2. Dismiss 后永不再显示；添加连接后 banner 自然消失。

### 旅程 4：清空全部模型

1. 回到 Gate A（状态驱动，不是「首次」标志驱动）。  
2. 与是否 dismiss 过 tip 无关——**无模型永远阻塞发送**。

---

## 八、文案草案（中 / 英）

| 场景 | 中文 | English |
|---|---|---|
| Gate A 标题 | 先接通模型，再开始任务 | Connect a model to get started |
| Gate A CTA | 配置模型 | Configure model |
| Gate A Composer | 请先配置模型 | Configure a model first |
| Gate B 标题（有工作区） | 接下来在 {name} 做什么？ | What should we work on in {name}? |
| Gate B 标题（无工作区） | 接下来做什么？ | What should we work on? |
| Gate B 副文 | 描述任务，或从下面选一个开始 | Describe a task, or pick a starting point below |
| Tip MCP | 连接 MCP 后，可在对话里调用外部工具 | Connect MCP to use external tools in chat |
| Tip 知道了 | 知道了 | Got it |

Starter 标题保持任务向（示例，可与现网对齐）：梳理现状 / 排查问题 / 制定方案 / 起草改动——具体 prompt 继续由产品与工作区上下文生成，本方案不锁死字符串。

---

## 九、度量（可选，P1）

| 指标 | 含义 |
|---|---|
| `onboarding_setup_model_click` | 点击配置模型 CTA |
| `onboarding_provider_saved` | 首次保存可用 Provider |
| `onboarding_first_message` | 首次成功发送 |
| `onboarding_time_to_first_message` | 首启到首条消息耗时 |
| `onboarding_tip_dismiss` | tip id + dismiss |

若暂无埋点体系，实现阶段至少保证状态机可手动走查。

---

## 十、分阶段落地（供后续实现，本轮只出方案）

### P0（必须）

1. Gate A：未配置模型的空态强 CTA + 设置闭环 + 保存后无需重启即可聊。  
2. Gate B：巩固现有 Welcome 空态与 starter；保证 focus / 填入稳定。  
3. 明确不自动弹系统权限、不做多步 Wizard。

### P1（增强）

1. Gate C 一次性 tip 框架 + MCP / Skills / Goal 三条。  
2. Starter 视觉向设计语言「建议行」收敛。  
3. 无工作区弱提示；设置内「重置引导」。  
4. 基础埋点。

### P2（可选）

1. 根据角色 / 工作区类型动态 starter。  
2. 首条任务成功后的轻量「下一步」建议（仍非 Wizard）。

---

## 十一、验收标准（产品 DoD）

### 自动可核对（文档）

- [x] 本文档位于 `design/product/`  
- [x] 包含「情境式引导」方案与 P0/P1  
- [x] 含创建时间 / 最后更新  

### 实现阶段走查（本轮不执行代码，仅作为后续验收清单）

1. 全新用户无模型：不能发送；主路径只能先配置模型。  
2. 配置成功返回：starter 出现，发送成功。  
3. 已配置用户：不强制弹设置。  
4. MCP/Skills 空态 tip 只出现一次，可 dismiss。  
5. 冷启动页无产品教育文案堆叠。  
6. 无安装后系统权限轰炸。

### 本轮交付边界

- 落地 Desktop 首启主路径：空会话内嵌接通模型，看清工作区后发出第一条任务  
- 不再自动打开整页设置  
- 工作台零任务给首启让路，只保留一个发起任务入口  
- Gate C tip 框架、埋点、重置引导仍可后置

---

## 十二、开放问题（实现前可再定）

1. 首启是否自动打开整页设置？**已裁决：否。** 空会话内嵌窄路径接通；设置只是闸门。  
2. Starter P0 保持卡片还是提前改建议行？（建议：P0 卡片，P1 收敛。）  
3. 企业预置 Provider（已配置 Key）用户是否跳过一切引导？→ 是，直接 Gate B。  

---

## 十三、总结

Peer Agent 的首启体验应是：

```text
冷启动就绪
  → 主界面空会话
      → 没模型：空会话内嵌窄路径接通（不再自动打开整页设置）
      → 有模型：任务邀请 + 可见工作区 + starter + 大 Composer
      → 用到进阶能力时：一次性轻 tip
```

而不是：

```text
安装向导 → 权限轰炸 → 功能巡礼 → 终于能打字
```

这与现有代码骨架（`hasProvider` 空态 + Composer 门闩 + 能力面板 empty state）同向，后续实现应以**补齐状态闭环与克制提示**为主，而不是另起一套 onboarding 子系统。
