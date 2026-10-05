# RC7 任务详情的层级与操作修订

创建时间：2026-10-05
最后更新：2026-10-05
状态：InReview（实现、本机、实机与推送完成；最终提交 CI 待完成）
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

## 测试与退出

定向覆盖所有任务状态、未知/不可用、排队原因、报告与签收区分、证据去重；受影响 desktop 完整测试、build、workspace typecheck/architecture。实际 Electron 验证受阻/进行/结果就绪/签收/无会话与事实失效、长标题、深浅主题、大字号、窄抽屉、信息折叠、返回和会话打开。认知与会话数据受控，只证明界面和现有入口，不代表真实任务执行验收。提交同轮 push，PR 回开发线等待评审；本卡不发布 RC。

## 截图审查与设计结论

审查范围是负责人提供的任务详情截图。现有任务、状态与工作会话关联保留；主要问题是技术字段占主界面、动作尺度过大、缺失报告/证据反复占位，以及状态和报告缺少层级。单凭原截图不推断键盘或读屏行为，交互问题以本轮原生检查为准。

新的任务详情以名称、结构化状态、实际进展和下一步为主；报告单独表达，不代替验证或签收。返回成为紧凑导航，工作会话操作与进展同组。任务信息默认折叠，缺少会话给说明，不提供无效按钮。复用已有 Frost 主题、表面与圆角 token，所有新增图标均为 PeerIcon SVG。

实机截图使用受控任务数据，正式 Renderer 未注入视觉 CSS：

- [深色受阻详情](../../design/product/assets/peer-frost-task-detail/task-detail-blocked-dark.png)
- [浅色受阻详情](../../design/product/assets/peer-frost-task-detail/task-detail-blocked-light.png)
- [按需任务信息](../../design/product/assets/peer-frost-task-detail/task-detail-info.png)
- [已签收与任务报告](../../design/product/assets/peer-frost-task-detail/task-detail-accepted.png)
- [760px 视口、深色大字号](../../design/product/assets/peer-frost-task-detail/task-detail-narrow-large.png)

已把负责人原截图与最终原生截图并排检查。原图为截取区域且像素密度未知，按共同阅读宽度比较层级、操作尺度、内容与留白，不声称像素复刻；这是一轮界面修订。并排图只保留在本机验证材料中，知识仓不转存原用户截图。

## 交接报告

### 卡片
RC7 任务详情的层级与操作修订，C 级。

### 分支与提交
- 代码分支：PeerAgent/pa/rc-task-detail；基线：7276b5e6。
- 提交：bd06cda9ed717330ef416d2018978a3bbca4dcf5。
- [代码 PR125](https://github.com/ly-ccx/Peer-Agent/pull/125)，目标 PeerAgent/dev/0.1.0。
- 验收 tree：ca533c08e20236f0c80eb2fb048736dddc67fe08，与提交 tree 一致。

### 改了什么
8 个文件，均在许可清单内：任务详情、纯显示投影及测试、详情样式、中英文文案、外层 Escape 让位、隔离原生夹具及交互检查。报告/依据不决定完成或签收；失效事实不保留旧的运行进展；内部引用原值保留，展示计数去重。

### 与卡片的偏差
实机复现了内层会话 Escape 连带关闭外层档案，扩入同一返回路径的两行修复。任务列表事实夹具原来没有相应详情读投影，补同源详情事实以测试失效回退。已在允许改动中记录，未移动运行时边界。返回门禁改为定位原任务行，避免新增隔离会话同时出现在历史分组时产生选择器歧义；未放宽旧检查。

### 验证
- `node --test apps/desktop/renderer/src/project-agent/drawer/sessionDetailPresentation.test.ts`：新增 7/7 通过。覆盖所有状态中英文、报告不能改变签收、未知/失效事实、真实队列原因、缺失数据和引用去重。
- `pnpm --filter @peer-agent/desktop build`、`pnpm typecheck`、`pnpm architecture:check`、`git diff --check` 通过。
- `pnpm --filter @peer-agent/desktop test`：5356 用例，5351 通过、5 个既有跳过、0 失败/取消；额外 i18n 检查 1/1 通过。
- `pnpm --filter @peer-agent/desktop smoke:bots --streaming --accessibility --effort-stability --work-surfaces`：60 项壳/界面交互检查通过，0 页面错误、0 窗口授权错误；专属测试进程确认退出。
- 新增实机检查：受阻/运行/待确认/签收/失败/取消/暂停/替代/启动/排队，事实读取失败、缺少会话、SVG 折叠与依据去重、键盘、同一会话打开、Escape/焦点恢复、返回原任务、深浅主题、760px 视口大字号、主操作悬停文字对比度至少 4.5:1。逐图复核发现初稿悬停引用了不存在的主题 token，已修复为 graphite-base-hover 并通过颜色门禁，最终图如上。
- 本机材料：`$CODEX_HOME/visualizations/2026/10/05/rc-task-detail/`，含最终报告/trace/日志、截图、比较图与失败修正记录。原生报告 sourceDirty=true 如实保留（先验收再提交）；最终源 tree 与代码提交匹配。
- GitHub 已触发 PR CI；最终提交的双平台结果待完成，不把前一提交或 PR124 的成功记录算作本次通过。
- 未验证真实模型、任务工具执行、复杂写任务的 Evidence 或全量读屏；受控认知和会话事实只用于验证界面、现有 IPC 入口、存储读取与导航。

- 最后一次完整测试在依赖构建完成后顺序运行通过。此前误把 build 与测试同时启动，导致测试读取正在重建的 dist 而出现缺失 export；该文件隔离重跑 7/7 通过，完整重跑结果如上，未修改或跳过测试。

### 架构影响
C 级。能力链、Runtime、协议、权限、Evidence、System Context、IPC、存储边界无变化；无新依赖或版本变更。

### 文档偏差
只增加本知识卡及 5 张受控实机截图，不修改产品北极星、ADR 或版本计划，不向代码仓写知识文档。

### 未完成与后续
PR125 待双平台 CI 和审阅；按实施手册不自行合并。本卡不发布新 RC，不改写 RC7 tag 或资产。PR124 的 SVG/消息修复仍独立待审。
