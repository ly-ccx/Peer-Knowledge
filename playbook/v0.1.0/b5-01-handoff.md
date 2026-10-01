# B5-01 终端宿主交接

创建时间：2026-10-01
最后更新：2026-10-01

## 卡片、分支与状态

B5-01 TUI 运行时接入。基线 dev `ca0736da`；代码分支 `PeerAgent/pa/b5-01-tui-host`，代码 [PR #86](https://github.com/ly-ccx/Peer-Agent/pull/86)。实施契约见 `b5-01-tui-host.md`，先于代码登记。状态：本地 Review 与最终双平台 CI 通过，按负责人既有授权合入。

提交：`220078bb` 共享宿主；`23761c4f` 恢复屏障；`dfb1e12c` 构造类型适配；`ea948630` 退出和切换项目的准入关闭。每次提交均已推送。

## 改了什么

- runner / supervisor / Goal 宿主 / worktree 与合回 / Watch / 验证 / 事实与回复 / 提示资产共享至 runtime-node；桌面保持兼容导出及平台装配。
- 终端持有租约时通过实际 Pipeline、Manifest、Projection、Provider、Grant / Evidence 执行；桌面持有租约时终端仅提交输入队列和每秒读取变更投影。
- 接管先停止旧执行再释放租约；退出、切换在异步等待前关闭准入；恢复屏障关闭前不能启动任务。仅恢复 host_handoff 暂停，保留执行 intent，用户暂停和完成状态不改写。
- 共享 GoalStore、跨进程缓存版本失效、持久只读 Gate、Hook 后执行权复查、批准身份与一次性 args digest、流失败的实际文本保留。
- 共享模型元数据和 OpenCode Go wire / endpoint / session header；API-key Responses 与 Messages 沿既有 Provider seam。
- 桌面 typed takeover IPC / catalog / preload / SVG 控件；main.mjs 净增 0。

## 与卡片的偏差和架构影响

A 级共享提取及必要模型兼容、恢复、只读路径先在 Accepted 实施契约登记。无新依赖或存储根。模型负责认知，宿主负责授权、能力与证据；界面没有执行权。旧入口通过兼容 Adapter 引用共享实现。TUI 产品界面与 CLI 默认分支仍由 B5-02 交付。

## 实际验证

命令：`pnpm build`、`pnpm test`、`pnpm typecheck`、`pnpm architecture:check`、`pnpm --filter @peer-agent/desktop ipc:check`、`git diff --check`；收尾 TUI 变更后再次运行 `pnpm --filter @peer-agent/tui build` / `test` / `typecheck`。

- 全仓 build / test / typecheck / architecture / IPC 通过：Runtime 968，Desktop 5206 / 5 既有跳过，Protocol 173。最终终端全包 735 通过，0 失败 / 0 跳过；定向项目模块 21 通过。
- 新增恢复屏障测试先失败（未恢复却 ready=true）后通过；退出竞争测试先失败（停止期间启动第二个回合）后通过。没有删除、跳过或放宽既有用例。
- 脚本化实际 Pipeline 覆盖双进程消费、同时启动、接管和停流、任务委托与独立验证、真实文件 Grant / Evidence、持久批准、只读和 Hook 后重查、任务退出状态及恢复 intent。
- 真实 Electron + 独立 Bun + `glm-5.3-flash`：桌面持有时终端输入由桌面读取 README 并 post_reply；实际退出 Electron 后，终端接管并读取同一文件 / 回复。每个 inputId 的 canonical user_input 仅一条，没有开任务或改文件；页面错误 0；四个实际 read_file / post_reply Evidence 索引已登记。见 [脱敏真实记录](evidence/b5-01-real-model-20261001.json)。该记录在干净 `dfb1e12c` 上运行，后续退出竞争修复有单独自动回归，不混称为相同提交。
- 曾有真实调用超时：一次终端 waiting_provider，一次桌面明确 upstream service timeout 并投影 unavailable 卡。隔离重放正常，随后同一真实模型两次交接成功；不隐藏这些失败，也不将单次网络问题记作功能永久不可用。
- 临时凭据 / device identity / 模型配置副本已删除，测试自有进程已退出；未迁移或修改真实用户数据。

## Review 与未完成

本轮本地 Review 已修复恢复屏障和退出竞争。最终 `ea948630` 的 [CI 36872310737](https://github.com/ly-ccx/Peer-Agent/actions/runs/36872310737) 已通过（macOS 4m9s、Linux 3m4s）。本地 Review 的两项缺陷均有先红后绿的回归记录，按负责人既有授权合入。终端产品 UI / 录屏、手机页面 / 远程准入、完整 RC 自测矩阵、安装候选版与详细用户测试文档属于后续卡片，均继续执行。正式版本等待用户全面测试后明确确认。
