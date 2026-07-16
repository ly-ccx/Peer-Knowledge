# Workbench 文件预览与文档渲染技术方案

创建时间：2026-07-05
最后更新：2026-07-05

## 状态

技术方案草案，待在代码仓 `peer_agent` 落地。

关联代码仓：

- `apps/desktop/renderer/src/workbench/views/DiffView.tsx`
- `apps/desktop/renderer/src/workbench/views/FilesView.tsx`
- `apps/desktop/renderer/src/workbench/WorkbenchContext.tsx`
- `apps/desktop/renderer/src/chat/components/markdown/*`
- `apps/desktop/renderer/src/chat/styles/markdown.css`
- `apps/desktop/electron/main/main.mjs` 的 `workbench:read-file` / `workbench:git-diff` / `workbench:read-dir` IPC

## 一、背景

当前 Workbench 的文件查看链路把所有文件都落到 `DiffView`：

```text
FilesView 点击文件
  -> openDiff(absPath)
  -> DiffView
     -> Diff / 文件内容 两段切换
     -> 文件内容用 <pre><code> 原文逐行渲染
```

这个实现适合审查代码 diff，但不适合阅读文档。Markdown 文件会以源码形式展示，标题、列表、表格、代码块、引用都没有被渲染，和 Codex.app 的文件阅读体验有明显差距。

问题本质不是“Markdown 缺一个 parser”，而是 Workbench 缺一个独立的 **File Preview / Document Preview** 概念。Diff、源码、文档阅读三种任务被塞进同一个 `DiffView`，导致入口语义和渲染策略都不清晰。

## 二、目标

1. 点击文件时默认进入适合该文件类型的阅读视图，而不是一律进入 diff。
2. Markdown 文档默认渲染为可读文档，支持常见格式。
3. 代码文件默认以源码视图展示，保留行号和基础语法可读性。
4. 有未提交改动时仍能进入 Diff 视图审查变更。
5. 所有渲染结果必须兼容用户主题、暗色/亮色、未来自定义主题。
6. 不执行文件内的脚本或 HTML，不把本地文件预览变成安全风险。

## 三、非目标

- 不在本期实现文件编辑器。
- 不在本期实现完整 IDE 级语法服务、跳转定义、诊断提示。
- 不在本期内嵌 Office 文档编辑或高保真预览。
- 不在本期支持 Markdown raw HTML 执行。
- 不在本期支持 Mermaid / HTML iframe / 任意嵌入脚本。

## 四、产品语义

Workbench 的文件视图拆成三个用户可理解的模式：

```text
Preview  阅读渲染后的文件
Source   查看原始源码/文本
Diff     查看 git 变更
```

### 4.1 默认打开策略

| 文件类型 | 默认模式 | 说明 |
| --- | --- | --- |
| `.md` / `.markdown` | Preview | 渲染 Markdown 文档 |
| `.txt` / `.log` | Source | 保留原文换行 |
| `.json` | Preview | 格式化 JSON，失败则 Source |
| `.yaml` / `.yml` | Source | M1 先按源码，M2 可加结构预览 |
| 代码文件 | Source | 行号 + 语法高亮 |
| 图片 | Preview | 图片预览 + 文件信息 |
| CSV / TSV | Source | M2 再做表格预览 |
| 二进制 / 超大文件 | Preview fallback | 显示不可预览说明 + 外部打开 |

### 4.2 Diff 的入口语义

Diff 不再是“点击文件”的默认含义，而是一个审改模式：

- 文件有 git 改动时，顶部显示 Diff 可用状态。
- 用户可手动切到 Diff。
- 从聊天消息中的“改动文件 / patch / diff artifact”进入时，可以直接打开 Diff。
- Source / Preview 不应该因为无 diff 而显示“没有未提交改动”作为主体内容。

## 五、信息架构

新增概念：

```text
FileTarget
  absPath
  workspaceRoot?
  relPath?
  preferredMode?

FilePreviewView
  header
  mode switcher: Preview / Source / Diff
  content slot

PreviewRenderer
  MarkdownDocument
  JsonDocument
  ImagePreview
  FallbackPreview

SourceViewer
  line-numbered source
  optional syntax highlight

DiffViewer
  existing unified diff renderer
```

### 5.1 WorkbenchContext 调整

