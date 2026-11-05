# RC36 候选与发布回执

创建时间 2026-11-03
最后更新 2026-11-05
状态为最终候选工程、产品与双平台 CI 均通过，准备推送 RC36 标签。

## 候选

版本为 `0.1.0-rc.36`。源码 `5093407395d28d7cf650f43bb4eff00493e60c9a`，tree `f15f5d3572d667be29afa24e937f42fb99078f34`，开发线为 `PeerAgent/dev/0.1.0`。冻结时开放 PR 清单为空。最终合并提交与必需 CI 通过的 PR271 head `b9dfc720` 的 tree 相同。冻结后在同一源码重新完成工程门禁。

用户先暂停发布，要求核对停止与明确恢复。隔离验证修正后，用户恢复发布，并于 2026-11-05 明确接受 ADR118 首期范围，纳入 RC36。知识 PR118 已合入 `db4b917b`，交互结果默认关闭。

## 全部合入的代码 PR

| PR | 内容 | 合并提交 |
| --- | --- | --- |
| [#266](https://github.com/ly-ccx/Peer-Agent/pull/266) | feat(ui): keep full task conversations outside collapsed details | `7d21f7d2` |
| [#267](https://github.com/ly-ccx/Peer-Agent/pull/267) | fix(prompt): improve project bot investigation strategy | `fcf0d8c3` |
| [#268](https://github.com/ly-ccx/Peer-Agent/pull/268) | fix(runtime): preserve waits and recover retained takeover state | `ca61670b` |
| [#269](https://github.com/ly-ccx/Peer-Agent/pull/269) | docs: require evidence-backed delivery and scoped validation for every change | `fef3d01b` |
| [#270](https://github.com/ly-ccx/Peer-Agent/pull/270) | fix(runtime): 统一父协调处置并接通资源等待闭环 | `160a518c` |
| [#271](https://github.com/ly-ccx/Peer-Agent/pull/271) | release: prepare v0.1.0-rc.36 | `50934073` |
| [#272](https://github.com/ly-ccx/Peer-Agent/pull/272) | fix(tui): unify the bot bind screen and keep typing focused | `73487366` |
| [#273](https://github.com/ly-ccx/Peer-Agent/pull/273) | fix(tui): show the user message time at the right edge | `516c619a` |
| [#274](https://github.com/ly-ccx/Peer-Agent/pull/274) | 实现 ADR 118：OpenUI 交互结果与受管维护 | `3fbb062f` |

知识 PR114—118 已合入。ADR119 的完整认知代次控制仍为 Proposed，本版实现范围见 ADR120。

## 工程验收

冻结后全部通过构建、全仓类型、架构与 UI 约定、IPC、Rust build/test、Runtime 打包内容与外部安装、产品回归脚本契约、更新日志、版本、发布源与发布准备检查。全仓测试中 Node 9189 项通过、5 项跳过，Bun 849 项通过，另有工程脚本、marketplace、changelog 和升级矩阵检查通过。原任务停止与恢复用例随 Runtime 再次运行。OpenUI 窗口三项单独串行运行通过。

macOS 源码产品采集完成。255 张必需截图逐张经 64 张带原图标签的审查拼图核对，透明 Quick Chat 截图另在对应深色底复查。每张原图 SHA256 与具体观察均写入 review.json，未改动原图。`qa:product:verify` 于 2026-11-05T05:36:53Z 通过，runId `1012fcbd-f1b8-4c37-bd04-1ab5a24c8382`，sourceFingerprint `3dbbc3b220fdbfe751055921e7d7057d18462152ef4c791609dab7fd73be531b`。无未解决的阻断发现。审阅由实施者完成，independent=false。交互断言覆盖停止、显式继续、冷恢复、权限、任务核验、草稿、焦点、历史阅读、输入与共享界面。

合并后 [CI41972274888](https://github.com/ly-ccx/Peer-Agent/actions/runs/41972274888) 的 macOS 成功，Linux Test 步骤在 15 分钟超时。日志表明首段 6227 项已结算（6220 通过、7 跳过），二段的 Vite SDK 策略文件未产出测试结果。先前相同 tree 的 PR271 双平台 CI 成功。失败日志保留，未改动源码复跑失败任务，attempt 2 的 Linux 完整测试与桌面交互 smoke 均通过，macOS 保留成功结论。该超时未在本地门禁、相同 tree 的前序 CI 或本次复跑中重现，具体底层原因未确定，保留为测试基础设施的间歇性问题。标签前再次核对开放 PR 必须为空。

## 已保留的失败与修正

- PR270 首次 CI 揭示旧事件托管、停止回复表示及测试目录资源构造的回归。保留旧断言并补上缺失当前事实时阻止关闭的检查。后续整合通过。细节见 ADR120 §14.1。
- 停止回执先于落盘会在收尾前退出后自动续跑。现在协调日志先封闭准入，迟到的子结果留待明确恢复。原工作和 checkpoint 继续沿用。
- 整项恢复遗留停止范围会屏蔽宿主等待。恢复操作全部结算后回写当前范围和 end，历史控制回执保留。含混旧状态保守停止，沿原暂停及明确恢复路径处理。
- 两个并发整项控制曾共享 pendingControl。按 work 串行结算，较早恢复不能覆盖后来停止。未结算停止期间的新恢复被拒绝。
- 宿主在停止卡写入前退出会缺失继续入口。新宿主从原停止事实和 checkpoint 恢复同一 attempt 的入口。
- PR272 双平台 CI 复现点离输入框后首字符丢失。修正提前返回和字符转交，补充原输入框焦点，保留已有快捷键与输入保护。
- PR274 的旧 TUI 测试要求成功正式回报后再次请求模型。改为从真实 Tool Result 与规范回复核对固定引用，并断言两次请求。
- Linux 新 Electron 用例先因没有显示服务失败，补上正常运行和重试的 Xvfb。后续隐藏窗口截图不稳定，隔离 Linux 测试改为实际绘制。
- 组合测试的窗口并发及最后窗口关闭会干扰驱动生命周期。窗口用例串行执行，测试应用由驱动在关闭断言结束后退出。保留原保存、关闭、来源与截图断言。

## 产品与发布范围

README 中英文已检查并更新源码版本与可选交互预览入口。双语 release notes、CHANGELOG、docs 用户文档和生成站点日志已更新。可选预览保持默认关闭，Linux 受管清理的部署门槛见 ADR118 §24.1。

本轮 Linux x64 隔离容器的三项 OpenUI 窗口用例串行通过，覆盖原生重开、SDK 组件和工作区交回。此前 64MiB 共享内存容器中并发运行出现截图或目标进程失败，该失败保留，不计通过。

标签、GitHub Release、npm 与 Pages 尚待发布核验。在线模型、正式安装包、系统输入法和辅助技术的历史专项各自绑定原提交，本轮源码测试和受控模型不替代这些范围。个人运行实例和真实任务数据保留。
