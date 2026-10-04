# Peer Frost · 统一交互 Demo 设计核验

创建时间：2026-10-04
最后更新：2026-10-05

这是独立前端原型的设计核验。通过表示已关闭本轮发现的 P0/P1/P2 视觉和交互问题，不表示负责人认可审美，也不表示生产应用或真实模型已验收。

## 比较对象与状态

- 视觉真源：[用户选中的全局快捷键截图](assets/peer-frost-unified-demo/source-original.png)。源图 1688×504 px，只覆盖一个设置分组，不覆盖整页导航或对话。
- 实现：本机 Vite 预览，Codex 内置浏览器实际渲染。
- 同状态区域：快捷键页、浅色、标准字号、快捷键 `⌘⇧N`、可用、恢复默认禁用。1128×724 CSS px 窗口下，分组宽 764 CSS px。
- 源区域：(61, 84) 至 (1588, 395)，1527×311 px。为比较字重、节奏和控件比例，归一化为 [764×156 px](assets/peer-frost-unified-demo/source-group-1x.png)。源图未提供 DPR 元数据；约 2 倍缩放是本次比较的选择，不能声称已验证源图的原生 DPR。
- 实现密度：浏览器截图 1 像素对应 1 CSS px。最终 [区域截图](assets/peer-frost-unified-demo/15-reference-matched-density.jpg) 为 764×159 px，DOM 高度约 159.9 CSS px。
- 全视图：源原图与 [快捷键页](assets/peer-frost-unified-demo/16-shortcuts-matched-viewport.jpg) 在同一次图像输入中打开比较；整页新增导航、页标题及应用内快捷键组，属于从单组参考扩展的设计，不声称整页逐像素复刻。
- 聚焦比较：源归一化区域与第 03、05、07、15 次区域截图在对应修订后放入同一次图像输入比较。交付前再将源原图、最终通用页、对话与详情、最终参考区域同时打开，检查扩展后的组件关系。

## 发现与修订历史

本轮未发现 P0/P1。下列 P2 均已修复；发现时的结果为 blocked，保留失败画面，不用后续截图覆盖历史。

| 轮次 / 严重度 | 位置与问题 | 具体修复 | 修订后的证据 |
| --- | --- | --- | --- |
| 1 / P2 | 分组标题过重、内容行过松；初次分组约 172 px 高，源归一化为 156 px | 组标题由 600 经 500 调整至 400；标题带 padding 18/23/16，内容行纵向 17 px，说明间距 4 px | [初次区域](assets/peer-frost-unified-demo/03-reference-group-initial.jpg) → [中间修订](assets/peer-frost-unified-demo/05-reference-group-final.jpg) → [精修](assets/peer-frost-unified-demo/07-reference-group-refined.jpg) → [同宽最终区域](assets/peer-frost-unified-demo/15-reference-matched-density.jpg) |
| 1 / P2 | 快捷键录制区 148×40 px，比源中紧凑的控件显得松散 | 改为 132×38 px，保持键帽和状态同一基线 | [初次页](assets/peer-frost-unified-demo/02-shortcuts.jpg) → [精修页](assets/peer-frost-unified-demo/08-shortcuts-refined.jpg) → [同宽最终页](assets/peer-frost-unified-demo/16-shortcuts-matched-viewport.jpg) |
| 1 / P2 | 推理强度窄字段中“极高”截断 | 收窄内部间距；全局强度列 90 px，详情强度列 80 px；箭头固定尾端 | [最终模型菜单](assets/peer-frost-unified-demo/25-bot-model-menu-final.jpg)、[最窄深色大字号](assets/peer-frost-unified-demo/31-bot-dark-large-fixed.jpg) |
| 2 / P2 | 标题带偏淡，接近内容底色，弱化了参考分组层次 | 标题带使用 `--paper-base`，正文继续 `--paper-sheet` | [早期区域](assets/peer-frost-unified-demo/05-reference-group-final.jpg) → [精修](assets/peer-frost-unified-demo/07-reference-group-refined.jpg) → [同宽最终](assets/peer-frost-unified-demo/15-reference-matched-density.jpg) |
| 2 / P2 | 模型来源与强度说明未共享列关系；页面多出约 4 px 外层滚动；拖动分段后焦点仍停在旧项 | 两行共用同一网格；应用高度扣除 Demo 外壳；拖动后焦点进入选中的分段 | [最终详情](assets/peer-frost-unified-demo/24-chat-drawer-final.jpg)、[窄窗](assets/peer-frost-unified-demo/30-built-in-narrow-final.jpg)；DOM 检查确认新选中项获得焦点 |
| 3 / P2 | 返回设置分区沿用旧 scrollTop，页标题被裁切 | 路由切换重置设置内容 scrollTop | [失败画面](assets/peer-frost-unified-demo/27-general-final.jpg) → [修正后通用页](assets/peer-frost-unified-demo/32-general-final-fixed.jpg)；scrollTop=0，页标题 y=95 |
| 3 / P2 | 390 px 深色大字号下，主导航按钮覆盖机器人详情标题 | 主导航 z-index=20；详情覆盖层 z-index=30 | [失败画面](assets/peer-frost-unified-demo/26-bot-dark-large-final.jpg) → [修正后](assets/peer-frost-unified-demo/31-bot-dark-large-fixed.jpg)；标题、关闭和五个分段完整可见 |

