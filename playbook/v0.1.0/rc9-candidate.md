# RC9 任务详情、对话引用与界面一致性

创建时间：2026-10-08
最后更新：2026-10-09
状态：Released

负责人已授权“发布新的 rc”。候选为 `0.1.0-rc.9`，覆盖已合入的 PR125–128，并通过 PR129 准备发布。Desktop 三平台、CLI 两平台、四个公开 npm 包沿用现有 tag 发布链；仅推进 rc dist-tag，stable/latest 保持 0.0.18，beta 保持 0.1.0-beta.5。

## 范围与架构

- 任务详情优先呈现进展、下一步与具体问题，支持资料加载、失败重试、旧报告和嵌套返回。
- 历史对话分组、搜索、预览、继续及任务展开过渡；紧凑引用位于消息气泡内部，没有装饰竖线。
- 统一语义圆角；矩形图片/主题预览保持圆角矩形；加载、展开、返回、关闭及重命名提示使用 SVG。修复诊断披露焦点滚动导致的顶部裁切。
- C 级发布准备：版本、中英 notes、生成 changelog、升级矩阵和版本断言。执行、授权、Evidence、协议、System Context 与存储边界未移动。
- 升级矩阵按真实已发布 Git RC 标签生成，包含上一版 RC8；changelog 最新版本测试读取 VERSION，避免固定 RC8 断言阻断后续候选。

## 发布前验收

候选 `84cb42851c6d31c96beab55b4e9a7f0897eb5112`，tree `639f5c5fe4002d2443eca426782d7753a55bc04f`。完整本机 build/typecheck/architecture/IPC/test 通过；桌面 5418 项，5413 通过、5 项既有跳过、0 失败。Runtime package contents 与 external-host smoke、版本/changelog/readiness/source 检查通过。

最终源码 Capture `746fbe18-5462-40f2-9fa3-62f64f5405ac`：95 张必查图片全部实际逐张查看，具体观察已写入 review.json，Verify passed；fingerprint `98dcfbced4484855a0654f785d6f02094faffaaf50fef6a9c9f710cfbe8672fd`。实施者自审，`independent=false`。实际合入同一 tree 后再 Verify passed。[产品审查](evidence/rc9-product-review-20261008.json)。

实际旧 tag 数据模块、受控 updater 与真实 SIGKILL/恢复矩阵 27 项通过，sourceDirty=false；未冒充旧安装客户端 GUI 升级。[升级与恢复](evidence/rc9-upgrade-matrix-20261008.json)。

[精确候选 CI37751694341](https://github.com/ly-ccx/Peer-Agent/actions/runs/37751694341) Mac/Linux 全部门禁成功。合成合入 `ac7a09ebb4b4c602d5bfbb2ea264c1c41a7a6901` 与候选 tree 相同；[PR129](https://github.com/ly-ccx/Peer-Agent/pull/129) 实际合入 `e2bdfa28e730b6193032e5ffeb527d1805f1a0e3`，tree 仍相同。干净合入的 readiness/source 检查及产品 Verify 通过。不可变标签 `v0.1.0-rc.9` 对象 `57e2ccef1bbfd959aaf8706a46a7c88364defb40` 指向实际合入。[源码绑定](evidence/rc9-ci-binding-20261008.json)。

首次快捷窗口采集因 Electron 异步 evaluate 被回收失败，保留失败事实，后续最终源码重新采集通过。首轮本机测试和 CI37750367173 发现 changelog 测试固定断言 RC8；修正为 VERSION 后完整测试、新 CI 与新 Capture 均重跑通过。较早 packet 未作为最终源码验收。

## 发布与产物

[合入后 CI37753489502](https://github.com/ly-ccx/Peer-Agent/actions/runs/37753489502) Mac/Linux 再次全部成功。[Release37753707229](https://github.com/ly-ccx/Peer-Agent/actions/runs/37753707229) 首次运行的全部八个 job 成功：meta、三平台 Desktop、两平台 CLI、release、publish-npm。没有改写已发布标签。[工作流](evidence/rc9-release-workflow-20261008.json)。

[GitHub RC9](https://github.com/ly-ccx/Peer-Agent/releases/tag/v0.1.0-rc.9) 于 2026-10-08T09:08:32Z 公开，prerelease=true、draft=false，14 项资产完整；发布正文与标签内中英 notes 一致。[公开资产](evidence/rc9-published-release-20261008.json)、[最终绑定](evidence/rc9-final-binding-20261008.json)。

实际下载全部 14 项资产，逐项核对 GitHub SHA256 digest 与大小。三平台 Beta 更新清单的版本、文件、大小与下载文件 sha512 一致。Mac ZIP 内未改写的正式 app 严格签名、Developer ID Team82672N97RP、公证票据及 Gatekeeper Notarized Developer ID 全部通过；DMG 完整性、只读挂载后的同一签名/公证核验通过，app.asar SHA256 与 ZIP 相同，验证后已卸载只读卷。实际 Mac CLI 为 peer 0.1.0-rc.9，凭据助手的 Developer ID 验证通过。[下载与信任](evidence/rc9-assets-trust-20261008.json)、[DMG 应用](evidence/rc9-dmg-trust-20261008.json)。Windows/Linux 下载文件哈希已核对，但没有交互安装。

公开 npm 四包 protocol/runtime-core/runtime-sdk/cli 的固定版本与 rc 标签均为 0.1.0-rc.9；latest=0.0.18、beta=0.1.0-beta.5。发布成功后部分 registry 节点短暂返回 RC8 缓存，等待版本可见后再做固定版本安装。隔离 prefix/cache 的真实 npm postinstall 下载成功，CLI 版本正确，peer 与 helper 的 SHA256 均等于 GitHub 归档二进制；未修改全局安装或用户数据。[npm 与实际安装](evidence/rc9-npm-install-metadata-20261008.json)。

生产 PeerGitHubProvider、electron-updater6.8.9 与实际 HTTP 发布元数据完成 18 项检查（3 平台×6 场景），包括 RC8 → RC9 Beta 可发现、当前 RC9 不提示降级、Stable 仍为 0.0.18；不冒充三平台安装测试。[真实更新发现](evidence/rc9-live-update-20261008.json)。

实际下载的、未改写的签名 Mac ZIP 应用使用隔离数据和 Chromium profile 启动，packaged=true、版本 RC9。四张正式包关键 UI 图片实际查看并写出具体观察：52px 页头、“机器人设置”直达设置、概况与记忆可读、关闭侧栏后消息/输入区同宽对齐。正式包生产 updaterCheck 返回当前 RC9、Beta、not-available，没有执行下载或安装。四图与合成历史不替代全部 95 张源码场景或真实模型验收。[正式包 UI](evidence/rc9-published-ui-20261008.json)。

[Pages37753707208](https://github.com/ly-ccx/Peer-Agent/actions/runs/37753707208) 成功。实际 HTTP RC9 changelog 和 manifest 正文与标签内容一致；manifest 的构建时间单独验证为有效日期。[线上日志](evidence/rc9-pages-20261008.json)。

## 覆盖限制

最终源码使用 scripted cognition；自审不是独立评审。95 张源码截图不替代真实模型回复质量、安装包完整交互、完整读屏或长期日用。快捷窗口 PNG 不证明原生半透明材质；四张旧 Artifacts/Diff 图为实际生产组件隔离场景。

本次 RC 的 Windows/Linux 交互安装、复杂写 Evidence 完整性、跨供应商核验独立性和 GA 缺口保留。回退必须恢复升级前完整兼容备份，另存新数据与产物；不得让旧宿主直接写入新数据目录。用户无需为升级重置数据。
