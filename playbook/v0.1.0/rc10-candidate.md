# RC10 回复连续性与对话交互

创建时间：2026-10-09
最后更新：2026-10-09
状态：Released（官方预发布与发布后核验完成，GA 缺口继续保留）

## 卡片与范围

负责人授权“发布新的 rc”。目标 `0.1.0-rc.10`，集成 PR130–134，经 PR135 合入 `PeerAgent/dev/0.1.0`。沿用官方 tag 发布链、Desktop 三平台、CLI 两平台和四个公开 npm 包；仅推进 rc dist-tag，stable/latest 保持 0.0.18，npm beta 保持 0.1.0-beta.5。

- 空 Responses 仅做一次同模型、同思考强度的有界恢复，保留工具结果、使用量与总预算；不重放已执行工具。
- 回复详情按过程、关联任务与依据分层，入口在内容悬停或键盘聚焦后显示于右侧；任务当前核验阶段优先于旧摘要。
- 机器人回复气泡使用头像身份色的柔和背景，用户和技术卡片保持各自语义；覆盖浅深主题与图片头像稳定回退。
- 选项点击立即成为待发送用户消息，选项区域约 200ms 收起；服务端回执保持同一消息节点，保留焦点、重试和读历史时中断自动滚动。
- 更新弹窗约 320ms 收向左下角版本/下载区，由实际下载事件驱动进度；处理快速完成、失败重试和减少动态效果。

## 分支与提交

发布候选分支 `codex/release-0.1.0-rc.10`，准备提交 `b1b0e5dd7dbd03d1ef42e40c9cbc9fbe73d70e89`，tree `d2e0c024be0d9839ff531ad152670223e6111aca`。PR130/131先合入；保留132/133/134原提交在候选上 merge，解决 BotConversation、smoke 与 product-regression 交叉改动，保留所有颜色、输入上下文、截图库和机器检查入口。

