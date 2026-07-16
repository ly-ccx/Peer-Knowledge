# Peer Agent App 视觉精致度审计

> 创建时间：2026-07-06  
> 最后更新：2026-07-06  
> 状态：第一轮审计草案  
> 关联代码仓：`/Users/liangyin/Documents/DEV/github/peer_agent`  
> 证据目录：`design/audit/app-visual-refinement-2026-07/`

---

## 一、审计范围

本轮审计聚焦“整体 App 为什么不够精致”，不是单点改色或单个控件优化。

覆盖范围：

- 左侧 Sidebar：品牌区、项目/会话列表、账号区。
- 中间 Chat Surface：空状态、消息流、工具执行记录、Composer。
- 右侧 Workbench：Tab rail、文件树、文件预览、文档/源码/Diff 视图。
- 视觉系统：Peer Frost token、深浅主题、用户主题色兼容、图标/边框/圆角/字号。

不覆盖：

- 不做完整可用性测试。
- 不声明 WCAG 合规，只记录截图和 CSS 能支持的可见风险。
- 不评估业务功能正确性。

---

## 二、证据

截图均保存在 `design/audit/app-visual-refinement-2026-07/`。

| 步骤 | 截图 | 观察对象 | 健康度 |
|---|---|---|---|
| 1 | `01-file-tree-overall.png` | 三栏布局、Workbench 文件树、旧 Terminal 占位入口、Composer | 中等：结构接近目标，但视觉语言混杂 |
| 2 | `02-unrendered-document.png` | 旧文件内容源码视图 | 偏弱：文档没有渲染，像调试视图 |
| 3 | `03-rendered-document-reference.png` | 目标方向：文档渲染 + 文件树 | 较好：左文档右文件树的任务感更明确 |
| 4 | `04-code-preview-reference.png` | 目标方向：源码预览 + 文件树 | 较好：代码阅读和文件定位形成明确工作区 |

补充代码证据：

- `apps/desktop/renderer/src/styles/tokens.css`：已有 Peer Frost token、深色主题、Catppuccin palette 和兼容别名。
- `apps/desktop/renderer/src/styles/workbench.css`：Workbench 已有文件树、文档、源码、Diff 样式，但 token 和布局语义仍未完全收敛。
- `apps/desktop/renderer/src/chat/styles/sidebar.css`、`chat-surface.css`、`chat-composer.css`、`message.css`：主界面样式分散，存在 Vellum/Frost 历史语义混用。

截图限制：

- 截图来自本轮对话中的产品状态，其中 `01` 仍包含已移除的旧 Terminal 占位入口；该问题已在 `d5aed7a` 修正。
- 截图无法验证键盘焦点顺序、屏幕阅读器语义、动态 hover/focus、滚动性能和实际主题切换表现。

---

## 三、总体判断

Peer Agent 现在的问题不是“不好看”，而是**设计系统没有真正收敛到一个产品气质**。

当前界面同时出现了四种语言：

1. **Codex-like**：三栏桌面工作台、文件树、文档/代码预览。
2. **Electron 工具壳**：很多 1px 线、空状态、系统按钮。
3. **后台管理台**：设置页、能力面板、卡片/表单语言。
4. **历史 Vellum/Frost 混合**：注释和 token 已切 Frost，但局部 CSS 仍保留 Vellum 的“卷轴”“暖纸”语义和旧写法。

这会导致视觉上“不贵”的根因：

- 用户无法一眼判断哪里是导航、哪里是内容、哪里是工具。
- 字号、行高、圆角、边框、选中态没有形成一致节奏。
- 主题色和状态色有 token，但应用层仍有硬编码 fallback 和局部特殊值。
- 工具视图的密度更像 IDE，聊天视图更像文档流，设置页更像表单后台，三者没有中间层连接。

---

## 四、已有优势

### 4.1 产品骨架是对的

三栏结构合理：左侧承载会话与项目，中间承载任务对话，右侧承载工作台。这个方向比“聊天 + 工具弹窗”更适合 Agent 桌面产品。

### 4.2 Peer Frost token 有基础

