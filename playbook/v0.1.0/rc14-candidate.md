# RC14 图片权限请求完整生命周期

创建时间：2026-10-12
最后更新：2026-10-12
状态：RC14 已发布，正式包验收通过；合入后 CI 收尾中

## 范围与源码绑定

用户明确授权合并两个 PR、发布新的 RC 并验收。代码 [PR156](https://github.com/ly-ccx/Peer-Agent/pull/156) 已合入开发线 `e49ec23e4927579b1c7ece082e19bfa047a0f106`，知识 [PR37](https://github.com/ly-ccx/Peer-Knowledge/pull/37) 已合入 main `160c6f66c257228e5601dae0edc5e027cd08890f`，ADR92 §8 先于实现完成。发布准备 [PR157](https://github.com/ly-ccx/Peer-Agent/pull/157) 初始候选 `983ff6469955fb3cfb322b1142ed16f7faa97418`；仅验收脚本修正后的候选 `fa75a8d31cd7ba9296310dc202bab4d09bcc08cc`，同时纳入已合入 PR155 回复活动扫光。PR154 小猫状态栏图标未合入，不属于本次资产。

- Bot 的真实图片权限请求由共享 ApprovalStore 投影成权限卡，并静态显示“等待你的授权”。普通文字同意不替代本地 PermissionGrant。
- “仅这一次”“本轮允许此图片”“拒绝”“取消本次读取”处理具体请求。批准后原调用继续；本轮许可仅覆盖当前图片、当前 Bot 及其任务，30 分钟内有效。
- 等待授权最多五分钟。拒绝、取消、停止生成及超时均关闭按钮，保留结构化 Tool Result 与 Evidence；迟到批准不能重新打开终态请求。
- 权限等待生命周期遵循 ADR92，通过 Projection → Tool Call → PermissionGrant → Evidence；发布准备属于 C 级，不另建图片执行路径。
- 更新中英文 release notes、CHANGELOG、README、用户权限文档及生成的日志数据。README: updated；落地页检查后无须改动。稳定版及 npm latest 保持 0.0.18，npm beta 保持 0.1.0-beta.5。

## 发布前验收

- build、typecheck、architecture/ui、Runtime 包内容、外部 npm tarball host、readiness、source-check、changelog 与版本一致性通过。升级恢复矩阵 32 项全部通过。
- 产品 capture 共 152 张截图已逐图实施者自审，verify 通过。最终 runId `e910adb2-4514-4183-aa80-1b0c5b0baea9`，sourceFingerprint `82d13bf3f40ea43bdb7e1ddc694321863142954b51cc320a6bddaa41b62eac71`，绑定 `fa75a8d3`。独立审查为 false；已有两项非阻塞限制详见 review。
- [候选 CI38152736752](https://github.com/ly-ccx/Peer-Agent/actions/runs/38152736752) 首次 Linux 全流程通过；macOS build、typecheck、architecture 与单测通过，在 quick-chat 原生下拉测试 `selectNative` 的 inspector Promise 回收失败：`Resulting promise was garbage collected`，页面错误为空。保留首轮报告；未修改源码、断言或移除该 gate，仅重跑失败 job。第二次快捷界面通过，随后旧任务 disclosure 连续帧断言失败；该失败没有保存 throw 前的采样数组，不能据此断言真实动画实现错误或纯掉帧。第二次失败报告仍记录图片权限六分支通过；同一源码本机 152 图完整产品验收和已合入 PR156 两平台 CI 通过。第三次在快速更新完成后断言 outgoing modal 仍存在失败，定位为远程动作耗时超过 280ms 动画后再查询瞬态 DOM 的观察时机竞态。修正仅限三个验收脚本：点击前安装采样器并检查完整保留内容及下载完成发生在退出过程中；下拉变更明确返回同步值；任务折叠等前一有限过渡结束、减少 PNG 录制负载并在断言前存下采样。连续帧原断言全部保留。最终 [候选 CI38155979769](https://github.com/ly-ccx/Peer-Agent/actions/runs/38155979769) macOS / Linux 全部通过；完整 152 张截图包已重跑并逐图自审，verify 通过，32 项升级恢复矩阵在最终候选重跑通过。
- 额外正常 HTTP 模型接口验证使用隔离合成数据和受控模型意图，实际 Runtime Projection 暴露 view_image，实际 PermissionGate 自动生成授权卡，授权后 native 图片解码与像素 SHA-256 `431ced6916a2a21a156e38701afe55bbd7f88969fbbfc56d7fe099d47f265460` 到达下一次 provider request，调用 Evidence 保留。六个分支全部完成；五分钟超时实际等待 300453ms。停止时旧回合记录另含一个 not_executed 占位，该占位没有触发第二次实际调用；只有一次 view_image 实际执行，取消 Evidence 保留。

## 发布与签名包验收

- 发布准备 PR157 已合入 `f931664783e08ea7673519d72e6ded1369e3d1ee`，与候选 `fa75a8d3` 的 Git tree 完全一致。合并后再次验证同一 152 图 review 绑定、readiness、source-check、版本和日志一致性通过。不可变标签 `v0.1.0-rc.14` 绑定该提交。
- [RC14 Release](https://github.com/ly-ccx/Peer-Agent/releases/tag/v0.1.0-rc.14) 在 2026-10-11 17:00:30 UTC 公开（北京时间 10-12 01:00:30），prerelease=true、draft=false。官方 [Release38157279556](https://github.com/ly-ccx/Peer-Agent/actions/runs/38157279556) 八个 job 全部成功，14 个公开资产全部下载并验证 GitHub SHA-256 与实际大小；三平台更新清单版本、SHA-512 与文件大小一致。
- Mac ZIP 与实际 DMG 内的 app 均通过严格 Developer ID 签名、Team `82672N97RP`、stapled notarization 与 Gatekeeper；DMG 完整性、ZIP/DMG 的 app.asar 一致，正式 CLI 和凭据助手签名通过。
- 四个 npm 固定版本和 rc 标签为 RC14，latest `0.0.18` 与 beta `0.1.0-beta.5` 保持不变；实际隔离 npm 安装、postinstall、CLI 版本及 binary/helper hash 与发布归档相符。
- 三平台 24 项实际公开更新源检查通过，包括 RC13 升级 RC14、当前 RC14 无降级。原装签名 RC13 通过生产 IPC 和真实界面发现并下载 RC14，14 个进度采样从 0% 到 100%；下载 ZIP 的 SHA-256 与公开资产一致，完成后安装按钮可见，没有执行安装或替换日常应用。三张图中的前两张处于入场/退场过渡阶段，不将单帧视为稳定对比度或完整动效证明；完整产品包另有连续帧验证。
- 原装签名 RC14 的版本与 packaged 身份核对、52px 标题、SVG 机器人设置入口直达设置页、头像颜色保存及实际助手气泡颜色、概况、记忆和真实 Beta 检查无降级通过，四张正式包 UI 已逐图实施者自审。
- 原装签名 RC14 通过实际 HTTP provider adapter、Bot 宿主、Runtime Projection、view_image Tool Call、PermissionGate、native 图片解码和 Evidence 完成六个场景：允许一次、任务内具体图片许可、拒绝、取消本次读取、停止回复、实际默认五分钟超时。权限卡由真实待批准自动生成，没有注入 Tool Result 或预制卡片。实际像素 SHA-256 为 `431ced6916a2a21a156e38701afe55bbd7f88969fbbfc56d7fe099d47f265460`，仅允许分支进入下一次模型 HTTP 请求；任务内分支两次原调用使用同一个许可，没有重新启动任务。四个否定分支没有像素传入，终态旧按钮关闭，迟到批准无效；超时实测 `300463ms`。12 张截图（含浅色 760px 与深色 1280px）全部逐图自审；受控 loopback 模型只提供认知意图，不替代云模型视觉质量验收。
- [Pages38157279576](https://github.com/ly-ccx/Peer-Agent/actions/runs/38157279576) 全部成功，五个实际 HTTP 页面/JSON 与标签源码匹配，公开预览清单为 RC14，正式版仍为 0.0.18。

### 合入后 CI 收尾

[CI38157270109](https://github.com/ly-ccx/Peer-Agent/actions/runs/38157270109) 的首轮 Linux build、typecheck、architecture 和完整单测均通过；Electron smoke 在原有任务资料再次展开后点击“打开现场”，等待 nested scene 15 秒超时（`bot-task-detail-checks.mjs:132`），页面错误为空。失败报告和实际截图已保留。该失败发生在新增图片权限用例之前，同一 Git tree 的候选两平台完整 CI 与本机 152 图验收已通过；源码仅表明入口同步 setSceneOpen，截图/日志不足以证明是应用缺陷或点击与折叠过渡的竞态。未删除断言或改动已发布标签；macOS 首轮已于 17:14:08 UTC 完整通过；随后只原样重跑 Linux 失败 job，保留首次失败事实，第二次结果待补齐。

### 固定下载摘要

| Mac 资产 | SHA-256 |
|---|---|
| `Peer-Agent-0.1.0-rc.14-arm64.dmg` | `b68f4951df22157757bbe1a61eef9f6a16444da10d4c008fa590e4a7a1e7267e` |
| `Peer-Agent-0.1.0-rc.14-arm64.zip` | `63d9476e33bfb2321e14525037c7705c9fced13d44801e7aedb24b14b19c40bf` |

## 证据入口与覆盖限制

`evidence/rc14-*-20261012.json` 保存来源绑定和实际门禁结果，路径以占位符脱敏。截图仅为隔离合成数据，真实数据和日常安装保持原状。实现者自审不称独立审查。真实云模型视觉判断质量、Windows/Linux 交互安装、完整读屏、复杂外部写入、七天日用和总体 Ready/GA 不能由受控认知及本轮检查替代。
