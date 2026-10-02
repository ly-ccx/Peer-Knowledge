# RC：机器人侧栏更新入口恢复

创建时间：2026-10-02
最后更新：2026-10-02

## 目标与边界

用户报告机器人界面左下角丢失升级入口。经典侧栏挂载 `VersionBadge`，机器人侧栏只挂载 `MeMenu`，因此版本、更新状态和安装入口没有进入默认壳层。分类 C：恢复表达层入口，复用既有 `useUpdater`、更新弹窗、自定义 `Dropdown` 和 typed preload API。

- 分支：`PeerAgent/pa/rc-bot-update-entry`，从 `origin/PeerAgent/dev/0.1.0` 创建。
- 允许改动：`BotListShell.tsx`、`project-agent/styles/bot-list.css`、`app/components/VersionBadge.tsx`、`app/state/useUpdater.ts`、`packages/i18n/src/index.ts`、`apps/desktop/scripts/bot-shell-electron-smoke.mjs`；新建 `apps/desktop/scripts/bot-shell-updater-checks.mjs`。
- 知识交付：本卡、既有 RC 自测报告和验收指南的更新入口条目及对应证据。
- 不增加依赖、IPC、存储、执行能力或发布版本；经典壳层的版本徽标保持既有默认行为。

## 实现与验证

1. 在机器人侧栏底部保留个人菜单，恢复版本徽标；可直接选择自动 / Beta / 正式更新通道。
2. 版本徽标可选展示渠道，状态与动作由同一个既有 updater hook 消费；主进程继续拥有通道和更新状态真值。
3. 自定义下拉向上展开，图标使用 SVG；240–360px 侧栏、中英文、浅深主题中入口可达，下载与安装状态不溢出。
4. 先让真实 Electron 壳层检查复现缺失入口，再实现。通过实际渠道 API 验证设置持久化、切换经典壳层后通道一致；事件注入只验证更新阶段表达，不声称完成真实下载或安装。
5. 运行定向 Electron 检查、受影响桌面完整测试、构建、类型、架构检查和两平台 CI。记录结果后推送 PR，沿已有用户授权评审合入。

### 两个设置入口的同步

恢复渠道下拉后，底部与“更新与关于”会同时消费 `useUpdater`，后者原来只更新发起修改的实例。已有用户授权自主完成 RC 修复涵盖此表达层补齐：同一窗口中仅分发主进程成功返回的状态快照，保证返回机器人列表后渠道仍一致。不增加 IPC 事件或独立通道事实源；补实际设置页→底部读回的失败复现和窗口检查。

## 当前状态

本机修复与回归通过，PR [106](https://github.com/ly-ccx/Peer-Agent/pull/106) 已推送并附到任务；两平台 CI 进行中，尚未合入。源码 `6360c4039da5bb9448df771373c247248081a3d2`，tree `3cc892774acace7f5f46bd89db646acb2d7382e5`。

- [失败复现](evidence/rc-bot-update-regressions-failed-20261002.json)：缺失入口、设置页修改后旧渠道、安装按钮入场缩放使点击目标短暂不足24px。失败均保留，owned进程退出。
- [本机实际窗口](evidence/rc-bot-update-local-window-passed-20261002.json)：5组 updater、9壳、11可访问性、7诊断，36种阶段/布局组合全部通过，0页面错误。列表15.29ms、搜索23.30ms、Received51.30ms，原预算未放宽。
- [完整本机门禁](evidence/rc-bot-update-local-gates-20261002.json)：完整构建、最终桌面构建、typecheck、architecture、5292桌面测试通过（总5297，原5 skip），独立i18n AST1项通过。
- 用户当前安装应用仍为 `0.1.0-beta.5`；已发布RC2不含本修复。下一不可变安装候选必须复验，不能把源码与注入阶段表达写成真实下载/安装已通过。
