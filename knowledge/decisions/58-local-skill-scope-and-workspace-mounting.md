# 本地 Skill 范围与工作空间挂载

创建时间：2026-07-27
最后更新：2026-11-27（统一 Bot 模式下的技能安装目标，补充多选批量安装与逐目标回执）

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

## 2026-11-27 修订：Bot 模式下的技能安装目标与批量安装

**状态：Accepted。** 项目主人于 2026-11-27 确认本次 A 级修订。代码落地与发布验收分别核实并独立记录。

RC 45 现场取证发现，技能市场（「技能发现·Find Skills」中的 SkillHub 与 Qoder）在「安装位置 → 机器人」只列出 `SillyTavern`，漏掉原生创建的活跃机器人 `peer-dev`。候选列表、主进程 `skill-install-target.mjs` 的安装准入和「已安装」视图均依赖经典 `settings.workspaces`。原生 Bot 的档案及绑定由项目存储记录。

本节补充上文「UI 要求」在 Bot 模式下的适用方式，并取代技能市场架构在 Bot 模式下的单目标和路径必填条款。技能包体范围、挂载和同名覆盖沿用本文原决策。[技能市场架构的「工作区安装目标」](../architecture/peer-skill-marketplace.md#工作区安装目标)

技能管理沿用机器人设置入口。Electron 主进程负责当前 Desktop 安装入口的准入校验。迁移到统一 Rust Core 时，由 Core 承接同一目标资格与写入准入契约，Desktop 消费其投影。[ADR 84](84-bot-list-shell.md)、[ADR 133](133-unified-rust-core-and-dual-host-architecture.md)

### 目标资格的单一真源

- **Bot 目标由活跃档案与当前有效绑定取交集。** 以稳定 `workspaceId` 关联 `projects/<workspaceId>/profile.json` 和本机 `projects/registry.json`。档案须满足 `status == "active"`，注册表须有该 ID 的当前绑定，且绑定路径可解析为现存可用的真实目录。历史路径仅用于识别旧记录，禁止用作写入目标。[ADR 85](85-project-agent-hosts-inputs-and-surfaces.md)
- **兼容经典工作区。** 统一集合同时纳入 `settings.workspaces` 中仍有效且已添加的经典工作区。按 `workspaceId` 或规范化后的真实路径去重，重叠时保留活跃 Bot 的身份、显示信息及当前绑定。经典模式的既有工作区安装入口继续可用。
- **失效的目标拒绝写入。** 归档或停用的 Bot、已解绑记录、目录失效的绑定均不具备写入资格。对应的经典残留条目也不得恢复其资格。界面可展示这些条目及不可用原因，且须禁用选择和安装。

### 三处消费同一目标集合

1. **市场候选。** SkillHub 与 Qoder 共用宿主投影的目标集合。渲染层提交用户选定的目标，授权由主进程判定。
2. **安装准入。** 主进程优先用 `workspaceId` 从权威集合解析目标，写入前重新核对当前资格、规范化真实路径和目录可用性。旧请求仅携带 `workspacePath` 时，须将该路径规范化并匹配同一集合中的当前有效目标。同时携带 ID 和路径时，两者须指向同一目标。失效、查无匹配或不一致时拒绝该目标，禁止绕过准入或回退写入其他位置。
3. **已安装视图。** 「已安装」使用同一集合定位目标工作区，并根据 Skill Store 的实际内容展示。成功写入后刷新相应目标的安装状态。查看或安装至其他目标均无需改变当前活动工作区。

### 多选批量安装与逐目标回执

1. **明确选择。** 用户可在「安装位置 → 机器人」勾选一个或多个合法目标，再显式提交一次安装。请求只覆盖此次选中的目标和同一市场技能版本。用现有选择控件表达选中、不可用和提交中状态。至少选中一个合法目标才可提交，提交中防止重复触发。[Peer 产品体验规范](../specifications/peer-product-experience-standard.md)
2. **同一批次只下载、验证一次。** 复用市场来源的包验证链。SkillHub 的指定版本 ZIP 仅下载一次，平台 Ed25519 签名、ZIP MD5 与 v1 内容哈希各校验一次。其他市场包沿用其来源的校验规则。任一必需校验失败时整体中止并反馈原因，所有目标均不得落盘。[SkillHub 签名安装契约](../architecture/skillhub-marketplace-source.md#signed-installation)
3. **校验通过后逐目标独立写入。** 主进程沿同一规则去重并逐一复核所选目标，再由现有 Skill Store 将技能写入通过准入的各目标的 `<workspace>/skills/`。单个目标失效或写入失败时，其他合格目标仍可继续，已成功落盘的目标保留。批次内禁止写入未选中的机器人或全局 `skills/` 目录。
4. **逐目标报告实际结果。** 回执按目标身份返回结构化的成功或失败结果，失败须携带原因。共用的包校验失败时，所选目标均回执失败并标明共用原因。部分失败时，发起安装的界面分别展示成功清单与失败清单及原因。只有全部所选目标写入成功时才显示全部成功。

### 后续实施验收

- 在 SkillHub 和 Qoder 验证原生创建且已绑定的活跃 Bot 能被选择、能通过主进程校验，且安装成功后能在「已安装」中看到。覆盖经典有效工作区、重复 ID 或路径、旧 `workspacePath` 请求以及 ID 与路径不一致。
- 验证归档、停用、解绑、目录失效和任意未登记路径均被拒绝，覆盖经典残留条目和选中后、落盘前失效的情形。
- 验证多选仅下载和校验同一包一次。覆盖包验签或完整性失败时零落盘、逐目标写入部分失败的真实回执，以及未选中目标和全局目录零写入。
