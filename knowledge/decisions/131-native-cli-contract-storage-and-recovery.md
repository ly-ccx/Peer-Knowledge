# ADR 131：原生 CLI 的跨语言契约、共享数据与恢复

创建时间：2026-11-14
最后更新：2026-11-18
状态：Accepted（2026-11-14 用户接受评审稿 118；正式编号 131；授权实施，不授权个人数据迁移、接管、安装或重启）
级别：A
依赖：[ADR 129](129-native-rust-cli-and-ratatui.md)、[ADR 130](130-bounded-cli-memory-and-transcript.md)

2026-11-18 NR-04 普通 Runtime 模式投影（B，实施前）：依 ADR35/65/76/106/129，隔离真实 TS Host 的工具数为 chat15、plan10、goal15、explorer5、compact0、system0；尚未迁移的 Goal/Skill/交互工具和 shell_stop 不能计入原生完成。补齐同一 ProviderRegistry 的 typed mode 投影和 capability allowlist 交集；现有 Goal 模型入口显式选择 goal，再叠加原 readonly 约束。无 mode 的 project() 保留全工具观察契约；实际模型发送使用明确 mode。

沿真实 isRuntimeToolAvailableInMode/createRuntimeProjection：缺失或空 modeScopes 仅在 chat/plan/goal 可见；explorer/compact/system/project_agent 需显式声明。保留原 scope，不由未知 scope 推导执行权。Shell 声明原 chat/goal 可见性，仍经同一实时 EffectAdmission。工具回读 Manifest 当前 goal-only 不借本卡扩大；普通大产物历史回读另列验收。实际筛选后的 Manifest 集合派生 projection hash，同一 immutable 投影限制 Provider prepare，不让工具名穿透 mode/allowlist。

先冻结真实 TS helper 与隔离 Host 向量，验证 Rust 投影及实际 prepare 拒绝、既有 Goal 模型/工具/Evidence 与 readonly 回归。本卡不新增权限、持久 schema、执行账本或 Bot Full 继承；普通会话身份/持久执行、Context、ACP 与完整 P4 继续开放。

## 1. 问题

### 2026-11-18 NR-04 原生 Hook 进程与原 Tool Call（A，运行时接线前）

依据 ADR16 的现行链路、35、76、116、129、130 与 [Hooks 规范](../specifications/hooks.md)。真实旧 TUI 的工作区 Hook 可在本地 Shell 原效果前拒绝并留下 Evidence；无 stdin 消费的快速退出旧例出现 EPIPE，见 [隔离回执](../../playbook/native-cli/evidence/p4-native-skill-runtime-20261118.json)。Hook 使用用户已有全局和当前工作区配置，依原次序合并；目录与文件版本必须可核。脚本由已选本地配置提供，模型只提供原已投影 Tool Call 的数据，不能指定 Hook 命令。保留显式配置的外部 Shell 接口，核心 Host 使用 Rust。子进程持有有界 stdin/stdout/stderr，只继承用于查找用户已配置命令与区域设置的最小环境。

Pre 在原 Tool Call 准备持久化后、Provider 授权前运行。Post 接收已观察的原 Provider 结果。Hook 选择和生效需同一实际 Host、配置版本、Tool Call、dispatch 与进程所有权。允许只表示继续原授权，询问归原审批，拒绝收紧原授权。原 TUI Shell 经过单次 SDK lifecycle 匹配，旧 Desktop 的额外 Shell 分类回调继续按既有宿主契约处理。配置选择不能由模型文本生成权限。只保留结构化的决策、退出、时长、原因和来源标识到原 Evidence；不把 Hook stdout 或 stderr 整段传给模型。

普通 Runtime 使用既有 canonical 执行句柄容纳子 Hook 命令，每个源进程绑定原 Tool Call 和 phase，保留独立状态。准备、准备启动、观察实际 child、真实 wait 与 process-group 缺失分别记账；不同 Hook 与 Provider 进程不得互相覆盖。启动缺口、未证明结束、已停止但未观察到真实结果必须保留。Hook 结束的事实由实际证据提供；回收进程不证明外部效果成功。源不再当前、取消、输出限额和超时通过原 Host 停稳。旧执行句柄保持兼容读取，未知新状态由保守恢复保全。

验收以实际原生入口为准，覆盖 Pre allow/ask/deny、Post 证据、普通与 ACP 的同一授权、早退出与 EPIPE、取消/超时和进程组、硬退出前后身份与未知保全。委派工作执行及旧安装宿主对照另取真实证据。纯配置与选择测试不构成此验收。

### 2026-11-18 NR-04 委派 Work Hook 登记与恢复（A，运行时接线前）

沿上节以及 ADR 16、35、116、129、130。旧 TUI 的委派工具经过同一 TUI Host 和 SDK Pre/Post；SDK 的 Hook ask 使用当前本机审批入口。已迁移的普通 Host 持有 ConversationExecution，委派 Host 的权威执行源是带工作区 lease、目标修订和预算登记的既有 Work。共享同一 Hook 配置、选择、命令、输入输出边界和结构化结果，执行记录归各自 Host 的 canonical 原 Tool Call。

委派 Host 在 Pre 运行前先为原投影调用登记预算与当前执行身份，关联该 dispatch 下各 Hook 独立进程和阶段。Pre 的允许继续原许可，询问进入原一次批准，拒绝形成原调用的未派发结果。权限等待和 Provider 实际派发前复核目标修订、工作区 lease、配置版本和当前策略。通过 Pre、取得许可、派发 Provider 分别留存事实。Post 接收已观察的 Provider 结果，已有 Provider 及其 Grant/Evidence 继续保全。无外部效果的运行状态必须由原 Host 的未派发事实证明。Hook 和 Provider 的进程身份、结束观察及 Evidence 分别持久化。

Rust 和 TS 对同一 Work pending / uncertain 原记录校验执行身份、Tool Call、dispatch、owner、Hook handle 和观察。旧 Work 记录继续可读。新增语义必须提高持久化读写最低版本，避免不了解 Hook 进程事实的旧宿主写入或收口。复制、预算转 uncertain、索引重建、历史修复和故障接管都须保全记录。原 owner 已证明死亡时，只能回收 positively identified Hook 进程组。启动缺口、未观察的 Hook 效果及已派发而无原结果的 Provider 继续未知。已观察的原事实经现行 Evidence 和停稳对账门禁收口。任何 Hook 命令或 Provider effect 均不因恢复而重放。

验收须经原生 `exec --plan`、真实工作区 lease、持久预算与 Evidence，覆盖来源替换、审批期间撤销、只读模式、取消、硬退出、失去启动身份和下一独立任务。用 TS 冷读、旧写入门禁及重建证明跨宿主保全。

### 2026-11-18 NR-04 委派 Hook 的已观察 Tool Result（A，落盘接线前）

沿上节的 Work/Hook 执行边界。登记原 Tool Call 时，Work 持久记录绑定会话内同一 Tool Call 消息身份和原参数摘要。以既有会话写入及 Work dispatch 为准，原参数只保存在原会话消息。原 Grant 在 Provider 实际派发前保存。原 Provider 的真实返回需要在 Post Hook 能启动前写入该同一调用。有界结构化 Tool Result 使用既有正文外置和原 Evidence 规则。Post 可补写 Hook 观察和停稳信息，不能变更原返回、Grant 或外置正文的对象身份。

恢复仅在原 Work owner 已证明终止且原消息、Work dispatch、工具参数身份和存储版本一致时补写。已观察结束的 Pre 且 Provider 未获准派发，可形成原调用未派发的收口。已有真实 Provider Result 时保留原结果，已观察 Hook 继续回填，未知的独立 Hook 仍保持未解，不能用原工具结果自动关闭其未知外部效果。缺失或冲突的锚点、启动身份缺口及缺少原 Provider Result 的已派发调用继续保守对账。恢复不重跑模型、Hook 或 Provider。

### 2026-11-18 NR-04 原生 Skill 准入和正文（A，运行时接线前）

依 ADR 16 的现行能力链、ADR 55、58、76、129、130。隔离旧入口证明工作区同名覆盖、禁用过滤和用户显式借用安装链接。旧在制原生入口连已禁用清单也整轮阻断，见 [基线](../../playbook/native-cli/evidence/p4-native-acp-v1-20261118.json)。共享的 Skill 目录、挂载 settings 和正文路径继续按 ADR58 读入；全局安装叶链接保留借用能力，工作区叶链接只准到同一实际工作区，目录根和 SKILL.md 不得以链接换代绕过检查。读取规模、YAML 深度和展开量须有界。无法验证的配置在发送或执行前显式失败。

Host 将实际挂载、模式与允许列表求交，投影既有 `skill__<id>` 和 `local.skill.<id>`。原有效安装 ID 作 canonical capability 后缀。遇到点号、非 ASCII 或过长 ID，wire alias 保持可追溯的有界 ASCII 和确定性摘要。CLI 允许列表可用 canonical ID 或实际 wire alias，碰撞在 Projection 校验时失败。L4 Source 只列真实投影中 Skill 的定位字段，描述仍由 Manifest 提供。正文经固定包体的读取能力和实际一次 Grant 获取，保持 Tool Result 的事实身份；旧输出的 system-reminder 字样不导入 System Context。Model 参数不选择本地路径，allowed-tools 只是包体元数据。每次认知和读取前验证挂载及选中包体的当前性。取消、挂载撤销或改链在读取前失败，已确认读回保留其实际 Evidence；不得从过时握手或文本补写授权。

大正文沿既有 immutable Tool Result 存储。普通会话在挂载 Skill 时可投影同会话的 `read_tool_result`，它仍经显式模式、允许列表及原一次授权。受委派的只读角色不增加 Skill 准入，Skill 不建立可执行脚本或新资产访问权。原 Hook、Plugin 和未迁移设置的已有阻断不归本切片放开。验收须包含真实模型 HTTP 的工具投影与选中正文、实时撤销和下一轮恢复、允许列表拒绝、持久 Grant/Result/Evidence 配对及大正文引用检索。

### 2026-11-18 NR-04 ACP 并发会话的 Store 当前性（A，实施前）

ADR 76 要求两个独立 ACP 会话可并发持有各自的 Runtime 和待批准请求。真实原生在制入口已复现两个不同会话因共享 index.jsonl 换代均返回 CONTEXT_SNAPSHOT_CHANGED，实际没有发送模型请求。见 [隔离反例](../../playbook/native-cli/evidence/p4-acp-conversation-source-baseline-20261118.json)。

将既有会话 HistorySnapshot 的逻辑 sourceRevision 明确绑定到目标会话的唯一完整 metadata 行和该会话实际正文、stream sidecar 版本。只改别的行不会中止该会话。目标行任何字段包括未知字段改变、同会话正文/sidecar 改变、身份重复或文件读取期间换代仍按原错误拒绝。仍有界检查整个索引的可读性、JSON 结构与真实文件代。单次 Store 事务另持有原 index→body 锁并核对整索引实际代。对整个索引发布的中途变化按原先失败/提交不确定处理。过时的调用者只允许凭本会话逻辑版本进入锁内取得新全索引，不能用旧全索引覆盖其它行。全索引目录/导出的原读指纹仍独立。局部修订本 ADR 普通 metadata publication 对“外来写入”的旧说明，目标会话的外来写入继续冲突。

原持久 schema、模型上下文/授权/Evidence/计费和恢复真源保持原合同。验收同时覆盖两个真实 ACP prompt 交错、取消后迟到允许未执行、同会话 CAS 与不同会话保全，以及现有 TS/原生持久往返。本卡不宣告完整 ACP 配置平价、旧安装宿主 drain 或 P4 总闸。

### 2026-11-18 NR-04 macOS 稳定进程起点与旧记录保全（A，实施前）

普通恢复的真实时区反例已固定：同一实际活 CLI 在 TZ=UTC 采集 `ps lstart`，恢复者用 TZ=Asia/Shanghai 观察，旧实现把同一 PID 判成 Reused 并关闭其准入；原根、实际 owner/child、stdout/记录变化和清理保留于 [反例回执](../../playbook/native-cli/evidence/p4-recorder-timezone-baseline-20261118.json)。这不是允许接管的进程死亡，不将全仓/原生门禁绿代替本反例验收。

收紧既有 boot/pid/start/host/acquiredAt 契约：macOS 新 recorder 的 pidStart 使用 OS 的 PROC_PIDTBSDINFO 起始 epoch 秒与微秒，编码为 `macos-v2:<seconds>:<microseconds>`；不使用日期格式、语言、TZ、进程命令名或裸 PID。通过固定版本 libproc 的安全 pidinfo/BSDInfo API 读取系统 libproc，检查 PID 匹配、seconds>0、microseconds<1000000；查询失败只能在实际 test_kill 确认 ESRCH 时判缺失，其余 Unproven。自有代码继续 forbid unsafe，FFI/绑定属于受审查依赖；固定 libproc=0.14.11（MIT，声明 MSRV1.72）并审查 BSDInfo 的零初始化/字段与 pidinfo 返回、bindgen 构建前提，Mac/Linux 实际构建另验。系统 boot 仍实际前后核对；Linux /proc start ticks 及原权限、Grant、Evidence、预算/stop/unknown 边界不动。

pidStart 在原五字段中是 opaque string，不新增或覆写持久 schema，不把旧记录就地升级。只有双方都是可解释的 macos-v2 数值起点才可按完全匹配判 Alive 或不同起点判 Reused；旧 `macos:<本地显示时间>` 或未知版本在 PID 仍存在时一律 Unproven，不因字符串不同判 Reused，也不据此杀 child、关闭活 owner 准入或产生新 stop。旧记录若实际 PID 已不存在，仍可据明确 ESRCH 与稳定 boot 判 Dead；换 boot 仍按原规则。旧 child 只有旧秒级显示身份、PID 仍存在而无法安全匹配时保持原 handle/process/unknown 和明确恢复阻断；不能删除记录、重放工具或用升级假造新精确身份。原 known usage 在原 owner 死亡/stop 已确证时仍可独立核对，blocked child 不消除费用。该条局部取代早期 Adapter 把不同 macOS lstart 文本视作 Reused 的实现解释，不扩大接管/杀进程权限。

旧原生二进制也属于兼容边界：只认识显示时间的旧 prove 实现可能把新 macos-v2 误判为 Reused，不能因旧 normalizer 能保全 opaque string 就宣称执行兼容。默认共享写域切换前必须完成旧原生与 TS/安装宿主的真实 drain/升级；已有项目 lease/owner 闸保留。本卡不操作运行中的旧实例，仅隔离根验证当前消费者和保守的旧记录读取，不声称旧二进制因本次字段前缀自动安全。

验收含实际跨进程 TZ/LC_ALL 变化时活 owner 拒绝且 canonical 不变、真实 child group 不被误杀、实际新 owner/child 崩溃恢复、旧真实已死 owner 原16费用一次与 unknown 保全、旧仍活 PID/未知起点保守拒绝、完整 Goal/MCP/普通恢复回归、TS opaque 互读和固定 featureless release 无 Node/Bun。`recover --session` 仍不重放/不接受 unknown；P4 总闸、旧 TS/安装宿主 guard/drain、P5–P7 与长期内存/默认安装发布继续开放。

实现期 B 复核（同日，修正前）：冻结718f 的完整原生门禁成功，但实际解压 featureless 包在 Git 快速子命令失败；21/22 不算产品接受。已用真实已退出未回收 child 在生产 process_recorder seam 确定性复现 None，原断言和现场见[红例](../../playbook/native-cli/evidence/p4-owned-child-zombie-baseline-20261118.json)。XNU 的 PROC_PIDTBSDINFO 在非零 arg 时才包含 zombie；固定 libproc 的同一 BSDInfo API 改用该查询选项，仍读取实际 PID/微秒起点，不退回显示时间、不补造身份、不延长执行/恢复时限。SZOMB 仅用于测试确认 readiness，不成为生产 ended/death/stop 证明；已拥有 Child 的实际 wait 与 group absent 规则不变。该修正不改五字段格式、权限、Evidence 或已登记恢复边界；需真实快速 child/原 Git/普通 Shell/MCP 与最终解压产物再次验证。

