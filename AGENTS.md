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
