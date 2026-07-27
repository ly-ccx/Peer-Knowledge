# 本地 Skill 范围与工作空间挂载

创建时间：2026-07-27
最后更新：2026-07-27

> 状态：已采纳
> 适用范围：Peer Agent Desktop、TUI 与本地 Skill Store

## 背景

Peer Agent 的 Skill 既可能是跨项目复用的个人能力，也可能绑定某个代码仓的文件、命令和发布流程。如果只使用一份用户级 Skill 列表，会产生两个问题：

1. 项目专用 Skill 会出现在无关项目中，Agent 可能在错误目录执行命令。
2. UI 无法解释一个 Skill 是“安装在用户目录”还是“随当前项目提供”。

因此，Skill 的**包体来源**与**当前工作空间是否挂载**必须分开建模。

## 决策

本地 Skill 分为两种范围：

| 范围 | 规范目录 | 含义 |
|---|---|---|
| 全局 Skill | `~/.peer-agent/skills/<skill-id>/SKILL.md` | 安装在用户目录，可被任意工作空间挂载 |
| 工作空间 Skill | `<workspace>/skills/<skill-id>/SKILL.md` | 随项目版本控制，只在该工作空间中发现和使用 |

外部公共 Skill 仓（例如 `~/.agents/skills`）只是“可借用来源”，不等于已经安装。借用后进入用户级全局目录。

### 挂载状态

- Skill 包体的存在表示“已安装或已由项目提供”。
- `enabled` 表示该 Skill 是否挂载到**当前活动工作空间**。
- 同一个全局 Skill 在工作空间 A 和 B 中可以有不同的挂载状态。
- 会话运行时只注入当前活动工作空间中已挂载的 Skill。
- Desktop 和 TUI 必须使用相同的工作空间路径和挂载状态。

### 同名覆盖

如果全局目录和当前工作空间都存在相同 `skillId`：

1. 当前工作空间版本优先。
2. 列表中只展示一个有效版本。
3. 运行时只注入工作空间版本，防止重复指令和来源歧义。

## 放置判断

创建 Skill 前按以下顺序判断：

### 应放到工作空间

满足任一条件时，优先放到 `<workspace>/skills/`：

- 引用了该项目专有的脚本、目录或配置。
- 依赖该项目的分支、版本、发布或测试约定。
- 离开该项目后，指令大部分不成立或有误操作风险。
- Skill 应随代码评审、分支和版本一起演进。

### 应放到全局

只有在以下条件基本成立时才放到 `~/.peer-agent/skills/`：

- 不依赖某一个仓库的目录结构。
- 可安全用于多个项目。
- 输入、输出和验证方式具有通用性。
- 即使在未知项目中出现，也不会诱导 Agent 执行项目专有命令。

### 不应放 Skill 的内容

长期知识、设计背景、事故记录和人工 SOP 应进入知识库，而不是塞入执行型 Skill：

- 架构与规范：`peer-knowledge/knowledge/`
- 人工操作手册：`peer-knowledge/playbook/`
- 项目执行 Skill：关联代码仓 `<workspace>/skills/`

## `release-process` 的归属

Peer Agent 的 `release-process` 是项目级 Skill，规范位置为：

```text
/Users/liangyin/Documents/DEV/github/peer_agent/skills/release-process/SKILL.md
```

理由：它直接依赖 Peer Agent 代码仓中的：

- `VERSION`
- `scripts/stamp-version.mjs`
- `scripts/check-version.mjs`
- `.github/workflows/release.yml`
- `release-notes/`
- `CHANGELOG.md`
- `docs/`
- Desktop、CLI 与 Runtime workspace package

它不应软链接到 `~/.peer-agent/skills/release-process`，否则其他项目会把它误认为全局能力。

与之对应的人类可读发布知识放在：

```text
peer-knowledge/playbook/release-process.md
```

两者职责不同：

| 载体 | 职责 |
|---|---|
| `peer_agent/skills/release-process/SKILL.md` | 指导 Agent 在代码仓内执行、验证和留证 |
| `peer-knowledge/playbook/release-process.md` | 解释发布原则、职责边界、人工检查和故障处理 |

## UI 要求

Skills 页面必须明确展示：

1. 当前活动工作空间及其绝对路径。
2. “工作空间”和“全局”两个分区。
3. 工作空间无 Skill 时仍显示空状态，不得隐藏整个分区。
4. 点击 Skill 可查看名称、范围、来源路径、`whenToUse` 和完整正文。
5. 开关表达“挂载到当前工作空间”，不能误导为全局启停。

因此，当活动工作空间是 `peer-knowledge` 时，看不到 `peer_agent` 的 `release-process` 是正确行为；切换到 `peer_agent` 后，它才应出现在工作空间分区。

## 非目标

本决策不要求：

- 自动扫描任意关联仓库的 Skill。
- 把知识库与代码仓合并成一个工作空间。
- 将工作空间 Skill 自动复制到用户全局目录。
- 允许一个工作空间读取另一个工作空间的项目级 Skill。

## 验收标准

- 全局与工作空间 Skill 在数据模型和 UI 中可区分。
- 工作空间切换后列表和挂载状态同步刷新。
- 项目级 Skill 不出现在无关工作空间。
- 同名 Skill 由当前工作空间版本覆盖全局版本。
- 运行时只注入当前工作空间已挂载的有效 Skill。

## 关联资料

- `knowledge/decisions/15-plugin-skill-mcp-system.md`
- `knowledge/decisions/16-skill-call-lifecycle.md`
- `playbook/release-process.md`
- 关联代码仓：`/Users/liangyin/Documents/DEV/github/peer_agent`
