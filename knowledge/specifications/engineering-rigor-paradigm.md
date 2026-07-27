# 工程严谨范式（Engineering Rigor Paradigm）与 Peer 落地

> 创建时间：2026-07-28
> 最后更新：2026-07-28
> 状态：规范（总纲）— 从 Codex session 与 Peer 托盘/启动/上下文占用等案例抽出的**可迁移工程思维操作系统**，以及嵌入 Peer 现有链路的落地方式
> 关联：
> - `design/product/agent-mode-default-and-adaptive-planning.md`（Agent 默认 + L0–L3）
> - `design/product/goal-mode-ultrathink-workflow.md`（Goal 闭环 / DoD-as-Code）
> - `knowledge/architecture/00-engineering-philosophy.md`（本地优先 / 证据优先）
> - 实例：`knowledge/experience/desktop-startup-init-slowness.md`、`context-occupancy-ring-inaccuracy-root-cause.md`；托盘图标对比 session（Peer `01713cd9-…` / Codex `019fa425-…`）

---

## 〇、定位

| 文档类型 | 本篇角色 |
| --- | --- |
| 哲学 | 不替代 `00-engineering-philosophy.md`，而是把它落到「单次任务怎么想、怎么验收」 |
| 规范 | 规定非琐碎任务的默认思维顺序与质量门 |
| 落地 | 规定如何嵌进 mode / prompt source / plan / DoD / verifier / UX，而不是只写鸡汤 |
| 案例库 | 不替代 `knowledge/experience/*`；案例证明范式，范式约束案例写法 |

**一句话内核：**

> **先把用户语言翻译成系统语言，再做最小正确解，并用证据关闭问题。**

---

## 一、为什么需要总纲

### 1.1 反复出现的失败模式

| 失败 | 表现 |
| --- | --- |
| 症状疗法 | 用户说糊/慢/不准 → 直接调参、重画、加缓存 |
| 用户当 QA | 本可自检的预览/日志/尺寸，反复丢给用户重启确认 |
| 临时资产长期化 | 先能跑，母版/管线/命名永远不补 |
| 计划有步骤无因果 | 任务列表是文件清单，不是根因链路 |
| 默认路径最松 | 最常用 chat 无诊断门；最严谨 goal 不在默认入口 |

### 1.2 专家代理与普通助手的差

| 维度 | 普通助手 | 工程严谨代理 |
| --- | --- | --- |
| 听用户 | 照做 | 翻译后再做 |
| 第一步 | 改 | 建模 + 取证 |
| 成功标准 | 用户暂时不骂 | 证据关闭问题 |
| 修改单位 | 文件 / UI 点 | 因果链 |
| 工具观 | 有什么用什么 | 匹配问题尺度 |
| 质量来源 | 多轮反馈 | 前置约束 + 自检 |
| 文档角色 | 事后记录 | 约束与验收的一部分 |

---

## 二、思维操作系统（10 步）

非琐碎任务默认顺序。允许跳步，但**跳过必须可辩护**（例如 L0 纯问答）。

```text
1. 接收症状 / 需求
2. 问题重写（系统语言）
3. 约束建模（平台/产品/工程/验收）
4. 分层取证（先契约与链路，后表现）
5. 主根因 + 可证伪点
6. 工具适配（拒绝错误工具）
7. 单一真相源
8. 最小正确解（覆盖因果链）
9. 证据闭环自检
10. 交付：结论 + 变更面 + 验收方式
```

中途证据打脸主根因 → **回到 4**，禁止硬刚。

---

## 三、分步细则

### 3.1 问题重写（Problem Rewrite）

用户原话几乎总是症状。动手前用一句话写出：

> **真正的问题是：______（系统层）导致 ______（可观察症状）。**

| 用户原话 | 差的翻译 | 好的翻译 |
| --- | --- | --- |
| 图标太糊 | 画清楚一点 | tray template 像素预算 / `@2x` 语义 / 加载缩放链路 |
| 启动好慢 | 优化一下 | 离开启动页的关键路径被何种同步 I/O 阻塞 |
| 百分比不准 | 调一下算法 | 显示口径与发送口径分叉，权威快照失效面 |
| 有时丢消息 | 加个重试 | 状态机哪条转移丢事件 |
| 不好用 | 重做 UI | 任务目标在信息架构哪一步失败 |