现有 `diffTarget` 只表达“要看 diff 的文件”。应新增或改名为更通用的 `fileTarget`。

推荐迁移：

```ts
export interface WorkbenchFileTarget {
  readonly absPath: string;
  readonly workspaceRoot?: string;
  readonly relPath?: string;
  readonly preferredMode?: 'preview' | 'source' | 'diff';
}
```

保留兼容方法：

```ts
openFile(absPath, workspaceRoot?, relPath?, options?)
openDiff(absPath, workspaceRoot?, relPath?)
```

其中 `openDiff()` 内部等价于：

```ts
openFile(absPath, workspaceRoot, relPath, { preferredMode: 'diff' })
```

### 5.2 FilesView 行为

`FilesView` 点击文件不再调用 `openDiff(entry.absPath)`，改为调用：

```ts
openFile(entry.absPath, workspacePath ?? undefined)
```

目录仍然展开/收起。文件树本身不承担“判断该文件是不是文档”的责任，判断放在 FilePreviewView。

## 六、渲染架构

### 6.1 组件拆分

```text
workbench/views/FilePreviewView.tsx
  - 读取 fileTarget
  - 负责 header、模式切换、刷新、外部打开
  - 管理 content/diff 加载状态
  - 根据 file type 选择 renderer

workbench/file-preview/fileTypes.ts
  - detectFileKind(fileName, contentResult)
  - detectPreferredMode(fileKind, target.preferredMode)

workbench/file-preview/MarkdownDocument.tsx
  - 文档级 Markdown 渲染
  - 不复用聊天气泡尺寸逻辑

workbench/file-preview/SourceViewer.tsx
  - 行号、横向滚动、源码展示
  - M2 接语法高亮

workbench/file-preview/DiffViewer.tsx
  - 从 DiffView 抽出现有 unified diff 解析与渲染

workbench/file-preview/ImagePreview.tsx
  - 图片预览

workbench/file-preview/FallbackPreview.tsx
  - binary/too_large/error 状态
```

### 6.2 复用现有 Markdown 能力的方式

当前聊天消息已有：

- `MarkdownMessage.tsx`
- `markdownParser.ts`
- `InlineMarkdown.tsx`
- `markdown.css`

不能直接把 `MarkdownMessage` 原样用于文件预览，原因：

- 聊天气泡里 `#` 标题被降级为 `h3`，文档阅读需要保留 h1/h2 层级。
- 聊天代码块最大高度有限，文档代码块不应该默认被 260px 截断。
- 聊天内联文件路径会接入 Workbench 路径行为，文档内链接需要更明确的本地/外链处理策略。

推荐做法：

1. 抽出 parser 与 inline renderer 的可复用核心；
2. 新增 `MarkdownDocument` 做文档级 block rendering；
3. 新增 `.workbench-document` 样式，不污染聊天消息样式。

## 七、Markdown 支持范围

M1 支持：

- h1-h6 标题；
- 段落；
- 无序 / 有序列表；
- 引用；
- 分割线；
- 表格；
- fenced code block；
- inline code；
- strong / emphasis；
- 外部链接；
- 本地相对路径链接。

M1 不支持：

- raw HTML；
- script；
- iframe；
- Mermaid；
- 自定义组件；
- 远程图片自动加载。

### 7.1 链接处理

Markdown 链接分三类：

| 类型 | 行为 |
| --- | --- |
| `https://...` | 通过系统浏览器打开 |
| `./relative.md` / `../file.ts` | 解析到 workspace 内，调用 `openFile` |
| `#heading` | 当前文档内锚点滚动 |

安全要求：

- 相对路径必须解析后仍在 workspaceRoot 内；
- 不允许 `javascript:` / `data:` 链接执行；
- 不自动加载远程图片，除非后续引入明确的远程内容授权。

## 八、Source Viewer

Source Viewer 是所有文本文件的兜底视图。

M1 行为：

- 行号 gutter；
- 横向滚动；
- 保留空格和 tab；
- 当前选中文件名和路径；
- 复制全部；
- 外部打开。

M2 行为：

- 语法高亮；
- 当前行 hover；
- 搜索高亮；
- 大文件虚拟滚动。

### 8.1 语法高亮选型

推荐路线：

