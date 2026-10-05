# RC命令核验快照补修

2026-10-02。Accepted，依负责人“全部做完并先自测”的修复授权。A级：扩展既有EvidenceIndex执行快照及核验器事实准入；先修订ADR80与运行时契约，再实施。依赖设置页PR99已合入；CLI发布装配PR100独立，不修改其路径。

## 实际失败

真实RC1双写任务A在独立worktree内写入正确内容，随后Bash精确字节检查exit0。该实际工具引用在criterionResults中，但核验器只准入旧read_file快照，判定证据缺失而保持核验失败。B使用新的read_file引用核验通过。失败证据见 `evidence/rc-installed-complex-first-failed-20261002.json`。不把文件已写或暂态completed当全链通过。另一次代理背景回合提供方确实返回空文本/零工具，保留错误闸门，后续单独验证Retry恢复。

## 边界与实现

- 既有 `bodyPreview` 增加 `kind: 'command'`，来源只能是实际 `local.shell.exec` 的成功终态、exitCode0且已allow的Provider执行结果。仅记录结构化stdout/stderr/退出码的脱敏限长JSON；不把命令参数、助手声明、goal wrapper、运行中后台任务、拒绝/失败/超时/中断升级为成功快照。单条4000字符、总体12000字符保持。
- file行为兼容；新共享Tool Result快照准入Module收拢两个宿主的提取。索引只接受对应capability/tool身份，首个原始Provider正文不可被wrapper覆盖；旧索引无快照不补造历史内容。
- 核验器按criterion引用优先取证，其后叶子引用；显式外国planId不得借同conversation越界。时间戳保留，旧文件快照与新的命令事实都能检查；没有新鲜证据仍必须失败，不能用旧快照推测新内容。
- 执行正文只进入既有Verifier用户事实请求，不新增系统指令来源/能力/权限/IPC/存储目录。展示沿现有 `command` Evidence kind；不重读磁盘覆盖历史快照。

## 允许改动

- `packages/protocol/src/goal.ts`
- 新 `packages/runtime-node/src/project-agent/tool-result-evidence-preview.mjs` 及 `.test.mjs`
- `packages/runtime-node/src/index.ts`
- `packages/runtime-node/src/goal-plan-store.mjs`、`goal-plan-store.cache.test.mjs`
- `packages/runtime-node/src/project-agent/evidence-presenter.mjs`、`verifier-evidence.mjs`、`goal-runner-host.mjs`
- `apps/desktop/electron/main/chat-runtime/file-evidence-preview.mjs`、`tool-orchestrator.mjs`及`.test.mjs`
- `apps/desktop/electron/main/agent-host/verifier-evidence.test.mjs`、`goal-runner-host.test.mjs`
- `apps/desktop/electron/main/project-agent/evidence-presenter.test.mjs`
- `apps/tui/src/tui-host.ts`、`tui-host.test.ts`
- 本卡、ADR80、运行时契约、自测/测试指南及交付状态/证据。

不改main.mjs、App/chat大组件、凭据/权限/签收闸门，不新增依赖/执行通道/能力。不更改旧tag/资产，不发布GA。

## 测试/退出条件

先红测试复现command标准引用丢失；覆盖Desktop和Node两种Provider结果、PermissionGrant/ToolResult绑定、拒绝/失败/运行/超时/取消、秘密脱敏/截断/4000与12000预算、索引重启/不可伪造覆盖、跨plan拒绝、标准引用优先、真实两个宿主工具到索引及Verifier准入。受影响包完整测试/build/typecheck/architecture与两平台CI。合入后rc.2重新下载，实际批准双任务、独立核验、关联汇报、用户签收及单独合回授权均通过才Ready；真实空响应的Retry恢复也需留下证据。


## 源码与门禁记录

源码HEAD35f4606d已推送，代码PR101。build、typecheck、architecture通过；六文件focused45/45、runtime-node1002/1002、TUI751/751及i18n AST1/1通过。Desktop全量5292项：5286通过、原有5项skip、一项goal-plan-store增量订阅超时；按现有回归规则单文件隔离重跑142/142通过，未增加skip或放宽超时。两平台CI36956003447待macOS窗口末段，Linux已通过。

同HEAD真实双写首轮：A完成且host独立核验通过，B实际收到L1执行角色与L7 phase=running，但仍误把父历史批准要求作为新批准，自己标waiting_user；180秒等待失败，原项目未写、未签收、未合回。完整失败保存 `evidence/rc-command-source-first-failed-20261002.json`。另一次背景回合为空响应，沿既有agent_unavailable处理；正在同一持久夹具通过真实Retry和用户插话恢复，不将重跑计为无干预首轮通过。


PR101已于2026-10-02T02:39:46Z合入c104ee0f。CI36956003447 macOS/Linux均SUCCESS；CI临时merge2ed69f56与交付merge tree均11b14d6d，包含PR100发布装配。原源码branch只含生产核验代码，不伪称其tree与集成merge一致。两平台真实壳/设置/诊断及性能原预算通过，见 `evidence/rc-command-evidence-ci-20261002.json`。实际模型首轮与恢复仍单列，尚未Ready。
