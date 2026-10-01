# B5-02 终端机器人界面实施边界

创建时间：2026-10-01
最后更新：2026-10-01

状态：Accepted。B5-01 已通过双平台 CI 并合入 dev `f69691ac`（代码 #86、知识 #17）。负责人已授权完成所有剩余 Beta5 / RC 工作及必要修复、Review、合并和预发布；GA 仍等待用户全面测试确认。

## B 级实施与 A 级批准边界补齐

新增 BotListView、BotConversationView、CardLine、commands、ProjectApp 和纯投影 / 入口选择模块；大 app.tsx 不加业务逻辑。终端界面使用共享目录、输入队列和卡片事实；不复制任务推进、权限、签收、记忆或目标算法。经典界面沿原 App 入口，peer exec / ACP 维持原行为。

- peer 在已有机器人目录打开对话，未绑定目录询问确认；拒绝进入经典模式。peer bots 打开列表，peer --classic 强制经典模式。切经典时先停止终端项目宿主并释放租约，再启动经典 Runtime。
- 列表键盘选择、对话回复锚点 / 标记、编号卡片与动作、任务详情 / 记忆 / 目标 / 接管命令。所有编号绑定当前 workspaceId 和真实 cardId；更新后过期卡片不可操作。批准只通过宿主批准端口，客户端提示在桌面处理。
- 人类卡片操作沿共享 supervisor / lifecycle / objective / memory seam；不调用模型工具冒充批准。客户端可提交普通消息与回答，签收、合回、记忆冲突等本机事实变更要求当前租约持有者。关机等待现有宿主的停止 Promise。
- TUI 只显示经过控制字符过滤的文本，防止会话内容改变终端状态。跟随已有语言和主题存储，终端不引入字符装饰图标。

终端每个任务回合新建 Runtime，现有 allow-session 若只存在该 Runtime 会在下一回合消失。补齐由本地 executor 持有的批准 scope 集合，经既有 TuiHost Provider 权限 seam 共享；scope 必须包含持久 session / plan / workspace 身份、capability 和工作路径。不能由 renderer 保存批准真值；不得跨任务、跨工作区或跨宿主继承。退出 / 切换 / 租约丢失后清除，重启 stale 批准仍走一次性 argsDigest。补入 tui-runtime、tui-host、tui-turn-executor 及批准隔离测试。此部分升级为 A 级，先登记本文，不扩大可见工具或增加 IPC。

## 必要路径补齐

原卡漏列实际程序入口。补入 `apps/tui/src/index.tsx`、`tui-shutdown.ts` 与入口测试（异步关机保持既有同步 shutdown API）、`tui-project-client.ts` / `tui-project-host.ts` 的用户动作装配与测试。不增加 main.mjs / ChatSurface / Sidebar / LlmSettingsPanel，也不增加 IPC、依赖或持久化根。

已有 bot-directory 的 before 是向前分页，兼容性测试明确依赖它。补入 `packages/runtime-node/src/project-agent/bot-directory.mjs` 与测试，增加显式 latest 分页选项供新 TUI 使用；默认旧语义完全保留。对话可以翻到更早页并回到最新，不让第一页永久遮住新回复。

## 验证与交接

命令解析、编号稳定 / 过期拒绝、绑定 yes / no / classic / bots 分支、分页、控制字符、实际卡片动作与客户端批准拒绝；终端全包、共享目录包、build / typecheck / architecture、经典回归和双平台 CI。真实终端录屏附交接，脚本模型与真实模型分别标注。
