# RC12 主 Bot 自主协调与并行执行

创建时间：2026-10-11
最后更新：2026-10-11
状态：Released（官方预发布及本轮正式包验收完成；总体Ready/GA缺口保留）

## 范围与源码绑定

用户明确授权“发布新的 rc，你要验收一下”。本轮先按依赖收拢 R91-01 至 R91-05：#148 → #147 → #146，#144 和 #146 汇入 #143，再由 #143 合入开发线；知识 PR33 合入 main。代码 #143 的整合 head `5d8a2344953369a2b6c5d8d4708e7073b8c24b07` 与原已验收 `9462a4ca` 的 tree 一致，实际合入 `c25e05dff8585eed610d36e3a4cb08c3e021d906`。发布准备 [PR149](https://github.com/ly-ccx/Peer-Agent/pull/149) 已合入。无关 draft PR145 不纳入本轮。

目标 `0.1.0-rc.12`。不可变 tag `v0.1.0-rc.12` 指向实际开发线合入 `cc9f9a1b9ec718c92c63eb324756bfb08b57eeaa`，tree `88c06375d1670beb7ad4a7e5e2753f721368682f` 与干净验收候选 `c767dd44c0b1842665737c20f12df5beb49fbc4e` 完全相同。[最终绑定](evidence/rc12-final-binding-20261011.json)。

- 主 Bot 按实际目标把输入分成补充、独立要求与纠正，自主派发和协调独立工作 Agent。
- 同目标补充送入原执行者；错误目标可取消并重派，保留已有结果且不停止兄弟任务。
- 子 Agent 与主 Bot 通过持久具名消息、关联问题/回答通信；既有授权范围内由主 Bot 核对并收尾，真正需要用户决定时才问。
- 协调保留并发资源，短片段让出；停止中、结果待核实、替代谱系和重启闸门都有真实投影。
- 主回复失败或停止不等于独立子工作取消。原历史任务不自动接管或签收，历史读取能力未随本轮新增。

## 发布前验收