写不出来 = 还没理解问题 = **禁止大规模改代码**。

### 3.2 约束建模（Constraint Modeling）

先列约束，不列方案：

1. **平台约束**（OS / Electron / API 语义）  
2. **产品约束**（这是什么入口、不是什么）  
3. **工程约束**（兼容、打包、测试、单一真相源）  
4. **验收约束**（怎样叫好、怎样叫关闭）  

并显式列出 **错误工具 / 错误做法黑名单**（例：16px template 不用生成式位图碰运气）。

### 3.3 分层诊断（Layered Diagnosis）

推荐排查顺序（从更底层、更中心、更可证伪开始）：

```text
1. 契约 / 语义     API、状态机、命名约定、口径定义
2. 数据 / 真相源   谁是 source of truth，是否双写双估
3. 加载 / 传输链   路径、打包、scaleFactor、IPC、序列化
4. 渲染 / 呈现     像素、布局、动画、文案
5. 审美 / 润色     圆角、间距、气质
```

**规则：** 未排除下层契约/加载错误前，不沉迷表现层手艺。

### 3.4 根因优先（Root Cause First）

候选解释必须回答：

1. 是否解释**全部**关键症状？  
2. 有无**最小证据**？  
3. 修它是否顺掉一串下游问题？  

| 好的根因 | 差的根因 |
| --- | --- |
| Retina 文件名不被识别，@2x 当 1x 硬缩 | 有点糊 |
| renderer 估算漏计 system+tools | 可能是缓存 |
| 启动门闩绑死全量 jsonl 扫描 | 再优化一下 |

**法则：** 同时存在管线/契约问题与表现/手艺问题 → **先修管线**。

### 3.5 工具适配（Tool Fitness）

| 问题尺度 | 正确工具 | 错误工具 |
| --- | --- | --- |
| 16px 系统图标 | SVG 母版 + 确定性导出 | 生成图碰最终资产 |
| 状态不同步 | 状态机 + 日志证据 | 到处 setState |
| 性能卡顿 | 关键路径计时/采样 | 无证据乱加缓存 |
| 协议 bug | 抓包/对契约 | 先加 UI 重试 |
| 设计方向探索 | 低成本草图 | 一上来写死实现 |

用户点名的工具也可以是错的；专家价值包含 **拒绝并解释**。

### 3.6 单一真相源（Single Source of Truth）

反复会变的东西必须有母版：

- 图标：SVG / 生成脚本  
- Token：一套设计 token  
- 占用口径：一套权威投影  
- 配置：schema  
- 状态：明确 owner  

检验：`若改一次要动几处？` → 答案 > 1 则未建真相源。

### 3.7 最小正确解（Minimal Correct Fix）

是 **Correct**，不是 Minimal Hack。

通常包含：

1. 修根因  
2. 修被污染产物  
3. 防复发（测试 / 校验 / 命名约束 / 文档）  
4. 清理错误中间态  

反例：只改 png 不改 loader；只改显示不改写回。

### 3.8 证据闭环（Evidence Loop）

| 级别 | 例子 |
| --- | --- |
| 静态 | 代码路径、文件名、契约 |
| 生成物 | 导出 png、构建产物、snapshot |
| 运行 | 测试、日志、实际 scale/尺寸 |
| 感知 | 深浅色预览、真实菜单栏、真实启动路径 |

规则：

- 能自检就不把用户当探测器  
- 「我觉得可以了」不是关闭条件  
- Goal/Agent 的 evidence 字段应指向**根因相关**证据，而非无关命令成功  

### 3.9 完成定义（Definition of Done）

任务结束前核对：

- [ ] 根因已用系统语言说清  
- [ ] 修改覆盖因果链，不只是症状点  
- [ ] 有 source of truth  
- [ ] 有可重复验收步骤  
- [ ] 旧路径/旧资源/旧假设已处理  
- [ ] 用户下一步是确认，而不是继续当调试器  

若用户连续纠错 ≥ 3 次仍在同一症状上打转 → **DoD 当初失败**，应停手重做诊断，而不是继续微调。

### 3.10 沟通范式

推荐结构：

