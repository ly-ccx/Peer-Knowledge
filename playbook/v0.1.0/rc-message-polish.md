# RC7 消息引用、定位与 SVG 图标修正

创建时间：2026-10-05
最后更新：2026-10-06
状态：InReview（引用修订、本机验收、推送与最终 head 双平台 CI 完成；上一版记录保留）
派单来源：负责人 RC7 实测指出普通接续回复重复引用、用户消息外框，以及全局禁止字符图标。
级别：C。分支：PeerAgent/pa/rc-message-polish；基线 PR123 已合入的开发线。

## 范围与允许改动

- 普通接续单条用户消息的回复不显示重复引用；跨消息、较早锚点和多来源上下文保留定位入口。显式划词引用仍随用户消息显示。流式、正式回复、停止/失败卡与历史使用同一展示投影，原关联数据不变。
- 消息定位以原内容短暂底色反馈，不在消息和送达状态外围画框；保持分页/虚拟化定位及键盘焦点。
- 全局扫描桌面 renderer 的 JSX、状态展示、菜单、分页、附件按钮及 CSS 生成内容中的字符图标，替换为既有 SVG 图标组件。原文、快捷键说明、数学计数、diff 内容不属于图标。
- 允许修改 apps/desktop/renderer/src 下对应的界面、样式与图标组件；新增/修改状态投影与定向测试；同路径 UI 图标扫描门禁；AGENTS.md 加入负责人明确的 SVG 图标规则；apps/desktop/scripts/bot-shell-electron-smoke.mjs、bot-shell-reply-checks.mjs、scripts/rc-response-interaction-smoke.mjs 补实机验收。

不修改 Runtime、协议、权限、Evidence、System Context、IPC、存储或版本；不加依赖。产品资料只写知识仓。

## 验证与退出

先复现普通流式引用与永久描边，再验证修复：定向状态与图标扫描、desktop build/完整测试、workspace typecheck/architecture；原生 Electron 深浅主题、普通流式到正式/历史、显式引用、旧消息分页定位、临时高亮退出、SVG 展开状态、键盘与窄窗口。受控模型夹具仅验证表达链，不等同真实模型或任务执行验收。代码提交同轮 push，PR 回开发线；本卡不发布新 tag。

### 2026-10-06 引用视觉修订

负责人否定当前「回复 / 摘录 / 右箭头」的大块灰底卡片。沿用本卡代码分支和 PR124，C 级表达修订：引用为正文上方的来源名称与最多两行摘录；去掉独立填色容器、常驻右箭头和泛化“回复”标题，保持小字号与紧凑间距。正常连续回复仍不显示引用；显式引用和较早关联仍可通过鼠标或键盘回到真实原消息。用户消息内引用复用同一预览，来源按实际已加载消息角色判断，未加载来源不猜作者、不显示 UUID。完整原文和引用关联不随显示截断改变。

允许文件沿用上文 renderer 状态/界面/样式与定向测试范围，原生验收扩展 `apps/desktop/scripts/bot-shell-reply-checks.mjs`；知识截图保存到 `design/product/assets/peer-frost-quote-refinement/`。不修改引用存储、消息事件或执行边界。先验证来源投影，再核验深浅主题、长文本、760px 窄窗口、键盘定位、划词发送、普通流式到正式不重复引用；构建、受影响包完整测试、类型/架构门禁及最终提交双平台 CI 完成后交接。


## 全局排查清单

| 位置 | 原字符表达 | 当前表达 |
| --- | --- | --- |
| Bot 跟进摘要、工具参数/结果/技术详情 | CSS `⌄`、`›` | PeerIcon SVG，展开时旋转 |
| 旧聊天工具/结果/stdout/stderr/引用 | CSS 字符箭头，部分层另有 SVG mask | 直接 SVG；同步去掉伪元素，避免双箭头 |
| 更多菜单与两类技能市场分页 | `⋯`、`‹`、`›`、`…` | SVG 更多、左右箭头、省略指示 |
| 模型测试、快捷会话选中与模型目录 | `✓`、`✗`、`×`、`–`、加载 `…` | SVG 状态图形；忙态保留可读按钮名称 |
| 模型登录/保存与系统设置保存 | `⚠`、`...` | SVG 警告/忙态指示及明确状态文案 |
| macOS 权限拖动提示 | 文案开头 `↑` | SVG 向上箭头 |
| 历史、任务、复核与源头交付 | `✓`、`□`、`×`、`!`、`Ⅱ`、`−`、`•`、`→`、`↛` | SVG 状态/交付图形 |
| 上传、附图、引用、成功条件移除 | `×`、提示图标字母 `i` | SVG 关闭/信息；保留或补足无障碍名称 |
| 旧聊天流式光标 | `▍` | SVG 矩形光标，沿用现有动态效果 |
| 自动化与浏览器 | `⌁`、`★`、`⚠️`、加载 `…` | SVG 空态/警告/忙态；默认模型改为“默认”文案 |

