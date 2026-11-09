# 47. Workbench 多资源标签模型

创建时间：2026-07-15
最后更新：2026-11-09

## 状态

Accepted，第一阶段 DocumentSession 已实现并验证。

## 背景

ADR 46 为 Browser 建立了会话绑定的 BrowserSession 和多网页标签。Workbench 当前仍把
`Plan / Browser / Files / Diff` 都当成同一层级的能力入口，其中浏览器已经出现第二层网页
标签，而文件预览仍由单个 `fileTarget` 驱动：打开下一份文件会覆盖上一份文件。

多标签不是所有能力的默认形态。Workbench 需要区分：

1. **Capability Navigation**：Plan、Browser、Files、Documents 等稳定能力入口；
2. **Resource Session**：能力内部需要同时保留、切换和恢复的资源实例。

如果把所有能力都包装成相同的万能 Tab，会掩盖网页、文档、终端进程不同的生命周期和目标
选择语义；如果完全不抽象，则每种能力都会重复实现标签交互和会话持久化。

## 决策

### 决策一：一级能力入口与二级资源标签分层

- Workbench 顶部一级导航表达能力类别，不允许同时出现多个同类入口。
- Browser、Documents 以及未来的 Terminal 可以在能力内部维护多个资源标签。
- Plan 保持单一当前焦点；历史计划和子计划使用列表、树或显式计划切换器，不使用可随意关闭的
  浏览器式标签。
- Files 是工作区导航器，不为文件树本身创建标签；从文件树打开的资源进入 Documents。
  （2026-11-09：本条在**资源窗口标签条**范围内被 [ADR 125](125-resource-window-directory-tabs.md)
  替代——目录在该窗口升为一等资源标签；经典 Workbench 一级能力栏语义不变。）

### 决策二：第一阶段建立会话绑定的 DocumentSession

```ts
interface DocumentSession {
  tabs: Array<{
    id: string;
    absPath: string;
    workspaceRoot?: string;
    relPath?: string;
    mode: 'preview' | 'source' | 'diff';
  }>;
  activeTabId: string | null;
}
```

- `documentSessions[conversationId]` 保存每个会话的文档标签集合和活跃标签；无会话时使用
  `__none` 桶。
- 同一绝对路径在一个会话内只对应一个标签；重复打开只激活已有标签。
- 显式 `openDiff` 会把目标标签切到 Diff 模式；普通 `openFile` 不覆盖已有标签的用户模式。
- 关闭活跃标签后选择其右侧邻居，没有右侧时选择左侧；关闭最后一个标签后进入空态，不创建
  不具备资源身份的“空白文档”。
- 标签元数据随 Workbench settings 防抖持久化；文件正文、diff 内容、滚动位置等运行时状态
  不进入 settings。

### 决策三：Diff 是文档模式，不是独立能力

- 一级 `Diff` 入口正名为 `Documents`；持久化中的旧 `diff` 值迁移到 `documents`。
- 每份文档内部继续提供 Preview / Source / Diff 模式。
- 文档标签切换时保持各自已加载内容、模式和组件运行时状态；应用重启后只恢复标签元数据并重新
  读取文件。

### 决策四：复用标签表达，隔离领域状态机

- Browser 与 Documents 复用无业务状态的 ResourceTabStrip 视觉组件。
- BrowserSession、DocumentSession 和未来的 TerminalSession 分别拥有独立 reducer/kernel；
  不引入 `Tab<any>` 或全局 `activeResource`。
- Browser 的 Agent 控制目标继续由 `conversationId + browserTabId` 解析。
- 文件工具继续使用显式 path；不得把“当前文档标签”变成文件 Tool Call 的隐式目标。
- 未来 Terminal 工具若支持多会话，必须显式携带 `terminalSessionId`，不能依赖当前可见标签。

## 状态结构

```text
WorkbenchSession(conversationId)
  -> open + activeCapability
  -> BrowserSession(tabs, activeTabId)
  -> DocumentSession(tabs, activeTabId)
  -> PlanViewState(single focus)
  -> TerminalSessionRegistry(optional, future)
```

Browser WebContents、PTY 进程、文件内容缓存等运行时句柄不进入持久化状态。

## 验证要求

1. 同一会话可同时打开、切换和关闭多个文档标签。
2. 重复打开同一路径不会产生重复标签，显式打开 Diff 会切换已有标签的模式。
3. A/B 会话的文档集合和活跃文档互不影响，返回会话后恢复元数据。
4. 旧的 `activeTab = diff` 自动迁移为 `documents`。
5. Preview / Source / Diff 保持为每份文档自己的模式。
6. Browser 多标签和 Agent 浏览器目标解析行为不发生回归。

## 后续

- Artifact / Evidence 预览优先复用 DocumentSession 或其资源承载层。
- 只有在恢复真实 PTY 生命周期后才增加 TerminalSession 多标签。
- 暂不实现标签拖拽排序、固定、分组、跨会话移动和编辑器写入。
