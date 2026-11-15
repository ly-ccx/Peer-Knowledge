# ADR 106：结构化只读 Git 与委派能力准入

创建时间：2026-10-23
最后更新：2026-10-24
状态：Accepted（用户明确授权先更新 ADR，再实现和审阅；测试及运行验收留到发布前）
级别：A（能力暴露、任务契约与 Evidence），B（委派准入与错误恢复）
依赖：ADR 15、16、35、49、80、91、92、101、103、104

## 问题与事实

只读双仓核验要求 origin、分支、HEAD 及未提交/未跟踪工作树事实，但只读工作者投影没有 shell。主 Bot 后来以 bash 读取已保存的任务清单，遭到 `project_agent_capability_denied`；该调用没有运行 Git。这是能力准入差异，不是系统终端、Git 可执行文件或用户授权发生故障。

ADR80 的主 Bot 只读与调度、ADR101 的 Full 不覆盖角色闸继续成立。问题在于缺少结构化仓库读取能力，委派前没有比较所需能力和实际投影，以及技术缺口被转成用户裁减验收范围的选择。

## 决策

### 1. GitRead Module

Interface 为 `local.git.query` / `git_query({path, operation?, limit?})`：operation 仅 `snapshot`（默认）、`status`、`log`；limit 限制返回条数。snapshot 返回仓库真实根、origin、分支（detached 为 null）、完整 HEAD、最近提交、工作树修改与未跟踪数量/条目。未初始化 HEAD、非仓库、缺 Git、访问拒绝、超时、取消、输出上限及采样期间漂移分别报告。输出被截断不能推导为干净或完整；多条读取是带起止时间的观察窗口，不冒充原子快照。

不递归进入 submodule；返回 submoduleCount 与 submodulesInspected=false。有未检查的 submodule 且顶层未发现改动、或采样漂移时，clean 为 null，不声称整个仓库干净。Git 的有效配置文件来源也经 realpath 和读取授权；外部 clean/process filter 禁用时返回 filtersDisabled=true，clean 为 null，状态计数仅描述受限观察，不冒充执行过滤器后的最终状态。consistent 仅比较窗口两端的 HEAD/分支及顶层状态记录，不证明期间文件内容从未变化。

Implementation 位于 runtime-node，由 Desktop 与 TUI 的既有 Provider Registry 装配。直接以固定 executable/argv 运行 Git，不启动 shell，不接收任意命令、环境、config、revision 或 Git 参数。不运行 fetch/pull/push/checkout/reset/commit/stash/build/test，不递归访问 submodule。进程禁止继承 GIT_* 配置注入，禁用 optional locks、fsmonitor、pager、hooks、自动维护、外部 diff/textconv 与 lazy fetch；有超时、输出上限和 AbortSignal。

路径先 realpath，再沿既有本地读取授权处理工作区外访问；Git 解析出的顶层目录与 git/common directory 也须在读取授权范围内，否则授权后才能继续读取。调用前、异步等待后、返回前重检宿主权限/当前性。不扩大任意 Shell 的角色白名单。主 Bot、只读 Worker、Explorer、Verifier 可得到该结构化读取能力；Probe/Automation 的既有约束不变。

所有动作仍为 Provider → Manifest → Runtime Projection → Tool Call → PermissionGrant → Evidence。成功事实包含调用身份、观察时间、查询种类、仓库身份、完整性与漂移标记；大结果进入既有 tool artifact 路径，预览不替代完整证据。失败/拒绝/取消沿相同 Evidence 链，不改写旧记录。

### 2. DelegationCapabilityAdmission Module

输入为任务 readOnly、成功标准及显式 requiredCapabilities；宿主从目标工作者的实际 Runtime Projection 取得当前可用 capabilityIds。模型只能声明需求，不能提交“已具备”的能力名单或授予权限。命令/test 标准必需 shell，文件标准必需文件读取；Git 状态/身份需求经 requiredCapabilities 明确声明结构化 Git。显式需求与宿主按结构化 kind 推导的需求取并集，不能用少报需求绕过标准的硬要求。不从描述中的关键词推断能力，以免将“不做 git status”等排除条件误作执行要求。

新工具 schema 要求声明任务 requiredCapabilities；旧持久化任务不迁移、不补造准入事实。旧内部调用的缺省需求可从结构化成功标准推导，无法确定的自然语言不宣称预检全覆盖。准入不替代运行时授权，也不保证未来进程、凭证、网络或文件持续可用。