最终源分组与实现约 3–4 px 高度差、系统 sans 字体和语义绿的细微差别，是映射现有 Frost token 与字体环境的可接受适配。源图没有可识别的字体文件，不能宣称同一字体逐像素一致。当前无待修的 P0/P1/P2。

## 五项视觉检查

| 表面 | 检查与结论 |
| --- | --- |
| 字体与排版 | 使用 Inter / 系统 sans / PingFang SC 等回退，不额外加载来源不明字体；中文、英文、数字视觉检查通过。页面标题 30 px；组标题 15 px / 400；设置名称 14 px / 600；说明 13 px / 400，行高 1.6；元信息 11–12 px。较大字号下模型值、强度、来源说明可读。实际未证明 Inter 字体文件加载，也未做完整读屏验收。 |
| 间距与结构 | 参考同宽比较、全页与窄窗比较完成。组圆角 12 px、控件 8 px、单层 1 px 边界、组间 24 px；常规选择器高 38 px，caret 距右边界 13 px；详情使用相同部件的紧凑密度。长页正常纵向滚动，测试窗口无根节点横向溢出。 |
| 颜色与 token | 冷灰纸面、石墨主操作、少量冰湖青、语义绿。浅色正文/说明对纸面的计算对比度约 16.04/6.96，深色约 13.90/7.58；绿色状态约 4.74/5.92，并附“可用”文字。浅深色主题同步到 portal 菜单；普通设置组和消息没有外投影、发光、装饰强调线。 |
| 图片与图标 | 源分组无插画，不需生成或重画资产。品牌图复制正式产品 logo；机器人 SVG 导出既有 BotAvatar 路径；操作图标使用 Lucide。视觉检查比例、清晰度、透明边缘正常。未用 emoji、CSS 画图或自造 SVG 代替参考素材。 |
| 文案与内容 | 源分组标题、说明、动作、快捷键、状态保持；扩展页使用简短标签和二级说明。模型显示实际值，继承来源放在次级说明。过程使用可读步骤，没有 raw `post_reply` 或 JSON。Demo 工具条与 README 明确模拟边界。 |

## 浏览器交互检查

下列操作均在内置浏览器执行，未以脚本直接写 DOM 或 localStorage 代替用户操作。

| 范围 | 实际检查 |
| --- | --- |
| 选择器 | 点击开关、当前项勾选、模型渠道分组、搜索、无结果、Enter 选择、方向键、Escape 关闭、焦点返回、点击外部收起。 |
| 通用配置 | 改为工作台、开启安静时段、22→23；切换分区后保留；新鲜重载后仍保留。检查后通过界面恢复默认值。关闭时段时两个时间控件禁用。 |
| 快捷键 | 普通 a 显示需修饰键的错误；⌥⇧J 录入并反馈；恢复 ⌘⇧N。没有注册 OS 全局快捷键。 |
| 消息归属 | 用户右侧、Bot 左侧、回执在用户正文下方。点击选项后原消息选项收起；自由输入也清除原选项。 |
| 增量与停止 | 按预设分片追加到同一条 Bot 消息；一问一答消息数保持为 4；停止保留部分正文，显示已停止，不错误标为已回答；完成后回执变为已回答。 |
| 引用 | 草稿引用可取消；携带引用发送；Bot 引用使用原消息 ID 定位来源。没有左侧强调线和双向箭头。 |
| 模型与强度 | 全局改变后继承值显示实际模型；Bot 覆盖与恢复继承；输入框和详情同步；“极高”完整显示。消息过程保持该轮配置快照。 |
| 详情分段 | 点击、方向键、左右拖动；拖动后选中和焦点一致。概况、任务、目标、记忆、设置可进入，空状态有归属。 |
| 过程弹层 | 易读演示步骤，Tab 留在弹层，Escape 关闭、焦点回到来源按钮。 |
| 文字与附件 | 实际 Meta+V 粘贴文字；PNG 剪贴板粘贴；文件选择器选图及文本/图片混合；预览、移除、带附件发送。[发送后的原消息](assets/peer-frost-unified-demo/34-attachments-source-final.jpg) 包含 1 个文件和 1 张图片，选项为 0、总消息数为 4，引用定位可以返回这条原消息。剪贴板检查后恢复原值。使用无敏感信息的演示文件。 |
| 设置操作 | 名字空白时保存禁用；改名反映到侧栏；随后恢复。⌘K 聚焦设置搜索，筛选“模型”后只显示模型分工，清除恢复导航。 |

