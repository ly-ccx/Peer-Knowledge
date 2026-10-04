# RC 侧栏底部入口与版本设计

2026-10-04，Accepted。负责人指出「我」的产品含义不清，头像框和孤立版本文字缺乏整体设计；沿既有自主修复与合入授权推进。本卡不发版。

## 边界

基线 dev `e2fa5e5d`，分支 `PeerAgent/pa/rc-footer-design`。C 级表达层：入口实际承载设置、历史、自动化、能力管理，改为明确的设置入口；版本保持右侧，区分版本与预发布阶段，不把更新渠道当作身份。经典界面保持原样，更新真值与动作仍来自已有 useUpdater。不修改 IPC、存储、权限、Evidence 或运行时契约。

文档偏差：工作台早期设计稿底部仍描述「我的头像 · 设置」，当前实现没有个人资料入口。此卡按实际承载的全局功能修正表达；不据此新建账号或个人资料功能，也不修改产品北极星。

允许路径：desktop renderer 的 project-agent/{MeMenu,AppMenu,BotListShell}.tsx、styles/bot-list.css、state/botListShellContract.test.ts；app/components/{VersionBadge.tsx,versionBadgeLabel.ts,versionBadgeLabel.test.ts}；ui/icons/PeerIcon.tsx（新增原创 SVG 设置图标）；现有 bot-shell-{updater,accessibility,diagnostics}-checks.mjs 和 bot-shell-electron-smoke.mjs；本卡及脱敏验收证据。无新依赖、版本文件或发布工作流改动。

## 验收

- 去掉「我」及用户头像框，设置入口与右侧版本统一垂直节奏。菜单保持原有四个入口，增加准确的 SVG、键盘导航和 Escape 回焦；无光晕、无字符图标。
- 机器人壳版本显示紧凑基础版本与 RC/Beta 阶段标签；完整版本保留在可访问名称中，不修改版本比较或升级筛选。经典版本展示不变。
- 更新渠道仅在设置内。现有弹窗、下载进度、安装入口保持可用；240/292/360px、中英文、明暗主题下无裁切或重叠。
- 构建、受影响 desktop 完整测试、typecheck/architecture/IPC；隔离真实 Electron 截图检查底部与菜单及更新三状态；两平台 CI。测试使用临时数据，不触碰真实用户数据。

## 本机验收

代码 `a09256b6`，PR [#120](https://github.com/ly-ccx/Peer-Agent/pull/120)。desktop 5327 通过、5 个既有条件跳过；i18n 独立测试 1 通过；build、全仓 typecheck、architecture、IPC 通过。完整单元测试在 85574950 完成，最终提交仅再移除菜单阴影；构建和实际窗口在最终 clean head 重跑，CI 再跑完整门禁。

2026-10-04 实际隔离 Electron：7 项 updater、72 个布局样本、9 项主流程、5 项回复交互、12 项可访问性检查及诊断导出通过；页面及主进程授权错误均为 0。底部闲置高度 44px，已查看深色闲置、菜单、240px 更新/42% 下载/安装截图。更新状态为受控事件，不宣称完成真实下载或安装。

新增键盘验收先发现 Tab/关闭后的焦点问题；持续复查定位外层 capture Escape 提前移除菜单，修复后 Escape 回到设置、Tab 移到版本、Shift+Tab 回到设置。未放宽断言。裸 Electron 测试入口改为提供 desktop package.json 的产品版本，验证真实 RC 标签，经典壳仍显示完整 `v0.1.0-rc.5`。最后检查再移除暗色菜单发白阴影；最终 clean head 的原生检查与截图通过，机器记录提供源码及截图哈希。

最终 CI 37173813949（a09256b6）在 Mac/Linux 均成功，含两平台实际窗口检查。PR #120 已合入 dev，merge `7b793640b662a2c9583d52b3ca072c1a40110df5`，主工作区已快进同步。旧候选 CI 37173601283 因菜单阴影修正被替代，已取消，不作为最终门禁结果。

## 负责人复测步骤

1. 在机器人壳看左下角：SVG 设置入口，无「我」、无头像框，版本及阶段在最右侧。
2. 点设置：四个功能入口仍在；鼠标悬停、键盘上下/Home/End/Enter 可操作，Escape 回到触发器，Tab/Shift+Tab 退出菜单。
3. 点版本：打开既有更新弹窗；更新渠道仅在设置 → 更新与关于出现，切换后重启保持。
4. 对可升级的已签名安装包检查可用更新、下载进度和安装动作。这是负责人真实安装环境检查，本机受控 UI 测试未代替真实下载/安装。
5. 调整侧栏到最窄 240px，分别检查中英文、明暗主题。底部控件无裁切/重叠，版本始终在右侧。
6. 切经典界面：保持完整版本文本及原有展示；再切回机器人壳，设置与机器人数据仍在。

当前安装版 RC5 不包含本卡。本卡没有发版，不改变整体 GA 验收结论。
