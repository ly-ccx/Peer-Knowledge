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
