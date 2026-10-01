# RC-04 升级 / 降级矩阵实施边界

创建时间：2026-10-02
状态：Accepted；负责人已授权自主完成全部 RC，GA 仍须负责人全面测试后确认。

## 范围与顺序

B级测试：不改变持久化或权限契约，不改生产数据迁移；如自动化发现生产缺陷，先补相应合同与定向回归，再修复。可在隔离工作区从 RC03 实现提交准备；最终 PR/合入必须同步已合入的 RC01–03 开发线并完整复验。

允许路径：`scripts/rc-upgrade-matrix.mjs` 与测试、必要只读标签源码提取 helper；根 package.json 与 CI 的实际矩阵调用。现有迁移、项目注册、档案/记忆/目标、恢复、更新器模块只作为实际测试对象；必要的既有测试夹具可复用。main.mjs 净增 0。

## 证据要求

- 从 `v0.0.18` 的真实 settings-store、conversation-store、workspace-application-service 源码产生及读取临时目录；用 git show 读取文件，依赖也从同一标签取出。不能用当前实现冒充旧版读取器。
- 真实 beta.1–5 标签迁移实现各自运行；0.0.18 到各 beta、逐版迁移、降级再升级的稳定 ID、完整旧会话和文件校验和，均有明确断言。
- 旧版会话、Goal、自动化与远程设置，升级后机器人与任务会话，档案/记忆/目标均纳入保存与读取检查。重启恢复沿当前真实恢复器进行，不以状态字段读到代替任务恢复。
- 备份失败保持原始数据，迁移幂等；beta 到 GA 更新器毕业仅作契约测试，不发布 GA。旧 TUI 不理解租约的兼容限制写入发布说明。
- 全矩阵进入 CI。数据模块测试与真实安装包启动证据分别说明；测试标签依赖的转译/装配只能改变模块定位，不能改旧源码行为。

全部在临时数据根执行。不能读写负责人真实 `~/.peer-agent`；失败记录保留，不新增 skip 或放宽验收。


## 实测与退出证据

实现c1d8c0be；同步RC03/RC01后干净d2708024。完整本机build/typecheck/architecture/test通过，矩阵19项全部通过，源码依赖均记录不可变commit和原文件SHA256。两平台CI36913659093完整门禁与包含无障碍/诊断的真实窗口均SUCCESS。代码PR96依赖PR94/95合入后仍须同步开发线；未提前宣布依赖卡完成。

初始夹具错误与校正保留：根script不能直接解析workspace包名，改用当前已build dist相对入口；automationId误取id与task误用role修正为实际公开字段；旧workspace adapter必须提供getDefaultWorkspacePath。共享catalog在合法新建会话/任务后会追加，原错误hash断言不能要求catalog仍字节不变，改为严格检查原记录前缀、原实体文件逐字节hash及旧实体仍可完整读取；plans/.changes.jsonl同样校验前缀。原会话/Goal/自动化本体、档案/记忆/目标保护未放宽，19条未删、超时未延长、无skip。第二至四轮失败与第五轮通过、最终干净报告均保存evidence。

四个逐版升级间隙使用真实owned进程SIGKILL停在持久task创建之后、reply提交之前，沿现有生产租约/恢复/GoalRunner重启，输入1、任务2（含原legacy Goal）、reply1，workerCalls1；再次重启waiting_user workerCalls0。模型为脚本，不代表真实认知；安装包测试另列。更新器whole module在受控stable feed执行，明确autoDownload=false且不调用download/install，不代表GA已发布。
