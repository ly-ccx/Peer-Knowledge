# RC7 流式过程与 Bot 信息归属候选

创建时间：2026-10-05
最后更新：2026-10-05
状态：Published

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
- 精确候选 [CI 37307997001](https://github.com/ly-ccx/Peer-Agent/actions/runs/37307997001) Mac/Linux 全部门禁通过。
- README: updated；docs/docs.html 同步当前 Bot 流程，经典界面有明确标识；docs/index.html 安装与入口检查 no-op。生成 changelog 86 个版本通过检查，稳定 latest 为 v0.0.18，候选 beta 为 v0.1.0-rc.7。
- PR122 已合入开发线 `4549f307ea43b249500d4425d9c14f1d1f1dd837`；实际合入、CI 合成 merge 和源码准备的 tree 均为上述值。干净合入提交 readiness/source 门禁再次通过；固定 tag `v0.1.0-rc.7` 已推送；发布工作流及实际资产检查均已通过，详见下方。

## 候选绑定

[精确源码/CI/合入绑定](evidence/rc7-candidate-ci-binding-20261005.json)，[Mac 原始窗口报告](evidence/rc7-ci-macos-window-20261005.json)，[Linux 原始窗口报告](evidence/rc7-ci-linux-window-20261005.json)。两端各 11 项流式 / 6 项信息归属通过，页面与授权错误均为零；Mac 阅读位置 5311→5311，Linux 5337→5337。真实云模型、实际子任务与对应 Evidence 不由受控夹具验收替代。

## 发布完成

[GitHub RC7](https://github.com/ly-ccx/Peer-Agent/releases/tag/v0.1.0-rc.7) 于 2026-10-05T12:32:33Z 公开，prerelease=true、draft=false，14 项资产和中英 notes 与标签一致。[Release 37309318447](https://github.com/ly-ccx/Peer-Agent/actions/runs/37309318447) 八个 job 全部成功；[Pages 37309318315](https://github.com/ly-ccx/Peer-Agent/actions/runs/37309318315) 部署成功。tag 对象 `f35a750013d4b9491b2d4fa7f156d8244d001f76` 指向前述合入提交，未重写标签。[工作流](evidence/rc7-release-workflow-20261005.json)、[资产元数据](evidence/rc7-published-release-20261005.json)。

实际下载 Mac ZIP/DMG、对应两份 blockmap、两平台 CLI 和三平台 manifest 共九份文件，大小与 GitHub SHA256 digest 全部匹配；Mac ZIP/DMG SHA512 与更新清单匹配。ZIP 应用和只读挂载 DMG 内应用通过严格签名、Developer ID Team 82672N97RP、Gatekeeper 与 stapled notarization；DMG 完整性及卸载通过。Mac CLI 与助手严格签名、实际执行版本 RC7；peer 为既有 Bun adhoc 签名，助手为 Developer ID。包内更新 Provider、项目应用服务及由标签源码按固定 TypeScript 5.9.3 编译的实时过程模块均匹配。[产物信任与源码绑定](evidence/rc7-published-assets-trust-20261005.json)、[DMG 应用](evidence/rc7-dmg-embedded-trust-20261005.json)。Windows/Linux Desktop 的 digest 来自发布元数据，并核对清单与 CI 打包；Linux CLI 已下载校验，未在本机执行。不将这些范围扩写为实体交互安装。

公开 npm 四包的固定 RC7 与 rc 标签核对通过，latest=0.0.18、beta=0.1.0-beta.5 保持不变。首次完整 packument 查询仍返回旧内容的观察保留；实际 fixed-version 与 dist-tags 端点查询四包均成功，未重复发布。[首次观察](evidence/rc7-npm-metadata-first-20261005.json)、[注册表核验](evidence/rc7-npm-metadata-passed-20261005.json)。隔离 prefix 和缓存实际安装 `@peer-agent/cli@0.1.0-rc.7`，正常 postinstall 下载后执行得到 `peer 0.1.0-rc.7`，安装与版本命令均 exit0，未修改用户全局安装。[npm 安装](evidence/rc7-npm-install-passed-20261005.json)。

使用实际包的公开 app-update.yml、生产 Provider 与 SDK，对真实 GitHub feed 和三平台清单执行 24 项联网选择/资格检查：预览中的 Beta5、RC2、RC4、RC5、RC6 选择 RC7，RC7 不出现同版或旧版本降级，正式通道不接收 RC。Node HTTP 适配器及受控 rollout 资格用于此检查，旧 Beta5/RC1–3 安装内旧 Provider 仍需手动迁移。[联网发现](evidence/rc7-update-live-discovery-passed-20261005.json)。

实际下载、未修改的签名 Mac 应用在隔离数据与 Chromium profile 中启动，回复详情聚合、概况身份/职责而无过程列表、记忆保存内容优先且管理折叠、版本 RC7 与真实检查更新后“当前已是最新版本”均通过。合成两 Bot、历史及记忆仅用于展示验证，不代表模型/真实工具/Evidence 验收；没有配置模型凭据。自有应用已退出，未替换用户已安装应用、写其数据或执行原数据迁移/安装。[签名包 UI](evidence/rc7-published-ui-passed-20261005.json)。

线上 docs.html 与 RC7 changelog 数据 SHA256 和标签源码逐字节一致，manifest latest.beta=RC7、latest.stable=0.0.18，generatedAt=2026-10-05T20:24:08+08:00。[Pages HTTP 核验](evidence/rc7-published-pages-20261005.json)。README: updated；入口与安装矩阵未变化，落地页 no-op。复杂写任务 Evidence 缺口与 GA 门槛继续保持原状态。

## 合入后的额外 CI

合入 push 触发的 CI 37309281575 首次 Linux 全部通过，Mac 在档位失败保存的采样断言处失败；完整构建、类型、架构、测试，以及流式/任务/档案检查此前已通过。原始 Playwright trace 显示 Home 操作开始到帧采样开始相隔 3019.584ms，跨过夹具 650ms 的失败回退窗口；截图显示失败提示及高档位回退。该观察不能证明响应到达前发生了回跳。[首次结果](evidence/rc7-merge-ci-first-failed-20261005.json)、[原始窗口](evidence/rc7-merge-ci-first-window-failed-20261005.json)、[trace 时序](evidence/rc7-merge-ci-timing-analysis-20261005.json)。同一合入提交重跑 Mac job 后，设置页档位检查通过，输入区在相同采样断言处失败。[第二次结果](evidence/rc7-merge-ci-second-failed-20261005.json)、[第二次原始窗口](evidence/rc7-merge-ci-second-window-failed-20261005.json)。发布前两端候选 CI 与本机门禁通过的事实不改写。

## 固定下载与 SHA256

Mac ZIP/DMG 与两 CLI 的 hash 已实际下载验证；Windows/Linux Desktop 的 hash 来自 GitHub 发布 digest。

| 平台/文件 | 固定下载 | SHA256 |
|---|---|---|
| Peer-Agent-0.1.0-rc.7-arm64.dmg | [下载](https://github.com/ly-ccx/Peer-Agent/releases/download/v0.1.0-rc.7/Peer-Agent-0.1.0-rc.7-arm64.dmg) | `2e55a4e457f3e9ef04c635f58c7e28540990ab3bff116eacc3e36976f4f621e3` |
| Peer-Agent-0.1.0-rc.7-arm64.zip | [下载](https://github.com/ly-ccx/Peer-Agent/releases/download/v0.1.0-rc.7/Peer-Agent-0.1.0-rc.7-arm64.zip) | `0b4bf8e4dccbdcfb716269ff3eaeb3128f1fc68ac37c20e45d7b00f86a94a382` |
| Peer-Agent-0.1.0-rc.7-x64.AppImage | [下载](https://github.com/ly-ccx/Peer-Agent/releases/download/v0.1.0-rc.7/Peer-Agent-0.1.0-rc.7-x64.AppImage) | `0c3685688af4b483147b6d0fb5107dbb2df075d1a66076f3f0eeb5402d32f66b` |
| Peer-Agent-0.1.0-rc.7-x64.deb | [下载](https://github.com/ly-ccx/Peer-Agent/releases/download/v0.1.0-rc.7/Peer-Agent-0.1.0-rc.7-x64.deb) | `c8301ac3340ac37fa13da6b3ce7f6bc7ac6b697ce5c37e7999392a446dfd1831` |
| Peer-Agent-Setup-0.1.0-rc.7.exe | [下载](https://github.com/ly-ccx/Peer-Agent/releases/download/v0.1.0-rc.7/Peer-Agent-Setup-0.1.0-rc.7.exe) | `7eed463986394453ee90935b42780cfe8160ff34c2903351514d74a5deded613` |
| peer-darwin-arm64.tar.gz | [下载](https://github.com/ly-ccx/Peer-Agent/releases/download/v0.1.0-rc.7/peer-darwin-arm64.tar.gz) | `2a17f4c9db44a4817155db599e016d8c4f42ce36a217ae32a81f0a259794f027` |
| peer-linux-x64.tar.gz | [下载](https://github.com/ly-ccx/Peer-Agent/releases/download/v0.1.0-rc.7/peer-linux-x64.tar.gz) | `f73e27b102f8e18cdf792c8e42aca009e77f4fb782b63c33e2989d0e6cdb67c9` |

### 发布后的验收采样修正（C 级）

为消除 Node→CDP 往返延迟与 650ms 受控失败窗口的竞态，允许只修改 `apps/desktop/scripts/bot-effort-stability-checks.mjs`，在实际 keyup 前于 renderer 中注册采样，随后收集本机帧；失败用例强制延迟 900ms 才从 Node 收集结果，确定性覆盖“回退后读取仍保留此前 pending 帧”的情况。保留原有至少 5 帧、每帧档位值、触发器/弹层各轴 <0.5px、错误提示与持久配置回退断言。该修正只影响验收脚本，产品 Runtime/协议/权限/Evidence/存储均不改变，发布 tag 与产物保持不可变。单独 PR 完成验证并合入开发线，结果随后记录。
