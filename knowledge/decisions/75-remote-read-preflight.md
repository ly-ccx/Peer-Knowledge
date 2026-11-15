# 75. 远程读取预检：通过不等于获得执行权

创建时间：2026-09-26
最后更新：2026-11-15（跨 ADR 对齐：补注 [ADR 85](85-project-agent-hosts-inputs-and-surfaces.md) 决策 8 的 4 个 opt-in project 操作与远程无授权底线）

## 状态

已实现，本文按 0.0.18 代码补记（P0-6）。原决定没有单独的 ADR 文件；代码注释与网关实现一直称它为 ADR 75。本文不新增能力。

`design/product/remote-access-simple-implementation.md` 是之后的简化方案（文件凭据、扫码授权），尚未实现，不取代本文已经落地的预检边界。

## 级别

A 级。远程入口的协议、准入和「网关不持有执行真相」都由本文固定。

## 关联

- `packages/protocol/src/remote-access.ts`（`REMOTE_PROTOCOL_VERSION = 1`，`parseRemoteReadRequest`，`admitRemoteRead`）
- `apps/gateway/src/remote-task-router.mjs`（只中转）
- `apps/desktop/electron/main/runtime-gateway/remote-goal-read.mjs`（设备侧再次校验后才读）
- `packages/runtime-node/src/remote-device-connection.mjs`（设备自己发布的委托投影）
- [ADR 85](85-project-agent-hosts-inputs-and-surfaces.md) 决策 6、8（0.1.0 将本机 `workspaceId` 与这里的委托名单对齐，并在同一条预检链上开放 4 个显式 opt-in `project.*` 远端操作：`project.list`、`project.snapshot`、`project.open` 与受约束的 `project.message`；远端无权限授权能力、`remote_*` 执行受显式委派策略与只读/主 Bot 边界约束）

## 决策

1. **M1 只有 `task.read`。** 线上形状是 `type: 'task.submit'`、`operation: 'task.read'`，字段集合固定。多一个字段、少一个字段、版本不是 1、操作不是 `task.read`，一律 `INVALID_REQUEST` 或 `PROTOCOL_UNSUPPORTED`。没有 shell、路径、任意参数或写入。
2. **预检通过不等于获得工具执行权。** `admitRemoteRead` 只决定这次读取能不能进行。它不创建 PermissionGrant，也不投影任何工具。
3. **上下文由本机构造。** `RemoteReadContext`（绑定、委托、任务归属、是否在线）来自设备自己的状态，不从请求体里取。
4. **拒绝码按这个顺序成立即可，实现按代码里的顺序判断：** 身份未绑定或绑定版本不符、委托过期或已撤销或版本不符、工作区不在委托名单、不允许读任务、不允许导出结果、任务不存在或不属于该身份与工作区、设备离线、连接纪元过期、请求已过期或寿命超过 30 秒。
5. **网关只中转。** 它不保存执行真相，不排队，不重放，不做权限决定。版本、纪元和工作区名单来自设备在这条连接上发布的委托投影，不来自浏览器。发出后没有应答的请求记为 `OUTCOME_UNKNOWN`，不是失败：设备可能已经执行。再次提交是新请求，不是重放。设备离线直接拒绝，不进入队列。
6. **设备在执行前再查一遍。** 网关放行之后，本机 `remote-goal-read` 仍用本地任务存储核对归属。错误信息不得带出本机路径或内部异常文本。

## 不做什么

- 不做远程任意工具执行、远程写文件或远程审批（PermissionGrant 授权与破坏性/执行决策始终留在本机策略与本地交互确认中；即便开启 [ADR 85](85-project-agent-hosts-inputs-and-surfaces.md) 决策 8 的 4 个 opt-in project 操作，也不得未经显式受控委派策略在远端批准权限或直接执行任意本机工具）。
- 不把 Gateway 变成任务或 Evidence 的存放处。
- 不在本文里改身份存储（钥匙串或文件）和扫码授权。那是 `remote-access-simple-implementation.md` 的范围，实现前仍是设计。
