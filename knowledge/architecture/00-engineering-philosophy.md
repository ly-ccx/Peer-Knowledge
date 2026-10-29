# 工程哲学与设计原则

> 创建时间：2026-06-23  
> 最后更新：2026-08-23  
> 适用范围：所有 Peer Agent 相关项目（peer_agent、xiaoer_design 等）  
> 产品理念：`design/product/peer-product-alignment.md`（本文只锁工程哲学，不另立品类）

## 第一原则：优雅

**优雅是第一原则。** 无论代码架构还是产品交互，都必须追求优雅。

- **代码层**：方案设计优先简洁、一致、克制，拒绝粗糙的凑合实现。能用一个概念解决的不引入两个，能复用的不重复。
- **产品层**：交互体验要自然流畅，视觉表达要清晰有层次。每个细节都值得被认真对待。
- **判断标准**：如果一个方案让你觉得"凑合能用"，那就不够好，继续打磨。

## 架构准则

架构优雅、模块解耦、功能明确、高度抽象、扩展性强、各司其职。

代码要像精密发动机一样，每个模块都有清晰边界和稳定接口。遇到大 service/component/handler/runner/executor 时，优先检查职责拆分、依赖方向、扩展点和请求态隔离，避免继续堆成 god file。

## 能力代理设计原则

```text
模型负责认知。
本地负责能力。
界面负责表达。
契约负责边界。
证据负责治理。
```

- **模型（Model）** 负责认知、规划与工具选择；「模型」指角色而非部署位置，可以是云端 provider，也可以是未来的本地推理 runtime
- **本地（Main Process）** 拥有发现、授权、执行、证据返回
- **界面（Renderer）** 只负责表达和用户交互
- **契约（Protocol）** 定义跨层边界
- **证据（Evidence）** 承载事实问责

## 工作风格

**先读-分析-草案，后执行-调用。** 小步提交，不大范围重写。

1. 读代码 → 理解上下文
2. 输出方案草案 → 等用户确认
3. 再动手实现 → 小步验证

设计讨论阶段只输出方案，不直接修改代码。给用户思考和反馈的时间。

## 模块设计术语

| 术语 | 定义 |
|------|------|
| Module | 有 Interface 和 Implementation 的单元 |
| Interface | 调用者必须知道的一切（类型、不变量、排序、错误、权限、配置） |
| Implementation | Module 内部代码 |
| Depth | 小 Interface 背后的高杠杆 |
| Seam | 行为可替换的位置 |
| Adapter | Seam 上的具体实现 |
| Leverage | 调用者获得的收益 |
| Locality | 变更和调试集中的地方 |

新 Module 必须增加 Locality 或 Leverage。避免浅层透传 wrapper。

## 变更纪律

| 级别 | 范围 | 要求 |
|------|------|------|
| A | 运行时契约、能力暴露、权限、Evidence、System Context、存储边界 | 先写/更新架构文档或 ADR |
| B | Chat Runtime、Tool Runtime、Prompt Assembly、Compaction、Task-Thread 事件模型、IPC | 说明架构影响 |
| C | UI、样式、文案、测试、小修复 | 保持范围；触碰 A/B 边界时升级 |

## Hard Bans

- Renderer 不得使用 `fs`、`child_process`、MCP lifecycle、secret storage
- 不得仅在 Renderer state 中存储权限真值
- 不得绕过 Runtime Projection 暴露模型可见工具
- 不得让 assistant text 替代结构化 Tool Result 或 Evidence
- 不得在应有 protocol object 时添加 ad hoc 跨进程载荷
- 不得让 god module 继续膨胀——在 seam 处拆分

## 非协商运行时链路

所有本地能力必须经过：

```text
Capability Provider → Manifest → Runtime Projection → Tool Call → PermissionGrant → Evidence
```

不允许为 Bash、文件操作、MCP、Plugin、Skill、附件、应用自动化创建独立执行路径。

## Legacy Code 策略

接触遗留代码时：

