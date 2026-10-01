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

## 实测发现与补充边界（2026-10-02）

真实规模夹具进入记忆页会同时渲染10000项、约30000按钮，关闭按钮仍在可访问树且有名称，但定位/输入受阻；不应通过删除规模或增大超时绕过。允许 `drawer/MemoryTab.tsx` 与独立 `state/memoryPage.ts`/测试增加每页50项的表达分页、按工作区/筛选重置，完整记录仍在内存/原store，导出保持完整，编辑/固定/恢复/撤销入口保留。没有IPC/存储/权限变化。初次实测列表名称16.32、摘要3.29、时间2.01，后二者低于4.5:1；允许既有bot-list.css用语义文字token修复，并检查两种主题/既有两种palette。

窗口检查前两轮窄布局阈值/标签定位错误保留为测试夹具失败；真实cover阈值960px，900px模拟viewport通过Tab/Shift+Tab/Escape恢复，不能称为Electron物理900px窗口（产品minWidth1040）。单元全量首次增量订阅8s超时，独立文件142项通过，初次失败不可抹去。

## 搜索性能复核边界（2026-10-02）

CI36913383937 首轮列表122.69ms、复跑可见搜索157ms分别超过100/150ms门限；保留两次失败。复跑搜索阶段表显示每次 corpusStamp 另读全部200份profile两遍，占28–53ms。允许应用服务将本次 directory.query 已读取的 catalog 传给 corpusStamp，宿主用同一次新鲜投影的 workspaceId/agentConversationId 生成文件戳；仍逐次 stat 所有正文、profile、记忆及计划变化日志，不引入持久缓存、不改变授权或存储。无 catalog 时保留原端口兼容。涉及 project-agent-application-service.mjs、project-agent-host.mjs 及 focused tests，B级内部查询端口复用；不增加 IPC 或 main.mjs。必须验证查询间外部写入仍触发索引更新、原性能预算及两平台CI。

## 验证

1. 命名空间与source contract检查；有行为意义的键盘/时间值/focus纯测试。
2. 实际源Electron：list Tab/方向/Home/End/Enter/Space，drawer各布局focus/tab/Esc恢复，卡片Enter不被壳拦截，Quick picker与quiet时间控件中文英文及持久值，超限草稿不丢；reduce没有位移动画，实际tokens对比记录。
3. 完整受影响desktop tests、typecheck、architecture、mac/Linux CI；保留RC01搜索/Received/分页预算与停止反馈实际TCP回归。

## 当前验证事实（未宣布整卡完成）

搜索补修 fe2b5e86 干净源窗口全部9项壳/10项可访问性检查通过，列表16.81ms、可见搜索24.60ms、Received49.00ms；逐次新鲜文件戳3.02–3.15ms。51项应用服务/真实宿主集成测试通过，包括外部store写入后搜索刷新。原CI失败和最终窗口分别保留为 `evidence/rc02-ci-search-retry-failed-20261002.json`、`evidence/rc02-search-catalog-clean-20261002.json`。新两平台CI待确认；预算未改变。

2026-10-02 的真实源 Electron 运行：原有9项壳检查与10项可访问性检查均通过，10000记忆每页50项、前后页身份正确；列表小字在 Frost/Catppuccin 的浅深主题最小对比7.06:1；安静时段键盘修改持久化23:15，英文设置/档案/Quick Chat从保存语言刷新。减少动效下新增壳位移动画数为0。列表20.74ms、可见搜索34.30ms、可见Received67.10ms中位数达原预算。证据`evidence/rc02-accessibility-fixed-20261002.json`来自38bc685c加未提交修复，必须在最终干净HEAD复验，不能充作最终版本认证。

真实首次低对比度与Catppuccin浅色单独失败保留为`rc02-memory-contrast-first-failed-20261002.json`、`rc02-catppuccin-first-failed-20261002.json`。修复后全量类型检查首先发现新测试夹具缺MemoryFilter完整字段，已按真实接口补齐，重跑typecheck通过。最终全量测试、真实停止回归和两平台CI仍在执行。


最终 RC01 同步后干净HEAD c9020ec0 本机完整build/typecheck/architecture/test通过（代码树与此前40a57a09相同，仅增加合入开发线的merge祖先），真实Electron全部九项壳检查与十项可访问性检查通过；窗口0错误，owned进程退出，原报告见evidence/rc02-final-clean-window-20261002.json。包含10000记忆真实50条分页、五主题/语言、减少动效、键盘列表与焦点捕获。PR94与CI36913383937运行中；最终CI结果待确认，不提前宣布卡完成。
