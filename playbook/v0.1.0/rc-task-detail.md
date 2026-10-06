# RC7 任务详情的层级与操作修订

创建时间：2026-10-05
最后更新：2026-10-06
状态：InReview（最新提交本机、实机与双平台 CI 均通过，待人工审阅）
派单来源：负责人实测指出任务详情粗糙，原始字段和整行按钮抢占主界面。
级别：C。分支：PeerAgent/pa/rc-task-detail；基线：开发线 7276b5e6。

## 目标与依赖

依据产品北极星与已批准 Frost 灰底/连续曲线规范，让任务详情先说明任务、当前进展和下一步。已有任务投影、工作会话入口、主题与控件 token 均已合入；不依赖待合入 PR124，不改其文件中的在途修改。

## 范围与允许改动

- apps/desktop/renderer/src/project-agent/drawer/SessionDetail.tsx：紧凑返回、标题/状态、实际报告、会话入口、按需任务信息；保留原会话与工作台装配。
- apps/desktop/renderer/src/project-agent/drawer/BotProfileDrawer.tsx：实机已复现打开内层会话后 Escape 同时关闭外层档案；外层停靠抽屉在已有浮层打开时让出 Escape，复用既有 overlayStack 标识。这是原工作会话返回路径的必要修复，维持 C 级范围。
- 同目录新建 sessionDetailPresentation.ts / sessionDetailPresentation.test.ts：只处理已有状态的显示文案、空态和事实区分，不由报告文本推断完成。
- apps/desktop/renderer/src/project-agent/styles/bot-drawer.css：任务详情局部样式，复用全局表面/圆角/字体/焦点 token；不重画其它标签页。
- packages/i18n/src/index.ts：只增加 projectAgent.drawer.taskDetail.* 的中英文文案。
- apps/desktop/scripts/bot-work-surface-checks.mjs：用现有隔离 Electron 测试宿主与会话事实夹具补任务详情交互、主题/窄窗/键盘检查和截图。
- apps/desktop/scripts/bot-shell-electron-smoke.mjs：在已有受控会话列表读取 seam 同步提供详情读取事实；原夹具只有列表而详情返回真实 NOT_FOUND，无法用于测试状态失效后的详情回退。只改隔离副本中的读投影替身，不改生产服务。

不改 Runtime、协议、权限、Evidence、System Context、IPC、存储、依赖、版本或发布物。UI 图标全部复用 PeerIcon SVG。

- 真实接口核对：列表投影没有报告，报告来自既有 `get(detail: report)`。详情由当前列表提供状态、同任务详情提供报告，状态变化时刷新报告；读取中、读取失败和已读空报告分开表达。任务切换不能混用报告，临时失败保留同任务此前报告并说明刷新失败；明确 NOT_FOUND 清除详情。

## 实现要点

紧凑返回导航；任务标题与短状态分层；进展按真实状态及已有排队原因表达；已有报告作为「任务报告」展示，不当作验证结论。缺失报告只显示一次明确空态，证据引用按需展开，不堆编号按钮或空字段。工作会话为一个明确操作；缺少会话说明原因。内部锚点、模型快照与任务标识放在默认折叠的信息区，不在主界面展示 UUID。

### 2026-10-06 布局复审修订

负责人指出 PR125 实机图仍缺乏阅读秩序：返回悬停底色、标题、状态徽标、独立受阻标题、报告空区形成过多视觉节点。本次在同卡原许可文件内继续修订：轻返回导航；标题后只保留一个结构化状态主层级；记录进展和下一步组成自然文本，无重复「最近进展」标签或深底卡；工作会话入口使用紧凑灰底控件；创建时间移至按需信息；没有报告时只保留一行诚实提示，存在报告才展示报告标题。标题、正文、报告与信息区共用同一左基线，避免负边距和嵌套卡片改变对齐。原有状态/报告事实、会话入口、键盘和缺失数据边界不变。原生截图在指针离开控件后采集，同时检查普通与大字号窄窗的对齐、空态空间、控件对比度与返回路径。

## 测试与退出

定向覆盖所有任务状态、未知/不可用、排队原因、报告与签收区分、证据去重；受影响 desktop 完整测试、build、workspace typecheck/architecture。实际 Electron 验证受阻/进行/结果就绪/签收/无会话与事实失效、长标题、深浅主题、大字号、窄抽屉、信息折叠、返回和会话打开。认知与会话数据受控，只证明界面和现有入口，不代表真实任务执行验收。提交同轮 push，PR 回开发线等待评审；本卡不发布 RC。

## 截图审查与设计结论

审查范围是负责人提供的任务详情截图。现有任务、状态与工作会话关联保留；主要问题是技术字段占主界面、动作尺度过大、缺失报告/证据反复占位，以及状态和报告缺少层级。单凭原截图不推断键盘或读屏行为，交互问题以本轮原生检查为准。

复审后的任务详情只有一条阅读线：轻返回导航、任务名称、结构化状态与已有进展/下一步、报告、按需信息。移除进展深底卡与「最近进展」标签，不再把受阻进展当作大标题；状态不使用独立填充徽标。灰底紧凑会话操作保留一个 SVG 方向图标。无报告时没有整节空标题或装饰文件图标；创建时间、模型、标识保留在默认折叠区。标题、正文、操作、空态及信息区共用左基线，展开指示位于右侧。报告仍不代替验证或签收，缺少会话有说明。复用 Frost 全局表面、圆角和字体 token。

2026-10-06 最新提交实机截图，受控任务数据、正式 Renderer，未注入视觉 CSS。受阻图的指针位于控件外；展开与签收图保留键盘焦点环：

