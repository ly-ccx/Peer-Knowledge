# RC 更新发现与防降级修复

2026-10-02，Accepted。负责人要求自主收口RC，并再次提供实际rc.3→beta.5错误提示。B级：主进程已有更新Provider的适配与校验；既有auto/beta/stable、IPC、偏好存储、下载授权及签名/哈希链不变。基线`b2a9049f`，代码分支`PeerAgent/pa/rc-update-provider`。

## 实施边界

依赖ADR61（Accepted）及[真实诊断](rc-update-discovery-diagnosis.md)。beta代表预览池，包含发布流程已经映射到beta*.yml的alpha/beta/rc；显式beta保持预览池，不自动毕业到正式。auto预览先探查严格更新的正式版，无可用则回预览；正式auto保持stable。通道选择不代表允许降级。

在已冻结electron-updater的custom Provider工厂Seam接入GitHubProvider子类，读取打包app-update.yml既有配置，不硬编码另一个发布源。保留其HTTP执行器、平台/架构清单命名、resolveFiles、下载取消、哈希与平台签名校验。预览Atom按有效semver选最高alpha/beta/rc；正式沿现有latest端点并校验正式标签。清单版本必须与所选标签绑定；RC仍读beta平台清单。读取失败明确失败，不伪造可用版本或向旧包回退。

通道setter之后明确allowDowngrade=false；主进程事件、下载入口、安装入口校验候选严格高于当前安装版本。旧或非法候选不得发available、不得下载或安装；仍保留已有downloading/downloaded相位锁与事件事实。避免新增自管下载或renderer事实源。

## 允许修改

- apps/desktop/electron/main/auto-updater.mjs及auto-updater.test.mjs
- 新建apps/desktop/electron/main/update-github-provider.mjs及update-github-provider.test.mjs
- 新建apps/desktop/scripts/update-discovery-live-probe.mjs（显式联网，运行真实Provider/AppUpdater资格判断，记录实际清单和资产URL/SHA，不下载包或安装）
- 本卡、诊断、RC报告/指南/证据；ADR61实施说明可补当前预览映射澄清，不改变毕业决策。

不改main.mjs、IPC、renderer、存储、依赖、版本文件、发布工作流或已发布tag/资产。需要新签名候选时另走RC发布卡。新源码不能修正冻结的旧Beta5/RC3客户端：它们先人工安装修复候选，后续升级再验证自动发现；不宣称旧客户端已经自动可达。

## 验证与退出

先失败复现rc.3→beta.5与Beta5跳过RC。真实SDK+HTTP夹具覆盖Beta→RC、RC→RC、不同核心号的新Beta、最高版本、显式stable排除预览、auto毕业及beta不毕业、乱序/无效标签、版本不匹配、清单缺失、配置来源、平台清单与下载URL/hash。主进程模块测试覆盖setter降级副作用、旧事件、旧下载/安装入口及相位锁。

联网读取真实GitHub Atom、清单，校验实际发布版本及资产链接/hash；不以合成事件替代发现。定向及桌面完整回归、build/typecheck/architecture、两平台CI通过后评审合入。下一不可变签名候选必须复验实际应用检查且不提供旧Beta下载/安装，旧客户端人工升级步骤单列。未安装验证不写总体Ready。