1. 结论（根因一句话）  
2. 证据  
3. 方案（改哪些链路）  
4. 不做项  
5. 验收方式  

禁用空话：`优化一下` / `先临时做做` / `你看糊不糊`（在自检之前）。

---

## 四、反模式黑名单（看到就停）

1. 用户驱动试错：丑→改、糙→改、大→改  
2. 先能跑再说：临时资产无回收  
3. 工具迷信：用户点啥用啥  
4. 表现层沉溺：不查加载/口径/状态机  
5. 多真相源：各算各的、各画各的  
6. 交付半截：只改 A，B/C 仍按旧假设  
7. 外包验收：可自检项甩给用户  
8. 解释含糊：用「处理一下」代替因果  
9. 为仪式感建空心大计划  
10. 证据与成功标准无关（跑了个不相关 test 也算完成）  

---

## 五、案例锚点（范式如何被证明）

### 5.1 托盘图标「糊」（对照）

| 步骤 | Codex 路径（强） | 松散路径（弱） |
| --- | --- | --- |
| 重写 | template 语义 + @2x + 像素预算 | 再画好看点 |
| 拒工具 | 生成图不进最终 16px | 直接当最终资产 |
| 根因 | 命名/scale/占用 | 用户反馈驱动重绘 |
| 真相源 | SVG 母版 | 多版手工 png |
| 闭环 | 自预览深浅色 | 多次让用户重启看 |

### 5.2 启动慢 / 上下文圆环不准

已有 experience 文是本范式的**实例**：

- 关键路径上的同步 I/O / 门闩  
- 显示口径与权威快照分叉  

写法要求：根因层、证据、修复链、防复发；禁止只写「已优化」。

---

## 六、嵌入 Peer 现有工程链路（落地总表）

> 原则：**不另起炉灶**。把专家默认动作编码进 mode / source / plan / DoD / verifier / 面板。

### 6.1 链路全景与缺口

```text
用户请求
  → mode 分流（现状 chat/plan/goal → 目标 Agent/Plan）
  → brainstorming（建设型设计门）
  → 【缺口】diagnosis gate（症状型根因门）
  → 【缺口】adaptive depth L0–L3
  → goal_create_plan / micro-plan
  → 批准（仅 L3/Plan）或自驱
  → act + evidence
  → 【缺口】evidence 与 successCriteria 根因相关性
  → verifier / 完成门
```

| 已有强项 | 主要缺口 |
| --- | --- |
| Goal 自驱闭环、DoD-as-Code、hooks、生命周期治理、brainstorming、mode 工具投影、证据字段 | 默认入口过松；chat 无结构；诊断非强制；计划偏文件清单；弱 DoD 仅告警；自检预览文化不足 |

### 6.2 按层级嵌入

#### A. 模式层（产品入口）

见 `agent-mode-default-and-adaptive-planning.md`：

- 默认 **Agent**（Goal 哲学 + 低摩擦入口）  
- **Plan** 保留人审  
- L0–L3 决定计划重量  

**落地产物：** UI 文案、`MODE_COPY`、wire 兼容策略、runtime reminder 当前深度。

#### B. Prompt / System Context 层

| Source / 规则 | 作用 | 优先级建议 |
| --- | --- | --- |
| mode-copy（Agent） | 执行哲学、最少打扰、自动规划 | P0 |
| adaptive-planning source | L0–L3 路由与禁止项 | P0 |
| diagnosis-gate source | 症状任务强制问题重写与根因字段 | P0 |
| brainstorming source | 建设型设计门（已有，保持） | 已有 |
| evidence-quality 规则 | evidence 必须映射 successCriteria | P1 |

投影策略：L0 不灌长大诊断文；L2/L3/bugfix 全量诊断规则。

#### C. 计划数据模型层

GoalPlan / micro-plan 增强字段（实现可分期）：

```text
planningDepth: L0 | L1 | L2 | L3
diagnosis?: {
  problemRewrite
  constraints[]
  rootCauseHypotheses[]
  sourceOfTruth
  causalChain[]
  nonGoals[]
}
successCriteria[]   // 已有，强化可验证性
tasks[]              // 尽量对齐 causalChain
```

质量门建议：