```text
M1: 无依赖 SourceViewer，先解决阅读模式与 Markdown 渲染
M2: 引入 Shiki，懒加载高亮器和语言包
```

选择 Shiki 的原因：

- 质感接近 VS Code / Codex；
- token scope 稳定；
- 适合静态文件预览；
- 可以按需加载语言，避免首屏包体膨胀。

风险：

- wasm / grammar 初始化有异步成本；
- 需要为主题色映射做一层适配；
- 对超大文件需要降级到 plain source。

降级规则：

- 文件超过阈值（建议 300KB）禁用高亮；
- 高亮初始化失败时显示 plain source；
- 未识别语言显示 plain source。

## 九、主题色兼容

这是本方案的核心约束之一。

### 9.1 原则

文档渲染必须接入应用语义 token，而不是自带一套固定颜色。

```text
文档排版：语义色
交互状态：accent 色
代码高亮：syntax token
```

### 9.2 文档排版 token

Markdown 正文、标题、列表、表格、引用只使用现有语义 token：

```css
--za-text
--za-text-soft
--za-text-muted
--za-text-faint
--za-bg-0
--za-bg-1
--za-surface-0
--za-surface-1
--za-surface-2
--za-line
--za-line-strong
--za-accent
```

使用规则：

- 标题用 `--za-text`，不要用 accent。
- 正文用 `--za-text-soft` 或 `--za-text`。
- 辅助说明用 `--za-text-muted`。
- 表格边界用 `--za-line`。
- 引用左边线可用 `--za-line-strong`，不要默认用 accent。
- 链接、focus ring、当前选择态才使用 `--za-accent`。

### 9.3 Syntax token

代码高亮不要直接使用 Shiki / highlight.js 固定主题色。应先在主题系统里定义 syntax token：

```css
--syntax-keyword
--syntax-string
--syntax-number
--syntax-type
--syntax-function
--syntax-variable
--syntax-property
--syntax-comment
--syntax-punctuation
--syntax-operator
--syntax-inserted
--syntax-deleted
```

默认 token 应由当前 palette 派生，而不是写死某个主题。

推荐约束：

- `--syntax-comment` 必须低对比，但可读；
- `--syntax-string` 与 `--syntax-number` 不应都落到同一 hue；
- `--syntax-keyword` 可接近 accent，但不能等同于 accent；
- `--syntax-inserted` / `--syntax-deleted` 使用语义成功/危险色，不跟随用户 accent；
- 明暗模式分别调色，不用反色算法。

### 9.4 用户主题色的边界

用户主题色只作为交互锚点：

- 链接；
- focus ring；
- 当前文件选中态；
- mode switcher active；
- copy button hover；
- 搜索结果 active。

不要把用户主题色扩散到：

- 所有标题；
- 所有引用边框；
- 所有代码关键字；
- 表格 header 背景；
- 大面积文档背景。

这样可以避免用户选择橙色、紫色、绿色时，文档整体变成一套廉价单色主题。

### 9.5 CSS 结构建议

```css
.workbench-document {
  color: var(--za-text-soft);
  background: transparent;
}

.workbench-document h1,
.workbench-document h2,
.workbench-document h3 {
  color: var(--za-text);
}

.workbench-document a {
  color: var(--za-accent);
}

.workbench-source .tok-keyword {
  color: var(--syntax-keyword);
}
```

禁止：

```css
/* 不要写死 */
color: #58a6ff;
background: #0d1117;
```

## 十、读取与 IPC 契约

现有 `readFile` 可继续复用，但建议补充元信息，让 renderer 不靠扩展名猜全部：

```ts
interface WorkbenchFileReadResult {
  ok: boolean;
  status:
    | 'ok'
    | 'not_found'
    | 'not_file'
    | 'too_large'
    | 'binary'
    | 'invalid_path'
    | 'error';
  absPath: string;
  resolvedFrom?: string;
  content: string;
  size?: number;
  mtimeMs?: number;
  encoding?: 'utf8';
  fileName?: string;
  ext?: string;
}
```

M1 可不改 IPC，先在 renderer 用 `absPath` / `content` 推断。M2 再补 `mtimeMs` / `ext` / `encoding`，用于缓存和预览决策。

## 十一、安全模型

文件预览运行在 renderer，风险来自三类输入：