依据：[libproc pidinfo](https://docs.rs/libproc/0.14.11/libproc/proc_pid/fn.pidinfo.html)、[固定源码](https://github.com/andrewdavidmackenzie/libproc-rs)。此次先核对 Cargo 下载的0.14.11实际源码；不是只凭 latest 文档推断已验收。


### 2026-11-18 NR-04 普通会话恢复入口与排他恢复权（A，实施前）

在已接受的普通 execution v1 恢复边界上明确新增本地管理命令 `peer recover --session <conversation-id>`；原 `recover --plan` 保留。该入口不读 prompt、不初始化 TUI、不调用模型、Provider 工具或外部 MCP，也不向模型投影恢复能力。它只核对指定原 execution 的 canonical 事实、实际 OS 停稳和原用量提交；不补造 Goal/Work，不重放命令/网络请求；本次实施和自测仅使用隔离根，不修改个人数据或接管在用宿主。返回沿原 recover 的 `status=recovery_observed` / `facts` 形态，facts 为原 Protocol ConversationExecution；只有原 run 已 permits_new_run 才退出0，unknown 或停稳未证明仍输出真实观察并退出1，不能以命令运行过冒充恢复完成。

恢复者在原 conversations 目录 FD 取得非阻塞排他 flock，并核对实际命名目录的 device/inode；跨进程竞争只能有一名恢复者。FD 必须 CLOEXEC、由当前恢复任务持有，退出/进程死亡由 OS 释放；不新建持久锁文件、执行日志、权限真源或 runtimeExecution schema。它与原短期 index→body mkdir 锁分别负责“整个恢复生命周期排他”与“单次事实提交 CAS”，不能持 mkdir 锁跨 OS 等待或递归获取同一锁。正常调用仍使用原 owner token；恢复 Store 只暴露受排他 guard 约束的窄 token，不能反序列化、转成正常派发 token、观察新模型费用、prepare 或 dispatch。每次修改复核原 identity/owner/revision，目录替换或控制记录变化立即拒绝。旧 TS/安装宿主仍须独立参与 owner/guard 与 drain，目录 flock 不倒过来保护忽略本协议的实现。

没有已记录 stop 时，必须先以完整原 owner 的 boot/pid/start/host/acquiredAt 取得实际死亡/复用/换 boot 证明；活 owner 或查询失败不变成死亡，不向其发停止。存在 canonical stop 时可修复同一闭合汇总的账本，不重新制造 stop 或假定旧任务成功。原 cognition 只有在 owner 已死或原 stop 已证明 runner idle 后才可冻结；关闭准入、保留 dispatching 为 outcome_unknown，再结算已知费用。停止不证明的工具/连接仍阻断，费用回执不创造 stop。真实 OS 查询、停止与 Store 写入均保留实际 owner；截止或取消关闭后续恢复操作，已开始观察/清理不能靠 drop future 伪报完成。单次遍历沿 v1 的128个pending/handle上限，并设恢复控制截止；未完成部分留待原身份重复核对。

command 与 MCP stdio 沿既有受管 child 规则：not_started 只有在 owner 死亡后才可形成未启动观察；starting 无完整 child 的崩溃窗口保持 unproven；running 只针对完整同 boot/pid/start 且 PID=PGID 的原 child 定向停止，并实测 group absent。不同 owner、未知 handle 元数据、失败查询或缺失 stdio child 都保持原记录。网络 MCP 的本地 pump 可在 owner 已死后收口，远端工具效果继续 unknown。只有原完整 handle/process 全部得到实际本地结束证明，才能提交新 stop；不从“缺少 live registry”推断空闲。共享 OS 停止实现可由 Goal 与普通 adapter 复用，原 Goal lease/身份与预算闸不变。

恢复只承认原 message/stream/toolCall/capability/args digest 绑定的 canonical 结构化 Tool Result、原 Grant 与 Evidence。已有已确认结果可通过原 Evidence Store 补齐登记并沿原结算闸核对；不得由 assistant 文本、文件存在、工具产物片段或 summary 推导成功。prepared 且确证原 owner 死亡的未派发调用可记录真实 cancelled/not_dispatched，保留已有 Grant；尚无 Grant 时仅记录当前恢复 Host 的拒绝事实，不能签发执行许可。dispatching/unknown 没有已确认结果时不合成结果、不删除 pending、不因进程结束抹去未知效果。重复恢复不得重放工具、重复费用或在事实未变时改写 stop；后续独立会话使用新的真实准入。更进一步的未知效果范围核对/解除阻断仍需既有 Probe/Grant/Evidence 的具体证明，不能借本入口自动接受 unknown。

Store-only uncertain publication 须保全原身份和真实已拥有的 claim；恢复不得靠读取 JSON 重造正常执行权。原 mkdir 锁无 owner 来源时不能仅凭 execution owner 已死便删除：保持 lock_busy、未知锁和数据，给出具体阻碍及离线核对路径，不用测试中的孤锁维护替代生产证明。历史/模型外来修改只影响后续认知准入；清理与已观察事实仍可按同一原意图核对，不能覆盖外来 Grant 或 unknown。

验收：固定86fb2fa9的真实公开 exec→文件效果→exit88为红例，保留原根/二进制/请求与摘要；实际恢复须原效果不重放、known16一次入账、unknown仍阻断；已确认结果/未派发/终态费用窗口、真实 Shell/MCP child 与活 owner 拒绝、并发恢复者/恢复进程死亡释放、目录替换/记录CAS/未知 schema/starting窗口、取消/重复恢复与后续独立任务均须覆盖。真实 TS 互读、无 Node/Bun PATH 的固定 featureless 产物另验。该新增管理入口和恢复 guard 不取代 P4总闸、混合安装版本 drain、普通 unknown 全部核对或 P5–P7/长期内存/安装发布验收。

### 2026-11-18 NR-04 普通生产Host接线（B，实施前）

依ADR25/26/49/55/56/57/65/76/92/101/129–132，继续实现已登记的普通conversation/stream主体：进程内ExecutionRegistry与MCP credential epoch只接纳显式、已校验的Goal或Conversation身份，Goal的原key/解析/生命周期不变；不得构造假Goal复用控制、凭据或资源许可。普通主体复用同一受管attempt/handle、取消与真实drain，只有实际结束且已写入canonical停稳/结算后才可逐出进程内记录；重启缺少live token仍为unknown。

普通Host按原CLI的实际access状态和修订、模式/allowlist与当前会话主体签发真实Grant，通过既有ApprovalStore、Provider EffectAdmission、canonical消息及Evidence链执行。Full不绕过身份、当前性、清单或unknown；动态读取scope、command starting/running/ended和MCP未poll前登记沿原Provider契约。普通exec/Ratatui/ACP通过同一Host装配，无另一条文件/Shell执行器、loop或账本。Context迁移须以实际默认TS Source registry的有序section/hash为oracle，包含原core、agent策略、runtime、mode与MCP事实、project.instructions和continuity；不能用测试Source、worker规则或ad hoc系统字符串充当普通Source。尚未迁移的来源须保全并明确阻断，不能静默漏注入。

本次是已接受边界内的B级接线，不新增持久格式、Source类别或许可政策；原runtimeExecution、真实metadata回执和ADR25汇总不变。owner死亡/未知效果仍须完整OS与资源证明，不能以缺少进程内记录、计时或仅PID收口；未证明时保持原阻断。先在隔离根验证真实入口、计数/发送同请求、工具Grant/Evidence、撤权/取消/硬退出及原数据保全，TS生产guard、旧安装版本drain、P4总闸与P5–P7继续分别验收，不因入口存在宣告可默认替换。

接线前补充复核两项既有生命周期：MCP connection属于整个execution，已确认的单次Tool Result可在该连接仍存活时结算，连接必须保持完整原owner/registry/transport事实并在最终stop中真实drain，不能把任意未结束handle当成可忽略连接。已观察费用的结算与工具停稳分开：Host须先等待实际认知/模型观察完成、关闭新准入进入stopping，再以原最终汇总提交账本；工具或连接停稳失败不能抹去已知费用，usage回执也不能制造stop。cognition尚活跃时禁止冻结/提交汇总，未知工具和句柄仍阻断后续准入。

### 2026-11-18 NR-04 普通会话执行事实与已拥有metadata发布回执（A，实施前）

普通exec、Ratatui与ACP必须以实际Conversation/stream为主体复用同一原生loop、cognition和Provider链，不建立假Goal/Work、继承Bot Full或私有执行日志。扩展原Conversation index metadata的可选`runtimeExecution` v1（执行事实，不是权限）：实际`conversationId/streamId`、engine、完整owner Recorder（boot/pid/start/host/acquiredAt）、单调revision、active/stopping/stopped/recovery_required、原调用的pendingTools、已观察的runtime_turn用量/原稳定归因与usageCommitted、真实本地停稳观察。未知版本/身份/状态或损坏保全并阻断执行，不降为无owner；其它metadata未知字段保留。无该字段的旧会话可在真实新准入时建立，不重建历史身份或补造旧工具事实。

调用意图只存Host派发身份/真实capability/args digest/声明scope与可选受管handle/process；原完整args、Tool Result、PermissionGrant与Evidence仍在原canonical消息/索引，不从metadata生成成功或允许。prepared意图须持久化于效果之前；进入dispatching并确认真实Store提交后才允许poll/start Provider。崩溃后dispatching/未知保持unknown，不重放；prepared的未派发观察也须完整owner/版本与真实生命周期证明，不能只看时间或PID。普通受管进程复用原starting/running/ended/完整Recorder语义，但execution为显式conversation identity；既有Goal的SessionExecutionIdentity解析仍严格，不把普通身份混入Work预算或Goal claim。所有控制回复仍由实际普通Host校验当前owner/模式/参数/访问修订和原Grant，MCP凭据连续性不是授权。

同一会话只允许一个实际执行owner。新准入在原index→body目录锁内以实际source/contentRevision和原execution revision CAS；active、stopping、未知效果/句柄或未结用量不准覆盖。owner仍活着时不抢占；重新启动先读原记录，只有完整OS观察与实际owned资源结束证明才完成本地停稳，不以owner死亡推断文件/网络/MCP效果。unknown及原Grant/Evidence/产物保留，重复恢复不执行旧工具。停止metadata只投影Host真实停稳回执，不能由assistant文字或界面动作构造。source当前性失败时停止新派发，结算已观察事实；真实已退出的独立新会话不得受旧取消域污染。

ADR25的每stream一份runtime_turn累计/原ledger id不变：每个实际模型响应（含summary、重试和迟到用量）先更新相同run的canonical已知用量快照，终态/恢复经既有serialized usage Store提交/去重，再以实际Store回执CAS确认usageCommitted。记录失败不能补零、拆成伪物理请求turn或清旧unknown；无已观察用量不生成虚假费用。账本不用于Context restore。

该metadata写入会改变index source，新增Store签发、非Deserialize/不可由JSON制造的`ConversationMetadataPublication`：绑定原/新实际source、conversation/contentRevision及锁内已核对不变的正文/sidecar和上下文相关metadata。共享cognition只能在真实已拥有的纯execution metadata发布回执连续匹配原请求source时前移期待revision，随后仍与实际冷读source对照；任何正文、模式/模型、外来写入或不连续回执继续冲突。Host更新已知用量可在历史已变化时保全原stream事实，但不能给旧请求签发跨该变化的回执或继续认知。不得把source相等比较整体删除/改成仅revision。

当前TS/Native普通宿主须参与同一owner/互斥与guard；原Bot/Work仍走其既有lease/Goal，不新增第二套项目控制。旧已加载/已安装实现不会因未知字段自动安全：生产共享写入及默认切换必须先完成实际旧宿主drain/升级兼容闸，未证明者不宣告受保护；本卡只在隔离根和当前双端源码验证，不操作在用实例/个人任务。旧版本未知控制记录的诊断读取与保全不等于可执行兼容。

验收必须包括真实TS↔Rust读写/同会话跨进程竞争、外来内容/metadata CAS、未知schema/损坏保全、先存意图再真实Provider效果/Grant/Evidence、拒绝/撤权/取消/超时与实际资源结束、dispatch/结果/费用窗口硬退出、原unknown保全/不重放/已有状态恢复和后续独立新任务。生产普通exec与Ratatui/ACP入口、完整Context/协议/工具、旧宿主drain与P4总闸、P5–P7仍须分别接通验收；Store或类型测试不算日常CLI完成。


2026-11-18 NR-04 共享认知请求管线（B，实施前）：依ADR55/56/57/65/76/129，从Goal绑定的ContextPipeline提取同一原生计数、结果视图、容量持久化、压缩/重建和物理请求重试实现。公共Runtime内核只依赖显式Host seam：当前性/请求预算准入、注册Source组装、受管等待与已观察用量归属；不接收Goal/Work/Grant/ResourcePlan。Goal Adapter保留原lease/执行修订/Bot policy/MCP revision与credential epoch、budget请求计数和canonical用量快照/终态结算，ModelObservation仍在实际响应后、所有权/取消拒绝之前捕获。计数与发送复用同一prepared bytes，summary与每次重试分别计费，结果视图不得重跑工具；原source CAS、单次overflow恢复与8MiB/256KiB等预算不动。不新增Context Source或系统字符串，不启用普通会话或新持久执行格式；普通Host须提供自己的真实主体与pending/unknown，不能构造假Goal。本卡完整实际Goal Host回归与非Goal Host seam验证分别记录，P4总闸及日常CLI仍开放。

2026-11-18 NR-04 终态Store后的旧JSONL兼容证明修正（B，测试实现前）：fcfee全仓Linux Test及本机相同文件均在Interactive Results反馈测试的readJsonl→readJson源块digest失败；该块还包含writeJsonl，新增durable flush/目录同步改变源码而非消息序列化。保留原失败与8b3ffbcf冻结digest，不只替换expected。将该原版完整JSONL primitives逐字冻结为测试fixture，实际用旧reader/writer在隔离会话上重写已知附件，再由当前Store读取/更新/重开，验证全文、冻结版本、游标及重复inputId；同时保留其它原writer块检查并审查新durable块。此证明只覆盖这些旧primitives及已冻结的原队列，不冒充完整旧安装宿主并发/drain。依ADR118 §IUI-T29与本ADR既有共享数据契约，不改生产格式、授权、Evidence或兼容边界；普通Runtime/P4总闸仍开放。

2026-11-18 NR-04 共享回合循环（B，实施前）：依 ADR26/65/76/129，从现有Goal episode提取同一个原生turn loop；Host接口承接模型请求、已观察助手内容提交、单个真实工具调用及本轮continuation绑定。循环只拥有请求/内容/顺序调用/续行的次序、显式回合限制和取消传播，不签发Grant、不写Store、不判Goal验收。Goal adapter继续使用原Context/count/compaction、canonical预算、权限/资源/Recorder/Evidence和停稳/计费finally路径，不构造新Goal或另一套工具执行器。普通入口未传max-turns时无隐式有限上限；已有Goal候选显式限制与max_turns退出码保留。取消后不接受迟到请求结果或启动下个工具；失败不自动重试/重放。循环只持有当前model turn和本轮已提交工具id，不能累计整个会话。新普通会话主体/持久执行/ACP仍须单独接线；本步不算普通CLI发送或P4总闸完成。

2026-11-18 终态提交窗口复核（B，源前）：替换终态正文前，先确保同一 v1 provisional marker 已持久化并绑定真实目标消息；已有 marker 保留原预览，没有 marker 时使用空 patch，不提前注入未确认全文或工具结果。body/index/marker 后半段失败明确返回 uncertain，保留实际写入；恢复从新 source 核对原终态事实，完成 Store 提交，不重跑工具。TS streaming 写/清理使用原 index→body 锁，终态清理失败不能伪报成功。原生有界历史预算不扩大，大历史与旧安装版本 drain 另验；无新权限/执行日志，不等于普通 Runtime 已完成。

2026-11-18 普通会话终态 Store 接线（B，实施前）：依 ADR55/57/65/76/129/130 与本 ADR 的现有 JSONL/v1 streaming sidecar/锁/CAS 契约，迁移既有 patchStreamingMessage/commitStreamingMessage，不新增任务、权限或执行日志。Rust 接口用真实 HistorySnapshot 的 source identity/revision、明确 messageId 与 Host patch；禁止找不到目标时回退最后一条 assistant，不能改变消息身份。正文、metadata 和未知字段保全；patch 不是权限或 Tool Result 的来源，Host 仍只提交真实结果。

流式 patch 沿原 v1 文件，只影响展示 sidecar，不 bump contentRevision 或使其成为 committed history。终态沿原 index→body 目录锁，合并 canonical 原消息与 Host 的完整终态 patch（不把旧 sidecar 文本混为已确认结果），更新 index/revision/preview 并仅清同一 messageId 的 sidecar。TS 的公开 streaming patch/clear 同样参与原锁；内部已持锁的清理不重复加锁。Native 的稳定 source 校验拒绝中途变化、未知/损坏 sidecar、外来目标、非普通文件和超限；未迁移的大历史明确失败，不以本卡宣称 P6。

部分提交不能回滚或丢弃已保存的 Tool Result/Grant/Evidence。body/index/sidecar 清理后的未知均返回 commit-uncertain，保留可观察文件。恢复是重新读取实际 source、核对原目标及已经观察的完整终态 patch，再调用同一 Store CAS 完成元数据/sidecar；此操作不调用模型或工具、不补造成功。重复的已提交相同 patch 不再写入；外部变更必须重新准入，不接受旧 snapshot。恢复多 bump 的 revision 仅使派生视图失效，不重复消息、工具或计费。测试保留各阶段失败并验证未知字段、并发/孤锁、取消、实际 TS↔Rust 互读和恢复后追加新消息。此处不引入普通会话执行身份或恢复授权；后续 Host 接线和混合安装版本 drain 仍须分别验收。

2026-11-16 NR-04模型OAuth条件提交：按[ADR0001原生模型OAuth修订](0001-cross-platform-credential-vault.md)先登记Helper可协商快照/CAS，再实现原生token读取、刷新和模型传输；不增加能力或本地执行授权。配置元数据不能取代实际Vault token，迟到刷新不得复活删除或覆盖新一代。模型配置完整写入、登录回执和提示投影恢复未验证前仍属于P4余项。旧Helper特性缺失须在远端效果前拒绝，原子Vault提交与失败保全需真实跨进程验证。

同日补强：远端刷新前先以同一加密token的`peerModelRefresh`意图争取唯一刷新者，未知结果保留意图并阻止自动重放；完成仅CAS自己的意图代。完整新旧宿主须迁移同一seam并验证，旧预读token的宿主不因新增字段自动变安全。该连续性事实不改变本地能力授权或Evidence，未完成多宿主兼容不记P4总闸。

CLI 改用 Rust 后，Desktop 与公开 Runtime SDK 暂时仍使用 TS / JS。机械翻译类型不能保持权限 digest、System Context checksum、工具配对、sidecar、宿主租约、SQLite CAS 或完成门一致。新的二进制也不能因为启动成功就接管旧任务。

本 ADR 将 ADR 55 / 57 的共享 Implementation 约束扩展为跨语言 conformance；保留 ADR 0001、35、37、49、65、74、76、80–85、88、92、98、100、101 的事实、权限、存储和恢复边界。`104-bot-capability-visibility.md` 在最新实施 checkout 仍为 Proposed，不随技术迁移被接受；同号的 `104-progressive-interaction-and-coordination-storage.md` 已接受，其日志 / writer 屏障 / 恢复契约继续保留，二者不能混称。ADR 115 页头已 Accepted，按其既有准入 / 草稿边界迁移当前 CLI 可达功能，不能继续沿用初次旧 checkout 的 Proposed 判断。

## 2. 单一工程契约

1. `packages/protocol` 保持现有公共契约归属。新增语言无关的 contract resources 与 fixtures，供 Rust / TS 共同消费；不另建由 Rust 私自维护的第二份协议仓库。
2. 先以现有已治理 Interface 和测试冻结 v1 schema / fixtures，再生成或校验 Rust 类型与 TS 类型；无法自动提取的 TS 类型必须逐项审阅。schema 只管形状，顺序、权限、幂等、错误和恢复规则另以可执行 fixture 表达。
3. 生成产物可提交以支持 Cargo 独立构建，CI 重生成对比，禁止手工维护相同常量的两份副本。契约版本独立标识于产品版本，根 VERSION 仍统一发布列车。
4. 导入共享 Context Source 的资源正文、layer / trust / priority、稳定排序、hash 输入及 snapshot 规则。宿主只投影事实，不在 Rust encoder 临时添加身份、mode 或 Skill 提示。
5. 以 ADR 57 的同一 canonical history 规范实现 Rust projector；顺序、工具配对、不完整历史、附件和 compaction 边界一致，再经 provider encoder lowering。展示分页不能改变模型上下文准入。
6. 明确区分展示兼容和执行兼容：未知可选展示字段可保留，未知权限枚举、未知控制消息、未知 checkpoint / schema 或执行 policy version 必须拒绝准入；不能默认 allow / success。

## 3. 必须冻结的等价性

| 合同域 | 验证要求 |
|---|---|
| 工具 Manifest / schema / mode / role projection | 同一配置与事实得到同一可见工具面；未投影工具在执行入口仍拒绝 |
| Context Source 与 history | 相同输入得到相同 section 顺序、正文 / hash、canonical tool pairing、history fingerprint 和预算归属 |
| 权限 | 相同主体、capability、args、scope、policy revision 得到相同审批要求与拒绝；过期 / 降权 / 撤回后不能命中旧缓存 |
| 生命周期 | 同一事实序列得到同一等待、yield、失败、取消、核验、签收和送达结果 |
| Provider wire | 固定 clock / IDs 后，请求与 SSE 归一化等价；error、空回复、截断、tool args 碎片、reasoning replay、usage 与重试政策不漂移 |
| 命令 / 外部协议 | argv、stdin、stdout、stderr、退出码、JSONL 与 ACP 能力协商保持已发布行为 |

特别注意：当前 `permission-operation.mjs` 使用对象 key 排序 + JavaScript JSON 序列化 + SHA-256，不是可以随意替换的“任意 canonical JSON”。Rust 必须对齐 UTF-16 key 排序、UTF-8 编码、number 格式、null / 缺失、数组顺序和异常输入；安全整数范围与时间单位显式约束。不得只用 serde map 默认顺序重算旧批准。不能一致表示的参数失败关闭；若要更换 digest 算法，需另记版本化授权兼容决策，不能默认复用历史 grant。

conformance 采用可分享合成数据，固定不确定量；同时以不变量断言防止“旧实现有 bug 就永久复制”。发现原契约冲突先修订 ADR，不通过修改 expected 输出隐藏行为变化。

## 4. 共享数据而不大迁库

- 根目录仍为 `PEER_AGENT_HOME` → `PEER_USER_DATA_PATH` → 用户默认 `.peer-agent`。不建立原生 CLI 专用事实根；测试候选使用显式隔离根。
- 会话 / JSONL、streaming sidecar、contextSnapshot、contentRevision、GoalPlan、协调日志、输入队列、批准、Bot policy SQLite、记忆及 FTS、artifact / Evidence 引用维持现有格式和语义。正文与大对象不因 Rust 迁为 SQLite blob。
- 新增的 viewport / offset index 只能是可重建 cache，按 DATA_STORE_ENTRIES 登记 scope、schema、失效和回退；不得重写原会话或把索引当 Evidence。
- 未知字段保留，不能把旧开放对象反序列化为窄 struct 后覆盖写回。canonical 正文、toolCallId、grantId、Evidence ref、inputId、reply receipt 和任务身份保持；不能重建为新的“等价会话”。
- 原子临时文件、flush / fsync、rename、锁顺序、目录布局、SQLite transaction / CAS、busy / schema / corruption 错误均与现有 Store 对齐。Node / Bun / Rust 对同一 SQLite schema 和 FTS tokenizer 做交叉实测，不因 Rust 选择 rusqlite 就假定兼容。
- 凭证继续经 ADR 0001 Helper v1 请求，保留相同 app 身份与 OS 授权边界；配置只持非秘密元数据及引用。

## 5. 写入所有权与锁

项目任务继续用现有 `host.lease` / yield / holdsLease 规则；Rust 宿主仍声明 surface=`tui`，不新增一个绕过互斥的 surface。Native / Desktop 同时打开时只能一个项目执行所有者，其他入口只提交持久输入与读投影，不能双跑 Supervisor / Watch / Goal。

项目租约不能代替所有 Store 的写锁。例如会话 Store 已使用 `${file}.lock` 目录互斥，异步多锁获取失败会释放已持有锁，再等待重试；原生实现必须参与同一锁命名和获取顺序，不能自行换为旧版不识别的 advisory lock。跨进程 stale revision、sidecar merge 与索引更新需分别测试。

当前目录锁无 owner 元数据，崩溃残留无法仅凭 TTL 或“没有租约”证明安全删除。原生首版对此失败关闭，报告具体锁与受阻写入；支持的恢复路径是离线维护：确认该数据根所有写入宿主已退出、保全锁及相关文件的诊断副本，再通过显式受控维护清理已核实的孤锁并重试原事务。无法确认所有权时不清锁、不重放，保留阻断。此方案不在本次文档阶段执行；若要自动回收，须先给新旧宿主统一补 owner / fencing 契约并评审。

对其他 Store，P0/P2 必须逐项登记已有互斥 / CAS / append 保证。发现竞态时按 Store seam 双端修复并记录接受条款，不能把“相同 JSON 格式”或“都用 Rust”当并发正确性的证明。未经证明的共享写域不开放生产写入。

## 6. 旧任务与中断恢复

恢复先读事实，再决定是否能继续。顺序：数据 / schema → 项目身份 → 当前所有者 / lease → 输入和回复幂等 → 未结算工具 / Evidence → policy / approval revision → checkpoint / provider compatibility → 原有调度和核验策略。

| 已有状态 | 原生候选的处理 |
|---|---|
| 完成 / 已送达 | 原样读取，不能再次执行、核验、签收或发送重复回复 |
| 输入已入队、尚未确认显示 / 回复 | 用原 inputId / receipt 继续观察与消费，不生成新输入 |
| 旧 Host 仍持租约 | 客户端读取 / 提交，不抢占；接管只走现有显式移交流程 |
| 待审批 / stale approval | 展示原记录；按既有具体操作、主体、期限、revision 重新核对；不自动继承未知允许 |
| 运行中崩溃、未知工具效果 | 保留 ToolCall 与未知效果；先结算 / 对账，不能按“Rust 首次启动”盲目重跑 |
| 已有有效 checkpoint | 仅当版本、模型 wire、历史 fingerprint、lease、权限及原恢复闸全部兼容才续接 |
| 未知 / 不兼容 checkpoint | 可读诊断；继续由兼容旧引擎恢复，或在明确新执行尝试中沿原系统支持的重试政策处理；不能丢掉后从头自动执行 |
| 中断的 sidecar / 部分提交 / 不完整尾行 | 按原 Store 恢复语义保全已确认记录；隔离坏尾、拒绝无法证明的提交，不制造完成 |
| policy 损坏 / SQLite 未知 schema / 磁盘满 | 结构化拒绝，保留旧库及诊断；不得重建为空库后回退 Full |
| 已取消 / 暂停 / 取代、晚到结果 | 严格校验 execution identity / revision / lease；保留合法事实，不重新激活旧任务或写入新会话 |

所有恢复用故障注入、独立数据副本与真实 Store 验证；恢复后必须再接收一个新任务，证明所有权、队列和取消域没有卡住。不能通过删用户数据制造成功。

## 7. 发布与回退

1. 迁移期保留两份可执行候选，但一次会话只选一个执行引擎。没有运行中热切引擎或自动双写。
2. 切换前完成 TS→Rust→TS 的配置、会话、权限、任务和 Evidence 往返；旧版本无法读取的新事实不得进入默认共享写域。
3. 回退保留数据和审计，只在执行已 drain 或已明确结算未知效果后释放所有权；旧版重新获取并按其支持的 checkpoint 恢复。不兼容任务维持阻断，不清历史后重跑。
4. 新版和旧版的不兼容信息须能被 doctor / 启动检查说明。不能只增加一个旧版完全不识别的 manifest 就声称有兼容保护。
5. CLI 平台归档仍包含 `peer` + `peer-credential-helper`，先保留当前正式构建的 darwin-arm64 / linux-x64。其他平台须独立通过构建、终端、Helper 和安装验收后才能宣告支持。
6. 原生二进制默认切换前需完整 release gate；包括所有开放 PR 合入、最终合并候选全仓测试及产品回归、逐图审查、再次核对 PR 清单、公开产物与安装器验证。不得在本次方案阶段安装、重启或发布。

## 8. 协议 SDK 的兼容注意

MCP 首选官方 Rust SDK `rmcp`，但其当前 upstream 明确不提供 legacy HTTP+SSE，而现有 Peer `mcp-client.mjs` 提供 `SSEClientTransport`。必须实现受控 legacy Adapter 或选定仍支持的安全版本并审查维护成本；不允许静默把已有 `sse` 配置当作 Streamable HTTP。任何移除 / 代理部署方案均需独立产品接受，不能作为迁移的隐性前提。[官方 MCP Rust SDK](https://github.com/modelcontextprotocol/rust-sdk#transports)

ACP 使用官方 Rust SDK 的稳定协议入口，对齐现有 TS SDK 的已实现能力，不因换库默认开启 draft v2、新客户端工具、登录或恢复能力。[官方 ACP Rust SDK](https://github.com/agentclientprotocol/rust-sdk)

## 9. 验收

- 对同一 fixture 运行 TS / Rust 的 projection、Context、digest、错误与 reducer，输出逐字段对比。
- 真实双子进程竞争租约、文件锁、SQLite CAS、输入幂等、late approval、sidecar commit；故障点含写前、写中、rename 后、回执前与退出中。
- 断连 / 超时 / 拒绝 / 取消后无未授权执行；重启后不重放未知效果；恢复阻断必须给出具体对象与可用路径。
- `exec` JSON / 退出码、ACP stdio、公开 SDK smoke 和 Desktop 原合同保持；候选绑定 commit、构建 hash、fixtures / schema hash 与平台。
- 本文当前只有方案与静态审阅，不表示上述验证已运行。

## 修订记录

- 2026-11-14：新增跨语言单一契约、兼容数据与锁、旧状态恢复、原生发布和回退提案；未改权限档位、数据真源或当前已接受 ADR。

## 接受与编号校正（2026-11-14）

同日措辞澄清：§1 将同号 ADR 104 区分为文件名。未接受的是能力可见性提案；已接受的 progressive storage / writer fence 决策未被撤销。此为消除引用歧义，不变更既有存储 / 权限 / 恢复边界。

用户明确接受三份原生 CLI 迁移 ADR 并要求先完成 P0/P1、自测后持续推进，最终无 Bun/Node sidecar。评审稿来自落后的知识 checkout，误用主线已有编号；核对全部 origin 分支后，将原 116 / 117 / 118 按同一内容分别登记为 129 / 130 / 131。既有同号其他 ADR 未被覆盖。接受不等于实现、性能、恢复或发布验收。

### 最新主线约束复核

已补读 ADR 112、既有 116（session-control-and-resource-settlement）、120、122、124 与 127 的相关条款。ADR 127 页头为 Accepted，即使 map 的摘要仍写未接受也以文件原文为准；不能将旧稿的保守阻断描述解读为撤销当前受控对账 / claim 收口策略。恢复、停止回执、unknown 不重放与原执行政策均按这些已接受条款迁移。

### NR-03 原生 attempt 的停稳观测补充（2026-11-14，实施前）

按本 ADR 的跨语言恢复授权，明确一个新增的可选存储合同：既有 canonical `work.budget.attempts[attemptId]` 与其 `pendingTools`/`uncertainDispatches` 行可携带 `nativeRecorder`，形状为 `{schemaVersion:1, runtime:"peer-native", execution:<原 SessionExecutionIdentity>, recorder:<既有完整 bootId/pid/pidStart/hostId/acquiredAt tuple>}`。写入者必须是当前 lease 的实际原生 executor，在首次模型/工具 dispatch 前采集，随同一 canonical budget 事务提交。它不是新任务表、私有执行日志、checkpoint 或可重用 grant。TS 保留未知字段并继续保守恢复，不能把其存在当执行成功。新增合同必须在 packages/protocol contract resources 固化并对照旧 TS 冷读。

此条补充 ADR 124 的原生停稳 Adapter：只有原执行 identity 完全匹配、全部相关 recorder 一致、实际 OS 观测证明旧 executor 已死、且不存在任何未结束 capability handle 时，Host 可据此确认本地原生 runner/scheduler 已停止并生成既有 managed_execution stop receipt。它不证明历史工具的效果；所有 pending dispatch 仍转入 canonical uncertainDispatches，unknown 保留，原工具绝不重放。Shell/MCP/外部任务句柄未能证明结束时继续阻断，不能用 recorder 死亡伪造 ended。缺失/不完整/混杂/新版本 recorder 或 OS 观测失败一律不可用。Session Control operation 自身的 recorder 仍是实际记录该 operation 的新 Host，不冒充旧进程。现有 ADR 124/127 的其它 recorder、claim closure、策略与人工确认要求不变。此为 A 级可选合同补充，不替代运行/平台验收。

### NR-03 已确认文件创建的 claim 身份（2026-11-14，实施前）

允许既有 ledger 中属于同一执行与 hostEpoch、仍为 reserved/active 且无 unknown/closure 的 file claim，从 `identity=missing` 更新为本 Host 的实际 File Provider 刚创建并确认的文件身份。必须先持久化配对的真实 Tool Result、Evidence 与 dispatch receipt，再在 ledger 事务内重新核对 scope、执行、owner、当前文件身份；递增原 claim revision，并在既有 resource_events 记录真实 tool-result 引用。相同已应用身份为幂等；已有非 missing 身份变化、外来 owner、reconciling/closed、unknown 或观测不一致全部拒绝。它不推断助手文字、工具计划、文件存在或历史 approved 为创建成功，也不释放 unknown。此为既有 schema 的受控身份确认补充，不新增执行日志或授权路径；须验证同轮“创建→读取→改写”和 TS 冷读。

### NR-04 用量双文件提交恢复（2026-11-15，实施前）

ADR25 的 scope、Store 所有权和既有格式不变；本条收紧其“不声称 index/JSONL 崩溃原子性”处的恢复保证，仍不声称两个文件瞬时原子可见。已用隔离真实 TS Store 复现：index 累加10后 ledger append EACCES，重试同一 id 后 index20而 ledger一行。按本迁移的恢复授权，A 级补充如下，先登记再实施：

- 同一 ConversationStore sink 负责 Node/Rust。持锁顺序为 index.jsonl.lock → .usage-ledger-transaction.lock → usage/requests.jsonl.lock；无 TTL 清锁。辅助 usage 日志写入也参与最后一把锁并拒绝不完整尾行。
- 既有 `.usage-ledger-transaction` basename 增加可选 schemaVersion=1 的单笔 Store 提交意图文件：ledgerRelative（只与 Host 已配置目的地比较，绝不据内容解析写入位置）、conversationId、before/after（仅 lifetimeUsage/runtimeTurnCount）、完整 ledgerRow、ledgerLine（其唯一末尾换行的原始UTF-8行；解码内容必须与ledgerRow一致）、prefixBytes/prefixSha256。它是用量提交恢复材料，不是第二个执行日志、任务、checkpoint 或权限真源；不得包含秘密。生产目的地仍为既有 usageRequests。意图随 conversations portable 数据保留，未结算提交须在同步/回退前 drain。
- 严格验证、有限内存扫描与同 id 去重 → fsync 意图并同步目录 → 原子更新并 fsync index → append并fsync真实 ledger行 → 删除意图并同步目录。返回前必须完成两边。重复身份且已提供字段冲突（重试省略可选归因仍返回原行，保留ADR25既有幂等）、未知 schema、坏账本/非普通文件、安全整数溢出全部失败关闭，不归零或略过。
- 恢复只比较相关计数器；仍为 before 则应用 after，已为 after 则只补日志，其它值冲突即阻断。保留其它 metadata/未知字段。先核对保存的 ledger 前缀长度与 SHA256；完整额外行可以保留，并在追加前重新持久化当前前缀。只有从已证明前缀开始、逐字节等于原行前缀的部分追加，才允许补剩余字节；不截断未知数据。已存在相同行为幂等，重复/冲突阻断。
- 单行256KiB、意图512KiB、index沿既有8MiB/4096行边界；扫描不将整个 lifetime 日志驻留内存。取消只在提交意图前终止；已开始提交必须完成或留下可诊断意图，不能删失败记录制造成功。错误区分 invalid/limit/conflict/commit_uncertain。
- 崩溃残留目录锁仍按§5离线维护：确认全部写入者退出、保全文件/锁副本，核实并受控移除孤锁后，由支持v1意图的新 Store 先恢复，才准许旧版本写入。旧版不能自行忽略意图恢复。未带意图的历史半提交无法可靠推断；不自动重算、回填或改个人账单，保留原计数和明确诊断限制。
- 原生 Host 用稳定 runtime-turn id，在成功和已知终态错误都持久化已观察的 turnTotal；null usage不制造零量。lastRequest仍独立，ledger禁止用于容量恢复。Store失败不得跳过真实 attempt/工具停稳。硬退出前尚未持久观察的供应商用量不能重建，不重放模型请求；需保留未知，不能宣称已知零费用。原生公开接线与恢复分别验收。

实施验收：实际 TS↔Rust 写读与同 id 冷读；index后追加失败、部分行、意图清理失败、冲突/损坏/新版本、双进程竞争与已知孤锁离线恢复；每次恢复后再写新回合。旧失败保留。未完成这些验证不得宣告 P4 总闸通过。

### NR-04 已观察用量的 canonical 预算快照（2026-11-15，实施前）

A 级补充：终态提交意图只能恢复已经进入 Store 的账目；原生 executor 在工具效果之后硬退出时，旧预算虽保留 tokens 总和，却不足以重建 input/output/cache 的分量。保留旧数据的 unknown 限制；本条只为新观察增加预防，不推断旧记录或重放请求。

允许既有 canonical `work.budget.attempts[attemptId].nativeUsage` 携带 v1 billing-only 快照：`{schemaVersion:1, workId, execution:<完整原execution identity>, conversationId, attribution:<原stable stream/ledger id、模型/渠道、workspace与role>, usage:<tagged RuntimeTurnUsage>, knownAmountsOnly:true}`。仅支持当前已迁移 `work_session` executor；其它角色须先完成其兼容 pass。每次真实模型请求的归一化观察，同预算 tokens/unknown 更新原子进入同一 canonical Work 事务，并先于任何后续工具 dispatch。它不是第二个执行日志、checkpoint、grant 或 Context 来源；不能据此生成 Tool Result、Evidence、完成或许可。只存分量和归因，不存凭证、原始供应商签名、正文或 lastRequest 容量观察；账本仍不得用于 Context restore。

Loop 结束时，原 attempt 的快照和 nativeRecorder 原样移入 `work.budget.nativeUsagePending[attemptId]`，同时沿原规则保留 settled/pending dispatches。原 attempt 保留 `nativeLoopFinished:true` 与完整 nativeRecorder，直到匹配 execution 的真实 managed_execution stop receipt 证明 runner/scheduler idle 且 admission closed，才移除该结束标记；标记本身不证明工具或进程已停稳，未产生可计费用量的 loop 也保留此恢复来源。未知/新版本快照保留并阻断记账，不得阻断真实 stop/drain。只有现有 Store 返回相同身份、分量与归因的真实 ledger receipt 后，当前 journal owner 才能 CAS 移除相同 pending 值；失去 lease、回执丢失或值变化时保留，下一次用原 id 去重核对。工具 unknown 和 budget unknown 不因记账而清除。

新执行先核对 Store 意图和已结束的 pending 快照，再准入模型。恢复正在运行时先取得既有实际停稳/对账证明，才把旧 attempt 的完整快照转入 pending；未停稳的活跃观察不能被另一 Host当完整回合提前封账。已记录 loop结束的 pending 可独立核对费用，不证明历史工具效果。每次恢复最多处理64条；超量保留剩余并要求继续显式 recover，首次执行保持阻断。单快照16KiB，已知计数安全整数，未知/冲突/损坏均失败关闭。

兼容范围：当前旧 TS 的 worker 路径保留未知预算字段；delegation dispatch recovery 只删除 project_agent/spawn_session attempt，不能把该证明扩展到尚未迁移的 coordinator。必须用实际 TS read→saveWork→read 及 Native重读验证两种字段保留。旧引擎不负责结算新增快照，回退/同步仍受§7的 drain 要求；此条不声称已通过默认共享写入或发布验收。新增形状先冻结在 packages/protocol contract resources，复用现有 canonical journal、锁、身份与 Ledger，不建私有文件或第二套任务系统。

验收包括：真实“模型→文件效果→硬退出→停稳→已知用量一次入账”；stop后/意图前硬退出；Store错误及回执丢失；未知快照仍先停稳、事实原样保留；TS往返与后续任务；无模型/工具重放。此前未携带分量快照的旧记录继续 unknown，不自动制造账目。

### NR-04 可恢复的压缩历史选择与容量绑定（2026-11-15，实施前）

A 级补充，修订 ADR57 §3.1/§3.6/不变式5。实际 TS split 在同一用户回合只保留原 user，现有 marker 插在 user 之前，冷读却重新引入其后的已压缩工具历史。daa4c478 的隔离基线 warm1/cold4 已保存。不能用内存历史宣称持久压缩成功，也不能删除原文或复制相同 id。

既有 `_compaction` marker 允许可选 `historySelection:{version:1,compactionEpoch:<安全正整数>,retainedMessageIds:<原始消息id有序列表>}`。marker 追加在 canonical JSONL 末尾，原始消息和 Tool Result/Evidence 原位保留。选择仅引用 marker 之前唯一存在的非 marker user/assistant/tool 行，次序与原文一致；随后接 marker 后的新行。缺失、重复、乱序、未知版本、非法类型、超限或与后续重复身份均失败关闭，原文不动。上限在 packages/protocol resource 冻结。旧 marker 仍按既有 suffix 规则解释。

Canonical projector 升至3，TS/Rust 同时实施、重生成差分 fixtures；新 marker epoch 进入 continuity metadata。选择只决定上下文，不提供许可、执行、Evidence 或完成真值。Renderer/Ratatui 不解释引用。压缩后必须从实际持久源重新投影、装配和计数，不能复用旧 count。

容量继续使用既有 `.context-snapshots/<conversation>.json` 和 index mirror，不从账单恢复。新写入增加 `projectorVersion:3`、`compactionBoundaryId:null|<实际最后marker id>`。同模型、合法 provider-request observation、匹配 boundary/epoch 才能恢复 pending 基线。新选择出现后，缺失/旧 binding 和 superseded observation 不可复活压缩前高水位；未知快照保留，仅投影未知。summary 计费但 capacityBearing=false。

Store 持既有 index→conversation 锁，以原 content/source revision CAS 追加完整 marker，随后更新派生 index。沿用 body已提交/index未完成时的显式 reconcile_index，不声称瞬时双文件原子。marker 已落盘而 snapshot 未更新时，即使旧 index revision 未推进，boundary 不匹配也必须使旧快照失效。当前 TS/Rust getter 同时核对。Native recover 在真实停稳后才修复派生 index、核对账目，不重放模型或工具，不删除旧 snapshot/unknown。

首次原生 worker 会话若无模型 metadata，可由已通过准入的冻结 Goal model selection 写入实际绑定；已有不同绑定时拒绝，不覆盖用户选择。此 metadata 不是授权。System Context 增补注册的 continuity Source 和专用 summary cognition Source Adapter；历史原文只进入 user/factual payload。

兼容限制：v3 selection 要求支持合同的当前 TS/Rust reader。旧发行版不能安全续跑新选择，不宣称任意旧二进制兼容。默认共享写入、安装和回退仍须 §7 联合兼容与 drain 门禁；本条授权源码及隔离夹具，不授权个人数据、安装或默认切换。

验收覆盖真实工具后的自动压缩→落盘→重读→重建→重计数→发送；温/冷一致、原始字节及工具身份保留；summary/失败计费；overflow 单次恢复；marker后硬退出、index部分提交、旧容量不复活和后续任务；实际 TS↔Rust 冷读。未完成不得记 P4 总闸通过。

### NR-04 原生 MCP dispatch 与停稳观测（2026-11-15，实施前）

沿 ADR31/32、116/124/127 迁移 MCP Provider，不改变可见性、许可或 unknown 收口政策。三种 transport 分别实现；原生 SDK 不支持的 legacy SSE 使用有界 Adapter，不改写配置。连接初始化和 tools/call 分开：Host 在启动受管 transport 前验证真实 grant，在初始化完成、实际 tools/call 写出前再次核对同一 grant、registry source、Goal/binding、policy 与 lease；拒绝或取消不能发出 tools/call。MCP description、resources、prompts 均不自行成为 System Context 指令。

允许既有 resource handle 携带可选 `nativeMcp:{schemaVersion:1,role:"rpc"|"connection",transport,registryRevision,ownerRecorder:<完整原生 recorder>,childRecorder?:<实际 stdio 子进程完整 recorder>}`，与原 execution、hostEpoch、toolCallId 一起核对。它只证明受管本地连接/进程的身份和活性，不证明远端效果。未知版本、不完整身份和未登记启动窗口保持阻断；不得按 PID、超时、连接关闭或原生 owner 死亡推断任意外部工具已结束。stdio 的进程组必须实际结束并回收；HTTP 的 owner 死亡只证明本地请求泵已消失。恢复只针对匹配原执行和完整 recorder 的本地受管句柄，不重放请求，不把其 ended 写成工具成功或无效果。

MCP 已发出的请求在超时、断连、取消、超限或回执不确定时保留 canonical pending/uncertain dispatch；对账为 `unfenced_external`，不可凭本机 Git clean 自动收口。只有协议结果或明确的未派发事实可以进入相应已有结算；实际协议错误与业务 `isError` 分开。结果、失败、拒绝与 unknown 均经既有 Conversation/Evidence Store，元数据可携带 server/transport/tool/投影身份但不携带 headers/env/凭证或原始底层错误。

本条不引入新的执行日志或可重用 grant。bounded 连接/消息/通知/输出、真实正常/拒绝/降权/取消/超时/截断、重启 unknown 不重放及后续任务须通过公开 CLI 和 TS 差分验证。启动登记窗口和任何不支持的 credential/schema 明确阻断；未证明的恢复不记 P4 总闸通过。凭证命名空间与旧密文迁移仍按 ADR0001/32，不能在 transport 内暗中解密 Electron 或回退明文。

本卡 v1 界限冻结于 mcp-runtime-v1 resource：最多8个受管连接、通道1条、单帧1MiB、单RPC累计8MiB/128帧、单请求256KiB、归一化结果256KiB、30秒deadline。超限明确失败并保留可能效果，不静默截断或替换原返回类型。明确未写出 tools/call 时可在 Evidence 追加 `dispatchOutcome:"not_dispatched"`，canonical receipt 仅由 Host 采用此受信 Provider 事实；模型/服务端字段不能提供该事实。HTTP 不自动重试或重定向；legacy SSE endpoint 限同源，避免配置凭证跨源发送；这属于本原生 Adapter 的保守限制，不将此卡记为完整协议平价。现有已显式配置 headers/env 的注入值在返回进入模型/Evidence 前脱敏；新凭证管理仍须 Vault Adapter。

2026-11-16 B级协议补齐：Streamable HTTP等待原RPC的SSE结果时，仍须发送SDK产生的服务器请求回复/通知；最多保留原响应流和一个控制POST，不创建脱离受管owner的后台任务。控制回复只能沿已有transport，不生成工具、许可、Evidence或模型调用。客户端与服务器各自的请求id可重合；只有同id的JSON-RPC响应/错误可结束原响应流，服务器同id的请求不算工具结果。协商版本只绑定到真实initialize请求的响应，Tool Result里的同名字段仍是原始事实，不能改变连接配置或下一请求header。明确禁用底层HTTP协议NACK重试，保持不自动重放；断连/失败仍按原unknown契约处理。此补齐沿ADR31既有双向协议，未移动能力、授权、存储或System Context边界。

### NR-04 原生模型账号登录与只读状态（2026-11-16，实施前 A级补齐）

沿 ADR0001/28 和已接受的全面迁移，新增 `models auth <configured-channel-id>`、`models logout <configured-channel-id>`、`models status <configured-channel-id>`。这些是用户显式调用的本地凭据管理命令，不进入模型工具面，不授予能力、PermissionGrant 或 Evidence；不能因 auth 成功自动执行用户任务。既有裸 `models` 列表与完整配置 CRUD/写入所有权继续按 P4 功能表交付，本节不将缺项删出目标。

- 只选择现有 v2 channels 的唯一 id，认证方式来自当前已声明 Adapter，ChatGPT/Google 使用实际 TS 中冻结的 installed-app identity、固定授权/token端点、现有 localhost 回调路径/端口和 S256 PKCE。原生实现使用外部浏览器授权 URL（CLI 明示 URL 及取消方式），不嵌入浏览器、不用 Bun/Node 或旧 CLI 引擎代办。授权 URL 不包含 code verifier、token 或用户 client secret。
- 单次 flow 拥有 listener、state/verifier、HTTP请求与 Helper 子进程。回调只绑定 IPv4 loopback；按实际 redirect 检查唯一 Host、路径、唯一 state/code，拒绝混淆/重复/错误 state。头大小/连接数/每次读写与总等待有界，取消/拒绝/超时关闭所有自有资源。callback 页面只确认已收到回调，不能在 Vault 验证前宣称登录成功；输出/错误不带 code/verifier/token。
- 授权码交换固定端点，禁止重定向和自动重放，整响应有期限/大小界限；按现有 token schema 验证 access、Bearer、正 expiry 与账号元数据。JWT claims 仅用于既有路由/显示元数据，不被提升成新的授权事实。
- 开始时捕获只读 channel 绑定和真实 Helper snapshot/revision（包括明确重新登录要替换的 pending/损坏 token JSON）；交换完成先复核 channel，再只 CAS 原始凭据代。新登录/退出/配置移除或修改使迟到 flow 失败，不无条件覆盖。Helper 缺 CAS feature 在授权 URL 和远端效果前拒绝。Vault 密文/schema 损坏仍保全，不为重登重建 Vault。
- 登录只有在 Vault 条件提交且原值回读验证后返回 credential_updated；回执丢失报告 unknown，status/新登录以实际 Vault 对账，不自动重放授权码。logout 只条件删除当前代，不调用远端撤销、不复活已删账号；缺失幂等。status 仅投影真实凭据为 not_logged_in/authenticated/refresh_required/recovery_required，不输出秘密，pending/未知 token 不能冒充未登录或可自动刷新。
- 明确修正原生 loader 的实现偏差：oauthConfigured/oauthExpires/oauthAccountId 是非权威提示，不能替代实际 Helper token 或阻止已成功落盘的原生登录准入。仍需唯一配置绑定、已启用模型/渠道和原授权链；无 token、pending、错误 provider、未知 schema 仍拒绝。本卡保持 llm-providers.json 原字节，不无锁回写元数据。完整配置写入所有权、提示恢复、账号创建、混合旧安装版本升级/drain 和 P4总闸仍必须另行实现/验收。
- PKCE/state/请求参数从真实 TS 登录流程生成 conformance 资源；隔离 IdP + 真实原生 CLI + 加密 Helper Vault 验证正确/错误/重复回调、端口冲突、拒绝、取消、超时、晚到登录/退出、提交回执丢失，以及登录后实际模型/工具/Evidence 闭环。共享 loopback parser 可抽为 runtime 内部 Module，MCP仍保留原 redirect 限制与错误契约；不得顺带放开 MCP 端点。

正式 IdP、系统 Vault 和多平台安装分别验收；模拟网络不冒充真实平台认证。依据：[RFC8252](https://www.rfc-editor.org/rfc/rfc8252) 与 [RFC7636](https://www.rfc-editor.org/rfc/rfc7636)。

### NR-04 模型配置写入所有权与损坏保全（2026-11-16，实施前 A级补齐）

完整原生模型管理继续迁移既有 v2 `llm-providers.json`（channels/models），不建立另一份配置或把凭据写入JSON。新增跨语言 ModelConfigStore Module：边界是有界读取、源版本、同名目录锁与条件原子替换，负责配置事实，不负责模型、工具或凭据授权。此项收紧 §5 对此 Store 原先未证明的写入所有权；不改变 channel/model 身份、Vault命名空间或本地执行链。

- Rust 与当前 Desktop / runtime-node 配置写入参与同一个 `${file}.lock` mkdir协议，按文件所在目录的真实路径统一名称；锁自身不得是symlink。完整同步 read→mutate→write 在锁内，不仅锁 rename。进程内嵌套沿同一 owner，异步网络/浏览器等待不得持锁。等待有期限，可取消的宿主应检查取消；超时/锁替换失败关闭，未知残留锁不因TTL自动删除，沿 §5 离线维护恢复。
- 读取上限 1MiB，深度32/节点16384；拒绝非普通文件、损坏JSON、显式未知version及不支持shape。不存在才是空配置。已发布的flat数组及version缺失的channels/models兼容形态仍由既有迁移Adapter处理；当前原生写入先仅接受明确v2，旧格式不擅自升级。不能把解析错误当空配置后覆盖原文件。未知 root/channel/model 字段在相关更新中保留。
- 写入以同一快照身份/内容版本进行CAS；原子同目录0600临时文件→fsync→rename→目录fsync。rename前失败保留旧文件；rename后确认失败报告commit_unknown，重新读取实际配置对账，不回放修改或还原旧快照。锁被替换不得删除替代owner。没有未知效果时原配置可在修复后再次接收修改。
- Desktop 的同步CRUD、读取时迁移及metadata回写都由同一事务拥有。异步诊断/价格获取在网络结束后重读锁内最新对象，只更新仍匹配原对象身份/配置的结果，禁止用网络前整份旧数组覆盖其它宿主更新。runtime-node显式OAuth提示写入也必须在共享锁内重读，保留原布局和未知字段。
- 凭据提交与配置原子性不能仅凭此文件锁宣称完成。最终账号创建/删除/修改、原生auth/refresh和TS凭据管理需在各自短提交段取得此锁并重新核对绑定，锁顺序config→Helper/Vault；网络等待释放。失败恢复必须以真实凭据代条件核对，禁止无条件还原消耗过的旧refresh。提示是可重建投影；配置提示失败不使已提交token失效。完整Vault/配置联合故障、混合安装版本drain与CRUD命令仍逐项验收；未接入的写者/旧二进制不被此新规则自动保护。
- 验收必须从实际Desktop和runtime-node入口及原生Store跨进程竞争，覆盖丢更新、超时/取消、损坏/未知版本保全、未知字段、迟到网络、替代锁owner、提交不确定与后续修改。Store地基或源码接线通过均不等于完整原生命令/P4总闸。

### NR-04 配置能力范围校正（2026-11-16，后续命令实现前 A级澄清）

按 ADR129 与用户原始全面迁移目标，终态覆盖原 CLI 的实际可达行为，不借“全面”新增 Desktop-only 产品能力。重新核对 `apps/tui/src/cli-argv.ts`、`cli-models.ts`、`cli-model-lines.ts`、`model-config.ts` 与方案 §6 后确认：原 `models` 只输出可选模型的tab分隔列表，`PEER_MODEL_API_KEY` / `PEER_MODEL_BASE_URL` / `PEER_MODEL_ID` 提供无需Desktop的环境配置；原CLI没有新增/删除渠道与模型的完整CRUD命令。配置Store及Desktop写者共锁仍是跨宿主一致性的必做项，但不等于必须把Desktop设置产品全部搬成新增CLI命令。

本澄清取代上两节及实施账本中把“完整原生配置CRUD/账号创建命令”作为P4必要退出条件的扩大解释；不删除原有入口，不将尚缺的原生功能记为完成。P4配置交付必须包含：

- 原 `models` 的选择过滤、provider/model/display身份、stdout/stderr、退出码与环境优先级；按实际TS入口生成fixture，与真实公开原生CLI对照。
- 三个已发布 `PEER_MODEL_*` 环境配置字段、缺省模型/baseURL及显式选择的原生模型/工具/Evidence执行，不把环境秘密持久化、不需Desktop或Helper代取环境秘密，不靠JS sidecar。环境只是既有本地模型配置来源，不是System Context或工具授权来源。
- 已有文件/旧格式的模型读取、模型/强度选择、Vault引用、原有OAuth刷新/显式重登与metadata写入/恢复；当前 `models auth/logout/status` 已接受的账号入口保留。配置创建不成为普通模型工具，也不扩张能力/权限/Evidence。
- 所有当前Desktop/runtime-node配置写者与原生凭据短提交参与相同Store/锁/条件恢复；混合旧安装版本drain、真实平台和协议验收仍分别满足。未知/损坏配置不因范围校正被覆盖或默认授权。

将来若增加一套用户可见的模型/渠道CRUD命令，应作为新增产品能力单独确定Interface；不作为本次CLI迁移完成的额外前提。先前共享Store、损坏保全与并发修复继续有效，不回退为无锁写入。

### NR-04 OAuth配置提示重建与显式对账（2026-11-16，实施前 A级补齐）

原 `models`/ModelPicker只读metadata判断可选项；它们不应为列出模型而打开Vault秘密。原生登录已经能写真实Vault，旧候选刻意不写metadata，因此可能出现真实已登录而旧oauthConfigured仍false、列表没有该账号的既有状态。本节补齐这条用户可用链，取代模型账号首卡“本卡保持llm-providers.json原字节”的阶段限制；不改变Vault作为凭据权威、status只读或能力授权。

- 新增窄恢复入口 `models reconcile <configured-channel-id>`：仅核对该已配置OAuth渠道的真实Helper记录与配置绑定，在同一config→Helper顺序下重建 `oauthConfigured` / `oauthExpires` / `oauthAccountId`；不创建渠道/模型，不登录、不刷新、不请求模型/工具，不迁移个人任务，也不因修复提示生成授权或Evidence。
- 真实缺失可清理上述提示；有效已知token可投影存在/expiry/account。pending、损坏、未知schema、错误provider、无法读取Vault均保全原始事实并拒绝修复，不把unknown写成未登录。Account/expiry只来自已验证的token字段，提示中不写秘密。相同投影不改文件/revision；保留root/channel/model的其它字段，修复已知同组model残留的三种提示覆盖。
- auth/logout成功确认真实Vault结果后，在仍持config锁时尝试同一提示重建。凭据结果与提示结果分别结构化返回：已知updated/removed不能因metadata失败变成“凭据未更新”，失败也不能恢复旧token；提示失败返回rebuild_required或commit_unknown及明确reconcile动作。Vault提交本身未知仍沿原未知错误，不因metadata看似已更新宣称凭据成功，不重放code/refresh。
- 自动刷新沿同一Module尝试提示重建。非权威提示失败不能让已验证的新token失效；但配置operational binding、凭据代或锁owner无法证明时仍拒绝模型准入。无新增秘密影子库、独立修复日志或后台重试；对账从原配置引用和实际Vault可重跑。
- 为避免自身提示更新使原绑定失效，Native与当前TS凭据绑定比较只忽略上述三种非权威提示；provider/auth/endpoint/header/project/model/启用状态及其它既有操作配置仍按原边界核对。跨语言fixtures验证提示变化不伪造配置许可，真实操作配置变化仍使迟到结果失败。
- status保持只读，models列表保持metadata/环境来源，不为列表解封秘密。正式系统Vault、混合安装版本与默认共享域仍单独验收。新增reconcile的理由是已有原生账号操作的部分提交恢复，不扩展为Desktop整套CRUD。

2026-11-16 环境来源接线前补充（A级身份/Adapter澄清）：原环境catalog使用 `providerId=openai-compatible`、当前PEER_MODEL_ID或gpt-4o-mini，reasoning选择为off/low/default/high。原生模型factory只在显式选择该source且model相符时取环境秘密；普通三字段RuntimeModelSelection可用，canonical Goal既有四字段格式不变，该来源的modelProviderId/family若存在须同为openai-compatible。已有文件渠道绑定不因环境变量存在被重定向或获得环境key。独立Env Provider沿实际createOpenAICompatibleProvider的Chat请求（含off、default和tools语义），不误套品牌Chat启发式；它是现有wire encoder seam的Adapter，不另开工具loop。模型列表只读metadata/环境，不调用Helper；非法终端控制文本与未知配置版本可见拒绝，原文件保全。以上需真实TS请求fixture及公开原生CLI模型→工具→Grant/Evidence验证，不能由列表或factory单测冒充完成。

### NR-04 MCP刷新未知结果持久化（2026-11-16，实施前 A级补齐）

沿ADR132新增可选Vault envelope refreshState意图，先持锁发布并验证，再允许SDK刷新；同owner持锁publish推进binding，失败/中断不恢复旧refresh。当前Rust工具/refresh与Desktop冷读拒绝pending，显式原生重新授权才能清除。原不可变slot与历史保留，旧安装/预读token仍受drain闸。该凭据操作不是tools/call派发或工具Evidence；grant延续与当前TS token发送guard尚须后续实现验收。具体schema、顺序、异常恢复与测试见ADR132同日修订。

### NR-04 原生MCP credential epoch与原grant续行（2026-11-16，实施前 A级补齐）

沿ADR132同日修订引入execution绑定、只在内存存续的凭据epoch：只有受管OAuth持锁发布的内部凭据证明可以推进已知真实Store revision。Host每次检查真实revision，只对这条已验证代际链规范化credential来源以复核原grant；其它授权/Context事实和外部变化继续精确拒绝。连接owner有限排队，旧HTTP连接停稳/join后才刷新与替换，stdio不自动重启；不重放tools/call，不改写grant/Evidence或清除unknown。重启丢失epoch证明，沿原Store/任务恢复准入。细项与验收见ADR132；当前TS预读发送guard、安装drain与P4总闸另验。

### NR-04 当前TS MCP token发送与共享恢复（2026-11-16，实施前 A级补齐）

沿ADR132同日修订，TS官方SDK fetch seam在token HTTP之前取得共享metadata owner并发布已有refreshState，code交换也用同一pending合同；只由该owner验证并发布新Vault代，SDK晚到save仅消费匹配回执。当前读/保存/redirect回调复核代，显式Host authorize purpose可保留已知pending写入新的PKCE并重新授权，未知schema保全。tools/call认证失败/redirect不自动重放且保留unknown；close取消并等待受管HTTP。原生兼容已保存且一致的SDK issuer cache与真实token.scope，仍经受限发现和原权限链。新回调是同进程Host Interface，不是Renderer许可或新跨进程真值；旧已运行版本drain仍另验。


## 2026-11-16 NR-04 Grok 原生订阅接入（A，实施前登记）

沿ADR28/37/50和已接受129的完整Provider范围，将当前CLI实际`oauth_grok`接入原生Responses wire；不启动官方Grok CLI、JS引擎或业务sidecar。复用原ModelBinding、Helper模型OAuth CAS/前置刷新意图、Context/用量/压缩与模型编码接缝。Grok当前channel descriptor只声明订阅OAuth，不借本卡新增API-key渠道或工具授权。当前TS仍为迁移对照与Desktop实现，不把它当原生运行依赖。

### 认证与凭据

固定已有公共client身份、`auth.x.ai` issuer/device/token/userinfo和`cli-chat-proxy.grok.com/v1`模型平面，常量由当前TS生成共享contract resource。显式`models auth <已配置Grok渠道>`使用RFC8628 device flow：一次device request、至少按interval等待后poll；只对authorization_pending/slow_down继续同一device grant，slow_down每次再加5秒，denied/expired/未知错误/redirect/取消即结束。整体至多15分钟且服从服务器更短到期；单HTTP沿原15秒/64KiB模型OAuth预算，不自动刷新device code、不把轮询扩展为模型/工具重放。Secret device_code只在有owner的有界内存中，绝不落盘、入argv或回显；给用户的verification URL/userCode/有效期是独立的管理提示，不代表登录或任务成功。Ctrl-C取消当前登录，保留原凭据/配置/任务；新显式登录从新device授权开始。

Protocol登记可序列化的模型认证提示：保留旧browser的authorizationUrl输出，新device方式仅增加明确的userCode/有效期可选字段；CLI展示端消费结构化提示。原browser账户不改变callback/state/PKCE。仅呈现受限HTTPS官方验证地址；test-only loopback替换继续受编译feature与自有fixture marker限制，featureless产物不开放端点覆盖或读第三方Grok auth文件。不会自动打开浏览器或把URL内容作为系统指令。TUI完整交互仍在P6接同一管理入口，headless模型执行本身不暗中创建登录流程。

`model/<channel>/oauth-tokens`沿既有加密payload保存access/refresh/expires/scope/issuer/clientId与可选账号信息，未知字段保留；明确provider若存在须匹配Grok，提供的issuer/clientId必须匹配固定绑定。实际scope必须包含api:access，缺失不向模型平面发请求。刷新省略scope/refresh延续实际原值；返回scope集合变化或丢失api:access保留刷新pending并要求显式重登。新device授权的scope省略只按OAuth省略语义延续本次完整请求范围，不据metadata scopes_supported扩大scope。公共userinfo仅用于非权威账号展示，失败不伪造账号或撤销已证明的token；userinfo不进入System Context/许可。登录前后核对原配置身份与Vault代，晚到登录不得覆盖新登录/退出/删除；最终提交和提示投影恢复继续沿原Account seam，不另建凭据存储。

### Grok兼容传输

新增私有深Module持有每个原生模型实例的有界兼容状态，不按host散落分支。元数据只从已有`https://x.ai/cli/stable`读取，无Authorization/账号/自定义origin头；4秒、至多64字节、无redirect，只接受完整major1 semver。沿原6小时cache/24小时有限stale策略，不持久化版本、不从服务器报错或环境变量猜版本；未来major在推理前拒绝。取消覆盖本次metadata/HTTP，无detached task。元数据准备结束后、每次真正模型POST前，再走真实OAuth/config绑定检查；不能因为cache预读沿用过时token。

模型请求复用同一prepared原始字节与fingerprint，按既有Grok固定身份头加实际发现的client-version。只对原协议明确的推理前426拒绝，强制重读官方feed；仅版本确实改变且仍受支持时，允许同一逻辑请求再发一次。相同版本/第二个426/其它错误不重试，不更换模型或从error text取版本；取消/Context绑定变化阻断下一次物理请求。这个Grok专用426行为不开放给其它Provider、MCP或本地工具。预算/用量仍按既有逻辑请求，实际返回的观察与unknown不能用兼容重试制造成功。

账号头归Provider描述而非Responses wire：ChatGPT的chatgpt-account-id不能泄到Grok，仅发送该Provider实际声明的账号头；协议/品牌/凭据仍正交。普通OpenAI/Google/Anthropic请求保持原Module路径。

### 验证与边界

先冻结实际TS refresh、channel/request/header和版本状态fixture；用公开原生models auth/status/logout/reconcile、真实加密Helper和本机合成IdP/模型走工具→Grant→Evidence闭环。覆盖pending/slow_down/拒绝/到期/取消、无api scope、issuer/client/provider冲突、token轮换、迟到配置/凭据、bad/超限/未来版本、metadata无密钥、426最多一次且body/fingerprint不变、之后的新任务和原unknown保全。网络/TLS/代理继续同一Native Network；featureless候选通过隔离TLS/proxy入口核对，不触个人凭据或系统信任。实际公开IdP/模型、OS Vault和安装drain仍另验；本修订不是Grok或P4已完成声明。

核对于2026-11-16的主来源：[xAI OIDC metadata](https://auth.x.ai/.well-known/openid-configuration)、[官方CLI认证说明](https://github.com/xai-org/grok-build/blob/main/crates/codegen/xai-grok-pager/docs/user-guide/02-authentication.md)、[RFC8628](https://www.rfc-editor.org/rfc/rfc8628.html)、[CLI稳定版本feed](https://x.ai/cli/stable)。feed当前返回1.0.77只是核对事实，不写成原生固定版本。当前TS真实实现决定迁移兼容行为；公开文档不取代本地Grant/Evidence与恢复事实。

## 2026-11-17 NR-04 会话只读壳与有界导出（A，实施前登记）

沿已接受`108-cli-basic-shell-commands.md`迁移doctor、sessions list与export。它们是人明确调用的管理/阅读入口，不向模型投影新工具，不创建PermissionGrant、Evidence、会话接收或任务完成事实。sessions resume的完整交互仍须P6；不能以列表或导出冒充可继续普通对话。删除仍沿ADR34的独立跨Store级联，不能顺便实现为直接删文件。

doctor检查当前原生可执行文件及同目录Helper的存在/可执行性、数据根可写或其最近存在目录可创建下级、版本、TTY/颜色；不执行Helper、不解封Vault、不联网、不修复配置。不为检查而创建数据根/会话，缺HOME/非法根/不可执行Helper均如实失败。这里收紧旧TS检查时mkdir的副作用以遵守ADR108“只检查”；可写检查不承诺磁盘配额、未来权限或实际供应商可用。

列表由同一ConversationStore读index，继承原三种角色投影、时间降序和标题/更新时间输出；不触正文、stream、用量或任何后台迁移。索引沿原8MiB/4096行、节点/字符串预算，重复/损坏/非法身份或持续变化明确报错、原数据保全，不截取前N行冒充完整列表。时间按Store正常ISO字符串处理；非法类型/控制字符不作为可打印事实放行。完整源版本在输出前复核。

导出是展示快照，沿当前TS可见user/assistant content结构与Markdown格式，包括正确v1流式patch；不借用canonical persisted history的provisional-tail排除规则，也不把导出送入模型Context。Store复用现有有界JSON projection Reader，按行扫描/回读；先只投影id/role、跳过未选正文，再为可见行选择content。保留全源UTF-8/JSON结构/深度校验，100MiB工具行不分配其正文AST。扫描缓冲16KiB，每记录源上限1GiB；可见所选值原始编码/字符串各至多12MiB、65536节点/深度64、单key4096bytes，保证10MiB普通正文可处理且不加载整份1GiB历史。超出所选解析能力返回明确限制，不截断/修改源记录。索引/单次投影/临时格式化错峰，沿ADR130的32MiB其它缓冲预算；不是完整P6内存验收。

sidecar先投影身份与patch形状，只在首个匹配消息上读取其role/content，存在content覆盖时不再读原大正文。必须v1、conversationId/messageId匹配及object patch；未知/损坏/缺目标明确拒绝，区别于旧getConversation静默忽略坏sidecar的遗留行为。原JSONL、索引、sidecar的文件身份在开始/完成复核；同长度替换、内容改写、追加和stream代变化使本次导出失效。只返回派生sourceRevision/展示范围，不能据此证明停稳或授权。

CLI先将脱敏Markdown写入自己拥有的0600临时文件，源检查成功后才向stdout或目标发布。复用原sk-/Bearer/ya29模式，不读取Vault来搜索秘密，也不导出工具参数/原始Tool Result/Evidence字段；此模式过滤不承诺识别任意无前缀秘密。标题等可见metadata同样过滤。stdout只接受无终端控制/bidi控制的正文；出现不安全文本时明确拒绝，保留源，显式文件导出仍可取得脱敏阅读副本，不静默删除正文字符。用法诊断/输出路径须安全编码。

目标默认禁止覆盖；--force捕获原目标身份，完整spool后再次校验并原子替换，发布前失败/取消保留原目标，正常清理自有临时文件。拒绝会话Store内目标、所读源文件的symlink/hardlink别名及非普通文件，不允许--force写回会话。目录/文件版本变化拒绝而不制造成功；原生export发布阶段对输出父目录短暂取OS advisory lock（至多等5秒、可取消、进程退出自动释放），锁内复核目标CAS并rename，避免两个原生--force覆盖同一旧代。此锁无持久锁文件，仅用于显式阅读副本输出，绝不替代canonical Store既有mkdir锁/顺序；不合作的外部写者仍受协作式文件身份复核的局限，不称OS路径沙箱。磁盘满、broken pipe、SIGINT/TERM及发布异常分别如实结算；未确认的发布不能输出成功回执；rename已发生后的目录flush/回执失败保留现状并报发布结果未知，不反向删除/覆盖目标制造回滚。后续显式重试从当前目标重新捕获CAS；stdout写出失败可能已有前缀，非0退出不代表完整副本。不改变任何运行任务或unknown记录。没有新增持久化真源或自动清理用户文件。

验证先冻实际TS格式/脱敏/参数与正常Store/stream可见结果；损坏/未来sidecar的明确差异单列。公开原生CLI覆盖无HOME/TTY/JS、空/多角色目录、Helper/数据根失败、可见正文与秘密/控制、覆盖拒绝/原子--force、源/目标竞争、取消/损坏后原字节与后续导出。使用隔离合成Store验证1GiB历史、10MiB正文与100MiB被跳过工具行及资源曲线；正式二进制与普通P4总闸/安装/全产品/长时P6验收分开记录。实现与验收另记。


### 2026-11-18 NR-04 后台 Shell 启动、停止和失主恢复（A，实施前登记）

沿 ADR65、116、129–131 迁移既有 `bash background:true` 和 `shell_stop`。原 Tool Call、实时 Grant、canonical dispatch、运行子进程登记、公开工具结果和实际停稳是各自可核对的事实。原生 Host 先登记 NotStarted/Starting，复核授权后从 Provider 启动执行组，保存同一阶段下完整原 owner、PID/启动时点及本机启动代。只有 Host 已确认真实 Running 和产物初始化以后，模型才可取得 `status=running`、原不透明 `shell_<uuid>`、有界产物引用。该回执只确认启动，不能作为运行效果成功或进程已结束的证明。

普通会话沿原 `runtimeExecution.handles` 保存 schema 1 的 `shell_background` 派生控制记录和原 `NativeOwnedProcess`，与最初 pending dispatch 绑定。命令结果已发布后也要保留原 owner 责任，直到真实完成。进程相关权限仅来自原执行身份、批准和现有 Host，进程记录本身不签发许可。每个执行有上限，同时计入现有全局 live handle 上限。仍在运行的任务持续核验原权限修订和当前 owner，取消、租约失效或 Host 结束均走原 drain 屏障。以同一 execution 和原 Tool Call 定位停止，不按 PID、裸目录或用户传入工具路径选择进程。迟到/重复停止只能收真实终态，拒绝其他 execution 的 id。普通 `exec` 最终退出先关准入并停稳，ACP 断连同样；既有契约未授权 CLI 退出后分离后台任务。Post Hook 消费这次调用已实际观察的 Tool Result；启动回执只属于启动调用，不能替代另一次实际停止回执。

崩溃后只在原 owner 已死、scope 和实际 OS 起点相符时尝试停有记录的组。Starting 缺身份、未验证代次及未知外部效果保持阻断，不能从旧授权、进程组关闭或文件存在补事实。临时句柄和启动回执须可分别收口，真正未观察的原 dispatch 继续 unknown。前端仍走同一能力投影和权限；不增加主动模型执行、恢复重放或新数据根。委派复用同一进程 envelope 和停止语义，若新增 Work 数据只在相应语义 fence 及旧读写证明后接入。旧宿主实际 drain、P4 总闸另验。

先在实际公开入口冻结已知缺口和旧 Host 的启动、模式切换后定向停止、重复和找不到结果。验收包含真实权限撤销、两会话和两任务隔离、已有产物回读、正常/取消/超时/硬退出、真实 owner/current 检查、已确认和 unknown 双路径及后续任务。分步实施先落在可执行的 Handle 与 stop/recovery 约束，再开放新原生调用面并通过公开 Host 用例。

2026-11-18 实施复核（A，修正单 pending 准入）：真实原生 `exec` 已观察前一个后台任务实际 Running 和原启动回执，第二个 Tool Call 仍因 `prepare_conversation_tool` 的单 pending 守卫返回 `conversation_execution_busy`。普通 Host 仍只有一条串行工具调用链。该守卫只允许同一 active execution 下已经发布启动事实的后台 Shell 与下一次准备并存。要求原 Dispatching 记录、Running 的完整进程及精确 handle 镜像、原消息/调用/Grant/参数摘要、已提交的启动结果和匹配 Evidence 同时成立。任何 Prepared、未获准、未知、未留 Evidence 或其他种类的待处理工具继续拒绝后续准入。原会话新一轮准入、跨宿主读写和冷恢复保护保持原条件。原 owner 观察真实结束后，终态产物与现有进程记录分别落定，并用同一 Store 事务移除已确认的原挂起调用和已结束的镜像；启动回执和原 Evidence 留存。

### 2026-11-18 NR-04 持久前台 Shell（A，实施前登记）

沿 ADR65、116、129–131 将旧 Shell Session 中同会话的 `cwd`、环境变量和 Shell 状态迁入原生执行。实际旧 Node 套件覆盖同键串行、隔离、每次写入前重新授权、空闲句柄停稳、拒绝不消费 bootstrap 与超时重建。实际 `b1490f69` arm64 归档第二条前台命令仍报告 `empty workspace`。原始对照见[Shell 回执](../../playbook/native-cli/evidence/p4-native-background-shell-live-candidate-20261118.json)。

在同一实际会话执行内，由原生 Provider 持有唯一前台 Shell 进程组并保持原 owner。持久进程与每一次命令效果各自保存事实。普通世代的 Tool Call、Grant、声明 scope、派发和最终 Evidence 仍由原 Host 接线；进入排队和实际写入前用真实当前目录核对，拒绝无写入、无重放、无 bootstrap 损耗。空闲进程仍进入原 live Registry 与既有 canonical handles；每次命令关联当前进程代次及原 Tool Call。命令帧需要绑定本次写入和输出边界，stdout/stderr 分别有界流式归档，截断后继续排空。普通输出、时钟和退出文本不能单独确认命令完成。必要的命令结果观测和进程组停稳都由真实 owned worker 返回。

取消、超时、撤权、写入中断和关闭走原停稳屏障。仅确认实际旧进程组已结束后才能以新世代重建，已写入而无可信终态的原命令继续 unknown。失主恢复须核对旧 owner 死亡、进程组与本机启动代，不自动派发记录。未得到旧宿主兼容证明前，新增记录或语义不对旧读写器开放。普通 exec/ACP/交互共用当前会话装配和 Registry，委派资源继续受旧 claim/语义 fence 保护。接受条件包含真实 cwd/env 跨调用、命令/对话隔离、权限撤销和迟到、丢失帧及大输出、空闲与忙时断连、硬退出冷恢复、旧版互读和原生包执行。

实现复核（A，持久句柄格式）。使用既有 handles 中唯一的 `shell_session`，包含原已记录的 spawn Call、进程 envelope 及可空的当前命令绑定。绑定含原待处理 Tool Call、dispatch 和同一进程代次，只允许当前派发记录。可为空的绑定不释放仍存活的进程。起始阶段必须有原派发，Running 的空闲句柄可晚于最初工具结果独立存在。每次写入先条件登记绑定，完成消息与 Evidence 收口该绑定。冷恢复只凭实际进程组消失移除同一句柄，保留未核实的已派发命令。当前格式先在新 Rust/TS 与隔离数据验证。

进程层使用全双工 Unix socket 传入请求与返回专用控制记录，分别在原 stdout/stderr 读取随机命令边界。用户命令的 stdin 为 `/dev/null`，并关闭框架专用描述符。绝对目录改变和用户命令分步，经内核核对真实 cwd 后再取当前授权，文本 `PWD` 不参与范围证明。

### 2026-11-18 NR-04 原生 Shell 产物的有界记录（B，实施前复核）

沿 ADR65、116、129–131 补齐原 `local-shell-artifact://shell_<uuid>` 的产物写入。原路径、三份引用、Grant/Evidence 与已拥有进程组保持。Shell 产物根、日期、独占任务目录及各文件使用原目录 FD 打开和复核，拒绝替代路径、链接或已有任务目录。生成元数据必须在实际 spawn 前写成，失败沿原未派发状态。正文用小块从原进程管道持续读取，最多持久化每流 2,000,000 字节及一次截断标识，预览仍至多每流 64 KiB。超出持久化配额继续有界排空，遵循原超时及实时授权，保留已观察效果和截断事实。正文与终态元数据分别条件写入并同步，不作未经证实的成功回执。

取消、失权、超时和 I/O 故障仍经原 owner 控制端口及实际 process group/wait 核对。终态写失败报告未知并保留源文件及执行事实，不能由产物、时间或伪造退出码推导停稳。产物写入不建立执行或复活权。已有 Shell 任务及存量路径不迁库、不转移、不会因失败回退到原全量读取。

用旧 TUI Host/Provider 的实际合成用例核对持久、后台、停止与旧描述，并保留公开原生二进制对别名路径及 100,000 字节输出的失败事实。按实际公开入口验收小/大/双流、截断、零越界产物、拒绝和后续任务，覆盖旧读取器互读与原授权/Evidence。持久会话与后台 `shell_stop` 的执行登记、超时和恢复仍须继续接线验收，不能以产物通过替代。

### 2026-11-18 NR-04 固定交互结果的只读 CLI（B，实施前复核）

沿 `108-cli-basic-shell-commands.md`、ADR118 §17.3 和 §19、ADR129–131 迁移现有 `peer result <interactive-result://…> [--json]`。CLI 解析固定版本并格式化，Store 只读原 sqlite schema 5，原 Bot profile 仍是访问范围真源。读取前后核对 active profile 及原会话归属，读取过程中校验库、文件身份、固定版本、原发布操作与索引回执。复用既有无创建 SQLite 接缝，按已有合同限制所选字段和解码。不执行程序、取执行租约、访问模型、补写索引或创建清理回执。

本地可用版本、已清理墓碑和原设备摘要沿原可用性分支。只在固定版本确实缺失时查原 EvidenceIndex、GoalPlan、工作会话和唯一已完成的原 Tool Result；待登记、范围拒绝、损坏和清理均沿自身事实返回。清理后的摘要只读已校验墓碑。摘要以原 schema、纯文本/JSON 和未验证标识返回，不进入 System Context、模型工具或 Evidence。沿本机原格式与权限边界实现，不增加持久入口。P5 发布、核验、交付与保留清理另有工作包。

采用隔离数据上实际 TS/Bun 发布与登记写者、实际旧 CLI 输出和 Rust 正式入口做对照，覆盖三种可用性、原数据不变、owner 变更、重复/损坏/未知数据、待登记与终端控制字符。原 TS 集成基线 12 项通过，现有 featureless 原生包对固定引用明确返回命令不可用。实现和验收另记。

2026-11-18 兼容复核（B，恢复接线前）：使用真实旧写者的隔离 SQLite 状态复现了非空 WAL 与缺少共享内存索引的组合。旧只读入口由 SQLite 重建 `-shm`，会读取 WAL 已提交事实。原生沿同一只读 SQLite 连接处理，保持主库及 WAL 的原身份和内容代，禁止 checkpoint、事务写入与自建数据库，仅允许原 SQLite 为已有 WAL 恢复派生共享内存索引。原 WAL 或文件代变化、索引异常与无法重建均失败，本地原记录保全。正常已有索引的读取仍需验证文件字节不变。使用原路径稳定开关与旧端相同的 SQLite 恢复，不另存数据副本或增加执行能力。

## 2026-11-17 NR-04 Qoder 本地凭据与目录格式原生化（A，实施前登记）

沿ADR129的Qoder完整迁移范围及本ADR的Provider encoder/credential seam，先替换现有`qoder-local-auth.mjs`依赖官方程序内嵌WASM的本地解封和model-cache算法。最终CLI使用RustCrypto执行相同密码原语，不启动qodercli/Bun/Node，不嵌入WASM VM或捆绑官方SDK二进制；官方模块只在隔离开发夹具中作为互操作oracle。这里不声称Qoder原生请求/认证/队列/工具闭环已经完成，也不能以本Module替代整条Provider验收。

核对对象固定为当前TS实际引用的兼容版本1.0.39；由官方文档指向的`@qoder-ai/qodercli@1.0.39`公开npm包提取认证模块，仅作有来源/hash/包integrity记录的合成对照，不安装/运行官方CLI或读取个人登录数据。`credential_storage_decrypt`格式是标准base64、AES-128-CBC、PKCS#7，16字节UTF-8 key同时作为IV；保持已有格式，不把其称为具备认证的新加密方案。`model_cache_decrypt`新格式为base64(`QMC\x01` + 12字节nonce + AES-256-GCM ciphertext/tag)，HKDF-SHA256以实际uid字节为IKM，salt=`qoder-model-cache-enc`、info=`model-cache-v1`、32字节输出。旧目录格式与未知/损坏数据必须通过真实官方样本和当前TS调用点再确定，不能猜成功或悄悄清空目录。未确认格式明确阻断且保留原文件；v1 helper不接管第三方账户事实。

原生密码Module对编码、密钥、密文/明文长度、GCM tag、CBC块/填充及UTF-8作严格校验，限制单份本地凭据1MiB、目录4MiB及调用方更小预算。边界先检查、运算后再检查；不把异常异常文本、明文、key或ciphertext写入错误/日志。解封缓冲归唯一owner并在释放时零化，算法使用维护中的RustCrypto crate，不自写AES/GCM/HKDF或引入JavaScript执行路径。CBC既有格式不能证明内容真实性，后续Qoder身份、expiry、字段类型与配置绑定仍由Credential Adapter验证；解密成功不生成工具许可或账户在线事实。

后续文件Adapter沿现有`QODER_CONFIG_DIR` / `QODER_CLI_HOME` / HOME解析来源，第三方`.auth/user`、machine_id和目录只读，禁止通过host Node绕过EACCES/EPERM，不写入第三方凭据/刷新或创建新真源。路径、非普通文件、读取大小、取消及读前/后文件身份须有界核对；变化拒绝当前请求并支持修正后的显式重试。Qoder外部登录仍由其账户所有者管理，不借本卡新增Peer登录/自动安装或重启第三方程序。原生模型装配必须绑定明确选中的Qoder渠道及真实凭据来源，每次真正发送前复核，不能把本地文件存在当Grant、Evidence或远端登录成功。

验收先以官方模块和当前TS生成合成Unicode/空值/边界/坏key及旧/新cache样本，再跑Rust双向/固定样本、GCM篡改/CBC填充/UTF8/预算否决及源字节保全。原生完整模型→工具→Grant/Evidence、实际第三方登录/目录和安装多平台仍独立验收；本补充不开放任何工具或System Context来源，不改变canonical恢复和unknown规则。

来源：`https://docs.qoder.com/cli/authentication`、`https://docs.qoder.com/cli/installation`（2026-11-17核对；官方安装文档仍列出npm包）；实际TS `packages/runtime-node/src/provider-adapters/qoder-local-auth.mjs` 与 `qoder-model-catalog.mjs` 是迁移行为的对照，公开新版文档不覆盖本仓已存在的本地格式/权限契约。

2026-11-17 同卡补充：官方Module合成对照确认目录兼容非base64文本原样返回，以及标准base64无`QMC\x01` magic时按UTF-8返回解码文本。二者均须由调用方按原catalog schema校验，不产生已认证事实；空输入、无效UTF-8和损坏GCM tag失败保全。请求body按固定64字符表作base64位分组，使用`$` padding，再交换首/尾floor(n/3)区段。这只是传输混淆，仍须HTTPS、真实凭据与配置绑定。原生实现沿字节预算拒绝超限、坏字符、残片或非canonical padding；charset和合成向量由官方Module提供，消息形态由实际TS builder对照。完整Provider装配、网络、取消与工具闭环另验。

### 2026-11-17 Qoder 原生账户与模型 Host 接线（A，实施前补充）

沿同一Model factory/encoder/Native Network接入`qoder-private`与显式`qoder_local_auth`（现有`local_cli`别名同义）。账户来源是Qoder所有的本地登录文件；不启动第三方CLI、不自行刷新/写回第三方账户，不借API-key或旧JS sidecar填充缺口。沿已有QODER_CONFIG_DIR→QODER_CLI_HOME/.qoder→HOME/.qoder解析；环境token的既有优先级只属于显式Qoder来源，不能流入其它Provider。准备后的账户绑定当前选定channel/model的operational配置和真实来源文件身份，每次物理HTTP发送前重查取消、expiry、配置及凭据身份；晚到换号/退出/禁用使旧实例拒绝，不缓存grant或以目录存在充作在线账户。

文件读取对最终文件NOFOLLOW/NONBLOCK，只接受普通文件；路径别名可通过显式根目录解析，不使用host Node绕过权限。机器标识至多4KiB，user密文至多1MiB，索引/目录沿前述4MiB及有界JSON节点/深度限制。读前lstat→open/fstat→有界分块读取→fd/path再核对dev/inode/size/mtime/ctime；连续追加不扩大已捕获读取窗口，取消/坏UTF8/不可读/未来格式明确失败并保留源。已有加密文件仍以trim后的machine_id前16个JS字符取16字节CBC key；不合字节预算/不完整Unicode边界拒绝。实际token、uid、expiry与字段类型由Credential Adapter校验；账户JSON及应用持有的字符串副本在owner结束时零化。可选metadata不产生授权或Evidence。

保留官方兼容版本1.0.39的认证封装：已有encrypt_user_info/key均在时复用；缺少任一时，以OS随机UUID去连字符后的前16个ASCII字符为新key，对现有uid及实际存在的organization_id/organization_tags/data_policy_agreed按原TS顺序序列化，用AES-128-CBC/PKCS7（IV=key）加密，并以官方固定RSA1024公钥及PKCS#1 v1.5加密该key。使用维护中的RustCrypto公钥加密API，生产不允许外部seed/私钥或任意公钥覆盖，不自写密码算法。它只是已有第三方线协议兼容，不改变Peer Vault格式或工具许可。

COSY envelope使用每次认证准备独立生成的OS随机UUID作为requestId（官方模块不复用正文request_id；二者不代表工具执行身份）、encrypt_user_info、固定cosyVersion和空ideVersion。base64 envelope、Cosy-Key、当次epoch秒、**实际编码后的body**、固定API路径按换行连接计算现有MD5兼容摘要；URL的/algo前缀与查询不进入该API路径。签名/弱旧密码格式不作为Peer授权或安全设计范本。固定字段和合成随机源样本必须与未修改官方模块逐字段对照；源码测试才可注入合成随机源，featureless产物不读取fixture开关。

认证header只由账户Adapter产生并标记sensitive；自定义header不能覆盖Cosy身份、机器、日期、key或Authorization。当前2MiB prepared-request总上限保留，body先由Qoder专用encoder从同一canonical history和Projection生成，再编码成冻结原字节/指纹。它不拼接新System Context，不改变源历史或ToolResult/Evidence。工具配对、相邻assistant合并、双content/contents、工具schema、effort/context档位沿实际TS规则对照。Qoder使用observed-only计数；用量/未知收费仍归原Runtime账本，编码大小不当token容量。

普通发送走同一Native Network代理/TLS/证书/redirect和取消边界；Stream decoder复用经过Qoder业务错误/帧形态适配的现有Chat归一化，只有真实完整终态才公开工具intent。网络错误、队列/重试、部分usage和已发请求不因认证换代被清成未发送，不重放本地工具。完整目录、队列/连接重试及真实服务另按既有TS预算逐项验证；首条正常模型/工具闭环不能替代整个Qoder/P4总闸。

以真实CLI、隔离第三方文件、合成TLS/HTTP模型、当前TS与官方模块验证正常/缺字段生成、坏/过期/换代凭据、坏/超限/FIFO/取消文件、禁用/改选配置、代理/TLS、错误/截断/取消流、真实工具Grant/Evidence、后续任务及原unknown保全。来源、写域、授权与Evidence边界继续沿原主链，P5–P7不因本卡自动完成。


### 2026-11-17 Qoder 旧私有端点与环境凭据（A，实施前补充）

按现有TS分支选择Qoder方言：当前目录命中所选模型，或配置有非空modelOptions时，使用已登记的准备端点；其它模型使用旧/model/v1/chat/completions的JSON/Bearer方言。此选择只由同一ModelBinding、只读目录和已有配置派生，不增加用户可写的方言开关，也不在HTTP/认证/目录解析失败后降级为另一方言。坏/未来/身份冲突的目录继续明确失败，不能伪装成“目录没有该模型”。配置的空modelOptions数组仍是显式覆盖；null按未声明处理。

Qoder三个环境token保持QODER_ACCESS_TOKEN→QODER_PERSONAL_ACCESS_TOKEN→QODER_PAT的trim后非空优先级。环境来源获胜时不读取.auth/user或machine_id，也不借另一磁盘账户补资料：目录选择准备端点则报qoder_local_user_info_required；旧方言则仅在该Qoder模型/配置绑定下使用该环境token。无环境token时，继续只读解封既有本地文件，验证token/expiry；旧Bearer方言不要求准备端点独有uid或加密封装字段，但已有字段仍按原有类型/大小限制验证。准备端点继续要求有效uid，并沿上一条生成/复用封装。两种来源和方言均不得自行登录/刷新/写回第三方数据。

旧端点优先使用已有显式baseUrl。未配置时，沿QODER_MODEL_SERVER_HOST或QODER_ENV/ENVIRONMENT的prod/daily/test既有默认主机选择，严格通过同一URL、Native Network、代理/TLS、redirect和取消政策；环境主机不能覆盖显式配置。正文保留原messages/tools/max_tokens及metadata.context请求/会话标识，直接发送冻结JSON字节而不是准备端点的混淆载体。Authorization、X-Request-ID、X-Session-ID只由Adapter产生并保护，外层/内层业务失败规则相同，只有完整终态才公开工具intent。

来源读取的存在与缺失观察集中为同一有界read set；credentials/catalog/endpoint均沿前述普通文件与有限快照规则。每次物理发送前重查该集合、当前环境、expiry和ModelBinding；目录出现/变化导致方言选择失效时，旧实例拒绝而不换token或自动重放。后续新实例可按实际修复后的来源重建，既有unknown、费用、工具效果、权限和Evidence不清除。此集中不新增持久化源、授权事实或恢复捷径。

以当前TS请求/headers/方言选择对照及真实公开CLI验证两个方言的账户来源、优先级、正常工具链、拒绝、损坏、过期、换代、目录出现/配置变更、取消和后续任务。环境令牌不能进入其它Provider或日志。队列/连接重试及全部目录/流变体、真实服务和P4总闸仍须另验，不由本条接受或首环测试代替。

### 2026-11-17 Qoder 逐尝试重试、身份与计费（A，实施前补充）

原生Qoder沿当前TS的有界策略：10605队列至多40次等待、累计等待600000ms、单次50–60000ms，retryAfterSeconds优先于waitTime秒/estimatedWaitMs估计；估计至多作15000ms基础，再加min(attempt,3)*2000ms。剩余预算不足50ms时直接结束，不因下限突破总预算。103重复只重试一次、2000ms；其它已分类限流/瞬态失败按1000/2000/4000ms；收到响应前的连接失败按1000/3000ms，耗尽后进入同一外层瞬态预算，每次外层重试重置连接轮次。累计等待不是端到端耗时；每次HTTP仍受原有deadline与Host预算约束。取消、鉴权/配置/来源变化、上下文溢出、超限、非法流、缺终态和读空闲超时不自动重试；上下文溢出继续归既有压缩路径。两种Qoder方言共享该策略，其它Provider不借本条新增重试。

重试以同一冻结的非身份正文为种子，只重建request/session/task标识、准备端点is_retry与实际编码字节/指纹；首次真实runtime task_id也用peer-agent:UUID，纯builder固定向量保留原默认值。每次认证仍从实际body重新生成并复核同一只读账户、环境、ModelBinding和Native Network。拒绝后不能换号、换方言或重放本地工具。分类只保留有界枚举/数值，不保留上游错误正文、秘密或部分工具intent。

重试协调归现有Host请求生命周期，不能藏进网络层后只记最终一次。沿ADR25：每个已准入发送尝试都增加canonical modelRequests和providerRequestCount；失败的已知usage先进入同一budget/nativeUsageSnapshot，未知usage继续标unknown。费用/容量观察在策略等待前结算，晚到收费先保存事实再处理租约丢失。后续每次尝试前及等待后重新核对执行权、取消、Goal/MCP身份、预算与历史sourceRevision；maxTokens/maxCost的未知阻断不得绕过。等待由同一owned cancellation/heartbeat包裹；无独立后台请求、无持久重试队列，进程重启不自动续发旧模型请求。摘要请求沿同一逐次计费但capacityBearing=false；容量不能被摘要或累计费用替代。

验收须包括实际TS分类/等待向量、真实公开CLI两方言队列/重复/HTTP限流/连接恢复与耗尽、逐次新身份/指纹和非身份正文不变、失败usage累积、预算阻断、等待取消与凭据/历史变化拒绝、已有工具不重放、硬退出后known/unknown保全和后续任务。只用隔离合成服务/账户；真实服务、P4完整总闸和P5–P7仍另验。


### 2026-11-17 NR-04 原生文件能力与有界扫描（A，实施前登记）

沿ADR49/92/101/129–130迁移既有read/list/search/write/edit五个文件能力，名称/schema/mode来自当前TS Manifest和local-tool-contracts；不是新增权限种类。Provider内部按操作分工，Host从实际Provider投影核对required capability，不继续手写已支持能力白名单。所有操作仍由原Grant/Goal/role/policy/lease/取消和Evidence链约束。编辑复用同一Provider读取快照及文件claim；未读取、已改变、匹配不存在/歧义均不写，实际写入前重新检查原输入绑定的授权和文件内容。未知写入沿原dispatch/unknown恢复，不因新工具名重放；新模块不恢复任意旧未知效果。

文件操作在单个受管阻塞任务中执行，Host继续服务取消/授权复核/heartbeat；任务返回或确认结束前不能释放其执行所有权。复用有界EffectAdmission控制通道，阻塞任务通过原Host实时复核，不复制Grant或创建后台独立执行链。普通文件读取使用非阻塞打开及类型检查，FIFO/设备不按普通文件读取。保留当前原生read128KiB/write32KiB预算；大正文/artifact完整迁移仍为P4余项，不能因本条将原CLI较大文件能力算完整完成。

list/search的v1扫描集合同时限16384项、路径UTF-8合计4MiB；单文件search读取最多1000000 bytes（沿原TS上限）、结果最多200行，序列化结果最多256KiB。每步检查取消；预算耗尽返回明确file_collection_limit/file_result_limit，不以部分输出冒充完整目录或悄悄降低max_results。搜索保持原TS忽略.git/node_modules、非递归跟随目录symlink、按UTF-16完整路径排序、CRLF/缺省大小写/结果上限及truncated语义；文件正常不可读可按原算法跳过，取消/总体预算错误不得被跳过逻辑吞掉。list仅直接子项，保留file/directory/other事实。

目录排序与locale search使用原生ICU4X 2.1.1（MSRV1.83；不增加JS/WASM VM），复核当前TS默认locale的环境优先级和en-US默认值，以实际跨语言locale向量验收。具体依赖锁、未知locale回退、Unicode比较和展开不得靠ASCII替代或只测英文。版本/平台数据差异明确报告；没有跨平台证明时不称全平价。参考[Collator2.1.1](https://docs.rs/icu_collator/2.1.1/icu_collator/struct.Collator.html)、[CaseMapper2.1.1](https://docs.rs/icu_casemap/2.1.1/icu_casemap/struct.CaseMapper.html)。

公开原生CLI须覆盖真实列举→搜索→读取→编辑→读取、项目外路径沿原Goal/claim约束、未读/外部改动/歧义、拒绝/降权/取消、特殊文件/扫描超限、写后硬退出/unknown保全和后续任务。实际TS Provider对照与Host授权测试分开；本条登记不代表实现或P4总闸通过。


### 2026-11-17 NR-04 不可变工具结果快照与大文件（A，实施前登记）

沿ADR51/57/63/86/98/129–130，新增Conversation Store内部ToolArtifactStore，位置为已登记conversations目录下`<conversationId>.tool-results/`。它保存原工具观察的完整不可变正文，是canonical Tool Result的内容引用，不是用户交付物、缓存、权限记录、另一套对话真源或System Context来源。现有`artifacts/`缓存及其LRU不管理此目录；不得为准入新结果自动删除旧依据。conversations数据项注释登记该子格式；复制/删除/恢复兼容须逐项验证，不由目录存在推断迁移已完成。

v1引用为`{schemaVersion:1,conversationId,sha256,bytes,format:"utf8"|"json"}`；受信Store按当前home和严格id/摘要推导路径，不接受引用中的任意路径作为存储目标。完整数据按SHA256内容寻址、只写一次、0600文件/0700目录；同摘要再次写入必须核验已有字节，损坏/冲突保全并拒绝。临时文件独占创建、写入/限额/取消/哈希、fsync、无覆盖发布和目录fsync后才返回引用；发布后确认丢失报commit_unknown，按实际同摘要对象核对，不重放工具。使用目录OS advisory锁串行配额/发布，进程死亡自动释放；不增加可被TTL擅自清除的孤锁。未发布临时残留不成为正文，保全并计入磁盘准入，不因恢复而删未知内容。

单快照128MiB、单会话256MiB、4096个文件项，目录/文件名观察另限4MiB；写入和校验流式使用64KiB块。超额/磁盘满/只读/损坏返回结构化存储失败，不编造成功引用、不退回无限内存，也不删除已确认事实。内部读取按同一引用核验格式/字节/完整SHA和文件版本后给出有界窗口，范围读取不能把窗口冒充完整正文。旧引用缺失/损坏保留明确状态，不能读取当前工作区或自动重跑原命令代替。

Host在canonical结果提交前，将超过6000 UTF-16单位的结构化输出外置；文件读取原文用utf8格式，保留原path/bytes/contentHash及截断标记；其余输出保存完整JSON。canonical结果沿已有`local_file_ref`/`local_tool_result_ref`和可选`nativeContentRef`表达预览/回读路径，原ToolCall、Grant、状态、错误及Evidence元数据不被预览替代。预览至多1200 UTF-16单位，完整Unicode字符边界及真实总量保持；模型副本不得把预览称作全文。Store失败发生于工具之后时保留原pending/unknown恢复边界，不把实际副作用当未派发；已有不可读大历史单列恢复限制，不猜写旧数据。

本条局部修订前节文件预算：原生read上限对齐现TS的2000000 bytes；write/edit结果上限128KiB，仍受工具参数JSON/权限摘要1MiB等复合准入约束，超限必须在效果前拒绝。模型工具参数上限由64KiB提高至1MiB；SSE单事件1MiB/响应累计8MiB、32调用及既有64MiB组装预算保持，不接受部分参数生成Grant。write/edit的全量旧CLI极端输入平价仍须随整体资源预算验证，不能仅提高常量宣称全部完成。v2文件/引用资源登记在packages/protocol，TS/Rust差分和真实公开Host正常/拒绝/取消/崩溃/回读/后续任务必须绑定最终源码。

Provider model-facing结果编码沿现有encoder seam：file/shell/ref保持现TS字段和检索语义；原canonical事实不被模型预览覆写。live continuation先按原canonical身份核验，再编码模型副本；count和send消费同一冻结编码体。压缩及旧记录同样不能绕过原History/权限/预算边界。完整generic/旧超限历史、生命周期级联、混合旧安装版本、真实平台和P4总闸另验。

#### 2026-11-17 不可变结果的受管回读（A，接线前补充）

原生快照不能仅给出无法验证的路径。以同一Capability Provider链登记`local.tool-result.read`（模型别名`read_tool_result`），Manifest/schema纳入native-cli/tool-artifacts资源；它接受严格nativeContentRef、字节offset和至多256KiB的length，不接受home/任意文件路径。Provider从实际Host PermissionGrant绑定conversationId，必须与引用相同，不能借模型输入选择其它会话。沿既有Read授权类别及Goal/role/lease/policy实时复核，仍产生ToolCall/Grant/Evidence；不增加另一执行通道、文件写权限或System Context来源。完整正文先通过Store全量摘要/版本校验，再返回窗口。UTF-8起点不合法则明确拒绝，末尾不完整字符可缩短至完整边界并返回真实offset/bytes/totalBytes/complete，不能替代原快照。回读失败不读取当前工作区、不重放原工具。

Host外置任务由原owned等待与取消/heartbeat包裹，受管阻塞任务结束后才释放所有权；归档失败时保留原dispatch预算pending，不能提交虚假成功。回读的较大窗口亦可按原同一快照外置规则保存，原引用/offset元数据保存在不可变JSON中。此新能力仅为已保存结果检索，不表示完整Context、大历史分页或原文件工具极端输入平价已经完成。

2026-11-17 实施复核（B，既有边界不变）：回读窗口必须携带并复核全文哈希实际使用的文件版本，不能在哈希后重取版本而把中途篡改当作有效快照。归档类型由可信Provider的PreparedEffect Interface声明（缺省结构化JSON、真实File Read声明文件正文），Host不增加capabilityId分支，也不从MCP payload的文件状字段推断并丢失其它原始事实。反例、修正和各源码验证范围分别绑定，见实施账本；本补充不是P4总闸或发布验收。

### 2026-11-17 NR-04 模型侧结果编码与历史观察材料化（A，实施前登记）

沿ADR57/63/129–130迁移现TS tool-result-encoder seam，显式区分canonical Tool Result和只供模型请求使用的结果视图。Canonical Projector、ToolCall/Grant/Evidence、原正文与既有unknown不由视图改写；generic只选已知status/output/error及受治理Evidence引用，file/shell/local_*_ref按已登记结构编码。Evidence引用只收集真实Tool Result已知字段，不扫描output或URI文本创造事实。未知/纯文本旧观察保留为只读事实，不解释成新工具执行。模型视图不是第二份持久历史或System Context来源。

原始消息身份先进入既有LiveHistory精确匹配，随后才对模型副本的tool content应用编码。编码覆盖以tool id/name/原正文绑定，变化或丢配对明确失败；不能用预览参与原始续行身份校验，也不能在不匹配时注入旧签名/thinking。Provider encoder最终冻结一次wire正文，count与每次实际send沿同一冻结字节；Qoder只沿既有身份重试。普通NativeModel准备为纯编码；需要材料化却未提供受管Store时明确返回materialization_required，不隐式读取用户home或落入JS缓存。

Host在其已有可读历史范围内，从原已保存观察派生不可变内容快照。仅模型副本引用该快照，原canonical正文保持；这不是重新读取工作区、重放原工具、补写旧费用/许可或宣称旧任务成功。复用ToolArtifactStore的完整校验、配额、无覆盖发布、取消与部分残留规则；owned阻塞任务结束前不释放所有权，期间继续heartbeat/取消。材料化后、任何计数/发送前重新核对权限/Goal/MCP与实际历史sourceRevision；变化则阻断。缺失/损坏/超额/未来历史不猜写修复。8MiB之外的旧历史分页/恢复仍另验，不用本条缩小完整迁移范围。

编码源与视图合计限16MiB，单个模型结果视图限64KiB，原结果JSON读取沿既有1MiB/深度/节点预算；压力为明确encoding_limit/materialization_required而非丢字段或截断成功。新工具结果仍先按前条6000 UTF-16规则保存，旧可读大观察和任何会丢正文的shell预览先材料化。完整正文按原已保存payload保留；没有原完整内容的provider-truncated观察只记录当时片段与truncated事实，不从当前文件补齐。

局部收紧现TS视图：仅真实文件工具的文件观察采用file视图，MCP文件状payload保持结构化JSON及额外字段；shell保留独立stderr预览/长度，实际失败/取消/拒绝/unknown通过resultStatus/resultError明确携带，不能因现TS缺省completed或既有local ref而藏掉外层错误。预览计数用UTF-16单位但不拆完整Unicode字符。上述是原生字段/保真补充，实际TS基线与原生差异逐项登记在共享资源，不称字节全平价。受治理Evidence字段仍不由模型或payload升级。

压缩的事实输入采用同一受管结果视图，保留快照回读路线和原canonical/marker选择、CAS、计费、取消与known/unknown边界；摘要文本仍是连续性上下文，不能代替Tool Result/Evidence或创建授权。整体验证包括实际TS编码向量、真实公开Host小文件/shell/generic/ref、旧正文材料化与当前工作区变化、活跃续行签名、同请求count/send、摘要重建、拒绝/损坏/取消/历史变化和后续任务。真实模型、完整大历史/其它Context策略、快照生命周期与P4总闸继续另验。

2026-11-17 模型视图实施复核（B）：已保存文件范围观察的start_line/end_line/total_lines继续随模型副本保留，明确这是完整所选范围而不是整文件；不改变查询、原内容哈希、原字节计量、Grant或Evidence。现TS缺少该说明的视图作为基线保留，以显式原生保真差异验证。

2026-11-17 形态判别补充（A，接入前）：同一保真约束也适用于shell形态MCP payload。只有真实shell工具的观察使用shell预览；其它Provider返回的stdout/command字段仍是其结构化数据，不因形似shell而丢失其它字段或暗示执行了本地shell。实际capability事实优先于历史别名，权限/Evidence链不由此推断。

2026-11-17 显式错误保真复核（B）：若历史外层status为success/completed但仍含非空error，专用模型引用视图也保留原resultStatus与resultError；不得按状态标签删除已知错误，也不得把原成功标签改成推断失败。该反例属于既有外层错误保真要求，不改变canonical/权限/Evidence或执行状态。

### 2026-11-17 NR-04 缺失父目录的受管文件写入（A，实施前登记）

沿ADR49/51/92/101/129–130迁移当前TS write_file的recursive mkdir行为；仍是local.file.write同一次调用的准备性文件效果，不增加独立mkdir工具、权限类别或执行通道。路径先按现有绝对/相对语义规范化，再绑定现存祖先和缺失后缀；不在prepare或拒绝/审批等待期间创建任何目录。其它read/list/search/edit及shell cwd不借本卡自动创建目录。

Provider对目标file保留原resource scope，并在确有缺失父目录时保守预留最近现存祖先directory scope，避免以尚不存在的目录身份自证所有权。该目录claim只协调/保护本次准备效果，不扩大Goal/角色/当前PermissionGrant；现存祖先身份须持续匹配。其同一执行若未知，将连同原file claim保留保护；正常成功沿原停稳/结算释放，不引入目录materialization真值或私有恢复表。现有目标file的materialization仍须真实成功结果/Evidence后按原Host条件提交。

受管阻塞任务持有目录FD，从根逐段openat且NOFOLLOW，实际mkdirat、目标openat/write/fsync前沿现有EffectAdmission重检当前授权/取消，并复核命名路径与受控FD身份。对执行中新增的symlink/目录替换明确拒绝；不跟随替换后的路径写出。已有合法symlink先解析到其真实目标，保留既有跨工作区路径政策。文件数据和父目录flush按原耐久约定；新目录也需确认其父目录发布。文件内容/参数预算不放宽。缺失父目录最多128层，路径继续受原资源scope的8192 bytes及文件工具路径预算约束；超限在任何效果前明确file_parent_limit。

第一次成功mkdir或CREATE已是效果；后续取消、降权、命名变化、I/O失败或无法确认发布均保留部分目录/文件并返回execution_outcome_unknown，不能删除以制造未执行，不自动续写或重放。任何效果之前的拒绝/取消沿原明确失败/取消；restart/recover只观察、保留未知及其范围，再允许无冲突的后续工作。旧unknown不会被本实现自动结清。

验收绑定实际TS Provider生成的合成路径/内容/拒绝向量、原生公开write→read与Grant/Evidence、审批拒绝不创建、真实目录FD/替换、创建前后降权/取消、层数限额、硬退出后unknown保全/recover不重放及独立任务。完整P4、极端输入、真实服务/安装版本与P5–P7另验，不据本条宣称完成迁移。

2026-11-17 父目录实施复核（B，沿ADR127 §5.1/5.7既有边界）：dispatch声明只在全部scope都可由原file/git_ref/remote_object语法表达时发布；含directory的文件准备效果保持undeclared/conservative，不能过滤掉directory而伪造成单file声明，再错误收窄unknown保护。原生此卡仅能表达file，故有任一非file就不发布declaredScopes；TS沿原规则。实际目录副作用/重启反例与修正分别保留，不扩展声明语法或重写旧unknown。现有原生Provider对已解析alias输出canonical相对路径，按ADR51允许宿主输出差异逐项登记；TS原期望不改写。

### 2026-11-17 NR-04 已保存用户附件的原生模型准入（A，实施前登记）

沿ADR55/57/90/129–130，解除NativeModel对canonical user内容数组的临时总拒绝；已由原Projector投影的text/image_url仍是用户事实，经原provider encoder、同一PreparedRequest/count/send及既有请求预算进入模型，不成为System Context指令、Tool Result、PermissionGrant或已看图/已验收Evidence。原始attachments/images、message id、历史选择/原正文与unknown不因准入改写；压缩后重建继续以同一canonical选择为准。

增加纯内存的已保存用户图片传输准入：仅user内容数组中的已知text/image_url分片；图片URI只允许data:image或HTTP(S)，本机路径、file/其它scheme不得触发任何读取或抓取。Native CLI不会为URL下载图片，也不把保存的上传附件当作local.image.read授权。data base64做有界语法校验，非base64形式只在原encoder可表达时准入。Anthropic/Gemini当前encoder不能表达的远程URL/数据形式，在count/send之前明确model_image_transport_unsupported；不得静默丢图片，亦不自动切provider。其它wire保留原URL分片。坏类型/坏数据明确model_image_invalid；原2MiB请求预算与8MiB历史读取预算不抬高，压力在网络前拒绝。不引入图片长期cache、文件副本、私有模型通道或新Source。

该准入只约束canonical用户输入；authentic thinking/tool-use续行仍在原LiveHistory身份校验后由可信运行时注入，不能借用户数组提升为provider原生控制块。实际TS wire/projector向量作为编码基线，无法表达图片时的原静默省略作为显式原生安全差异保留。迁移不复制旧丢图行为。

验收包含现存公开候选的失败基线、四个标准wire与Qoder两方言的实际请求像素/URL字节和工具/Evidence闭环、同一图片count/send、取消/超限/不可表达时零网络、历史/原附件保全、显式模型切换恢复及后续独立任务，以及压缩后冷重建保留当前图片。仅合成附件/模型服务；不把传输断言称真实模型看图结论。local.image.read Provider/受信视觉侧带、附件输入/生命周期、其它Context目录/策略及P4总闸/P5–P7继续须完整迁移。

2026-11-17 附件实施补充（A，接线前）：实际压力反例显示Canonical Projector复用permission_digest的1MiB序列化上限，使已可读取的合法事实历史在2MiB模型请求闸前提前失败。为事实上下文增加显式有界的同一JS序列化Interface，调用者预算至多8MiB；Canonical Projector的输入检查和展开/fingerprint沿已有8MiB历史边界，深度64、JS排序/数值/escaping算法不变。approval_args_digest、permission_operation_key、control/javascript_json_digest及默认javascript_json_string继续固定1MiB，不能通过新上下文API放宽Grant参数或更换授权摘要。共享资源记录不同预算；以实际TS大事实序列化对照和原授权/escaped大小拒绝断言验证。不修改模型2MiB请求上限、不把过大输入截成成功。

同日B级准入排序：对首次已保存历史做纯图片传输预检，在reserve/activate、ready→started和attempt创建之前拒绝已知无法发送的内容；实际请求前仍重检当前历史。预检不签发Grant、不落执行成功或删除输入，不恢复旧started/unknown。这样新的未开始任务可在用户显式改变模型后以原输入/身份继续；旧候选已经started的失败仍需原recover/新准入，完整resume属P5继续迁移，不能静默清control或重放工具。

### 2026-11-17 NR-04 CLI 实际可达集校正（A，实施前）

原生迁移按ADR129的CLI产品执行栈与方案§6实际argv/registry可达集验收，不把共享runtime-node可导出的所有Desktop能力自动变成CLI新增能力。实际bc734878的createTuiHost在8种既有mode的隔离投影均不含local.image.read/view_image；createNodeProviderBundle未装配LocalImageProvider，tui-project-host仅注入project/interactive Provider；LOCAL_IMAGE_TOOL_DEFINITIONS和真实解码器仅由Desktop装配。CLI中的图片授权适配本身不是工具可达证据。

因此，前节“已保存用户附件”末段将local.image.read Provider/可信视觉侧带作为CLI必迁余项的措辞在此被替代：保持Desktop ADR90及共享协议不变，不能凭迁移授权在默认CLI注册一项过去不可达的工具。原CLI图片路径/用户附件准入、Provider支持的图片发送、恢复和完整附件生命周期仍必须迁移；经已有受支持扩展路径提供的工具仍按该路径迁移，不凭符号导出宣称支持。此前状态记录作为范围判断错误保留，不能改写为已经迁移完成。真实旧CLI投影清单与源码锚点记入native-cli回执。

### 2026-11-18 NR-04 用户显式选择本地图片（A，输入接线前）

沿 ADR55、57、90、129–131 和原 TUI Composer。旧 Composer 明确选择本地图片后将数据写入用户消息的 `attachments`；旧普通 `exec` 与 ACP 都接收文本。新增原生普通 `exec --image <path>` 作为同一输入接缝的显式调用，参数可重复并支持只发送图片。旧文本命令不扫描路径，ACP 保持原来的文本协商。后续 Ratatui 草稿和粘贴使用同一 Host 输入接口，保留选择、移除与原草稿回执。

仅人选择的文件进入该接缝。相对路径按本次 workspace 解析，文件路径不得来自模型、附件正文或远程 URI。绑定已打开的本地普通文件，采用有界读取、取消和文件变化复核。拒绝特殊文件、超限、空文件及明显不符的图片格式，不执行解释器或解码高膨胀像素。读取选中的文件不建立目录授权、模型可见的本地读取工具或 Tool Result Evidence。

用户消息只保存已有 Desktop 可读的图片附件对象、数据和有界展示名。绝对路径不写入模型请求、System Context 或结果。已有 canonical history 和 NativeModel 负责传输预检与原请求预算。无法读取、无法表达和超限须显式失败，原文件不改写。附件计入既有 2 MiB 请求闸，不引入常驻缓存或重复副本。公开验收包含同名路径、规范化格式、大小和非普通文件、原文件/消息事实保全、仅图片的真实模型请求、原服务的工具续行及后续冷读。长期附件视图、剪贴板和四小时门禁继续按 P6。

### 2026-11-17 NR-04 原生批量文件搜索（A，实施前登记）

迁移旧CLI实际投影的batch_search/local.search.aggregate，作为同一文件能力域内的独立Provider Adapter，复用既有有界文件扫描、locale排序/大小写、EffectAdmission和Host权限链，不执行Shell、不新增系统上下文来源或私有状态。1–8个lane；保持原id/label/query/path规范化、重复id拒绝、max_results 1–200、dedupe、lane输入顺序、命中计数/排序、500 aggregate上限及原先“先遇cap即返回、未排序”的截断语义。正常结果和全失败/部分失败事实与真实TS Provider对照，平台错误信息使用已登记稳定原生码，不能把失败lane丢失成全成功。

max_concurrency是1–8的请求上界（默认4），不是保证实际同时启动的数量。原生有界调度至多两个阻塞扫描worker；多lane排队并遵循请求上界。每个worker复用原16384项/4MiB路径、1,000,000字节单文件、256KiB lane结果限制；最多8份lane结果合计2MiB，aggregate最多500条，最终结构化JSON另限4MiB。排队参数仍受原1MiB工具参数/权限摘要闸。该资源策略不降低8-lane契约、不截短query或把预算错误当完整结果，不改ADR130整体RSS/响应性验收门槛；完整P5并行Runtime仍须全局池与内存验收。

整个批次只有一次真实Tool Call/Grant/Evidence。每次实际读取沿原控制端口复核；worker在取消/降权/Host停稳时停止新读取，全部已启动worker结束前不释放批次所有权。普通lane失败保留其它已完成观察及partial；控制取消/授权失效必须明确结算且保留已观察lane事实，不把仍在工作的线程标成停止，不重放已有搜索。结果归档仍走原不可变Tool Result路径，不新建缓存或持久化源。验收需实际TS向量、公开原生模型→批次→结果/Evidence→模型、并行上界、审批拒绝、执行中取消/降权/心跳、预算超额、后续任务及冷读互操作；P4总闸和P5–P7另验。

2026-11-17 批量搜索实施复核（B，既有授权/unknown边界不变）：原TS批次Provider会按全lane失败反写deny式grant；原生保持实际已签发的Grant事实，失败不倒改过去的授权，Tool Result/Evidence单独记录全失败/partial。TS原grant字段保留在对照资源，作为显式事实保真差异。硬退出后的undeclared批次继续沿ADR127保守命名空间保护，不能把同目录新任务ID称作“独立资源”并要求放行；验收须保留同范围阻止，实际独立目录可准入且原unknown未变化。此复核不新增声明语法、未知自动关闭或执行重放。

2026-11-17 批次整闸失败调查（B，控制调度修正前）：5bf5543d冻结门禁在两项取消场景的原8秒整CLI退出断言失败，失败候选、原数据和被测试owner清理前的限制保留，不称flake。多worker可持续填满既有EffectAdmission控制通道；每次就绪消息同步校验会在current-thread Runtime中连续占用一个调度预算，存在取消监听被饿死的路径。按原控制优先契约增加每次控制校验前的明确调度让步，并在让步后先传播外部取消、再以当前真源校验请求；不丢弃控制消息、不放宽Grant、不跳过真实worker等待。先用仅fixture编译的受控慢校验、真实公开命令/信号和原8秒界限建立红例，再验证修正及完整整闸。调查阶段不把假设称已验证根因；P4/P6响应性总体验收不由该专项替代。

### 2026-11-17 NR-04 原生静态 HTTP fetch 与网页产物（A，实施前登记）

沿ADR55/57/98/101/129–130迁移旧CLI真实可达的web_fetch/local.web.fetch；旧Node Provider/engine/ArtifactStore是行为对照。ADR38仍Proposed，不在本次借迁移接受其搜索/Browser设计；ADR72的Desktop浏览器边界不变。仅静态HTTP(S)，waitForRender仍是兼容参数，rendered=false；不加载JS、浏览器登录态、模型凭据或Cookie，不新增默认浏览器工具或系统上下文Source。网页正文/title/URL是事实Tool Result和artifact内容，不能成为System Context指令、授权或模型已经核验的Evidence。

独立Provider Adapter经原Manifest/Projection/一次Grant/Evidence，按原web-fetch自动批准语义：Full沿当前Bot策略，Ask/session需实际批准；只读Explorer/Verifier/主Bot的能力闸不扩大。参数原url/waitForRender/timeoutMs，超时默认30000ms、钳制1–120000ms；手动最多5次重定向/6次GET，无自动重试/错误降级。仅HTTP(S)，每跳重新校验URL、当前授权、取消和原Native Network路线/证书策略；无跨目的client复用。URI userinfo明确拒绝（旧Node fetch实际也拒绝），不因reqwest默认行为添加Basic凭据。URL上限16384 bytes，content-type上限8192 bytes，标题原始capture及规范化结果各上限64KiB；超限明确失败，不以标题片段冒充完整标题。

启用固定reqwest0.12.24的gzip/br/deflate解码，但在共享Network默认builder显式禁用，仅Web Adapter开启，不能静默改变原模型/MCP/认证请求的Accept-Encoding或解码语义。响应解码后最多5000000 bytes，分块先检查再扩容；网络等待/正文读取的取消与权限撤回沿原EffectAdmission控制通道定期复核。HTML去脚本/样式/标签、实体和空白沿实际TS算法对照，原2,000,000 UTF-16正文与4000摘要上限保留；不截断Unicode scalar。原TS在engine先截正文却可能contentTruncated=false的事实保留为对照；原生明确contentTruncated并记录源长度/已存长度，不能将已截断artifact称完整网页。坏数字实体/无法表达的UTF-16明确web_content_invalid；网络/HTTP错误保留原HTTP状态和原http_<status>细节，native错误族可用稳定web_http_error/web_fetch_failed，不返回可能含秘密的底层错误串。

代理凭据保护沿既有Native Network的实际route secrets，对title/content/URL/header事实在任何持久化/模型返回前做单次最长匹配替换并记录redacted；替换输出也有界，超限明确web_redaction_limit，不能先无限展开或以未脱敏片段降级。状态/HTTP分类先由可信响应确定，不能由正文或替换结果改写。进程内至多一个web fetch持有正文/归档工作集；网络/解析/发布均保留实际完成所有权，取消不丢弃仍在运行的阻塞任务。

网页产物保留原local-web-artifact://<uuid>[/content|/metadata]、web-artifacts/YYYY-MM-DD/<uuid>/content.txt和metadata.json，存放于显式选定data_home；默认home与旧CLI相同，不在隔离数据根之外写真实用户目录。新目录/文件使用0700/0600、NOFOLLOW目录FD及EXCL发布、内容和元数据fsync与目录发布确认；根/日期目录命名身份复核。已有旧产物只观察、不覆写/删除；原元数据字段保留，可增加schemaVersion/nativeContentRef/hash/redaction/源截断事实。全局网页存储512MiB、16384观察项、4MiB路径观察、目录深度4，读取与统计流式有界；原生写者共持根flock复核配额，不能因超额逐出已确认历史。旧未加锁安装版不因新锁自动变得兼容，混合版本drain仍须另验。

正文同时经既有Conversation ToolArtifactStore保存不可变UTF-8引用（原128MiB单对象/256MiB会话配额），在output给出原生read_tool_result回读参数，支持旧read_file字节上限之外的已存网页正文。此双格式保留是兼容成本，不是第二历史真源；legacy文件供旧工具读取，native回读只信其不可变全文hash/会话绑定，不从可改legacy文件重建事实。产物写入失败/取消前无效果可明确失败；首次可能持久效果之后无法证明完整发布则保留execution_outcome_unknown及已知引用/尝试身份，不删除部分目录、不重发HTTP、不清原unknown。常规HTTP/内容错误不制造产物或成功Evidence。

验收须实际TS HTTP/HTML/截断/错误向量和旧ArtifactStore内容/metadata、公开原生模型→网络批准→静态抓取→两种artifact/真实Evidence→模型、不可变全文回读、拒绝零网络/零目录、逐跳限制/降权、分块/压缩/超限、真实TLS/代理/额外CA和凭据回显脱敏、超时/取消连接关闭与worker结束、发布中断/硬退出/原unknown保全及后续独立任务。固定依赖/lock/MSRV实际编译；仅本机服务不能冒充真实互联网/平台/发布或P4总闸/P5–P7验收。

2026-11-17 静态抓取实施复核（B，既有Tool Result/Evidence状态边界不变）：公开Host反例发现新Adapter把超时写成timeout状态，现有Tool Result与Evidence登记只接受success/failed/denied/cancelled，导致原结果已经保存但登记失败并保守留下unknown。修正仅在Web Adapter将超时编码为failed并保留error.code=timeout；不扩大共享协议状态、不修改已产生unknown或抹除失败记录。授权撤回则保存原Grant与failed/permission_policy_changed，关闭实际连接；允许模型观察失败不等于重新批准后续网络。公开测试分别验证SIGTERM取消退出、超时失败续行和撤权后零新增抓取。

网页元数据采用序列化时256KiB输出闸，禁止先构造无限编码副本；新增路径预算在发布前计入。写后全文复核以预期长度限制实际读取，命名身份复核使用NONBLOCK/NOFOLLOW，不可因外部追加或替换为FIFO无限读取/阻塞；已有文件保全。上述均是原有有界发布契约的实现约束，不放宽配额、权限或unknown恢复。真实网络、工作集与发布总验收以对应候选回执为准。

### 2026-11-17 NR-04 原生结构化 Git 读取与动态读取范围（A，实施前登记）

沿ADR49/92/101/106/127/129–130迁移旧CLI已投影的git_query/local.git.query，不把仅用于unknown对账的GitStatusProbe当完整工具。原snapshot/status/log、默认limit40与1–200、真实仓库/git/common/config来源、HEAD/branch/commit、顶层状态与漂移、unborn/detached、filtersDisabled/submoduleCount/submodulesInspected/clean=null等语义按实际TS GitRead/Provider冻结。不得以工作区硬沙箱取消跨仓/外置gitdir与worktree；不得以Git工具变相开放Shell或写操作。恢复专用Probe继续保持原10s/256KiB及原范围/编码/收口约束，不能从新工具的较宽读取许可继承对账成功。

固定系统Git executable和编译期argv序列，无模型提交binary、flags、revision、config、环境或Shell。完整查询累计15秒实际Git执行预算、stdout/stderr累计8MiB；禁用pager/hooks/fsmonitor/optional locks/维护/外部clean-smudge-process filter/replace/lazy fetch/网络协议，不递归submodule，不修改index或仓库。复用原生owned-child生命周期：执行前及等待期间复核当前授权/取消；超时/超额/撤权关闭实际管道并终止、等待自有进程组，无法证明停稳不得伪报ended。共享底层命令执行实现时，原Probe的预算、错误和scope不被放宽；真正的Git发现/解析与授权分别归Module，不在中心Host按git capabilityId拼命令。

对原根授权语义作显式适配：真实已准入workspace/read root内读取可沿该次Read Tool Call形成宿主Grant；Full对角色允许的外部读取仍走当前Bot自动批准，不能额外硬拒路径。Ask/session对原未准入目标及后续发现的repository/git/common/config外置来源必须取得实际宿主批准，不能将一次原路径批准扩大到新外置路径。具体可达行为以真实TS Provider/CLI授权对照为准；不从模型声明readOnly或路径文本推断许可。动态scope通过同一有界EffectAdmission控制通道请求，只能由Host核对原call/capability/args摘要、workspace/parent/session/plan/执行代、当前policy/lease/角色及canonical路径后签发；Provider不能回传自造Grant。

需要人工批准的范围继续用现有ApprovalStore和PermissionInput，不开第二批准库或私有执行路线。批准参数绑定原操作摘要与具体读取路径/文件或目录语义；本次调用内只能复用已准入根和已批准的具体范围，不能跨调用/session自动复用。批准与拒绝事实随同一canonical Tool Result保存，保留原已签发Grant，新增scope的拒绝/撤回不能倒改过去批准。Evidence只引用真实Host决定；Grant不是执行成功，读到Git状态不等于Goal核验/签收。原生权限等待按ADR92既有5分钟截止、取消、过期与迟到决定收口补齐，实际等待/心跳和执行计时分别管理，不把审批耗时误算成Git执行超时。

有界观察：最多16384条状态记录、4MiB状态路径文本、128个config来源/128个origin/128个filter key（每key512bytes），单路径沿原8192bytes身份预算；超额明确失败，不丢条目后报告clean。UTF8无效字节按实际Node替换语义；路径/HEAD字段必须保持事实身份，不靠trim改变合法文件名。origin/subject沿原秘密规则，最多4000UTF16的原字段预览使用安全scalar边界并明确截断事实；最终完整观察JSON限8MiB，不能先无界扩容。进程内一次Git工作集，完整JSON经既有不可变ToolArtifactStore保存；预览沿原4000单位/limit/3个origin与400字符片段约束并明确contextPreviewTruncated。artifactPath指向实际保存的JSON，保留read_file检索并提供原生read_tool_result的会话/hash绑定入口；不重执行Git补历史、不覆盖或逐出旧产物。首次可能持久效果后发布/回执失败仍保留unknown与已知引用，不能删除来制造恢复。

验收先实际TS真实临时仓库的clean/staged/unstaged/untracked/rename/特殊路径、log/detached/unborn/worktree/external gitdir/include config/filter/submodule/凭据origin与subject、输入/权限/执行失败向量。原生必须公开模型→投影→根/动态scope批准→固定Git→完整归档/预览→Evidence→模型/回读；真实PTY逐项批准/拒绝、无审批者、迟到/过期、执行中降权/取消/heartbeat/限额/进程组结束、无index/过滤器副作用、发布/硬退出unknown与后续独立任务都要覆盖。Module或GitProbe单测不能冒充Host闭环，合成Git服务不代替真实模型/平台/安装或P4总闸/P5–P7。

2026-11-17 Git接线前权限实施复核（B，ADR92/101既有决定来源与5分钟等待边界不变）：在b716固定featureless产物的既有隔离non-TTY Web拒绝记录中，实际没有界面决定，但TerminalPermission返回Deny后被记为decidedBy=local_ui，open/denied两行deadlineAt均为空。原Tool Result为拒绝、零网络/零网页目录，不把此问题称为已越权执行；原数据根、行与hash保留，不改写历史来修正归因。新增动态读取scope不能复制此缺口。后续实现须区分真实用户拒绝与宿主不可交互/取消/超时：不可用、取消与过期使用现有policy决定来源及对应reason，实际用户Approve/Deny才使用local_ui；新活跃请求持久化既有5分钟deadlineAt并拒绝迟到批准。既有参数/主体/策略/lease复核仍先于授权，失效行按现有CAS收口；非白名单的执行失效原因不得把Expired落盘变成InvalidInput，精确原因仍保留在调用失败。旧无deadline、旧误归因记录不补造用户决定或新许可；重启只在原owned恢复闸后沿既有stale/expired规则处理，不从历史audit恢复活跃授权，不触碰个人实例/数据。


2026-11-17 Git Host接线实施复核（B，沿上段已接受读取准入边界）：实施复核确认旧Git Provider已有file-read/capabilityId/path/workspacePath运行时对象，但Protocol中并不存在名为LocalFilePermissionScope的类型，前稿名称表述不准确。按本节已接受的typed scope要求，将该既有JSON形态正式命名为LocalReadPermissionScope并补齐TS/Rust类型，在原PermissionGrant.scope与Host提示中表达，不增加历史批准的执行权或另一个持久格式；目录/文件包含关系由Host根据实际canonical路径及类型判定，模型不能提交已准入根。追加scope批准使用“原工具参数摘要+具体scope”的独立摘要，避免旧普通操作匹配器复用为整次工具批准；原Authority仍校验原参数摘要/主体/策略/执行代。补充批准由Host保留、随同一canonical消息/Evidence保存，不把它委托给Provider输出。一次调用的根/补充scope集有界，终态释放，不从历史记录恢复执行权。

只读任务的resourceDirectory原本为null，这是“不占写目录”的资源事实，不能拿它当读取工作区不存在。原生Host按当前canonical Goal的已绑定worktree/target、会话workspacePath与原workspace来源解析读取锚点，按原source revision复核；不把目录重新写入只读资源claim，不从工具参数授予根。readonly Worker的公开exec沿相同准入/当前性/预算/停稳链；模型投影与Provider都检查已接受的只读能力策略。Explorer/Verifier的任务发起、模型角色选择、核验和签收仍由P5原有角色入口接入，不能仅凭一个枚举或Git单测宣称完整产品闭环。完整CLI迁移目标不变。


### 2026-11-17 NR-04 原生受管本地子进程的只读恢复（A，实施前登记）

Git接线复核发现，既有ExecutionResourceStore对readOnly任务的markHandle为no-op；原native recorder v1只证明CLI宿主死亡，不证明其尚存Git子进程结束。不能用resourceDirectory=null制造本地停稳。沿原canonical work budget的attempt.pendingTools/uncertainDispatches中同一调用保存可选nativeProcess v1：完整owner Recorder、handleId、调用/dispatch身份、单调generation、not_started/starting/running/ended状态及running时完整child Recorder。一个工具至多64次固定命令启动；不新开进程/批准/恢复账本，不把预算数值或模型文本当进程事实。字段是Host-owned协议，Provider不能提交原任务/owner身份或持久写入。

登记新的coordination语义floor13（12继续保留给ADR127，10不复用）：写入该字段前沿既有writer-fence晋级，TS/Rust同样识别、保留及校验；含该语义的头/索引/重建保持13，旧<=12 reader/writer明确拒绝，不仅靠进程内标志防旧宿主把parent死亡当全部停止。无该字段的旧记录不补造身份/未派发证明。当前已加载旧宿主/安装版本drain仍是独立P4兼容闸，源码更新不倒过来保护旧实例；不操作个人任务或在用进程。

每次固定Git spawn之前，受管Engine必须通过原有有界EffectAdmission端口让Host在同一pending dispatch记录starting并收到持久确认；之后立即捕获完整PID/start/boot与原host/acquiredAt，Host核对owner、当前call/args/scope/lease及实际进程组，再保存running。旧child必须已实际结束/组不存在才可推进下一generation。回执或身份捕获失败仍由原owner终止并await实际子进程组，不能遗失进程、只drop future或伪报ended。首次未启动状态与真实ended可解释为已知本地空闲；starting且没有完整child身份的崩溃窗口保持unproven，不能凭超时或“Git只读”推测无子进程。

原CLI已确证死亡、原执行身份/owner一致、当前Host取得既有owned恢复权后，才能针对仍为同一PID/start/boot且PID=PGID的自有child发停止；复用PID、不同boot及不存在等沿原Recorder proof区分，组存在/查询失败均不等于结束。恢复更新同一canonical记录的实际停止观察，再允许原managed_execution停稳；原工具pending/unknown及产物不因此变success、不重放Git、不删除部分JSON或旧Evidence。正常最终结果只有在所有自有child已结束后才可结算；取消/撤权/超时的清理不因新派发许可已撤回而被拒绝，但不得趁清理启动新命令。该Host seam可供后续已接受的本地工具Adapter复用；不改变外部MCP远端效果的unfenced判断。

验收包含：真实命令意图/完整Recorder冷读及TS↔Rust往返、<=12已加载实现对13拒绝、只读任务不占写目录却能恢复自有child、实际TERM/KILL与PID复用/boot变化/失败查询、starting崩溃窗口保全、原unknown/产物/批准不变、重复recover幂等及后续独立任务。只有本地停稳可证明时才推进；该登记与单元测试不等于P4总闸、完整角色产品或安装/真实模型验收。

2026-11-17 Git大固定元数据的归档澄清（A，实施前登记）：4000单位预算同时包含新增原生检索元数据，先裁切旧约定内的entries/commits/origin预览，并明确contextPreviewTruncated。真实repository/git/common/config路径等固定身份不可为了过预算被字符串截断或替换成猜测路径；固定部分仍超过预算时，沿已接受的通用JSON Tool Result归档/模型视图引用保存整个预览对象，返回既有local_tool_result_ref与read_tool_result，不新造结果类型。完整Git观察另有其原不可变JSON；被引用的完整预览保留真实artifactPath/read_file提示及该观察引用，检索不能重执行Git。正常内联结果继续直接含artifactPath，超额引用明确“预览/需继续读取”，不能称完整。两次可能发布都受原Store/权限/取消/配额与unknown保护，失败保留已知引用，不删除旧产物。该补充保护身份及完整检索能力，不放宽最终模型视图预算或把引用当执行成功。

2026-11-17 child登记实施复核（A，修正上述“实际进程组”观测时点）：真实Darwin快速退出且尚未wait回收的Git仍可由ps观测完整start身份，但getpgid返回ESRCH，kill(-pgid,0)可能返回EPERM；不能把它当组不存在，也不能要求暂停或改用Shell才能登记。固定Engine仍通过process_group(0)真实启动且独占Child/wait；Host在启动回执只登记原owner、完整child身份及running（已发起、尚未证明停止）。getpgid返回实际group时必须PID=PGID；仅ESRCH允许保全身份并继续等待，其它查询错误拒绝。该分支不签发死亡/组不存在/ended事实，不允许在恢复中凭ESRCH杀进程；正常结束仍由原Child wait和实际group absence共同证明，下一generation仍须旧child结束且组不存在。硬退出恢复杀仍只限完整同PID/start/boot的Alive且getpgid确为PID；EPERM/组查询失败保留unproven。保留原失败与真实zombie实验，公开入口覆盖快速命令；不降低停稳或unknown规则。

### 2026-11-17 NR-04 共享 Provider 执行接缝（B，实施前复核）

ADR65/76/129要求普通exec、ACP、交互入口复用本地能力链。当前b308的PreparedEffect.start直接要求NativeSessionHost与Goal Grant，MCP Provider还直接写Goal资源句柄并操作live registry；这使已实现的Provider不能供普通会话使用。先将该真实变化点收敛到原EffectAdmission：Provider只取得Host生成的调用事实（conversation/toolCall/startedAt）与不可由模型制造的绑定端口；开始前和实际I/O仍从该端口取得当前授权确认。调用事实不是PermissionGrant，Grant仍由实际宿主保存、实时校验并与同一Tool Result/Evidence提交。不能构造虚假Goal、继承Bot Full给经典会话或另开文件/Shell执行器解决普通入口。

MCP新连接的未启动driver经同一有界控制通道交给Host，Host先核对本次MCP准入、源版本/owner及取消，再保存原nativeMcp handle并登记原live owner，确认后才能运行driver/发请求。拒绝、队列关闭或登记失败不启动该driver；取消/撤权后仍等待真正owner结束，不凭future drop制造已停止。Provider的连接池有界，异步等待不持标准Mutex，池失败不能导致新旧连接双跑；连接/child事实、旧凭据epoch、未围栏远端unknown与恢复规则不变。当前Goal adapter继续使用原ExecutionResourceStore/ExecutionRegistry，不增加存储、权限枚举、外部消息或私有账本。

该复核是已接受统一能力链的B级实现解耦，不移动准入/授权/Evidence/存储边界。验证应覆盖实际公开模型→file/Shell/Web/Git/MCP→结果链、MCP连接复用/换代/注册拒绝与断连、owner拒绝时零spawn/网络、取消/撤权/硬退出/后续任务与旧记录互读；不得以接口编译替代行为。普通会话身份/持久执行与完整Context/exec/ACP仍须沿既有契约分别接线和验收；本步本身不等于普通CLI可用或P4完成。

2026-11-17 共享接缝验证的Git执行计时复核（B，修复前登记）：真实并行专项在只读查询generation4即得到git_query_timeout，源代码将每次run之前的Host授权/starting持久意图等待也累加到execution预算。原约定仍是累计15秒受管Git执行窗口，审批/宿主准入单独管理；不能提高15秒或把此失败称flake。共享command runner用明确的deadline作用域表达：完整Git工具从实际spawn前瞬间计时至真正owned completion/组不存在，累计该区间（含spawn后的保守登记/排空开销）；spawn前的准入不重复计入，持久starting确认仍独立有界5秒且未确认不得spawn。超时后继续等待实际清理，不能以掉future代替停止。恢复Probe继续使用其原绝对10秒总时限/256KiB/范围和编码，不从工具较宽的计时作用域继承放宽。用同一受管runner的真实命令、受控慢准入建立红例，并保留公开只读/回读失败源和最终回归；无新权限、存储或结果成功规则。