`tokens.css` 已经有明确的 Chrome / Paper / Control / Graphite / Azure 分层，并且浅色、深色、Catppuccin 都有覆盖。问题不是没有设计系统，而是组件没有严格消费同一套设计系统。

### 4.3 Workbench 的方向已经接近正确形态

文档预览、源码预览、文件树、Diff 这几个模块在任务型产品里是高价值能力。相比单纯聊天气泡，它们更能体现“桌面 Agent 工作台”。

---

## 五、核心问题

### P0-1：产品气质没有一句话约束

现在设计文档里有 Peer Frost 的意象，但落到组件时还缺一句执行约束：

> Peer Agent 是“桌面 Agent 工作台”：安静、密集、克制、偏 IDE，但比 VS Code 更柔和。

这句话应该反向约束所有组件：

- 不做营销感 hero。
- 不做大面积卡片堆叠。
- 不用装饰性渐变和过强阴影。
- 内容区读起来像文档/代码工具。
- 控件区像 macOS 原生工具栏一样克制。

### P0-2：Chrome 层和 Content 层边界不够明确

规范里写了“Chrome 毛玻璃 + Content 实色”，但现状里 Sidebar、Chat、Workbench 的背景关系仍比较平：

- Sidebar 和 Workbench 视觉重量相近，容易抢中间任务流。
- 中间 Chat 的空状态过于空旷，和右侧密集工具区割裂。
- Workbench tab rail 和内容区的边界过硬，但层级又不够明确。

建议：

- Sidebar / Workbench 外壳统一为 Chrome 层。
- Chat message / 文档 / 代码 / tool evidence 统一为 Content 层。
- Composer 属于 Control 层，可以浮起，但不能比主内容更抢眼。

### P0-3：字号 scale 太碎

当前 CSS 中出现大量 `10.5px / 11px / 11.5px / 12px / 12.5px / 13px / 13.5px / 14px / 15px / 16px / 17px / 20px / 26px / 32px`。这会让界面看起来像多个时期拼起来。

建议收敛为任务型桌面 scale：

| 角色 | 建议 token | 用途 |
|---|---|---|
| Caption | 11px | 时间、弱 metadata、badge |
| Meta | 12px | 文件路径、状态说明、辅助按钮 |
| UI | 13px | 列表、tab、输入控件 |
| Body | 14px | 聊天正文、文档正文 |
| Body Large | 15px | 重要正文、空状态副标题 |
| Heading SM | 16px | panel 标题 |
| Heading MD | 20px | 文档 h2、设置页分组 |
| Heading LG | 26px | 文档 h1 |
| Empty/Hero | 30-32px | 真正空状态或首屏 |

落地方式：新增 `--font-size-*` 和 `--line-height-*` token，禁止组件继续写散落 magic number。

### P0-4：圆角和边框语言不稳定

当前同时有 `2 / 4 / 6 / 8 / 9 / 12 / 14 / 16 / 999`，还夹杂 Tailwind `rounded-[8px]`、`rounded-[12px]`。这不是致命问题，但会削弱“精致感”。

建议：

- `2px`：细小指示条，不用于容器。
- `4px`：代码 token、inline chip。
- `6px`：小按钮、segmented control、文件树选中框。
- `8px`：列表行 hover/selected、普通输入框。
- `12px`：Composer、Popover、主要 panel。
- `16px`：Modal / 空状态大容器上限。
- `999px`：只给 avatar、圆形 icon button、pill badge。

### P0-5：选中态不统一

截图里有几套不同选中态：

- Sidebar 会话选中是灰块。
- Workbench 文件树选中是亮蓝描边。
- Workbench tab 是灰底。
- Segmented control 是浮起白底/浅底。
- Quick appearance 是 primary 填充。

建议定义统一选中态层级：

| 场景 | 表达 |
|---|---|
| Navigation selected | 左侧 2px accent rail + `selected-bg` |
| Tree/file selected | `selected-bg` + 1px accent border，只在键盘焦点时显示强 outline |
| Segmented selected | content surface 填充 + 1px hairline，不用阴影 |
| Primary action | Graphite 填充，不用用户 accent |
| Focus visible | 单独 focus ring，不和 selected 混用 |