- [深色受阻详情](../../design/product/assets/peer-frost-task-detail-layout/task-detail-blocked-dark.png)
- [浅色受阻详情](../../design/product/assets/peer-frost-task-detail-layout/task-detail-blocked-light.png)
- [按需任务信息](../../design/product/assets/peer-frost-task-detail-layout/task-detail-info.png)
- [已签收与任务报告](../../design/product/assets/peer-frost-task-detail-layout/task-detail-accepted.png)
- [760px 视口、深色大字号](../../design/product/assets/peer-frost-task-detail-layout/task-detail-narrow-large.png)

负责人本轮提供的是首轮修订的裁切图；据此确认视觉节点过多的问题，并用本轮深浅主题、签收、展开与窄窗原生图复审。先看当前任务与下一步，再按需看记录；不为填满抽屉制造内容。原截图像素密度未知，不作像素一致性声明，知识仓不转存用户截图。首轮截图保留在原资产目录作为历史材料。

## 交接报告

### 卡片
RC7 任务详情的层级与操作修订，C 级。

### 分支与提交
- 代码分支：PeerAgent/pa/rc-task-detail；基线：7276b5e6。
- 提交：2e0df4fc3e5314978635c6172b1a79252c1d53aa（ecc90448 布局修订、2e0df4fc 报告空态采集等待）。
- [代码 PR125](https://github.com/ly-ccx/Peer-Agent/pull/125)，目标 PeerAgent/dev/0.1.0。
- 验收 tree：aae912b7d67fe8c15cc657f66f663182d4632845，与最终提交 tree 一致。

### 改了什么
PR 总计 8 个文件，均在许可清单内；本次布局续修只改原许可的 5 个文件：任务详情、纯显示投影及测试、详情样式、原生检查。中英文文案、外层 Escape 让位与隔离宿主读投影维持首轮实现。报告/依据不决定完成或签收；失效事实不保留旧的运行进展；内部引用原值保留，展示计数去重。

### 与卡片的偏差
实机复现了内层会话 Escape 连带关闭外层档案，扩入同一返回路径的两行修复。任务列表事实夹具原来没有相应详情读投影，补同源详情事实以测试失效回退。已在允许改动中记录，未移动运行时边界。返回门禁改为定位原任务行，避免新增隔离会话同时出现在历史分组时产生选择器歧义；未放宽旧检查。

### 验证
- `node --test apps/desktop/renderer/src/project-agent/drawer/sessionDetailPresentation.test.ts`：定向 8/8 通过。覆盖所有状态中英文、报告不能改变签收、未知/失效事实、真实队列原因、缺失数据和引用去重。
- `pnpm --filter @peer-agent/desktop build`、`pnpm typecheck`、`pnpm architecture:check`、`git diff --check` 通过。
- `pnpm --filter @peer-agent/desktop test`：5357 用例，5352 通过、5 个既有跳过、0 失败/取消；额外 i18n 检查 1/1 通过。
- `pnpm --filter @peer-agent/desktop smoke:bots --streaming --accessibility --effort-stability --work-surfaces`：60 项壳/界面交互检查通过，0 页面错误、0 窗口授权错误；专属测试进程确认退出。
- 新增实机检查：受阻/运行/待确认/签收/失败/取消/暂停/替代/启动/排队，事实读取失败、缺少会话、SVG 折叠与依据去重、键盘、同一会话打开、Escape/焦点恢复、返回原任务、深浅主题、760px 视口大字号、灰底主操作悬停文字对比度至少 4.5:1；新增统一左基线、导航/标题间距、无空报告标题、单行空态高度及无标题/状态碰撞检查。逐图检查两种主题与展开/签收/大字号状态，如上。
- 最新本机材料：`$CODEX_HOME/visualizations/2026/10/06/rc-task-detail-layout/`，含报告/trace/日志、原生截图、深浅预览与失败修正记录。最终原生报告 sourceHead=2e0df4fc、sourceDirty=false，与提交匹配。
- [最新提交 CI 37404047620](https://github.com/ly-ccx/Peer-Agent/actions/runs/37404047620)，head 2e0df4fc，Mac/Linux 首次均通过。首轮 bd06cda9 的 [CI 37335599606](https://github.com/ly-ccx/Peer-Agent/actions/runs/37335599606) 双平台通过保留为历史记录；该轮 Linux 既有流式门禁超时，失败 job 重跑一次通过，未改门禁。
- 未验证真实模型、任务工具执行、复杂写任务的 Evidence 或全量读屏；受控认知和会话事实只用于验证界面、现有 IPC 入口、存储读取与导航。

- 本轮第一次原生测试的精确文本定位在合并说明后失配，说明文本节点已独立，界面内容不变；第二次在既有 350ms 异步报告读取完成前断言空态，改为等待真实空态出现，保持原断言。两次进程都确认退出，报告保留。最终原生 60 项通过。

- 最后一次完整测试在依赖构建完成后顺序运行通过。此前误把 build 与测试同时启动，导致测试读取正在重建的 dist 而出现缺失 export；该文件隔离重跑 7/7 通过，完整重跑结果如上，未修改或跳过测试。

### 架构影响
C 级。能力链、Runtime、协议、权限、Evidence、System Context、IPC、存储边界无变化；无新依赖或版本变更。

### 文档偏差
本轮增加 5 张最新受控实机截图，保留首轮 5 张历史图及本知识卡，不修改产品北极星、ADR 或版本计划，不向代码仓写知识文档。

### 未完成与后续
PR125 最新提交本机、实机与双平台 CI 均通过，待人工审阅；按实施手册不自行合并。本卡不发布新 RC，不改写 RC7 tag 或资产。PR124 的 SVG/消息修复仍独立待审。