1. 本地 Markdown 里的 HTML / script；
2. 本地 Markdown 里的远程资源链接；
3. 本地路径跳转越过 workspace 边界。

治理规则：

- Markdown parser 不输出 raw HTML；
- HTML block 作为纯文本或直接过滤；
- `javascript:` / `data:` / `file://` 链接默认禁止；
- 远程图片默认不加载；
- 相对本地链接必须 resolve 后仍在 workspaceRoot 内；
- 点击外链走系统浏览器，不在 webview 中隐式打开；
- 预览失败不应 fallback 到 `dangerouslySetInnerHTML`。

## 十二、性能策略

### 12.1 文件大小阈值

建议阈值：

| 类型 | 阈值 | 超限行为 |
| --- | --- | --- |
| Markdown Preview | 1 MB | 切 Source 或提示外部打开 |
| Source Plain | 2 MB | 现有 `too_large` 兜底 |
| Syntax Highlight | 300 KB | 禁高亮，plain source |
| JSON formatting | 1 MB | plain source |
| 图片 | 10 MB | 显示文件信息 + 外部打开 |

### 12.2 渲染缓存

以 `absPath + mtimeMs + size + mode` 作为缓存 key。

M1 可不做复杂缓存，只依赖 React state。

M2 在 Workbench 收起时：

- 当前文件内容保留；
- 非当前文件的渲染缓存可以释放；
- FilesView 树缓存仍按既有策略。

### 12.3 虚拟滚动

M1 不做虚拟滚动，依赖 readFile 2MB 上限。

M2 若要支持更大源码文件，再引入行虚拟化。不要在 M1 提前引入复杂滚动系统。

## 十三、视觉规范

### 13.1 Markdown 文档

文档阅读区应像“正文”，不是代码面板：

- 左右 padding 24-32px；
- 最大阅读宽度建议 `760px`；
- 宽 Workbench 下正文不要无限拉长；
- h1 首屏醒目，但不要像 landing page；
- h2 / h3 用边距和字号建立层级；
- 段落行高 1.65 左右；
- 表格可横向滚动；
- 代码块是文档中的独立块，带复制按钮。

### 13.2 Source Viewer

源码区应像工具：

- 等宽字体；
- 行号 gutter 固定宽度；
- 背景使用 `--za-bg-1` 或透明，不要新建厚重卡片；
- 当前行 hover 低对比；
- 长行横向滚动，不强行折行；
- 不要把 source 放进卡片再嵌套进 Workbench。

### 13.3 Diff Viewer

现有 Diff 解析可保留，但应从 `DiffView` 抽为 `DiffViewer`。Diff 的视觉继续强调增删和双列行号，不和文档 Preview 混用样式。

## 十四、交互细节

### 14.1 顶部栏

顶部栏建议：

```text
[breadcrumb / filename]                         [Preview] [Source] [Diff] [Refresh] [Open]
```

规则：

- Preview 不可用时禁用，不隐藏；
- Diff 没有改动时仍可点击，但显示空状态；
- 当前模式持久化到当前 fileTarget，不必全局记忆；
- 点击文件树另一个文件时重新按默认策略选择模式。

### 14.2 空状态

空状态文案要短：

- 无文件：`从文件树中选择文件`
- 二进制：`无法预览二进制文件`
- 过大：`文件过大，请在编辑器中打开`
- 无 diff：`该文件没有未提交改动`

不要用大段说明解释功能。

### 14.3 复制

- Markdown 代码块：复制该代码块；
- Source：复制全部；
- Diff：复制 diff；
- JSON Preview：复制格式化 JSON。

复制按钮只在 hover / focus 时增强显示，避免文档阅读时控件太吵。

## 十五、格式矩阵

| 格式 | M1 行为 | M2 行为 |
| --- | --- | --- |
| Markdown | 文档渲染 | heading outline / 锚点 |
| Code | Source plain | Shiki 高亮 |
| JSON | 格式化 + 折叠外暂不做 | 可折叠树 |
| YAML | Source plain | 基础高亮 |
| Text / Log | Source plain | 搜索 |
| Image | 本地预览 | 缩放 / 复制路径 |
| CSV / TSV | Source plain | 表格预览 |
| SVG | Source plain | 安全预览需单独评估 |
| PDF | 外部打开提示 | 内嵌 PDF 预览 |
| DOCX / XLSX / PPTX | 外部打开提示 | 不默认内嵌，需专门评估 |

