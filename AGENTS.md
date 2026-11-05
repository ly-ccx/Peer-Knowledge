# Peer Knowledge

Peer Agent 开发知识库。与代码仓 `peer_agent` 解耦，专注于架构决策、设计规范、开发经验和运维流程。

## 关联代码仓

- 代码仓名：`peer_agent`（package name: `peer-agent`，Electron + Vite monorepo）
- 远程仓库：https://github.com/ly-ccx/Peer-Agent
- 本地目录别名：`Peer-Agent`、`peer_agent`、`peer-agent`
- 说明：本知识库只存知识，代码改动一律在该代码仓落地。

不要把本机绝对路径写进本仓库。历史文档里出现的 `/Users/...` 只是撰写时的现场记录，不是克隆约定。

## 本机路径解析

按以下顺序解析代码仓根目录，解析到就停止：

1. 环境变量 `PEER_AGENT_ROOT`（目录必须存在）
2. 本仓根目录的 gitignored 文件 `.peer-workspace.local.json`（字段 `peerAgentRoot`）
3. 与本仓同级、且目录名匹配代码仓别名的目录
4. 当前多根工作区里已经打开的代码仓文件夹

知识仓自身可用 `PEER_KNOWLEDGE_ROOT`、`.peer-workspace.local.json` 的 `peerKnowledgeRoot`、或别名 `Peer-Knowledge` / `peer-knowledge` 做对称解析。

解析失败就询问，不要编造家目录路径，也不要把解析结果提交进 Git。

## 工作入口

日常入口是代码仓，不是本仓。Cursor / Agent 默认以 `Peer-Agent` 为第一工作区根；本仓按需挂在旁边。

| 级别 | 先做什么 | 改动落在哪 |
|---|---|---|
| C | 直接改代码 | 代码仓 |
| B | 在代码仓改，并说明架构影响；边界真变了再回写本仓 | 代码为主，知识为辅 |
| A | 先在本仓更新架构文档或 ADR，评审后再实现 | 先知识，后代码 |

从本仓发起会话，不等于向本仓交付。可执行改动仍提交到代码仓。

## Git 同步

本地一旦 commit，必须在同一轮立刻 push 到当前跟踪的远程分支。多设备以 `origin` 为准；不要把提交只留在本机。

更短的入口说明见 `playbook/change-intake.md`。
项目代理落地进入 0.1.0 大版本（ADR 80–85）：版本计划见 `design/product/v0.1.0-release-plan.md`，执行约定见 `playbook/project-agent-implementation-handbook.md`，任务卡见 `playbook/v0.1.0/`；任何模型接手相关任务前必须先读。
产品理念与价值对齐见 `design/product/peer-product-alignment.md`（产品链路唯一对齐方向）。

## 产品体验规范（2026-10-23 起生效）

后续所有 Peer 产品设计与实现必须依据自己的规范。涉及视觉、组件、文案、输入、焦点、滚动、状态反馈或动画时，先读相关章节：

- `knowledge/specifications/peer-product-experience-standard.md`：Frost 视觉、组件与规范优先级。
- `knowledge/specifications/peer-human-agent-interaction-contract.md`：输入、行动权、授权、结果、恢复与用户控制。
- `knowledge/specifications/motion-system.md`：集中动效、语义选型、可中断与减少动效。
- `knowledge/specifications/transition-system.md`：页面、层级、对象切换时的输入、焦点、阅读位置与恢复连续性。
- `playbook/product-experience-development.md`：需求、实现、内容/diff 审阅与发布验收。

产品北极星和架构治理分别保留其权威。上述规范取代旧设计文件中相冲突的体验条款；历史 Demo 与 `design/product/open-claude-ui-study.md` 是参考依据，不是第二套规范。新文档不得另立配色、交互状态机或动画体系。

硬约束：意图有回执、行动有归属、执行有边界、结果有依据、中断可恢复、注意力归用户。复用 Frost/`--ui-*`、共享 SVG 与动效/焦点/滚动 seam；不能以点击、timer、动画或助手文本冒充权限、执行成功或 Evidence。

开发共识（2026-11-03）适用于全部后续修改，详见 [工程哲学与开发共识](knowledge/architecture/00-engineering-philosophy.md)：实现者承担验证与已有状态恢复责任，用户不承担试错验收。代码改动须自动执行与范围相称的定向验证，相关失败必须定位、修正并保留记录；完整发布门禁仍针对最终组合候选。纯文档/指令改动只做内容、差异与一致性审阅。本条取代 2026-10-22 的日常不自动验证约定，以代码仓 AGENTS 的最新 Engineering Delivery Consensus / Validation Scope / Release Gate 为执行准则。不得把候选补丁、PR 或 CI 通过单独称为原任务已恢复。

全产品存量登记见 `design/product/peer-interaction-standardization-matrix.md` 与 `design/product/peer-ui-motion-transition-matrix.md`；具体排程见 `design/product/peer-product-renovation-plan.md`。新增或改变页面、组件与状态时，同步对应矩阵和改造任务；静态已存在不等于候选验收已通过。

规范定义应有行为，不表示存量已全部实现。知识只沉淀在本仓，运行时实现仍落代码仓；新增权限、Evidence、协议、System Context 或存储边界仍按 A/B 分级治理。

## 其他产品与交付入口

当前改造总纲见 `design/product/peer-transformation-charter.md`（任务壳 + 工作台雷达；阶段 A–E 已交付；阶段 F 项目代理壳 Proposed，见 ADR 80；记忆体系见 ADR 81；项目目标与定时 / 事件驱动见 ADR 82；模型分工见 ADR 83；机器人列表壳见 ADR 84；宿主、输入与多入口见 ADR 85）。
活的产品路线图（近/中/远景）见 `design/product/peer-product-roadmap.md`。
CLI 无头/脚本缺口见 `design/product/cli-scripting-and-headless-gap.md`。
P0 `peer exec` 契约见 `knowledge/decisions/65-cli-headless-exec.md`。

## 目录结构

```
peer-knowledge/
├── knowledge/
│   ├── architecture/     # 架构设计文档（从 peer_agent/docs/architecture/ 迁移）
│   ├── specifications/   # 编码规范、Prompt 规范、设计语言规范
│   ├── experience/       # 踩坑记录、调试经验、性能优化心得
│   └── decisions/        # ADR（架构决策记录）
├── design/
│   ├── product/          # 产品设计、交互设计、功能规划
│   └── visual/           # Peer Frost 设计语言、Token 文档、视觉资产
├── playbook/             # 发版流程、运维 SOP、应急预案
└── AGENTS.md             # 本文件
```

## 使用原则

- 本仓库只存放**知识**，不存放可执行代码
- 代码仓的 `AGENTS.md` 关注工程治理（怎么写代码）；本仓库关注认知治理（为什么这么设计）
- 文档命名使用 kebab-case，按主题而非时间组织
- 每篇文档开头标注 `创建时间` 和 `最后更新`，便于判断时效性
