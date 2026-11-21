# ADR 文档图谱

2026-11-19：ADR131 登记普通 `peer-ts` 前台 Shell 的同一 `shell_session` 记录。旧宿主先持久化原授权、启动与本次命令绑定，凭原进程组消失结清句柄；新版读侧保全旧宿主未证明停稳的记录，后台 Shell 与冷恢复权限保持原范围。

2026-11-18：ADR131 登记普通 Goal 创建、任务更新和只读 Explorer。沿既有根锁、canonical 文件及同一个会话执行 owner，保留 Plan 批准闸。Explorer 的独立历史、派发、报告及取消沿真实证据和停稳契约，部分提交保全并阻断未经核对的重放。

2026-11-18：ADR131 登记普通 Goal 查询的会话范围、canonical 计划与 Runner 复核、实际 TS 工具契约及原生 Tool Result 回读。显式 ID 查询收紧到同会话。

2026-11-18：ADR131 复核普通显式 Goal 的文件与 Shell 准入。真实旧包拒绝无计划写入，原生候选实测产生文件效果。以 canonical Goal 及原会话、实际目录核对准入，沿原 Grant、Evidence 和停稳边界收口。

2026-11-18：ADR131补充真实旧 TUI v3 设置的 Native 显式执行读取规则，普通和 Work 继续以各自已有授权真源为准。

2026-11-18：ADR131补充原生压缩摘要输入的单项和总量预算及原文回读规则，保留 canonical、Tool Result、冷读重计数和恢复契约。

2026-11-18：ADR131登记委派 Work 后台 Shell，同执行原启动 Evidence 后继续派发，定向停止沿原资源和实际 owned handle。

2026-11-18：ADR131登记委派 Work 持久 Shell，经原 attempt 与 pending Tool Call 保存解释器和本次许可，原 claim/Registry 停稳，coordination-v2 semantic floor 15 防止旧宿主误写。

2026-11-18：ADR131沿65/116/129登记原生后台 Shell。启动回执、现有 native process/handle、定向停止与最终停稳由同一 Host 持有，前序 Grant、scope、unknown 及其他执行隔离不变。普通 handles 兼容和委派 fence 分别验收。

2026-11-18：ADR131根据公开 `exec` 双后台红例修正同一执行的 pending 准入。只接受原已确认的 Running Shell 启动、完整进程镜像、原 Grant 与 Evidence；其他挂起、未知及跨宿主准入维持保护。

2026-11-18：ADR131依据真实旧 Shell Session 与 `b1490f69` 原生包登记持久前台 Shell 的原会话串行派发、每次写入授权、独立命令事实与空闲句柄、实际停稳和未知保留。

2026-11-18 ADR131 记录持久 Shell 句柄与短命令绑定的总约束，以及前台控制帧、内核目录证据和分步授权。

2026-11-18 ADR131 补充持久 Shell 的命令输出归属。实测有迟到的异步子进程输出混入下一条命令，公开入口要求独立输出通道。

2026-11-18：ADR131沿65/116/129复核 Shell 旧产物只读引用和有界写入。固定路径、目录/文件 FD、2 MB 正文及 64 KiB 预览、真实截断和原 owner 停稳不改 Grant/Evidence。保留公开入口的链接与 100,000 字节输出失败基线，持久/后台能力另验。

2026-11-18：ADR131沿ADR118 §17.3/§19、108-cli-basic-shell-commands和ADR129复核原生 `peer result`。原 profile、schema 5、发布回执/索引、真实墓碑与原可携带会话来源仍是事实来源；只读、有界，无新持久格式、模型执行、授权或 Evidence。B级移植前登记，旧实现与原生失败基线保留。

2026-11-18：ADR131按实际旧 CLI 冷读兼容复核原 WAL 与缺少 `-shm`。仅由同一只读 SQLite 恢复已有 WAL 的派生索引，主库/WAL 的版本和内容保全，无执行或写入事实。

2026-11-18：ADR131/76 在 ACP Store 修正前登记目标会话逻辑 sourceRevision 与事务整索引实际代的职责。原真实双会话零模型请求反例保留，禁止用旧索引覆盖其它行。

2026-11-18：ADR131在OS Adapter修复前A登记 macOS PROC_PIDTBSDINFO 微秒 epoch 的 macos-v2 起点、固定安全 libproc seam与旧显示时间记录保全；真实跨TZ活owner误接管反例已保留。未知/旧起点仍活时 Unproven，不伪造死亡/升级或杀进程；五字段schema/授权/Evidence不变，完整验收另记。

2026-11-18：ADR131在普通恢复实现前A登记 `recover --session`、原目录FD排他恢复 guard 与窄token；无新持久格式或普通派发权。完整 owner/child OS 证明、原 Grant/Tool Result/Evidence 与已知账本分开核对；未知效果/starting/未知孤锁保全，不从文件存在推导成功，不以本入口替代 P4完整对账或旧宿主drain。

2026-11-18：ADR131在普通生产Host接线前B复核真实Conversation主体、同一ExecutionRegistry/credential epoch与loop/Provider；原Goal身份、access/Grant/Evidence/unknown和存储格式不变。普通Source以默认TS registry的实际section/hash对照，不用worker/测试Source替代；实际入口、旧宿主drain与P4总闸另验。

2026-11-18：ADR131在普通Host实现前A登记原Conversation metadata的runtimeExecution v1与真实Store metadata publication回执：普通conversation身份/owner、pending/用量/停稳/unknown，沿原锁/CAS及Grant/Evidence；保留ADR25每stream汇总和严格历史当前性，无假Goal/私有执行日志，旧已加载宿主drain及完整P4另验。

2026-11-18：ADR131在共享Context请求管线实现前B复核ADR55/56/57/65/76/129：同一计数/压缩/重试与用量事实捕获只依赖Host seam；Goal保留实际授权/预算/lease/MCP当前性，普通Host身份/持久执行仍另接，无新Source/格式/权限边界。

2026-11-18：ADR131在CI兼容证明修正前B登记：保留原失败和8b3ffbcf旧JSONL digest，以实际冻结旧writer↔当前Store重写取代仅靠当前源码未变的推断；原ADR118附件/游标/幂等边界不变，不宣称完整旧宿主drain。

2026-11-18：ADR131在共享原生turn loop实现前B复核ADR26/65/76/129的同一循环语义；Goal adapter保留实际权限/预算/存储/停稳与计费，普通默认不添隐式回合上限，不以抽出循环声称普通Host或P4完成。

2026-11-18：ADR131在普通会话 Store 接线前B复核既有v1流式sidecar与终态CAS；TS streaming写/清理共用原锁，部分提交保全并以新source核对原终态patch恢复，不新建执行日志或权限真源，普通Host/P4总闸仍开放。

2026-11-18：ADR131在普通 Runtime 接线前B复核 typed mode 投影与 capability allowlist 交集，先冻结真实 TS helper/隔离 Host 向量；既有 Goal 显式选 mode，不新增授权/存储路径，普通执行与 P4 另验。

2026-11-17：ADR131在计时修复前保留并行Git超时，按既有约定区分工具spawn起15秒累计窗口与Probe原绝对10秒总时限；spawn前Host准入单独有界，不提高预算或放宽unknown。

2026-11-17：ADR131沿ADR65/76/129复核共享Provider执行接缝：调用事实不授予权限，原绑定Host端口校验；MCP未启动driver由原Host先登记owner再运行。B级解耦，不改原授权/存储/unknown边界，不以此宣称普通exec/ACP完成。

2026-11-17：ADR131在修正实现前登记Darwin快速退出child的登记时点：ESRCH仅允许保全完整身份并等待，不代表group absent；正常wait/组不存在与恢复定向kill的证明要求不变。

2026-11-17：ADR131在原生git_query实现前登记既有ADR106固定Git观察、共享owned child与原Probe窄边界、有界完整产物及动态读取scope的同Host批准/事实保真；不新增Shell/跨调用许可或unknown自动收口。

2026-11-17：ADR131在实现前登记旧CLI静态web_fetch原生迁移：逐跳授权/Network、压缩隔离与有界正文、真实截断/脱敏事实、legacy网页产物兼容和不可变回读、FD发布/配额/partial unknown；不接受Proposed ADR38或新增Browser能力。

2026-11-17：ADR131批量搜索B复核保留真实Grant与失败结果分离；undeclared硬退出继续保守保护原命名空间，同范围后续任务仍阻断、独立目录另验，不放宽unknown恢复。

