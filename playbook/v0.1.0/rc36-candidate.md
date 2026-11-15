# RC36 候选与发布回执

创建时间 2026-11-03
最后更新 2026-11-05
状态为 RC36 已发布，最终工程、产品验收、双平台 CI 与线上发布核验全部通过。

## 候选

版本为 `0.1.0-rc.36`。源码 `793c9a5223e7ba12d3f83f2d99c3e8a0bc2b7618`，tree `b247d6a625aacc5910a4b2dd8246e6a75c5d3017`，开发线为 `PeerAgent/dev/0.1.0`。冻结时开放 PR 清单为空。最终合并提交与必需 CI 通过的 PR275 head `4fbbe519` 的 tree 相同。于 2026-11-05T09:00Z 重新冻结，完整工程和产品门禁已通过。

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
| [#275](https://github.com/ly-ccx/Peer-Agent/pull/275) | Windows ASAR 路径与 SDK 测试生命周期 | `793c9a52` |

知识 PR114—118 已合入。ADR119 的完整认知代次控制仍为 Proposed，本版实现范围见 ADR120。

## 前序候选 50934073 的验收

该前序候选冻结后全部通过构建、全仓类型、架构与 UI 约定、IPC、Rust build/test、Runtime 打包内容与外部安装、产品回归脚本契约、更新日志、版本、发布源与发布准备检查。全仓测试中 Node 9189 项通过、5 项跳过，Bun 849 项通过，另有工程脚本、marketplace、changelog 和升级矩阵检查通过。原任务停止与恢复用例随 Runtime 再次运行。OpenUI 窗口三项单独串行运行通过。

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

标签、GitHub Release、npm 与 Pages 已完成发布核验，详见下节。在线模型、正式安装包、系统输入法和辅助技术的历史专项各自绑定原提交，本轮源码测试和受控模型不替代这些范围。个人运行实例和真实任务数据保留。


## 首次标签构建与候选撤回

2026-11-05 首次标签工作流 [Release41977250103](https://github.com/ly-ccx/Peer-Agent/actions/runs/41977250103) 中 macOS 签名公证与 Linux 构建成功，Windows 的 Verify packaged runtime entries 失败，后续 CLI、Release、npm 未执行。四个 npm RC36 版本与 GitHub Release 均核对为 404，完成的失败记录已保留后删除未发布标签。Pages 首次部署已成功，待最终源码再次部署。

定位到校验脚本的 Windows ASAR 路径分隔符错误。目录枚举返回原生反斜杠，正斜杠筛选漏过全部主进程 imports。读取 API 内部按本机 path.sep 分割目录，原脚本直接传正斜杠使交互包误报缺失。PR275 `22e510af` 在读取边界统一 path.normalize，并将目录筛选转换成可移植表示。新增六项跨平台正反用例，原脚本三项 Windows 断言失败，修正后六项通过，仍拒绝真实缺失依赖与子路径。

以上工程与 255 张产品验收绑定旧候选 `50934073`。PR275 合并后重新完成最终组合门禁和产品 Capture/Review/Verify，后续记录为准。


### PR275 后续测试宿主修正

Linux 多次 Test 超时经原生资源诊断定位为 SDK 策略测试完成后的 2124 个 FSEventWrap。Vite 合并文件和 inline 配置会忽略 null，原 server.watch=null 未生效，异步目录扫描与关闭发生竞争。先前关闭预打包和隔离缓存后，SDK 断言及 server.close 已完成但仍未退出，因此没有将该改动称为修复完成。最终在 config 钩子直接关闭监听，并断言实际配置为 null、监听列表为空。移除临时阶段及全量句柄日志，保留隔离缓存与文件超时。Linux 隔离环境五次正常完成退出，macOS 同组六项通过；远端最终 head 继续验证。失败证据依次为 CI41978471022、41980977595、41984974816、41988181988。


## 最终候选 793c9a52

PR275 最终 head `4fbbe519` 的 [CI41991817239](https://github.com/ly-ccx/Peer-Agent/actions/runs/41991817239) Linux 成功。macOS 第一次根 Test 步骤超时，桌面全部完成，TUI Bun 停在 goal-bridge 文件，保留失败记录。按既有约定复跑失败任务一次，完整测试及桌面交互 smoke 均成功，未修改源码。此前一次 macOS 截图窗口尺寸恢复 promise 回收也保留为失败，后续完整 smoke 成功。最终组合候选的构建、工程、测试、Capture/Review/Verify 已重新执行并通过。

最终候选全量构建、全仓类型、架构/UI/SVG、IPC（405 channels、439 preload、354 registrations）、Rust locked build/test、发布源与准备检查、版本与更新日志、产品契约、runtime 打包内容及外部安装全部通过。Node 9,195 项通过、5 项跳过，Bun 849 项通过。另有工程脚本与升级矩阵通过。OpenUI 原生窗口三项串行通过。

最终产品包 runId `06effc8e-36a2-4d44-a960-20c3af29c195`，sourceFingerprint `806e94fb03fca8fd33b852f97e86a251c4cc48ad92074d466a3dfc14764a41c5`。255 张截图全部经带标签拼图复核，透明 Quick Chat 另在匹配深色背景复查。每张 SHA256 和具体观察写入 review.json，2026-11-05T09:44:53.160Z Verify 通过，无未解决阻断项。实施者自审，independent=false。受控模型、源码 Electron、无完整读屏与长时间验收的限制继续保留。

合并后 [CI41998768885](https://github.com/ly-ccx/Peer-Agent/actions/runs/41998768885) Linux 成功。macOS 全量 Test 成功，Electron smoke 在约 15 分钟后失败，主日志未给出具体断言。下载保留的 report、failure screenshot 和 trace 后，报告定位为任务折叠反转的逐帧跳变断言。两次采样间隔 150ms，高度差 70.75px，整体范围 85.375px，超过现有 80% 阈值。打开和关闭最大采样差为 21.58px 和 20.03px。该记录可见采样缺口，尚不能仅凭该次报告区分宿主调度与真实渲染卡顿。未修改源码或断言，复跑失败任务一次，attempt 2 的完整 Test 与 Electron smoke 均成功，双平台最终结论通过。该单次采样失败和复跑成功都保留，未将其描述成确定修复。


## 最终发布回执

2026-11-05，标签 `v0.1.0-rc.36` 已推送，annotated tag object `101289f9b8cf5f2185efe468109ceba09f8f78f5`，目标源码 `793c9a5223e7ba12d3f83f2d99c3e8a0bc2b7618`。推送前开放 PR 再核对为空，以上十个 PR 全部包含在最终候选中。

[Release42008952591](https://github.com/ly-ccx/Peer-Agent/actions/runs/42008952591) 所有步骤成功。三平台 Desktop runtime 打包校验成功，macOS Developer ID 签名及公证成功。darwin-arm64 与 linux-x64 CLI 归档的真实 `peer --version` 校验成功。GitHub Release 与四个 npm 包发布成功。[Pages42008952590](https://github.com/ly-ccx/Peer-Agent/actions/runs/42008952590) 从同一最终源码部署成功。

[下载 RC36](https://github.com/ly-ccx/Peer-Agent/releases/tag/v0.1.0-rc.36) 为 prerelease，包含下列 14 个非空 uploaded 资产。核对 GitHub 资产 SHA256，下载三平台 beta YAML 并校验其版本、文件名、文件大小与摘要格式，清单自身 SHA256 与 GitHub digest 一致。本节验收范围为发布资产与更新元数据，安装后交互的覆盖限制见文末。

| 资产 | 字节数 | SHA256 |
| --- | --- | --- |
| `beta-linux.yml` | 559 | `f55d2ac663596ceba06485446830837cdce86daa118a0ffcdebeb1b2888b9b8d` |
| `beta-mac.yml` | 530 | `191765d05e6327af229f1313a4aaf2d2779e6bc2e0e483355ceffd6826868b07` |
| `beta.yml` | 367 | `1252bf16ac0a05b574cc653258ffcbd4a02825431ea1dd4ffbf59cc29a9ada2f` |
| `builder-debug.yml` | 1462 | `68cc0b67001f873d78a3c179dacf6e094dc9dbbe94d8858d72427ad92b9b1f8c` |
| `Peer-Agent-0.1.0-rc.36-arm64.dmg` | 148303331 | `3bbb46be9cabf46d7977a602aba0fa0848911b64031b0dc02679afbcb80e045b` |
| `Peer-Agent-0.1.0-rc.36-arm64.dmg.blockmap` | 151921 | `bdf4d94a90dfbcc2a2f201d81785d4bf2891fedaeebcccd75a2941c71321c23f` |
| `Peer-Agent-0.1.0-rc.36-arm64.zip` | 145837300 | `8df1441e4a469cc8a7d056d03ef109707047cd3c011224127e97b367dc60eb6d` |
| `Peer-Agent-0.1.0-rc.36-arm64.zip.blockmap` | 149734 | `7766629e94746a5ceb883cde74e5a23d338935fe0715e28fcbcf9257af2d71ff` |
| `Peer-Agent-0.1.0-rc.36-x64.AppImage` | 148434943 | `dc231f707f2756903520fc3ac9c999bf185f6b3d835de436730beb0c4e2f4703` |
| `Peer-Agent-0.1.0-rc.36-x64.deb` | 119150780 | `3af3a7fe72af71c154d08ef451e1254509d432d47169c76e04cc092e35d8db48` |
| `Peer-Agent-Setup-0.1.0-rc.36.exe` | 228158707 | `a37fccdaf8947908ccfd584ff54b4c4bdd89c1dc61b8f5098a28ac578a18f5c2` |
| `Peer-Agent-Setup-0.1.0-rc.36.exe.blockmap` | 235383 | `d9f31e126c68a50e89141f68d913e5103acaab97de1114441036966af1602c47` |
| `peer-darwin-arm64.tar.gz` | 24259521 | `0178ac76ee2602415e17499f35c52204a6d523f0ce66f49458ae036a1c92df5a` |
| `peer-linux-x64.tar.gz` | 47921571 | `fa58ca840dceae5a4b38a591dbac98bc6a33e15d6d37da12aedb4655fc494078` |

四个 npm 包 `@peer-agent/protocol`、`@peer-agent/runtime-core`、`@peer-agent/runtime-sdk`、`@peer-agent/cli` 的 `0.1.0-rc.36` 版本与 tarball 均可读取，`rc` 为 `0.1.0-rc.36`，`latest` 保持 `0.0.18`。发布完成后的首次查询曾遇到版本 404 与旧 rc 元数据，随后 npm 规范端点四个版本和标签均验证成功，未重复发布已有版本。

Pages 首页、用户文档、Changelog 页面、manifest 与 RC36 双语数据均返回 200。manifest 的 latest.beta 为 `v0.1.0-rc.36`，generatedAt 为有效时间，目标版本中英文内容非空。

线上联合核验完成于 `2026-11-05T10:29:22.824Z`。本版验收为实施者自审，使用受控模型及源码 Electron。真实在线模型、安装后交互、完整读屏与长时间运行的覆盖限制保留。
