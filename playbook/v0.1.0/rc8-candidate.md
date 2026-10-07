# RC8 连续执行、结果交付与对话修复

创建时间：2026-10-07
最后更新：2026-10-07
状态：Preparing

负责人明确授权“发布新的 rc”。目标为 `0.1.0-rc.8`。发布 Desktop 三平台、CLI 两平台和四个公开 npm 包；推进 npm rc 通道，保持 stable/latest 与 beta dist-tag。现有代码工作区包含同一会话已授权的修复，发布准备不替换、丢弃或重置这些改动。

## 范围与架构

- [ADR88](../../knowledge/decisions/88-project-agent-execution-continuity.md) 已 Accepted：标准验证权限、统一会话事实、本地协调与 checkpoint、输入/事件回执、预算与无进展保护、结果交付及策略签收。相关执行仍走现有 Capability Provider → Manifest → Projection → Tool Call → PermissionGrant → Evidence。
- Provider seam 保留思考历史，Grok 版本信息由实际配置解析；用户界面只表达事实与结构化动作。
- 完整段落气泡、技术详情右侧栏、可读任务与依据、对齐输入区、模型/强度与快捷 Bot 选择、无竖线引用和贴近选区的引用浮层；52px 页头及“机器人设置”直达配置。
- 中英 notes、用户文档、生成 changelog、版本事实源与升级矩阵同步。普通签收不是新的远端发布授权。

## 门禁

1. 本机 build/typecheck/architecture/IPC/完整测试、真实旧 tag 升级与恢复矩阵、公开 Runtime 打包及外部宿主 smoke、版本与发布来源检查。
2. 对最终 RC8 源码运行产品 Capture；实施者实际查看每张必查图片，写具体 review，Verify 绑定源码及图片。自审不是独立评审。
3. 精确候选 Mac/Linux CI 通过后合入开发线；核对树与 tag 对应。RC8 标签固定后不重写。
4. Release 三平台 Desktop、两平台 CLI、Mac Developer ID/公证、npm 与 Pages 工作流。
5. 实际下载检查 digest/清单、Mac 签名与公证、CLI 版本、npm 固定版本与 rc 标签、隔离 npm 安装、真实更新发现和正式包关键 UI。

## 现有证据与限制

[ADR88 实施证据](evidence/adr88-execution-20261007.json) 包含真实 Grok 熟悉、排查、插话与执行中重启场景；旧受阻任务已经受限审计恢复并经真实宿主签收，记录与人工历史、记忆分别保留。DeepSeek 订阅拒绝和响应超时保留为失败。不得把较早候选的模型抽样当成最终发布包全部重跑。

发布前最后页头/选区修复的 Capture `c61004d3-c353-4970-b205-a3ccc5255d7d` 在 RC7 版本源码上自审 66 张截图并 Verify passed；它不代替 RC8 版本变更后的新包。源码与本机包均未冒充已签名发布。

RC8 新 authority/model_review/协调字段在旧写入中可能丢失。回退使用升级前完整兼容备份，并保留新数据和产物；旧安装客户端 GUI 降级未验收。

复杂写任务命令描述 Evidence 完整性、跨供应商复核独立性、Windows/Linux 交互安装、生产远程、实体手机、完整读屏与长期日用仍有覆盖缺口，总体 Ready/GA 不因 RC8 发布改变。

## 发布记录

候选源码 `52ab510a3f76f9dc246a6218b55c14ad3ea0e3f3`，tree `ab8112a5e05fe37eb808215d0aa9907703332a77` 已推送，源码 [PR124](https://github.com/ly-ccx/Peer-Agent/pull/124)。完整本机 build/typecheck/architecture/IPC/test 与 Runtime package contents / external-host smoke 通过；desktop 5413 项测试，5408 通过、5 项既有跳过、0 失败。版本、changelog、readiness/source 检查通过。

RC8 最终源码 Capture `7ee16a70-76cd-4d54-a9b4-418cfd98850b`：66 张必查截图实际逐张查看并写出观察，Verify passed；fingerprint `4f01eed4a3e30da7060ca3724c42a1df350585e9405189d7bade5ac658248935`。提交后再次 Verify passed，源码字节未变。实施者自审 `independent=false`。[产品审查](evidence/rc8-product-review-20261007.json)。

实际旧 tag 模块与受控 updater、真实 SIGKILL/恢复矩阵 26 项通过，sourceDirty=false；不冒充旧安装客户端 GUI 升级。[升级与恢复](evidence/rc8-upgrade-matrix-20261007.json)。[精确候选 CI37619750146](https://github.com/ly-ccx/Peer-Agent/actions/runs/37619750146) 正在跑 Mac/Linux 最终窗口门禁；合入、标签和实际发布产物尚未写成成功。
