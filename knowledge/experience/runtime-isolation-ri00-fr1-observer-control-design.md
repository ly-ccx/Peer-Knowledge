# RI-00 FR1：封存余部审计与 Electron 计量开关对照

创建时间：2026-11-14
最后更新：2026-11-14

本轮属于 C 级诊断。已读 ADR 图谱、ADR 96 与 ADR 128；不改变产品职责、接口或 Accepted 决策。原始失败与旧预算保留。先冻结本设计与机器预算，再实现和执行；不以工具通过代替产品机制证据。

## 封存数据能进一步证明什么

以 fffc0576 的原始 report、stages、history 为唯一事实来源，不改写原文件。离线重放已确认 27 个旧自计时窗口 CPU 合计 2.187ms，粗窗口覆盖 1.928ms。按原始整数微秒快照差分，不能用 wall 包络代替 CPU。

| 位置 | 余部 user / system / total µs | 粗窗口扣直接子窗口后的 user / system / total µs |
|---|---:|---:|
| root.pre | 5 / 2 / 7 | 45 / 12 / 57 |
| span.pre ×12 | 62 / 42 / 104 | 118 / 58 / 176 |
| span.post ×12 | 90 / 51 / 141 | 129 / 16 / 145 |
| root.post | 2 / 2 / 4 | 39 / 6 / 45 |
| root.keep | 1 / 2 / 3 | 5 / 0 / 5 |
| 合计 | 160 / 99 / 259 | 336 / 92 / 428 |

259µs 可按粗窗口前/后拆为 201/58µs（前 user124、system77；后 user36、system22）。428µs 的 103 段按第一子窗口之前、子窗口之间、最后子窗口之后、无子窗口拆为 58/167/58/145µs。

源码边界说明：`read` 的 native CPU 快照之后还有 `clocks.push`、返回对象；`begin` 还有 row 字段赋值、`open.push` 与 wall 读取；`end` 还有字段赋值、`open.pop`、`stages.push`。旧 CPU 点与新粗窗口点之间也有原始 `cpu()` 返回算术、span tail 算术、root 时间与计数更新。span.post 的 145µs 同时包含原始 evidence 对象/push 和新增 begin/end 工作。故上述每段都是**原始工作与新计量工作混合的 CPU 区间**；不是纯时钟、纯对象分配或原始簿记成本。55 个旧时钟和 242 个新增边界时钟在旧窗口内的 wall 上界仍分别为 0.268957/0.275997ms，不减出 CPU，也不回填历史 2.387123ms。

## 新实验的单变量与边界

只启动 **1 个私有真实 Electron 41.7.1**，不启 Inspector、Profiler 或采样器。只从封存只读副本调用一次生产 supervisor.list，保留返回对象于该宿主局部变量，核对 23 sessions、130581 字节和原 SHA；不把业务值传出宿主，不重复业务读取，不安装记录器。该实验专门测新增计量的反事实成本，**不是记录器资格验证，也不是现场复现**。

三个固定操作族依次执行，每族仅切换 `meter`：A=关闭新增分段计量；B=使用封存版本 `createFr1StageMeter`。外层 CPU/wall 采样、分支、循环、输入和输出验证相同。每族固定 8 格：ABBA、BAAB；没有预热、不删除首格、不补格、不换进程。相邻格之间仅一次 setImmediate，保存实际间隔。外层测量也有自己的成本，不宣称净操作 CPU。

1. **metadata-topology**：按封存 27 个旧窗口的事件顺序重放 121 个 stage begin/end 和 55 个旧 CPU clock 调用；源业务语句替为空。两边保留相同旧 API 调用与 previousValue 关系，B 增加原 meter 的边界时钟/记录。核对 121 stages、297 clocks、零 open/invalid。它只能识别该空载拓扑下新增计量的开关差，不能从 0.259/0.428ms 中按比例扣除。
2. **stack.capture**：同一调用位置、固定 32 层同步递归，13 次 `getCallSites(96,{sourceMap:false})`；A/B 均保存并在计量外核对当前完整返回向量相同、未达 96 帧。B 只增加 stack.capture begin/end。这里的调用链属于该诊断宿主，不能冒充历史或现场业务调用链。
3. **output.encoding**：对同一个生产返回对象执行原始 JSON.stringify → Buffer.from UTF8 → SHA256 各一次；B 只增加 output.json、output.utf8、hash.output begin/end。每格在计量后核对完整 JSON 字节与 SHA，禁止用合成文本或只核对长度。不得根据 Node 微基准改写算法。

每格结束立即保存原始 user/system/合计 CPU、wall、间隔和 B 的完整 meter 快照；两组分别计算 B 均值减 A 均值及 A 返回漂移，保留符号。CPU 差只描述同进程固定操作的配对对照，冷态/顺序差异和外层测量仍是限制。若两组方向不一致，或原始区间不一致，不宣称观察者影响已稳定量化；不以平均数调整门。

## 预算、停止与恢复

机器预算为 `playbook/evidence/runtime-isolation-ri00-fr1-observer-control-budget-20261114.json`。每格原始外层 CPU >2ms 或 wall >100ms、累计控制 CPU >50ms/wall >1000ms、身份/向量/拓扑不一致、计量异常、输出超帽、读预算超限、任一失败，立即停止后续所有格，只做清理。2ms 不加容差；CPU/wall 一致性检查的 4µs 量化误差不能加到门上。

完整子树 CPU≤8s、业务读 CPU≤6s、返回 wall≤30s（含3s清理）。23s 后不准入新操作；owned watchdog25s，进程组仅对自有子树28s TERM/30s KILL。Node 资格/绑定一次，CPU≤2.5s/wall≤20s，失败不进入 Electron；源码/数据检查前后绑定，原始结果和退出状态原样保留。关闭只读 host/guard，恢复诊断 getter 监视，核对生产输入未变。实际 Peer 零连接/业务查询/重启。

无论对照结果如何，都不授予记录器资格或现场准入。只有后续候选在完整生产根上通过原始 2ms 与恢复契约，才可申请/执行其已有范围内的现场阶段；产品卡顿仍要求现场同进程快到慢与机制复现。