用户主题色只进入 `accent / selected-bg / focus-ring / link`，不进入 CTA 背景。

### P1-1：图标来源和 stroke 需要统一

历史上出现过 emoji 文件树，当前已经改掉，但整体仍有自绘 SVG、可能的 lucide、品牌图标和系统图标混用。自绘 SVG 如果 stroke、圆角、尺寸不同，会让精致度下降。

建议：

- 常规 UI 图标统一 lucide 或等价线性 icon set。
- 默认尺寸：sidebar 18px，toolbar 18px，dense list 16px。
- stroke：1.75 或 2 二选一，不能混。
- 文件类型图标不要彩色过多；Git 状态可以用文字/小符号，而不是每个文件都一个高饱和图标。

### P1-2：Chat 和 Workbench 的密度断层

截图中间 Chat 读取区留白大，右侧 Workbench 文件树密度高。用户在同一屏里会感到“左右两个产品”。

建议：

- Chat 主区缩小空状态装饰感，强化任务上下文。
- Workbench 继续保持 dense，但标题栏、文件树、文档正文需要与 Chat body 使用同一字号/行高逻辑。
- Tool card 和文件预览都应归入同一种“evidence surface”视觉语言。

### P1-3：文档渲染方向正确，但需要“阅读模式”和“工具模式”两档

`03` 的文档渲染明显比 `02` 的源码视图好，但文档字体和工具区文件树并排时容易过大。工作台里文档不是网页文章，而是“可扫读工程文档”。

建议：

- 文档正文默认 14px，行高 1.68。
- h1 不超过 26px，h2 20px，h3 16px。
- 代码块不使用过重卡片；更像编辑器 block。
- 长文档顶部提供 breadcrumb + 文件名，而不是只靠 tab label。

### P1-4：深色模式偏一色化

当前深色截图整体落在单一深蓝/Slate 族，符合 Frost 冷感但层次有点粘。精致感不是继续加颜色，而是拉开材质层：

- Chrome：更冷、更透明或更深。
- Content：略亮，便于阅读。
- Control：介于两者之间。
- Hairline：更低透明度，减少“到处都是线”的感觉。

建议加入 alpha token：

- `--border-subtle`
- `--border-strong`
- `--surface-hover-soft`
- `--surface-selected`
- `--surface-elevated`

而不是让所有组件直接用 `--za-line / --za-surface-*`。

### P1-5：硬编码颜色和旧命名会持续破坏主题兼容

代码里仍能看到：

- `#fff`
- `rgba(0,0,0,...)`
- `rgba(255,255,255,...)`
- `#1a7f37 / #cf222e`
- `--cinnabar-*` 兼容名
- `--azure-*` 直接落组件

其中一部分是 fallback，但它们会让用户主题色、Catppuccin、深色主题出现局部不协调。

建议：

- 新增 lint 或 `rg` 检查清单。
- 除 token 文件和图片遮罩外，组件层禁止新增 hex。
- `--cinnabar-*` 只保留兼容，不允许新代码引用。

---

## 六、用户主题色兼容策略

主题色不应该改变产品气质，只改变“印记”和“可定位性”。

建议 token：

```css
:root {
  --accent: var(--za-user-accent);
  --accent-hover: color-mix(in srgb, var(--accent) 86%, var(--za-text));
  --accent-soft: color-mix(in srgb, var(--accent) 14%, transparent);
  --accent-muted: color-mix(in srgb, var(--accent) 28%, var(--za-text-faint));
  --focus-ring: color-mix(in srgb, var(--accent) 34%, transparent);
  --selected-bg: color-mix(in srgb, var(--accent) 16%, transparent);
  --selected-border: color-mix(in srgb, var(--accent) 72%, var(--za-line));
}
```

使用规则：

- CTA：仍使用 graphite primary，不使用用户主题色。
- 链接 / focus / selected / active rail：使用用户主题色。
- 状态色：success/warn/danger 不跟随用户主题色。
- 大面积背景：不跟随用户主题色。
- 文件树选中、sidebar 当前会话、Workbench active tab：使用 `--selected-bg`，不要各自写 `color-mix`。

