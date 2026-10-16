# RC15 发布与验收记录

创建时间：2026-10-16
最后更新：2026-10-16

## 范围与授权

用户明确要求发布新 RC。集成线 `PeerAgent/dev/0.1.0` 已依次合入代码 PR154（小猫状态栏图标）、PR159（Full 权限与连续看图）、PR160（中断核验核清与原工作恢复），知识 PR39/40 已合入。发布准备 PR161，仅更新版本与双语产品说明。用户授权覆盖合入和发布，无需再次确认。

## 不可变候选与门禁

代码候选头 `46155894ea777ae6be4322f5dfbd3efe99c6f220`。本机构建、类型、架构、完整测试、产品门禁单测、包外 Runtime 宿主冒烟和版本/更新日志门禁通过。真实不可变标签升级恢复矩阵 33/33 通过。标准产品包 Capture 成功，154 张必需截图全部实际查看并写逐图观察，Verify 通过；实施者自审 independent=false。Run ID `5cd6dc0d-fb0a-42cf-8a9f-173231397070`，源码指纹 `bb7362be4e0ac54f218d39918b978a0dc6e1ca7886ac61e5e5e5d5be617bb830`。窗口机器报告的 Full 四图、图片权限六生命周期与所有其他必要场景通过，页面和宿主授权异常均为空。

版本为 `0.1.0-rc.15`，使用 beta 自动更新通道和 npm rc dist-tag；正式版保持 `0.0.18`。不可变标签、Release、签名包、npm 和 Pages 均已发布，Mac 原装包及旧版本更新下载验收完成，具体覆盖见下文。README updated：Full 与 ask 模式区别、候选说明链接与版本；docs/docs.html 与生成的中英文 changelog 同步。落地页现有任务、授权和下载叙述继续适用。

## 行为与边界

- 已选择 Full 时，主 Bot、Worker、Verifier 的连续看图使用同一份本地权限判断；不悄悄改写为逐图询问。ask 模式的授权续跑、拒绝、取消、停止和五分钟超时保留。
- 图片内容跨主动让出/继续保持真实像素；重启后读取及撤权仍受当前授权控制。
- 已知工具结果在取消前关键持久化。旧中断 verify_session 必须经宿主唯一绑定和非活跃核对后才能继续原工作，不重置预算、不伪造通过、不重放真正未知副作用。
- 主 Bot 只读能力边界、任务质量和签收真值不因 Full 改变。

## 覆盖限制

产品审查由实施者执行，非独立审查。标准截图与交互为源码 Electron 和受控模型；真实云模型质量、Windows/Linux 交互安装、完整读屏、复杂外部写入、七天日用与 GA 不由这些检查代替。用户日常数据和安装应用不作为回归数据根；正式签名包使用隔离测试数据验收。

## 候选 CI 的首轮失败

