# B5-04 网关与手机网页实施边界

日期：2026-10-01。状态：Accepted；实现须等待 B5-03 代码合入。负责人已授权完成 Beta5/RC 的必要路径、Review、合并及预发布；GA 等待用户全面测试。

## 边界

采用独立 remote-project-router，不扩展旧 task router。网关只存有界在途 Promise，不存输入或事实、不离线排队、不重放；身份来自已登录本机账户会话，绑定/委托投影来自设备当前连接。电脑逐请求重新准入为最终权限真源。

四个 HTTP 入口全部要求认证：GET /api/projects；GET /api/projects/:workspaceId/conversation?deviceId=&before=；GET /api/projects/:workspaceId/sessions/:sessionId?deviceId=；POST /api/projects/:workspaceId/input（严格 deviceId/inputId/text）。GET 无正文，未知或重复参数拒绝；POST 同源 Origin 和 JSON、32KiB 限制。列表聚合当前账户设备，每台仍是独立的在线准入，离线状态明确展示；单机器人操作离线 DEVICE_OFFLINE，已发送无答复 OUTCOME_UNKNOWN。

稳定 inputId 只用于本机幂等。每次转发另生成随机 correlationId，置于 remote.project.request/result 信封；结果必须同时匹配 correlationId、requestId 和实际认证连接 handle，且返回前重查账户设备绑定及当前连接。迟到答复、另一设备或旧纪元不能结算新请求。这个信封关联是 A 级协议补齐，不改变 capability / ToolCall / PermissionGrant / Evidence。项目原操作请求字段保持 B5-03 精确集合。没有新增远程批准或工具执行。

项目投影帧≤128KiB、结果≤2MiB、请求≤32KiB；已认证在线的对应类型才允许较大帧。旧握手/heartbeat/task 仍≤4KiB。共享 protocol 导出投影形状解析，设备与网关使用同一校验，避免重复 schema 漂移；gateway 只增加既有 workspace protocol 包依赖，不增加外部依赖。

独立 /bots 页面及静态 project assets。手机优先列表/对话/任务摘要，头像 SVG，控件统一样式、状态有文本、键盘标签和 reduced-motion；内容用 textContent，无 innerHTML。每条 input 未确认时保持原 ID/正文/设备/机器人，提供“可能已送达”与同 ID 重试；切换机器人不丢失各自待确认输入。401、logout 清空私人页面数据，晚返回不能重新显示；停留页可刷新对话。待批准只显示需要电脑处理。

## 必要路径

原卡 router/http-server/web-surface 之外补 account-http（认证组成）、device-websocket（逐类型帧、投影、真实连接结果关联）、main/package 描述（删除已过时“路由未开放”文案）、gateway package/lock（内部 protocol 引用）。protocol remote-access/index/test/package 与 runtime-node remote-device-connection/test 补共享投影校验和关联信封；protocol test script 纳入根测试/CI，避免新增协议矩阵未执行。新 remote-project-http、project-web-surface 与对应单元/真实 socket/网页脚本/截图测试；测试专用 fixture 与手动 browser-smoke 不带认证旁路进入生产。无新增本机存储/IPC，desktop main 不改。

## 验证

认证/同源/正文/参数矩阵；在线/离线/未知结果；同稳定 ID 独立关联、并发重试、迟到结果、旧连接/跨设备拒绝；真实 Ed25519 配对+WebSocket+HTTP+本机队列/SQLite 幂等；Unicode 帧与旧 M1 回归。浏览器 390px 截图、键盘发送、任务详情、401/晚返回/重试测试。完整 build/type/architecture/Gateway/Runtime/Desktop 与双平台 CI。截图为桌面浏览器手机宽度，不能称实体手机实测。
