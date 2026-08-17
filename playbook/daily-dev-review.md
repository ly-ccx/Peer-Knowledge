# 每日开发进度回顾

创建时间：2026-08-05
最后更新：2026-08-17

> 用途：按固定流程回顾「昨天」在 `peer_agent` 与 `peer-knowledge` 的开发进度，产出一页可扫读的进度摘要。
> 适用场景：晨会前自检、跨日续作、给 Agent 下达「回顾昨天进度」时复用同一格式。

## 一、覆盖范围

| 仓库 | 本机根目录 | 回顾内容 |
|---|---|---|
| `peer_agent` | 按 `AGENTS.md` 解析为 `$PEER_AGENT_ROOT` | 产品代码、测试、发版脚本、用户文档站、release notes 等可执行/可交付改动 |
| `peer-knowledge` | 按 `AGENTS.md` 解析为 `$PEER_KNOWLEDGE_ROOT` | 架构决策、设计文档、规范、Playbook、经验记录等知识改动 |

原则：

- **双仓一起看**，避免只看代码仓漏掉决策/SOP，或只看知识库漏掉实现进度。
- 回顾默认基于 **git 已提交历史**；未提交改动单独标为「工作树脏状态」，不当成已完成进度。
- 本文件是人工/Agent 可执行的 Playbook；不替代代码仓中的测试与 CI。

## 二、时间窗口

默认回顾 **本地时区「昨天」自然日**：

| 概念 | 定义 |
|---|---|
| 回顾日 `REVIEW_DATE` | 昨天的日期，格式 `YYYY-MM-DD` |
| 起始 | `REVIEW_DATE 00:00:00`（本地时区） |
| 结束 | 今天 `00:00:00`（本地时区，不含今天） |

若昨天无提交（周末/请假），可按需扩展为「上一个有提交的工作日」到今天 00:00，并在输出中写明实际窗口。

## 三、信息来源（事实源）

按优先级使用，避免凭记忆编造：

| 信息 | 事实源 | 命令/位置 |
|---|---|---|
| 昨天提交列表 | 各仓 `git log` | 见第四节 |
| 改动文件与体量 | 各仓 `git log --stat` / `git diff --stat` | 见第四节 |
| 分支与是否落后远端 | `git status -sb`、`git rev-parse --abbrev-ref HEAD` | 各仓根目录 |
| 未提交改动 | `git status --short`、`git diff --stat` | 仅作「进行中」，不计入已完成 |
| 主题归类线索 | commit message、路径前缀（`apps/`、`packages/`、`knowledge/`、`design/`、`playbook/`） | 人工/Agent 归纳 |
| 关联决策/设计 | `peer-knowledge` 中同日新增或修改的 md | 与代码提交对照 |

禁止：

- 把未 push 的本地提交说成「已上线」
- 把 knowledge 文档草稿说成「代码已合入」
- 在无 git 证据时填写「完成了 XX」

## 四、操作步骤

以下在 shell 中执行；`REVIEW_DATE` 换成昨天日期（例：`2026-08-04`）。

### 4.1 计算昨天日期（可选）

```bash
# macOS
REVIEW_DATE=$(date -v-1d +%Y-%m-%d)
# Linux
# REVIEW_DATE=$(date -d yesterday +%Y-%m-%d)
echo "REVIEW_DATE=$REVIEW_DATE"
```

先按 `AGENTS.md` 解析出两个根目录，再执行后面的命令。不要把解析结果写回本仓库。

```bash
# 若未导出环境变量：用同级目录或 .peer-workspace.local.json
: "${PEER_AGENT_ROOT:?set PEER_AGENT_ROOT or resolve the code repo first}"
: "${PEER_KNOWLEDGE_ROOT:?set PEER_KNOWLEDGE_ROOT or resolve the knowledge repo first}"
```

### 4.2 回顾 peer_agent

```bash
cd "$PEER_AGENT_ROOT"

echo "=== peer_agent branch ==="
git rev-parse --abbrev-ref HEAD
git status -sb

echo "=== peer_agent commits on $REVIEW_DATE ==="
git log --since="${REVIEW_DATE} 00:00:00" --until="${REVIEW_DATE} 23:59:59" \
  --pretty=format:'%h %ad %an %s' --date=format:'%H:%M' --no-merges

echo "=== peer_agent stat ==="
git log --since="${REVIEW_DATE} 00:00:00" --until="${REVIEW_DATE} 23:59:59" \
  --pretty=format:'--- %h %s' --stat --no-merges

echo "=== peer_agent dirty tree (optional) ==="
git status --short
git diff --stat
```

### 4.3 回顾 peer-knowledge

