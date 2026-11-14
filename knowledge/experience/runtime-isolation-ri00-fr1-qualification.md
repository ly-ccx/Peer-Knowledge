# RI-00：FR1 实现、唯一功能槽失败与恢复收据

创建时间：2026-11-14
最后更新：2026-11-14
状态：唯一一次功能验证失败；现场未准入；RI-00 和产品重构门保持关闭。

## 结论与授权范围

按用户授权实现 FR1 记录器、触发控制器、同候选绑定与现场入口，在干净候选 `39636570358c1d65316176ac1fdb26fb6a055156` 上完成 20 项单元/接缝检查及唯一一个 owned Electron 功能槽。该槽在第一根记录业务查询后因 **2.253846ms 保守自计成本超过原 2ms 门**停止，正式报告 passed=false、CLI exit1。不是通过，不进入现场，不新增进程或重跑资格；原候选和原始失败不改写。

[启动前绑定](../../playbook/evidence/runtime-isolation-ri00-fr1-qualification-intake-20261114.json)、[结果与原件 SHA](../../playbook/evidence/runtime-isolation-ri00-fr1-qualification-results-20261114.json)、[原冻结方案](../../playbook/evidence/runtime-isolation-ri00-field-first-witness-plan-20261114.json)。原方案的 proposal/runnable=false 描述保留为设计时状态；用户后续授权实现和一次功能槽，现场执行仍以该槽通过为条件，本次条件未满足。

C 级诊断改动；沿用 ADR96 Accepted、ADR128 Proposed，不移动产品职责、权限、数据或执行权。现有 Peer 本轮未附着、未重启，零主动业务查询、零参照；只有 OS 进程存活检查和安装字节的离线核对。以下 owned 查询属于单独功能预算，不能称为现场自然慢化。

## 模块实现和实际验证边界

实现位于代码仓 `apps/desktop/scripts/ri00/fr1-*.mjs`，入口为 `qualify-fr1.mjs`、`bind-fr1.mjs`、`run-fr1.mjs`。复用原 owned 宿主的 EOF/退出契约，仅增加可选诊断 entrypoint；没有改产品查询实现。

| 模块 | 职责、事实与依赖 | 本次证据边界 |
| --- | --- | --- |
| recorder / install | 包装已注册 handler、Application、Directory、Supervisor 和 Store 既有端口；ALS 父 ID、当时同步栈、root/12 遍 CPU、查询图和源代次归记录器持有 | 一根生产查询图、12 遍、输出与父链核对；非现场证据；后续覆盖未验证 |
| policy / controller | 独占触发/前史/后续自然根/采样阶段与预算；没有发业务查询的控制接口 | 固定九根、首候选、阶段/停止的单元检查通过；完整真实 Electron 控制器取消场景未到达 |
| journal / transport / session | 不变批次单槽，先持久化再 ACK；精确序号和 hash 链；控制器统一恢复原 owner、绑定与未确认记录 | 本次两批 23 条无序号缺口且全 ACK；注入 fsync/未知 ACK 的 Electron 场景未到达 |
| identity / binder | 源码候选、编译产物、输入 manifest 与功能收据绑定；拒绝未通过的资格收据 | 同候选源码与输入/生产产物前后核对完成；实际 Peer 的最终产物/对象准入绑定未执行 |
| profiler / analysis / native sampler | 单次自然入口 profile、时钟区间及停止；外部堵塞时仅控制自有采样子进程组，禁止杀 Peer | 模拟接口检查通过；真实 Electron start/stop、native 堵塞采样未到达，启动均为 0 |
| field runner / archive | 只读源副本与失效信号、随机端口发现、租约/有界预算/停止与清理统一装配 | 已实现，未执行；不以旧 M 或本次 owned 映射代替实际装配资格 |