| 条件 | 门 |
| --- | --- |
| bugfix 且 L2/L3 缺 diagnosis | 禁止标记计划完成 / 弱 DoD 升级为阻断 |
| successCriteria 全是空话（「更好用」） | 创建时警告或拒绝 |
| evidence 与 criteria 无关键字/路径关联 | verifier 弱通过不计完成 |

#### D. 执行与 Verifier 层

复用 ultrathink 设计中的：

- Runner  
- DoD-as-Code  
- stop hooks / completion gate  

增强：

1. **弱 DoD 默认阻断完成**（可配置，Goal/Agent L2+）  
2. evidence 至少一类：测试 | 日志断言 | 生成物检查 | 明确的人工感知确认（且需写清已做自检）  
3. no-progress 时强制回到诊断，而不是同质重试  

#### E. UX / 面板层

1. 展示 planningDepth  
2. 诊断摘要（问题重写 + 根因一句话）  
3. L1 短卡片 vs L2 重面板  
4. 完成态展示「证据如何关闭 criteria」  

#### F. 知识库层（本仓）

| 类型 | 路径约定 |
| --- | --- |
| 总纲 | 本文件 `knowledge/specifications/engineering-rigor-paradigm.md` |
| 模式设计 | `design/product/agent-mode-default-and-adaptive-planning.md` |
| 案例 | `knowledge/experience/<topic>-root-cause.md` |
| ADR | `knowledge/decisions/5x-agent-as-default-mode.md`（实现前） |

案例文模板最少包含：症状 → 问题重写 → 证据 → 根因 → 因果链修复 → 防复发 → 验收。

---

## 七、与任务类型的检查清单（可执行）

### 7.1 症状修复（bug / 糊 / 慢 / 不准）

- [ ] 问题重写  
- [ ] 分层取证记录  
- [ ] 主根因 + 否决的假根因  
- [ ] 因果链任务  
- [ ] 自检证据  
- [ ] 防复发（测试或校验）  

### 7.2 功能建设（feature）

- [ ] 产品边界（是什么/不是什么）  
- [ ] brainstorming / 设计批准（非平凡）  
- [ ] L 深度判定  
- [ ] successCriteria 用户可感知  
- [ ] 实现与测试任务分离  

### 7.3 像素 / 系统图形

- [ ] 平台约束（尺寸、template、@2x、安全边距）  
- [ ] 加载链路（命名、scaleFactor、打包拷贝）  
- [ ] 母版（SVG/脚本）  
- [ ] 深浅色自预览  
- [ ] 再请用户确认  

### 7.4 性能

- [ ] 关键路径定义  
- [ ] 前后对比数据  
- [ ] 避免无证据缓存/并发「优化」  

---

## 八、落地分期（与 Agent 设计对齐）

| 阶段 | 内容 | 主要落点 |
| --- | --- | --- |
| **Doc（已做）** | 范式总纲 + Agent 模式设计 | 本仓 |
| **P0** | Agent 文案与 mode-copy；L0–L3 规则；diagnosis source | `system-context` / UI |
| **P1** | L2 自动建计划；深度元数据；生命周期 | goal-plan-store / gates |
| **P2** | diagnosis 字段；弱 DoD 阻断；evidence 相关性 | plan schema / verifier |
| **P3** | L1 micro-plan UX；面板诊断摘要 | desktop UI |

---

## 九、度量（避免「感觉更严谨了」）

可在实现后观察：

1. 同症状用户连续纠错轮次（目标下降）  
2. 无 evidence 宣称完成次数（目标 → 0 于 L2+）  
3. 僵尸 executing 计划数（不上升）  
4. L0 任务误建正式 plan 比例（目标低）  
5. bugfix 计划含 problemRewrite/根因字段比例（目标高）  

---

## 十、非目标

1. 用冗长 prompt 替代代码闸门  
2. 让所有对话都先写长篇诊断  
3. 规定具体 UI 视觉稿  
4. 在本知识库落可执行代码  

---

## 十一、给实现者的最短口令

> **Agent 默认；按 L 深度规划；症状先诊断；建设先设计；完成靠证据；修改走因果链。**

若只能记住三条：

1. **翻译问题，再动手**  
2. **先管线，后手艺**  
3. **自检关闭，再交给用户**  
