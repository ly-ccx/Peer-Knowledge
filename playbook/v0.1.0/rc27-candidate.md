# RC27 组合候选与发布回执

日期：2026-10-28（发布服务时间使用 UTC，见下方）
状态：已发布 `0.1.0-rc.27`；完整源码门禁、333 张产品逐图自审、标签流水线、Release/npm/Pages 核验均已完成。覆盖限制保留，不代表全部平台安装或真实模型验收。

## 范围与来源

用户明确要求新 RC，并确认包含已完成 R5–R10 与近期界面修复。保留无关在制、当前应用/任务及已完成写入。所有发布实现、构建和夹具在隔离克隆进行；个人两仓文件与原索引不改。

本轮初始代码 PR #221、知识库 PR #79；R5–R10 知识增补 PR #80 已合并。代码 #221 审查、回归修复与 RC27 准备沿原 PR，不另建代码发布旁路。最终发布前再次清点全部代码 open PR（含草稿、其他目标）；有未合并项即阻断。

## 发现并修复的真实问题

- 嵌套注册根的限定/绝对读取使用不同资源身份，首次读取即 source_changed；先守原范围，再统一合法物理根身份，不放宽访问。
- Portal 的 React 焦点冒泡被当成会话区焦点，窄窗隐藏实际详情；改按实际 DOM 归属判断。
- 详情往返重复揭示工作区覆盖领域焦点；避免同区重新揭示，返回实际可用控件，保留用户后续选择。
- 工作区关闭的父级回退覆盖任务指定的主消息/Composer 焦点；明确动作指定目标优先。内联现场返回按真实去向命名。

## 回归脚本与失败保留

旧 push/cover、已卸载详情、嵌套模态与内部 resizer 的断言同步为实际非模态侧栏、稳定场景、保留但 inert 的 DOM 与面板间拖拽线。布局等待只等真实有限动画；持续装饰粒子不作为保存未完成依据。滚动到物理底部不代表跟随意图，跟随用例先明确返回最新；恢复用例等待实际 pump 而非 150ms 竞速。旧依据夹具补齐当前 Bot 的真实归属，其他 Bot 的拒绝规则不改。

前期全部失败日志和未接受包保留；较小/较旧候选不能作为最终发布门禁。最终结果另填精确提交、源码指纹、命令退出、机器联调、每图原始 SHA 和审阅意见。实现者自审不称独立；不把通过的合成认知当作真实供应商/长期日用/完整输入法读屏/全部平台安装通过。

## 当前候选与验证台账

