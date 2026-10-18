# ADR95：进展驱动的持续执行

## 实施边界

- 设计先行：`6f224b9` 接受 ADR95，最终代码候选 `25b49d8f7783f22387b52faf1853d93efad53429`，沿用 [Peer-Agent PR163](https://github.com/ly-ccx/Peer-Agent/pull/163)。
- 不再注入默认累计 256 请求 / 2048 工具；核验不再按累计 96 请求 / 512 工具 / 5 分钟中止。12 轮 / 128 工具仍是核验每片的调度边界，单片超时、取消、权限和未知结果保护保留。
- 新 `work-budget-policy` 集中解释策略来源、显式上限、未知用量与精确旧默认迁移；`reply-recovery-admission` 供协调命令和只读卡片投影共同使用。未添加 IPC、工具旁路或存储位置。
- 每片保存已配对 Tool Result、Evidence、原生检查点和累计用量；无进展指纹保留已见事实，交替重复旧读结果或换路径重试同错不能无限续跑。
- 仅持有协调租约且有完整检查点的精确旧系统默认停止会迁移。保留计数、旧策略和迁移时间；显式预算、不明来源、取消、暂停、人工等待及未知执行结果不自动放行。
- 真正显式预算停止显示类型、用量、上限与来源；费用未知明确说明未知不等于零。后台不准入的继续按钮不显示，调整策略后才重新准入。
- 显式费用/Token 预算被另一执行占用时单列临时 reservation；释放后按原上限与实际用量恢复，不要求提高限额。预算占用与真实耗尽的守卫、只读投影及 Renderer 文案均有测试。

## 产品验收

最终源码绑定的 176 张必需截图已全部查看（30 张联系表及关键原图），实现者逐图填写 `review.json`，标准 Verify 通过。`result.json` 记录 runId、源码指纹和审查身份。当前 `review.json` 保留 5 项非阻断限制：浅色 Quick Chat 离屏合成、旧侧栏技术摘要、合成签收夹具旧说明，以及暂停详情和窄窗引用相邻预算说明处的浮钮局部遮挡。关键预算状态原图均完整可读，不把这些限制描述为全屏无重叠或原生外观验收。

## 可复现测试入口

| 场景 | 源码测试 |
| --- | --- |
| 生产 Runner 跨旧上限并重启：301 请求、2100 次唯一配对工具结果、一次正式交付 | `packages/runtime-node/src/project-agent/progress-execution.integration.test.mjs` |
| 精确旧默认停止从原生检查点恢复，256→257 请求、468 工具不重放；显式及不安全停止不迁移；宿主投影与 retry 准入一致 | 同上 |
| 核验 24 个切片、289 请求、2304 工具，受控时钟跨累计 24 分钟，首片证据可供最终报告引用 | `packages/runtime-node/src/project-agent/verification-continuation.test.mjs` |
| 相同读结果交替、相同错误换路径仍停止；失效切片回调不能再派发 | 上述核验测试及 `progress-continuity.test.mjs` |
| 真实 Responses 编码、Agent Executor、Runtime Projection、只读 File Provider、PermissionGrant、Evidence、原生续接：13 个真实文件、14 请求、13 个唯一工具调用 | `apps/desktop/electron/main/agent-host/verifier-continuation.integration.test.mjs` |
| 主 Bot/子任务/历史错误、静默等待与结果唤醒、技术阻塞接手及无进展停止 | `continuity.integration.test.mjs`、`repair-ownership.test.mjs`、`wake-wait.test.mjs`、`reply-failure-facts.test.mjs` |
| 显式次数/Token/费用上限、并发记账、未知结果与未知用量 | `work-budget.test.mjs`、`work-budget-policy.test.mjs` |
| Renderer 的真实预算、用量未知、限制调整和迁移状态及继续按钮 | `apps/desktop/renderer/src/project-agent/state/replyRecoveryState.test.ts` 及标准产品回归 |

## 覆盖限制

301/2100 与 289/2304 是生产协调器/预算守卫和核验续跑器中的受控执行结果，不能称为 2100/2304 次真实文件操作或真实云模型调用。13 文件测试实际执行本地 File Provider，但模型传输受控。标准产品包来自隔离源码 Electron，由实施者逐图自审（`independent=false`）；不代表安装 RC、真实云模型质量、完整读屏器或长期使用验收。

真实用户工作区、正在运行的任务、权限和历史记录未改；安装的 RC15 没有替换。本次不合并、不发 RC。最终测试、CI、截图指纹与验收结果见同目录 `validation.json`。
