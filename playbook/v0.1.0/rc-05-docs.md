# RC05 用户文档与候选包交付

## rc.4 候选准备（2026-10-02，Accepted）

负责人要求自主完成RC收口，本轮再次指出实际rc.3提示旧beta.5更新；允许依赖PR110侧栏排版及PR111真实更新发现/防降级通过最终两平台CI并合入后，从开发线准备PeerAgent/pa/rc4-candidate。发布修复候选以解决实际安装客户端；复杂任务命令描述快照仍为独立A类未完成项，RC4不得据此宣称总体Ready。GA继续等待负责人全面测试、七天日用及明确批准。

允许新release-notes/v0.1.0-rc.4.md，既有stamp-version覆盖的VERSION、12个package.json、Cargo.toml/lock及两个README版本/链接；changelog生成物及build-changelog.test.mjs候选断言；rc-upgrade-matrix.mjs保留RC1–3并新增当前RC4，测试期望22项。不得移旧tag/资产、改依赖、签名、发布工作流或更新器实现。

新候选需完整构建/类型/架构/测试、版本/changelog/readiness和最终两平台CI、真实源窗口。发布后下载实际资产比对digest、验证同Team签名/Gatekeeper/公证，再用实际macOS签名包原生更新检查：Beta及auto不提供旧Beta/同版本，显式stable不提供旧0.0.18。旧Beta5/RC3先人工安装新候选，实测后才能称旧客户端迁移完成；不假称旧冻结更新器已修。平台清单和模型/多入口/复杂任务的已有范围单列，Windows/Linux互动安装及未发生的未来RC自动安装不写Pass。

原用户应用替换前可回滚备份当前app和完整数据，保留canonical记录、机器人身份与原模型偏好；实际确认新版本、侧栏渠道只在设置内、版本右对齐、无错误旧版红点，再更新详细测试文档和事实报告。

## rc.3 候选准备（2026-10-02，Accepted）

RC3 窗口门禁追加范围（2026-10-02，Accepted）：PR109 同提交一次重跑后 Linux 全通过，macOS 在菜单进入动画尚未结束时读取几何，trace 记录 trigger.top=820、menu.bottom=822.0625；失败截图进入完成后正常向上。允许本卡仅修改 apps/desktop/scripts/bot-shell-updater-checks.mjs，使用既有有界 until 等候原几何条件成立并保留原断言、事件状态及性能预算，记录最终几何；不改产品样式或运行时。首轮两平台 GC transport 失败和二轮 macOS 几何失败分别保留，不推断产品根因，不无限重跑。新提交需本机真实窗口与最终两平台 CI 完整通过。

负责人自主修复、自测及 RC 预发布授权继续适用。新候选纳入已合入的批准事实 PR105、侧栏更新入口 PR106、启动历史读取 PR107，以及待最终两平台 CI 合入的回复终结 PR108；依赖齐全后从开发线开 PeerAgent/pa/rc3-candidate。旧 RC1/RC2 tag 和资产保持不变，GA 等负责人全面测试、七天日用与明确批准。

允许新 release-notes/v0.1.0-rc.3.md；既有 stamp-version 覆盖的 VERSION、12 个包清单、Cargo.toml/lock、两个 README 候选标记和发布说明链接；changelog 生成物及 build-changelog.test.mjs 当前候选断言；rc-upgrade-matrix.mjs 及其测试保留 RC1/RC2 并加当前 RC3 毕业行（21 项，六版真实旧 tag 来源不变）。本卡不改更新器实现、依赖、签名配置或工作流。

RC3准备提交4d97ff6d（tree bab3d33454c92e54e63dd28fc43c6767e4cce828）干净完整门禁通过：[源码门禁](evidence/rc3-source-gates-20261002.json)、[实际源窗口](evidence/rc3-source-window-passed-20261002.json)。Desktop5302项中5297pass/原5skip、独立AST1；runtime1014、TUI755与其他包通过；21项矩阵通过。9壳/11可访问性/7诊断无页面错误且owned退出；列表14.55ms、搜索23ms、Received51.70ms在原预算。PR109最终CI36979821056进行中，尚未发布。PR108真实GPT61双写补明确基线diff证据后的完整独立核验/签收/授权合回通过，首轮证据不足拒绝保留：[源码复杂通过](evidence/rc-post-reply-source-complex-scope-passed-20261002.json)。新包默认helper与复杂任务仍须实测。

