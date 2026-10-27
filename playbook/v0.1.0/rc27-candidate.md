# RC27 组合候选与发布回执

日期：2026-10-27
状态：准备中；只有最终候选全量检查、完整产品逐图验收、PR 合并和标签发布均完成后才更新为已发布。

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

代码 PR [#221](https://github.com/ly-ccx/Peer-Agent/pull/221)，合并前头 e72f4610da5db7d7b3b0964f0b55a21b1862f349。知识 PR #79、#80 已合并；补充回执在 #81。最终合并提交、源码指纹、完整套件和逐图审阅必须以下方完成记录为准；尚未推送 RC27 标签。

补充修正包括启动反馈双行挤压与旧最小宽度、预格式文本行尾空格悬挂。启动四组宽窄/明暗、真实重试、六组长错误几何、选区/共享组件已定向通过；完整主流程在此前候选通过，不沿用为最终组合验收。原始失败保留，禁止把旧夹具定位失败说成用户模型失败。

## 验收方式和限制

最终全量检查使用 Node 25 与仓库固定 pnpm；根测试保持真实入口并将 workspace 并发限制为 1，避免整库并行造成非业务定时器竞速。标准产品包绑定源码指纹、runId 与每张图的 SHA256；必须逐图实现者自审（independent=false），再运行 qa:product:verify。扩展资源包另跑 5 个 Electron 脚本 × 明暗 2 组，真实主进程/preload/IPC、隔离 Git/文件/SQLite/网页；网页截图使用原生 guest 的真实像素。

README: updated。中英发布说明、CHANGELOG、生成的站点数据、使用文档和全部版本戳均在代码 PR #221。生成检查已在 stamp 前通过；最终组合候选还会检查版本、changelog、release source/readiness、运行时包与消费者。

发布本身不安装/重启个人应用。合成模型只覆盖状态链与受控回复，不代表真实供应商质量或网络时延；源码 Electron 不代表每个平台原生安装交互，键盘/减少动效不等于完整硬件 IME 或读屏认证，也不代表长期日用。

最终检查第一次编排误将产品采集的依赖重建与根测试并行，造成两项测试读取正在重写的 protocol/dist 导出而导入失败；同文件稳定输出后 14 项隔离重跑全部通过。保留 attempt1 的完整失败记录，后续最终完整检查改为与采集重建串行；这不作为源码修复或通过证明，最终结果必须另记完整重跑。

第一份合并后采集从本机 23:59 跨至 00:05，历史夹具在播种时生成的“今天”在检查时已正确变为“昨天”；硬编码四组标题的断言失败。保留失败包，日期稳定后从同一未改动源码完整重采集，不改生产分组或放宽断言。该失败不作为用户记录错误或任务丢失的事实。

## Final combined source and checks (product review pending)

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

These are the complete serial rerun results on the merged source, including the root upgrade matrix. Screenshot acceptance, expanded resource integration and publication are still pending and recorded separately below. No tag has been pushed at this checkpoint.
