# RC33：长会话输入、工作现场与联合协调发布

创建时间：2026-11-01
最后更新：2026-11-01

状态：RC32 最终源码验收通过，但发布被 GitHub macOS 14 runner 的计划停用阻断，未产生 GitHub Release。保留失败标签及原始证据，准备 RC33；不得把 RC32 的结果当作 RC33 最终联合候选验收。

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

待 #256 必需检查、合并及 open PR 再清零后冻结新的精确提交，重新运行完整工程和产品门禁，再推新标签。最终事实取得后补齐本节和可移植证据。

范围限制：实现者自审 independent=false，不是独立评审。源 Electron 和受控模型执行，不等于真实供应商质量、系统IME/原生候选窗、完整屏幕阅读器、安装交互或长期验收。专项入口所见 v41.7.1 是 Electron 引擎版本，不是产品RC版本。没有安装、替换或重启个人应用；原工作区未提交内容和现有运行实例保留。
