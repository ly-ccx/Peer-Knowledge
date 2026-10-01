# B5-04 网关与手机网页交接

日期：2026-10-01。状态：实现、本机门禁与浏览器证据完成，等待 Review / 双平台 CI。代码 `a24e009c`，基线 B5-03 `43765d84`；契约见 [b5-04-project-web.md](b5-04-project-web.md)。

## 实现

独立 project router / HTTP adapter / /bots 手机网页；账户会话鉴权与同源 Origin、严格参数/字段/32KiB正文，全部操作依设备当前绑定和逐机器人投影路由，电脑重新准入。无离线队列、重放或远程执行/批准。输入稳定 ID 与每次转发 correlationId 分开；只接受对应实际 socket handle 的结果，旧连接/旧关联/迟到结果不结算新请求。输入发送后的连接/授权变化及传输异常为 OUTCOME_UNKNOWN。

传输按认证状态/类型限制：旧类型4KiB，新投影128KiB，新请求32KiB，新结果2MiB；共享 protocol projection parser、设备及网关同校验。gateway 仅增加内部 protocol workspace 依赖。协议 test script 纳入根测试和 CI。HTTP socket空闲期限30秒覆盖20秒设备答复超时，保留请求正文期限。

手机页使用 SVG 头像、textContent、手机布局、统一控件、可读状态与电脑批准提示。未知结果保留原ID/正文/目标，跨机器人切换后仍重试同一条；所有失败都保留原关联以防首次已入队。打字期间晚读取不清掉草稿；晚任务/列表回答受 generation 保护；401/logout 清空私人数据，HTTP 导出前再查会话是否撤销。

## 验证

- `pnpm build`、`pnpm typecheck`、`pnpm architecture:check`、`pnpm test` exit0。Runtime976 / Desktop5228（5既有skip）/ TUI749 / Gateway200，0fail。
- 最后 protocol/parser/UI 小修后 `pnpm --filter @peer-agent/protocol build`，protocol完整227pass、Gateway完整200pass；full suite在这些小修前，最终提交由CI再次验证。
- 真配对 Ed25519 + 真实 loopback WebSocket + HTTP + 设备 setup + 原队列/SQLite：2集成case通过。并发同ID 4000中文收到同首次回执、原对话只一条；冲突正文/撤权/离线/跨源/未登录/附加字段/大正文拒绝。
- 路由关联/超时/重连/授权变化/关闭5case；HTTP字段/会话撤销4case；网页请求形状/未知同ID/切项目/401/退出晚回/草稿5case；共享projection3case。
- `node apps/gateway/src/project-web.browser-smoke.mjs` 最终pass，390×844暗色Chrome，pageErrors0。实际HTTP首回执被测试故意丢弃一次，键盘发送、同ID重试、唯一输入、脚本回复、任务摘要、电脑批准提示、退出清理通过。没有横向溢出。

## 浏览器证据与范围

- [证据JSON](evidence/b5-04-browser-20261001.json)
- [列表](evidence/b5-04-list-390-20261001.png)、[对话](evidence/b5-04-conversation-390-20261001.png)、[任务](evidence/b5-04-task-390-20261001.png)

这是桌面浏览器手机宽度，测试使用私有fixture账户会话、loopback transport seam和脚本回复，不是物理手机 / 已部署OIDC / 真实模型证明。生产无该认证旁路。源码可重跑；真实安装候选版、多入口模型及账号部署验收仍在B5-R/RC。未知消息保留在当前页面内存，刷新整页/退出将清空待确认输入，用户应先在电脑核对，不重新发送同正文。

## 下一步

B5-05设置页依赖B5-03已合入，可在本卡CI期间独立推进。代码/知识各自PR，Review后依授权合入；GA等待用户全面测试。
