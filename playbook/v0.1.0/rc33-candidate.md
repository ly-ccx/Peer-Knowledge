# RC33：长会话输入、工作现场与联合协调发布

创建时间：2026-11-01
最后更新：2026-11-02

状态：RC33 最终联合提交 `429fa64d7f41a1c3476f2e6ba7bc3c3beacf7520` 已重新完成工程与产品验收，标签已推送，Release、npm、更新源与Pages核验全部完成。RC32 因 GitHub macOS14 runner 计划停用未发布，失败标签和证据保留。

## 范围与边界

用户在载入 1,274 条 Peer RSI 长会话副本的隔离源码窗口确认输入顺畅，要求与全部待合并 PR 一同发布。逐键草稿保存已沿 PR245 的 `hasActiveBot()` 轻量身份检查，不再构建完整机器人概览；该修复已在 RC31 主线，本轮持续保留。第四栏与引用同样继续保留。

本轮合入 #252（任务停止、恢复与资源交接）、#253（原目标持续协调与联合格式9）、#254（智能输入建议设置与共享模型选择器）、#251（工作现场及文件阅读区），以及 #255（RC32准备及响应式面板留位修复）。#256 将发布的 Desktop/CLI macOS runner 从14迁到受支持的15，并提前核对 darwin-arm64；Developer ID、公证、包内运行时与签名 helper 门禁保留。格式9的 A/B 边界及先建设备账本再启用契约见 ADR116/117；界面不新建执行、权限或 Evidence 路径。

升级前备份完整数据目录，Desktop、CLI/TUI、Gateway 使用匹配版本。旧程序不能接管格式9的活跃数据，降级需要完整升级前备份。模型直接声明的资源等待仍为 adapter_unavailable；不能把宿主已有排队恢复说成该入口已开放。

README: updated。双语说明、CHANGELOG、用户文档与落地页同步；失败 RC32 的发布说明迁为 RC33，不把未发布版本列为可用下载。

## RC32 验收与基础设施失败

最终源码 `7c080c4e693c14bd22c93fca255fee20c72c6b8e`，指纹 `61033aae1b6c872425bafaae83b3dbe820e4a6414f3ffb79a66da2740a0bbe77`。全部 PR 合入且 open PR 清零后运行13项工程门禁，全数首次通过；包括完整 build/type/architecture/IPC、Rust、全套 Node/Bun、产品回归契约、release source、runtime pack、readiness及changelog。现有跳过项保留，不能称为已通过。

标准产品包 run `3516a9cb-6d96-4133-81b7-2b8e2a487412` 的255张必查截图全部实际逐图自审，摘要绑定 verify 通过；输入建议19项/8图、资源工作区19项/8图亦通过并逐图自审。性能样本仅报告受控源码场景：可见搜索中位25.30ms，输入已收到中位26.30ms；不是安装版端到端打字或系统输入法承诺。划词引用锚定、滚动、离屏关闭、键鼠、草稿、正文边界、宽度重排和停靠断言全部保留。详见 [RC32未发布尝试证据](evidence/rc32-unpublished-attempt.json)。

推标签前再次确认所有 open PR 为空。标签触发 [Release 41322658622](https://github.com/ly-ccx/Peer-Agent/actions/runs/41322658622)，macOS job 124896025336 没有执行任何步骤即被基础设施取消；错误注解明确指向 [GitHub runner弃用公告](https://github.com/actions/runner-images/issues/13518)。确认没有 RC32 Release 后取消剩余流水线，未覆盖标签或不可变 npm 版本。RC32 Pages 曾成功部署，这不等于 Release 已成功；后续以RC33线上核验收尾。

## 最终联合候选与发布

#256 实际 PR head 的 macOS/Linux 必需 CI 全部通过后合并；最终提交 `429fa64d7f41a1c3476f2e6ba7bc3c3beacf7520` 的主线 CI 也全部成功。冻结时和推标签前再次确认全部 open PR（含 draft 和其它目标分支）为空。实际合入代码 PR：#252、#253、#254、#251、#255、#256。输入修复 #245 已在祖先主线，继续包含。

最终源码指纹 `fbd9b7dcf07e0a9d2db7b63224bd365eb5b240da2a40d54b252c07398b9f0edc`。13项工程门禁首次全过、没有重跑；Desktop 6142项中6137通过、5跳过，现存跳过项不记为通过。标准产品包 run `f7918746-5443-48db-bdd0-3b3e5093b86d` 的255张截图全部实际逐图自审后verify通过；19项输入建议/8图与19项资源工作区/8图同样重新运行、逐图审阅并绑定当前源码。此处没有继承RC32验收。受控性能样本：可见搜索中位25.30ms、输入已收到中位26.90ms、列表16.29ms；读取位置从5225到5224，后台事件不重启追随。均不是系统IME或安装版端到端性能承诺。

首次标准采集在 Electron inspector 的 `screen.getPrimaryDisplay` 读取处出现 `Resulting promise was garbage collected`，发生于产品交互前，页面错误为空；原始日志和正常首页失败现场保留。未改源码与断言，进行一次新的隔离采集后全程通过。工程检查没有因此重复。详细可移植结果见 [RC33最终源码验收](evidence/rc33-source-acceptance.json)。

双语说明、CHANGELOG、版本戳与发布源检查通过。`check:changelog` 输出 `changelog data is current (111 releases, 112 JSON files)`。README: updated。确认GitHub Release和四个公开npm版本均尚不存在后，从该精确提交推送 `v0.1.0-rc.33`；[Release 41328505008](https://github.com/ly-ccx/Peer-Agent/actions/runs/41328505008) 的8个作业全部成功，[RC33](https://github.com/ly-ccx/Peer-Agent/releases/tag/v0.1.0-rc.33) 于2026-11-01 17:01:59 UTC（北京时间11月2日01:01:59）发布为prerelease，14项资产齐全。三平台beta更新清单均指向RC33，文件路径、字节大小与SHA512编码核对通过；GitHub资产上传状态与非零大小、SHA256元数据记录到回执。

macOS15实际以darwin-arm64构建；原始 `.app` 和更新ZIP解压应用均通过Developer ID（82672N97RP）、严格codesign、stapler与Gatekeeper `Notarized Developer ID`。CLI归档为darwin-arm64和linux-x64；macOS helper从同次已签Desktop产物取出，签名身份和字节哈希验证通过。

protocol、runtime-core、runtime-sdk与cli四个公开npm包的精确版本与rc标签均为0.1.0-rc.33，tarball地址全部HTTP200且完整性字段存在；runtime-node继续private。Pages run41328505151在同一最终提交部署成功，首页、文档、更新日志、manifest和版本JSON五条路径HTTP200，manifest.latest.beta为RC33、非epoch时间戳、双语说明完整。详细线上事实见 [RC33发布回执](evidence/rc33-publication.json)。

范围限制：实现者自审 independent=false，不是独立评审。源 Electron 和受控模型执行，不等于真实供应商质量、系统IME/原生候选窗、完整屏幕阅读器、安装交互或长期验收。专项入口所见 v41.7.1 是 Electron 引擎版本，不是产品RC版本。没有安装、替换或重启个人应用；原工作区未提交内容和现有运行实例保留。