代码 PR [#221](https://github.com/ly-ccx/Peer-Agent/pull/221)，合并前头 e72f4610da5db7d7b3b0964f0b55a21b1862f349。知识 PR #79、#80 已合并；补充回执在 #81。最终合并提交、源码指纹、完整套件和逐图审阅以下方完成记录为准；RC27 标签与真实发布核验均完成。

补充修正包括启动反馈双行挤压与旧最小宽度、预格式文本行尾空格悬挂。启动四组宽窄/明暗、真实重试、六组长错误几何、选区/共享组件已定向通过；完整主流程在此前候选通过，不沿用为最终组合验收。原始失败保留，禁止把旧夹具定位失败说成用户模型失败。

## 验收方式和限制

最终全量检查使用 Node 25 与仓库固定 pnpm；根测试保持真实入口并将 workspace 并发限制为 1，避免整库并行造成非业务定时器竞速。标准产品包绑定源码指纹、runId 与每张图的 SHA256；必须逐图实现者自审（independent=false），再运行 qa:product:verify。扩展资源包另跑 5 个 Electron 脚本 × 明暗 2 组，真实主进程/preload/IPC、隔离 Git/文件/SQLite/网页；网页截图使用原生 guest 的真实像素。

README: updated。中英发布说明、CHANGELOG、生成的站点数据、使用文档和全部版本戳均在代码 PR #221。生成检查在 stamp 前通过；最终组合候选的版本、changelog、release source/readiness、运行时包与消费者检查也均通过。

发布本身不安装/重启个人应用。合成模型只覆盖状态链与受控回复，不代表真实供应商质量或网络时延；源码 Electron 不代表每个平台原生安装交互，键盘/减少动效不等于完整硬件 IME 或读屏认证，也不代表长期日用。

最终检查第一次编排误将产品采集的依赖重建与根测试并行，造成两项测试读取正在重写的 protocol/dist 导出而导入失败；同文件稳定输出后 14 项隔离重跑全部通过。保留 attempt1 的完整失败记录，后续最终完整检查改为与采集重建串行；这不作为源码修复或通过证明，最终结果必须另记完整重跑。

第一份合并后采集从本机 23:59 跨至 00:05，历史夹具在播种时生成的“今天”在检查时已正确变为“昨天”；硬编码四组标题的断言失败。保留失败包，日期稳定后从同一未改动源码完整重采集，不改生产分组或放宽断言。该失败不作为用户记录错误或任务丢失的事实。

## Final combined source and checks

- Commit: `5cd2d6d9d03c4d00682aeaba2fa54435fe9810f8` (merged code PR #221).
- Tree: `857217d43e7f1f2baceb7a4079ce55429e73c016`.
- Source fingerprint: `37b3d530dbaa7cf96cc30b22fa5261f0adc425599b9a2004974a5960157740f3`.
- Clean source: true; open code PR inventory empty after merge.
- Gate report SHA256: `2e5d3789c63a2566c8ebac1840c1a1dd86653aeb33028ca9292104727e8eddb8`.

| Check | Exit | Seconds |
| --- | --- | --- |
| build | 0 | 18.1 |
| typecheck | 0 | 12.9 |
| architecture | 0 | 1.0 |
| ipc | 0 | 0.3 |
| test | 0 | 177.1 |
| product-contracts | 0 | 0.9 |
| release-source-tests | 0 | 0.3 |
| runtime-contents | 0 | 4.6 |
| runtime-consumer | 0 | 5.9 |
| rust | 0 | 37.2 |
| version | 0 | 0.3 |
| changelog | 0 | 0.3 |
| source | 0 | 0.3 |
| readiness | 0 | 0.4 |

These are the complete serial rerun results on the merged source, including the root upgrade matrix.

## Final product acceptance

- 标准产品包 runId：`c76b2741-03ae-4dbf-a236-81205493a9e5`；244 张必审原始截图全部逐张审阅，`qa:product:verify` 通过（2026-10-27T16:37:09.911Z）。
- 资源组合：5 个生产 Electron 脚本 × 明暗 2 组，10/10 机器联调通过；89 张原始截图全部逐张审阅，原始与归档副本 SHA256 一致。包含正文/源码/固定历史、目录与 Diff 更新、独立来源、草稿与讨论引用、一次授权、拒绝/取消/冲突/未知结果对账、独立文档/目录/Diff/网页窗口。网页实际内容另外读取原生 guest 像素，不能把父容器空白截图当网页验收。
- 两份验收均绑定上述最终合并提交与同一源码指纹，采集前后指纹未变；实现者 AI 自审，`independent=false`。可移交的逐图 SHA、观察、完整命令退出和覆盖限制见 [RC27 源码验收记录](evidence/rc27-source-acceptance.json)。
- 接受的非阻断覆盖限制：旧自动化页面在低于原生主窗口最小 1040px 的 760px 压力图仍有宽内容；正常窗口宽度可读。透明 Quick Chat 原始 alpha 保留，并按 Frost 回退色合成检查；不代表原生系统 vibrancy 验收。旧完成报告抽屉仍为兼容入口；本次新增文件/目录/网页/Diff 使用工作区标签。
- 认知为受控替身，文件/Git/SQLite/回环网页和主进程/preload/IPC 为真实隔离执行；不据此声称真实模型时延、所有平台安装交互、读屏或长期日用通过。资源脚本显示 Electron 41.7.1 属测试宿主版本，候选 manifests 为 RC27。
- 合并前代码 PR #221 的 macOS/Linux CI 均通过；最终合并提交 push CI [40536236470](https://github.com/ly-ccx/Peer-Agent/actions/runs/40536236470) 的 macOS/Linux 均通过。首轮 macOS 因 GitHub 托管 Runner 未分配而未执行，原失败保留；重试在同一提交真实执行后通过，未绕过检查。
- 2026-10-27T16:48:30.993719Z 再清点全部代码 open PR（含 draft/其他 base），结果为空；远端开发线仍为上述候选，源码干净且指纹不变。标签 `v0.1.0-rc.27` 推送到同一提交；本轮实际合并代码 PR 清单为 #221。
- Pages [40544539284](https://github.com/ly-ccx/Peer-Agent/actions/runs/40544539284) 已部署；首页、使用文档、更新日志、manifest 和 RC27 条目均返回 HTTP 200，beta 最新项为 RC27，稳定项保持 0.0.18。

## 发布完成回执

- [GitHub RC27 预发布](https://github.com/ly-ccx/Peer-Agent/releases/tag/v0.1.0-rc.27) 发布于 2026-10-27T16:57:36Z；prerelease=true、draft=false，正文与已提交双语说明一致。
- [标签 Release 流水线](https://github.com/ly-ccx/Peer-Agent/actions/runs/40544539827) 共 8 个 job 全部 success：meta、三个桌面平台、两个 CLI 平台、统一 Release、npm。全部绑定 `5cd2d6d9d03c4d00682aeaba2fa54435fe9810f8`。
- 14 项 GitHub 资产已上传：macOS ARM64 DMG/ZIP 及 blockmap、Windows EXE 及 blockmap、Linux x64 AppImage/deb、macOS ARM64/Linux x64 CLI tar.gz、3 份 beta 更新清单和 builder 调试元数据。核对资产非空、服务端 SHA256 元数据、更新清单的版本/目标文件/大小及 SHA512 编码；没有把元数据核验称为本地安装测试。
- macOS 打包 job 的 Developer ID 签名、Team ID、stapled 公证票据、Gatekeeper 及 ZIP 内应用校验步骤真实通过；三个平台 packaged runtime 校验通过。Windows/Linux 仍未签名，不承诺与 macOS 相同的签名体验。
- npm `@peer-agent/protocol`、`runtime-core`、`runtime-sdk`、`cli` 的精确 RC27 版本和 integrity 均可读取，dist-tag `rc=0.1.0-rc.27`；`latest=0.0.18`、`beta=0.1.0-beta.5` 保持原值。首次读取部分 npm packument 命中旧缓存；流水线真实发布日志成功后，以 no-cache/独立请求核对 Registry，未重复 publish 或覆盖不可变版本。
- 发布动作未安装或重启个人应用，没有运行个人任务、重放已完成写入。原工作区 297 个代码文件、23 个知识库文件及各自原索引保持不变；隔离发布、夹具和验收文件不混入个人暂存区。
- 完整可移交检查、逐图观察、资产清单、更新清单与 npm receipt 记录在 [RC27 源码与发布验收](evidence/rc27-source-acceptance.json)。原始截图和失败包保留在本机隔离验收目录；该 JSON 记录其 SHA 和观察，不声称图片本身已提交知识库。
