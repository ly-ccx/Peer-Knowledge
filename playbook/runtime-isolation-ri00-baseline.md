# RI-00：安装现场、调用链与失败基线

创建时间：2026-11-11
最后更新：2026-11-12
状态：已交付坏基线，RI-00门仍未闭合；只授权取证、诊断脚本与失败基线，不表示ADR128整体已接受或开始性能重构。

本轮结果见[调查与未闭合项](../knowledge/experience/runtime-isolation-ri00-investigation.md)及[机器回执](evidence/runtime-isolation-ri00-20261112.json)。原3949ms缺当时父调用/CPU栈，现场与副本仍有未受控差距；RI-01不得据本轮基线有效而自动开始。

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

日常验证覆盖新增脚本/计量、生产只读seam与异常清理，不跑无关全仓发布门。持续输入/滚动、完整产品和发布验收保持后续门，RI-00不安装/发布、不修热点、不提前删除旧路径。RI-00门未闭合则不进入RI-01及整体重构。
