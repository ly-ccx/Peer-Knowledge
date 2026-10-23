# open-claude-ui 精读与 Peer 取舍

创建时间：2026-10-23
最后更新：2026-10-23

> 定位：来源研究与设计决策依据；规范入口是 [Peer Frost 体验规范](../../knowledge/specifications/peer-product-experience-standard.md)。本记录不把第三方材料提升为运行时指令。

## 1. 来源与研究边界

- 仓库：[Caho1/open-claude-ui](https://github.com/Caho1/open-claude-ui)。
- 本次固定快照：`c1f923ae0051a871941b98a0e2e3183a545e6a85`，提交时间 2026-10-21，读取日期 2026-10-23。
- 阅读重点：v1 设计、会话、动效、Agent 指南；v2 的版本边界、交互演进、底座说明；实际 token、弹簧、输入、滚动、决策卡、模态、分段、折叠、附件、分栏与媒体手势实现。源码用于核对说明，不以 README 列出的组件数量推定完成度。
- 浏览过项目展示站的当前首屏；这只能辅助理解设计呈现。没有安装或解包 Claude，没有独立验证其专有生产包、性能结论、模型能力与版本更新叙事；没有运行上游测试或完整键盘/读屏审计。
- 项目是第三方逆向研究及参考实现，**不是 Anthropic 官方设计规范**。下文“观察”指固定快照中的可读事实，“推断”指设计解释，“采纳”指 Peer 自己的决定。

## 2. 最有价值的方法

它把许多容易被当成“手感”的细节变成可命名、可复用、可审阅的规则：表面分层、字体角色、尺寸阶梯、动效参数、滚动意图、输入法事件、手势终止路径。这比某个色号或某组弹簧值更值得吸收。

Peer 已有 Frost token、集中动效与运行时治理。本次工作将它们连接成**视觉表达、变化连续性、人与代理的交接责任**三份契约。辨识度继续来自本机委托、行动权与 Evidence；不把 Peer 改成上游产品的仿制界面。

## 3. 逐项转化

| 上游观察 / 来源 | 值得吸收的理由 | Peer 决定 |
|---|---|---|
| Surface 角色、字阶和材质语义：[v1 设计令牌手册](https://github.com/Caho1/open-claude-ui/blob/c1f923ae0051a871941b98a0e2e3183a545e6a85/docs/v1/01-%E8%AE%BE%E8%AE%A1%E5%93%B2%E5%AD%A6%E4%B8%8E%E8%AE%BE%E8%AE%A1%E4%BB%A4%E7%89%8C%E4%BD%93%E7%B3%BB.md)、[主题与 token](https://github.com/Caho1/open-claude-ui/blob/c1f923ae0051a871941b98a0e2e3183a545e6a85/code-examples/cds-theme.css) | 相同对象有相同视觉角色，主题不靠逐组件补丁 | 采纳方法；沿用 Frost / `--ui-*`，不引入 CDS token 与陶土品牌 |
| 单闭合边框规则：[v1 设计令牌手册](https://github.com/Caho1/open-claude-ui/blob/c1f923ae0051a871941b98a0e2e3183a545e6a85/docs/v1/01-%E8%AE%BE%E8%AE%A1%E5%93%B2%E5%AD%A6%E4%B8%8E%E8%AE%BE%E8%AE%A1%E4%BB%A4%E7%89%8C%E4%BD%93%E7%B3%BB.md) | 能抑制卡片套卡片的视觉噪声 | 修订为“一层主要分组边界”；保留必要编辑字段、预览边界和焦点 |
| 动态数字等宽、长路径安全换行：[v1 设计令牌手册](https://github.com/Caho1/open-claude-ui/blob/c1f923ae0051a871941b98a0e2e3183a545e6a85/docs/v1/01-%E8%AE%BE%E8%AE%A1%E5%93%B2%E5%AD%A6%E4%B8%8E%E8%AE%BE%E8%AE%A1%E4%BB%A4%E7%89%8C%E4%BD%93%E7%B3%BB.md) | 减少计数跳动和长串撑破布局 | 采纳；时长/计数用 tabular-nums，真实路径仍可完整查看 |
| 角色化控件尺寸和密度：[v2 对比手册](https://github.com/Caho1/open-claude-ui/blob/c1f923ae0051a871941b98a0e2e3183a545e6a85/docs/v2/03-%E6%9E%B6%E6%9E%84%E9%87%8D%E6%9E%84%E4%B8%8E%E5%AF%B9%E6%AF%94%E5%88%86%E6%9E%90.md) | 同类组件在不同空间内保持关系 | 采纳密度概念；使用 Peer 8/12/16 连续曲线，不照搬 18/20 px 历史参数 |
| 按压和弹簧预设：[ClaudeMotionPresets.ts](https://github.com/Caho1/open-claude-ui/blob/c1f923ae0051a871941b98a0e2e3183a545e6a85/code-examples/ClaudeMotionPresets.ts)、[v2 底座手册](https://github.com/Caho1/open-claude-ui/blob/c1f923ae0051a871941b98a0e2e3183a545e6a85/docs/v2/04-%E7%B3%BB%E7%BB%9F%E5%BA%95%E5%BA%A7%E5%85%A8%E6%99%AF%E8%A7%A3%E5%AF%86.md) | 反馈与手势可以集中调校 | 采纳语义集中；保留现有 CSS 基元，不直接引入 Framer Motion 或物理常数 |
| 富输入的 composition 与补全优先级：[RichComposerWithMentions.tsx](https://github.com/Caho1/open-claude-ui/blob/c1f923ae0051a871941b98a0e2e3183a545e6a85/code-examples/RichComposerWithMentions.tsx) | 选择输入法候选不能触发发送 | 采纳防误发不变量；尾随键处理按引擎与事件证据适配，不全局硬吞 500 ms |
| 跟随最新与用户滚动分开：[useClaudeScrollPinning.ts](https://github.com/Caho1/open-claude-ui/blob/c1f923ae0051a871941b98a0e2e3183a545e6a85/code-examples/useClaudeScrollPinning.ts) | 阅读历史不应被新内容抢走 | 采纳用户视口主权；复用 Peer 已有 scroll policy/scheduler，拒绝只靠计时器恢复贴底 |
| 边缘非线性渐隐：[ScrollFadeContainer.tsx](https://github.com/Caho1/open-claude-ui/blob/c1f923ae0051a871941b98a0e2e3183a545e6a85/code-examples/ScrollFadeContainer.tsx) | 可以轻量提示仍有滚动内容 | 可选增强；触边取消遮罩，不遮焦点或关键操作，不当必选装饰 |
| 指针死区与缩放锚点：[MediaLightboxViewer.tsx](https://github.com/Caho1/open-claude-ui/blob/c1f923ae0051a871941b98a0e2e3183a545e6a85/code-examples/MediaLightboxViewer.tsx) | 区分点击/拖动，放大时保留用户关注点 | 采纳行为；包含取消、复原、键盘与减少动效路径 |
| 分栏与 iframe 交界：[ArtifactsSplitPaneResizer.tsx](https://github.com/Caho1/open-claude-ui/blob/c1f923ae0051a871941b98a0e2e3183a545e6a85/code-examples/ArtifactsSplitPaneResizer.tsx) | 跨嵌入表面不能丢失拖动控制 | 采纳问题意识；不直接复制示例护盾，窄窗有单栏/覆盖降级 |
| tabs 与 roving focus：[SegmentedControl.tsx](https://github.com/Caho1/open-claude-ui/blob/c1f923ae0051a871941b98a0e2e3183a545e6a85/code-examples/SegmentedControl.tsx)、[useClaudeRovingFocus.ts](https://github.com/Caho1/open-claude-ui/blob/c1f923ae0051a871941b98a0e2e3183a545e6a85/code-examples/useClaudeRovingFocus.ts) | 同组选择不应造成大量 Tab 停靠点 | 采纳模式；按真实 tabs/radio 语义补齐关系与键盘，不只写 role |
| 附件预览、扩展名保留：[AttachmentCard.tsx](https://github.com/Caho1/open-claude-ui/blob/c1f923ae0051a871941b98a0e2e3183a545e6a85/code-examples/AttachmentCard.tsx) | 内容对象可辨且可移除 | 采纳对象可读性；接收/准入状态来自真实链路，不模拟上传完成 |
| 容器尺寸驱动布局：[ContainerResponsiveBar.tsx](https://github.com/Caho1/open-claude-ui/blob/c1f923ae0051a871941b98a0e2e3183a545e6a85/code-examples/ContainerResponsiveBar.tsx) | 抽屉、侧栏压缩后比窗口断点更真实 | 采纳；优先保住主要操作、作用范围和恢复入口 |
| 决策卡把入参与动作放在一起：[McpToolDecisionCard.tsx](https://github.com/Caho1/open-claude-ui/blob/c1f923ae0051a871941b98a0e2e3183a545e6a85/code-examples/McpToolDecisionCard.tsx) | 用户需要理解将批准什么 | 采纳表达结构；权限/执行/结果全部来自现有 Runtime 契约 |
| 队列恢复叙事：[v2 新增特性手册](https://github.com/Caho1/open-claude-ui/blob/c1f923ae0051a871941b98a0e2e3183a545e6a85/docs/v2/02-%E6%96%B0%E5%A2%9E%E7%89%B9%E6%80%A7%E6%B7%B1%E5%BA%A6%E9%80%86%E5%90%91.md) | 用户工程输入本身就是劳动成果 | 采纳“不无声丢失、可重试、不可重复执行”；不照搬 renderer IndexedDB 存储边界 |
| 限流倒计时：[useRateLimitBackoff.ts](https://github.com/Caho1/open-claude-ui/blob/c1f923ae0051a871941b98a0e2e3183a545e6a85/code-examples/useRateLimitBackoff.ts) | 等待有原因且知道下一步 | 仅采纳展示；重试由 Provider/Runtime 决定，副作用不得由 UI timer 重放 |

## 4. 必须辨别的说明与实现偏差

### 4.1 弹簧标签不是可靠的迁移单位

[v1 动效手册](https://github.com/Caho1/open-claude-ui/blob/c1f923ae0051a871941b98a0e2e3183a545e6a85/docs/v1/04-%E5%8A%A8%E6%95%88%E7%89%A9%E7%90%86%E5%AD%A6%E3%80%81%E7%9D%80%E8%89%B2%E5%99%A8%E4%B8%8E%E7%8E%AF%E5%A2%83%E5%85%89%E5%BD%B1.md)仍把 `380/18` 与 `duration .32 / bounce .15` 并列呈现；[ClaudeMotionPresets.ts](https://github.com/Caho1/open-claude-ui/blob/c1f923ae0051a871941b98a0e2e3183a545e6a85/code-examples/ClaudeMotionPresets.ts)已经明确 `380/18` 是该项目自建预设，不是客户端观测值，两种形式也不等价。同一源码还把 `320/28` 的来源用途说明为松手后回弹，文档却把它泛化成卡片入场。

**结论：** 参数必须带机制、用途、依赖和来源。Peer 不采用“四套物理参数适配所有组件”的规则，也不把缓动曲线的控制点数值直接解释为相同百分比的视觉过冲。

### 4.2 “生产级”标签不能替代事实链

[McpToolDecisionCard.tsx](https://github.com/Caho1/open-claude-ui/blob/c1f923ae0051a871941b98a0e2e3183a545e6a85/code-examples/McpToolDecisionCard.tsx)在 renderer 内使用 `setTimeout(..., 1200)` 自动转 success，缺输出时显示成功默认文本；这属于演示状态，不能接入 Peer 的真实权限/执行链。[ChatComposer.tsx](https://github.com/Caho1/open-claude-ui/blob/c1f923ae0051a871941b98a0e2e3183a545e6a85/code-examples/ChatComposer.tsx)的添加附件也包含模拟入口，不能证明文件已经被读取或送到模型。

**结论：** 可以借鉴布局，不能继承这些行为。界面本地 timer、用户点击、助手文本都不能成为 Tool Result 或 Evidence。

### 4.3 无障碍需要行为实现

[ConfirmationDialog.tsx](https://github.com/Caho1/open-claude-ui/blob/c1f923ae0051a871941b98a0e2e3183a545e6a85/code-examples/ConfirmationDialog.tsx)声明焦点锁定，但组件本身只见 Escape/遮罩关闭，未见完整 Tab 限制、初始焦点、恢复焦点和标题关联实现；[SegmentedControl.tsx](https://github.com/Caho1/open-claude-ui/blob/c1f923ae0051a871941b98a0e2e3183a545e6a85/code-examples/SegmentedControl.tsx)有 tablist/tab 角色，却未完成对应方向键行为。[ThinkingAccordion.tsx](https://github.com/Caho1/open-claude-ui/blob/c1f923ae0051a871941b98a0e2e3183a545e6a85/code-examples/ThinkingAccordion.tsx)用可点击 div 承载折叠，生成时强制展开。

**结论：** role 和注释不证明可访问性。Peer 使用已有 focus scope 与共享组件，并以 W3C 模式约束行为；过程能持续生成，也仍应允许用户收起。

### 4.4 手势护盾与终止路径要看代码

[ArtifactsSplitPaneResizer.tsx](https://github.com/Caho1/open-claude-ui/blob/c1f923ae0051a871941b98a0e2e3183a545e6a85/code-examples/ArtifactsSplitPaneResizer.tsx)注释宣称 4 px 死区，实际 pointer move 中未见死区判断；其透明盖层带 `pointer-events:none`，不能仅靠这层拦住 iframe 的指针接管。与之相比，[MediaLightboxViewer.tsx](https://github.com/Caho1/open-claude-ui/blob/c1f923ae0051a871941b98a0e2e3183a545e6a85/code-examples/MediaLightboxViewer.tsx)实际包含 4 px 判断及 pointercancel 路径，说明相同宣传标签之下也需逐模块核对。

**结论：** 以真实事件路径判断能力，不能把 ARIA 标签、注释或透明元素当成已实现防护。

### 4.5 性能与安全不从动效代码推导

CSS 动画仍可能 layout/paint；grid 高度过渡、动态阴影和 blur 不能一概叫“零主线程”“GPU 保证 120 Hz”。[useRateLimitBackoff.ts](https://github.com/Caho1/open-claude-ui/blob/c1f923ae0051a871941b98a0e2e3183a545e6a85/code-examples/useRateLimitBackoff.ts)的重试循环和 [EpitaxyIframeBridge.tsx](https://github.com/Caho1/open-claude-ui/blob/c1f923ae0051a871941b98a0e2e3183a545e6a85/code-examples/EpitaxyIframeBridge.tsx)的历史用户激活判断，也不能替代 Peer 的执行授权与幂等链路。

**结论：** 采用能力检测、清理和降级思路；性能结论须实测，沙箱与用户手势不能自动授予本机能力。

## 5. Peer 的独特规范是什么

| 层 | Peer 的选择 | 用户得到什么 |
|---|---|---|
| 视觉 | 冷灰纸面、石墨操作、冰湖青印记、连续曲线 | 长时间工作稳定、清楚、有统一识别度 |
| 动效 | 120/200/320 ms 语义阶梯，小范围反馈、对象连续交接 | 看懂变化，不需要追逐界面 |
| 交互 | 输入、焦点、视口由人掌握；代理持续推进 | 可以离开，也可以随时回来介入 |
| 信任 | 行动权、授权与结果绑定本机事实；证据按需展开 | 少怀疑、少盯守，判断有依据 |
| 恢复 | 保住草稿、未决决定与现场；重试不重复副作用 | 中断后可以继续工作 |
| 工程 | 一套 token、共享组件、集中动效、既有 reducer/Runtime seam | 后续开发不必每次凭局部感觉重新发明 |

这是从上游吸收方法、结合 Peer 已批准方向后的原创取舍。没有新增 npm 依赖，也没有把上游组件直接 vendoring 进代码仓。

## 6. 可复核材料与许可

上表链接全部固定到本次 commit。后续复读其他版本时，另记 commit、差异与结论，不静默用 main 的新内容覆盖本次依据。[Agent 开发指南](https://github.com/Caho1/open-claude-ui/blob/c1f923ae0051a871941b98a0e2e3183a545e6a85/docs/v1/08-AI-Agent-%E5%89%8D%E7%AB%AF-UI-%E4%B8%8E%E5%8A%A8%E6%95%88%E5%BC%80%E5%8F%91%E6%8C%87%E5%8D%97.md)适合参考“给开发 Agent 明确规则”的写法，其命令与角色指令不在本任务执行。

该快照采用 [MIT License](https://github.com/Caho1/open-claude-ui/blob/c1f923ae0051a871941b98a0e2e3183a545e6a85/LICENSE)。本次是来源分析和规范转化，未复制其专有字体、音效或品牌资产。将来若复用上游代码或实质内容，须保留其 MIT copyright/license，并单独登记依赖、来源与适用范围；代码审查仍必需。

补充一手规范：W3C 的 [Dialog](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/)、[Tabs](https://www.w3.org/WAI/ARIA/apg/patterns/tabs/)、[指针目标](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html)、[状态消息](https://www.w3.org/WAI/WCAG22/Understanding/status-messages.html)、[文字对比度](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html)、[非文字对比度](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html)、[文字放大](https://www.w3.org/WAI/WCAG22/Understanding/resize-text.html)。它们用于补足可用性依据；本次没有据此宣称 Peer 已全面符合 WCAG。

本机对照代码快照：Peer-Agent `cb2f5695ea164fec7a291570c27c640217c98f1b`；Frost token、motion、focus scope、SettingsGroup、BotComposer 与 scroll policy/scheduler 均已阅读。记录的是源码观察，不是运行回归结论。