475 个 renderer、共享 UI、语言源码文件经过全局 AST/CSS 门禁。该门禁识别 JSX/状态分支、emoji、ASCII 图标、CSS 生成内容及 Unicode 转义；以夹具验证注释、快捷键、正常路径说明、数学计数、diff 与截断文案不会被误当作图标。唯一 HTML 预览另行检查，无字符图标。用户内容与工具原文不改写。

## 2026-10-05 交接报告（历史）

### 卡片
RC7 消息引用、定位与 SVG 图标修正，C 级。

### 分支与提交
- 代码分支：PeerAgent/pa/rc-message-polish；基线：7276b5e6。
- 提交：401f27ff1b7f240b97d43abf328fa08c93658016。
- [代码 PR124](https://github.com/ly-ccx/Peer-Agent/pull/124)，目标 PeerAgent/dev/0.1.0。
- 验收源 tree 与提交一致：c2491e2fd335d9fad65af0dd20c776efbad20c90。

### 改了什么
SVG 清单见上表；AGENTS.md 固化图标规则。replyReferenceState 只决定展示是否重复引用，不修改 replyTo/签收/委派关联；流式、正式、历史、停止/失败共用同一规则。useMessageHighlight 等定位目标实际出现后短暂改变内容底色，1800ms 后退出，保持重复请求、分页/虚拟化定位与键盘焦点；不在用户消息和送达状态外围描边。

### 与卡片的偏差
无。47 个代码文件全部在许可范围内，没有依赖或版本变更。

### 验证
- 定向状态/扫描/模型面板门禁：15/15 通过，全局扫描 475 个文件。
- `pnpm --filter @peer-agent/desktop build`、`pnpm typecheck`、`pnpm architecture:check`、`git diff --check` 通过。
- desktop 最终全量：5358 个用例，5353 通过、5 个既有跳过，0 失败/取消。先前 SVG 忙态替换额外占了一行，触发行数冻结门禁；改为在原有表达行内替换并复测，既有门禁未放宽。该次原始失败日志与最终成功日志均保留。
- 原生 Electron 最终验收：55 项通过，0 页面错误、0 窗口授权错误，专属测试进程确认退出。包含 200 Bot/10000 消息、普通等待/增量/正式/历史/停止/失败无重复引用、较早锚点分页定位/高亮退出/重复定位、显式划词引用及草稿、SVG 嵌套详情、深浅主题、760px 窄窗口、键盘、减少动态效果、模型/档位、工作/记忆分区。
- 外部证据目录：`$CODEX_HOME/visualizations/2026/10/05/rc-message-polish/`；verification.json、electron-report.json、electron-trace.zip、完整测试/类型检查/构建日志与八张实际窗口截图。原生报告的 sourceDirty=true 如实保留（验收先于提交），提交 tree 已与验收源 tree 对齐。
- [PR 全量 CI37318451492](https://github.com/ly-ccx/Peer-Agent/actions/runs/37318451492) 对 401f27ff 的 macOS/Linux 全量构建、类型、架构、测试与原生窗口检查全部成功。Actions 测试的合成合并提交 a58511c0e1a7a887abff77d019ce178a6f0a187a，tree 同为 c2491e2fd335d9fad65af0dd20c776efbad20c90；本机、PR 提交与 CI 候选 tree 一致。
- 未运行本卡范围外的真实模型耗时与任务工具执行验收；受控认知与会话事实夹具只证明本机表达链和真实宿主/IPC/存储交互。

### 架构影响
C 级。Runtime、协议、权限、Evidence、System Context、IPC 与存储边界未移动，不修改北极星/ADR。

### 文档偏差
SVG 规则已写代码仓 AGENTS.md，具体排查与验收事实写本知识卡；无产品知识写入代码仓。

### 未完成与后续
PR124 待审阅；按实施手册不自行合并。本卡没有新 RC 发布授权，不改写已发布 RC7 的 tag/资产。

## 2026-10-06 引用修订交接报告

### 卡片

负责人实机截图追加“这个引用一点都不高级”。沿用 RC7 消息修正卡，C 级；只调整引用表达与对应验收。

### 分支与提交

- 代码分支 `PeerAgent/pa/rc-message-polish`，仍在 [PR124](https://github.com/ly-ccx/Peer-Agent/pull/124)。
- 引用实现 `16107c55`；三个验收补修提交 `ee8d38ee`、`d1c72ccc`、`8a888f8c`。
- 最终 head `8a888f8c6d6c5d963e6388b6889f0e089164a200`，tree `af2c2b20391ac071bdbe0b0df0412943d99d4567`。

### 改了什么

- 正文上方的引用改为透明、无边框、无阴影的紧凑来源与摘录，去掉泛化“回复”标题和常驻右箭头。来源 11px、摘录 13px，摘录最多两行、宽度不超过 360px；保留至少 44px 点击区域与键盘焦点。悬停/聚焦只提升文字和下划线提示，不画新的卡片。
- 来源基于实际已加载消息角色：用户显示“你”，Bot 回复显示真实 Bot 名称；未知或未加载来源使用“引用”标签，不猜作者、不露出 UUID。显示截断交给 CSS，完整原文留在提示与关联里。
- Bot、流式、停止/失败及用户气泡内引用复用同一预览；普通接续回复继续不显示冗余引用，replyTo 与 quoteRefs 原关联不改。实际发送、草稿取消和分页定位走原有宿主/IPC 链。

### 与卡片的偏差

无。追加 10 个代码文件的修改均在 renderer、纯投影测试及原生验收许可范围；PR 累计 50 个文件，包含上一轮 SVG 排查与消息定位修正。没有依赖或版本变更。

### 验证

- 新来源投影测试先红；最终引用/图标定向检查 10/10，475 个源码文件 SVG 门禁通过。完整原文、未知来源、实际角色、英语标签和不变更 canonical 内容均有覆盖。
- 最终 head 的 desktop build、workspace typecheck、architecture、diff 检查通过；desktop 完整测试 5359 个，5354 通过、5 个既有跳过、0 失败/取消；另 i18n 1/1。
- 受控原生 Electron 57 项通过（10 主流程、7 更新器、6 引用、11 流式、4 问题卡、6 工作面、13 无障碍），0 页面异常与权限异常，测试进程确认退出。引用包括鼠标/键盘旧消息分页定位、真实作者、完整提示、深浅色、两行截断、760px 窄窗、划词取消/发送与用户引用回跳，正常等待/流式/正式/停止/失败没有新增引用框。
- 本机原始报告如实保留 `sourceHead=d1c72ccc`、`sourceDirty=true`：最后一份滚动验收补修已暂存后运行，受验候选 tree `af2c2b20` 与最终提交 tree 完全相同。提交前后没有产品代码变化。[最终 head CI37409351891](https://github.com/ly-ccx/Peer-Agent/actions/runs/37409351891) 的 Mac/Linux 构建、类型、架构、完整测试和原生窗口门禁全部成功；实际 CI 合成合入 `44ed6e30f708bb3537bfea2e6349f00cb3865095` 的父提交为基线 `7276b5e6` 与最终 head `8a888f8c`，tree 同为 `af2c2b20`。
- 三次前置实机失败及日志均保留：旧消息定位后原回复重挂载，原脚本仍假定详情展开；用鼠标重开详情改变键盘焦点模式；新增实际引用对话后旧工作回复移出虚拟窗口。修正脚本通过键盘重开详情、通过实际滚动找回回复，既有焦点、过程、工作与动态效果断言均保留；失败测试进程也确认退出。被新提交取代的 CI 三次取消，不列为成功证据。
- 证据目录 `$CODEX_HOME/visualizations/2026/10/06/rc-quote-refinement/` 保存原始报告、前置失败、构建/完整测试/类型/架构日志及六张原生截图。受控认知只证明表达、真实宿主/IPC/存储与导航，不声称真实模型耗时或工具执行。
- 已下载并检查两平台实际窗口报告：`sourceHead=44ed6e30`、`sourceDirty=false`、`ok=true`、0 页面/权限异常、测试进程均确认退出；`verification.json` 绑定本机候选 tree、最终 head、CI 合成合入 tree、job 与平台报告。隔离 canonical 文件也确认只创建一条对应用户输入，`quoteRefs[0]=rc-message-9999`，不是仅验证乐观显示。

### 架构影响

C 级，来源预览投影只驻留 renderer。Runtime、能力暴露、协议、权限、Evidence、System Context、IPC 和存储边界均未移动。

### 文档偏差

上一版低对比填色预览的视觉规格已由负责人本次截图评审修订为透明文字上下文；具体尺寸、行为和事实记于本卡，产品北极星不变。截图归档在 `design/product/assets/peer-frost-quote-refinement/`。

### 未完成与后续

最终 head 的双平台 CI 已完成；PR124 仍待审阅，不自行合并或重写 RC7。

### 实机截图

- [深色引用](../../design/product/assets/peer-frost-quote-refinement/reply-dark.png)、[浅色引用](../../design/product/assets/peer-frost-quote-refinement/reply-light.png)
- [窄窗引用草稿](../../design/product/assets/peer-frost-quote-refinement/reply-narrow-quote.png)、[发送后的用户引用](../../design/product/assets/peer-frost-quote-refinement/reply-narrow-sent.png)
- [普通等待无引用](../../design/product/assets/peer-frost-quote-refinement/stream-waiting.png)、[普通流式转正式无引用](../../design/product/assets/peer-frost-quote-refinement/stream-complete.png)
