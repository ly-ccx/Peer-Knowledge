# RC7 历史对话与任务折叠交互修订

创建时间：2026-10-05
最后更新：2026-10-06
状态：InReview；本机通过，双平台 CI 待回填，等待人工审阅
派单来源：负责人实测指出历史对话卡片粗糙、任务展开和关闭无过渡。
级别：C；代码分支 PeerAgent/pa/rc-history-motion，基线 PeerAgent/dev/0.1.0 的 7276b5e6。

## 目标与依赖

按产品北极星与既有 Frost 规范，历史入口用于找回之前的讨论并交给项目机器人继续；优先标题、时间、搜索和阅读顺序。任务折叠补充内容高度与 SVG 箭头双向过渡，保留原生 details 的键盘语义和结构化状态。依赖已合入的历史读取/继续 IPC、Overlay、主题及动效 token。

## 允许改动

- project-agent/AppMenu.tsx：历史菜单入口把返回焦点目标设为原设置按钮，复用已有菜单 focus-return 状态；不改菜单接口或其它入口。
- project-agent/HistorySheet.tsx：列表读取状态、选择/返回与对话预览的呈现；不改继续历史的协议或后端。
- project-agent/HistoryConversationList.tsx（新建）、state/historyPresentation.ts / historyPresentation.test.ts（新建）：标题搜索、更新时间分组/排序、无标题回退、限定可见行数与渐进加载；只处理 UI 数据，不改存储或搜索范围。
- project-agent/styles/bot-history.css（新建）：紧凑历史浮层、固定头部、独立列表滚动、灰底搜索、无卡片描边、主题/窄窗/焦点/强制颜色。
- project-agent/conversation/BotConversation.tsx、DelegatedWork.tsx、styles/bot-reply-context.css 与 bot-disclosure.css（新建）：任务外层和内层折叠的高度/淡入及 SVG 旋转，既有 details 语义和 disclosure 状态不变。只对本屏触及的字符箭头做 SVG 替换；与待审 PR124 的同一处 SVG 改动等价，合并时保留两者所需的 SVG 与过渡规则。
- ui/icons/PeerIcon.tsx：只增加 Search SVG；既有 SVG 接口不变。
- packages/i18n/src/index.ts：projectAgent.history.* 中英文文案。
- scripts/bot-history-motion-checks.mjs（新建）、bot-shell-electron-smoke.mjs、bot-work-surface-checks.mjs：复用既有隔离宿主/原生 Renderer，验证历史查找/返回/继续、键盘、深浅主题、大字号/窄窗与实际双向过渡；只用隔离事实，不触碰真实用户数据。

以上 renderer 路径均相对于 apps/desktop/renderer/src/；scripts 相对于 apps/desktop/。不改 Runtime、协议、权限、Evidence、System Context、IPC、存储、依赖、版本或发布物。仅做这一新增反馈卡，不重复 PR125 的任务详情修改或 PR124 的全局 SVG 扫描。

## 实现与验证

历史行不加大卡片外框；以分组标题、紧凑标题/时间行和悬停层表达。搜索明确只搜当前入口的对话标题；不同任务/机器人历史读取不混用。加载中、失败、实际空、无搜索匹配分别说明。分页只是当前已读数据的逐步展示，不假装新增后端全局搜索。Overlay 关闭按钮走已有 requestClose，保留退场动画及焦点恢复。

折叠高度使用当前 Electron 支持的 ::details-content 与 interpolate-size；复用 200ms motion token、内容裁剪和 content-visibility allow-discrete，展开/收起都有中间帧，快速反向从当前高度连续变化；减少动态效果直接切换，隐藏内容不能接受键盘焦点。

历史预览只展示用户与机器人内容，复用既有 Markdown 展示；工具载荷不进入主预览。机器人目标选择复用既有 Dropdown，提交繁忙和读取失败提供人类文案。以上仅改变阅读表达，继续历史仍由原上下文快照/确认/输入队列路径负责。

## 必须新增的验证

纯状态测试：标题检索、日期边界/分组排序、非法时间/无标题、排序不修改原数组、可见行数。原生检查：标题检索与清除、无匹配、分组、滚动头部、选择/返回、历史读取和真实既有继续入口、焦点/Escape、主题/窄窗/大字；任务外层/内层展开收起中间高度帧、快速反向、SVG 旋转、关闭后不可聚焦、减少动态效果。运行受影响 desktop 完整测试、先 build 再 test、workspace typecheck/architecture。

## 退出与交接

提交同轮 push，PR 回开发线待双平台 CI 和人工审阅，不自行合并或发布新 RC。实际原生截图和动效帧提供可检查结果。受控认知/任务只证明 UI 与既有入口，不代表真实模型/任务工具执行验收。

## 卡片

