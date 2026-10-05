# Peer Frost · 生产界面落地核验

创建时间：2026-10-05
最后更新：2026-10-05

负责人已认可[统一 Demo](peer-frost-unified-design.md)，并明确要求落地。本报告只证明本次界面迁移、受控事实链与列出的原生交互通过，不将产品整体标为 Ready，不改变正式版发布门槛。

## 1. 版本与边界

- 代码 PR：[Peer-Agent #121](https://github.com/ly-ccx/Peer-Agent/pull/121)。界面提交 `2160ece1e770a1117e1c7a1c545a0a5ee11c94b6`；窗口验收同步提交 `10c943d1f98271e1a42849013bbd2d8e59aa2955`。
- C 级：共享 SettingsGroup、呈现样式、局部排版与文案。模型目录、强度滑块、保存接口、流式投影、附件能力、协议、权限、Evidence、System Context 和存储边界沿用既有实现。
- 本机原生 Electron 验收窗口加载生产 renderer 构建，无 CSS overlay。隔离数据、项目和 Chromium profile；受控 Provider 只替换认知输入输出。未替换用户安装应用、未迁移用户数据、未发布新 RC。
- 受控 Provider 经真实宿主、队列、角色路由和流式投影到达界面；实际请求日志确认模型 ID、effort、文本附件和图片内容。它不能证明真实订阅模型推理质量、视觉理解或生产网络重试。

## 2. 比较与归一化

源为负责人已认可的 Demo 截图和原始「全局快捷键」参考。源截图为 1×；原生截图 2560×1720 px 对应 1280×860 CSS px，2080×1520 对应 1040×760，均按 DPR 2 下采样到 1 CSS px。没有拉伸字形或独立放大控件。

同输入比较已实际打开检查：

| 比较 | 证据与状态 |
| --- | --- |
| 全页结构 | [源与正式页](assets/peer-frost-production/37-full-view-source-production.jpg)：浅色、标准字号、通用页；源 1264×724，正式 1280×860。外部 Demo 工具条和原生窗口外壳不同，不能以空白高度判断漂移。 |
| 分组细节 | [通用分组](assets/peer-frost-production/31-general-source-production.jpg)：源区域 901×319，正式 912×320，均为 1 CSS px；标题带、行、字重、右列与箭头可直接比较。 |
| 快捷键 | [修正前](assets/peer-frost-production/32-shortcut-source-production.jpg) → [修正后](assets/peer-frost-production/36-shortcuts-source-production-final.jpg)：同为浅色、标准字号、默认可用状态；源分组宽 764，正式 912，差别来自容器宽度。保持相同文字和控件尺度，未把不同宽度强行缩成一样。 |
| 详情 | [分段与模型组](assets/peer-frost-production/33-drawer-source-production.jpg)：源 390 px 抽屉、正式 414 px；源为示例模型与下拉档位，正式保留真实目录与强度滑块，额外高级角色折叠和已选过程。比较共同部件关系。 |

生产保留完整设置导航和既有语义：如“界面”仍说明立即切换；未知类型的回复来源仍使用“回复”标签，不能全部硬编码为“你”。实际模型值、强度文字和高级角色随能力目录变化。以上为有意适配，不声称逐像素或逐字复刻演示数据。

## 3. 发现与修复

没有发现本轮 P0/P1。以下 P2 发现时为 blocked，修正后重新捕获和比较；旧截图保留历史。

| 问题 | 修复 | 修正后证据 |
| --- | --- | --- |
| 外观缩略图在宽窗过高 | 限制为 92 px，保持实际 ThemeModeCards 内容 | [外观页](assets/peer-frost-production/16-appearance-final.jpg) |
| 开发者标题与说明同排，部分旧卡片缺少稳定组间距 | 页面 flex 纵列、标题说明整行；保留诊断内容和动作 | [最终开发者页](assets/peer-frost-production/25-developer-production-final.jpg)；[早期画面](assets/peer-frost-production/21-developer-native.jpg) |
| 快捷键外层 gap 与旧 margin 叠加；录制框仍淡边框 | 移除额外 margin，录制框石墨细边框，键帽统一 14 px | [最终快捷键页](assets/peer-frost-production/34-shortcuts-border-final-1x.jpg)、[最后同输入对照](assets/peer-frost-production/36-shortcuts-source-production-final.jpg) |
| 停止消息转成系统卡片后失去机器人身份 | agent_stopped 继续显示 BotAvatar 与真实名称 | 最终重新打开对话，AX 同时含“代码维护”、原部分正文和“生成已停止，以上内容未完成”；[停止交互证据](assets/peer-frost-production/09-stopped-native.jpg)为身份补修前画面，不能拿它证明补修后的头像。 |
| 抽屉分段与共享分组表面不一致 | 统一轨道、纸面选中块、细边界与密度 | [浅色详情](assets/peer-frost-production/28-chat-drawer-production-final-1x.jpg)、[窄窗深色大字号](assets/peer-frost-production/30-chat-narrow-dark-large-final-1x.jpg) |

最后快捷键修订重新 build，重启原生验收应用，再捕获相同 1280×860、浅色标准字号状态；不使用 HMR 前旧画面作最终证据。当前未留待修的本轮 P0/P1/P2。

## 4. 五项视觉检查

| 表面 | 结论 |
| --- | --- |
| 字体 | 复用现有系统 sans / PingFang 回退；页面 30 px / 600，组标题 15 px / 400，标签 14 px / 600，说明 13 px / 1.6，元信息 11–12 px。中文、数字与模型名称检查；大字号输入正文随 rem 放大。未宣称下载或识别出来源字体。 |
| 间距 | 12 px 分组圆角、单层细边界、标题带与正文；组间 24 px；选择器 38 px、详情 35 px、强度列 80 px；caret 固定右端。1040 px 通用行上下排列，模型角色两列，无可见横向溢出。 |
| 颜色 | 复用 Frost 冷纸/石墨 token，浅深色同步；Switch 40×23、圆点 15，关闭也可见。普通内容组、消息和弱操作无外发光。原生截图中的紫色 macOS 检查标记及鼠标指示圈不属于产品样式。 |
| 资产 | 复用现有产品 logo、BotAvatar 和 PeerIcon，没有生成替代品牌素材、新增图标依赖或栅格化界面。角色头像的既有品牌处理保留；不把它扩展到消息外框。 |
| 文案 | 简短主标签、次级说明和实际选值；移除个性化说明中的内部 System Context 术语。过程默认“发送回复 / 已发送”，技术详情按需展开。保留真实继承/不可用/禁用语义。 |

## 5. 原生交互核验

| 项目 | 实际结果与证据 |
| --- | --- |
| 模型和强度 | Bot 从 GPT 6.1 Sol 改为 GPT 6 Sol，强度 high；输入框同步，退出重启仍保留。受控执行请求收到 provider ID `719ff394-625d-484a-9ce8-0806c240962e` 和 `high`，其余角色仍继承；[模型控件](assets/peer-frost-production/07-bot-settings-latest.jpg)。 |
| 流式 | 原生 progress 分片更新同一条回复，有停止动作；[生成途中](assets/peer-frost-production/08-streaming-native.jpg)。没有改成一次性定时显示整段。 |
| 停止 | 实际点击停止，保留部分正文并标记未完成；输入框“停止后保留的草稿”保留。前两次验收内容已完成，未将其算为停止通过；受控分片延长到 1200 ms 后捕获真实停止。 |
| 选择回答 | 选项附在所属回复下方；发送自由输入后，旧选项与“需要你 1”立即收起，随后收到回复；[选项布局](assets/peer-frost-production/10-options-native.jpg)。 |
| 附件与粘贴 | 原生选择 PNG + Markdown，预览与移除入口可见，粘贴文本发送；实际请求含测试 Markdown 正文及一张图片的 image content；[输入预览](assets/peer-frost-production/11-attachments-native.jpg)。本轮未重新实机验证剪贴板图片粘贴和跨应用文件拖放，前一轮证据与自动回归范围另计。 |
| 引用与过程 | 点击引用定位对应用户消息，出现返回最新入口；[引用定位](assets/peer-frost-production/26-reply-jump-production.jpg)。查看过程显示可读动作，原始参数收在技术详情；[过程](assets/peer-frost-production/27-process-production-final.jpg)。 |
| 分段 | 点击概况再按 Right，选中和焦点进入任务；五个分段保持固定可达。拖动行为沿用前一轮已核验逻辑，本轮未增加新逻辑。 |
| 设置分区 | 通用、外观、个性化、快捷键、服务商、模型分工、使用统计、Git、开发者、远程、更新、归档全部实际打开；对应合法空态保留。假 Provider 没有真实凭证，全球模型分工呈未配置状态，不算真实服务商接入通过。 |
| 自适应 | 原生通过窗口角拖动到 1040×760；[通用深色大字号](assets/peer-frost-production/29-general-narrow-dark-large-final-1x.jpg)、[模型角色](assets/peer-frost-production/20-routing-roles-narrow.jpg)、[对话详情](assets/peer-frost-production/30-chat-narrow-dark-large-final-1x.jpg)。1280×860 浅色标准字号 [正式通用页](assets/peer-frost-production/35-general-delivery-1x.jpg)。 |

## 6. 自动检查与 CI

- Desktop 完整回归：5342 项，5337 通过、0 失败、0 取消、5 项既有跳过；i18n 命名空间额外 1 项通过。
- 工作区 `pnpm typecheck`、`pnpm architecture:check`、Desktop build、`git diff --check` 通过。完整回归后最后仅改录制框边框/键帽两条 CSS，重新 build 成功。
- 首轮新增页标题放入 LlmSettingsPanel 超出既有 2265 行门槛，已改为 SettingsPage 外部装配；隔离 7 项和完整 Desktop 回归通过，没有放宽行数门槛。
- 原生 smoke 更新对应批准设计的视觉断言：单个引用 SVG、27 px 弱操作、40×23 开关、15 px 圆点和当前 Frost 状态色。保留对比度、保存、键盘、隔离、模型与附件契约验收。
- 最终 CI：[37220072567](https://github.com/ly-ccx/Peer-Agent/actions/runs/37220072567)，源 `10c943d1`；Mac 与 Linux 的构建、类型、架构、完整测试及 Electron 窗口验收全部通过。两份窗口报告 `ok=true`、`pageErrors=[]`、`mainAuthorizationErrors=[]`，源码无脏改动。CI 检出合成合并提交 `fa162e65`，其父提交包含 `10c943d1`；[脱敏结果与检查清单](assets/peer-frost-production/production-ci-20261005.json)记录精确绑定。前一个 `2160ece1` run 被最终提交自动取消，不作为通过证据。

## 7. 负责人复核路线

在包含 PR121 的构建上复核；已安装 RC5 不包含本次提交。正式版的 195 项测试手册与复杂任务 Evidence 剩余项仍有效。

1. 通用页：比较标题带、标签/说明、右列和 caret；开安静时段，修改开始/结束；关掉后时间禁用。切分区再回来，检查实际选值。
2. 快捷键页：检查同一结构、录制键帽、可用状态与恢复默认；用键盘录制，再恢复。
3. 外观页：浅/深色、标准/大字号；缩到 1040 宽，检查长文案、模型角色、菜单和抽屉。
4. 机器人设置：对话模型与强度直接修改，核对输入区；检查执行/复核各自配置、继承来源和高级限制。
5. 对话：发送普通问题，观察同一条回复逐步增长；生成时输入草稿并停止，检查部分正文、未完成标记和草稿。
6. 选择题：分别点击选项和自由输入，检查原消息选项与需要你计数立即收起。
7. 引用：引用 Bot 原文发送，再点击引用定位；检查无左强调线、大胶囊和双向箭头，回执在用户正文下方。
8. 输入区：文字粘贴、图片粘贴、多选图片/文本、删除单个附件、只发附件；发送后检查原消息回显。
9. 查看过程：可读步骤默认可见，技术详情按需展开；键盘打开/关闭与焦点返回。
10. 设置剩余分区：检查服务商长模型名、模型分工无模型状态、统计空态、Git、远程关闭态、更新与归档；不因视觉迁移触发连接或执行能力。

真实模型质量、网络失败/重试、超大文件、跨应用拖放、全量读屏、所有平台安装及长时间使用不在本次原生受控通过范围。

final result: passed


## RC6 后续验收（2026-10-05）

负责人批准连续曲线与灰底方案，并要求测试发布RC6。当前正式组件的共同表面、状态、消息与模型细节及截图见[本轮QA](peer-frost-radius-rc6-design-qa.md)；旧PR121记录作为历史保留，最新发布绑定见[RC6交接](../../playbook/v0.1.0/rc6-candidate.md)。
