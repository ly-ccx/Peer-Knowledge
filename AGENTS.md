# Peer Knowledge

Peer Agent 开发知识库。与代码仓 `peer_agent` 解耦，专注于架构决策、设计规范、开发经验和运维流程。

## 关联代码仓

- 代码仓名：`peer_agent`（package name: `peer-agent`，Electron + Vite monorepo）
- 本地路径：`/Users/liangyin/Documents/DEV/github/peer_agent`
- 远程仓库：https://github.com/yinLiangDream/Peer-Agent
- 说明：本知识库只存知识，代码改动一律在该代码仓落地。

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
