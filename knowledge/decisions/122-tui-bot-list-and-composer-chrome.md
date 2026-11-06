# ADR 122：TUI 机器人列表与输入条呈现

创建时间：2026-11-06
最后更新：2026-11-06

状态：Accepted（2026-11-06。页头 Accepted 只表示本决定已被接受，不表示实现已经发布验收）

级别：C。只定当前机器人 TUI 壳上的列表行和输入条怎么画。不改卡片编号、权限、输入恢复存储，不新增能力、Evidence、协议或 System Context。

关联：

- `knowledge/decisions/84-bot-list-shell.md` — 桌面机器人列表壳。本文不改它的行：头像、未读、档案仍按那篇
- `knowledge/decisions/85-project-agent-hosts-inputs-and-surfaces.md` — 决策 9 的 TUI 入口不变：已绑定目录里运行 `peer` 打开该机器人；`peer bots` 与 `/bots` 列出机器人；租约仍决定宿主或客户端
- `knowledge/decisions/80-project-agent-delegation-model.md` — `peer --classic` 仍保留直接任务
- `knowledge/decisions/109-resource-reference-preview-and-artifact-collaboration.md` — 输入恢复记录的版本与限额不动
- `knowledge/decisions/115-input-prediction-and-draft-boundary.md` — 未发送草稿的存储与预测边界不动
- `knowledge/decisions/74-deployment-surfaces-and-local-storage.md` — 内网 Gateway 与设备配对仍是后置顺序。本文不写那份契约
- `knowledge/specifications/peer-product-experience-standard.md`、`knowledge/specifications/peer-human-agent-interaction-contract.md` — 呈现仍服从既有规范，本文不另立配色或状态机

核对过的代码是 Peer-Agent [PR #283](https://github.com/ly-ccx/Peer-Agent/pull/283) 的 head `0430bd196bb5850a7d37ecc87c756d7affaf3b99`（分支 `PeerAgent/tui-bot-composer`，基线 `PeerAgent/dev/0.1.0`）。

---

## 背景

当前机器人 TUI 已经能列出机器人，并在对话里输入。列表行用整行底色表示选中，名字、计数、预览和时间挤在一起。顶栏常驻印着 `F2 · 普通任务模式`，输入条下面还有两行提示。草稿恢复失败时，输入条会因为恢复状态未就绪而拒绝键入。边框盒子还会缩到占位文字的宽度。

这些都发生在已经存在的机器人壳上。桌面列表、卡片编号、权限和输入恢复存储都不在这次范围里。

## 决策

### 1. 列表行

每一行是：名字、一段短时间、待处理计数、进行中计数，以及一行截断的预览。

| 位置 | 取什么 |
|---|---|
| 名字 | 现有显示名。超宽则按行宽截断，末尾用省略号 |
| 短时间 | 现有最后活动时刻。能认出的按字符串里的月、日、时、分收成 `MM-DD HH:mm`（例如 `2026-11-05T12:36:10.000Z` 显示为 `11-05 12:36`），不另做时区换算；认不出的截短后留下，不换行 |
| 待处理 | 现有 `needsYou`。中文文案仍是「待处理」，英文仍是 Needs you |
| 进行中 | 现有 `running` |
| 预览 | 现有最后一条预览，单独一行，按行宽截断。时间不跟预览挤在同一行 |

选中沿用现有插入符（caret），不用整行高亮。空列表仍用原来的空状态文案。上下键选择、回车打开、Esc 返回，仍是原来的列表操作。

### 2. 不再常驻印出模式标签和输入区提示

去掉常驻的 `F2 · 普通任务模式`，以及输入条下面的两行提示。

`/classic`、`/help`、`/cards` 仍然可用。F2 仍然切换到普通任务模式，但屏幕上不再印出 F2。`/help` 仍列出这些命令，正文不再以 F2 开头。

顶栏不再追加「机器人模式」。列表页标题是 Peer；打开某个机器人后，标题是 Peer · 名字。列表页不印宿主或客户端那一行。

### 3. 草稿恢复失败时输入条仍可编辑

草稿恢复失败时，输入条保持可编辑。草稿警告不得挡住打字，也不得挡住 `/save-draft`。

恢复状态尚未就绪，不再作为拒绝聚焦、插入文字或回车的理由。警告仍由原来的恢复状态行显示。忙碌和卡片焦点仍按原路径让出输入。

### 4. 通栏分隔线与通栏输入

输入区画一条通栏分隔线，下面是一条通栏输入。不再用会缩到占位文字宽度的边框盒子。

## 明确不做

- 不改卡片编号。`/approve N` 等命令仍按原来的卡片身份。
- 不改权限、能力、Evidence 或 System Context。
- 不改输入恢复存储：不改记录版本、限额、保存路径，也不新开一套草稿库。
- 不改 ADR 84 的桌面列表行，不改 ADR 85 的入口和宿主租约，不改 ADR 80 的 `peer --classic`。
- 不决定后置的 P3：内网 Gateway、远程配对，以及把 TUI 写成新表面的契约。那些仍按 ADR 74 的落地顺序和路线图 M6 后置，本文不补那份契约。
- 页头 Accepted 不表示发布验收已经通过。

## 实现记录

Peer-Agent [PR #283](https://github.com/ly-ccx/Peer-Agent/pull/283) 已按上面四条改了现有壳。落点是 `apps/tui/src/project-agent/` 的 `BotListView.tsx`、`ProjectApp.tsx`、`bot-list-format.ts`、`project-copy.ts`，以及 `bot-list-format.test.ts`。

该 PR 记录的定向测试是 `bun test apps/tui/src/project-agent/bot-list-format.test.ts`。同一篇说明写明：最后一次输入条改动之后，没有在新开的 TUI 会话里再核对版面。因此本决定被接受，以及该 PR 的存在，都不等于发布验收。
