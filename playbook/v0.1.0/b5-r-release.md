# B5-R 预发布实施边界

日期：2026-10-01。状态：Accepted。B5-01–05已全部合入；B5-05 `8556ab36` 双平台CI36883768066通过。负责人授权全部Beta5/RC、自测、Review/合入及预发布，GA等待其全面测试。

卡片只修改版本事实源（stamp-version维护的VERSION/package/Cargo/README beta标记）、beta5中英发布说明与生成changelog。无架构/运行行为新增。先完成build/type/architecture/test、版本/来源/readiness/changelog门禁，PR双平台CI通过后在dev分支打v0.1.0-beta.5 tag；保留stable0.0.18、npm latest和main，beta渠道发布。

发布后逐项核验签名公证三平台Desktop、两平台CLI、npm四包beta版本与14资产。macOS arm64真实安装候选版冒烟；隔离数据的Desktop/TUI/remote同时在线真实模型输入与宿主切换、不丢不重、远程批准提示留电脑。测试账户或loopback边界必须单列，不冒充生产OIDC/真实手机。KB回写发布计划§5.2/§12.1与handoff；Windows/Linux构建或自动冒烟不冒充手工日用。RC01–05完成后再发RC候选，不发布GA。

发布准备首次根测试发现build-changelog.test.mjs仍把latestPrerelease写死为beta4；本卡补入该既有发布事实断言，更新为beta5，保留stable0.0.18与通道分离的全部断言，不跳过测试。readiness必须在版本提交后检查HEAD，未提交时的版本diff失败不是产品回归。