---

## 七、建议改造顺序

### Slice 1：Design Token 收敛

目标：先让后续改动有统一语言。

动作：

- 增加 typography token：`--text-caption / --text-meta / --text-ui / --text-body / --text-heading-*`。
- 增加 interaction token：`--surface-selected / --selected-border / --focus-ring / --border-subtle`。
- 增加 radius token：`--radius-control / --radius-row / --radius-panel / --radius-modal`。
- 写一份 `design/visual/peer-frost-component-rules.md`，明确组件使用规则。

验收：

- 新 UI 不再写散落字号。
- 组件层新增 hex 为 0。
- 选中态统一从 token 来。

### Slice 2：Workbench 精修

目标：右侧工作台先成为最精致的“工具面”。

动作：

- Workbench tab rail 缩短文字依赖，图标+tooltip 为主。
- Files tree 行高、选中态、folder/file icon、Git 状态统一。
- 文档预览顶部补 breadcrumb / file title / mode switch 的稳定结构。
- Source/Diff 行号槽、滚动条、选中行、空状态统一。

验收：

- 文件树不再像临时列表。
- 文档/源码/Diff 都像同一个工具系统。
- 用户主题色只改变选中/焦点，不改变内容阅读底色。

### Slice 3：Sidebar 精修

目标：让左栏像“任务索引”，不是普通会话列表。

动作：

- 统一项目、会话、置顶、归档、账号区的行高和选中态。
- 弱化过多边框，靠 indentation、spacing、section label 建层级。
- 当前会话使用 accent rail + selected background。
- 项目/工作区状态 chip 使用 mono caption，不抢会话标题。

验收：

- 30 秒内能扫出当前项目、当前会话、待处理项。
- hover/selected/focus 三种状态不混淆。

### Slice 4：Chat Surface 精修

目标：让主区成为“任务叙事流”，不是聊天气泡堆。

动作：

- 空状态缩小视觉重量，强调新任务入口。
- Assistant 消息、tool timeline、permission card、goal card 使用同一 evidence surface。
- Composer 变成稳定底部 control，而不是大灰盒。
- 消息操作条位置和出现方式统一。

验收：

- 同屏长对话时不显乱。
- 工具执行信息可以扫读，不打断主回复。

### Slice 5：Settings / Appearance 收尾

目标：避免设置页像另一套后台系统。

动作：

- 设置页 panel、form row、segmented、select、popover 复用同一 control token。
- Appearance 里的主题色预览展示真实影响范围：selected/focus/link，而不是让用户误以为能换整套皮肤。
- 增加主题 QA 表：light / dark / Catppuccin / custom accent。

验收：

- 设置页和主界面不割裂。
- 用户改主题色后不会破坏层级和可读性。

---

## 八、第一批代码任务建议

建议先拆成 4 个小 PR：

1. `design tokens: add interaction and typography aliases`
   - 只改 `tokens.css` 和文档。
   - 不改组件视觉。

2. `workbench: normalize selected/focus states`
   - 文件树、tab rail、segmented control、Diff/Source 状态统一。

3. `sidebar: refine conversation list density`
   - 当前会话、项目、置顶、账号区统一行高、选中态、section label。

4. `chat: align composer and evidence surfaces`
   - Composer、tool timeline、permission card、goal card 做同一套 surface 规则。

不要一次性“重做 UI”。这类产品如果一次改太大，很容易从“不够精致”变成“变了一个产品”。

---

## 九、最终目标状态

用户打开 App 时应该形成三个明确判断：

1. 左侧是任务索引：我在哪里、还有什么任务。
2. 中间是任务叙事：我和 Agent 正在推进什么。
3. 右侧是工作台：文件、Diff、文档、浏览器、证据都在这里验证。

视觉上应该做到：

- 冷、静、清晰。
- 少装饰，重秩序。
- 选中、焦点、状态都可预期。
- 主题色是印记，不是涂料。
- 看起来像一个成熟桌面工作台，而不是多个实验界面拼接。
