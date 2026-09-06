# 全局后台任务管理

创建时间：2026-09-05
最后更新：2026-09-05

状态：已实现并通过 macOS 定向回归与独立 Electron 验收（A 级运行时边界变更；其他平台尚未实机验收）

## 决定

后台任务由当前设备的 Peer 本地运行时全局托管。会话是来源，不是所有者；工作区是项目关联和筛选维度，不是进程生命周期容器。切换、关闭、删除来源会话不停止已经接受托管的任务。界面显示同一份运行时记录，不维持另一套进程事实。

依据：产品北极星 `../../design/product/peer-product-alignment.md`；治理基线 `20-architecture-governance.md`。

## 诊断与因果链

问题是进程存在而受管任务记录缺失，不是端口标签的视觉问题。已观察到普通 shell 使用 `&` 后命令完成、服务存活；模型可见 bash 仅有 command，适配器只传 command，而底层另有后台参数和任务管理器。

主要假设：工具投影和参数传递未进入后台登记分支。反证方法：通过实际工具到 provider 启动服务，检查同一 taskId 是否出现在全局列表并可停止。修复链为 Manifest/Projection → Tool Call → PermissionGrant → Provider → 全局任务记录/Evidence → IPC 协议 → UI。不通过扫描系统端口或从日志匹配 URL 伪造托管状态。

## 执行与授权边界

- 前台命令继续使用会话隔离 shell，cwd、export、虚拟环境不得跨会话共享。前台超时、取消和会话销毁规则保持兼容。
- 后台启动必须明确声明，完成本地权限检查及 hook 决策后才创建进程。返回接受托管的 taskId，不把接受托管称为服务已就绪。
- 后台运行不套用前台默认短超时；显式超时仍按约定清理。
- taskId、toolCallId、启动工作区、来源 conversationId、命令、启动时间、状态、退出结果、日志 artifact 构成可追溯记录。删除会话不抹去来源标识，不泄露来源会话聊天正文。
- 全局可见不构成模型停止授权。显式停止按目标 taskId 或 toolCallId 走既有权限/Evidence 链；隐式“停止当前任务”只能解析调用会话的前台任务，不能回退选择其他会话的后台任务。
- 用户全局管理视图可停止明确选中的任务，依然由 main 执行而非 renderer 操作进程。
- 本轮不扩展跨设备、系统进程接管或应用退出后常驻。正常退出 Peer 应清理受管进程组；终态以实际退出为准，必要时 TERM 后升级 KILL。异常应用崩溃不能宣称具备守护服务保证。
- 不自动接管或停止当前 5198 服务；测试只操作自己创建的临时端口和进程。

## 状态与展示

后台任务记录是单一状态来源，位于应用级本地运行时。会话切换不重建管理器。全局入口在无选中会话时仍可用；会话关联视图只是同一数据的筛选。产品名称为“后台任务”。运行中、停止中和终态须与实际进程生命周期一致。

跨 main/renderer 数据使用 protocol 类型和受检 IPC 声明。日志有界或通过 artifact 读取。服务地址只有获得受管进程的监听证据后才展示为已确认服务；任意 stdout URL 不足以证明监听。启动宣告、监听验证、进程退出须能区分。

## 验收矩阵

每格为独立命名测试；全部完成前不宣称交付。

| 执行方式 | 同会话 | 切换会话 | 删除来源会话 | 显式停止 | 应用退出 |
|---|---|---|---|---|---|
| 前台命令 | foreground_same_session：环境复用 | foreground_switch_session：环境隔离 | foreground_delete_source：会话 shell 清理 | foreground_explicit_stop：只停选定会话 | foreground_app_exit：全部前台清理 |
| 受管后台 | background_same_session：返回并登记同一 taskId | background_switch_session：B/无会话仍见同一任务 | background_delete_source：保活且可管理 | background_explicit_stop：目标进程退出及端口释放 | background_app_exit：进程组清理 |

附加必测：权限拒绝不启动；跨会话隐式停止不选中后台任务；后台无前台默认超时；既有 shell/hook 回归；视图不由当前会话裁剪；日志 URL 不冒充服务；IPC 生成一致；desktop 构建；真实临时端口服务经受管启动，在另一会话读取同一 taskId、来源、日志及服务信息，前台调用结束仍可访问，停止后端口释放，finally 自行清理。

## 已验证的实现与限制

- 全局任务按规范化 data home 共享；前台 shell 按工作区、来源会话保持隔离，应用负责统一释放。
- 运行中 stdout/stderr 展示最新 32,000 字符尾部；结束后保存的 artifact 采用既有 2,000,000 字符上限并标明截断。日志证据文件不是无限保留的完整录制。
- TCP 观测仅查询受管 POSIX 进程组的 `lsof` LISTEN 结果，不从日志 URL 推断 HTTP 协议或可用性。缺少 `lsof`、观测失败和 Windows 均返回无观测地址，不扫描接管其他进程。Windows 的进程树清理尚未取得实机证据。
- 停止时等待进程组清理，再写终态；已覆盖父进程先退出但子进程忽略 TERM、父子都忽略 TERM，两种情况均验证端口可重新绑定。正常应用退出复用现有 composition root 的异步 dispose；不承诺异常崩溃后清理。
- 复核入口（相对代码仓）：`global-background-tasks.test.mjs` 的十格矩阵、真实 HTTP 服务、来源删除与端口释放；`managed-background-lifecycle.test.mjs` 的日志上限和进程组清理；`backgroundTaskPresentation.test.ts` 的全局视图模型；Desktop 的 `typecheck`、`build`、`ipc:check` 及根 `architecture:check`。
- 独立 Electron 交互验收使用生产全局按钮/视图、preload、IPC、投影启动和应用任务表，不加载用户数据目录。构建 Desktop 后执行 `PEER_BACKGROUND_UI_SMOKE=1 node --test apps/desktop/electron/main/global-background-service-smoke.test.mjs`，覆盖空态、跨来源可见、日志、实际 TCP 端口、停止拒绝提示、显式停止与端口释放。测试夹具不是运行时能力旁路，也不会启动或停止 5198。

## 非目标

不把所有 shell 全局化，不将 `&` 解释为自动授权托管，不通过 UI 假条目遮掩漏登记，不修改当前预览服务，不扩大 renderer 能力或另建能力执行旁路。