候选干净源完整构建/类型/架构/测试、版本及发布门禁、21 项矩阵和最终两平台 CI 必须通过。发布后验证正式签名公证包与资产 SHA、401 旧计划历史双机器人启动/切换、GPT61 真实 canonical 回复及无额外模型请求、默认 packaged helper、复杂任务和多入口。安装包通过前不能把源码通过写成用户已修复。Beta→RC 真实自动发现与错误降级仍是独立未解决发布阻塞；本次说明明确提供手动安装升级路径，不宣传自动更新已可用。

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

最终准备提交 eaabfa98（tree 2cc939ae6df77ee36e251a4d82d7b69f39319724）全部本机源码门禁再次通过；干净实际源窗口9壳/11可访问性/7诊断通过，无页面/授权错误、owned退出。Accepted追加仅修正测试菜单动画采样时机，原几何/状态/性能断言保持。最终CI36981399115进行中。见[最终源码门禁](evidence/rc3-final-source-gates-20261002.json)、[最终源窗口](evidence/rc3-final-source-window-passed-20261002.json)。

PR109最终CI36981399115两平台完整通过，9壳/11可访问性/7诊断、0页面/授权错误、owned退出，原性能预算通过。eaabfa98、CI合成528e7054与实际合入78178d0c的tree完全一致（2cc939ae…）。已按负责人授权合入；新不可变tag v0.1.0-rc.3指向78178d0c，正式Release构建与安装实测待完成。见[最终CI绑定](evidence/rc3-candidate-ci-binding-20261002.json)。


RC4候选准备acf19ee3/tree10707e13：本机完整build/typecheck/architecture/test及releaseReadiness通过；Desktop5320项5315pass/原5skip＋AST1，runtime1014，22项矩阵保留RC1–3与六版旧tag来源。干净源实际窗口9壳/11可访问性/7诊断、0页面/授权错误、owned退出与原性能预算通过。[源门禁](evidence/rc4-source-gates-20261002.json)。PR112最终两平台CI36995512881进行中，尚未发布或替换原应用，不改判复杂任务阻塞。


RC4最终CI首轮：Linux完整通过；macOS构建/类型/架构/回归通过，窗口阶段发送合成更新事件的Playwright主进程transport报Resulting promise was garbage collected，页面/授权错误为零，owned退出。[原失败](evidence/rc4-ci-window-transport-failed-20261002.json)。保留失败日志/截图，同提交仅重跑该失败job一次，未改产品代码或断言；再次失败则修复具体测试Seam，不无限重跑。新签名包仍待原生实际更新检查。


PR112最终CI36995512881两平台全部成功；macOS同提交一次有限重跑窗口通过，原失败保留。acf19ee3、CI合成eb4b0e40及合入11b5f645的tree一致10707e13，已合入。新不可变tag v0.1.0-rc.4固定11b5f645，Release36997106815构建中；尚未验证签名资产及安装，不将源码/CI通过等同实际用户修复。[绑定](evidence/rc4-candidate-ci-binding-20261002.json)。


### RC4 实际发布与原用户迁移完成

Release36997106815八个job全部成功，2026-10-02T10:53:11Z发布14项资产，固定tag11b5f645不变。ZIP/DMG/macOS CLI下载SHA匹配，ZIP与DMG内.app同Team严格签名/公证/Gatekeeper通过；DMG容器staple65保留、应用票据通过。[发布信任](evidence/rc4-published-assets-trust-20261002.json)。四npm包RC4固定版本/rc标签可见，旧latest/beta标签保持；第一轮部分元数据尚不可见记录保留，不推断原因或重发包。归档CLI/助手签名和版本RC4通过，本轮未重跑RC3模型/完整PTY多入口。

三平台真实发布清单12项、实际签名RC4生产Electron HTTP三渠道和无候选下载/安装拒绝通过；第一轮观察脚本动态import限制只修脚本观察Seam，产品与断言不变。原用户RC3完全退出后完整备份app与数据，人工替换官方RC4；43份canonical文件旧行、模型/角色/项目身份和设置字节保持，未重置profile。实际版本RC4，主动检查显示当前最新，旧Beta5提示消失，底部账户左/版本右/渠道设置内。原机器人对话已打开，应用保持运行。[实际包](evidence/rc4-installed-updater-passed-20261002.json)、[原数据迁移](evidence/rc4-original-user-install-passed-20261002.json)。旧客户端人工升级已证明可达，不宣称旧冻结更新器自动可达；未发生未来候选下载安装、物理Win/Linux安装、实体手机/生产远程和七天日用不写Pass。复杂任务Evidence命令描述仍独立A类阻塞，整体未Ready。全面测试手册更新为RC4与真实SHA，195用例和6流程不减少。
