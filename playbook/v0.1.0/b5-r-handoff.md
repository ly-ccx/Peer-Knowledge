# B5-R 多入口预发布交接（进行中）

日期：2026-10-01。准备代码 `31aa7fff` / PR #91，双平台CI在途；尚未打tag，不能宣布Beta5已发布。正式版仍0.0.18。实施边界见 [b5-r-release.md](b5-r-release.md)。

## 已完成的准备与自测

stamp-version更新beta5版本事实、README beta标记、中英说明与changelog。根build/type/architecture/最终完整test均exit0（Desktop5238，5既有skip；Runtime976/TUI749/Gateway200/Protocol227）。版本/来源/changelog/提交HEAD后readiness通过。首次根测试的发布事实断言仍写死beta4，更新为beta5后完整复跑通过，没有跳过；未提交的readiness按HEAD检查版本diff，提交后通过。

真实配置glm-5.3-flash：源码Electron拥有租约，独立Bun TUI为客户端发只读README请求，desktop实际read_file Evidence后post_reply；同时配对真实HTTP/WebSocket设备适配发同项目输入，两次同ID返回首次回执、对话仅一条，Desktop真实模型回复；Desktop退出后TUI获取租约、恢复输入并真实read_file/post_reply。三轮均实读BETA5_HANDOFF_OK，不开写任务，pageErrors0、owned进程正常退出、复制的模型凭据清理。

[脱敏证据](evidence/b5-r-source-multi-entry-20261001.json)：精确准备代码head，真实模型，不是脚本回复。Remote使用test账户、memory identity、loopback socket seam，共享真实宿主facts/queue、不能执行；不冒充已部署OIDC或真实手机。不是安装包证据，最终签名候选版复测/远程真实任务批准提示/产物/npm事实仍待发布后补齐。

## 待完成

双平台CI/Review/合入→dev tag v0.1.0-beta.5→三平台Desktop/两平台CLI/DeveloperID公证/14资产/npm四包beta验证→mac arm64真实发布包多入口自测→更新release计划§5.2/§12.1。本卡退出后RC01–05与详细用户手册。GA仍待用户全面测试。
