# RC-01 性能与壳层自测实施边界

日期：2026-10-01。级别 B；依赖 Beta5 已发布。负责人已要求自主完成全部实现、自测和详细验收文档；包含必要路径、回归修复、CI及预发布合入，不新增审批停点。GA仍等待负责人全面测试。

## 边界与证据

不改 capability/permission/Evidence/Context/storage 协议。新脚本只操作 mkdtemp 隔离目录，显式区分生产数据读取、脚本执行器、真实模型和发布包。原始个人数据不重置，凭据不进入证据。每指标5次中位数并保留所有样本；规模必须200 bot/10000 messages/100000 inbox events/10000 memories，经生产读取核对。脚本回合不得充当真实快档p50。报告非全达标时exit1；供应商失败样本不能静默删除。

列表/搜索测生产应用服务投影及完整语料（首索引和热查询分列），不能仅测索引数组循环。收到/消费在实际IPC/UI或生产queue→conversation→wake链测量并写清计时边界；UI可见收到由Electron smoke额外测。收件箱冷恢复用新reader读取全部规模事件并还原游标；不能只读最后一条。空闲用独立进程初始化200宿主并稳定GC取增量RSS/heap，记录没有模型流；不是仅除以一个空数组大小。真实模型5轮要记录模型/每轮耗时/终态。

## 允许路径

- 新 `apps/desktop/scripts/seed-bot-shell-home.mjs`、`perf-project-agent.mjs`、`bot-shell-electron-smoke.mjs`、对应 `.test.mjs` 及专用fixture辅助模块（同目录）。
- `apps/desktop/package.json`：脚本入口及脚本测试登记。
- `.github/workflows/ci.yml`：mac/Linux Electron smoke（Linux Xvfb与必要系统库）；保留原完整测试门禁，不删除/skip旧测试。
- `apps/desktop/scripts/background-tasks-electron-fixture.mjs`、`apps/desktop/electron/main/global-background-service-smoke.test.mjs`：旧fixture仍导入已移除GlobalBackgroundTasksButton导致启动失败，改用现有BackgroundRunsProvider+BackgroundRuntimePanel生产组件；明确fixture入口不是当前产品全局入口，不削弱停止反馈/实际端口释放断言。新增产品图标只用SVG。
- 达标需要的生产修复：先在本边界追加测量事实和具体文件，每个修复单独提交，说明对应预算及回归测试；涉及协议/权限/Context/存储边界时先更新架构决策。

main.mjs净增0，不扩展ChatSurface/Sidebar/LlmSettingsPanel/TUIapp。验证全build→受影响包test→typecheck/architecture→mac/Linux精确HEADCI；各结果真实写handoff，性能偏差不能自行视为负责人接受。
