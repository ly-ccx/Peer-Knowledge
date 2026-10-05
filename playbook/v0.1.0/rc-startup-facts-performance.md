# RC 启动与机器人切换卡顿修复

日期：2026-10-02。级别 B；负责人已授权自主修复、完成自测与预发布交付，正式版仍等待负责人验收。

## 实测问题与边界

安装版 rc.2 原窗口正常退出重开后，主进程 CPU 接近 100%，内存峰值约 1GB。使用本机历史/计划的隔离副本、停用执行记录并重绑定到临时项目，在安装版主进程 V8 profile 中复现：`project-agent-host.mjs` 的 `readFacts` 按每条 Goal 调用 `getConversation` 判断 workspaceId，反复同步读取并解析完整历史。401 条计划引用重复会话，其中一个历史文件约 46MB。索引列表与全量计划详情本身读取仅数毫秒，不能用它们的预算代替此调用链。

修复只替换此事实读取的内部实现：一次读取新鲜会话元数据索引，覆盖 default/project_agent/work_session 和归档会话；仅水合属于目标项目的计划，继续使用原 delegationFactsForWorkspace。无缓存权限真值，无新 IPC、工具、依赖、数据路径、Context 或 Evidence 契约。Lease、输入、恢复、审批与失败事件仍走既有路径。历史内容及原用户配置不重置。

## 允许改动

- 新 `apps/desktop/electron/main/project-agent/delegation-facts-reader.mjs` 及 `.test.mjs`。
- `apps/desktop/electron/main/project-agent/project-agent-host.mjs`：替换原 readFacts 装配，移除原重复历史读取。
- `apps/desktop/electron/main/project-agent/desktop-integration.test.mjs`：真实 store/host 回归。
- 本卡、RC 自测报告与脱敏测量证据。

不修改 main.mjs、ConversationStore 协议、权限/Lease/调度/Context、原用户数据及已发布 rc.2/tag/资产。

## 退出条件

先红测试复现 readFacts 扫描正文；修复后同会话多计划只读一次元数据、不读正文，归属隔离正确且外部 store 写入立即生效。覆盖真实 host 唤醒及各会话角色、归档/缺失会话；保留原结构化依赖事实。安装版副本首次 profile 因选到 quick-chat 窗口触发 IPC 角色拒绝，属于测量夹具失败，不能记通过；CPU profile 仍能定位生产热路径。修复后用正确主窗口复测启动/空闲/切换，记录所有样本及 owned 退出。focused/受影响包完整测试/build/typecheck/architecture 与两平台 CI 通过后交付。

原窗口 net::ERR_FAILED 单独追查。新进程 GPT-6.1 Sol 已有真实 post_reply 成功，不能据此把原窗口错误、复杂任务或总体 RC 标为 Ready。

### 网络报错根因收敛（2026-10-02）

原会话 GET 0–2ms 失败，而同进程内新内存会话 GET 返回 405。此前复制 profile / 简单数据能联网，不能据此断言原 profile 损坏。随后相同历史/401 计划的单机器人旧版本 13.5s ready、三次 GET 405；双机器人旧版本 24.7s ready、三次 GET 1ms ERR_FAILED，Chromium 日志明确为“15 seconds with no connection”后退出 NetworkService。相同 Electron 41.7.1 的修复源码双机器人 3.8s ready、三次 GET 405，无此退出。主进程重复历史读取使初始连接超时，NetworkService 重启后默认会话请求仍失败；Electron 官方 [PR49887](https://github.com/electron/electron/pull/49887)也记录这一后续故障，但本卡未升级依赖或绕到 Node fetch。

[原窗口与控制对比证据](evidence/rc-startup-network-diagnosis-20261002.json)。仅 unauth GET，不能替代真实模型和新签名包验证；原数据/配置未重置。

## 交付与验证

代码 PR107，源提交 `3a1069d0`，两平台 CI `36975763494` SUCCESS。下载的 macOS/Linux bot-shell 报告均 ok、无 pageErrors，源为合成 merge `9dfb194c`；source/CI/合入 Git tree 均 `c468c7fa231f7f7c6b07dd4577c32243f5b9d1a0`。已授权合入 `68b9689e`，主开发工作区已快进同步。

本机 focused 35/35、完整桌面 5301 中 5296 通过/5 既有 skip/0 新增、i18n 1/1；完整 build/typecheck/architecture 通过。同一只读副本五次测量中位数 4085.458→0.506ms，正文读取 401→0 且事实一致；真实源码窗口启动 ready 3480ms，八次实际双机器人切换 75–167ms，50ms 主进程探针最大间隔 104ms。保留前两次夹具失败，不计通过。详见[测量证据](evidence/rc-startup-facts-performance-20261002.json)。尚未更新已安装 rc.2，须新候选包复测；原网络故障另行追查，总体未 Ready。