源码与数据绑定通过的含义仅为本次测试和功能槽使用同一份代码、同一输入；不是实际 Peer 现场装配、低干扰或根因合格。[代码候选](https://github.com/ly-ccx/Peer-Agent/commit/39636570358c1d65316176ac1fdb26fb6a055156)保持不变。

## 唯一槽为什么失败

固定上限未变：1 槽、0 替换、最多 12 次功能业务读、读 CPU 8 秒、完整进程 CPU 12 秒、wall 60 秒。实际执行 2 次业务读：安装前 Supervisor 选择读取和安装后的首根 list-sessions；原 Promise 和原异常透明性检查通过，然后首根触发停止。其余 10 次计划读及场景未补跑。

| 首根诊断计费位置 | ms | 计量含义 |
| --- | ---: | --- |
| root 前元数据 | 0.220000 | 线程 CPU 自计小段 |
| root 后元数据 | 0.471000 | 线程 CPU 自计小段 |
| 12 遍 Evidence 元数据合计 | 1.334000 | 线程 CPU 自计小段；逐遍原数在收据中 |
| root 日志保留/序列化尾段 | 0.013000 | 线程 CPU 自计小段 |
| 3859 次 plan 计数/RLE 更新 | 0.215846 | performance 时钟 wall 上界，不能称精确 CPU |
| 保守混合计费合计 | **2.253846** | 超原 2ms 约 0.253846ms |

即使把 wall 上界单列，已测线程 CPU 小段合计仍为 **2.038000ms**；所以不是只因把 wall 算入才越过 2ms。12 遍元数据的计费最多，但其内部 captureStack、字典/记录更新等没有进一步独立计时，不能把 1.334ms 全指给某个函数。首次查询只有一个样本，无法确认首调用/JIT/分配等对成本形成的作用；不以假设补齐，也未设计或执行新对照。

这些小段不是 OFF/ON 的净新增 CPU，不包含所有间接 VM 效应，且根 CPU 本身包含内联记录器工作。保守自计通过也不能证明 VM 中立；本次更没有通过。不能将已知观察器开销或本根约 447ms 替代现场剩余 30–40ms 的归因。

首根 user=411.761ms、kernel=35.583ms、total=447.344ms；Evidence user=282.181ms、kernel=5.120ms；余部 user=129.580ms、kernel=30.463ms。12 遍各 69266 行、3859 plan 调用、23 会话及完整输出 SHA 与冻结输入一致。只是功能数据身份与位置算术，不是性能反事实或快态。

## 原件、完整性和恢复

原始报告、journal、退出状态和完整返回成本已保留，离线审计不重写它们。两段 hash 链重放得到 23 条连续记录：1 安装、7 栈字典、4 入口开始/同步前缀/结束、1 root 开始/完成、1 停止。真实业务父链 transport-listSessions→ipc-listSessions→root 及全部 Evidence 栈引用存在且未截断；两个人工透明性检查入口本就标 chainIncomplete，不能替它们宣称映射完整。无 GC 记录不能排除 GC；这里的无缺口仅指已记录的序列，不声称 VM 的全部事件或进程出生历史已保留。

退出实测：原 list/index/plan/batch/get 和注册 handlers 恢复、绑定恢复、lastAckSeq=lastSeq=23、未确认字节 0、pending=false、in-flight=0、activeRoot=null、lost=0、metadataErrors=0。owned 正常 exit0、专用 Inspector 连接拒绝；读取失败和源写入拒绝次数均为 0，三个 heap getter、Profiler 与 native 调用均为 0。8534 内容文件和 1 个空 fence 与原 manifest 内容一致，生产编译模块身份未变。

这证明了本次**超门失败路径**的停止和退出恢复。正常停止、租约失联、堵塞 watchdog、真实 Profiler 异常恢复以及完整控制器恢复均未到达；20 项单元检查不能替这些真实宿主场景打勾。原件未丢不等于现场资格完成。

## 成本账本与下一步边界

最终同候选单元/数据检查 CPU 1125.468ms、完整返回 wall 1950.140584ms，20/20 通过。开发期首轮另有一次 coverage 与 deadline fixture 混用导致的失败，原日志保留；仅把 deadline fixture 改为已覆盖的输入，不改生产门。后续开发检查通过不抹除原失败。

唯一功能槽读 CPU **2462.825ms**，含等待 Node/Electron/helper 全子树 user=3065.394ms、kernel=602.490ms、合计 **3667.884ms**，完整返回 wall **3085.534583ms**；CLI 内 wall=2969.330791ms 单列。离线审计 CPU user=404.690ms、kernel=439.386ms，wall=800.557458ms，新增宿主/业务查询 0。各功能槽成本上限可核对，不据此声称开发期所有读文件/命令具有完整 CPU 总账。

累计实际 owned 从 41 增至 **42**；产品读 CPU 已知下界从 635118.989ms 增至 **637581.814ms**，另有旧 C 未知成本保持。不能把完整子树成本重复加进产品读 CPU。源码 CI 查询无 workflow/status，不称绿色 CI；没有产品 build、release 或安装。

本次失败后停止：不执行实际 Peer binder、不进入 30 分钟现场、不补资格进程、不放宽 2ms/15ms 门、不把剩余额度当自动续跑许可。已经实现的记录入口仍不具备现场通过收据。原 3.95 秒证据缺口、现场同进程快到慢及剩余 30–40ms 机制仍未获得新证据；机制复现额度仍 0，RI-00 不闭合、不重构。后续若修改记录器，须作为新候选和新的明确验证范围审阅，不冒用本次已耗尽的槽。