2026-11-18：ADR131登记原生用户本地图片输入，沿原用户消息、模型预算与明确选择边界，新增显式 `exec --image`，不投影模型侧图片读取工具。

2026-11-17：ADR131实施前校正CLI实际可达集（view_image仅Desktop装配，图片附件仍须迁移），并登记既有batch_search原生Adapter、有界lane调度/partial/控制取消与同一Grant/Evidence链。

2026-11-17：ADR131附件接线前补充分离事实上下文8MiB序列化预算与固定1MiB权限/控制摘要预算；JS算法及授权不变。纯图片预检在ready→started之前，实际请求仍重检，不清旧control/unknown。

2026-11-17：ADR131在实现前登记已保存用户图片的原生请求准入：事实留在user分片，无本机/URL抓取，不可表达时在count/send前拒绝而非丢图，保持原预算、canonical选择与授权/Evidence边界；本地图片Provider及P4完整验收另记。

2026-11-17：ADR131实现前登记受管父目录创建：同一write_file/Grant，现存祖先协调claim，NOFOLLOW目录FD与实时授权复核，128层预算及首次效果后unknown保全，不扩大Goal/权限、不自动重放。

2026-11-17：ADR131在实现前登记模型侧结果编码、按原消息身份绑定的视图覆盖、历史观察受管材料化与sourceRevision复核；失败/stderr/Unicode保真、同字节count/send及压缩事实视图。原canonical/授权/Evidence/unknown不由视图改写，旧大历史与P4总闸另验。

2026-11-17：ADR131在接线前补充local.tool-result.read原生快照回读能力，经原Provider/Projection/Read Grant/Evidence，严格绑定实际会话并校验全文摘要；无任意路径、跨会话、缓存回填或执行重放。

2026-11-17：ADR131在实现前登记Conversation Store不可变工具快照、内容引用/流式校验、无覆盖发布和保留配额；大文件与模型结果副本、参数预算按v2资源迁移。原授权/Evidence/unknown政策不变；不以缓存逐出删除历史，不以当前工作区补旧事实，完整P4另验。

2026-11-17：ADR131在原生文件能力实现前登记五种既有Manifest操作、受管I/O任务与实时EffectAdmission复核、扫描/结果双预算及明确超限；ICU4X对照原locale排序/搜索。授权/未知恢复边界不变，大文件artifact与P4总闸另验。

2026-11-17：ADR131沿既有108-cli-basic-shell-commands在实现前登记只读doctor、会话目录与流式展示导出：独立于canonical模型历史，源版本复核、原子目标发布、原目标/会话保全和取消；复用有界JSON projection，不新增工具或授权/Evidence/Context来源。实现/大历史与P4总闸另验。

2026-11-17：ADR131/28的Grok原生实现按源前2d5e1cf实施于5182ad5e，并沿ADR108补齐原生shell补全。冻结原生tree29ea：387 Rust/148 Episode/291根1688互读/9PTY及featureless固定URL TLS工具闭环通过；最终仅另改CI总作业预算，前Mac45分钟超时和新CI待验均保留。device提示秘密字段反例与修正保留。未改变本地授权/Evidence边界，真实服务/安装drain与P4–P7仍待验，见实施账本和p4-native-grok-20261117回执。

2026-11-16：ADR131/28在Grok原生实现前登记device授权提示/有界轮询、实际scope与固定身份、既有Vault CAS和Grok专用兼容版本Module；仅原协议426受限再发一次。Model Provider不向本地能力授权，真实服务/安装drain与P4总闸另验。

2026-11-16：ADR132/131当前TS owned exchange、显式pending恢复与原生旧SDK缓存兼容按cf9540e实施于dc70fc3c；373 Rust/138 Episode原生门禁及最终TS投影67项聚焦通过，真实Provider/canonical预算保留unknown。安装drain/真实平台与P4总闸另验，详见实施账本。

2026-11-16：ADR132/131实施前A补齐当前TS MCP token发送前owned intent（含code交换）、一次提交回执、无工具认证重放和显式pending管理恢复；原生核对旧SDK issuer cache/实际token.scope。旧运行版本drain与全P4另验。

2026-11-16：ADR132原生自动刷新接线前B复核跨代旧凭据脱敏寿命与原64值/256KiB预算；epoch不持秘密。区分OAuth数值CONNECT与普通MCP域名CONNECT，不放宽地址或权限。

2026-11-16：ADR132/131实施前A补齐原生MCP运行时刷新、execution内存credential epoch与原grant/Context续行；仅受管真实发布推进，外部修改阻断；旧连接停稳后替换，工具不重放。TS预读发送guard/安装drain另验。

2026-11-16：ADR132/131实施前A补齐MCP加密刷新意图；同owner持锁publish推进binding，已登记后失败未知不恢复旧refresh；Rust与Desktop冷读阻断，显式原生重登恢复。旧预读发送者/drain及自动刷新grant延续另验。

2026-11-16：ADR132 OAuth数值连接实施复核：沿已接受地址/权限边界接SDK HTTP，64 DNS/32KiB头与原30秒/1MiB/256KiB约束、同一可信根、标准CONNECT upgrade和原域名TLS；失败不切路、不重放。B级接线前登记，实现验收另记。

2026-11-16：ADR132实施前A补充普通MCP统一Native Network策略、逐物理请求预检/dispatch与代理凭据脱敏；旧SDK默认fetch与模型专用策略明确区分。OAuth代理必须先批准IP再数值CONNECT并保留原TLS主机名，当前卡不放宽地址政策。实现/验收另记。

2026-11-16：ADR50按实际CLI迁移原生模型网络Module：逐请求macOS代理、原env/NO_PROXY、显式extra CA和受限OS信任查询，保留TLS及OAuth不重放；MCP地址策略不借本卡放宽。实施/平台验收另记。

2026-11-16：ADR131环境来源Adapter接线前补齐显式openai-compatible身份、原三字段选择/既有canonical四字段校验与独立env Chat编码；不把环境key注入文件渠道，不改变工具授权。

2026-11-16：ADR131 NR-04补齐OAuth提示重建与窄models reconcile恢复入口：真实Vault与metadata结果分开、无秘密影子库、不重放认证，提示变化不取代operational binding；status/models列表仍不写或解封秘密。实现/平台验收另记。

2026-11-16：ADR131 NR-04配置范围校正：原CLI models是列表，PEER_MODEL_*是独立环境配置；按原实际可达集迁移，撤回把Desktop全套CRUD新增命令列为P4前提的扩大解释。Store共锁、Vault条件恢复、原有功能与完整P4–P7验收不变。

2026-11-16：ADR28/131实施前A补齐原生models auth/logout/status，固定Adapter身份与S256/loopback，原凭据代CAS及真实Vault状态；纠正OAuth提示字段被误作准入真值。完整配置写入/恢复和升级drain仍待实施，不新增工具授权。

2026-11-16：ADR0001/131同日A补强：模型OAuth须前置CAS加密刷新意图，唯一刷新者才发远端请求；未知结果保全并阻止旧refresh自动重放。完成仅提交自己的意图代；旧预读token宿主仍须迁移并通过drain/升级兼容闸，不宣称新增字段解决全版本并发。

2026-11-16：ADR131 NR-04补齐模型配置共享mkdir锁、严格有界读取、未知字段/CAS/原子提交和损坏保全；配置/Vault联合事务与旧宿主drain须独立验收，不因文件锁宣告完整P4。
2026-11-16：ADR28/`48-provider-model-options.md`原生移植前A校正：订阅采用当前生产内置权威模型目录（替代旧gpt-5前缀/远程fallback文字），选择值沿当前Protocol标量类型，有限select投影预算；订阅Responses不发送max_output_tokens，off/default采用原有CLI语义。普通API-key与权限边界不变，实现/真实模型验收另记。

2026-11-16：ADR0001/131实施前A修订：原生模型OAuth可协商Helper v1快照/条件写入，原Vault nonce作为opaque记录revision，迟到刷新不能覆盖轮换或复活删除。旧四action/密文格式/权限不变，缺feature在远端刷新前拒绝；模型配置写入与提示投影仍须单独验收，不冒充P4完成。

2026-11-16：新增 [ADR132 MCP Vault 与原生 OAuth](132-mcp-vault-and-native-oauth.md)，先登记 MCP Helper 命名空间、v2 元数据与不可变 slot 提交；取代 ADR32 的新写入 safeStorage / plaintext fallback。实现及验收另记。