[CI38839346073](https://github.com/ly-ccx/Peer-Agent/actions/runs/38839346073) 首轮 Linux 全部通过；macOS 构建、类型、架构和完整测试通过，窗口场景在首段流式文字等待处超时。已取实际失败截图与报告：右栏原始错误明确为 `Controlled stream was not advanced`，来自受控执行器每阶段 30 秒等待上界，不是真实模型连接或图片授权错误；本机相同提交的完整场景已通过。没有改生产实现、删除断言或扩大权限；保留首轮失败后仅对原提交失败的平台重跑一次，attempt 2 同一提交的 macOS 构建/类型/架构/全量测试和完整窗口回归全部通过；最终两平台检查全绿。首轮失败保留，不声称真实模型发生网络错误。

源码产品自审仍保留两项既有非阻断限制：Quick Chat 透明窗口的离屏浅色合成不能代替原生合成验证；历史侧栏摘要的旧 response_ 错误前缀尚未统一表达。详见逐图 review 与完整候选边界，不将标准截图通过称为安装版或独立验收。

## 标签与发布流水线

发布准备 PR161 已合入 `549ea1b2c76b74d3ba5acfa3d825ea52b555a22a`。合入后的 Git tree `203adcc79276e25946c5c28042f282fd914169cf` 与候选 `46155894` 完全相同；再运行 release readiness/source check 和产品 Verify 通过，源码指纹未变。不可变 annotated tag `v0.1.0-rc.15` 已推送并绑定该合入提交。

Release 工作流 [38842028963](https://github.com/ly-ccx/Peer-Agent/actions/runs/38842028963) 与 Pages [38842029087](https://github.com/ly-ccx/Peer-Agent/actions/runs/38842029087) 全部成功。[RC15 公开预发布](https://github.com/ly-ccx/Peer-Agent/releases/tag/v0.1.0-rc.15) 含 14 个资产。合入额外触发的 CI38841936973 单列状态；发布前依据为候选同 Git tree 的双平台完整 CI 和本机全部门禁。

## 公开渠道与合入后附加 CI

Release38842028963 的所有 meta、三平台 Desktop、两平台 CLI、集中 release 和 npm 发布作业全部成功。预发布已于 `2026-10-16T02:53:15Z` 公开，共 14 个资产；Pages38842029087 全部成功，五个实际 HTTP 页面/JSON 与标签内容一致，manifest 指向 RC15，正式版仍为 0.0.18。四个 npm 固定版本及 rc dist-tag 已核实，隔离真实 npm install/postinstall、CLI --version 和两个公开二进制哈希检查通过。Mac 发布包验收结果如下。

合入后额外触发的 CI38841936973 首轮 Linux 全部成功；macOS 构建、类型、架构和全量测试成功，原生 Quick Chat 菜单测试的 Electron evaluate Promise 被回收（`Resulting promise was garbage collected`），页面异常为空。此为与已验候选同 Git tree 的额外 run；未修改生产源码或公开标签，保留失败后只对失败平台原样重跑一次，attempt 2 的构建/类型/架构/全量测试仍通过，窗口回归在窄窗停止图标断言处失败（期望 1，实际 0）。已实际查看该轮失败截图：原始错误为 `Controlled stream was not advanced`，受控流已在布局检查期间达到阶段等待上界，随后停止控件消失；不是图片权限或真实模型请求。没有第三次重跑，也没有修改标签或生产源码。此附加 run 最终为 failure，不能称所有 CI 全绿；受控场景阶段时限与前置布局检查的协调仍待单独维护。发布前同 Git tree 的候选双平台 CI、本机标准 Capture/Verify 和正式包真实 HTTP 看图/更新验收结果各自保留，不相互替代。

## 发布后原装包与真实 HTTP 验收

- 14 个公开资产全部实际下载，文件长度及 SHA-256 与 GitHub 公开记录一致；三份 beta 更新清单中的 SHA-512 和文件大小逐项匹配真实下载文件。
- Mac ZIP 的 Developer ID、Team ID `82672N97RP`、严格签名、stapled 公证及 Gatekeeper 通过。DMG 只读挂载，内置 App 同样通过签名、公证和 Gatekeeper，app.asar 与 ZIP 完全相同，挂载已释放。CLI/helper 签名和版本通过。
- 原装 app-update.yml 存在且指向正确仓库。六个关键 Runtime/SDK 模块与已验候选编译结果逐字节相同，含中断核验恢复、协调、核验、预算、图片上下文和先提交结果再取消的 SDK；小猫 16/32 PNG 与源码资产哈希一致。
- 正式签名包首次运行和退出重启后，各经正常 HTTP Provider 入口读取四张不同项目外 PNG；总计 8 次实际 view_image 原调用，四种 PNG 字节的 SHA-256 在两轮请求中都真实出现。Full 持久设置生效，无图片权限卡/批准记录，Evidence 持久化；未注入 Tool Results 或绕过权限层。两个实际窗口截图自审通过，测试专用凭证已清理。认知由受控 loopback 服务提供，不代表云模型图像理解质量。
- 原装包 6 项设置/概况/记忆/聊天/配色/实际更新检查通过，当前 RC15 不提供降级。4 张实际 UI 截图自审通过。
- 原装 RC14 通过生产更新入口实际发现并下载 RC15，缓存 ZIP 的 SHA-256 与公开资产一致，实际可用/下载/安装就绪三张截图自审。缓存与数据隔离，关闭自动安装交接，未替换用户日常应用或执行 Squirrel 安装；不能把下载验收称为安装器交接验收。
- 三平台 27 项真实公开元数据资格检查通过，RC14 在 macOS/Windows/Linux 均选择 RC15；检查不下载执行 Windows/Linux 安装器。
- 四个 npm 固定版本/rc 标签与正式版 0.0.18 核对通过，隔离 npm install/postinstall、CLI --version 及安装后的 peer/helper 与公开归档二进制哈希一致。Pages 五项公开 HTTP 页面/JSON 验证通过。

详细记录和 9 张实际发布包截图见 `evidence/rc15-published-validation-20261016.json`，逐图审查为实施者自审，不称独立审查。

### Mac 资产固定摘要

| 资产 | SHA-256 |
|---|---|
| `Peer-Agent-0.1.0-rc.15-arm64.zip` | `2d828aa0a6d62c4ce68b30192cc3e5115fca56969bbf38a01e81d80a109e4078` |
| `Peer-Agent-0.1.0-rc.15-arm64.dmg` | `c66b497517dea181221ffe3968fd1bbb6a9397cdbd64c79c24204d44518d70b3` |