1. 不扩大违规
2. 在可行时将触及路径推向受治理的 seam
3. 清理太大时，隔离变更，在文档或测试中标明下一个 seam

## 来源声明

本文档综合自：
- `xiaoer_design/CLAUDE.md` — 设计哲学、工作风格
- `xiaoer_design/personal/CODEX_MEMORY.md` — 架构准则
- `peer_agent/AGENTS.md` — 架构治理、Hard Bans、变更纪律、模块术语

三方应保持对齐。如有冲突，以本文档为认知层权威源，`peer_agent/AGENTS.md` 为代码层执行权威源。
# Peer Agent 工程哲学

> 状态：工程原则草案  
> 目的：把 Peer Agent 的工程设计固定在 Xiaoer / Peer Agent 的既有设计哲学上，避免退化成普通 Electron App 或本地 Agent。

---

## 一、核心判断

Peer Agent 的工程哲学不是“客户端越强越好”，而是：

```text
模型负责认知。
本地负责能力。
界面负责表达。
契约负责边界。
证据负责治理。
```

它必须同时满足两件事：

1. 像 Codex 一样提供高质量任务执行界面。
2. 像 Peer Agent 一样保留显式对象、显式账本、显式边界和显式闭环。

所以 Peer Agent 不能被设计成：

- 本地 Agent。
- 本地 CEO Agent Runtime。
- 普通 WebView 聊天壳。
- 本地工具万能入口。
- Plugin / MCP / shell 的拼装平台。

它应该被设计成：

```text
Cloud cognition runtime
  + local capability runtime
  + task-thread interaction harness
```

Codex.app 是 Peer Agent 的客户端产品参考模型，但只参考它的任务型运行态组织方式：

```text
Sidebar 是任务和项目索引。
Task thread 是主工作面。
Composer 是上下文和权限入口。
Tool call / Review / Evidence 是线程事件。
```

Peer Agent 不照搬 Codex.app 的代码执行假设；本地能力必须继续服从 Manifest、Runtime Projection、PermissionGrant 和 Evidence 主链路。

---

## 二、从防御到赋能

现有知识里最重要的工程哲学是：不要把系统设计成一层层补救模型错误，而要消除错误发生的条件。

在 Peer Agent 中，这意味着：

| 防御式设计 | 赋能式设计 |
|---|---|
| 让模型猜本地能做什么 | 用 Manifest 明确声明能力 |
| 让模型搬运大段上下文 | 用 ref、summary、Evidence 和按需展开 |
| 让 UI 弹一个泛化确认框 | 用 Review card 说明 tool、scope、data、duration |
| 出错后靠兜底修复 | 通过 schema、permission、projection 在执行前收敛 |
| 把所有能力暴露给模型 | 通过 Runtime Projection 只暴露本次可用能力 |

原则：

```text
先减少模型犯错的机会，再增加模型做对的能力。
```

---

## 三、Harness 是本机能力层，不是云端薄壳

Peer Agent 不是为某个云端 Agent 做的客户端外壳，也不是企业协作台。它是本机上的任务委托系统：模型负责认知，本地 Harness 负责把委托做成可授权、可证明的工作。

工程目标不是“功能越多越好”，而是提高委托在本机场景里的真实能力上限：

- 渐进上下文：Composer chips、Local Reference、artifact ref，而不是一次性塞全量数据。
- 机械化约束：Manifest、schema、access level、permission gates，而不是靠提示词提醒。
- 闭环验证：Review card、tool result、Evidence summary、audit event，而不是只看最终回复。
- 可观测：每次本地工具调用都能解释、展开、回放。
- 运维治理：插件、MCP、权限、诊断都能被治理，而不是散落在 UI 状态里。

一句话：

```text
Agent 能力 = 模型 + Harness。
Harness 在本机：发现、授权、执行、Evidence。
模型是认知角色，不是部署位置，更不是产品主语。
```

已作废：把 Peer 写成「Cloud CEO / 宙斯员工版的客户端 Harness，不是本地大脑」。桌面持有能力与授权；Electron main 仍然只是组合层，不是把认知塞进 UI。