2026-11-16：ADR131补记MCP Streamable HTTP的有界控制回复和双向请求id区分；属ADR31已有双向协议的B级补齐，不新增能力或授权路径。

2026-11-15：ADR131 增补 NR-04 原生 MCP dispatch 与停稳观测，实施前登记可选 nativeMcp handle 身份、初始化后实时复核和 unfenced external 对账。授权、可见性、Evidence 与既有人工收口政策不变；实现/验收另记。

创建时间：2026-11-06
最后更新：2026-11-09（登记 ADR87 D1–D11 修订经用户接受：过程叙述与正式交付分离，A 级；实施未完成，V01–V17 待验证，结果回填 ADR87 D10。85 对应展示交接条款同日被替代。同日新增 ADR 126 提案：执行资源 claim 的受控闭包、unknown 保留与隔离逃生；ADR 124 仍为已接受，ADR 126 只修订其永久占用边界，状态为未接受、未实现。同日新增 ADR 127 提案：unknown 对账、策略化自主收口与资源范围收敛；ADR 126 的闭包机制不变）

2026-11-09（晚）新增 ADR 125：资源窗口目录标签（方向经用户确认）；ADR 47 决策一第 4 条在资源窗口标签条范围内被替代。

> 这是 `knowledge/decisions/` 的索引，不是一条新的架构决定。
> 基线是知识库 `origin/main` 的 `ec96b057`（2026-11-06 核对，已包含 #122）。
> 编号 108 有两篇：`108-bot-reply-document-preview.md` 与 `108-cli-basic-shell-commands.md`（Accepted 2026-11-06，实现未发布验收）。引用必须带文件名。

本页只记录文件里写明的状态、日期和替代关系。页头写了接受，只说明这篇决定曾被接受，不说明对应实现已经发布验收。

## 知识库分层

ADR 是知识库五层中的决策层。产品方向和架构治理各自保留权威；2026-10-23 起，体验冲突以规范层为准。同一篇 ADR 里，后写的「后续」只改它点名的条款。

| 层 | 位置 | 回答的问题 |
|---|---|---|
| 架构 | `knowledge/architecture/` | 系统怎么分，哪条链不能旁路。治理基线是 `20-architecture-governance.md` |
| 决策 | `knowledge/decisions/` | 某一次边界怎么定。A 级改动先改这里，再改代码 |
| 规范 | `knowledge/specifications/` | 体验、动效和交互怎么做 |
| 产品 | `design/product/`、`design/visual/` | 路线和版本计划。方向以 `design/product/peer-product-alignment.md` 为准 |
| 执行与现场 | `playbook/`、`knowledge/experience/` | 怎么落地、怎么回归、出过什么问题 |

决策目录内部不再按主题分文件夹。编号大致按写入时间排列。读某一条时，先看文件名，再看页头状态，再看文末「后续」。

## 编号

2026-11-07 按 `origin/main` `3402e83` 重数：本图谱之外有 **110** 个决策文件、**105** 个编号。此前本段写的 109 个文件少计 1，编号数仍是 105。缺的编号是 `2`–`14`、`19`、`20`、`23`、`107`。`0001` 不占 `1`。`108-cli-basic-shell-commands.md` 复用编号 108，文件数比合并前多 1，编号数不变。ADR 122 用 121 之后的下一个空号，不回填 107，也不复用 108。ADR 124 用 123 之后的下一个空号，同样不回填、不复用。收入 ADR 124 之后，决策文件为 **111**，编号为 **106**。

2026-11-09 按 `origin/main` 重数：图谱之外为 **114** 个决策文件、**110** 个编号（含 48/59/104/108 四组同号双篇），已计入 ADR 126 / 127 提案。

同一个编号有两篇时，引用必须带文件名：

| 编号 | 文件 | 读取 |
|---|---|---|
| 48 | `48-cli-first-class-release.md` | 页头已接受 |
| 48 | `48-provider-model-options.md` | 页头已接受 |
| 59 | `59-appshots-capability-boundary.md` | 页头已接受 |
| 59 | `59-browser-panel-reveal-capability.md` | 页头已接受 |
| 104 | `104-bot-capability-visibility.md` | 未接受 |
| 104 | `104-progressive-interaction-and-coordination-storage.md` | 页头已接受 |
| 108 | `108-bot-reply-document-preview.md` | 页头已接受 |
| 108 | `108-cli-basic-shell-commands.md` | 已接受，实现未发布验收 |

## 已写明的替代和作废

只有正文自己写了替代或作废，才记在这里。没有出现的文件，不因为日期早就被当成过时。

| 文件 | 日期 | 写明的变化 |
|---|---|---|
| `52-unified-next-request-context-accounting.md` | 2026-07-25 | 页头标明部分被 ADR 56 取代。观察用量以 `56-provider-observed-context-accounting.md` 为准 |
| `41-rename-goal-mode-to-plan-mode.md` | 2026-07-03 | wire 值从 `goal` 迁到 `plan` 仍然有效。原结论「Runner 只属于 goal、plan 只是审批门」被 B2-b 推翻：批准后两边共用同一个 Runner |
| `16-skill-call-lifecycle.md` | 页头未标日期 | 本地能力链仍有效。原文中的「宙斯客户端 / Cloud CEO Gateway」已作废，不再是产品主语 |
| `112-runtime-module-and-loading-boundaries.md` | 2026-11-01 | 早期 manifest 3 草案已被替代。文中写明实际沿用 schema 2，新记录的最小 reader/writer 是 5 |

## 不能整篇当作现行契约

下面这些文件还在目录里。草案和未接受的，整篇都还不是生效契约。写了「部分被替代」或「部分作废」的，只有被点名的条款失效，其余句子仍然有效。

`105-portable-coordination-baseline-integrity.md` 没有「状态」行。它的第二行写的是「实施前决策，发布验收另记」，并写明用户已授权修复日志恢复。

| 文件 | 页头 |
|---|---|
| `15-plugin-skill-mcp-system.md` | 设计草案 |
| `16-skill-call-lifecycle.md` | 本地能力链仍有效。原文写的「宙斯客户端 / Cloud CEO Gateway」已作废，不再是产品主语 |
| `17-local-context-compaction.md` | 设计草案 |
| `18-claude-code-style-file-edit-plan.md` | 计划草案 |
| `38-web-search-fetch-provider.md` | Proposed on 2026-06-20（设计草案，尚未动代码） |
| `41-rename-goal-mode-to-plan-mode.md` | 部分修订（Superseded in part） — 方案 A（wire 值 `'goal'`→`'plan'`）与 wire 值迁移三步已落地；但本 ADR 核心结论之一「Runner 归… |
| `52-unified-next-request-context-accounting.md` | Superseded in part by ADR 56 |
| `74-deployment-surfaces-and-local-storage.md` | Proposed（产品方向已与用户对齐；实现未开工。本文不是已落地 Accepted 实现。） |
| `76-peer-acp-agent.md` | 实施边界已确定，尚未完成实现或验收 |
| `77-image-generation-capability.md` | Proposed（待架构评审；不是已接受或已实现能力） |
| `104-bot-capability-visibility.md` | Proposed（用户已确认扩展设计方向及默认全开的兼容规则，并要求完整重写；本文待逐项评审，实现与验收另记） |
| `113-checkpoint-content-addressed-storage-and-retention.md` | Proposed（用户要求先写决策、审阅后再实现；2026-10-29 用户已对 §6 的四个问题作出决定，全文待用户审阅后转为 Accepted 再实施）。§4.6 恢复入口由用户 202… |
| `119-user-stop-cognition-admission-and-settlement.md` | Proposed（用户要求先写完整 ADR；尚未批准实施，未改变运行行为）。ADR 124 已接受，只收窄其中「不增加工具通道」一句，不接受本篇 |

## 修订记录

只列出页头「最后更新」晚于创建日，或括号里写了修订说明的文件。没有统一的增删改 changelog。括号里的话是原文摘要；没写原因的，只记日期变过。

