# RI-00：安装现场、调用链与失败基线

创建时间：2026-11-11
最后更新：2026-11-12
状态：已交付坏基线，RI-00门仍未闭合；只授权取证、诊断脚本与失败基线，不表示ADR128整体已接受或开始性能重构。

2026-11-12同进程续证：[现场转换、自然入口与原生分配标记配对](../knowledge/experience/runtime-isolation-ri00-thread-transition.md)、[逐点回执](evidence/runtime-isolation-ri00-thread-transition-20261112.json)。实际完整查询已有快→慢→快，直接自然查询的主线程指令与额外后台CPU已补到；3个自然窗口均有major/incremental与分配标记或写屏障栈，暖读后3点未采到这些栈。GC observer的零不再用于排除GC，原生样本数不换算成精确毫秒，不把全部残差写成暂停成本。启动恢复顶层链已找回，首次索引上层连接尚缺；用户已授权另一次启动，但须等明确安全退出通知。RI-00门不放宽，不开始RI-01或重构。

2026-11-12授权启动已执行：[现场顺序及计量自检](../knowledge/experience/runtime-isolation-ri00-startup-followup.md)、[回执](evidence/runtime-isolation-ri00-startup-20261112.json)。首次索引前已有2086次计划文件读；新进程密集夹测未出现旧正向残差，恢复项目页后自然轮询仍约500ms。细粒度计量ABBA开/关中位507.782/507.909ms，不能将主要成本归给探针。相同源宿主15秒节奏也复现约500ms完整读取；旧进程形成与启动顶层栈缺口保留，G2不自行放宽，重构未开始。此前“等待退出”的收据为历史阶段，当前应用已打开、采样探针与端口均按轮恢复关闭。

2026-11-12归一化续证：[CPU/堆/节奏对照](../knowledge/experience/runtime-isolation-ri00-normalization-cpu.md)、[逐点回执](evidence/runtime-isolation-ri00-normalization-20261112.json)。15秒节奏可重复增加CPU，完整幅度未稳定复验；同源三对新进程中，交换初始读取顺序可重复造成约22–26ms归一化CPU增量，是部分形成条件。尚未把该顺序绑定到实际启动，不能与不同窗口节奏差直接相加宣布约430/500ms闭合。自然0.5秒读点的主/后台CPU与堆状态已补采；tier/保护状态、代际与64样本对象大小未提供唯一原因。用户已授权安全退出后的一次启动采样，观察器已在隔离Electron验证；G2未通过，RI-01与重构不开始。

2026-11-12重开续证：[重开对照](../knowledge/experience/runtime-isolation-ri00-restart-control.md)、[回执](evidence/runtime-isolation-ri00-restart-20261112.json)。同文件宿主夹测、无CPU的自然6.57秒及全真实源只读基线已取得；旧Path额外成本消失，跨宿主归一化剩余成本仍待受控归因，G2未通过。该轮已启用探针均收尾关闭；后续启动采样安排以上方最新续证为准。

最新结果见[自然停顿续证](../knowledge/experience/runtime-isolation-ri00-natural-followup.md)及[续证回执](evidence/runtime-isolation-ri00-natural-20261112.json)，首轮[调查](../knowledge/experience/runtime-isolation-ri00-investigation.md)与[原回执](evidence/runtime-isolation-ri00-20261112.json)保留。已补到5.417秒自然同窗调用链和完整坏基线；长期main的Path/getPlan成本差额已定位，但慢化触发原因仍未证实，RI-01不得自动开始。

用户明确要求先查清3.95秒峰值和现场约500ms/隔离约190ms差值，拿到完整调用链和可复现基线，再推进整体方案。上游为[实施包](runtime-isolation-implementation.md)与[ADR128](../knowledge/decisions/128-local-runtime-isolation-and-bounded-query-contract.md)。

## 决策与范围

重新核对00-adr-map、`96-task-execution-responsiveness.md`、`98-large-history-execution-responsiveness.md`、`104-progressive-interaction-and-coordination-storage.md`、`112-runtime-module-and-loading-boundaries.md`、`121-desktop-session-windowing-contract.md`与128。本卡为诊断/脚本补强，保持原运行契约：不新增产品IPC、存储真源、工具、授权、Evidence或System Context边界。真实生产IPC owner/窗口校验只在隔离harness复用。

代码基线固定rc.41 `b05b7afbf26b43444635f77710397c3a658d6a0f`。诊断代码单独分支`codex/ri00-responsiveness-baseline`；原源码工作树、日用进程和个人任务不修改。私有历史只进0700隔离副本，无Provider/凭据/identity/活跃lease，不启动模型、工具或恢复执行。源码/包内生产Module哈希、输入manifest与冷暖状态绑定结果。

## 必须完成的核对

1. 找回原峰值的原始行、时间/来源；历史缺调用身份时保留缺口，不用数学吻合冒充原始因果栈。
2. 相同数据、Electron/Node、生产Module，逐个恢复真实宿主读依赖；按同一请求区分排队、准入、查询、Store/归一化、序列化、返回。保留inclusive/self时间，不能把嵌套耗时相加重复计数。
3. 安装现场短时CPU profile核对业务栈；单列Inspector启动/停止、探针和同步诊断writer开销，profile不作为无探针交互验收。调试通道此前关闭则结束后关闭，不重启日用应用。
4. 单查询、周期读取、真实IPC并发突发、冷/暖缓存各自复现；突发数量必须说明观测来源或明确为等价机制实验，不冒称用户当时实际发出了该数量请求。
5. 提供可重复脚本、去私有内容的源/数据指纹、原始时序和预期失败断言。当前坏基线必须失败；后续候选复用相同条件，不能只比较更快的单个函数。

跨进程四时间戳按原始值保存。Renderer时钟存在量化，时钟校准固定声明每项时间戳1ms误差界，并记录实际performance时钟步长；实测步长超过该界则该轮失败，不自动放宽。传输/排队只报告带该不确定度的估计，不能把负的亚毫秒估计裁成已证明零等待。单进程handler/主循环计时与原500ms门不因此改变。初轮出现无量化界时校准矛盾，必须保留失败并用确定性量化反例验证修正。

## 收口门

现场约500ms与隔离约190ms必须有受控变量对照和实际宿主栈；多秒峰值必须区分“原事件已归因”“同机制可复现”“仅数量/时间相关”。保留任何未解释差值与失败尝试。不能把不同窗口的最大值直接相减，不能用profile overhead、OS睡眠或用户操作作没有证据的解释。

2026-11-12用户明确允许原3.949秒无法追溯时登记证据缺口。G1按此处理：保留原行/缺失父调用与CPU栈，不再以补造历史细节为出口；替代要求是新的自然多秒现场及同源受控基线。此修订不降低差额门：当前约0.6秒main与约0.4秒完整宿主的差额虽定位到Node路径JS及getPlan，长期上下文为何慢化仍未证明，RI-00继续未闭合。原生交互/完整执行/发布门另列，不被短时fixture或自然空闲观察替代。

日常验证覆盖新增脚本/计量、生产只读seam与异常清理，不跑无关全仓发布门。持续输入/滚动、完整产品和发布验收保持后续门，RI-00不安装/发布、不修热点、不提前删除旧路径。RI-00门未闭合则不进入RI-01及整体重构。
