# 64. Workbench 源码预览先复用 highlight.js，不上 Monaco

创建时间：2026-08-17
最后更新：2026-08-17

## 状态

Accepted。Source 模式已接到现有 highlight.js，未引入 Monaco。

## 背景

Workbench 打开 `.jsx` / `.ts` 等代码文件时，Source 视图只有行号和纯文本，关键字、字符串没有颜色区分。聊天区已经有一套同步的 highlight.js 高亮（`codeHighlighter.ts`），文件预览却没有复用。

产品讨论里出现过“要不要引入 Monaco Editor”的选项。现有文件预览方案已经把本期边界写成：

- 不做文件编辑器
- 不做 IDE 级语法服务 / 跳转 / 诊断
- 代码文件默认是 Source 阅读，不是编辑
- M2 可以评估 Shiki 或等价高亮器，不是整颗编辑器

## 决策

### 决策一：先复用现有 highlight.js

- `SourceViewer` 继续负责行号 gutter 和只读排版。
- 按文件扩展名映射到 highlight.js 语言 id / 已注册别名（`.jsx` → `javascript`，`.tsx` → `typescript`）。
- 高亮 HTML 按源码换行切开，跨行 token 补回每一行，避免打乱现有 gutter。
- 未知扩展名、超长文件（沿用聊天区 20_000 字符上限）或高亮失败时回退纯文本。
- 配色继续走现有 `--za-code-*` / `hljs-*` CSS，不引入独立编辑器主题。

### 决策二：不上 Monaco

Monaco 解决的是编辑问题：光标、选区、查找替换、语义着色、补全、诊断。本期只缺静态高亮。引入 Monaco 会带来：

- 体积、web worker、资源路径和 CSP 成本
- 与 Peer Frost 主题系统的额外对接
- 把只读预览做成半个 VS Code，越过当前产品边界

只有用户要在 Peer 内改文件，并且准备为此单独做主题、worker 和性能预算时，才重新评估 Monaco。

### 决策三：Shiki 仍是后续阅读体验选项，不是这次的替换

聊天区需要同步高亮，不能换成异步 Shiki。文件预览若要接近 VS Code 的 TextMate 着色，可以在 M2 单独评估按语言懒加载的 Shiki，但不能替换聊天区现有同步链路。

## 验证要求

1. 打开 `.jsx` / `.ts` 时关键字、字符串有颜色区分，行号仍在。
2. 未知语言和大文件回退纯文本，内容不丢失。
3. 不引入 Monaco / CodeMirror / Shiki 依赖。

## 后续

- Diff 视图可按同样方式复用 highlight.js，但不是这次的范围。
- 若 Source 阅读体验不够，再评估 Shiki，而不是先上编辑器。