负责人新增实测反馈：历史对话大卡片缺少层级；任务展开/关闭没有过渡。本卡对应 [代码 PR126](https://github.com/ly-ccx/Peer-Agent/pull/126)，不重复 PR124 的全局 SVG/消息修订和 PR125 的任务详情修订。

## 分支与提交

代码分支 PeerAgent/pa/rc-history-motion，提交 30c6430242bfca0fd12a648796958a4a6ad5ce8d，源 tree 316ac4bb87257841f628953b523e290ce95d0dec；基线 7276b5e6。提交已推送。本机原生报告 sourceDirty=true 如实保留，验收源在提交前已固定，提交 tree 与之相同。

## 改了什么

紧凑历史标题/时间行、今天/昨天/最近 7 天/更早分组、明确范围的标题搜索与 40 行渐进展示；固定头部与独立滚动。返回保留搜索、列表位置及所选行焦点；关闭恢复原设置入口。预览用户在右、机器人在左，复用 Markdown 和 Dropdown；载荷不进入主预览。继续仍走原 IPC、背景确认、历史快照及输入队列。

外层任务、单项任务、更多项和回复详情保留原生 details 语义，使用双向高度/透明度过渡与 SVG 旋转；快速反向从当前高度变化。减少动态效果直接切换，关闭后的操作不能接受 Tab。使用既有 Frost 表面、圆角、200ms 高度及 120ms 淡入 token，不新建视觉体系。

## 与卡片的偏差

实机修正本浮层与通用 Overlay 边距叠加导致的窄窗溢出；将 AppMenu 的已有返回焦点状态设为原入口；原工作界面门禁补条件等待同一实际进展文本，断言不变。继续历史检查用隔离 canonical 输入队列核实历史引用/快照，使用既有 latest=true 获取尾页，避免把界面字段裁剪或默认旧页误认为数据未写入。未新增 IPC 或后端能力。

## 验证

- 新增纯状态 4/4：本地日历跨年分组与真实时间排序、标题检索规范化、非法/未来时间与无标题、源数组不可变、渐进展示与稳定排序。
- desktop build、workspace typecheck、architecture:check、git diff --check 通过。
- desktop 完整 5353 用例：5348 通过、5 个既有跳过，0 失败/取消；额外 i18n 1/1。
- 生产 Electron/main/preload + 隔离数据完成 60 项壳/界面检查，本卡新增 5 组；0 页面错误、0 窗口授权错误、专属测试进程已退出。
- 真实历史投影：40→48 行、标题搜索/无匹配/清除、键盘打开、Markdown 预览/返回、保留查询/焦点、实际空与暂时不可读/重试、关闭/Escape、深浅主题、390px 大字号无横向溢出。继续在选定机器人只追加一条 canonical input，含原历史引用与快照；原历史消息和 contentRevision 不变。
- 263 帧原生 CDP 屏幕录制与 5 段 rAF 高度采样：外层 26.5→62.5px、内层 32→117.390625px，展开/关闭都有中间帧；驱动等待 85ms 后再次实际点击反向连续收起；关闭最终内容隐藏且不能接收 Tab，SVG 最终旋转 180°，减少动态效果直接切换。GIF 从原生帧按时间线取样、10ms 时间分辨率、末帧停留 1 秒；不以 GIF 编码时长代替实际 CSS/采样验收。
- [深色历史](../../design/product/assets/peer-frost-history-motion/history-dark.png)、[浅色历史](../../design/product/assets/peer-frost-history-motion/history-light.png)、[预览](../../design/product/assets/peer-frost-history-motion/history-preview.png)、[窄窗大字](../../design/product/assets/peer-frost-history-motion/history-narrow-large.png)、[实机折叠录制](../../design/product/assets/peer-frost-history-motion/task-disclosure-native.gif)。
- 本机保留原生报告、追踪包、原始帧/时间线及失败检查记录。受控认知与任务只证明 UI 和既有入口，不代表真实模型或任务工具执行/Evidence 验收。
- 初次双平台 CI（ed9281c8，[run 37339491168](https://github.com/ly-ccx/Peer-Agent/actions/runs/37339491168)）Linux 通过；Mac 的四段展开/收起通过，在快速反向的最终隐藏断言失败。旧采样从远端点击指令前起算 480ms，可能在第二次实际点击的过渡结束前截止。30c6430 只修正测试计时：预先安装采样器，确认实际点击次数，再保留最后一次实际点击后的完整 480ms，6 秒总边界和原高度/中间帧/无整段跳跃/隐藏断言不变。修改后本机完整原生 60 项再次通过；Renderer 与产品样式未变。最终提交双平台 [run 37341105993](https://github.com/ly-ccx/Peer-Agent/actions/runs/37341105993) 进行中，完成后回填。

## 架构影响

C 级：Renderer 表达与交互；Runtime、协议、权限、Evidence、System Context、IPC、存储、依赖及版本不变。

## 文档偏差

本知识仓只补本卡及受控截图/动效证据；不复制用户截图，不改北极星或 ADR，不在代码仓新建知识树。

## 未完成与后续

双平台 CI 待回填最终结果；人工审阅未完成，不自行合并或发布 RC。PR124 的背景任务 SVG 与本卡重叠，合并时保留 SVG 和本卡过渡规则。PR125 任务详情双平台 CI 已通过，独立等待审阅。
