# 模型下拉：从「打平单层」改为 provider→model 两级级联菜单

创建时间：2026-07-08
最后更新：2026-07-08

## 背景

聊天区 composer 的模型切换下拉原本把 `provider × model` 打平成单层列表（复合 id = `groupId::modelId`），一行一个「分组 · 模型」。渠道多、每个渠道模型也多时，单层列表很长、层级信息丢失。

需求：改成方案 B —— 一级 provider、二级模型的级联子菜单；单模型 provider 退化为一级直接选中；触发器（收起态）仍显示 `分组名 · 模型名`。

## 落地方案

- 新建通用组件 `apps/desktop/renderer/src/app/components/CascadingMenu.tsx`：
  - `groups: { id, label, items: { id, label }[] }[]`，一级 = provider 分组，二级 = 该 provider 下模型。
  - 单 item 分组自动退化：不渲染右侧箭头，点一级项直接 `onChange(itemId)`。
  - 交互：hover 展开子菜单，`← →` 切主/子菜单，`↑ ↓` 移动焦点，`Enter/Space` 选择，`Esc`/点外部关闭。
  - 主面板与子面板都用 `createPortal` 投影到 `document.body`，`position: fixed` 定位，避免被 composer 容器裁剪。
  - 触发器 `triggerLabel = ${selectedGroup.label} · ${selectedItem.label}`，满足「分组·模型」文案。
- `TokenUsageDisplay.tsx` 把模型 `Dropdown` 换成 `CascadingMenu`：在组件内按 `groupId || id` 折叠 `providers`（仅 `apiKeyConfigured`）构造 `modelGroups`，`value` 仍是复合 id，`onChange` 仍回调 `onModelChange`（写会话绑定）。思考深度（effort）下拉保持原 `Dropdown` 不动。
- 保留 `modelOptions` prop：`shouldShowModelDropdown` 的门槛判断仍用它（≥2 个可用模型才显示切换），ChatSurface 调用点无需改。

## 踩坑

- **CSS 类名必须和组件实际渲染的类名逐一对齐**。第一版 CSS 用了想当然的名字（如 `pa-cascading-group-item`、`pa-cascading-arrow`、`pa-dropdown-caret`），与组件真实类名（`pa-cascading-group` / `pa-cascading-group-arrow` / `pa-cascading-caret` / `pa-cascading-menu-panel` / `pa-cascading-submenu` / `pa-cascading-item-check` 等）对不上，样式整片失效。改法：先 `grep 'className='` 把组件里所有类名拉出来当权威清单，再据此写样式。
- 触发器根节点是 `pa-cascading-menu`，面板才接收外部 `className`（`pa-cascading-menu-panel`）。给 composer 定制尺寸时要作用在 `.pa-cascading-trigger` 上，别错挂到 `.composer-cascading-menu` 后代选择器里。

## 验证

- `pnpm -r typecheck`：6/6 workspace 项目通过。
- desktop `npm test`：969 pass。仅有的 4 个失败在 `prompt-assembler.test.mjs`（System Context assembly，新增 `agent.mcp-host` 提示段），属于树内另一处未提交的主进程改动，与本次 renderer-only 改动无耦合。