## 响应式与最终截图

| 尺寸 / 状态 | 证据 |
| --- | --- |
| 1264×724，浅色标准字号 | [通用最终](assets/peer-frost-unified-demo/32-general-final-fixed.jpg)、[通知与时间](assets/peer-frost-unified-demo/28-general-lower-final.jpg)、[对话与详情](assets/peer-frost-unified-demo/24-chat-drawer-final.jpg)、[模型菜单](assets/peer-frost-unified-demo/25-bot-model-menu-final.jpg)、[混合附件](assets/peer-frost-unified-demo/29-files-and-image-final.jpg) |
| 1128×724，源参考对照 | [快捷键整页](assets/peer-frost-unified-demo/16-shortcuts-matched-viewport.jpg)、[764 px 分组](assets/peer-frost-unified-demo/15-reference-matched-density.jpg) |
| 1024×860 | [通用](assets/peer-frost-unified-demo/17-general-1024.jpg) |
| 390×844，浅色标准字号 | [通用](assets/peer-frost-unified-demo/18-general-390.jpg) |
| 390×844，深色较大字号 | [外观](assets/peer-frost-unified-demo/19-dark-large-390.jpg)、[对话](assets/peer-frost-unified-demo/20-chat-390-dark-large.jpg)、[修正后的详情](assets/peer-frost-unified-demo/31-bot-dark-large-fixed.jpg) |
| 760 px 内置窄窗 | [自适应设置](assets/peer-frost-unified-demo/30-built-in-narrow-final.jpg) |

源只给出浅色单分组；深色、窄窗、消息、菜单属于沿共同部件扩展后的补充检查，不能当作源设计逐像素保真结果。代码支持减少动效/透明度偏好，本轮没有完整 OS 偏好组合验收。

## 构建、日志与版本绑定

- 最终 `npm run build` 成功。未请求 Sites 发布，未执行发布专用 gate，也未生成远程分享链接。
- 编辑期间一次 HMR 报告 Effect 依赖数组大小变化；这是编辑态日志。最终源码重载后的 error/warn 检查为空，记录见 [fresh-console.json](assets/peer-frost-unified-demo/fresh-console.json)，reloadTime 为 `2026-10-04T15:48:31.199Z`。不宣称开发全过程零日志。
- [final-metrics.json](assets/peer-frost-unified-demo/final-metrics.json) 记录 1264×724、浅色标准字号、按钮高度、箭头右间距和未截断选值。
- 最终源码 SHA-256：
  - `src/App.jsx`：`2d3f002f367236cc4c92113fa9d5e59409efb3d56882755adf90d34c7fc08655`
  - `src/styles.css`：`e3c43105c5f972f62a32d5c71ab091928f89e6e34c55d865ec62981537f2bbfb`
  - `package-lock.json`：`d89d2165060502d9b7c77f91393061a5d49999be036d433c1760f2b806d87160`

## 实施清单与剩余范围

- [x] 参考区域归一化并同输入比较，保留修订历史。
- [x] 统一 Group / Row / Select / Switch / TimeControl / 操作层级，浅深色和窄窗验证。
- [x] 核验普通消息、引用、选择回答、增量、停止、模型、附件和键盘操作。
- [x] 构建成功；最后修正后的标题与覆盖层画面复查；新鲜载入控制台无 error/warn。
- [ ] 等待负责人审美评审；后续正式 renderer 组件落地和逐页迁移尚未进行。
- [ ] 服务商、Git、远程访问、使用统计等正式页面未逐页复刻。
- [ ] 真实 provider 流式传输、完整 Markdown、网络故障/重试、跨应用文件拖放、超大附件、完整读屏、长时间使用、原生快捷键与发版升级均不在这个前端 Demo 的通过范围。

模型回复为预设内容分片，过程为演示数据。只在本地预览域名保存演示全局配置；Bot 设置与消息只保留本次页面会话。语言选择展示状态，预览仍使用中文；新增/第二机器人为导航示例。没有更改生产设置，没有合并代码 PR，没有发布 RC。

final result: passed