- [候选 CI38067440919](https://github.com/ly-ccx/Peer-Agent/actions/runs/38067440919) 的 macOS/Linux build、typecheck、architecture、全仓 test、Electron smoke 全部通过。[CI记录](evidence/rc12-candidate-ci-20261011.json)。功能整合 CI38067193612 的 Linux首次通过，Mac第一次漏采更新收起动画中间帧；失败作业用相同代码和相同断言重跑后通过，未放宽动画或性能门禁。[首次失败](evidence/rc12-ci-animation-first-failure-20261011.json)、[整合CI](evidence/rc12-integration-ci-20261011.json)。
- Runtime package contents 与外部 npm tarball host smoke 通过；升级/恢复矩阵30项通过，源干净。[升级恢复](evidence/rc12-upgrade-matrix-20261011.json)。
- 产品 capture 成功，143张必查截图全部实际查看，逐张记录观察，verify通过；实际合入后再次verify通过。runId `6b783da6-5842-49cb-b86a-d64119d5fb3d`，fingerprint `d285c219ba1de33a28a04dac597ba69a50de5e384a8e034795a769dfb3b638fe`。[产品观察](evidence/rc12-product-review-20261011.json)、[合入后verify](evidence/rc12-product-verify-20261011.json)、[机器摘要](evidence/rc12-product-machine-summary-20261011.json)。实现者自审，independent=false。
- 消息间距、身份色气泡、无竖线的引用、气泡边缘的 hover/focus 详情、具名 Agent 活动、证据降噪、窄屏侧栏、选择发送与更新收起流程，以及8张新协调状态截图通过。旧手动完成卡片只作为遗留契约夹具，不能代替本轮主 Bot 自主收尾的真实模型验收。
- 架构：ADR91 为实施前批准的 A/B 级设计依据；本次版本/文档发布准备为C级，没有新增能力旁路或权限边界。
- README: updated。中英入口、发布说明、CHANGELOG、指南与落地页自主协调叙事同步；生成 changelog 门禁在 stamp/tag 前通过（91 releases、92 JSON files），readiness/source-check通过。

## 正式发布与安装包验收

- [官方 Release](https://github.com/ly-ccx/Peer-Agent/releases/tag/v0.1.0-rc.12) 于 `2026-10-10T17:02:28Z` 发布，draft=false、prerelease=true。发布说明与标签源码逐字一致。[Release38069506060](https://github.com/ly-ccx/Peer-Agent/actions/runs/38069506060) 全部8个job成功，head为标签所指cc9f9a1。[发布记录](evidence/rc12-published-release-20261011.json)、[工作流](evidence/rc12-release-workflow-20261011.json)。实际合入 [CI38069419566](https://github.com/ly-ccx/Peer-Agent/actions/runs/38069419566) 两平台全部通过。[合入CI](evidence/rc12-merged-ci-20261011.json)。
- 14项公开资产全部实际取得，大小与SHA256逐项匹配GitHub；三平台Beta更新清单的版本、文件、大小、SHA512一致。Mac ZIP严格签名、Developer ID/Team ID、公证票据、Gatekeeper通过；DMG完整性与只读挂载后实际应用签名、公证、Gatekeeper、app.asar与ZIP一致性通过，挂载已卸载。两平台CLI归档实际解包，Mac CLI和凭据助手版本及签名通过。[资产信任](evidence/rc12-assets-trust-20261011.json)、[DMG信任](evidence/rc12-dmg-trust-20261011.json)。Mac先取得同一官方工作流dist-mac供实测，随后与公开Release逐项SHA绑定；没有重打包或修改签名应用。
- 四个npm固定RC12版本和rc标签公开可见，latest保持0.0.18、beta保持0.1.0-beta.5。隔离实际 `npm install @peer-agent/cli@0.1.0-rc.12`，postinstall从官方Release下载，输出 `peer 0.1.0-rc.12`，peer/helper SHA与官方Mac归档一致。[npm安装](evidence/rc12-npm-install-20261011.json)。首个发布后registry查询尚未见固定版本；保留首轮结果，传播后重新核对并实际安装通过。[首轮查询](evidence/rc12-npm-first-check-20261011.json)。
- 三平台21项真实HTTP更新发现通过：Beta5/RC2/RC9/RC10/RC11在Beta策略发现RC12，当前RC12不重复提示、stable不降级到0.0.18。使用发布包实际app-update.yml和生产PeerGitHubProvider/electron-updater，仅测试HTTP适配器不安装旧客户端。[真实更新发现](evidence/rc12-live-update-20261011.json)。
- 实际未修改签名RC11客户端在隔离数据/profile中通过生产IPC发现RC12，点击更新后真实下载，17次状态样本从0到100%，下载ZIP SHA与公开资产一致；3张截图实际查看，下载完成后左下角安装入口可见。测试只隔离cache并关闭自动Squirrel交接，没有调用安装、没有替换日常应用。[旧版实际下载](evidence/rc12-old-updater-download-20261011.json)。临时探针首轮在Playwright的主进程VM中使用dynamic import失败，尚未开始下载；改用既有Node builtin module访问后在新隔离目录重跑通过，生产代码未变。[探针首轮](evidence/rc12-updater-harness-first-check-20261011.json)。
- 未修改正式签名RC12包在隔离数据/profile启动，app.isPackaged=true。52px页头、机器人设置直接进入设置、真实保存头像颜色与气泡一致、概况/3条记忆/返回聊天和当前版本真实Beta检查通过。4张截图实际查看、具体观察已记录；pageErrors=0、自有应用退出。[签名包UI](evidence/rc12-published-ui-20261011.json)。实现者自审，independent=false；该UI历史为合成数据，实际工作执行由下一节单独验收。
- [Pages38069506059](https://github.com/ly-ccx/Peer-Agent/actions/runs/38069506059) 成功；真实HTTP核对5项页面和JSON与标签一致，manifest stable=v0.0.18、beta=v0.1.0-rc.12，生成时间有效。[Pages内容](evidence/rc12-pages-20261011.json)、[工作流](evidence/rc12-pages-workflow-20261011.json)。

## 正式签名包的真实模型协调验收

时间：`2026-10-10T17:02:58.680Z` 至 `2026-10-10T17:06:21.151Z`（Asia/Shanghai为2026-10-11 01:02至01:06）。实际运行官方签名RC12 `.app`/app.asar，app.isPackaged=true；真实配置的OpenAI OAuth `gpt-6.1-sol`，模型总并发4、只读工作准入2。所有输入经生产IPC，主Bot与工作/Verifier模型自行选择生产工具；没有注入模型结果或人工修改任务完成状态。

| 场景 | 实际结果 |
| --- | --- |
| A/B/C独立要求 | 独立持久会话，A/B真实模型工具执行区间累计重叠37,921ms；C遵守两个只读工作准入，主Bot保留协调能力 |
| B格式补充 | 送入原B执行者的真实update消息，未取消或重建B |
| 纠正A | 旧A确认cancelled，创建唯一Corrected A，B/C未被取消 |
| 关闭重启 | 会话与替代谱系恢复，旧A不复活，替代身份唯一 |
| 子Agent提问 | 向主Bot发送真实question，主Bot以replyTo关联回答“只计算C”，未交给用户代答；全部8次文件读取在回答后发生 |
| 正确结果 | B=16条/1000，C=8条/276，Corrected A=6条/165，Question=8条/276 |
| 核验与自主收尾 | 四份持久model_review全部passed，主Bot自主汇报并收下，四个session最终accepted，旧A cancelled；不以result_ready代替成功 |

8个严格场景全部通过，pageErrors=0；自有进程退出，隔离凭据副本删除。[完整真实模型记录](evidence/rc12-live-coordination-20261011.json)。**使用正式包原装签名凭据助手，没有helper路径覆盖**；原安装候选验收对bundled helper未覆盖的缺口，本轮已以正式包实际OAuth模型调用补齐。执行和Verifier同为GPT-6.1 Sol，独立模型回合不等于异源独立审查。

## 覆盖限制

源码回归是脚本化认知；正式包真实模型范围限于上述只读协调故事。实现者自审不称独立审查。Windows/Linux交互安装、完整屏幕阅读器、跨供应商核验、真实云端看图、真实外部副作用/复杂并发写、七天日用与GA缺口继续保留；不据单轮RC宣布整体Ready或GA。升级发现/下载实测不代表执行Squirrel安装或替换日常应用。升级前备份完整数据根，Desktop/CLI/Gateway同步升级，回退使用完整兼容备份。
