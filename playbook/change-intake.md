# 变更入口

创建时间：2026-08-17
最后更新：2026-08-17

> 用途：决定一条需求从哪开、先写哪、交到哪。
> 适用场景：新开 Agent 会话、跨机开发、判断要不要先改知识仓。

## 一、默认入口

日常从代码仓开始。`Peer-Agent` 的 `AGENTS.md` 已经关联本知识库；需要读治理合同时按该文件的解析规则打开本仓，不必把会话开在知识仓。

推荐工作区：代码仓为第一根，知识仓按需并列。不要把本机绝对路径写进任一仓库。

## 二、先分级，再动手

| 级别 | 判断 | 入口 | 提交 |
|---|---|---|---|
| C | UI、文案、样式、测试、小修复；未碰能力、权限、Evidence、协议、prompt 边界 | 代码仓，直接改 | 只交代码仓 |
| B | Chat / Tool Runtime、Prompt 组装、compaction、task-thread、IPC | 代码仓开工，回复里说明架构影响 | 代码仓；边界变了再回写本仓 |
| A | 运行时契约、能力暴露、权限、Evidence、System Context 顺序、存储边界 | 先在本仓更新架构文档或 ADR，评审后再改代码 | 知识仓先于或并行于代码仓 |

C 级升 A/B 的条件：改着改着碰到了能力执行、权限真值、Evidence、协议对象或 prompt 边界。

## 三、三件不要绑在一起

| 角色 | 含义 | 由什么决定 |
|---|---|---|
| 入口 | 会话默认开在哪 | 上表：日常代码仓，A 级先知识仓 |
| 执行 | 工具读写哪 | 本机解析出的仓库根，或 Goal 的 origin/target |
| 交付 | git 提交进哪 | 改动归属：代码进代码仓，决策进知识仓 |

从知识仓发起 ≠ 向知识仓交付。

## 四、本机根目录

不要在 Playbook 或 `AGENTS.md` 里写 `/Users/...`。按 `AGENTS.md` 解析：

1. `PEER_AGENT_ROOT` / `PEER_KNOWLEDGE_ROOT`
2. 各仓根目录的 `.peer-workspace.local.json`（不提交）
3. 同级目录别名
4. 已打开的多根工作区

可选本地文件示例见 `.peer-workspace.local.example.json`。复制为 `.peer-workspace.local.json` 后按本机填写。

## 五、Agent 快捷判断

可对 Agent 说：

```text
按 playbook/change-intake.md 给这条需求分级，并决定从哪开、写到哪、交到哪。
```

Agent 应先给出 A/B/C 和入口，再开始改文件。
