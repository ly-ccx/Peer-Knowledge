# RC 设置页布局补修

2026-10-02，Accepted。负责人指出安装版机器人设置混乱；沿既有全面自测与修复授权执行。C级：仅表达、布局和既有设置入口，不移动能力、权限、存储、System Context或IPC边界。

## 当前截图事实

本轮从实际安装应用捕获设置首屏和下半屏，并对照负责人截图：全局并发与单机器人策略交错，标签/说明继承粗体，接管图标与文字分离，本地模型开关画成普通按钮，自动合回开关被通用按钮CSS覆盖；向下滚动后标题与页签消失。截图可以证明布局问题，不能单凭截图认证模型或可访问性行为。

## 允许改动

- renderer/project-agent/drawer的BotSettingsTab、BotPolicyFields、BotHostControl、BotProfileDrawer及既有bot-drawer.css：外观、工作方式、模型分工分组；左标签右控件；更多角色/模型限制和运行/全局折叠；全局作用域明确；接管按钮同行SVG；复用Switch；标题/页签在滚动中保留。
- packages/i18n/src/index.ts：上述界面的中英文键。
- apps/desktop/scripts/bot-shell-accessibility-checks.mjs及bot-shell-electron-smoke.mjs：沿已有隔离Electron检查设置持久化、展开/收起、窄布局/键盘、真实开关绘制和稳定标题；输出设置截图供本轮复查。
- 本卡、RC05自测/负责人手册：增加已发布RC1之后的UI修复事实与回归范围。已发布tag不移动；下一候选使用rc.2。

## 验证与交付

运行定向契约、中英文检查、受影响Desktop完整测试、typecheck、architecture；实际隔离原生窗口检查，不触碰负责人的设置/数据。检查默认设置页、更多角色、运行/全局、窄覆盖抽屉及开关持久读回；不降低任何性能预算。按既有授权提交推送、PR及两平台CI，合入后再生成新候选。整体Ready仍须本次安装版真实模型与多入口复验。

## 本机结果

代码[PR99](https://github.com/ly-ccx/Peer-Agent/pull/99)，干净提交`1c1957f48cb6f157f1abd5e89d59d965791b3a46`。`pnpm build`、`pnpm typecheck`、`pnpm architecture:check`通过；定向23项通过；Desktop5288项中5283通过、5原有skip，独立i18n契约1项通过，无新增skip。

实际生产源Electron完成9壳/11可访问性/7诊断检查，0页面错误；开工批准、签收策略、本地模型开关、自动合回开关和全局并发均沿实际IPC保存读回。两套配色、深浅色、开关两状态的8项滑块对比度最低6.035:1。窄900px覆盖抽屉无横向溢出，滚动保留标题页签，接管SVG实际几何居中。列表15.63ms、可见搜索27.50ms、Received58.90ms，原预算均通过，owned进程已退出。[原始脱敏报告](evidence/rc-settings-source-passed-20261002.json)。此范围是源码UI、脚本化认知与持久设置，不充当安装包真实模型证明。

复查实际截图：[深色首屏](evidence/rc-settings-default-dark-20261002.png)、[浅色首屏](evidence/rc-settings-default-light-20261002.png)、[更多角色](evidence/rc-settings-advanced-20261002.png)、[运行与全局](evidence/rc-settings-runtime-20261002.png)、[窄抽屉](evidence/rc-settings-narrow-20261002.png)。这些图片仅含隔离的合成项目和消息。

检查器修正亦保留证据：[首轮](evidence/rc-settings-checker-first-failed-20261002.json)误要求flex item的computed display为inline-flex，依CSS blockification修正为flex，实际图标居中断言保留；主题截图最初抓到过渡帧，等待全页面过渡又被离屏动画挂起，主动退出owned测试窗口并[保留中断](evidence/rc-settings-checker-transition-interrupted-20261002.json)。最终检查等待可见开关实际主题颜色稳定，5秒上限，未改产品动效或性能预算。

## 合入

2026-10-02 PR99已合入`7368c8e86c5fcfe9a0b2ece8de5efeda40533636`。[两平台CI36952885532](evidence/rc-settings-ci-20261002.json)全部通过，8项主题/状态对比均通过。macOS列表99.11ms/搜索70.00ms/Received113.00ms，Linux22.09/38.80/77.10ms；预算未改。源提交、CI临时merge与交付merge的tree均为`db66fb3165d1ba1222160595aad5ea135557089c`。本卡代码完成；负责人的安装应用尚未更新，修复须进入rc.2后独立验包。