成功准入只在新 Plan 保存所需能力、工具清单指纹、已知/声明标记和检查时间，不把完整工具清单反复复制进任务日志。完整可用清单仅在缺项诊断返回，沿既有大工具结果材料化路径保存。

2026-10-24 合并补修：GoalPlan 的归一化与重载必须保留上述 `delegationOrigin.capabilityAdmission` 白名单字段（required、inventoryHash、inventoryKnown、requirementsDeclared、checkedAt），不能在保存时丢弃成功准入记录。无效记录舍弃，旧任务仍不补造记录；该快照只描述建立任务时的能力清单观察，不授予 PermissionGrant，也不免除实际执行时的投影与权限检查。

检查位于新建子会话、GoalPlan、排队/隔离准备与替换旧任务之前。不匹配返回 `delegation_capability_unavailable` 或 `delegation_capability_unknown`，附 required/available/missing、criterionIds、stage=delegation_admission、retryable=false、userActionRequired=false。没有必要副作用，不建半成品任务，不取消旧任务，不擅自升级 readOnly/Full，不自动重复派同一不可能任务。请求幂等重放仍返回既有任务，不倒查新规则来改写历史。

直接 spawn 与 coordinate_work 的 parallel/replace 共用准入函数。协调入口须在 store.decide（会变更 goalRevision/执行版本）之前检查；恢复尚未启动的 recorded 处置也在发出取消前检查。spawn 在真正建会话前再次核对，动态能力在预检后变化仍可能导致执行期受阻，不能承诺跨 Provider 配置事务。

Desktop/TUI 共用预检 Module；各宿主只适配自身真实投影。目标工具存在但具体 Git 不可运行属于执行期可用性错误，不能报成模型缺能力；具体权限拒绝和角色拒绝保持不同失败码。

### 3. 受阻与用户说明

结构化诊断分清 projection（未提供）、role（角色禁止）、permission（用户/策略拒绝）、execution（实际进程失败）。返回原始 reason、具体能力及可用替代工具。主 Bot 的 shell 角色拒绝提示使用 git_query 或既有文件/任务查询；不因为一个 shell 调用被拒就声称整个机器没有命令入口。

能力缺项是宿主技术受阻，不是待用户验收、重新授权或缩减范围。沿既有工具结果与会话事实保留，主 Bot 在现有目标内查询/纠正能力需求；只有真实权限、缺凭证、不可逆动作或产品决定才询问用户。不能用用户一句话把缺失 Evidence 改成通过。旧报告保留原时间，不能把旧 branch/HEAD/build 复述为当前检查。

## 兼容、范围与交付

- 无新 IPC、无第二个任务/证据库；不改写历史 Conversation、GoalPlan、Evidence。
- 不对进行中任务做批量暂停、恢复、重派、关闭、补签或权限变更；本次不安装、不重启应用。
- 只修改干净工作树内本需求文件，其他在制改动保留。
- 本轮实现与静态差异审阅；补充回归用例但不执行任何测试、构建、类型/架构检查或应用验收。提交时明确未运行，发布前运行最终合并候选全量门禁。

## 发布前必须验证

真实临时仓库（干净、暂存、未暂存、未跟踪、rename、特殊路径、detached、unborn、worktree/gitdir 外置）、凭证 URL 脱敏、配置/环境注入不执行、无仓库写入、取消/超时/大输出不伪造成功、跨根授权及权限版本失效；Desktop/TUI 投影和 Provider parity；命令标准不能委派只读任务、未知/缺失需求在创建前拒绝、幂等重放和替换不伤旧任务；Evidence 绑定与错误分层；旧数据恢复及运行实例连续性。

## 本轮实现与审阅记录

在 RC26 的干净工作树实现；未修改原工作区在制文件或真实应用任务数据。GitRead/Provider、工具定义和 Node Adapter 在 runtime-node；Desktop/TUI 仅装配，协议集中定义观察与准入事实。主 Bot/只读任务只新增 local.git.query，通用 shell 仍拒绝。

实施者自审覆盖：固定命令参数与配置过滤、跨根读取授权和版本重检、完整证据材料化、子模块/过滤器/漂移的未知语义、直接委派和协调替换前的准入顺序、历史幂等重放与成功标准字段保存。审阅中将协调预检移到版本变更/取消旧任务之前，并将成功准入存储改为工具清单指纹，避免重复保存完整清单。

新增及更新相关回归用例，但本轮未运行测试、构建、类型检查、架构/IPC 检查、真实 Git 功能试跑或应用验收；不是独立审查，不声称运行验证通过。上述发布门禁仍全部待执行。
