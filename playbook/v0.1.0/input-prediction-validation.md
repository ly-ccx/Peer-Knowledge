# 智能输入建议：实施与提前功能验证

创建时间：2026-10-31
最后更新：2026-10-31
状态：源码功能提前验证通过，最终提交、19 项场景与 8 张图的自审／hash verify 已绑定。不是版本／RC 发布验收。

本轮依据用户“完整做完，自己独立验证整个功能”的后续指令，实施 [IP-00—IP-06](input-prediction.md)，并提前验证本功能。原方案的暂不编码限制已解除；没有发布、安装或重启用户实例。实现者亲自完成检查，`independent=false`，不称为独立第三方复核。

## 交付身份与入口

代码在 `codex/input-prediction`，基线为 RC31 开发线 `73ff763a`；最终代码提交为 [`c78f861f`](https://github.com/ly-ccx/Peer-Agent/commit/c78f861f0e23e71ae6dbf655f8bf62bae8965683)，[代码 PR249](https://github.com/ly-ccx/Peer-Agent/pull/249) 目标为 `PeerAgent/dev/0.1.0`；当前未合并／发布。知识在 `codex/input-prediction-implementation`，基线为知识 main `2f83d5f`。两个原工作树保持原状，原知识仓两份在制文件的 SHA-256 与启动时一致；没有夹带原工作树修改。

Desktop 主 Bot 与经典输入框均支持空草稿下一句、末尾后缀续写、Tab／无修饰右方向键和明确按钮采纳。建议仅是呈现数据，采纳变成一次可撤销草稿编辑；原发送、回执、授权、执行与 Evidence 链保持原所有者。设置在通用页“智能输入建议”：默认关闭，需明确选择 `input_predictor` 模型；续写未发送草稿另有开关和外发说明。没有路由、预算、足够公共上下文或必需限制无法保留时不建议。

架构与取舍见 [ADR 115](../../knowledge/decisions/115-input-prediction-and-draft-boundary.md) 与 [完整方案 §16](../../design/product/peer-input-prediction.md#16-首版实现收敛2026-10-31)。当前包不包含多候选、逐词采纳、主动检索、Quick Chat／TUI／CLI／只读任务输入支持。

## 实际运行及结果

构建与验证命令使用 Node 25.9.0，Electron 沿锁文件解析到 41.7.1；依赖沿既有锁文件离线安装，没有新依赖。

| 检查 | 实际结果 |
| --- | --- |
| `pnpm build` | 全工作区通过，含 runtime、Desktop、TUI 与既有凭证 Helper；最后归焦改动后另跑 Desktop build 通过 |
| `pnpm typecheck` | 全工作区通过；最后归焦改动后另跑 Desktop typecheck 通过 |
| `pnpm architecture:check` | 治理与 UI/SVG 约定通过，最后归焦改动后复核通过 |
| Desktop `ipc:check` | build／包测试中通过：393 channels、417 preload operations、342 main registrations；预测新增四个固定 owner 端口 |
| 预测相关专项 | 50 项、0 fail、0 skip；最终提交以 `node --test --test-concurrency=1 …` 运行。覆盖 Protocol、控制器、Provider、Context、host、凭证 Worker、预算与编辑事务，含既有路由回归 |
| runtime-node 全量 | 1637 项中 1636 首轮通过；既有 runtime-host 优先抢占时序用例并发压力下未赶上断言，原文件隔离重跑 9/9 通过，未删除断言或改运行时代码来绕过 |
| 其余包全量 | `pnpm --filter '!@peer-agent/runtime-node' -r --if-present test` 通过；Desktop 主批报告 6133（6128 pass、5 既有 skip），附加批 3/3；TUI 817/817；其余包均通过 |
| 根补充检查 | ui:test 8/8；marketplace 6/6；changelog／发布脚本测试 27/27；upgrade 1/1 |
| 源码 Electron 功能包 | 19 个具名场景、8 张必需截图；最终提交重复捕获后逐图自审并 hash verify 通过，结果见随附 JSON |

全量测试不是一次无失败的 `pnpm test`：上表如实区分首次时序失败、隔离重跑与其余包补跑。过程中发现凭证测试夹具人为等待 300ms，在重型并发负载下消耗了 1 秒 Helper 截止的大部分余量；缩为 50ms，仍保留真实 Worker／子进程、主线程 heartbeat、真实凭证结果与取消断言，最终 50 项顺序通过。没有新增 skip。早期构建产物与测试并发更新造成的导出不一致结果已作废，不用于本回执。

## 真实 Electron 覆盖

脚本为代码仓 `apps/desktop/scripts/input-prediction-electron.mjs`。它使用隔离源码／数据目录和拥有身份的子进程，运行真实 main、preload、renderer、预测服务、Context、HTTP Provider 编码／解析、预算和草稿持久化。仅模型输出、凭证与普通 Agent 执行器受控；预测服务没有替换为模拟对象。全局 Provider tracing 强制开启，以检查预测仍不落正文 trace。

19 个具名场景覆盖：空 Enter 不发送灰字；Tab 采纳一次且再次 Tab 可离开；手工输入／采纳／再输入的撤销重做；末尾 ArrowRight 与前缀保留；选区／行中／composition 优先；迟到响应；Escape／Shift+Tab；鼠标及可访问按钮键盘采纳和归焦；未发送附件暂停；跨 Bot 隔离；HTTP 失败恢复；预算为零派发前拒绝；真实设置及说明；关闭续写／总开关；经典空草稿／Enter／Tab／撤销；经典 slash 优先与后缀；1040px／大字号／reduced-motion／Chromium AX；未采纳内容不入草稿与 Provider trace；采纳后 Enter 沿原 Bot 输入链恰好投递一次并清理已收取草稿。

另有服务／host 用例覆盖受信 sender、跨工作区／只读入口拒绝、显式路由、结构化决定停用、Context／政策变化、真实 ConversationChangeEvent 失效、预算重启与预约结算、损坏日志 fail-closed、异常工具、超时／不响应取消／晚 usage、TTL、单次校验与验证期间本地 CAS。没有工具执行端口。

截图审阅检查了灰字与真实文字区别、完整可读、快捷键与按钮、输入框尺寸、键盘焦点、历史位置、设置文案与限额、经典字号／减少动效。镜像同步修复了 CSS font shorthand 可能为空的问题，现按独立字体属性测量；可访问按钮在校验时以 aria-disabled 保持焦点并防重复；采纳发起时记录归焦意图，采纳完成明确返回原输入，离开交互组则取消。每张图的具体观察见 review JSON。

## 真实模型小样本

探针通过隔离 Electron net 和既有正式 Provider Adapter、凭证 Helper 与预测服务，使用明确选择的 API-key `deepseek-flash`（anthropic-messages wire）。只发送自造的文章润色情景，未发送真实用户对话或草稿；原设置／会话／凭证配置不写入，也没有重启已安装应用。

| 模式 | 服务耗时 | 最终输出 |
| --- | --- | --- |
| next_turn | 1822ms | 第三段到技术部分的过渡再润色一下，语气别太生硬。 |
| continuation，原前缀“再帮我” | 1036ms | 把第三段到技术部分的过渡改得自然些，语气保持现在的风格。 |

两次都在原定 2 秒截止内，返回真实 usage，保留“先不发布”约束，没有工具或授权／验收结论。首个旧版 prompt 的 next_turn 曾误用助手口吻；调整为明确原用户视角和带 role 的事实数组后，上表两样本复测正常。另一 GLM 模型的 Node-fetch 探针两次超时，不记为质量通过；签名 Helper 与 Electron net 的实际可用模型另行验证。源构建 Helper 的同步 10 秒阻塞由可取消 Worker／1 秒 Helper 上限修复，专门验证主线程仍能前进。

这只是一个合成情景的两次请求，耗时包含凭证和传输、不含 UI 去抖；不是采纳率、长期质量或 P50／P95 结论，也不宣称 1.5 秒 P95 目标达成。账单取消后可能仍消费；无实际 usage 时预算保守估算，不能报告为零。

## 可复跑与证据边界

```sh
pnpm build
node apps/desktop/scripts/input-prediction-electron.mjs --output <repo-outside-packet>
# 实施者逐图检查后填写 review.json：machineSha256、每图具体观察及限制
node apps/desktop/scripts/input-prediction-evidence.mjs <same-packet>
```

验证器核对最终源码内容指纹、machine 摘要及每张图 hash，拒绝缺失／旧审阅、变动源码或图片。最终包机读摘要、图与自审结论保存在本仓 `evidence/`，不带本机绝对路径或凭证；临时原包不作为跨机器依赖。

设置图只展示功能标题、总开关和公共上下文说明，下方模型、草稿披露与限额由真实滚动交互／回执验证，未完整截图覆盖全区。

当前边界：源码 Electron 自验而非安装包；IME 包含 composition 事件及 CDP 中文 composition／commit，不等同 macOS 中文／日文候选窗实测；Chromium AX 按钮和焦点已检查，VoiceOver／其它读屏未实测；未做多原生窗口恢复、系统 Edit 菜单、完整 forced-colors／透明度降级及长期模型质量矩阵。大项目指令超过保守预算时会 abstain。IP-07 的全部开放 PR、最终联合候选、完整产品 capture／review／verify 与安装版门禁仍留到实际版本／RC 发布，不能由这份功能包替代。


## 最终归档

- [Machine：19 项场景与 8 图摘要](evidence/input-prediction-20261031/machine.json)
- [实现者逐图自审与限制](evidence/input-prediction-20261031/review.json)
- [最终源码／截图／审阅绑定 verify](evidence/input-prediction-20261031/verify.json)
- [构建、测试与重跑记录摘要](evidence/input-prediction-checks-20261031.json)
- [真实模型两样本及质量自审](evidence/input-prediction-live-model-20261031.json)

最终源码内容指纹为 `466be1a259002114c529bad5d14d52715bf24c58a2ea5cfa8af600c020043d6c`（3448 个受管源码／资源文件）；临时原包与移除绝对路径后的归档包均实际运行 verify 通过。图像按最终原包复制，未修改像素；归档只将 machine 的路径改为相对文件名，并重新绑定 review 的 machine 摘要，同时保留原摘要。
