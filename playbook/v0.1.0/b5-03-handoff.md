# B5-03 设备侧远程项目准入交接

日期：2026-10-01。状态：完成。代码 `4c70636c`，基线 B5-02 `31527990`；[CI 36879351025](https://github.com/ly-ccx/Peer-Agent/actions/runs/36879351025) macOS/Linux 均通过，Review 后 [PR #88](https://github.com/ly-ccx/Peer-Agent/pull/88) 合入 `43765d84`；知识 [PR #19](https://github.com/ly-ccx/Peer-Knowledge/pull/19) 合入 `6ccf239`。实施合同见 [b5-03-remote-access.md](b5-03-remote-access.md)。

## 交付与架构影响

四种远程操作的严格协议、当前本机逐机器人授权、真实 session 归属、绑定/委托/连接纪元/到期检查；输入只写共享队列，首次回执保存于已登记 device SQLite。队列写成功而回执未写的重试恢复首次输入，不产生第二次消息。成功只代表 received，不代表任务完成。

对话最新分页、任务摘要、待批准摘要采用字段白名单，去除本机路径、工具结果、Evidence、附件和批准动作。读取 await 后重新准入。4000 字 Unicode 请求及 50 条页面有独立帧预算；旧 M1 帧与操作保持原预算。实际宿主 onReady 装配共享 directory/inputQueue/getSession/wake，无远程执行端口。main.mjs 6 行增加、10 行删除。

本机设置默认关闭项目权限；旧单 workspace 配置只迁移查看。授权保存先于重新连接，版本变更即时复查。委托有效期固定，不随访问延长；过期拒绝。旧连接关闭回调不能覆盖替换连接；身份加载期间 stop 不会晚启动。

## 自测证据

- Node 25.9.0，pnpm 10.22.0。`pnpm build`、`pnpm typecheck`、`pnpm architecture:check`、`pnpm test` exit 0。
- 完整门禁：Runtime 976 / 0 fail；Desktop 5227（5222 pass / 5 既有 skip）/ 0 fail；TUI 749 / 0 fail；Gateway 184 / 0 fail。
- 最后新增实际 desktop 注册装配测试：`node --test apps/desktop/electron/main/project-agent/desktop-integration.test.mjs` 25 pass（完整门禁之后新增一项）。远程路径无新增模型执行通道，复用同一宿主队列且只落一条对话。
- 最后投影补齐持久 meta.sources，`node --test apps/desktop/electron/main/runtime-gateway/{remote-project-access,setup-remote-access}.test.mjs` 36 pass。
- 协议矩阵 51 pass；SQLite/存储登记 17 pass；传输 5 pass（真实握手状态机 + socket seam，4000中文/50×4000 emoji、超限、默认关闭）。这不是已部署手机端到端证明。
- 本地日志 `/tmp/peer-b5-03-{build,type,arch,all-test,assembly,final-focused,protocol,receipts,transport}.log`。日志不进入知识仓；结果可通过上述命令重新运行。

## 范围与后续

原卡必要路径扩展已先写入 Accepted 实施合同；没有新增 IPC、依赖、根存储或模型工具。B5-04 必须补网关投影及帧准入、路由与手机网页；B5-05 补设置界面与 IPC DTO。当前仅设备侧完成，不能声称手机功能 ready；正式发布及 RC-06 仍等待用户测试。