| 文件 | 创建 | 最后更新 | 页头注明 |
|---|---|---|---|
| `17-local-context-compaction.md` | 2026-06-08 | 2026-07-24 | 日期有更新，括号未写原因 |
| `25-runtime-usage-ledger.md` | 2026-06-25 | 2026-07-26 | 日期有更新，括号未写原因 |
| `30-provider-recovery-broker.md` | 2026-06-15 | 2026-07-30 | 日期有更新，括号未写原因 |
| `41-rename-goal-mode-to-plan-mode.md` | 2026-06-30 | 2026-07-03 | 日期有更新，括号未写原因 |
| `42-context-display-vs-trigger-accounting.md` | 2026-06-30 | 2026-07-01 | 日期有更新，括号未写原因 |
| `46-conversation-bound-browser-tabs.md` | 2026-07-15 | 2026-09-02 | 日期有更新，括号未写原因 |
| `48-cli-first-class-release.md` | 2026-07-20 | 2026-11-06 | ADR 108 收窄「CLI 自动更新可缓做」，只保留无人值守安装 |
| `50-cli-system-proxy-fallback.md` | 2026-07-22 | 2026-07-22 | 代码已落地：`apps/tui` 新增 macOS 系统代理读取 + env 回退，bun test … |
| `51-unified-desktop-cli-file-tools.md` | 2026-07-22 | 2026-07-23 | 日期有更新，括号未写原因 |
| `52-unified-next-request-context-accounting.md` | 2026-07-23 | 2026-07-25 | 日期有更新，括号未写原因 |
| `56-provider-observed-context-accounting.md` | 2026-07-25 | 2026-07-26 | 日期有更新，括号未写原因 |
| `59-browser-panel-reveal-capability.md` | 2026-08-03 | 2026-08-15 | 日期有更新，括号未写原因 |
| `65-cli-headless-exec.md` | 2026-08-18 | 2026-08-18 | `exec` 默认不再设 `--max-turns` 上限 |
| `67-task-shell-workbench-radar.md` | 2026-08-22 | 2026-09-24 | 日期有更新，括号未写原因 |
| `72-l1-default-web-entry.md` | 2026-09-02 | 2026-09-02 | 第一刀系统提示落地 |
| `80-project-agent-delegation-model.md` | 2026-09-24 | 2026-10-10 | ADR 91 补充自主协调、目标修订与取消重派 |
| `81-project-agent-memory-system.md` | 2026-09-24 | 2026-09-26 | P0-2 评审通过 |
| `82-project-objectives-and-watches.md` | 2026-09-24 | 2026-10-01 | 日期有更新，括号未写原因 |
| `83-model-routing-by-role.md` | 2026-09-24 | 2026-10-24 | 补齐档位参数、角色继承覆盖与请求通道 |
| `84-bot-list-shell.md` | 2026-09-26 | 2026-09-30 | 状态驱动的机器人角色 |
| `85-project-agent-hosts-inputs-and-surfaces.md` | 2026-09-26 | 2026-11-09 | ADR87 修订接受：公开 delta 归过程、正文由 canonical 回复承接、新契约禁纯文本 fallback（仅新契约范围；旧记录与既有 fallback 语义只读保留） |
| `87-user-turn-live-process-presentation.md` | 2026-10-05 | 2026-11-09 | D1–D11 过程叙述与正式交付分离修订经用户接受，A 级；实施未完成，V01–V17 待验证 |
| `88-project-agent-execution-continuity.md` | 2026-10-07 | 2026-11-01 | 关联 ADR 117 实施边界；§22 中断核验契约保留 |
| `89-independent-agent-delegation-and-communication.md` | 2026-10-10 | 2026-10-10 | 补充 ADR 91 自主协调设计引用 |
| `91-project-bot-autonomous-coordination.md` | 2026-10-10 | 2026-11-05 | 第 15 节身份解析、派发责任与独立 PR 候选 |
| `92-scoped-permission-inheritance.md` | 2026-10-11 | 2026-10-21 | 日期有更新，括号未写原因 |
| `93-verification-continuity-and-repair-ownership.md` | 2026-10-18 | 2026-11-01 | 关联 ADR 117 实施边界 |
| `94-reply-attempts-silent-wait-and-recovery.md` | 2026-10-18 | 2026-11-01 | 关联 ADR 117 实施边界 |
| `95-progress-driven-execution-policy.md` | 2026-10-18 | 2026-11-06 | 稳定输入排序与查询工件进度 |
| `98-large-history-execution-responsiveness.md` | 2026-10-18 | 2026-10-20 | 日期有更新，括号未写原因 |
| `102-unified-task-lifecycle-projection.md` | 2026-10-21 | 2026-10-22 | 日期有更新，括号未写原因 |
| `104-bot-capability-visibility.md` | 2026-10-22 | 2026-10-25 | 日期有更新，括号未写原因 |
| `104-progressive-interaction-and-coordination-storage.md` | 2026-10-22 | 2026-10-28 | 历史分叉、安全恢复与旧 writer 屏障补充 |
| `106-readonly-git-and-delegation-capability-admission.md` | 2026-10-23 | 2026-10-24 | 日期有更新，括号未写原因 |
| `108-bot-reply-document-preview.md` | 2026-10-24 | 2026-10-25 | 日期有更新，括号未写原因 |
| `109-resource-reference-preview-and-artifact-collaboration.md` | 2026-10-25 | 2026-10-27 | 补充 §35：独立只读窗口的阅读连续性 |
| `110-follow-up-responsibility-and-current-list.md` | 2026-10-28 | 2026-11-08 | ADR 124 的 indexed 处置离开当前列表，且不进入用户可见的「待核实」 |
| `111-project-agent-duplex-supervision-and-continuity.md` | 2026-10-28 | 2026-11-01 | 关联 ADR 117 实施边界 |
| `112-runtime-module-and-loading-boundaries.md` | 2026-10-28 | 2026-11-01 | 关联 ADR 117 实施边界 |
| `115-input-prediction-and-draft-boundary.md` | 2026-10-31 | 2026-11-01 | 日期有更新，括号未写原因 |
| `116-session-control-and-resource-settlement.md` | 2026-11-01 | 2026-11-08 | ADR 124 已接受，释放仍只认停稳回执；可见性修订不改变释放条件 |
| `117-intent-driven-coordination-and-goal-closure.md` | 2026-11-01 | 2026-11-03 | 日期有更新，括号未写原因 |
| `118-openui-interactive-results-and-runtime-boundaries.md` | 2026-11-02 | 2026-11-05 | 日期有更新，括号未写原因 |
| `119-user-stop-cognition-admission-and-settlement.md` | 2026-11-03 | 2026-11-07 | 本篇仍未接受。ADR 124 已接受，只收窄三件义务工具，不接受本篇其余条款 |
| `120-runtime-facts-disposition-and-resource-wait.md` | 2026-11-03 | 2026-11-08 | ADR 124 已接受；核实不是停止确认。2026-11-08 起退役索引不对用户开放 |
| `123-main-bot-unnoticed-memory.md` | 2026-11-06 | 2026-11-06 | 替代草案估算触发、全文回流及裁尾回退；补齐有限准入、保真、回读、撤销、并发与恢复 |
| `124-legacy-stop-obligation-controlled-resolution.md` | 2026-11-07 | 2026-11-08 | 2026-11-07 20:03 Asia/Shanghai 已接受并授权实施。2026-11-08 修订用户可见性：索引只留内部审计，日常界面不展示「待核实」 |
| `125-resource-window-directory-tabs.md` | 2026-11-09 | 2026-11-09 | 新增：资源窗口目录为一等资源标签；47 的被替代条款同日登记 |

同一天被 ADR 117 的实施边界带过一笔的有：`88`、`93`、`94`、`95`、`110`、`111`、`112`，当时的最后更新都是 2026-11-01。ADR 110 在 2026-11-07 追加了 ADR 124 的关系说明；同日 20:03 起该说明改为已接受的 indexed 展示修订，117 那一笔仍在正文里。2026-11-08 再写明这条 indexed 处置不进入用户可见的「待核实」。ADR 117 自己的最后更新是 2026-11-03，记的是四包源码自测完成。ADR 118 在 2026-11-05 把交互结果纳入 RC36。ADR 91 在 2026-11-05 增加第 15 节身份解析。`48-cli-first-class-release.md` 在 2026-11-06 把 CLI 自动更新收窄为只保留无人值守安装，显式 `peer update` 改由 `108-cli-basic-shell-commands.md` 规定。

## 过时引用

