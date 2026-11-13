# RI-00 E3-P：专用时钟、Profiler恢复与等工作量对照

2026-11-14，执行前补充。ADR pass：00-adr-map、Accepted 96-task-execution-responsiveness、Proposed 128-local-runtime-isolation-and-bounded-query-contract。C级独立诊断，不改变产品Module/权限/Evidence/System Context或存储边界；不实施重构。P预算原文件/SHA、3 Electron槽、144根上限、原15ms/2ms门不变。

## 专用Module和验收顺序

- Marker Adapter仅在owned实验显式启用，单槽queue只增两个固定枚举clock-start/end，不接收表达式。两具名同步函数包住原生产Supervisor读，所有mode调用多重集相同；每个边界保存hr-before/performance/hr-after三戳，root业务时间保持原口径，新增metadata完整计费并纳入字节帽。
- Clock Mapper以profile原始timeDeltas与具名函数全部子树样本，分别约束profile→hrtime、profile→performance，再用每个三戳约束hrtime→performance。区间不相交、宽>2ms、缺失marker/父链一律拒绝；不借相同原点假设或放宽旧分析器门。
- Profiler Controller只拥有一次enable/setInterval(1000)/start/read-block/stop/disable生命周期。start应答未知只stop/disable，不重发start或业务读取；stop/disable/save任一失败保留原错误、partial或unknown profile及成本，不能发放结构或计时资格。save在disable后，读取错误优先保留；命令、状态、setup/stop成本及原异常均归档。
- P Result区别OFF入场、结构、计时和机制。八个dense点仍由原兼容summarizer判定；输入/图/PMC/metadata/校准同原门。OFF入场失败即结束该target；有ON时仍保留每遍、完整父链/未解析Native与GC/idle/program份额，逐遍至少10个确定样本才可比较。结构通过不代表开销≤2ms，也不能回填现场原因。

## P0先决资格（不是追加性能槽）

[独立P0机器预算](../../playbook/evidence/runtime-isolation-ri00-e3-p0-budget-20261114.json)：固定一个Node Inspector子进程、零Electron、无产品数据、无替换；90秒、fixture读体CPU8秒、控制器10秒、输出32MiB/profile16MiB，最多6次Profiler start与9个有限SHA读取fixture根。正常→start应答丢失→读体失败→stop应答丢失→stop派发前拒绝→恢复后正常六场景固定顺序，全部通过才运行P。丢应答由真实命令执行后在Adapter应答接缝注入，保留原失败，不冒称真实网络随机故障；SHA工作只验证工具与时钟，不代替现场残差。stop派发前拒绝后必须以真实disable及Profiler已禁用响应确认恢复，不重试未知start；最后正常profile验证后续准入。单元测试另外覆盖已知拒绝、save/disable失败和未知帧分类。

P0通过后按[原P冻结预算](../../playbook/evidence/runtime-isolation-ri00-e3-p-budget-20261113.json)一次固定3宿主对照；P自身任一失败不新增宿主。P0与P报告绑定独立producer/预算SHA，未通过不追补；实际Peer本轮不附着/重启。
