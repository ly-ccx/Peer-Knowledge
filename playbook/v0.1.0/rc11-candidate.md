# RC11 任务连续性、独立 Agent 与本地看图

创建时间：2026-10-10
最后更新：2026-10-10
状态：Released（官方预发布与发布后核验完成，GA缺口继续保留）

## 卡片与范围

用户授权检查待合入工作并发布新的 RC。本轮原有代码 PR 共五项：136 任务取消、137 气泡边缘详情及实际进度、138 检查点恢复、139 独立 Agent 通信、140 本地看图。139/140 按堆叠依赖先向父分支合入，再由138合入开发线；136/137直接合入。知识 PR30/31已合入知识库main。发布准备另经[PR141](https://github.com/ly-ccx/Peer-Agent/pull/141)合入。[实际合入清单](evidence/rc11-merge-inventory-20261010.json)。

目标 `0.1.0-rc.11`，沿用官方 tag 发布、Desktop 三平台、CLI 两平台和四个公开 npm 包，仅推进 rc dist-tag；stable/latest 保持0.0.18，npm beta 保持0.1.0-beta.5。

- 主对话和任务详情支持取消等待跟进的任务，失败可重试，保留其他工作和历史。
- Details对齐当前气泡右边缘，悬停/键盘聚焦显示；进度依据实际活动。
- 回复从检查点继续，保留已执行工具、公开消息和预算；分别说明缺少检查点、调度、次数与登录状态。
- 真实独立 WorkSession 执行并与主 Bot 双向通信，具名工作动态和持久消息归属；主 Bot 等待与人类决定分开。
- 主 Bot、执行 Agent、核验 Agent 共用受治理的本地看图 Provider，将授权图片像素送入视觉模型；图片引用与重读线索保留，恢复后重新读取。

## 分支与提交

发布分支 `codex/release-0.1.0-rc.11`；精确候选 `f915b86a7dd6c6e97dafbff149f5ae80af1f399f`，tree `cdb3d923b933d1587ee7b7ddcc47a3590ef7471a`。PR141实际合入 `438d1a6f52853ff55031fb351cb14625de554514`，tree与验收候选一致。不可变标签 `v0.1.0-rc.11` 指向实际合入HEAD。[最终绑定](evidence/rc11-final-binding-20261010.json)。

## 验证

- 本机完整 build/typecheck/architecture/test、runtime package contents/外部宿主 smoke、升级恢复28项通过。[本机门禁](evidence/rc11-local-gates-20261010.json)、[升级恢复](evidence/rc11-upgrade-matrix-20261010.json)。本机全仓门禁源为70a5575，后续05f86b/f915b86只调整截图采集与断言；最终两平台CI对精确候选和合入源码另做全部门禁。
- [候选 CI38047637465](https://github.com/ly-ccx/Peer-Agent/actions/runs/38047637465) macOS/Linux全部通过。[记录](evidence/rc11-candidate-ci-20261010.json)。[实际合入CI38048835690](https://github.com/ly-ccx/Peer-Agent/actions/runs/38048835690) macOS/Linux全部通过，head与标签一致。[记录](evidence/rc11-merged-ci-20261010.json)。
- 产品回归 runId `afe62d9d-78e1-4772-a29f-e025b5ed8722`；135张必查截图全部实际查看、记录观察；capture与verify通过，合入后再次verify通过。fingerprint `12ea42cf0790342279a1d84d226ca3f6ddd42b5b8bab8368cd8467a82d86dadc`。[产品自审](evidence/rc11-product-review-20261010.json)、[合入后verify](evidence/rc11-product-verify-20261010.json)、[机器摘要](evidence/rc11-product-machine-summary-20261010.json)。实现者自审，independent=false。
- 首轮采集遇到原生菜单CDP对象回收；后续两轮机器检查虽通过，四张恢复截图因关闭抽屉后的虚拟布局还未稳定而没有正文，未被接受。增加真实可见消息/有限动画结束与两个绘制帧等待，最终重新采集全部135张；四张恢复正文均实际可见，无裁切。未复用旧采集作为验收。
- 保留历史CI失败：早期Mac原生菜单CDP对象回收；Linux动画末帧因采样缺口未到测量目标；合入138后的Mac历史消息锚点超时。[采集首次失败](evidence/rc11-capture-first-failure-20261010.json)、[动画历史失败](evidence/rc11-ci-animation-first-failure-20261010.json)、[合入历史失败](evidence/rc11-dev-integration-first-failure-20261010.json)。未放宽动画目标或性能门禁。最终候选/合入CI状态以对应不可变head记录为准。

## 架构与文档影响

功能实施已先按ADR88/89/90记录A/B级恢复、通信和图片契约；知识PR30/31已合入。此次发布准备与采集修正为C级，没有增加执行路径或改变权限、Evidence、协议、存储边界。

README: updated。中英README版本和候选链接、Agent功能、发布说明、CHANGELOG、用户指南与生成changelog已同步；`check:changelog`显示90 releases、91 JSON files。落地页定位/入口不变，docs/index.html检查后no-op。

## 发布与产物

- [官方Release](https://github.com/ly-ccx/Peer-Agent/releases/tag/v0.1.0-rc.11) 于 `2026-10-10T11:54:33Z` 发布，prerelease=true、draft=false。双语说明与标签源码逐字一致。[Release38049546647](https://github.com/ly-ccx/Peer-Agent/actions/runs/38049546647)全部8个job成功，head为标签所指的438d1a6。[发布记录](evidence/rc11-published-release-20261010.json)、[工作流](evidence/rc11-release-workflow-20261010.json)。
- 14项公开资产全部实际下载，大小/SHA256与GitHub记录一致；三平台Beta更新清单的版本、文件、大小和SHA512与下载资产一致。实际Mac ZIP严格签名、Developer ID/Team ID、公证票据、Gatekeeper通过；DMG完整性通过，只读挂载后应用严格签名、公证、Gatekeeper与ZIP内app.asar一致性通过，挂载已卸载。Mac CLI/凭据助手版本和签名通过；Linux归档实际下载并解包。[资产/ZIP信任](evidence/rc11-assets-trust-20261010.json)、[DMG信任](evidence/rc11-dmg-trust-20261010.json)。
- 三平台18项真实HTTP更新发现通过：Beta5/RC2/RC9/RC10在Beta策略下发现RC11，当前RC11不重复提示，正式策略不降级到0.0.18。使用发布包实际app-update.yml、生产PeerGitHubProvider及electron-updater；临时探针仅增加RC9/RC10版本用例和绝对模块引用，没有改变生产Provider，也不安装旧客户端或写入用户设置。[真实更新发现](evidence/rc11-live-update-20261010.json)。旧Beta5/RC1–3仍按迁移指南手动安装；发现新版本不代表迁移策略改变。
- 四个npm包的固定RC11版本和rc标签公开可见，latest=0.0.18、beta=0.1.0-beta.5保持原值。隔离实际 `npm install @peer-agent/cli@0.1.0-rc.11`，postinstall从官方Release下载，CLI输出 `peer 0.1.0-rc.11`；peer/helper二进制SHA256与官方Mac归档一致。[npm安装](evidence/rc11-npm-install-20261010.json)。
- 未修改的正式签名Mac包隔离启动，app.isPackaged=true、版本RC11。紧凑页头与设置入口、概况、三条记忆、真实保存头像颜色后的身份气泡、返回对话和当前版本真实Beta更新检查通过；4张截图全部实际查看，页面无错误，拥有的应用已退出。实现者自审，independent=false；合成历史/隔离配置，没有替换日常安装。[签名包UI与实际观察](evidence/rc11-published-ui-20261010.json)。
- [Pages38049546633](https://github.com/ly-ccx/Peer-Agent/actions/runs/38049546633)成功；真实HTTP核对5项页面和数据与标签一致，manifest stable=v0.0.18、beta=v0.1.0-rc.11，构建时间有效。[Pages内容](evidence/rc11-pages-20261010.json)、[工作流](evidence/rc11-pages-workflow-20261010.json)。

## 与卡片偏差

原实施卡在交付时未授权合并/发布，本轮用户已明确授权收拢与发布。保留原实施记录，追加发布整合记录。

## 未完成与限制

- 原历史逐条统计仍缺少受治理的历史查询能力；恢复、Agent与看图能力不代表该原任务完成，不能自动签收旧任务。
- 源码回归使用scripted cognition；不替代真实供应商质量、网络时序、完整读屏或长期日用。本地图片链路尚未实连云端模型验收。
- 快捷窗透明PNG没有原生背景，不能据此证明OS背景对比度；已在review中接受为采集限制。
- Windows/Linux交互安装、复杂写任务Evidence完整性、跨供应商独立复核、七天日用与GA缺口继续保留，不能宣布总体Ready/GA。
- 升级前备份完整数据根，Desktop/CLI/Gateway同步升级；回退恢复完整兼容备份并另存新数据，不用旧宿主写入新版数据目录。
