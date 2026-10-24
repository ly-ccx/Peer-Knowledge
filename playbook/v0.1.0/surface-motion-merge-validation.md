# 菜单、浮层与抽屉合并验证记录

日期：2026-10-24
范围：[代码 PR214](https://github.com/ly-ccx/Peer-Agent/pull/214)、[代码 PR215](https://github.com/ly-ccx/Peer-Agent/pull/215)、[知识 PR74](https://github.com/ly-ccx/Peer-Knowledge/pull/74)。

用户本次明确要求把新增 PR 一起合并并本地测试，故提前验证这次合并；不沿用上一批“测试留到发布前”作为本次结果。本文记录专项验证，E13 的完整发布包验收仍独立。

## 目标、状态与边界

目标是打开对话、设置菜单/页面和档案抽屉可连续操作，调整模型强度后保留打开面板、输入与焦点，成功/失败由既有 IPC 保存回执表达，数据刷新不重播入场。关闭/取消、快速反向、减少动效和升级弹窗目标交接仍有静态终态及有界收尾。

共享动效整合为 C 级 UI/测试接线；快捷菜单补修为 B 级既有窗口生命周期事件转发，只把现有关闭事件送达既有菜单宿主。模型配置、授权、执行、Evidence、System Context、协议和存储边界未移动。使用隔离工作树和临时合成数据，未把原主工作区未提交文件纳入提交，未改个人模型配置或发起真实模型调用。

## 源码与补修

- PR214 最终测试头：`d7be7073b4446cbca0cdc839c1f4b83699537aa8`；PR215 汇合测试头：`78ec0fdfe959df4d8724d3832de585c94af8e812`，保留原 PR215 提交身份及 PR214 历史。窗口测试修正后又补上既有原生菜单关闭事件的宿主接线（见下条），其余生产源码与 b9b07dbd 相同。
- 原生 Quick Chat 菜单的关闭事件此前只发给 bar，宿主虽然已订阅却未收到；现在原生窗口隐藏后经现有 channel 清空宿主内容，下一次真实状态重新挂载并入场。选择、取消和切换到原生 enum Menu 共用关闭接线，不延迟系统隐藏或选择，不新增 IPC channel/payload、授权或执行。22 个宿主单元用例通过，另在窗口用例保留“关闭后菜单 DOM 为空”的实际断言。
- 修正 MotionDetails ref 返回清理的类型接线；保留生产 ref 和原生 details 语义。测试 VM 补 shared primitive/关闭准备接线，原焦点和后台执行状态断言保留。
- useMotionSettled 复用 visualMotion，按实际打开/对象代次释放入场 fill/过渡。移除初版组件固定 400/280ms 清理；背景 DTO 不变时保留引用，选中/高亮合法性仍单独核对；头像只按真实资源变化重读。
- 保留保存期间防重、失败恢复与 trigger ResizeObserver 定位；滑块当前输入不会被背景保存回读重置。档案已打开时不重新启动 push/cover 入场。
- 实测升级弹窗发现 CSS finished 先于原生终点事件取消 fill。Overlay 退出保留实际终点到原生 end/下一帧，沿既有 2s 硬上界处理停帧/无事件，减少动效、隐藏、拒绝保持静态收尾。升级采样保留中点、方向和终点断言，并观察原生 end 后 React 关闭提交；额外注入 360ms 渲染阻塞验证恢复。

## 本地结果

本地 Node 24.22、pnpm 10.22、Bun 1.4.4；CI 使用仓库所设 Node 25/Bun 1.2.17。桌面用生产 main/preload/renderer、真实 IPC/持久化，认知/延迟/失败/更新事件为受控合成输入，不访问个人数据。

| 范围 | 实际结果与限制 |
|---|---|
| 构建/类型/架构 | 完整 build、完整 typecheck 通过；共享退出补修后 desktop typecheck、renderer build、architecture/UI conventions 再通过。最终合并还以两平台 CI 为准 |
| 单元首次整批与修复 | 首次递归整批在并行负载下遇到 1 个 runtime 连续性时序断言；隔离重跑 28 项通过。desktop 发现 3 类旧 VM 未接共享组件及搜索聚合超时；修复夹具后原断言和搜索隔离重跑 35 项通过。不能称首次整批无失败 |
| 共享退出与关闭准备 | 最终 10 项通过，覆盖取消/反向、拒绝、静态、最终帧和硬上界 |
| 其他本地包 | TUI 813 项通过；desktop 后置 i18n/cancel 3 项；marketplace 6、更新日志/发布脚本 27、升级矩阵 1 项通过。依赖包整批其他项通过 |
| 设置/菜单/抽屉专项 | b9b07dbd 干净源码通过；12 设置分区往返、菜单 Escape 归焦/外点/快速重开、5 个档案 tab、原生高级区、草稿保留、宽窗 push/窄窗 cover/减少动效；renderer pageErrors 为空 |
| 强度保存/失败 | 设置与 composer 均用 650ms 保存延迟，每种成功/失败各观察 1100ms/66 帧，覆盖回执后的已开抽屉、popover DOM/透明度连续性；待保存几何保持，失败真实反馈出现后的自适应高度允许变化；失败恢复/丢弃保留原 API 责任 |
| 原生快捷菜单宿主 | 实际窗口专项通过，选择后菜单 DOM 为空；当前模型/强度、失败保留和跨 Bot 配置均正确；pageErrors 为空。22 个窗口单元用例通过；最终完整流程再次核对 |
| 图片授权/排版专项 | 78ec0fdf 干净源码通过；真实本地授权 IPC/存储、精确图片范围、键盘、未授权其他操作、宽窄/深浅/授权记录状态、完整命令内容均保留；合成 1px 图片，不涉及个人文件或云模型 |
| 升级弹窗专项 | 4f615f77 干净源码通过，生产内容与 b9b07dbd 相同（后者仅截图等待修正）；1280 深色、760 浅色、760 减少动效三例，并注入 360ms 阻塞；真实终点/关闭提交和下载错误/快速完成用例通过；没有实际下载或安装 |
| 完整 CI 同参数 Electron 冒烟 | **78ec0fdf 干净源码完整通过**，11 个顶层检查及任务/核验/记忆/权限/历史/设置/无障碍语义/诊断子场景完成；renderer pageErrors 与 mainAuthorizationErrors 均为空，隔离进程正常退出。两处强度每种保存再次采得 66 帧；原生宿主 DOM 清空、Evidence 编号和唯一图片授权卡均保留原断言通过 |

修复前的整条窗口运行没有直接通过：Quick Chat 曾在原生窗口新状态到达前点旧 DOM；技术详情与 Evidence 曾在原生 open 后、内容过渡提交前读取 innerText；图片授权夹具又重复追加生产目录已经投影的同 ID 消息。分别等待真实显示/内容、保留生产行并仅追加新 ID，始终保留原来的可见内容、单卡唯一性和授权存储断言。最后重新运行完整顺序得到上述通过结果，不把早期失败算作通过。

两个既有 standalone 入口在本次合成初始状态未到达目标场景（问题卡/历史行定位），不作为通过证据；本次使用 CI 完整顺序验证相应目标。

复现入口：`pnpm build`、`pnpm typecheck`、`pnpm architecture:check`、`pnpm test`；窗口脚本 `node apps/desktop/scripts/bot-shell-electron-smoke.mjs --accessibility --diagnostics --streaming --effort-stability --work-surfaces --output <repo 外临时目录>/report.json`。专项分别使用 `--surface-motion-only --effort-stability`、`--updater-only --updater-frame-gap`。窗口运行互斥，避免 OS 焦点互抢；临时输出与合成数据库不入库。

本地机器报告 SHA-256：完整流程 `afe690b99a95e969edee746829539eefedaf762ad18a0bd1d3eb999757fc341b`；6 图专项 `58f543787e3f278fc174f18a4fd24992cb8e132d89d62a513fdec15e159dbf50`；含 360ms 停帧的升级专项 `39c600cc4e613074be3eadebc072b23c3567b3042c6df248da55d6c1b02a6c53`。原始输出、trace 与合成数据库保留在仓库外，不提交到知识库。

## 图像自审

实现者本人审阅最终专项 6 张图：设置归档页、宽窗抽屉、窄窗覆盖、减少动效、设置模型菜单及 composer 模型菜单。分区与控件适配窗口，模型菜单无截断/退场残影；宽窗保留会话及草稿，窄窗保留覆盖层边界，减少动效焦点轮廓可见。另看升级弹窗深色宽窗/浅色窄窗前后共 4 图：退场后弹窗与 backdrop 消失，原主界面及 footer 42% 进度可见。截图本身不证明中间帧；中间帧和保存时序由上述采样断言负责。

早期图截在实际入/退场中，已将截图等待改成真实落定/DOM 退出，重跑后审阅最终图。评审非独立；不把合成图当真实模型、已安装签名包、读屏或全量无障碍验收。专项没有覆盖真实 IME、多屏、RTL、所有嵌套浮层/原生窗口及全部宿主，继续按 E13 在最终发布候选核对。

## 远端合并与本地同步

两条代码 PR 已按顺序 merge，未 force、未绕过失败检查：

| PR | 已验证 head / CI | 实际 merge commit |
|---|---|---|
| [214](https://github.com/ly-ccx/Peer-Agent/pull/214) | `d7be7073b4446cbca0cdc839c1f4b83699537aa8`；[40086013097](https://github.com/ly-ccx/Peer-Agent/actions/runs/40086013097) macOS/Linux 全部成功 | `979ad1fd8fcc5da615eb64d5a663a5ba26025317` |
| [215](https://github.com/ly-ccx/Peer-Agent/pull/215) | `78ec0fdfe959df4d8724d3832de585c94af8e812`；[40086015200](https://github.com/ly-ccx/Peer-Agent/actions/runs/40086015200) macOS/Linux 全部成功 | `7b6c9972906ec7faa814e2c191cf0452255f825e` |

最终远端 `PeerAgent/dev/0.1.0` 为 `7b6c9972`，与本地完整验证头 `78ec0fdf` 的文件 diff 为空，tree 为 `446b5f2fa15850652c35c4e96773443cc16a1983`。合并后再次清点代码仓 open PR 为 0。知识记录、计划、矩阵和共享规范通过 PR74 交付，其合并元数据以该 PR 为准。

本地原有 0.1.0 测试 checkout 在确认分支与工作区干净后 fast-forward 至相同 `7b6c9972`；Vite 对新 useMotionSettled 模块响应 200，原 Vite/Electron 进程保留。原生 Quick Chat 关闭事件补修属于主进程，当前常驻 Electron 需下次重启才载入；本轮隔离窗口已经运行并验证新主进程。未安装、替换或重启用户当前实例；主代码/知识工作区其他 dirty 保留。
