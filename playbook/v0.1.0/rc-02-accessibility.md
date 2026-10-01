# RC-02 中英文、可访问性与动效实施边界

创建时间：2026-10-02
最后更新：2026-10-02
状态：Accepted实施边界；负责人已授权自主完成全部修复、自测及候选发布。

级别C，全部为renderer表达、控件与验证；没有能力、PermissionGrant、Evidence、IPC、Context或存储契约变化。RC01的CI重跑同时，在独立代码工作区从开发基线实现；提交前同步已合入RC01，最终按卡合入。GA仍等负责人全面测试。

## 范围与允许文件

- `project-agent/BotList.tsx`、`BotListShell.tsx`、`BotRow.tsx`：列表焦点/aria关联及独立键盘处理；window通用方向/Enter处理只作用搜索框，不能拦截抽屉按钮。
- `project-agent/drawer/BotProfileDrawer.tsx`：打开进入tab、关闭归还trigger、隐藏dock inert；tablist roving与tabpanel关联。
- `app/components/Overlay.tsx`和深UI焦点helper：模态聚焦、Tab约束、关闭归还；非模态anchor沿已有规则，嵌套仅topmost处理。
- `app/components/QuickChatWindow.tsx`、独立目标picker：现有Dropdown替换机器人原生select，加载settings locale并用i18n键；不扩展经典Quick Chat能力。
- `app/components/GeneralPanel.tsx`、独立时间控件与纯状态：既有Switch/Dropdown替换quiet checkbox与time input，分别标注起止/小时/分钟，值仍HH:mm并沿原保存/失败恢复。
- `project-agent/conversation/QuoteChip.tsx`、`UserBubble.tsx`、`BotComposer.tsx`：字符图标换PeerIcon SVG、任务标签用键；按既有100000 UTF-16输入限制在UI保留超限草稿并提示，不改变后端边界。
- `workbench/BackgroundRuntimePanel.tsx`：触碰处既有字符图标换SVG、文案入projectAgent.background键；保留实际停止状态/Evidence，不扩大旧Details业务。
- `styles/tokens.css`、`motion.css`及必要既有控件styles：reduce禁用位移动画，不能禁用必要静态布局transform或让退出presence卡死；新增动效只用已有基元。
- `packages/i18n/src/index.ts`追加中英文对应键；新检查脚本/测试校验projectAgent、modelRouting、developer命名空间完整与占位符一致，源码契约禁止新增内联isZh三元表达式。
- `apps/desktop/scripts`专用真实Electron a11y检查helper；现有shell smoke装配调用及package.json登记。必要CI调用保持完整门禁和RC01原预算。

main.mjs净增0；ChatSurface/Sidebar/LlmSettingsPanel/TUIapp不加功能。禁止为通过删除/skip/放宽旧测试；确定实际焦点、键盘、中文英文、控件持久值、减少动效与contrast，不能仅靠源码字符串宣布窗口通过。

## 验证

1. 命名空间与source contract检查；有行为意义的键盘/时间值/focus纯测试。
2. 实际源Electron：list Tab/方向/Home/End/Enter/Space，drawer各布局focus/tab/Esc恢复，卡片Enter不被壳拦截，Quick picker与quiet时间控件中文英文及持久值，超限草稿不丢；reduce没有位移动画，实际tokens对比记录。
3. 完整受影响desktop tests、typecheck、architecture、mac/Linux CI；保留RC01搜索/Received/分页预算与停止反馈实际TCP回归。
