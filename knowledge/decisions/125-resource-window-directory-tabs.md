# 125. 资源窗口目录标签

创建时间：2026-11-09
最后更新：2026-11-09（追加决策五：头部导航入口的语境可见性；方向由用户于同日选定）

## 状态

Accepted（方向由用户于 2026-11-09 选定：目录在资源窗口中升为一等资源标签）。
实施与验证按「验证要求」执行；Accepted 不代表发布验收通过。
决策五为同日修订，与原文一并接受；实施回执见「验证要求」第 5 条。

## 背景

ADR 47 建立了「一级能力入口与二级资源标签」分层，并写死：「Files 是工作区导航器，
不为文件树本身创建标签；从文件树打开的资源进入 Documents」。该决定针对经典 Workbench
的一级能力栏（Plan / Browser / Files / Documents）。

此后出现的**会话绑定资源窗口**（resource workspace）是另一种形态：浏览器式多标签窗，
标签条承载的是资源实例（文档、网页、工作区 Diff、对话、交互结果），不是能力类别。
在这个窗口里，目录仍是旧通道：

- 聊天中的目录引用（`openReference kind:'directory'`）写入单例 `directoryIntent`，
  顶入唯一的「文件」辅助面板，后开覆盖前开；
- 新标签页（launcher）的「文件与目录」入口把整个内容区换成固定文件视图，标签条却仍
  高亮「＋ 新标签页」——标签身份与内容不一致；
- 文档、网页、Diff、对话、交互结果都能作为标签保留、重开、进入「最近」，唯独目录不能
  并排保留两个（例如对照 `branch-snapshots` 与 `worktrees`），也不进入「最近」。

能力导航与资源会话的分层原则本身仍然成立；失衡在于资源窗口把「目录浏览」一律当成
导航，而用户在该窗口里对目录的实际行为是阅读对象（打开、保留、对照、重开）。

## 决策

### 决策一：资源窗口内目录是 Resource Session

- 资源窗口标签条接纳目录标签，与 Documents / Browser 同级：可多开、可切换、可关闭、
  进入「最近」。
- 目录标签身份 = `BotDocumentReference`（`kind:'directory'`，含 `task` / `relativeTo`），
  按引用字段去重；重复打开激活既有标签。
- 标签内容复用既有 ScopedResourceNavigator（来源核对、面包屑、FilesView、阅读位置
  恢复、只读 Bot 工作区语义全部继承）。标签内导航（面包屑/来源切换）更新该标签的引用
  路径，浏览器标签的「身份随当前地址」语义一致；导航产生的新身份不做二次去重。
- 独立资源窗口（NativeResourceWindow）与经典 Workbench 不在本次范围。

### 决策二：保留辅助导航面板，两通道分工

- 顶部 📁 按钮切换的**辅助导航面板**保留，定位不变：临时导航，单例，按 workspace 记忆
  最近位置（既有 `DirectorySession.readings` 继续作为两个通道共享的阅读位置恢复存储）。
- 聊天目录引用、launcher 显式路径、最近列表中的目录 → 打开**目录标签**；不再写
  `directoryIntent` 顶替辅助面板。`directoryIntent` 随辅助面板通道一并退役或仅保留给
  辅助面板内部使用，以实现为准并在代码中注明。
- launcher 的「文件与目录」入口改为切换辅助导航面板，不再顶替内容区，消除
  「标签条亮着新标签页、内容却是目录」的错位。

### 决策三：状态机隔离，复用既有会话骨架

- 新增 `DirectoryTabSessionState`（`tabs: { id, reference }[]` + `activeTabId`），
  按会话键存于 Workbench settings（`directoryTabSessions`），与 BrowserSession /
  DocumentSession 同构；不引入 `Tab<any>` 或全局 `activeResource`（沿用 ADR 47 决策四）。
- 标签元数据持久化只含引用与顺序；展开态、筛选、滚动位置等运行时状态经
  `DirectorySession.readings` 恢复，不进 settings 正文。
- 关闭活跃标签选择右侧邻居，无右侧选左侧；关闭最后一个进入空态（回 launcher），
  与 Documents 语义一致。

### 决策四：协议面只加事实描述符

- `ResourceRecentReference` 增加 `kind:'directory'` 变体（path / relativeTo / task），
  仅作为「最近」提示描述符；不携带 workspace 授权、不新建权限或 Evidence 通道。
  最近描述符按既有规则在所属 owner 范围内解释。

### 决策五：头部导航入口的语境可见性（2026-11-09 修订）

- 资源窗口头部右侧的三枚导航入口——🌐 网页视图、📁 目录（决策二的辅助导航面板切换）、
  📄 变更导航（变更侧栏切换）——在 **launcher（新标签页）为激活标签且没有任何辅助
  面板打开**时不渲染：同组入口已由 launcher 页内「工具」区承载（网页 / 文件与目录 /
  查看更改），双份呈现挤占标签条头部空间（2026-11-09 用户提出）。
- 一旦辅助导航面板或变更侧栏打开（含从 launcher 页内入口打开），三枚入口立即恢复
  渲染并携带 `aria-pressed` 按下态，保证可切换关闭；进入任何资源标签（文档 / 网页 /
  目录 / 对比 / 对话 / 交互结果）或详情视图后照常显示。
- 保持不变的边界：非 launcher 语境下三枚入口是辅助面板的唯一显式切换入口（无键盘
  捷径），不删除、不移入菜单；`useResourceNavigation` 关闭时的焦点回退目标
  `[data-navigator]`、窄窗降级（`auxiliaryNavigator` 不可用时切标签）、launcher 页内
  入口语义（决策二）全部不变；最大化 / 收起按钮不受影响。
- 级别：C（纯 renderer 条件渲染；无能力、权限、Evidence、协议或上下文边界变化）。

## 被替代条款

- ADR 47 决策一第 4 条「Files 是工作区导航器，不为文件树本身创建标签；从文件树打开的
  资源进入 Documents」——**在资源窗口标签条范围内**被本 ADR 替代。经典 Workbench 一级
  能力栏、Plan 单焦点、文件工具显式 path 目标等其余条款继续有效。

## 状态结构

```text
WorkbenchSession(conversationId)
  -> BrowserSession(tabs, activeTabId)
  -> DocumentSession(tabs, activeTabId)
  -> DirectoryTabSession(tabs[reference], activeTabId)   # 新增
  -> DirectorySession(per-workspace 阅读位置记忆)          # 既有，两通道共享
```

## 验证要求

1. reducer 单测：开/去重/激活/关闭邻居/持久化归一（含畸形输入拒绝、`__proto__` 键）。
2. protocol 单测：directory 最近描述符接受合法输入、拒绝越权字段。
3. 交互核验（隔离环境）：聊天目录引用打开标签；重复打开激活既有标签；两个目录标签并排；
   关闭活跃标签邻居语义；辅助 📁 面板行为不回归；launcher「文件与目录」不再顶替内容区。
4. 现有态恢复：重启后目录标签元数据恢复、展开/滚动经 readings 恢复；旧 settings 无
   `directoryTabSessions` 字段可正常启动。
5. 决策五回执（待实施）：launcher 激活且无辅助面板时三入口不渲染（含可访问性树）；
   从 launcher 打开任一辅助面板后三入口恢复且按下态正确；非 launcher 标签与详情视图
   中功能、按下态、焦点回退、窄窗降级不回归；组件级源断言测试绑定条件。

## 后续

- 标签拖拽排序、固定、跨会话移动维持 ADR 47 的暂缓决定。
- 若经典 Workbench 将来引入资源式标签窗，按本 ADR 的「窗口形态优先于能力栏」原则评估。
