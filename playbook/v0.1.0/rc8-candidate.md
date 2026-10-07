# RC8 连续执行、结果交付与对话修复

创建时间：2026-10-07
最后更新：2026-10-07
状态：Released

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

实际旧 tag 模块与受控 updater、真实 SIGKILL/恢复矩阵 26 项通过，sourceDirty=false；不冒充旧安装客户端 GUI 升级。[升级与恢复](evidence/rc8-upgrade-matrix-20261007.json)。[精确候选 CI37619750146](https://github.com/ly-ccx/Peer-Agent/actions/runs/37619750146) Mac/Linux 全部门禁成功。CI 合成合入 `6968a70957e0e2b44ab192d6315fc89b054cca87`、候选和实际合入 tree 相同。实际合入 `8e17a9a12d09eb3466b0a7d151e0f60ef06ec0a9`，合入后 [CI37621750669](https://github.com/ly-ccx/Peer-Agent/actions/runs/37621750669) 两平台再次全部成功。干净合入提交 readiness/source 检查通过。不可变 tag `v0.1.0-rc.8` 的对象 `1d4e3af79f6601f887a673b243bd04eaa184027b` 指向实际合入；[源码绑定](evidence/rc8-ci-binding-20261007.json)、[Linux 原始窗口记录](evidence/rc8-ci-linux-window-20261007.json)。

[Pages37621929820](https://github.com/ly-ccx/Peer-Agent/actions/runs/37621929820) 成功。实际 HTTP 用户 docs 与 RC8 changelog 正文匹配标签；manifest 内容一致，其 generatedAt 按浅 checkout 的标签提交时间生成，单独核验。初次将生成日期也按旧文件字节比较的失败保留，未当成内容改变。[线上文档](evidence/rc8-pages-20261007.json)。

[Release37621929750](https://github.com/ly-ccx/Peer-Agent/actions/runs/37621929750) 首次 Windows/Linux 构建成功，Mac 获取公证票据时 Apple CloudKit 返回 HTTP503/THROTTLED、retryAfter=13，stapler65；后续 CLI/Release/npm 被阻断。已从同一不可变标签重跑失败 job，第二次运行的全部 8 个 job 成功，未重写源码或标签。[首次失败](evidence/rc8-publish-first-failure-20261007.json)。

### 已公开发布与实际包核验

[GitHub RC8](https://github.com/ly-ccx/Peer-Agent/releases/tag/v0.1.0-rc.8) 于 2026-10-07T12:49:01Z 公开，prerelease=true、draft=false，14 项资产齐全，中英发布正文与标签字节一致（去除外围空白）。Release attempt2 的 meta、三平台 Desktop、两平台 CLI、release、publish-npm 全部成功。[工作流](evidence/rc8-release-workflow-20261007.json)、[资产元数据](evidence/rc8-published-release-20261007.json)、[最终绑定](evidence/rc8-final-binding-20261007.json)。

实际下载 10 项资产并逐项核对 GitHub digest 与大小。三平台 Beta 清单核对版本、文件与大小，Mac ZIP 的 sha512 与清单一致。Mac ZIP 内未改写的正式 app 严格签名、Developer ID Team82672N97RP、stapled ticket 与 Gatekeeper Notarized Developer ID 均通过；DMG 完整性检查、只读挂载后的同一签名/公证核验通过，app.asar SHA256 与 ZIP 相同，并已卸载只读卷。实际 Mac CLI 显示 peer 0.1.0-rc.8，helper 的 Developer ID 验证通过。[下载与信任](evidence/rc8-assets-trust-20261007.json)、[DMG 内嵌应用](evidence/rc8-dmg-trust-20261007.json)。临时验证器首次误用归档顶层 peer 路径，修正为归档内 peer-darwin-arm64/peer 后通过；原始失败记录保留，不计为产品通过。

公开 npm 四包 protocol/runtime-core/runtime-sdk/cli 的固定版本和 rc 标签均为 0.1.0-rc.8；latest=0.0.18、beta=0.1.0-beta.5。首次安装在注册表尚未暴露刚发布版本时得到 ETARGET；版本可见后以同样固定版本重新安装成功，未重复发布。隔离 prefix/cache 的真实 postinstall 下载后 CLI 版本正确，peer 与 helper 的 SHA256 均等于 GitHub 归档内二进制；未修改全局安装。[npm 注册表与实际安装](evidence/rc8-npm-install-metadata-20261007.json)。

使用生产 PeerGitHubProvider、electron-updater6.8.9 和实际发布 HTTP 元数据完成 18 项检查（3 平台×6 场景）：含 RC7 → RC8 Beta 可发现、当前 RC8 不提示降级、Stable 仍为 0.0.18。该探针不安装三平台客户端。[真实更新发现](evidence/rc8-live-update-20261007.json)。

实际下载的、未改写的签名 Mac ZIP 应用以隔离数据与 Chromium profile 启动，packaged=true、版本 RC8；正式包关键 UI 四张图片实际查看并记录观察，52px 页头、“机器人设置”直达设置、概况/记忆、关闭侧栏恢复对话宽度均核对通过。正式包的生产 Beta updaterCheck 返回当前版本 RC8、not-available，未执行下载或安装。最初 harness 没有选择已有 Bot，导致等待页头超时；诊断后修正操作顺序。随后发现截图落在动画中间，已等待过渡完成重拍并审查四张图片；不把仅机器成功当作图像验收。[正式包 UI 与具体观察](evidence/rc8-published-ui-20261007.json)。

Mac CI job 全部成功，checkout 提交与树已绑定；但原始窗口大归档获取超时，未冒称已获得其 raw report。Linux raw report 已归档，最终源码本机 66 张图与 Mac 正式包四张图均实际自审。该补充没有替代独立评审。[Mac CI 原始归档覆盖限制](evidence/rc8-ci-mac-artifact-coverage-20261007.json)。

交付覆盖：实施者自审 independent=false；最终源码使用 scripted cognition，正式包关键 UI 使用合成历史/记忆，没有重新验收全部真实模型。Mac 实际签名包启动/更新检查通过；Windows/Linux 仅 CI 构建和清单/更新发现，没有交互安装。已有自动 accessibility 检查与人工图像审查不等于完整读屏验收；复杂写 Evidence、跨模型独立核验与长期日用/GA 缺口保持原结论。
