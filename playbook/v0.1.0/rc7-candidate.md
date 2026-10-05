# RC7 流式过程与 Bot 信息归属候选

创建时间：2026-10-05
最后更新：2026-10-05
状态：Preparing

负责人明确授权“发布 rc”。目标 `0.1.0-rc.7`，在开发线发布 Desktop 三平台、CLI 两平台和公开 Runtime npm 四包；npm rc 通道前进，稳定版与 beta dist-tag 保持原版本。

## 范围与允许改动

复用已验收源码 PR122（最终 b8d280d9；双平台 CI 37305218500）。沿用 `PeerAgent/pa/rc-live-process` 准备、CI 后合入 `PeerAgent/dev/0.1.0`，在已核对的合入提交打不可变 RC7 tag。

发布文件限于：`release-notes/v0.1.0-rc.7.md`、`CHANGELOG.md`、`docs/docs.html`、生成的 `docs/changelog-data/*`、`README.md`/`README.zh-CN.md`、`scripts/build-changelog.test.mjs`、`scripts/rc-upgrade-matrix.mjs`/`.test.mjs`，及 `stamp-version.mjs` 管理的 VERSION、12 个 package.json、凭据助手 Cargo.toml/Cargo.lock。不新增发布通道或依赖，架构边界沿用 ADR87；此前“不发新版本”的卡片约束由本次发布授权更新。

## 产品范围

- 原有流式正文保留；实际工具动作、耗时与扫光，分层展开真实预览，完成/停止/失败交接保持状态。
- 任务名与最新本机状态，用户处理入口，回复依据聚合。
- 概况描述 Bot，记忆展示保存内容，过程/证据独立查看与返回。
- 档位保存稳定、流式历史阅读位置保持；验收夹具隔离交互与后台认知。

[交互方案与实机截图](../../design/product/bot-human-readable-work-surfaces.md)、[机器报告](evidence/bot-work-surfaces-qa-20261005.json)。发布不会将受控认知/会话截图视为真实任务执行或 Evidence 验收。

## 发布门禁

中英 notes / CHANGELOG / 用户文档 / 生成 changelog → README 漂移检查 → stamp/version/readiness/source → 本机完整构建、类型、架构、测试与升级矩阵 → 精确候选双平台 CI → 按授权合入/tag → Release/Pages 工作流 → 实际资产、更新清单、Mac 签名公证、CLI 版本、npm 元数据与隔离安装核验。

复杂写任务 Evidence 缺口仍阻塞总体 Ready 和 GA；实体 Windows/Linux 安装、生产远程、实体手机与七天日用不由本次候选发布替代。

## 当前记录

- 发布准备提交 `d59af116a9e05845b19149e445918ccbab63014d`，树 `2301b4aad94b2f08f0c60d149065bef2d3e66925`，25 个发布文件。源码与发布准备均已推送。
- 本机完整 build/typecheck/architecture/test、25 项升级/恢复矩阵、公开 Runtime pack-check/外部宿主 smoke、release source tests 和 version/readiness/source 门禁通过。
- 正式原生窗口：11 项流式、6 项信息归属、档位保存/失败和阅读位置检查通过；无页面或授权错误。受控夹具仅验证展示链；详见 [本机门禁报告](evidence/rc7-source-gates-20261005.json)。
- 精确候选 [CI 37307997001](https://github.com/ly-ccx/Peer-Agent/actions/runs/37307997001) 运行中，发布前要求两平台通过。
- README: updated；docs/docs.html 同步当前 Bot 流程，经典界面有明确标识；docs/index.html 安装与入口检查 no-op。生成 changelog 86 个版本通过检查，稳定 latest 为 v0.0.18，候选 beta 为 v0.1.0-rc.7。
- 合入、tag 与公开资产尚未发生，后续根据真实结果追加。