| 位置 | 仍写着 | 被指文件现在的页头 |
|---|---|---|
| `knowledge/architecture/22-tui-desktop-shared-runtime-and-host-governance.md` | ADR 65 是 Proposed | `65-cli-headless-exec.md` 于 2026-08-18 写明 Accepted，且 P0 已落地 |
| `AGENTS.md` 对阶段 F 的一句话 | 项目代理壳 Proposed，见 ADR 80 | `design/product/peer-transformation-charter.md` 在 2026-10-23 已把阶段 F 核对为已落地、进入 RC 收敛。ADR 80 页头仍留着「实现未开工」，要连文末后续一起读 |

## 目录

「读取」一列只压缩页头，方便扫。细节以文件为准。

### 0001 凭据

| 编号 | 文件 | 创建 | 最后更新 | 读取 |
|---|---|---|---|---|
| 0001 | [ADR 0001：跨平台凭证 Vault 与统一 Helper](./0001-cross-platform-credential-vault.md) | 2026-07-15 | 2026-07-15 | 页头已接受 |

### 15–18 早期能力草案

| 编号 | 文件 | 创建 | 最后更新 | 读取 |
|---|---|---|---|---|
| 15 | [Plugin / Skill / MCP 能力体系设计](./15-plugin-skill-mcp-system.md) | 2026-05-20 | — | 草案 |
| 16 | [Peer Agent Runtime 调用生命周期](./16-skill-call-lifecycle.md) | — | — | 部分作废 |
| 17 | [Local Context Compaction 机制设计](./17-local-context-compaction.md) | 2026-06-08 | 2026-07-24 | 草案 |
| 18 | [Claude Code 风格文件编辑机制计划](./18-claude-code-style-file-edit-plan.md) | 2026-06-09 | — | 草案 |

### 21–79 宿主、工具、浏览器与发布