```bash
cd "$PEER_KNOWLEDGE_ROOT"

echo "=== peer-knowledge branch ==="
git rev-parse --abbrev-ref HEAD
git status -sb

echo "=== peer-knowledge commits on $REVIEW_DATE ==="
git log --since="${REVIEW_DATE} 00:00:00" --until="${REVIEW_DATE} 23:59:59" \
  --pretty=format:'%h %ad %an %s' --date=format:'%H:%M' --no-merges

echo "=== peer-knowledge stat ==="
git log --since="${REVIEW_DATE} 00:00:00" --until="${REVIEW_DATE} 23:59:59" \
  --pretty=format:'--- %h %s' --stat --no-merges

echo "=== peer-knowledge dirty tree (optional) ==="
git status --short
git diff --stat
```

### 4.4 归纳与填模板

1. 各仓提交数、主要路径、是否跨仓联动（例如代码实现 + ADR/Playbook 同步）。
2. 用业务语言写「昨天完成了什么」，每条尽量对应至少一条 commit 或明确文件路径。
3. 标出风险、未完成项、今日建议优先级。
4. 将结果填入下方 **输出模板**（可直接粘贴到对话或日记）。

### 4.5 Agent 快捷触发语

可对 Agent 说：

```text
按 playbook/daily-dev-review.md 回顾昨天开发进度（peer_agent + peer-knowledge）。
```

Agent 应：跑第四节命令 → 只基于工具输出归纳 → 按「输出模板」回复。

## 输出模板

复制以下块填写（无内容写 `无`，不要删节标题）：

```markdown
# 昨日开发进度回顾（{REVIEW_DATE}）

生成时间：{今天 YYYY-MM-DD HH:mm}
时间窗口：{REVIEW_DATE} 00:00 – 次日 00:00（本地）
覆盖仓库：peer_agent + peer-knowledge

## 一句话摘要
- {1–3 句：昨天主线是什么、有无双仓联动}

## peer_agent
- 分支：{branch}｜提交数：{n}
- 完成事项：
  - {事项}（依据：{short hash 或路径}）
- 主要改动范围：
  - {目录/模块}：{简述}
- 测试/构建（若有证据）：{通过 / 未跑 / 失败摘要}
- 未提交/进行中：{无 或 简述}

## peer-knowledge
- 分支：{branch}｜提交数：{n}
- 完成事项：
  - {事项}（依据：{short hash 或路径}）
- 主要改动范围：
  - knowledge/ | design/ | playbook/ ：{简述}
- 未提交/进行中：{无 或 简述}

## 风险与阻塞
- {无 或 列表：技术债、失败测试、待决策、依赖外部}

## 今日建议
1. {最高优先级}
2. {次优先}
3. {可选}

## 备注
- {窗口是否扩展到上一个工作日、仅本地未 push 等}
```

## 六、归纳规则（质量门槛）

| 规则 | 说明 |
|---|---|
| 证据优先 | 每条「完成事项」尽量带 commit hash 或文件路径 |
| 分仓陈述 | `peer_agent` 与 `peer-knowledge` 分节，避免混写 |
| 区分状态 | 已提交 / 仅本地 / 工作区未提交 三者分开 |
| 空窗诚实 | 某仓昨天 0 提交时写「无提交」，可附带脏工作树说明 |
| 联动点名 | 若同日既有实现又有 ADR/设计/Playbook，在摘要中点明联动 |
| 不做发版结论 | 除非有 tag/CI 证据，不写「已发布」 |

## 七、可选：一键双仓摘要脚本思路

不要求入库脚本；需要时可在临时 shell 中串行执行 4.2 + 4.3。若日后沉淀为 `peer_agent` 工作空间 Skill，应放在代码仓 `skills/`，本 Playbook 只保留人工步骤与输出模板。

## 八、Definition of Done（单次回顾）

- [ ] 已对 `peer_agent` 与 `peer-knowledge` 分别拉取昨天 `git log`（或确认 0 提交）
- [ ] 输出使用本文「输出模板」结构
- [ ] 完成事项有 commit/路径依据
- [ ] 风险与今日建议已填写（可为「无」）
- [ ] 未把未提交改动记成已完成

## 九、关联资料

- `AGENTS.md`（双仓职责与目录约定）
- `playbook/release-process.md`（发版 SOP；日回顾不替代发版检查）
- 代码仓：`https://github.com/ly-ccx/Peer-Agent`（本机根目录按 `AGENTS.md` 解析）
- 知识库：`https://github.com/ly-ccx/Peer-Knowledge`（本机根目录按 `AGENTS.md` 解析）
- 入口纪律：`playbook/change-intake.md`
