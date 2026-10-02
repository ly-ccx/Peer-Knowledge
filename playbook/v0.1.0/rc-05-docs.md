# RC05 用户文档与候选包交付

2026-10-02，Accepted；负责人授权自主完成实现、自测、详细手册及 RC 预发布。GA 必须等待负责人全面测试与明确确认。C 级文档与发布编排；不增加能力或权限。

允许代码路径：release-notes/v0.1.0.md（未发布草案）与 v0.1.0-rc.1.md；README 两种语言及真实界面截图；既有 stamp-version 覆盖的 VERSION、包清单及 Cargo 文件；changelog 生成物。允许 build-changelog.mjs 及测试识别显式 draft marker 并跳过未发布 GA 草案，避免更新摘要伪称正式版已发布。版本门禁与发布源约束保持。

知识路径：本卡、acceptance-test-guide.md、rc-self-test-report.md、rc-release.md；D10、roadmap 中景 0 及产品实现状态补正。保留历史设计作为背景，只更新当前事实。最终候选版本、安装包 SHA 与代码提交绑定；自动化、真实模型、源窗口、安装包、控制网络、真实手机、生产部署和七天日用分列。

必须先完成 RC01–04 两平台 CI 与合入，再完成最终候选完整门禁、已签名公证包安装及真实多入口复杂任务；不以模块或脚本执行器代替安装包模型执行。旧 TUI 必须同步升级；已知平台限制明确。RC06 七天日用由负责人完成，不能模拟或提前完成。


## rc.2候选准备（Accepted）

负责人“全部做完并先自测”覆盖RC1缺陷修复后的新候选预发布。原rc.1/tag/资产保持不变。rc.2纳入已通过两平台CI并合入的设置页PR99、同次签名CLI助手PR100、命令执行快照PR101。允许新release-notes/v0.1.0-rc.2.md、既有版本stamp与changelog生成物、README候选说明/链接、build-changelog.test.mjs当前候选断言；允许rc-upgrade-matrix.mjs及测试把新候选加入已有真实tag/受控GA更新毕业检查，保留rc.1历史并明确实际矩阵数量，不放宽既有断言。

先版本提交全部门禁与最终两平台CI；安装包真实复杂任务/多入口/默认CLI helper独立复验后才交付Ready。实际源码首轮模型误读与空响应及恢复操作保留，不能宣称无干预通过；无证据不得签收。GA继续等负责人195用例、6流程、7天日用与明确批准。


rc.2追加范围（Accepted）：同时纳入真实等待answer恢复PR102与负责人本轮要求的GPT-6.1 Sol目录PR103，均须先通过两平台CI并按依赖合入。升级矩阵新增当前rc.2的受控GA更新毕业行，保留rc.1和五个Beta，预期20项，真实旧tag模块仍六版。模型实际空响应按真实环境失败记录，不能宣传账号可用；发布说明准确写实现与验收状态，负责人交付仍须完成新包可行实测。


rc.2源码b1cae373干净门禁通过：[全量记录](evidence/rc2-source-gates-20261002.json)、[实际源窗口](evidence/rc2-source-window-passed-20261002.json)。Desktop5294项中5289通过/原5skip＋AST1，runtime1006、TUI751；全构建/typecheck/architecture/test/version/changelog/readiness通过。9壳/11可访问性/7诊断、0页面错误、owned退出；列表15.87ms、搜索25ms、Received54.5ms均在原预算。20项矩阵保留六版真实tag来源与旧检查。PR104两平台CI进行中，安装候选未发布，GPT61实际调用未通过，总交付尚未Ready。


设置页PR99、同次签名CLI助手PR100、命令快照PR101、等待answer恢复PR102与GPT-6.1 Sol目录PR103均已通过两平台CI并合入。rc.2候选PR104最终两平台CI36960002970通过，tag v0.1.0-rc.2固定到be65fb73ce672f87a144a68ed5a1622f5d632ae8，Release36960577284构建中。20项升级矩阵及完整源码门禁、9壳/11可访问性/7诊断通过；严格源码双写保留真实用户回答与一次重试，两任务独立核验、签收和单独授权合回通过。经典GPT61 low/default实际读文件回复通过；机器人同模型仍空响应，摘要请求也失败，尚无已确认根因。新安装包默认CLI、复杂任务与多入口待复验，尚未Ready；GA仍等负责人全面测试、七天日用和明确批准。 [最终CI与源码绑定](evidence/rc2-candidate-ci-binding-20261002.json)。


2026-10-02 rc.2发布后事实：Beta1–5已实现，RC1及RC2已预发布。PR99–104均通过两平台CI并合入；rc.2固定be65fb73，Release36960577284全成功。20项源码矩阵、完整回归、9壳/11可访问性/7诊断通过；实际macOS签名公证、六次安装轮换、归档与npm CLI默认助手读文件/回复通过。多入口复验通过（实际安装Desktop＋源码TUI后端＋本机远程网关夹具，非实体手机/生产OIDC）；严格安装双任务仍失败。Astra两文件和新鲜证据正确，A因计划拆分及缺批准历史被核验拒绝，未签收/合回；批准事实PR105已合入6bdbaf8c并通过两平台CI；源码Luna代理＋冻结Astra任务/核验的同夹具恢复全流程通过，首轮Astra空响应保留。新安装候选待复验。GPT61机器人仍空响应，尚未Ready。GA仍等负责人195用例、6流程、七天日用及明确批准。