[PR135](https://github.com/ly-ccx/Peer-Agent/pull/135) 实际合入 `013a0a17d644d491f59a07471ee85598ccda372b`，tree 与候选一致，PR130–134均已收拢。不可变标签 `v0.1.0-rc.10` 指向该实际合入提交。[源码与CI绑定](evidence/rc10-ci-binding-20261009.json)。

## 验证

- build、typecheck、architecture（包含圆角/SVG）、runtime package contents 与外部宿主 smoke、版本/changelog/readiness/source 均通过。
- 全仓 `pnpm test` 通过；桌面5432项（5427通过、5项既有跳过、0失败），runtime-node1128、TUI756；其他包、根changelog和升级矩阵测试通过。
- [精确候选 CI37936112130](https://github.com/ly-ccx/Peer-Agent/actions/runs/37936112130) macOS/Linux全部通过。PR132 首轮 Mac 搜索性能预算失败，按流程重跑后两平台成功，没有放宽性能门禁。
- [实际合入 CI37938195785](https://github.com/ly-ccx/Peer-Agent/actions/runs/37938195785) macOS/Linux全部通过，head 为标签所指的 `013a0a17`。[最终绑定](evidence/rc10-final-binding-20261009.json)。
- 产品回归 runId `84dac3fc-5dc4-4583-a3e5-bee0fd332036`；115张必查截图全部实际逐张查看并记录观察，`qa:product:verify`通过；合入后再次 Verify通过。fingerprint `22e11d4b7bcf065dcee8d2b987b56eb436200455c424e3f28bb875206611970a`。[产品自审](evidence/rc10-product-review-20261009.json)。实现者自审，`independent=false`。
- 三组 choiceSendMotion / updaterMinimize 逐帧交互记录通过；快速完成、失败恢复、减少动态、焦点、滚动、身份切换、32组颜色对比以及 currentPhaseWins/exitsToFollowUp 检查通过。静态截图不单独证明动画。
- 实际旧 tag 模块、受控 updater 与真实 SIGKILL/恢复矩阵28项通过，sourceDirty=false，夹具清理完成。[升级与恢复](evidence/rc10-upgrade-matrix-20261009.json)。不冒充旧客户端GUI安装升级。

## 与卡片偏差

无；原专项的交叉冲突在候选中整合，没有增加功能范围或改变发布通道。

## 架构影响

发布准备与冲突处理为 C 级。PR131为既有 B 级恢复修复，沿用现有 Provider/kernel、实际使用量和预算。此次没有新增能力、权限、Evidence、IPC、存储或 System Context 边界。

## 文档偏差

README: updated。根中英 README版本、候选说明链接、消息身份色已同步；安装/入口/CLI平台矩阵已核对。中英notes、CHANGELOG、docs/docs.html和生成changelog已提交。落地页入口与定位没有改变，docs/index.html检查后 no-op。

## 发布与产物

- [官方 Release](https://github.com/ly-ccx/Peer-Agent/releases/tag/v0.1.0-rc.10) 于 `2026-10-09T13:47:44Z` 发布，prerelease=true、draft=false，双语说明与标签源码一致。[Release37938438466](https://github.com/ly-ccx/Peer-Agent/actions/runs/37938438466) 全部8个job成功。[发布记录](evidence/rc10-published-release-20261009.json)、[工作流](evidence/rc10-release-workflow-20261009.json)。
- 14项公开资产全部实际下载，大小/SHA256与GitHub记录一致；三平台Beta更新清单的版本、文件、大小与SHA512和资产一致。实际Mac ZIP签名、Team ID、公证票据、Gatekeeper通过，实际DMG完整性、只读挂载后签名/公证/Gatekeeper及内含app与ZIP一致性通过；CLI及helper签名、版本通过。[资产与ZIP信任](evidence/rc10-assets-trust-20261009.json)、[DMG信任](evidence/rc10-dmg-trust-20261009.json)。
- 三平台18项真实HTTP更新发现检查通过：Beta5/RC2/RC4/RC9在Beta策略下发现RC10，当前RC10不重复提示，正式策略不降级到0.0.18。使用发布包实际配置、PeerGitHubProvider及electron-updater，不安装或写入用户数据。[真实更新发现](evidence/rc10-live-update-20261009.json)。
- 四个npm包的固定RC10版本和rc标签公开可见，latest=0.0.18、beta=0.1.0-beta.5保持原值。隔离执行公开注册表的实际 `npm install @peer-agent/cli@0.1.0-rc.10`，postinstall从官方Release下载，CLI输出 `peer 0.1.0-rc.10`，peer/helper二进制SHA256与发布归档一致。[npm安装](evidence/rc10-npm-install-20261009.json)。发布刚完成时第一次查询和npm view短暂拿到旧元数据/404；保留[第一次失败](evidence/rc10-npm-first-cache-failure-20261009.json)，公开版本可见后重验实际安装成功，没有重新发布版本或修改标签。
- 未修改的正式签名Mac包隔离启动，通过紧凑页头与机器人设置、概况、记忆、保存身份色后的真实气泡、返回对话与真实当前版本更新检查；4张截图全部实际查看，页面无错误，退出已完成。实现者自审，independent=false，合成历史与隔离配置，未替换用户安装。[正式包UI自审](evidence/rc10-published-ui-20261009.json)。
- [Pages37938438482](https://github.com/ly-ccx/Peer-Agent/actions/runs/37938438482)成功，实际HTTP核对5项页面和数据与标签一致；manifest stable=v0.0.18、beta=v0.1.0-rc.10，构建时间有效。[Pages内容](evidence/rc10-pages-20261009.json)、[Pages工作流](evidence/rc10-pages-workflow-20261009.json)。

## 未完成与限制

- 原历史逐条统计缺少受治理的读取能力；修复空回复与展示状态不代表原统计任务完成，不能将工人报告目标计为完成事实。
- 源码回归使用 scripted cognition；不替代真实供应商质量、网络时序、完整读屏或长期日用。透明快捷窗PNG不含原生背景；深色hover静态图没捕获淡入完成态，交互记录和其他键盘完成态证明行为，已记录为采集限制。
- Windows/Linux交互安装、真实复杂写任务Evidence完整性及GA缺口继续保留。升级前备份完整数据根；Desktop/CLI/Gateway一起升级，回退恢复兼容备份并另存新数据，不能用旧宿主写新数据目录。