---

## 四、四种真相不能混

Peer Agent 运行态里有一个关键判断：不同层持有不同真相。

| 真相 | 持有者 | 说明 |
|---|---|---|
| 认知真相 | 模型 / Chat Runtime | 为什么做、做什么、用哪个能力；模型可云可本地 |
| 执行真相 | Local Capability Runtime | 本地是否有能力、是否授权、执行结果是什么 |
| 放权真相 | PermissionGrant（本地；组织策略是远期） | 当前用户、任务、scope 是否允许 |
| 交互真相 | 任务线程 | 用户看到的过程、确认、结果、证据 |

禁止把这些真相混成一个黑盒：

- UI 不能成为权限事实源。
- Plugin 不能成为治理事实源。
- MCP 不能成为权限模型。
- 本地个人经验不能自动升格为系统指令或共享认知。
- 模型不能假装直接拥有用户机器。

---

## 五、运行链和进化链分离

Peer Agent 允许个人经验参与本次任务，但不能把个人经验自动变成系统指令、共享本体或云端 Patch。

正确链路是：

```text
Local Personal Memory
  → user-approved auxiliary context
    → Runtime Projection
      → 模型 / Chat Runtime
```

错误链路是：

```text
Local Personal Memory
  → 自动 Patch / 系统 prompt
    → 共享认知本体
```

除非未来有显式提交、审核和治理流程，否则个人经验默认只留在本地。

---

## 六、契约先于 SDK

SDK 是契约的包装层，不是安全模型本身。

工程顺序必须是：

```text
Protocol contracts
  → minimal local capability loop
    → SDK wrapper
      → Plugin / MCP ecosystem
```

第一批必须先稳定的对象：

- `CapabilityManifest`
- `RuntimeProjection`
- `ClientToolCall`
- `ClientToolResult`
- `PermissionGrant`
- `Evidence`
- `AuditEvent`
- `LocalAccessLevel`

如果这些对象不稳定，SDK 越早做，越容易固化错误边界。

---

## 七、界面是运行态，不是装饰层

Peer Agent 的 UI 不是简单展示层。它是 Agent 运行态的一部分。

UI 需要承载：

- 用户任务意图。
- 当前上下文选择。
- 本地访问级别。
- Review card。
- Tool call card。
- Evidence summary。
- 产物附件。
- 错误和降级状态。
- 中英文语义切换。

Codex-like 的意义不在于视觉相似，而在于交互结构相似：

```text
Sidebar 是任务/项目索引。
Task thread 是运行态主界面。
Composer 是本地访问与上下文控制面。
Review card 是权限与执行的阻塞点。
Evidence 是治理和解释的入口。
```

i18n 也属于运行态：

```text
locale 来自 ClientSession。
用户表达跟随 locale。
协议对象名保持稳定。
Evidence 记录生成语言。
```

不要把中英文切换做成组件内部零散文案；语言边界应该和 Manifest、Tool Call、Evidence 一起进入契约。

---

## 八、第一阶段工程纪律

第一阶段只做能证明主链路成立的最小系统。

应该做：

- Electron Shell。
- React / TypeScript task thread。
- Composer local access level。
- Protocol types。
- Local health capability。
- Review card。
- Evidence summary。

暂缓做：

- 完整 Plugin 市场。
- 复杂 MCP 管理。
- 任意 shell 命令。
- 文件写入。
- 浏览器自动化。
- 本地个人经验自动回云。
- 完整 SDK。

第一阶段的验收问题是：

```text
用户能否在一个任务线程里看到：
目标如何被签收、
本地能力是否被授权、
执行结果是什么、
什么 Evidence 用来关闭完成。
```

如果不能，工程还没有进入正确轨道。


2026-10-28：后续双向监督与连续工作设计见[架构说明](25-duplex-supervision-and-continuity.md)。本批源码、自测范围与限制见[实施回执](../../playbook/v0.1.0/code-structure-refactoring.md)；不将本次新增能力计入历史版本。