| 编号 | 文件 | 创建 | 最后更新 | 读取 |
|---|---|---|---|---|
| 21 | [ADR 21 — 跨重启的任务续传（Pending Task Resume，会话锚…](./21-pending-task-resume.md) | — | — | 页头已接受 |
| 22 | [ADR 22 — HMR/重载后的流式重连(Stream Reattach on …](./22-stream-reattach-on-reload.md) | — | — | 页头已接受 |
| 24 | [Provider Cache And Empty Response Guard](./24-provider-cache-and-empty-response-guard.md) | — | — | 页头已接受 |
| 25 | [Runtime Usage Ledger](./25-runtime-usage-ledger.md) | 2026-06-25 | 2026-07-26 | 页头已接受 |
| 26 | [ADR 26 — Agent Loop Termination Semantics](./26-agent-loop-termination.md) | — | — | 页头已接受 |
| 27 | [ADR 27 — 工作区切换与跨工作区运行可见性(Workspace Switch…](./27-workspace-switch-and-cross-workspace-running.md) | — | — | 页头已接受 |
| 28 | [28. OpenAI Subscription OAuth (ChatGPT Lo…](./28-openai-subscription-oauth.md) | — | — | 页头已接受 |
| 29 | [29. 工具调用参数流式进度（Tool Arg Progress Streamin…](./29-tool-arg-progress-streaming.md) | — | — | 页头已接受 |
| 30 | [30. Provider Recovery Broker](./30-provider-recovery-broker.md) | 2026-06-15 | 2026-07-30 | 页头已接受 |
| 31 | [31. MCP 连接管理与设置入口](./31-mcp-connection-management.md) | — | — | 页头已接受 |
| 32 | [ADR 32: MCP Authentication and Credential…](./32-mcp-authentication.md) | — | — | 页头已接受 |
| 33 | [Per-Message Turn Duration Persistence](./33-per-message-turn-duration.md) | — | — | 页头已接受 |
| 34 | [Conversation Delete Cascades to Goal Plans](./34-conversation-delete-goal-plan-cascade.md) | — | — | 页头已接受 |
| 35 | [Mode-Scoped Tool Projection](./35-mode-scoped-tool-projection.md) | — | — | 页头已接受 |
| 36 | [36. MCP 工具卡标题透传（MCP Tool Card Title Passt…](./36-mcp-tool-card-title-passthrough.md) | — | — | 页头已接受 |
| 37 | [37. Provider Channel 与 Wire 协议分离](./37-provider-channel-and-wire-protocol-separation.md) | — | — | 页头已接受 |
| 38 | [38. Web Search / Fetch Provider（联网搜索与读链接能…](./38-web-search-fetch-provider.md) | — | — | 草案 |
| 39 | [39. 应用更新下载交互改造（非模态后台下载）](./39-updater-download-ux.md) | 2026-06-25 | 2026-06-25 | 页头已接受 |
| 40 | [40. 内嵌浏览器 + Agent 操控（webview 载体 + webCont…](./40-embedded-browser-and-agent-control.md) | 2026-06-25 | 2026-06-25 | 页头已接受 |
| 41 | [ADR 41：将现有「Goal 模式」正名为「Plan 模式」](./41-rename-goal-mode-to-plan-mode.md) | 2026-06-30 | 2026-07-03 | 部分被替代 |
| 42 | [ADR 42：上下文计数口径分离（显示口径 vs 压缩触发口径）](./42-context-display-vs-trigger-accounting.md) | 2026-06-30 | 2026-07-01 | 页头已接受 |
| 43 | [会话运行时状态按 conversationId 分桶（消灭跨会话串内容）](./43-conversation-runtime-state-bucketing.md) | 2026-07-01 | — | 页头已接受 |
| 44 | [44. 全局动效体系：自建语义基元 + 激进收敛（不引第三方库）](./44-motion-system-consolidation.md) | 2026-07-01 | 2026-07-01 | 页头已接受 |
| 45 | [45. MCP OAuth 配置交互简化：探测即自动配置 + 回调地址只读 + 授…](./45-mcp-oauth-config-ux-simplification.md) | 2026-07-01 | 2026-07-01 | 页头已接受 |
| 46 | [46. 会话绑定的 Workbench 与多标签浏览器](./46-conversation-bound-browser-tabs.md) | 2026-07-15 | 2026-09-02 | 页头已接受 |
| 47 | [47. Workbench 多资源标签模型](./47-workbench-multi-resource-tabs.md) | 2026-07-15 | 2026-11-09 | 页头已接受；决策一第 4 条在资源窗口范围内被 ADR 125 替代 |
| 48 | [CLI First-Class Release（CLI 与 Desktop 同仓一…](./48-cli-first-class-release.md) | 2026-07-20 | 2026-11-06 | 页头已接受 |
| 48 | [48. 渠道无关的模型选项与渠道投影](./48-provider-model-options.md) | 2026-07-17 | 2026-07-17 | 页头已接受 |
| 49 | [49. 取消路径硬沙箱（允许跨工作区读写）](./49-cancel-path-hard-sandbox.md) | 2026-07-21 | 2026-07-21 | 页头已接受 |
| 50 | [50. CLI 系统代理回退（macOS）](./50-cli-system-proxy-fallback.md) | 2026-07-22 | 2026-07-22 | 页头已接受 |
| 51 | [Unified Desktop and CLI File Tools（桌面端与 C…](./51-unified-desktop-cli-file-tools.md) | 2026-07-22 | 2026-07-23 | 页头已接受 |
| 52 | [ADR 52：统一下一次请求上下文统计](./52-unified-next-request-context-accounting.md) | 2026-07-23 | 2026-07-25 | 部分被替代 |
| 53 | [Tool Call Duration Accounting](./53-tool-call-duration-accounting.md) | 2026-07-23 | 2026-07-23 | 页头已接受 |
| 54 | [ADR 54：开放 Runtime 公开包与发布策略](./54-open-runtime-public-packages-and-release-policy.md) | 2026-07-24 | 2026-07-24 | 页头已接受 |
| 55 | [ADR 55：Desktop 与 TUI 统一 System Context As…](./55-shared-system-context-assembler.md) | 2026-07-25 | 2026-07-25 | 页头已接受 |
| 56 | [ADR 56：Provider 实测优先的精确上下文记账](./56-provider-observed-context-accounting.md) | 2026-07-25 | 2026-07-26 | 页头已接受 |
| 57 | [ADR 57：Desktop 与 TUI 统一 Canonical Convers…](./57-canonical-conversation-history-projector.md) | 2026-07-25 | 2026-07-25 | 页头已接受 |
| 58 | [本地 Skill 范围与工作空间挂载](./58-local-skill-scope-and-workspace-mounting.md) | 2026-07-27 | 2026-07-27 | 页头已接受 |
| 59 | [Appshots 能力边界与 Evidence 链](./59-appshots-capability-boundary.md) | 2026-07-30 | — | 页头已接受 |
| 59 | [59. Browser 面板主动打开与可见工作现场闭环](./59-browser-panel-reveal-capability.md) | 2026-08-03 | 2026-08-15 | 页头已接受 |
| 60 | [Quick Chat 独立 Popover 窗](./60-quick-chat-independent-popover-window.md) | 2026-07-30 | — | 页头已接受 |
| 61 | [61. beta→stable 通道自动毕业决策](./61-beta-to-stable-channel-graduation.md) | 2026-08-03 | 2026-08-03 | 页头已接受 |
| 62 | [62. Automation Runtime 与持久化边界](./62-automation-runtime-boundary.md) | 2026-08-04 | — | 页头已接受 |
| 63 | [63. 用户产物与 Evidence 边界](./63-user-artifact-evidence-boundary.md) | 2026-08-16 | — | 页头已接受 |
| 64 | [64. Workbench 源码预览先复用 highlight.js，不上 Mon…](./64-workbench-source-highlight-without-monaco.md) | 2026-08-17 | 2026-08-17 | 页头已接受 |
| 65 | [65. CLI 无头发起（`peer exec`）](./65-cli-headless-exec.md) | 2026-08-18 | 2026-08-18 | 页头已接受 |
| 66 | [66. 浏览器工具的后台降级执行（Headless Fallback）](./66-browser-headless-fallback-execution.md) | 2026-08-21 | 2026-08-21 | 页头已接受 |
| 67 | [67. 任务壳 + 工作台雷达（原型 A）](./67-task-shell-workbench-radar.md) | 2026-08-22 | 2026-09-24 | 页头已接受 |
| 68 | [68. 交付模式契约：direct 与隔离合回统一语义](./68-goal-delivery-mode-contract.md) | 2026-08-26 | — | 页头已接受 |
| 69 | [69. 合回分流（Triage）分类器：结构化 verdict 替代布尔判定](./69-handoff-triage-classifier.md) | 2026-08-26 | — | 页头已接受 |
| 70 | [70. L1 内嵌浏览器动作面扩展（hover / scroll / key / …](./70-l1-browser-action-surface.md) | 2026-09-01 | 2026-09-01 | 页头已接受 |
| 71 | [71. L2 受控外部浏览器（Playwright / CDP）安全模型](./71-l2-playwright-external-browser.md) | 2026-09-01 | 2026-09-01 | 页头已接受 |
| 72 | [72. 网页任务默认入口：L1 内置浏览器（`browser_*`）](./72-l1-default-web-entry.md) | 2026-09-02 | 2026-09-02 | 页头已接受 |
| 73 | [73. Goal 中断挂起与失败解耦的状态契约](./73-goal-interruption-suspension-vs-failure.md) | 2026-09-03 | — | 页头已接受 |
| 74 | [74. 部署面与本机存储策略](./74-deployment-surfaces-and-local-storage.md) | 2026-09-06 | 2026-09-06 | 未接受 |
| 75 | [75. 远程读取预检：通过不等于获得执行权](./75-remote-read-preflight.md) | 2026-09-26 | 2026-09-26 | 页头已接受 |
| 76 | [ADR 76：Peer 作为 ACP Agent](./76-peer-acp-agent.md) | 2026-09-08 | — | 未完成 |
| 77 | [77. 多服务图片生成能力与凭证、产物边界](./77-image-generation-capability.md) | 2026-09-15 | 2026-09-15 | 未接受 |
| 78 | [78. Intake 期武装 UI 交付视觉验证门](./78-intake-ui-delivery-arm.md) | 2026-09-23 | — | 页头已接受 |
| 79 | [79. 移除预配置基准分支：交付绑定跟随工作区实时 HEAD](./79-remove-preconfigured-base-branch.md) | 2026-09-23 | — | 页头已接受 |

### 80–99 0.1.0 项目代理与执行链

| 编号 | 文件 | 创建 | 最后更新 | 读取 |
|---|---|---|---|---|
| 80 | [80. 项目代理委托模型：一个项目一个代理，任务由代理开出](./80-project-agent-delegation-model.md) | 2026-09-24 | 2026-10-10 | 页头已接受 |
| 81 | [81. 项目代理记忆体系：带来源的事实记录，只进事实层，自动但可撤](./81-project-agent-memory-system.md) | 2026-09-24 | 2026-09-26 | 页头已接受 |
| 82 | [82. 项目目标与定时 / 事件驱动推进](./82-project-objectives-and-watches.md) | 2026-09-24 | 2026-10-01 | 页头已接受 |
| 83 | [83. 模型分工：档位 + 角色，用户说了算，开任务时冻结](./83-model-routing-by-role.md) | 2026-09-24 | 2026-10-24 | 页头已接受 |
| 84 | [84. 机器人列表壳：工作台不再是页面，应用本身就是机器人列表](./84-bot-list-shell.md) | 2026-09-26 | 2026-09-30 | 页头已接受 |
| 85 | [85. 项目代理的宿主、输入与多入口（0.1.0 落地边界）](./85-project-agent-hosts-inputs-and-surfaces.md) | 2026-09-26 | 2026-11-09 | 页头已接受；展示交接条款被 ADR87 2026-11-09 修订替代（仅新契约范围） |
| 86 | [ADR 86：已持久化对话的批量读取](./86-batched-persisted-conversation-reads.md) | 2026-10-02 | 2026-10-02 | 页头已接受 |
| 87 | [87. 用户回合可展开的实时过程](./87-user-turn-live-process-presentation.md) | 2026-10-05 | 2026-11-09 | 页头已接受；D1–D11 修订（过程叙述与正式交付分离）2026-11-09 经用户接受，实施未完成 |
| 88 | [88 项目代理连续执行与结果交付方案](./88-project-agent-execution-continuity.md) | 2026-10-07 | 2026-11-01 | 页头已接受 |
| 89 | [ADR 89：独立 Agent 接手、双向通信与真实工作动态](./89-independent-agent-delegation-and-communication.md) | 2026-10-10 | 2026-10-10 | 页头已接受 |
| 90 | [ADR 90：本地图片能力与安装版产品截图审查](./90-local-image-capability-and-product-review.md) | 2026-10-10 | 2026-10-10 | 页头已接受 |
| 91 | [ADR 91：主 Bot 自主协调、并行调度与取消重派](./91-project-bot-autonomous-coordination.md) | 2026-10-10 | 2026-11-05 | 页头已接受 |
| 92 | [ADR 92：具体资源授权与执行链继承](./92-scoped-permission-inheritance.md) | 2026-10-11 | 2026-10-21 | 页头已接受 |
| 93 | [ADR 93：复核续跑与未完成工作的处理责任](./93-verification-continuity-and-repair-ownership.md) | 2026-10-18 | 2026-11-01 | 页头已接受 |
| 94 | [ADR 94：主 Bot 回复、静默等待与历史错误](./94-reply-attempts-silent-wait-and-recovery.md) | 2026-10-18 | 2026-11-01 | 页头已接受 |
| 95 | [ADR 95：以实际进展驱动持续执行](./95-progress-driven-execution-policy.md) | 2026-10-18 | 2026-11-06 | 页头已接受 |
| 96 | [ADR 96：任务执行期间的响应性与有序持久化](./96-task-execution-responsiveness.md) | 2026-10-18 | 2026-11-06 | 页头已接受 |
| 97 | [ADR 97：推理回传、续接归属与已汇报等待](./97-reasoning-replay-and-continuation-custody.md) | 2026-10-18 | 2026-10-18 | 页头已接受 |
| 98 | [ADR 98：大历史规模下的任务执行响应性](./98-large-history-execution-responsiveness.md) | 2026-10-18 | 2026-10-20 | 页头已接受 |
| 99 | [ADR 99：权威回复回执、模型切换恢复与历史详情](./99-authoritative-reply-receipts-and-model-recovery.md) | 2026-10-19 | — | 页头已接受 |

### 100–125 近期契约

| 编号 | 文件 | 创建 | 最后更新 | 读取 |
|---|---|---|---|---|
| 100 | [ADR 100：待处理事项与对话提问生命周期](./100-actionable-attention-and-question-lifecycle.md) | 2026-10-20 | 2026-10-20 | 页头已接受 |
| 101 | [ADR 101：主 Bot 授权主体与子 Agent 动态继承](./101-bot-owned-access-policy.md) | 2026-10-21 | 2026-10-21 | 页头已接受 |
| 102 | [ADR 102：任务生命周期单一投影](./102-unified-task-lifecycle-projection.md) | 2026-10-21 | 2026-10-22 | 页头已接受 |
| 103 | [ADR 103：核验收口、进度与停滞治理](./103-verification-settlement-and-progress.md) | 2026-10-21 | — | 页头已接受 |
| 104 | [ADR 104：Bot 能力绑定与专属上下文：全局共享、独立配置及动态继承](./104-bot-capability-visibility.md) | 2026-10-22 | 2026-10-25 | 未接受 |
| 104 | [ADR 104：交互优先读取与协调日志增量存储](./104-progressive-interaction-and-coordination-storage.md) | 2026-10-22 | 2026-10-28 | 页头已接受 |
| 105 | [ADR 105：协调基线的可迁移内容证明](./105-portable-coordination-baseline-integrity.md) | 2026-10-22 | — | 页头未写状态 |
| 106 | [ADR 106：结构化只读 Git 与委派能力准入](./106-readonly-git-and-delegation-capability-admission.md) | 2026-10-23 | 2026-10-24 | 页头已接受 |
| 108 | [108. Bot 回复文件引用的有界只读预览](./108-bot-reply-document-preview.md) | 2026-10-24 | 2026-10-25 | 页头已接受 |
| 108 | [ADR 108：CLI 基础壳命令](./108-cli-basic-shell-commands.md) | 2026-11-06 | 2026-11-06 | 已接受，实现未发布验收 |
| 109 | [ADR 109：内容引用、资源预览与产物协作契约](./109-resource-reference-preview-and-artifact-collaboration.md) | 2026-10-25 | 2026-10-27 | 页头已接受 |
| 110 | [ADR 110：跟进责任收口与当前待办列表判定](./110-follow-up-responsibility-and-current-list.md) | 2026-10-28 | 2026-11-08 | 页头已接受；ADR 124 的 indexed 处置离开当前列表，且不进入用户可见的「待核实」 |
| 111 | [ADR 111：主 Bot 双向监督、可靠续接与上下文连续性](./111-project-agent-duplex-supervision-and-continuity.md) | 2026-10-28 | 2026-11-01 | 页头已接受 |
| 112 | [ADR 112：运行时模块与功能加载边界](./112-runtime-module-and-loading-boundaries.md) | 2026-10-28 | 2026-11-01 | 页头已接受 |
| 113 | [ADR 113：检查点内容寻址存储与本机数据保留](./113-checkpoint-content-addressed-storage-and-retention.md) | 2026-10-29 | 2026-10-29 | 未接受 |
| 114 | [114. 回复引用的定位与打开](./114-reply-citation-resolution-and-open.md) | 2026-10-30 | 2026-10-30 | 页头已接受 |
| 115 | [ADR 115：智能输入建议与用户草稿边界](./115-input-prediction-and-draft-boundary.md) | 2026-10-31 | 2026-11-01 | 页头已接受 |
| 116 | [ADR 116：任务控制、执行停稳与资源交接](./116-session-control-and-resource-settlement.md) | 2026-11-01 | 2026-11-08 | 页头已接受；ADR 124 不改变释放条件；ADR 126 提案修订 unknown 的永久 hold（未接受） |
| 117 | [ADR 117：意图驱动的协调判断、持续责任与目标闭环](./117-intent-driven-coordination-and-goal-closure.md) | 2026-11-01 | 2026-11-03 | 页头已接受 |
| 118 | [ADR 118：OpenUI 可交互结果复用与运行时边界](./118-openui-interactive-results-and-runtime-boundaries.md) | 2026-11-02 | 2026-11-05 | 页头已接受 |
| 119 | [ADR 119：用户停止、认知续跑准入与宿主收尾](./119-user-stop-cognition-admission-and-settlement.md) | 2026-11-03 | 2026-11-07 | 未接受。ADR 124 已接受，只收窄三件义务工具 |
| 120 | [ADR 120：运行事实、统一处置与资源等待闭环](./120-runtime-facts-disposition-and-resource-wait.md) | 2026-11-03 | 2026-11-08 | 页头已接受；ADR 124 不把核实当成停止确认。退役索引不对用户开放 |
| 121 | [ADR 121：Desktop 会话窗口契约](./121-desktop-session-windowing-contract.md) | 2026-11-05 | 2026-11-05 | 页头已接受 |
| 122 | [ADR 122：TUI 机器人列表与输入条呈现](./122-tui-bot-list-and-composer-chrome.md) | 2026-11-06 | 2026-11-06 | 已接受，实现未发布验收 |
| 123 | [ADR 123：主 Bot 会话的无感记忆](./123-main-bot-unnoticed-memory.md) | 2026-11-06 | 2026-11-06 | 未接受；本轮收紧容量、准入与恢复，未授权实现 |
| 124 | [ADR 124：遗留停止义务的受控核实与跟进退役](./124-legacy-stop-obligation-controlled-resolution.md) | 2026-11-07 | 2026-11-08 | 已接受并授权实施。2026-11-08 修订：索引只留内部审计，日常界面不展示「待核实」。Peer-Agent PR 297 未合并、未发版；ADR 126 提案修订 §1.5/§6.2 的绝对不释放边界（未接受） |
| 125 | [125. 资源窗口目录标签](./125-resource-window-directory-tabs.md) | 2026-11-09 | 2026-11-09 | 已接受（方向经用户确认）；同日追加决策五：launcher 且无辅助面板时隐藏头部网页/目录/变更三入口（辅助面板一开即恢复，按下态与焦点回退契约不变）；实施回执按验证要求第 5 条 |
| 126 | [ADR 126：执行资源 claim 的受控闭包、unknown 保留与隔离逃生](./126-execution-resource-claim-closure-and-unknown-retention.md) | 2026-11-09 | 2026-11-09 | 未接受提案。逐 claim 闭包修订 ADR 116/124 的永久占用边界；前提是死亡证明或用户确认、无 live、无未结束句柄；unknown 保留且不重放。ADR 127 提案扩展其授权模型（未接受） |
| 127 | [ADR 127：未知执行结果的对账协议、策略化自主收口与资源范围收敛](./127-unknown-outcome-reconciliation-and-delegated-resolution.md) | 2026-11-09 | 2026-11-09 | 未接受提案。把 unknown 从“人工逐次确认”扩展为源头回执、宿主对账与 `ask / bot_verified / auto` 策略；不改变证据边界，不引入 force |

## 维护

2026-11-06 起，修改和新增功能先过本页，再写代码。细则见 `playbook/change-intake.md`。

新增一篇 ADR 时，使用还没有被占用的编号，并在同一天给本页目录加一行。修订一篇 ADR 时，改那篇的「最后更新」，写明新增、删减、修复或优化了什么，以及哪一条款被替代，同时改本页对应行。不要复用已有编号。不要因为本页写了「页头已接受」，就把它说成发布验收已经通过。


2026-11-06 本轮落实既有 ADR 95 / 96 / 120 的输入排序、有序持久化及统一恢复事实；各原文新增日期补充，未新增编号，既有权限、Evidence、存储所有权边界保持。实施与逐项验收见 `playbook/v0.1.0/persisted-turn-recovery.md`。

2026-11-06 实施前收紧：ADR110/120 以 A 级明确既有 blockedReason 的本地存储机器故障投影与安全失败叶子准备，不新增存储格式；ADR95 限定查询工件完整/截断材料的进度认定。

2026-11-07 新增 ADR 124。同日 20:03（Asia/Shanghai）用户明确「那就落实124」，状态改为已接受并授权实施。它只在有效 indexed 处置下收窄 ADR 110 的当前列表规则，不改变 ADR 116 的释放条件，不接受 ADR 119 的其余条款，也不把核实写成 ADR 120 的停止确认。

2026-11-08 修订 ADR 124 的用户可见性。用户在 Peer-Agent PR 297 手测通过后确认「要」：待核实不对用户开放。确认后仍写 `disposition=indexed` / `obligation_indexed`，索引留给诊断、支持和以后核对。Desktop、TUI 和工作面板不展示「待核实」分区、列表、徽章或注意提示。证据、停稳回执、占用、`user_panel` 授权和主 Bot 工具边界不变。该代码 PR 仍未合并，这次修订尚未写入代码。

2026-11-09 新增 ADR 127 提案。它回应“unknown 永久锁 + 主 Bot 无自主收口权”的批评：源头先登记结果、宿主执行对账协议、用户按项目/Bot 委托 `ask / bot_verified / auto` 收口权，claim 按声明范围保护；模型不能伪造执行结果或证据，外部未围栏效果仍保留人工门。

2026-11-09 新增 ADR 126 提案。它来自一次真实长时间阻塞：已取消会话留下的 unknown 调用把项目目录永久锁死，两条空 unknown 的旧取消也被巡检永久跳过。提案把“登记进程已死、无活体/句柄”的历史 unknown 从目录 hold 降为 `RetainedUnknown`，并提供逐 claim、用户在宿主卡片确认的闭包，以及不释放原锁的独立 clone 逃生。它只修订 ADR 116 §6.2/§6.3 与 ADR 124 §1.5/§6.2 的永久占用边界；ADR 124 的知悉、退役、界面可见性和 `release_resource` 拒绝规则不变。状态为未接受、未实现，待用户评审后再开代码实施。

2026-11-09 新增 ADR 125（资源窗口目录标签），并修订 ADR 47 决策一第 4 条在资源窗口标签条范围内的适用；经典 Workbench 一级能力栏语义不变。实施在 Peer-Agent 代码仓进行，本页不维护执行状态。

## 原生 CLI 迁移（2026-11-14）

用户已接受原生 Rust / Ratatui 三份迁移决策并授权按 P0→P1 自测后持续实施，最终无 Bun/Node sidecar。评审稿原编号 116–118 与本页既有 ADR 冲突，改登记为 129–131；既有 116–118 不变，128 仍为另一在途设计，不在本次接受范围。

| 编号 | 文件 | 状态 |
|---|---|---|
| 129 | [原生 Rust CLI 与 Ratatui](129-native-rust-cli-and-ratatui.md) | Accepted，2026-11-14；实现 / 验收另记 |
| 130 | [有界内存与历史](130-bounded-cli-memory-and-transcript.md) | Accepted，2026-11-14；预算待实测 |
| 131 | [跨语言契约、数据与恢复](131-native-cli-contract-storage-and-recovery.md) | Accepted，2026-11-14；2026-11-15 A级补充用量恢复；2026-11-16 A级补充 Helper 条件提交及加密模型 OAuth 刷新意图，未知保全与跨宿主兼容闸；2026-11-17 A级登记原生受管child的canonical pending身份与语义floor13，保护只读任务恢复；2026-11-18 A级补充普通 recover --session、目录FD排他恢复与窄token，原未知和停稳/账本边界保留；实现 / 恢复另记  macOS稳定起点/旧记录保全实施前已登记   2026-11-18 A级补充原生 Skill 准入、挂载当前性与同会话正文检索   2026-11-18 A级补充原生 Hook 子进程、原 Tool Call 与保守恢复；同日登记委派 Work Hook 原 dispatch、持久化最低版本与停稳恢复、原 Tool Call 消息身份与 Post 前返回持久化 |
| 132 | [MCP Vault 与原生 OAuth](132-mcp-vault-and-native-oauth.md) | Accepted，2026-11-16；MCP Helper 命名空间、旧凭据迁移、不可变 slot 与刷新意图；同日A补充execution内存epoch和原grant/Context续行。实现 / 验收另记 |

2026-11-14 同日澄清 ADR 131 §1 的同号引用：`104-bot-capability-visibility.md` 仍未接受；`104-progressive-interaction-and-coordination-storage.md` 已接受的 writer fence / 恢复契约保留。未移动既有边界。

2026-11-14 NR-03：ADR 131 增补 canonical budget nativeRecorder v1 可选合同与原生停稳观测 Adapter；只证明 runner 死亡且无开放句柄，unknown/权限/Evidence/claim 收口要求不变，实施及验收另记。

2026-11-14 NR-03 复核：ADR 131 补充真实 Provider 创建结果/Evidence/dispatch 已确认后，同 owner 的 missing file claim 身份确认；保留 unknown/closure/外来身份阻断，schema 不变。

2026-11-15 ADR131/57: A-level historySelection v1, projector3 and capacity boundary binding supplement precedes implementation. Legacy markers retain suffix semantics; compatibility/recovery acceptance is tracked separately.

2026-11-17 NR-04：ADR131在实现前登记Qoder本地凭据/目录原生密码格式、严格有界解封、第三方只读身份及真实SDK互操作验收；不捆绑/运行JS或WASM引擎，完整Qoder Provider与P4仍另验。

2026-11-17 NR-04：ADR131补充Qoder只读账户/来源身份、原生运行时认证封装、公钥兼容加密和COSY签名、专用encoder与既有Host/Network接线；逐项验收完整Provider，不把正常首环或格式Module称为P4完成。

2026-11-17 ADR131 Qoder实施前对照补充：官方prepareInferRequest的COSY envelope requestId是独立随机UUID，不是正文request_id；维持每次物理发送认证准备，不借该标识重放或结算工具。

2026-11-17 NR-04 ADR131实施前补充：Qoder旧JSON/Bearer方言、三个环境token优先级、metadata/config驱动分支和只读来源read set；不在错误后降级/换号，不改许可、Evidence、账本或unknown恢复边界。

2026-11-17 NR-04 ADR131实施前补充：Qoder队列/重复/瞬态/连接重试归Host逐尝试计费和预算准入；冻结非身份正文、刷新请求身份/签名、等待续约/取消与历史版本复核，不重放本地工具或重启续发。

2026-11-19 NR-04 ADR131 实施前补充：普通 headless 使用已结算的本轮创建与 canonical Goal 版本触发原自动 inspect，同批后继按实际提交版本派发，复用只读 Explorer 与停稳。运行推进、核验和 P4 总闸分别验收。

2026-11-19 NR-04 ADR131 实施前补充：普通 headless Runner 将模型续推、同 stream 任务更新、只读检查及真实停稳绑定到 canonical Goal，沿现有 Source、工具授权与完成门。

2026-11-19 NR-04 ADR131 实施前补充：普通 headless 独立 Verifier 复用只读 Host，真实引用绑定父 Goal 与 stream，报告按来源版本保存，父宿主停稳后复核完成门。ADR93、103 仍持有续接与返修责任。

2026-11-19 NR-04 ADR131 实施前补充：普通 headless 沿既有 `modelReviews` 保存且复核独立 Verifier 的标准级判断，通过当前修订和原核验身份留痕。

2026-11-19 NR-04 ADR131 实施前补充：普通 headless 自驱 Goal 沿 ADR93/95/103/116/117，在当前独立失败核验上记录同一宿主的有界返修、真实派发和续审；原停稳、授权和 unknown 边界保留。

2026-11-19 NR-04 ADR131 实施前补充：普通自驱 Goal 的确定性验收缺口沿既有核验行记录检查来源，机械检查和模型核验共享原返修额度，完成仍要求新独立核验与真实停稳。

2026-11-19 NR-04 ADR131 实施前补充：按 ADR34、108-cli-basic-shell-commands、116 接通会话删除，对确切确认范围登记持久级联与原锁的所有权，保护未结算事实及外来锁。

## 统一 Rust Core 基座（2026-11-21）

用户接受 Classic 先行的统一基座架构方案并授权先落 A 级设计决策再按 C0–C3 分阶段实施：以单一 `peer` 原生二进制暴露跨平台 `peer core --stdio`（后续演进至本机 UDS / Named Pipe 共享 Daemon），经双向有界 JSON-RPC 2.0 统一驱动 Desktop 与 CLI，并通过 `ExternalRpcProvider` 保持 Desktop 专属能力仍走唯一 `Capability Provider → Manifest → Runtime Projection → Tool Call → PermissionGrant → Evidence` 主链。

| 编号 | 文件 | 状态 |
|---|---|---|
| 133 | [统一 Rust Core 基座与 Desktop 接入架构（Classic 先行）](133-unified-rust-core-and-desktop-bridge.md) | Accepted，2026-11-21；C0–C4b-2a 已完成（Classic、Automations、Memory、Objectives 与 Bot 档案/权限/游标/搜索面默认走 Rust Core，保留即时回退开关），余 C4b-2b–C4d 推进中 |

