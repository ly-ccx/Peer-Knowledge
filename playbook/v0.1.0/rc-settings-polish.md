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
