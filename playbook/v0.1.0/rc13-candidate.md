# RC13 图片授权继承与核验收口

创建时间：2026-10-11
最后更新：2026-10-11
状态：已发布，正式包验收完成

## 范围与源码绑定

用户明确授权“发布新的 rc”。权限实施 [PR151](https://github.com/ly-ccx/Peer-Agent/pull/151) 已合入开发线 `5217265439246c7a9d7651f2228ced7c58d0bf27`；实施前的 ADR92 与知识 PR35 已合入 main `7e71ae6`。发布准备 [PR153](https://github.com/ly-ccx/Peer-Agent/pull/153) 候选为 `88ee465519eb16239180f27c4fc8c014340ce839`。本轮同时纳入已合入的回复详情 PR150 和服务商设置 PR152。

- 图片授权绑定具体文件与文件身份、工作区、当前 Bot，30 分钟内可传给其 Worker、Verifier 与恢复回合。不同 Bot、不同文件及文件变化不能沿用许可。
- 一次批准绑定实际能力、参数与执行身份；并发回合隔离权限上下文。批准条只处理当前请求，无关排队请求不批量获准。
- 撤回、过期、父任务停止、暂停及被取代均阻止后续读取。普通聊天的同意与旧批准记录不自动成为图片许可。
- 核验有五分钟整体截止时间，父任务取消及迟到结果有明确出口；缺少有效授权且没有确认入口时及时拒绝。
- 回复详情紧凑并优先显示最新步骤；取消后的缺失文件结果不显示 null；服务商设置沿用 Frost 分组和控件圆角。

发布准备为 C 级版本与文档变更，权限和核验实现遵循 ADR92；没有新能力旁路。实现者自审不称独立审查。

## 发布前验收

- [候选 CI38116141162](https://github.com/ly-ccx/Peer-Agent/actions/runs/38116141162) 的 macOS/Linux build、typecheck、architecture、全仓 test 和 Electron smoke 全部通过。
- 本机 build、typecheck、architecture、runtime package contents、外部 npm tarball host smoke、readiness 与 source-check 通过；升级与恢复矩阵 31 项全部通过。
- 第一轮产品 capture 在回复详情悬浮断言超时；该失败包不作为通过证据。同一候选保留原断言重新捕获完整通过。145 张截图逐张实施者自审并 verify 通过；runId `7080965e-dd93-4909-b064-8d10e939add9`，源码指纹 `53ae44b15e5e43002a36c81b16b5086b90808c8d601e71e0f368c50acfa0e71f`。合入 tree 与候选一致，合入后 verify 再次通过。
- 合入后 CI38118757305 的 macOS 第一次执行在切换 760px 窗口后立即测量聊天宽度的断言失败；全仓单测无失败，Linux 完整通过。保留该失败事实，仅原样重跑失败 job；2026-10-11 07:08 UTC 第二次 macOS 完整通过，Linux 第一次完整通过，未修改源码或断言。

## 发布与正式包验收

- [RC13 Release](https://github.com/ly-ccx/Peer-Agent/releases/tag/v0.1.0-rc.13) 为 prerelease，标签绑定合入 `8141300485a5cfaf936d78a14fdf99000ebc62c6`，tree 与已审查候选一致。官方 [Release38118823815](https://github.com/ly-ccx/Peer-Agent/actions/runs/38118823815) 八个 job 全部成功。
- 14 个公开资产已全部下载，以 GitHub SHA-256 和实际大小核对；三平台更新清单的版本、文件大小及 SHA-512 全部一致。
- Mac ZIP 内 app 和 DMG 内 app 的严格 Developer ID 签名、Team `82672N97RP`、stapled notarization 与 Gatekeeper 通过，DMG 完整性及两份 app.asar 一致；正式 CLI 与凭据助手签名通过。
- 四个 npm 固定版本和 rc 标签均为 RC13，latest `0.0.18` 和 beta `0.1.0-beta.5` 不变；隔离真实 npm 安装、postinstall 下载和 CLI 版本、二进制 hash 一致。
- 三平台公开更新源的 24 个版本/通道组合通过；[Pages38118823837](https://github.com/ly-ccx/Peer-Agent/actions/runs/38118823837) 完成，五个实际 HTTP 页面/JSON 与标签源码一致。
- 原装签名 RC12 通过生产更新 IPC 与界面发现并实际下载 RC13 ZIP，17 个进度采样，缓存 SHA-256 与公开资产一致；下载后安装入口可见，没有执行安装或替换日常应用。三张截图中的前两张处于进入/缩小过渡阶段，不以单帧宣称完整动画或稳定弹窗对比度验收。
- 原装签名 RC13 包版本与 packaged 身份核对，52px 机器人设置入口、头像颜色保存及实际气泡色、概况、记忆和 Beta 无降级检查通过；四张正式包 UI 逐图自审。
- 正式包使用隔离合成权限卡，通过生产 CardView/IPC/ApplicationService 键盘批准具体图片，生成具体文件的 grant；重启保留同一 grantId，无关写入请求保持未批准。深色 1280px、浅色 760px 两张图已审查，路径与三种动作在范围内。首次验收脚本把启动恢复为 stale 的无关请求错误地要求为 open，已修正夹具断言接受仍未批准的 open/stale 状态；没有改变应用。
- 合入后 [CI38118757305](https://github.com/ly-ccx/Peer-Agent/actions/runs/38118757305) 两个平台完成通过；macOS 为保留原断言的第二次执行。

## 证据入口

本目录 `evidence/rc13-*-20261011.json` 保存来源绑定、候选 CI、首轮失败、完整截图 packet/review/result、升级矩阵、正式工作流、资产 hash、签名公证、npm、公开更新发现、旧版本真实下载、正式包 UI/图片许可及 Pages。路径以占位符脱敏，不包含个人会话、凭据或真实私有文件。

发布标签冻结后，用户新增状态栏图标设计要求进入独立 [PR154](https://github.com/ly-ccx/Peer-Agent/pull/154)，不属于 RC13 资产。

## 覆盖限制

源码交互使用脚本化认知，权限测试使用受控模型与解码适配器。Windows/Linux 交互安装、真实云模型看图质量、完整读屏、复杂外部写入、七天日用和总体 Ready/GA 不由本轮替代。升级前备份完整数据根，Desktop、CLI/TUI 与 Gateway 同步升级，回退使用完整兼容备份。
