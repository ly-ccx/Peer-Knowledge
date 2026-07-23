# Peer CLI / TUI 主题治理规范

创建时间：2026-07-23  
最后更新：2026-07-23  
状态：实施基线

## 目标

Peer CLI / TUI 的主题不是一张可选颜色表，而是界面表达层的唯一视觉事实源。明暗主题、文本选择、输入选择、光标、焦点、状态色和品牌效果都必须经过同一语义 Token 契约，不得依赖 OpenTUI 或终端默认值。

本规范只治理界面表达，不改变能力、权限、Tool Result 或 Evidence 链路。

## 模块边界

| Module | Interface | 责任 |
|---|---|---|
| `tui-theme.ts` | `TuiPalette`、`DARK_PALETTE`、`LIGHT_PALETTE`、`COLOR`、主题 store | 定义语义 Token；解析 light / dark / system；更新 live palette |
| `themed-primitives.tsx` | `ThemedText`、`ThemedTextarea`、原生控件适配 props | 把 Token 绑定到 OpenTUI 原生交互状态 |
| 业务 surface | `COLOR.<semanticToken>` 与主题基础组件 | 只表达语义，不定义颜色 |
| `theme-governance.test.ts` | 自动质量门禁 | 阻止字段漂移、低对比度、裸颜色和原生交互绕过 |

## Token 分层

### Surface

- `background`
- `panel`
- `panelRaised`
- `userPanel`
- `selection`：菜单、列表等项目选中背景；不得用于文字拖选

### Text

- `text`
- `textSoft`
- `muted`
- `subtle`
- `dim`
- `link`

### Native text selection

- `textSelectionBackground`
- `textSelectionForeground`

两者必须成对定义。禁止只设置背景并继承正文前景。

### Input

- `inputBackground`
- `inputForeground`
- `inputPlaceholder`
- `inputSelectionBackground`
- `inputSelectionForeground`
- `inputCursor`

输入选择前景/背景也必须成对定义。焦点边界使用 `borderFocus`，不得复用 danger、accent 等临时近似色。

### Status and brand

状态必须使用 `info`、`success`、`warning`、`danger` 及工具状态 Token。品牌高亮或渐变终点使用 `brandHighlight`；品牌源 artwork 中的固定色值可作为资产数据保留，但不能扩散到业务界面。

## 消费规则

1. 所有可选择文字必须使用 `ThemedText selectable`。
2. 所有 textarea 必须使用 `ThemedTextarea`。
3. 第三方或无法包装的原生控件，必须使用 `themedTextSelectionProps` 或 `themedTextareaStateProps`。
4. 静态、不可选择的 `<text>` 可以直接使用，但 `fg` / `bg` 必须来自语义 Token。
5. 业务 TS / TSX 禁止出现 `#hex`、`rgb()`、`rgba()`。
6. 禁止业务 surface 直接设置 `selectionBg`、`selectionFg`、`cursorColor`。
7. 不得把菜单 item selection、鼠标文字 selection 和输入 selection 混成同一个 Token。
8. 主题切换必须修改 live `COLOR` 对象，避免调用方缓存失效；新 surface 不自行解析 system theme。

## 新增或修改主题的流程

1. 先说明新视觉状态的语义；确认现有 Token 无法准确表达后再新增字段。
2. 在 `TuiPalette` 中新增字段。
3. 同时给 `DARK_PALETTE` 和 `LIGHT_PALETTE` 提供值。
4. 在主题基础组件或唯一对应 surface 中消费，不得散落复制。
5. 为交互前景/背景增加至少 4.5:1 的对比度检查。
6. 补明暗主题回归；涉及原生状态时覆盖 selection、input、cursor、focus。
7. 运行：

```bash
cd apps/tui
bun test src/theme-governance.test.ts src/tui-theme.test.ts
bun test src
bun run typecheck
```

## 例外边界

允许的固定色值只有：

- `tui-theme.ts` 中的 palette 定义；
- `b3-wordmark.ts` 中作为不可变品牌 artwork 数据的颜色。

例外不能包含可交互组件样式，不能用注释临时豁免。若确有新例外，必须先在本规范说明原因和边界，再更新自动治理清单。

## 质量门禁

自动测试必须持续验证：

- 明暗 palette 字段完全一致且都是有效六位 hex；
- 正文、文字选区、输入文字和输入选区对比度不低于 4.5:1；
- `ThemedText` / `ThemedTextarea` 将原生状态绑定到对应语义 Token；
- 业务源码没有裸色值；
- 业务源码没有 raw selectable `<text>`、raw `<textarea>` 或原生选区覆盖；
- TUI 全量测试与 TypeScript 类型检查通过。

## 评审检查

每个 CLI / TUI 界面变更至少回答：

- 这个颜色表达什么语义？
- light 和 dark 是否都有对应值？
- 鼠标选择、键盘选择、焦点和输入状态是否仍可读？
- 是否绕过了主题基础组件？
- 没有终端默认色时是否仍能正确显示？

只要答案依赖“终端一般会处理”或“OpenTUI 默认应该可见”，就不符合本规范。
