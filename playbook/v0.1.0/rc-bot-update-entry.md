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

实施中。尚无完成证据。