## 十六、落地拆解

### M1：文档可读

目标：解决 Markdown 不渲染和文件入口语义错误。

任务：

1. 新增 `fileTarget` / `openFile`，保留 `openDiff` 兼容。
2. `FilesView` 点击文件调用 `openFile`。
3. 新增 `FilePreviewView`，承载 Preview / Source / Diff。
4. 从 `DiffView` 抽出 `DiffViewer`。
5. 新增 `SourceViewer`。
6. 新增 `MarkdownDocument`，支持基础 Markdown。
7. 添加 `.workbench-document` / `.workbench-source` 样式，全部走 semantic token。
8. Markdown raw HTML 过滤或纯文本化。
9. typecheck + renderer 单测覆盖 parser / mode selection。

验收：

- 点击 `.md` 默认看到渲染后的文档；
- 可切 Source 查看原文；
- 有改动文件可切 Diff 查看变更；
- Markdown 表格、代码块、引用、列表可读；
- 更换主题后文档颜色正常，没有硬编码亮色/暗色。

### M2：源码体验

目标：让源码预览接近 Codex/VS Code 的静态阅读体验。

任务：

1. 引入 Shiki 或等价高亮器；
2. 按语言懒加载；
3. 定义 `--syntax-*` token 并接入主题系统；
4. 超阈值文件降级 plain source；
5. JSON/YAML 增加基础高亮。

验收：

- 常见代码文件有语法高亮；
- 主题切换后高亮仍协调；
- 大文件不会卡死；
- 高亮失败不影响文件阅读。

### M3：更多格式

目标：补齐常见非代码文本格式。

任务：

1. CSV / TSV 表格预览；
2. 图片缩放和基础信息；
3. Markdown heading outline；
4. 文档内锚点；
5. 搜索。

## 十七、测试计划

### 单元测试

- `detectFileKind()`：
  - `.md` -> markdown；
  - `.json` -> json；
  - unknown text -> source；
  - binary result -> fallback。
- `detectPreferredMode()`：
  - explicit diff 优先；
  - markdown 默认 preview；
  - code 默认 source。
- Markdown parser：
  - heading/list/table/code/quote；
  - raw HTML 不执行；
  - unsafe links 被过滤。

### 组件测试

- `FilePreviewView`：
  - Markdown 文件默认渲染 Preview；
  - Source tab 显示原文；
  - Diff tab 调用 gitDiff；
  - too_large/binary 显示 fallback。

### 手工验收

1. 打开知识库 `.md` 文件，确认标题、列表、表格、代码块渲染。
2. 切换亮色/暗色/自定义 accent，确认文档不偏色。
3. 打开代码文件，确认 Source 行号和横向滚动。
4. 修改文件后切 Diff，确认 diff 仍可用。
5. 点击 Markdown 内部相对链接，确认跳到 Workbench 对应文件。
6. 点击外链，确认系统浏览器打开。

## 十八、开放问题

1. 是否在 M1 就加入 Markdown heading outline？
   - 建议否。先把 Preview / Source / Diff 语义和渲染打通。

2. 是否允许远程图片？
   - 建议否。后续可做“加载远程资源”显式授权。

3. 是否把 Diff tab 只在有改动时显示？
   - 建议不隐藏，只在无改动时显示空态，避免布局跳动。

4. 是否直接引入第三方 Markdown 库？
   - M1 可继续用自研 parser，减少依赖和安全面；若后续 CommonMark 兼容性不足，再评估 `micromark` / `remark`。

5. 是否直接用 Shiki？
   - 放到 M2。先用 token 架构把主题兼容边界定好。

## 十九、决策摘要

- 文件点击默认进入 File Preview，而不是 Diff。
- Workbench 文件视图拆成 Preview / Source / Diff。
- Markdown 使用文档级 renderer，不直接复用聊天气泡 renderer。
- 文档渲染全部走应用 semantic token。
- 用户主题色只用于交互锚点，不染整篇文档。
- 代码高亮必须走 `--syntax-*` token，不写死高亮颜色。
- raw HTML / script / 远程资源默认禁用。
- M1 先解决 Markdown 可读与模式语义；M2 再做 Shiki 高亮和更多格式。
