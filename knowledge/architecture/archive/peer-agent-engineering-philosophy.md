# Peer Agent 工程哲学历史说明

创建时间：2026-11-14
最后更新：2026-11-14
状态：历史参考，不再维护为通用工程规范

本文保留原工程哲学中的项目说明，供历史决策溯源。跨项目工程原则唯一正文见 [Coding Agent 工程总纲](../00-engineering-philosophy.md)；当前项目边界以 [架构治理基线](../20-architecture-governance.md) 和有效 ADR 为准。以下为原项目说明，不代表当前能力或发布验收。


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
