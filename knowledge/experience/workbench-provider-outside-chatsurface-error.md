# 运行时崩溃：`useWorkbench must be used within a WorkbenchProvider`

> 代码仓库：`peer_agent`（桌面端 `apps/desktop` renderer）  \
> 知识仓库：`peer-knowledge`  \
> 创建时间：2026-08-10  \
> 最后更新：2026-08-10  \
> 相关实现：`App.tsx` / `ChatSurface.tsx` / `WorkbenchContext.tsx` / `useWorkbenchOptional`

## 1. 用户可感知现象

打开「继续讨论」抽屉（会话 Drawer）时，renderer 抛错并导致界面崩溃：

```
useWorkbench must be used within a WorkbenchProvider
```

错误来自 `WorkbenchContext.tsx` 中严格版 `useWorkbench()` 的守卫分支。

## 2. 正常设计链路（source of truth）

```text
App.tsx
  <WorkbenchProvider conversationId=... isPageActive=...>   ← 938 行起
    <section className="main-panel">
      <ChatSurface />                                       ← 主聊天（Provider 内）
      ...
    </section>
  </WorkbenchProvider>                                      ← 1110 行止
  ...
  {/* 继续讨论抽屉：渲染在 </WorkbenchProvider> 之后！ */}
  <ChatSurface />                                           ← 1261 行（Provider 外）
```

- `WorkbenchContext.tsx` 提供两个消费 hook：
  - `useWorkbench()`：严格版，无 Provider 直接 `throw`（错误来源）；
  - `useWorkbenchOptional()`：可选版，无 Provider 返回 `null`，调用方自行降级。
- `ChatSurface` 是复用组件：主聊天与「继续讨论」抽屉共用同一组件。

## 3. 根因

抽屉复用 `ChatSurface`，但抽屉在组件树中位于 `</WorkbenchProvider>` **之后**（React Context 按组件树传播，与 DOM 位置无关），而 `ChatSurface` 顶层无条件调用严格版 `useWorkbench()` → 触发守卫抛错。

`useWorkbenchOptional` 此前已存在，但只有 `HomePage`、`InlineMarkdown` 这类本来就可能在 Provider 外渲染的组件在用；`ChatSurface` 当时是纯 Provider 内组件，被抽屉复用后就成了漏网之鱼。

## 4. 修复（最小正确改动，仅 ChatSurface.tsx）

1. import 从 `useWorkbench` 改为 `useWorkbenchOptional`；
2. 新增模块级 `const NOOP = () => {};`（稳定引用，避免 useCallback 依赖抖动）；
3. 解构处改为降级默认值：

```tsx
const workbench = useWorkbenchOptional();
const goalSlot = workbench?.goalSlot ?? null;       // GoalPlanPanel 的 sidePanelContainer 可选，null 时独立渲染
const setHasGoalPlan = workbench?.setHasGoalPlan ?? NOOP;
const workbenchOpen = workbench?.open ?? false;
const workbenchActiveTab = workbench?.activeTab ?? 'plan';  // WorkbenchTabId 合法值
const setWorkbenchOpen = workbench?.setOpen ?? NOOP;
const setWorkbenchTab = workbench?.setActiveTab ?? NOOP;
```

主聊天（Provider 内）行为不变；抽屉（Provider 外）优雅降级：不展开工作台、GoalPlanPanel 独立渲染。

## 5. 验证

- `npx tsc -p tsconfig.json --noEmit` 通过；
- renderer 全量测试 667/673 通过；6 个失败均为未跟踪新文件（acceptanceTransition / planStepRunningDot）的既有失败，与本次改动无关；
- `rg "useWorkbench" ChatSurface.tsx` 确认不再有严格版调用。

## 6. 经验沉淀

1. **复用组件必须选「可选版」Context hook**：只要组件有被 Provider 外复用的可能（抽屉、浮层、新页面），就用 `useWorkbenchOptional()` 并在缺失时降级，而不是假设永远在 Provider 内。
2. **React Context 按组件树传播，不看 DOM 位置**：抽屉即使视觉上位于 Provider 的 DOM 子树内，只要 JSX 层级在 Provider 标签之外，就消费不到。
3. **守卫抛错是设计内行为**：严格版 hook 的 `throw` 是 API 契约，出现该错误说明存在新的消费方漏网，优先修消费方（降级），而不是放宽守卫或包一层"假 Provider"。
4. 新增可在 Provider 外渲染的挂载点时（如本次的抽屉），顺手 `rg "useWorkbench\("` 全仓排查一遍新挂载子树内的严格版调用。
