# 原生 CLI 迁移实施账本

创建时间：2026-11-14
最后更新：2026-11-17
状态：P0–P3 scoped 总闸通过；P4 实施中，P5 未开始（不代表完整迁移或发布验收）


## 2026-11-17 Qoder 公共发送入口与持久选项对照

候选 `328cd85c`（tree `e2c9b88e`）已推送。复核 ADR25/37/56/129–131，B级同边界修复：公共sender已经解析的catalog/持久metadata直接传入私有prepared sender，移除再次查目录丢失fallback metadata的路径。缺目录但持久large512000的原公共入口断言在基线c09失败，修正后同一断言通过；保留空数组显式覆盖、null未声明、目录/选项默认规则，不移动权限、Evidence、Context或存储边界，不另开ADR。Rust生产实现本卡未改，不是新建另一种语义。

12份实际公共TS sender/catalog/stream parser向量、36次物理build覆盖缺目录、默认/选定/非法值、null/空/非空覆盖及auto；每个恢复组只查一次目录，非身份正文不变、身份更新、认证所见正文与实际init一致。认证与HTTP是显式mock，不能当真实SDK/网络证据。原生公开Host用同一12份选择完成真实write_file/Grant/ToolResult/Evidence与用量/容量；真实Bash改选后旧请求拒绝、已知16及成功事实保留，新Goal用小档位且不改旧历史。见[公共入口回执](native-cli/evidence/p4-native-qoder-caller-20261117.json)。

最终冻结源码完整原生scoped **456 Rust（含173 Native Episodes）/349根2002次实际TS互读/9PTY**，CI Bun1.2.17，exit0、440.365秒；fmt/clippy/边界与架构/UI通过。featureless release仍为 **17,163,312 bytes、SHA256 `37496a9933404832478ed09a2c89fc497951caff40d0c8efaed915d0ce4c60f4`**，与前候选字节相同；同一保留产物在env-i/PATH无JS下25组Qoder Host通过，58根314次后续互读通过。不是长期内存、真实服务、系统Vault或安装验收。

保留两次中间失败：初次TS null effort与原生Goal off输入不一致，已统一双方显式off并由真实caller重生成，原全等断言保留；首轮全闸172/173通过，150ms固定等待在Host首个容量观察提交前追加历史，保留fixture显示request_preflight、并发user及known16。等待测试复用已有hard-exit测试的index turn_complete与Store锁释放事实后再变更/杀进程，原错误码、一次HTTP及费用断言不放宽；10项重试测试及最终整闸通过。产品并发拒绝/恢复契约没有被修改。

基线c09的[CI43970657817](https://github.com/ly-ccx/Peer-Agent/actions/runs/43970657817)已终态失败：两平台native/build/type/architecture通过；Linux最后Electron smoke在Evidence返回详情时仍隐藏，发生在motion检查前；macOS Desktop测试全部完成，但Test步骤15分钟超时，旧TUI最后停在Goal bridge首项，未确认根因。本机隔离旧TUI879项（878pass/1skip）、Goal bridge10项、实际Electron work-surfaces/Evidence返回均通过；这不证明远端已修复，不称flake，未重跑或削弱断言。全日志、失败报告/图与trace保留。新[CI43978031587](https://github.com/ly-ccx/Peer-Agent/actions/runs/43978031587)独立执行，merge a250fc32 tree与328cd85c一致，尚未全仓绿。

P4仍缺剩余Qoder目录/发送/流变体及真实服务、完整Context/压缩、其余工具/Skill/Plugin/Hook/ACP/headless/命令和混合安装版本恢复；P5–P7未完成，普通Ratatui对话不可发送，长期内存未验收。无个人凭据/任务读取迁移、安装、用户实例重启、默认入口切换、合并或发布，无Bun/Node引擎sidecar。

## 2026-11-17 CI 折叠采集的输入与观察边界

候选 `c09d2bc3`（tree `af216294`）已推送。复核ADR44/129–131与当前动效/验证规范，C级夹具修正，产品与Runtime边界不动，不另开ADR。683b的macOS CI原断言/全日志保留；输入与观察共用6000ms计时，而实际关闭采样直到5900ms才出现，无法保住所需480ms。以原函数不改正文、仅开发导出，在实际DelegatedWork/MotionDetails/原CSS的隔离Electron中加延迟真实派发，再次复现同一deadline断言；不是对原托管CI环境的精确复现或生产动画缺陷证明。

采样Module为两处既有disclosure/panel夹具统一定时和清理：全部真实点击仍须在原6s内完成，最后预期点击另开有界6s观察，保留480ms最小后观察；多余点击不能刷新截止。点击数、中间帧、完整高度跳变拒绝、终态/隐藏/焦点、反向/减少动效均保持，原缺中间帧最多重采一次不增加。7项虚拟时间/跳变测试、真实Electron开合/反向/隐藏Tab/减少动效及晚点击通过；最终晚输入5805ms、后观察483.5ms。严格Desktop+夹具类型检查和architecture/UI通过；早期临时配置放在workspace外丢Node类型解析的错误保留，改为从现有Desktop配置在workspace内解析，没有关类型检查。两张最终图由实施者自审，不称独立/完整Bot体验验收。新测试接入Desktop原CI命令。见[计时修正回执](native-cli/evidence/ci-motion-observation-20261117.json)。

Rust/Cargo/native contracts/verifier与Desktop生产renderer树均与1d796f2a完全一致，原生454 Rust/336根1924互读/9PTY/无JS23组Host仍只作为相同Runtime的scoped证据，不冒充这张全仓绿。1d的[CI43967102253](https://github.com/ly-ccx/Peer-Agent/actions/runs/43967102253)因推送已验证修正而由既有并发策略取消：Linux build/native/type/architecture/Test成功、Electron smoke取消；macOS build成功、native取消，其后未跑，无失败步骤，不记全仓成功。新[CI43970657817](https://github.com/ly-ccx/Peer-Agent/actions/runs/43970657817)独立执行，merge90d3e41c tree与c09d2bc3相同。

后续Qoder caller基线：在c09d2bc3重新build的实际共享TS公共sender上，以自有空目录、认证/HTTP Host mock和真实流解析器运行，持久contextTier=large（512000、tier-large）实际准备正文却无contextTier、max_input_tokens=200000、is_vl=false，原断言确实失败。outer已解析的fallback metadata未传入inner，inner再次查目录得到null；下一B卡复用既有已接受的metadata/显式覆盖契约修复，并补原生Host对照。此证据只证明完整caller的正文参数缺陷，不是SDK认证/真实HTTP/真实Qoder服务或原生平价验收。原始src/旧Node导入尝试未执行目标函数，另留日志，不计行为证据。

继续P4原范围：Qoder完整caller/目录/流变体与真实服务、完整Context/压缩、剩余工具/Skill/Plugin/Hook/ACP/headless/命令及混合版本恢复仍开放；P5–P7未完成，普通Ratatui对话不可发送，长期内存未验收。无个人数据、安装、用户实例重启、入口切换、合并或发布，无Bun/Node引擎sidecar。

## 2026-11-17 Qoder 逐尝试重试与用量/恢复

候选 `1d796f2a`（tree `dd7bc413`）已推送。复核ADR25/37/55–57/129–131，先由知识提交524c9e1登记ADR131/map的逐尝试契约，再接Host。两方言已有界queue/duplicate/transient/connection恢复；冻结非身份正文，每次重建request/session/task和准备端点is_retry、字节/指纹与认证。首次runtime task也为peer-agent:UUID，纯builder默认向量保持。每次尝试的known usage/unknown先入canonical预算快照再等待，等待沿同一取消/续约，下一次复核预算、Goal/MCP/历史及原凭据来源；不重放本地工具。摘要逐次计费但不覆盖容量。准入后来源拒绝可保守增加请求数，不能把该数字当HTTP已发送或远端处理证明。

最终冻结源码完整原生scoped **454 Rust（含171 Native Episodes）/336根1924次实际TS互读/9PTY**，CI Bun1.2.17，exit0、547.023秒；fmt/clippy/边界及架构/UI通过。featureless release **17,163,312 bytes，SHA256 `37496a9933404832478ed09a2c89fc497951caff40d0c8efaed915d0ce4c60f4`**，同一产物env-i/PATH无JS下额外23组Qoder公开Host通过，45个自有根再做236次TS/原生互读。35份实际TS分类/队列等待向量匹配；真实闭环覆盖队列后工具、已完成Shell效果后队列不重放、部分intent丢弃但费用保全、重复/HTTP限流耗尽、连接恢复、预算/unknown费用阻断、换凭据/历史、等待续约与取消、硬退出→旧任务拒绝→幂等恢复→新任务准入。

首轮完整门禁af8c1fc4的171 Episodes有2失败：测试只看到sidecar便SIGKILL，实际杀在index提交内，留下两个空Store锁；并发历史变化落到真实Store CAS，返回CONTEXT_SNAPSHOT_CHANGED，与新helper另一分支的自造错误码冲突。原候选/日志/数据保留。复用Store错误码；测试改等index的turn_complete和锁释放，真实等待点才杀进程，不放大任意sleep。另在原失败数据副本保留诊断、确认原进程死亡后，只维护两个已证明空的孤锁，recover两次成功且不虚构用量，原数据hash未变。**产品不自动抢匿名Store锁，事务中断仍需受控离线维护**，不冒充自动恢复已验收。更早的取消计时器、raw等待估计和lint失败亦保留，原取消速度/效果断言不削弱。见[重试回执](native-cli/evidence/p4-native-qoder-retry-20261117.json)。

基线683b的[CI43957840836](https://github.com/ly-ccx/Peer-Agent/actions/runs/43957840836)已终态：Linux133617013628全仓success；macOS133617013973的build/native/type/architecture/Test通过，Desktop Electron smoke在bot-history-motion-checks:239失败。taskClose首个关闭样本5900ms、末样5930ms，6000ms总计时未给最后真实点击留下所需480ms；仅定位夹具计时边界，未复现该CI环境，不称flake或生产已修复，未重跑/放宽断言。merge7b45f494 tree与683b源相同；旧回执更新该真实终态。新[CI43967102253](https://github.com/ly-ccx/Peer-Agent/actions/runs/43967102253)后因计时夹具修正推送被既有并发策略取消，具体已过/未跑步骤见上；merge3ea1e32a tree与1d796f2a源相同，不称全仓成功。

仍是P4：Qoder完整目录/流变体、持久选项caller差异及真实服务、其余Context/压缩/工具/Skill/Plugin/Hook/ACP/headless/命令、混合安装版本drain与完整总闸开放；P5–P7未完成，普通Ratatui对话仍不可发送，长期内存未验收。无个人数据读取迁移、安装、用户实例重启、默认切换、合并或发布，无Bun/Node引擎sidecar。

## 2026-11-17 Qoder 旧JSON/Bearer端点与环境凭据

候选 `683b601a`（tree `3bd3eba6`）已推送。ADR37/56/129–131复核，ADR131/map先由a70d138登记旧方言与环境来源：目录命中或有非空modelOptions时走准备端点，其余模型走旧JSON/Bearer；不是错误后的认证降级。三个Qoder环境token保留trim后的优先级，获胜时不读磁盘user/machine文件；准备端点仍要求资料，旧端点可用env token或解封的本地token。旧方言不要求准备端点专有uid，但已有类型/大小/expiry继续校验，第三方文件不写回。null选项为未声明，空数组显式覆盖；有错/已知未来QMC/冲突来源不冒充“没有模型”。

来源存在/缺失观察集中进ReadSet，保持普通文件NOFOLLOW/NONBLOCK/CLOEXEC、有界快照、fd/path版本和发送前ModelBinding/环境/expiry校验。捕获设置、凭据owner、端点选择各自负责，构造后只留选中目录元数据。旧body复用同一history/tool transforms直接冻结JSON，Bearer与X-Request-ID/X-Session-ID受保护且sensitive，2MiB上限与实际发送字节指纹不变；显式baseUrl优先，未配置才沿既有model-host/prod/daily/test。两种方言复用原Network与工具Grant/Evidence/账本链，没有新Agent循环或JS/VM fallback。

冻结源码完整原生门禁 **440 Rust（含161 native Episodes）/316根1819实际TS互读/9PTY**，CI Bun1.2.17，exit0、510.710秒，fmt/clippy/边界与架构/UI通过。24个实际TS旧body/header向量、4个官方SDK合成凭据载体匹配。featureless release **17,116,976 bytes，SHA256 `1fd9eeb8b795d8bbceacfb2eca62ee5e1af32face18ccfd05e5c8a0786e5aa57`**，同一产物在env-i/PATH无JS下额外13组Qoder公开Host测试通过；25个自有根再做131次TS/原生互读。17项Qoder测试在release profile再过。已有真实HTTP count/send测试在3个Qoder token同时存在时另过，294个渠道/选项组合、4种wire继续断言无Authorization/X-API-Key串入。

实际覆盖本地/三个env优先级、坏本地文件不能抢占env来源、UID仅准备端点必需、过期/类型否决、原始请求指纹、真实写入与成对Evidence，以及工具成功后目录出现使旧方言停住。两种方言另经真实TLS/认证CONNECT，正确证书成功、错主机名不进模型HTTP，代理/模型认证分离；不完整工具流收到TERM后无效果、socket关闭/保留原历史与账本，独立后续任务可准入。旧b332同一featureless release对未知模型确实报native_qoder_legacy_wire_unsupported，原失败断言/二进制/自有根保留；测试可见性和相对include失败修正，未削弱断言、期限或lint。见[旧端点与凭据回执](native-cli/evidence/p4-native-qoder-legacy-20261117.json)。

基线b332的CI43949887094已核实Linux133589242332/macOS133589242848两平台全仓success，含各自Electron smoke，merge0ae68ff8 tree与源一致。新[CI43957840836](https://github.com/ly-ccx/Peer-Agent/actions/runs/43957840836)已终态：Linux133617013628全仓success，macOS133617013973在Desktop disclosure观察超时失败；merge7b45f494 tree与683b源码一致。具体失败/保全与后续重试候选见上，不称两平台全仓绿。**Qoder队列/连接/瞬态/重复重试与完整发送包装尚未完成**；共享builder默认task_id与实际TS sender每次qoderTurnTaskId的差异须随逐尝试身份/指纹收口。静态追踪另记录TS nested prepared sender在无目录命中时丢持久选项，native当前依已登记选择及实际builder；完整caller平价须在P4总闸前明确，未声称真实服务复现。全部目录/流变体、其余P4及总闸、P5–P7仍开放，普通Ratatui对话仍不可发送，长期内存未验收。仅合成账户/服务，未读个人凭据/任务、未安装/重启用户实例/默认切换/合并/发布。

## 2026-11-17 Qoder 原生账户与准备端点模型/工具闭环

候选 `b3320085`（tree `4012fd0f`）已推送。ADR37/56/129/130/131复核；ADR131与map先由df920ca/91f46b9登记只读第三方账户、来源绑定与认证接线，并以官方模块对照校正COSY认证requestId为独立随机UUID，不复用正文request_id。账户按QODER_CONFIG_DIR/QODER_CLI_HOME/HOME解析，普通文件NOFOLLOW/NONBLOCK/CLOEXEC、有界读取与fd/path双身份复核；坏/超限/过期/换号/退出/配置变更明确拒绝，源文件不写回。现有认证字段复用，缺失时由OS随机与固定官方公钥生成AES-CBC/RSA-PKCS1v15兼容字段；Cosy身份/认证头受保护且sensitive。不是Peer授权或Vault的新格式。

原生factory已接qoder-private准备端点、FREE_INPUT encoder与现有Network/Host。canonical history/Projection经工具配对、相邻assistant合并、双content/contents、schema、effort及contextTier转换后冻结实际编码字节和指纹，prepared request仍限2MiB，计数observed-only。只读本地加密/旧目录及所选模型绑定实际来源。实际工具仍经原Grant/Provider/ToolResult/Evidence/Store；没有第二个执行循环或JS/厂商VM。54份实际TS请求、12份本地目录投影、8份未修改官方模块认证头与4份仅测试RNG固定的运行时字段样本相符；真实HTTP另按捕获的实际正文核验签名。

最终冻结源码完整原生门禁 **428 Rust（含154 native Episodes）/300根1736实际TS互读/9PTY**，CI Bun1.2.17，exit0、470.436秒，fmt/clippy/边界及架构/UI通过。featureless release **17,107,648 bytes，SHA256 `5544caa5d1dd3b7e342b017f625e8025a4c64e186ba4b058c6d348e27680556f`**；该同一产物在env-i、PATH=/nonexistent下额外6组Qoder公开Host测试通过，9个自有数据根另做48次实际TS/原生互读。12项Qoder相关测试在release profile再过。无厂商认证WASM嵌入，host依赖无VM，动态库只有系统/CoreFoundation/iconv。

真实覆盖合成登录→认证→HTTP→读写工具/Evidence；拒绝无效果及后续任务；损坏/仅env token的准备端点认证前置阻断；实际Shell改写合成凭据后阻断下一次请求，保留已有成功Evidence/历史，修复后新任务可运行；官方加密目录选中模型/context档位；外层业务失败包着有效工具的拒绝。首轮完整门禁虽绿，后续反例在同一release真实写出了合成文件，日志/产物/数据根保留；修正为外层与内层先分别校验业务失败，新增10605/103/statusCodeValue公开反例，随后重跑最终完整门禁，没有继承旧绿或削弱工具断言。另保留SSE夹具缺末尾空行、目录整数被转浮点、编译/lint及测试模块发现失败。见[Qoder Host回执](native-cli/evidence/p4-native-qoder-host-20261117.json)。

基线cfdf两平台全仓CI43938893409含各自Electron smoke已成功，merge0cfff93d tree与源一致。新[CI43949887094](https://github.com/ly-ccx/Peer-Agent/actions/runs/43949887094)已核实Linux133589242332/macOS133589242848两平台全仓success，含各自Electron smoke；merge0ae68ff8 tree与源码一致。**Qoder完整队列/连接重试、旧私有端点/env-token路径、全部目录/流变体及真实服务仍未完成**；只有合成本机HTTP账户/服务，不声称Qoder特定TLS/代理、真实账号/OS Vault或安装验收。P4其余及总闸、P5–P7保持开放，Ratatui普通对话仍不可发送，长期内存未验收。无个人凭据/任务读取迁移、安装、用户实例重启、默认切换、合并或发布。

## 2026-11-17 Qoder 原生格式基础（未接 Provider）

候选 `cfdfd40a`（tree `92958346`）已推送。依ADR129–131范围，先由knowledge fe5a6cd/053b481登记第三方凭据/目录读取与有界密码格式、旧载体和传输编码，再实现RustCrypto Module。解封当前AES-128-CBC/PKCS7本地凭据、HKDF-SHA256/AES-256-GCM的QMC v1目录，以及旧明文/base64 UTF-8载体；后两类不会被标成已认证。正文按官方固定字表/美元padding和首尾third换位编码，明确只是混淆。边界1MiB凭据/4MiB目录/8MiB原始body、严格key/block/tag/UTF8/版本/编码校验，部分解码数据与明文归非Debug/Display/Clone的零化owner。只启用锁中已有密码crate版本和zeroize feature，不捆绑/启动SDK、WASM VM或JS。

公开npm1.0.39包完整性校验后，只在隔离开发oracle使用真正认证WASM（SHA256 `15dad38f7d9744dabfdc8a892ebad80d2c8157779f4e33882123ab3c954f04d3`），不运行官方CLI或读取个人账户。65个官方样本（21CBC、21GCM含3空输入拒绝、7旧载体、16body），含9个实际TS消息builder输入，与原生和Node密码原语交叉匹配。四组原生测试另覆盖nonce/密文/tag篡改、错误uid/key、坏块/填充、UTF8、未来QMC版本、非canonical正文、预算否决及随后正确解封。

最终完整原生scoped **410 Rust（含148 native Episodes）/291根1688实际TS互读/9PTY**，CI Bun1.2.17，498.972秒exit0；fmt/clippy/边界/架构/UI通过。release profile四组格式测试在env-i、PATH无JS下再过，featureless CLI 16,705,504 bytes、SHA256 `14bfa423916c9fc6f8136b303144c1c7c66b1cd619cde747fbd7a693e4421d8a`，额外10项既有公开会话命令通过。原生依赖无VM，产物不包含官方WASM。首轮/第二轮clippy及初次Node源导入失败保留，使用原CI Bun解析实际TS，不抑制断言或静态检查。见[Qoder格式回执](native-cli/evidence/p4-native-qoder-formats-20261117.json)。

基线7627两平台全仓CI43931485780含各自Electron smoke已成功；新[CI43938893409](https://github.com/ly-ccx/Peer-Agent/actions/runs/43938893409)已核实Linux133550764577/macOS133550764777两平台全仓success，含各自Electron smoke；merge0cfff93d tree与源一致。**本卡没有接文件读取/账户身份、Model factory或Qoder模型发送**；认证封装/运行时auth字段、完整消息/目录/选项、网络/SSE/队列重试/用量/取消，以及模型→工具→Grant/Evidence仍待完成，当前公开factory仍拒绝Qoder。其余P4与P5–P7保持开放，普通Ratatui对话仍不可发送，长期内存未验收；无个人数据、安装、用户进程重启、默认切换、合并或发布。

## 2026-11-17 原生 doctor / sessions list / 有界 export

候选 `7627d4c8`（tree `8f05f778`）已推送。ADR108/129/130/131 已复核；ADR131/map的展示读取、原子发布与未知回执 A 级补充由6395a575/c52072fb/c4d35111先登记。doctor改为检查实际peer/同目录Helper可执行性、数据根或最近现有父目录及版本，必查失败退出1，不执行Helper/读Vault/建数据根。sessions默认/list只读真实index，原角色/排序/标题不读正文、不后台迁移。export沿实际TS可见消息与v1 stream patch生成脱敏Markdown，不能用canonical执行历史的provisional排除规则替代展示。

Store复用有界JSON Reader，16KiB扫描、每行源1GiB、所选12MiB/65536节点/深度64；捕获有限文件长度，持续追加不延长读取。源版本或损坏/未来/孤patch明确失败。CLI匿名0600 spool、默认no-clobber、force目标CAS与父目录OS短锁/原子rename，拒绝Store/所读源别名；发布前取消保留旧target，rename后flush/回执失败保留新副本并报publication unknown。真实stdout背压/破管道/TERM、取消锁等待、后续显式重试覆盖；不改变grant、Evidence、任务、unknown或模型Context。

最终完整原生scoped门禁 **406 Rust（含148 native Episodes）/291根1688实际TS互读/9PTY**，CI Bun1.2.17，467.896秒exit0，fmt/clippy/边界/架构/UI通过。5个实际TS Store/可见消息fixture、17参数、14脱敏样本匹配。featureless release **16,691,456 bytes，SHA256 `218d34a218cce60792847962db105162cc02e1d5053d3b8c6e29c4b07f0d81ab`**，同一产物额外10个公开会话命令测试通过。五次1,080,033,792字节有效JSONL（10×100MiB工具/3×10MiB可见正文）导出均完整hash匹配且源未变；峰值macOS采样RSS49.23–51.42MiB、约6.89–7.07秒。只是文件导出专项，没有footprint/全进程树/长期交互验收。

首轮整闸因额外无fixture的cargo test重链接同路径debug peer造成109过39败（故障exit0而非77、夹具IdP未收到请求），日志/合成失败Store保留，不称flake。相同真实故障测试用featureless产物可重现失败、冻结fixture产物通过；verify改为先构建并复制/记录fixture hash，再给Host测试固定产物，原断言/期限不动，最终整闸独立重跑通过。另保留ya29断言、clippy与发布成功回执破管道反例，修正并覆盖提交未知后的显式恢复。见[会话壳回执](native-cli/evidence/p4-native-session-shell-20261117.json)。

基线5182两平台全仓CI43916683249（含各自Electron smoke）已核实成功；本候选[CI43931485780](https://github.com/ly-ccx/Peer-Agent/actions/runs/43931485780)已核实Linux133524760580/macOS133524761193两平台全仓success，含各自Electron smoke；merge f3897471 tree与源一致。P4完整总闸、sessions resume/delete/update及其余Runtime/协议仍开放；P5–P7完整退出条件未满足，Ratatui仍不可发送普通对话。无个人数据迁移、安装、用户实例重启、默认切换、合并或发布，无Bun/Node引擎sidecar。

## 当前剩余范围（2026-11-17）

| 阶段 | 当前事实 | 尚待完成 |
|---|---|---|
| P0–P3 | 各自 scoped 总闸通过 | 不代表完整日常 CLI 已可替换 |
| P4 | 实施中；已接原生模型/工具、用量、压缩恢复、MCP transport/auth，以及原生自动刷新、grant/Context续行、连接换代、当前TS发送guard、旧SDK缓存兼容、原生Grok与Qoder两种端点、账户/工具/TLS/取消及Qoder逐尝试重试/计费/等待恢复的本机验证 | 混合安装版本drain与恢复、Qoder完整目录/发送包装/流变体、完整 Context/压缩策略、剩余工具、Skill/Plugin/Hook、ACP/headless/其余命令、真实服务与总闸 |
| P5 | 完整项目代理全链未开始；已有 kernel/reducer 地基不算产品完成 | 主 Bot、队列/调度、委派并行/worktree、Goal/Watch/记忆、问题、核验/签收/交付、Interactive Results 与恢复 |
| P6 | 有终端骨架和局部 PTY 验证；完整验收未完成 | Ratatui 普通对话发送、模型选择/批准、历史/大正文/搜索、草稿/阅读位置恢复及长期内存/响应性 |
| P7 | 有本机候选打包验证；发布切换未完成 | 最终打包/安装更新/签名、多平台和全量发布回归、默认入口切换与旧 CLI 可达依赖退出 |

不能按阶段数量换算完成百分比。当前仍是 P4；P5–P7 的完整退出条件尚未满足。原生 `exec --plan` 的受限 worker 闭环与不可发送的 Ratatui 草稿入口，均不能冒充完整会话。

2026-11-17 原生Grok与基础补全候选 `5182ad5e` 已推送（tree `0966d4fc`）：按实现前ADR131/28/map修订 `2d5e1cf`，`oauth_grok`沿原Responses编码、ModelBinding、Helper CAS/刷新意图与Account提交Module接通，不启动Grok CLI、JS业务引擎或sidecar。显式`models auth`执行一次device grant，有界pending/slow_down轮询、取消和新授权恢复；用户提示只含公开URL/userCode/有效期，实际scope、固定issuer/client与原配置/Vault代分别检查。刷新scope变化保留pending，不重放模型或工具。兼容版本feed有界无凭据读取，6h缓存/24h受限旧值策略；仅426且版本实际变化允许同一prepared原始字节再发一次。ChatGPT账号头归其Provider，不随Responses协议泄到Grok。

完整原生验证冻结在tree `29ea9c09`：**387 Rust /148公开native Episode /291根1688实际TS互读 /9PTY**，CI Bun1.2.17，exit0、420.721秒；之后仅CI作业总预算改动，Rust与资源/脚本不变。全仓typecheck/architecture/UI在新增补全前通过，补全后的Rust由完整fmt/clippy/build/测试验证；最终featureless release **16,508,272 bytes**、SHA256 `1e36dd7aa1799f532349b7b747e0bbdc8aa4d192cb4a5da5713d948e30fd1d68`，额外用同一公开Host测试在固定官方URL/原域名TLS验证下，经强制隔离CONNECT代理走device登录或过期凭据刷新→两次模型请求→真实文件工具/Grant/Evidence。无端点覆盖文件，PATH不可发现Bun/Node，测试证书私钥不在正式产物中。

按已接受ADR108迁移`completions <bash|zsh|fish>`：从实际TS生成三份脚本、帮助与9个参数解析样本，原生入口无HOME/TTY/JS运行依赖，正文仅进stdout、用法错误退出2，不写shell配置。实际Bash可补全models和sessions resume；新增2组公开入口及3项邻接测试通过，正式产物再跑同一2组测试通过。此B级实现不移动能力、授权、Evidence、存储或提示边界。

前候选dc70的CI43899256310已终态：Linux全仓success，Mac首轮无arm64 runner取消；取得runner的重跑通过build/native/type/architecture/Test，最后Electron检查1219秒时触及整个作业45分钟上限而取消，没有报告，不能记全仓绿。原生门禁784秒、全仓测试531秒，同一Linux Electron包808秒。仅将作业总预算改为60分钟，原场景断言、性能预算与单步/动作超时不变；[新CI43916683249](https://github.com/ly-ccx/Peer-Agent/actions/runs/43916683249)已核实macOS133472597563/Linux133472598121两平台全仓success，含各自Electron smoke，merge c70991e9 tree与最终源一致。实际原Desktop生产源码未变的本机隔离全旗标检查（仅await前日志的实验副本）已通过并正常退出：列表12.87ms/搜索21.60ms/收到28.10ms中位数在原100/150/300ms门槛内。该日志副本可能影响调度，不冒充精确CI复现、独立产品审阅；远端通过由上述实际CI单独证明。

原`native_model_auth_unsupported`基线与中间失败保留；首轮整闸通过后审阅发现user_code可等于secret device_code，公开CLI反例真实失败（`.tmp3QMMGP`）。修正为展示前拒绝并保全旧Vault/config，反例通过后重跑完整最终整闸，未借先前绿替代。旧浏览器/MCP、停稳、账本与恢复仍在同一门禁。见[原生Grok回执](native-cli/evidence/p4-native-grok-20261117.json)。6h/24h真实时间老化未soak；真实Grok IdP/模型、OS Vault、旧安装版本drain、完整P4与P5–P7另验，Ratatui仍不可发送普通对话。无个人数据迁移、安装、运行实例重启、默认切换、合并或发布。

2026-11-16 当前TS发送者与旧SDK缓存候选 `dc70fc3c` 已推送（tree `ed6c2ee0`）。按源前ADR132/131 A修订 `cf9540e`：官方SDK真正token HTTP之前，由同一credential目录锁owner核对generation、旧refresh/PKCE和issuer/token endpoint，先经Helper回读验证并发布不可变加密意图；网络等待中不交锁，只有owner能发布最终代。SDK saveTokens仅消费一次匹配提交回执，不再写新代或重算expires_at；拒绝/redirect/损坏/超限/取消/Helper或源变化保留pending，不吞错后DCR、浏览器fallback、invalidate或重试。显式管理authorize purpose只恢复已知pending，保留它直到新code成功；旧code/verifier不能重放。close/disconnect取消并join，管理Host等待清理。

Streamable HTTP及legacy SSE已发tools/call的401/403/redirect不向SDK交出可重放响应；只有本地owned GuardError身份可投影为既有terminal `execution_outcome_unknown`。实际Provider→canonical预算checkpoint/finish保留原pending和unknown，阻止该executor继续模型请求，不拿错误文字当效果证明。实际SDK预读/双请求基线、首轮仅错误文字而缺结构化unknown的回归均已保留。

原生支持旧SDK cache中的issuer绑定，所有同时存在候选须合法一致；仍做新受限发现，不直接信任缓存token endpoint。实际token.scope优先，省略响应scope沿旧grant保存，保留请求偏好与未知cache字段；变化/未知原授权不被新响应洗成成功。真实加密夹具Vault下TS与Rust双向竞争仅一POST，随后原生Grant/ToolResult/Evidence继续；cache-only→native闭环、冲突/null issuer及scope省略冷读均通过。

完整原生门禁在冻结tree `ae80ace4` 通过：**373 Rust /138 native Episode /261根1528实际TS互读 /9PTY**，CI Bun1.2.17，exit0、403.595秒。之后仅TS owned-error→Provider终止投影及回归测试三文件改动，Rust源与release不变；最终tree另通过**67项聚焦测试**、新runtime build、全仓typecheck、architecture/UI及890 packaged imports。相同featureless release 16,431,344 bytes、SHA256 `31eeb1be8199be95580b4bc520b57db37d46642580bd1c39bf1090a5f9560ab0`，额外27组OAuth Host通过。全仓pnpm build/test通过于后续TS细化前，不冒充最终tree完整发布活动。见[当前TS/旧缓存回执](native-cli/evidence/p4-mcp-cohost-and-legacy-cache-20261116.json)。

首轮完整原生门禁130过7败：五项旧刷新夹具无实际scope却返回mcp.read；正常夹具补齐其明确的原grant，新增未知原grant必须pending的反例，scope/TLS/unknown断言不放宽。两项未改模型测试在与全仓JS并跑时超过原8秒停稳界限；原样隔离通过，最终完整原生门禁单独通过，不称原轮绿或flake。新夹具id0、错Helper和错Store代码失败均保留。[CI43899256310](https://github.com/ly-ccx/Peer-Agent/actions/runs/43899256310)已终态：Linux全仓成功；Mac初次runner容量取消，重跑原生/构建/类型/架构/Test通过，最后Electron遭整作业45分钟上限取消，未获全仓成功。merge e3965514 tree与最终源一致。事实、日志与5182ad5e的作业预算后续见上及Grok回执；321d0ccb两平台全仓绿已单独核实，不能移作本候选结果。

旧运行/安装版本drain仍未证明；本卡源码不能倒过来保护已加载旧代码。P4总闸与其余Provider/Context/工具/Skill/Plugin/Hook/ACP/headless/命令、P5–P7仍待完成；Ratatui仍不可发送普通对话，长期内存未验收。仅合成服务与加密夹具key，未验真实IdP/模型/OS Vault/安装；无个人数据迁移、安装、运行实例重启、默认切换、合并或发布，原生CLI无Bun/Node引擎sidecar。

2026-11-16 原生MCP自动刷新候选 `321d0ccb` 已推送（tree `61dd24c4`）。按先登记ADR132/131 A级修订58aa2c9与跨代脱敏实施复核731539d，实际grant后才解封凭据/访问IdP；execution内存epoch只接受OAuth owner持锁真实发布，逐次核对真实Store与registry，才规范化单一credential来源以复核原grant。Goal、args、policy、lease、祖先/角色、执行绑定和其它来源仍检查；不改写grant事实，不把epoch持久化成权限或秘密。Context继续同一已验证代。每server逻辑owner有界排队，使用当前请求的Host port；旧Connection停稳/join后才刷新与重初始化，stdio不自动重启，call_tool_once不重放。

冻结完整原生scoped **370 Rust /135 native Episode /254根1480实际TS互读 /9PTY**，CI Bun1.2.17，exit0、402.291秒。featureless release 16,429,936 bytes、SHA256 `f5754b065cf0533a9a60902bcacfb67929de0936d8276d80c9ff2f4825c97381`，额外24组OAuth Host通过。过期→唯一刷新→两次真实工具/原grant/Evidence→下一模型请求、实际长工具调用中的自然到期换代、scope扩大/收窄拒绝、拒绝不读Helper/访问IdP、policy/registry/外部凭据变化、真实加密Vault+合成key、严格TLS数值OAuth CONNECT与普通MCP主机名路由均验证。TERM保留意图但证明确认工具not_dispatched，显式重登后新canonical任务成功且旧历史不变；KILL恢复必须保留unfenced_external unknown，不能凭credential pending猜未派发或重放。

提前捕获未提交自动刷新版本的跨代旧token回显泄露，实际旧binary/hash和失败历史保留；最终逻辑owner用原64值/256KiB有界可零化集合保护接触/注入的旧新凭据及代理值，超限停止owner后续派发，epoch不持秘密。还保留新夹具把initialized通知计为initialize、错误Store代码假设、以及把OAuth数值规则误用于普通MCP的失败；原预期、权限/TLS/unknown断言不放宽。见[自动刷新回执](native-cli/evidence/p4-native-mcp-auto-refresh-20261116.json)。

基线fcf06bc2的Mac CI在后续coordination-conformance遇到status0 stdout的JSON未结束；本机80次原始Bun1.2.17真实Store探针未精确复现，不能叫flake。5bbbd0ed只把该开发夹具完整响应交给自有文件后读取，保留原1MiB界限、timeout和55项断言；Bun/Node各55项通过，首个numeric fd+encoding的Bun RangeError也保留。[CI43879494376](https://github.com/ly-ccx/Peer-Agent/actions/runs/43879494376) Linux全仓success含Electron smoke，Mac因未取得托管arm64 runner容量取消未执行。见[stdout夹具回执](native-cli/evidence/ci-coordination-stdout-20261116.json)。新[CI43885810034](https://github.com/ly-ccx/Peer-Agent/actions/runs/43885810034)两平台全仓success已核实（Mac133363511130/Linux133363511412），含各自Electron smoke；merge58a46f6a tree与源码相同。之后才推进当前TS发送guard与旧缓存兼容，不把本轮绿灯继承给下一候选。

原生刷新要求实际payload中有pinned issuer/client/scopes/refresh token；旧发现缓存独有绑定目前要求显式auth，不能冒充透明旧OAuth平价。当前TS已预读发送guard和安装版本drain仍必需；本卡epoch不阻止已预读TS请求。P4其余和P5–P7仍未完成，Ratatui仍不可发送，无完整长时内存验收。仅本机合成服务/密钥，未验真实IdP/模型/OS Vault/安装；无个人数据迁移、安装、运行实例重启、默认切换、合并或发布，无Bun/Node引擎sidecar。

2026-11-16 MCP刷新未知状态候选 `fcf06bc2` 已推送（tree `ef7d9dc8`）。按先登记的ADR132/131 A级修订（decf85a/7a5e981），在SDK刷新前先经Helper写入、回读核验不可变加密意图并持锁发布；移除普通oauth.tokens视图，元数据仅投影recovery_required。相同owner推进自身binding，成功才发布最终token代。已登记后的拒绝、超限、取消、registry/Helper/owner变化均保留意图与旧slot，不恢复或重放旧refresh。Rust工具/refresh、当前Desktop冷读/patch和旧代保存回调阻断；显式原生PKCE/state/code重登后原ready任务可经真实Grant/ToolResult/Evidence继续。未知/损坏意图连auth也拒绝并原样保全；KILL留下孤锁，不偷锁。

最终完整原生scoped **361 Rust /126 native Episode /242根1391实际TS互读 /9PTY**，CI Bun1.2.17，exit0、373.267秒。featureless release 15,667,584 bytes、SHA256 `5e305dfa12cf94d1e649f9fd0cd29f4a5a7c89f25b7d552743b3e1064124e8ea`，额外15组OAuth Host通过，含真实加密Vault/锁+合成key的中断、Desktop冷读阻断、重登与工具Evidence。其余故障用有界v1 Helper夹具，不冒充OS安全存储。2项持锁publish Store测试、16项Desktop Store、8项实际模型网络及architecture/UI通过。

首次冻结原生门禁360项虽过，后续release在socket关闭断言失败；保留失败与旧源码基线，未叫flake。控制实验发现普通CONNECT夹具漏计真实TCP RST，且3秒空闲截断在5秒预算内的4秒合法TLS隧道；修正为有限Tokio owner/双向copy/取消与join，客户端读侧只计真实EOF/reset，不把上游半关闭/本地清理/超时当关闭。原关闭期限、TLS及断言不放宽，同一release哈希通过15组后冻结最终tree重跑完整门禁。见[刷新意图回执](native-cli/evidence/p4-native-mcp-refresh-intent-20261116.json)。

基线4690766c的Linux全仓CI通过；macOS因GitHub runner容量不足未执行，不称两平台全仓绿。新[CI43875783285](https://github.com/ly-ccx/Peer-Agent/actions/runs/43875783285)已终态：macOS133328321354在后续coordination-conformance解析stdout失败，Linux133328320720在修正推送后由既有并发取消；merge10cbd6fa tree与源码相同。失败与5bbbd0ed修正见上，不称全仓绿。下一项仍是运行时自动刷新、已预读TS发送guard、原grant/Context代际延续与旧连接停稳替换；不能用本卡冷读/CAS宣称拦住已发/预读TS请求。P4其余与P5–P7继续待办，Ratatui仍不能发送，无长期内存验收，无安装/重启/个人数据迁移/默认切换/合并/发布，无Bun/Node引擎sidecar。

2026-11-16 验证夹具修正候选 `4690766c` 已推送（tree `c6c875cf`）。85dc28e3 的 CI43865232749：Linux133291958683在原生OAuth HTTPS代理场景失败；macOS原生/build/type/architecture/Test通过，后续Electron smoke在修正源码推送后被既有并发策略取消，不能记全仓绿。实际控制复现：旧TLS夹具在生产5秒CONNECT预算内等待4秒便丢隧道；修正为有owner的Tokio TLS、双向copy、有限并发与取消/join，原产品期限及断言不变。该复现证明夹具缺陷，不等于精确复现远端调度原因。合成代理trace写入受marker核验的CI证据目录。

最终本机完整原生门禁 **352 Rust /119 native Episode /232根1323实际TS互读 /9PTY**，CI Bun1.2.17，exit0、357.123秒；featureless release 15,632,704 bytes、SHA256 `c87083cac172c05084ef09618d63048f0347302073449986d6afc7719a323d41`，与85dc产物字节相同，另5组OAuth Host通过。新[CI43869546961](https://github.com/ly-ccx/Peer-Agent/actions/runs/43869546961)已终态：Linux133306984261全仓success（含Electron smoke）；macOS133306985019因未取得托管arm64 runner而取消，GitHub容量注释已保留，不能称两平台全仓绿。merge411da5dc tree与源码相同。见[夹具修正回执](native-cli/evidence/ci-native-https-proxy-fixture-20261116.json)。本卡仅C级验证修正，未改变产品边界，未实现MCP运行时自动刷新；P4总闸与P5–P7仍待完成。

2026-11-16 MCP OAuth原生网络候选 `85dc28e3` 已推送（tree `df1ebeab`）：沿ADR132既有数值连接/原主机TLS合同，接线前复核6364740/d687a6c，B级实现同一Native Network路由与PEM/DER根选择。官方SDK继续编码发现/PKCE/state/issuer/resource/DCR与token；本地批准DNS/IP（最多64），直连或HTTP(S)代理仅连接批准的数值目标，保留origin Host和严格TLS名称，代理认证不进入origin。固定30秒操作、5秒建连/TLS/CONNECT、256KiB body、32KiB head/100字段及1MiB响应；driver和exchange由同一future持有，无detached driver、自动切路或token重放。挑战只取有界头，不等待无限SSE body。

冻结原生scoped **351 Rust / 118 native Episode / 232根1323实际TS互读 / 9PTY**，CI Bun1.2.17，exit0、396.469秒。featureless release为15,632,704 bytes、SHA256 `c87083cac172c05084ef09618d63048f0347302073449986d6afc7719a323d41`，额外5组实际OAuth代理Host场景通过；合成私钥不在产物。9组OAuth公开CLI、5组地址/真实socket测试、architecture/UI及fmt/clippy通过。真正的TLS代理登录/刷新→加密Vault→模型/工具Grant/Evidence、禁止元数据目标、混合DNS/64界限、HTTP(S)代理与NO_PROXY、错主机/未知根、redirect/body/head限制、SIGTERM token交换与socket EOF/锁释放、显式重登后原ready任务继续均验证。取消保留已发刷新事实和原generation，不自动重放或声称旧refresh仍可用。

真实旧release即使配CA/代理仍发现失败的现场保留。测试还证明hyper max_buf_size单独可能接受完整超限head；保留原断言并加parser发布最终响应前的IO读预算，1MiB精确边界仍成功，informational heads不绕过。初版API假设、测试临时借用和误把credential取消当exec exit1的尝试均保留；采用既有精确exit4，不放宽权限/TLS/unknown断言。见[OAuth原生网络回执](native-cli/evidence/p4-native-mcp-oauth-network-20261116.json)。

基线2c071885的[CI43859827036](https://github.com/ly-ccx/Peer-Agent/actions/runs/43859827036)两平台全仓success（含各自Electron smoke）已核实后才推送；原run未取消/重启。新[CI43865232749](https://github.com/ly-ccx/Peer-Agent/actions/runs/43865232749)已终态：Linux133291958683原生OAuth代理测试失败、macOS133291959134在Electron smoke取消，merge f7502d2b tree与源码相同；失败与4690766c修正见上。本卡不是P4总闸：MCP运行时自动刷新/grant continuation、Grok/Qoder、完整Context/压缩策略、剩余工具/Skill/Plugin/Hook、ACP/headless/原命令、混合版本drain仍待完成；P5–P7完整退出条件未满足，Ratatui仍不能发送，无长期内存验收。仅本机合成IdP/模型/代理及测试加密Helper，无真实IdP/模型/VPN/OS Vault/安装验收，无安装、重启、个人任务迁移、默认切换或发布，无Bun/Node引擎sidecar。

2026-11-16 全仓CI验证修正候选 `2c071885` 已推送（tree `d342880a`）：1495b867 的 CI43855704882 原生门禁/build/type/architecture/Test两端通过；macOS全仓success，Linux最后Electron smoke在updater-minimize-checks第8行报`Resulting promise was garbage collected`，不能记全仓绿。只将该隔离夹具的安装和最后计数改走已有main command/receipt，不改产品UI/更新/Runtime，不加重试、不吞错。3组动画/缩减动效、真实第四次调用快速完成、最终计数4、错误恢复和真实进程退出在本机隔离Electron通过；具体脚本hash绑定提交，其他JS/UI源不变。实际Linux失败日志/Source/工件身份保留，本机未精确复现该VM GC，不能称flake或已通过Linux。[修正CI43859827036](https://github.com/ly-ccx/Peer-Agent/actions/runs/43859827036)已核实Linux133273408424/macOS133273407898两平台全仓success（含各自Electron smoke），merge91bed719 tree与源一致。见[CI夹具回执](native-cli/evidence/ci-updater-control-20261116.json)。后续原生OAuth数值代理候选85dc28e3见上，P4总闸及P5–P7仍未完成。

2026-11-16 原生普通 MCP 网络候选 `1495b867` 已推送（tree `9f7b463c`）：先登记并推送 ADR132 的 A级网络补充（ac6896a），再接同一 Native Network。实际旧 SDK transport 使用默认 fetch，不能冒充模型专用策略已在旧 MCP 落地。Streamable JSON、Streamable SSE、legacy SSE 的逐物理 GET/POST 均选择 env/NO_PROXY/macOS 路由和严格额外/系统根信任；前置构造完成才记 tools/call 已发送，不重试/redirect/fallback。仅选中代理的有界可零化秘密集合在结果入 Context/历史/Evidence 前脱敏，isError 协议真值独立保留。

冻结原生 scoped **341 Rust / 113 native Episode / 222根1261实际TS互读 / 9PTY**，CI Bun1.2.17，exit0、359.918秒。featureless release 14,906,224 bytes、SHA256 `394fadd315b9e565613dc3a17a9e03767e01cd9da109a10a6f0c9f685594764c`，额外5组真实MCP网络Host测试通过；合成私钥不在产物，architecture/UI及fmt/clippy通过。真实代理认证（含HTTPS代理转发HTTP）、NO_PROXY、TLS未知根/错主机、显式CA修复、凭据回显、双向控制POST与SIGTERM实际socket EOF通过。已发调用unknown保留并继续阻断原工作区；独立范围后续文件任务成功且原unknown/历史不变。旧release显式CA仍无法MCP初始化的失败、reqwest HTTPS转发不附认证的实际失败、测试误用类型/工作区/证据字段的尝试均保留，未弱化原权限或TLS/unknown断言。详见[普通MCP网络回执](native-cli/evidence/p4-native-mcp-network-20261116.json)。

本卡不放宽 MCP OAuth 地址政策；其受限 HTTP Adapter 仍不接环境代理。下一项须实现本地批准 IP 后数值 CONNECT、原域名 TLS/Host 和同一信任策略，防止代理重解析绕过；其余P4与P5–P7继续待办，Ratatui仍不可发送，长期内存未验收。仅隔离本机合成服务，无安装、重启、个人任务迁移、默认切换或发布。基线9d09192b的[CI43848554075](https://github.com/ly-ccx/Peer-Agent/actions/runs/43848554075)两平台全仓success（含各自Electron smoke）已核实，原run未取消/重启，完成后才推送本卡。[新CI43855704882](https://github.com/ly-ccx/Peer-Agent/actions/runs/43855704882)已终态：Linux133259289639最后Electron smoke失败、macOS133259290066全仓success，merge f130fbea tree与源码9f7b463c一致。失败及2c071885局部验证修正见上，不以本地scoped冒充全仓success。

2026-11-16 原生模型网络候选 `297ba570` / `9d09192b` 已推送（tree `9ca1777d`）：依先登记的ADR50实施复核（知识43a77a0）沿129/130/131做B级迁移，无新增授权/Evidence/Context边界。模型生成、冻结count和ChatGPT/Google交换/刷新共用Native Network Module，保留原环境优先/NO_PROXY精确host及后缀规则、逐请求macOS scutil回退和附加根证书选择；显式extra CA有界普通文件，保留Rustls公共根及主机名/TLS验证。OS查询为固定程序/参数、有界输出/2秒查询与清理期限；取消/超限/超时后实际子进程回收和后续查询通过。普通合成测试显式绕开个人代理，专门网络测试选择实际隔离HTTP/HTTPS/CONNECT代理，不修改系统信任。

完整冻结候选原生scoped **334 Rust / 108 native Episode / 212根1186实际TS互读 / 9PTY**，exit0、330.352秒，log SHA256 `33a0399ca24dca6f9eb19e144dbe0611a69ffd547c04507bff55edb6dc32218b`。38组真实TS route、4组scutil、3组指纹/证书选择及26项旧TS网络测试通过；7公开CLI网络场景涵盖真实代理鉴权、NO_PROXY、TLS/错主机/未知根、1MiB/编码/目录/FIFO拒绝、修复后任务、count/send和仅一次OAuth刷新→真实工具Grant/Evidence。19原生账号回归、fmt/clippy/architecture/UI通过。featureless release为14,811,216 bytes、SHA256 `f5cb2f84f590b06f7bef9704ec19c0a3ab4539858aa56849463293f2a900d2da`，额外6项真实网络Host测试通过，合成私钥不在产物。变更仅Rust/开发夹具，未为未变的JS/TS产品源码重跑本地整仓pnpm test/typecheck；旧候选全仓CI已绿，新候选独立验。详见[原生模型网络回执](native-cli/evidence/p4-native-model-network-20261116.json)。

实际复现旧46511513忽略坏PEER_EXTRA_CA_CERTS而继续模型/工具，失败根.tmpY0evv2保留；修复明确请求前阻断且同一ready任务修正后继续。TLS夹具最初被本机LibreSSL默认签成ecdsa-with-SHA1，OpenSSL verify虽成功但Rustls正确拒绝；原完整PKI与失败日志保留，显式SHA256签名修复夹具，生产验证不放松。新query PID marker非原子和私有测试helper误用的中间失败保留；已修复、原断言与期限不弱化。OAuth前置意图仅在证明确未send时条件恢复，真正发送后的未知继续保全。

首轮297ba570的[CI43846561319](https://github.com/ly-ccx/Peer-Agent/actions/runs/43846561319)两平台均在Native scoped的network-contracts比较失败：夹具误取运行时rootCertificates[0/1]，CI Bun1.2.17与本机1.4.2数据不同。已用CI版本实际复现；9d09192b只将输入固定为入库合成公开证书，仍由真实TS筛选器生成expected，原断言不放宽。两版Bun对照和CI版本完整原生门禁通过，最终产物字节与已验收的6项release测试相同；初验与最终tree、失败和hash均在回执保留。

基线46511513两平台全仓CI（含Electron smoke）success已核实；最终[CI43848554075](https://github.com/ly-ccx/Peer-Agent/actions/runs/43848554075)已核实Linux133234880361/macOS133234880280两平台全仓success，含各自Electron smoke；merge bf745936 tree与源码相同。本卡只完成模型路由/信任切片，MCP普通transport及OAuth的网络/地址政策、完整Provider/Host恢复策略、Grok/Qoder、完整Context/压缩、剩余工具/Skill/Plugin/Hook、ACP/headless/原命令、混合安装版本drain和P4总闸仍待完成；P5–P7未完成。仅本机合成代理/TLS/IdP/模型，不冒充真实VPN切换、正式模型/IdP/OS Vault、多平台安装或长时UI内存验收；Ratatui仍不能发送。无安装、重启、个人任务迁移、默认切换、合并或发布，无Bun/Node引擎sidecar。

2026-11-16 原模型目录与OAuth提示恢复候选 `46511513` 已推送（tree `a09a4c61`）：依先登记的ADR131范围/恢复/环境身份修订（a986a18 / 7a36114 / 7431edb）做B级接线。原 `models` 的12组真实TS入口对照、`PEER_MODEL_*` 独立来源和off/default wire已接；显式来源绑定不会把环境key交给已有文件渠道。实际canonical Host→模型流→工具→Grant/ToolResult/Evidence及拒绝场景通过，无Helper或JS引擎需求。`models reconcile <configured-channel-id>`只从真实Vault重建三项非秘密提示；auth/logout分别返回已知凭据结果和metadata状态，失败不回滚或重放登录，status/list仍只读。实际Store超限、配置owner被置换、pending/损坏/错误provider/不可解密、重复无写入、后续显式修复，以及自动刷新提示失败后真实工具闭环均验证。

最终冻结候选完整原生scoped **324 Rust / 101 native Episode / 202根1134实际TS互读 / 9PTY**，log SHA256 `60cf7d49f514ffcb8ec71201197dad8fbc1ad28b362ab6d3751e12f473a3af59`。真实Desktop/TUI跨HTTP提示/endpoint/auth/header绑定8场景、24次加密Vault CAS通过；全仓types、architecture/UI、887打包imports通过。完整pnpm test退出0、354.946秒、14包及最后升级/降级矩阵通过；开始tree0a57b3e5与最终tree差异仅PTY夹具，业务源码和pnpm测试源码不变，最终完整原生重跑覆盖夹具。featureless release为14,582,624 bytes、SHA256 `49d27eff8ad77e118b875275382328ab07c626b65d6830e3e691f0b2a334052b`；额外12模型列表、3环境执行与2真实Vault修复Host测试通过，测试端点marker不在产物。详见[模型目录与提示恢复回执](native-cli/evidence/p4-model-catalog-projection-20261116.json)。

首轮完整原生在最后PTY的PID文件存在但JSON尚未写完处失败，且清理wait期限触发；失败现场保留，进程表确认自有子进程已结束，原运行实例未动。修正为PID/status原子发布和清理失败仍关闭fd/保存ANSI，原期限、退出与终端属性断言不变；9PTY聚焦及最终完整重跑通过。两处旧“登录不写metadata”的阶段断言改为完整文档只允许三提示投影；种子历史非空的测试错误改为原历史精确不变，实际授权/Evidence断言保留。

基线c8654dd6两平台全仓CI成功已核实后才推送；[CI43839577892](https://github.com/ly-ccx/Peer-Agent/actions/runs/43839577892)已核实macOS133204605842/Linux133204606470两平台全仓success，含各自Electron smoke；merge72e41602的treea09a4c61与46511513相同。本卡仍不是P4总闸：混合安装版本升级/drain、Grok/Qoder、代理/证书、完整Context/压缩策略、剩余工具、Skill/Plugin/Hook、ACP/headless/原命令，以及P5–P7仍待完成。仅合成IdP/模型与加密KeyStore，不冒充正式IdP/OS Vault/真实模型或安装验收；交互Ratatui仍不能发送，无1GiB/四小时完整UI验收，无安装/重启/个人任务迁移/默认切换/发布。

2026-11-16 配置/Vault短提交候选 `c8654dd6` 已推送（tree `1ba940c5`）：依此前 `dc238b2` ADR131做B级接线，未移动权限/Evidence/Context或Helper协议边界。实际复现e632旧原生logout在别的config写者持锁时仍删除Vault并返回0；失败隔离根 `.tmpmlfjYa` 保留。Native auth/status/logout与模型OAuth读取、前置意图、最终CAS改为config→Helper短段；浏览器/HTTP等待释放锁。Store finish检查原源版本和owner，不改配置；异步零等待争取+Tokio期限/取消无遗留worker。SDK由实际Desktop/TUI宿主传入相同短事务，13次真实加密Vault CAS证明持锁，HTTP期间另一配置Store可进入。

冻结源码完整原生scoped通过 **311 Rust / 93 native Episode / 182根1034实际TS往返 / 9PTY**；14项原生登录聚焦、17项OAuth SDK测试、全仓types、architecture/UI、887打包imports通过；完整pnpm test退出0、363.254秒，14包与最后升级矩阵通过，退出回执绑定tree1ba940c5。公开CLI验证持锁logout不改密文、回调后等待可取消且不交换code、刷新后无法提交保留原pending、显式原生重登与新canonical任务可继续。Native log SHA256 `d7c54b517e9045ae7b728108720d2088c9db7f799930ea32efbbd5de88b9039c`，featureless产物SHA256 `3ba3b80778e0c4aa1a89ad86c48d77d1417898f6ec6d1bc1a9f242e20bcea650`。详见[短提交回执](native-cli/evidence/p4-model-config-vault-20261116.json)。

基线e632120f的CI43823605671 Linux133152103303/macOS133152103586均全仓success，含各自Electron smoke，merge848671e3 tree与源一致；确认终态后推送本卡。[CI43828693350](https://github.com/ly-ccx/Peer-Agent/actions/runs/43828693350)已核实macOS133168487356/Linux133168487738两平台全仓success，含各自Electron smoke；merge1e1465c8的tree1ba940c5与c8654dd6相同。A修订a986a18校正新增CRUD的范围偏差；7a36114先登记后续提示重建/reconcile，这两项不被当作本卡已实现功能。接下来补原models列表和环境配置、真实Vault提示重建/恢复及剩余P4。普通交互聊天、P5–P7、真实平台/模型、混合安装版本drain均未验收；无安装、重启、个人数据迁移、默认切换或发布。

2026-11-16 范围复核：从实际 `cli-argv.ts` / `cli-models.ts` / `cli-model-lines.ts` / `model-config.ts` 确认，原CLI的 models只列出模型，独立模型配置通过PEER_MODEL_*；原CLI没有整套渠道/模型CRUD命令。此前将“完整原生CRUD/账号创建命令”列为必要退出条件，扩大了原方案 §6 “以实际argv registry为准”的范围。ADR131已在后续命令实现前作A级澄清并登记map：优先补原models、环境模型来源、原有选择/auth与metadata恢复；配置/Vault共锁、条件恢复、混合旧安装版本drain及全部原功能仍必须交付。历史回执保留原范围判断，不反写为当时已完成；本次不是把缺失功能删出迁移目标，P4总闸仍未通过。

2026-11-16 模型配置写入候选 `e632120f` 已推送：先于源码登记 ADR131 A级配置Store写入所有权（知识 `dc238b2`），原生 `ModelConfigStore` 与当前Node/ Desktop参与同一真实目录下的mkdir锁、相同原文件/身份revision和条件原子替换。完整同步 read→mutate→write及读取时迁移受锁保护；坏JSON、未知版本/超限保全原文件，不再当空配置覆盖；保留未知root字段和旧providers envelope。异步诊断网络期间释放锁，提交时只修改仍匹配原配置的对象；价格回填在网络后锁内重读。配置rename后目录同步失败时保留实际Vault/config并报告unknown，不无条件回滚旧凭据。

真实Desktop公开CRUD与Rust Store跨进程竞争，20次渠道/模型创建与30次原生更新全部保留，双端revision相同；新13项互读与81项配置聚焦通过。冻结tree `41ae5d1f`完整原生scoped通过 **306 Rust / 90 native Episode / 179根1018实际TS往返 / 9PTY**；全仓类型、IPC411/445/359、architecture/UI与887打包imports通过。完整 `pnpm test` 真正exit0、364.379秒，退出回执绑定同一tree；14包和最后升级矩阵全部通过。Native log SHA256 `58f48264c1611b943b740bc4fe6fa8b944f2d92127b4ea2d15de7df8bbd9868d`，featureless CLI SHA256 `d77f18dc649cd9c515bc9b6def022ac09ac55f686d65c4974debbd91510c46d1`。见[配置写入回执](native-cli/evidence/p4-model-config-writer-20261116.json)。

保留真实竞争的mkdir已存在→lstat时owner已释放的ENOENT，修正为原期限内重争取；没有增加timeout或放松断言。完整回归还复现Helper测试握手文件存在但JSON尚未写完的EOF，失败隔离根保留；只把测试marker改为完整原子发布，原cancel=4、未启动MCP、kill/reap断言不变，聚焦与完整重跑通过。目录同步注入首次命中合法read-time迁移，改为确认新凭据真实写入后才触发；编译/类型推断中间失败与最终修复均记入回执。

基线54e02063的[CI43818809913](https://github.com/ly-ccx/Peer-Agent/actions/runs/43818809913) Linux133136880644与macOS133136881114均全仓success，含各自Electron smoke；merge150b4b9a tree与源码一致，确认终态后才推送下一候选。新[CI43823605671](https://github.com/ly-ccx/Peer-Agent/actions/runs/43823605671)Linux133152103303/macOS133152103586均已全仓success，含各自Electron smoke；merge848671e3 tree与e632一致。

这张卡仍是共享Store地基和当前写者接线，不等于完整原生配置CRUD/账号创建命令。下一步将native auth/refresh/logout短提交与TS凭据管理接入同一config锁、补齐配置/Vault联合条件恢复及提示重建；不跨网络等待持锁。混合旧安装版本drain、其余P4与完整P5–P7继续待办。无真实IdP/OS Vault、多平台安装、完整交互与长期内存验收；未安装、迁移个人数据、重启或发布，无Bun/Node引擎sidecar。

2026-11-16 原生模型账号候选 `54e02063` 已推送：先登记 A 级 ADR131/28/map（知识 `0b29cad`），再接 `models auth/logout/status <configured-channel-id>`。ChatGPT/Google 采用真实 TS 冻结的 PKCE 身份与端点、外部浏览器 URL、自有有界 loopback、加密 Helper snapshot/CAS；迟到登录/退出/配置变化不覆盖新代，未知提交用真实 status 对账，不重放 code。`oauthConfigured` 仅是提示，已登录但提示过期不再阻止模型准入；配置原字节不改。共享 callback Module 保留 MCP 原限制。实际原生 CLI→本地 IdP→加密 Vault→模型/工具/Grant/ToolResult/Evidence 通过，含拒绝、错误回调、超时、取消、旧 Helper、丢回执和后续准入。

冻结源码本地原生 scoped 通过 **305 Rust / 90 native Episode / 179 根 1018 实际 TS 往返 / 9 PTY**；2 组真实 TS browser flow、6 refresh、5 subscription request、77 context choices 一起核对。featureless release 14,468,976 bytes，SHA256 `9aa5fdafd490a1be9c6a57921b9566bc1a3cbcef07f2ecf2dd753de62b0a6d1e`，无测试端点 marker；无 Node/Bun 的 PATH 下实际 release+加密 Helper status/logout 四场景通过。全仓 type、IPC411/445/359、architecture/UI、886打包 imports通过；本地 `pnpm test` 14包均 Done、无失败，末尾升级矩阵通过。原 exec handle 在上下文压缩中丢失，未虚构 shell exit code；实际进程在末尾通过后均已结束，完整日志摘要与 hash保留。详见[原生登录证据](native-cli/evidence/p4-native-model-login-20261116.json)。

前候选 `aea02893` 的 CI43809352936 已核实两平台 **failure**，相同5个高层OAuth测试替身缺新接口，152项原文件修复后通过。全仓本地还暴露 Watch墙钟基准在并发文件负载下超500ms（原144次读）和 Vite测试fixture不允许共享依赖真实路径；前者保留原阈值/读数断言、相同8个glob覆盖，调整为265行为文件后独立跑原基准，故障自测证明失败不吞；后者仅允许测试fixture读取确切SDK入口。原失败、helper取消退出码和token_type缺口均保留，并在完整重跑中验证；不声称产品Watch性能已修复。新候选[CI43818809913](https://github.com/ly-ccx/Peer-Agent/actions/runs/43818809913)Linux133136880644/macOS133136881114均已全仓success，含各自Electron smoke；merge150b4b9a的tree fe02670b与54e02063完全相同。

完整配置CRUD/写入所有权/提示恢复、混合旧安装版本升级与drain、其余P4以及P5–P7继续待办；正式IdP/OS Vault、多平台安装、完整交互与长期内存未验收。无安装、个人数据迁移、重启或发布，原生CLI无Bun/Node引擎sidecar。

2026-11-16 当前宿主 OAuth 刷新协调候选 `aea02893`：依 ADR0001/28/37/48/129–131 做 B 级接线，沿已接受的加密前置意图/CAS，不新增权限、Evidence、存储格式或 Context 边界。SDK 在真实 token 读取时用 WeakMap 保留 Vault 记录代，复制或修改对象不能伪造回执；同值 set 也使预读快照失效。Desktop 请求解析/模型目录、旧 TUI Responses/Gemini/额度刷新统一在远端前争取原意图，仅提交自己仍持有的代；自动刷新不再无条件写回或因元数据错误回滚旧 refresh。新鲜旧 Helper 可继续读，过期先拒绝升级；保留未知字段与相同 64KiB 上限。宿主刷新 POST 禁止重放和重定向、15秒整响应取消，沿既有代理/证书 Adapter。额度失败不继续使用预读 access，也不把 unknown 虚构成 token 已过期。

实际复现 `505ac8e4` 的旧 resolver：真实加密 Rust Vault 在预读后写入 native 等价占用，旧代码仍发 1 次重复 HTTP；当前代码为 0。实际 Desktop/TUI/SharedSelection→加密 Vault→HTTP 覆盖单 owner、迟到登录/退出、停用、未知结果、丢提交回执、窄视图保留原代及后续准入。原生 full scoped 重跑通过 291 Rust / 79 native Episode / 157 根908互读 / 9PTY；SDK26、Desktop82、TUI34、Runtime27、全仓type、IPC411/445/359、architecture/UI与886打包imports通过。首次 full scoped 暴露 Helper 1秒期限内未到 fixture 启动标记（0个）的测试前提失败；保留日志，不称flake。测试时钟先确认真实子进程，再推进同一1秒并验证kill/reap与后续准入，未修改生产deadline；6聚焦与完整重跑通过。完整回归开始后仅将额度错误收紧为 fetch_failed，5聚焦复验，避免假称过期。详见[刷新协调回执](native-cli/evidence/p4-model-oauth-coordination-20261116.json)。

这仍不是 P4 总闸：当前源码入口已接同一协议，已经运行的旧二进制/预读宿主和外部SDK不会自动升级；实际双宿主执行、升级/drain与默认共享域完整验收仍缺。配置写入所有权/提示恢复、原生浏览器登录及其他P4、P5–P7继续待办。原生CLI产物字节未变，无Bun/Node引擎sidecar，无安装/重启/个人数据迁移。基线505ac8e4的CI43806200856 Linux全仓success；macOS最后smoke在新源码推送后按既有concurrency被取消，未观察到失败step，但不能记全仓success或解释未结束原因。新[CI43809352936](https://github.com/ly-ccx/Peer-Agent/actions/runs/43809352936)最终两平台Test失败，原因与后续54e02063局部修复见上；不能记全仓success。

2026-11-16 模型 OAuth 候选 `505ac8e4`：先于源码推送 A 级 ADR0001/131 Helper 快照/CAS（cceecf9）、ADR28/48 当前订阅目录与类型校正（2ce89a3）、刷新前加密意图与 unknown 保全（9df3605）。现有 ChatGPT/Google 账号在实际模型请求前读取真实 Vault token、核对配置/凭据代，先 CAS 加密刷新意图再发 HTTP；成功仅提交自己的意图代。取消、超时、崩溃或未知效果保留意图，后续不重放旧 refresh；新登录/退出使迟到回调失效。Helper v1 可选 feature 协商，旧 Helper 对新鲜 token 仍可读取，但过期刷新在远端效果前拒绝。原有权限与 Evidence 边界不动。

本地完整 scoped：291 Rust（79 native Episode）、157 隔离根 / 908 实际 TS 往返、9 PTY；6 组真实 TS refresh 表单、5 组订阅请求、77 组类型化窗口选择，以及真实 TS client→加密 Rust Vault 条件协议通过。Desktop 80 聚焦、TS Helper 11、IPC 411/445/359、fmt/clippy/release/boundary/architecture/UI 通过。完整 scoped 后仅追加 release Helper 构建/探针与格式整理，并重跑聚焦检查；featureless CLI 不含测试 OAuth 端点，debug/release Helper 均声明 CAS，探针不读秘密或改数据根。详见[模型 OAuth 回执](native-cli/evidence/p4-native-model-oauth-20261116.json)。新候选已推送，[独立 CI43806200856](https://github.com/ly-ccx/Peer-Agent/actions/runs/43806200856)的Linux已成功，macOS最后smoke被后续源码推送取消，不记全仓success。

本卡仍未通过 P4 总闸：旧 TS 预读 token 的自动刷新尚未迁移同一前置意图事务，仅有 get 保护不能防重复远端刷新；必须继续补齐同域升级/drain 兼容。原生浏览器登录、完整配置写入与元数据恢复、其余 P4 能力，以及 P5–P7 都未完成。未请求真实 IdP/付费模型，注入 KeyStore 不替代 OS Vault；没有安装、迁移个人数据、重启实例或发布。

2026-11-16 OpenCode Go候选 `c34f161f`：复核ADR37、`48-provider-model-options.md`、129、131，沿既有Channel/Wire与数据契约做B级迁移，不增加执行、授权或存储事实。原生Adapter接通按模型选Chat/Responses/Anthropic、显式wireOverride、旧双渠道别名与Go根地址归一；21个静态模型推理profile及各wire默认值从实际TS resolver生成并冻结，已同步reasoningEffortValues优先，旧支持标记/样式/五档映射不能覆盖Go模型声明。Go会话头和Anthropic身份头走同一受限headers seam；无显式会话标识时由NativeModel owner创建临时UUID，同一执行的count/send/工具续接不变，后续执行新建且不回写配置。自定义session头仍按现有条目覆盖规则执行，显式session长度与CRLF受限。

实际差分还复现了原native live Chat漏发mapped-off、空映射补回通用强度的缺口；按当前Desktop encoder与ADR37的声明映射语义修复，保留已有Runtime的DeepSeek历史准入，纯共享wire fixtures不改。live dialect集中在wire/runtime.rs，追加runtime字段后再核对2MiB上限；精确边界测试证明不能由一个合法共享请求扩成超限发送。

完整原生scoped通过：272 Rust（68 native Episode测试）、294组实际TS配置/请求及真实HTTP count/send，其中123组Go；28组公开CLI配置/wire组合（含旧别名）通过真实模型流→工具→grant/ToolResult/Evidence。133隔离根782项实际TS往返、9PTY、fmt/workspace clippy/release/boundary/architecture/UI均通过。独立公开CLI验证未知Go模型使用服务端默认、同一执行头稳定及后续任务新身份；配置原字节不变。保留原mapped-off差分失败、旧临时Go拒绝断言与中间Rust可见性编译失败；更新为Go已支持/非法wire仍拒绝的真实合同，不删除工具/Evidence覆盖。见[Go回执](native-cli/evidence/p4-native-opencode-go-20261116.json)。基线35e213d1的CI43794213954 Linux133059215802 / macOS133059216064两平台全仓（含Test和Electron smoke）success；merge0556763c的tree与候选f7c8db52相同，[CI43797484064](https://github.com/ly-ccx/Peer-Agent/actions/runs/43797484064)已核实Linux133069491919 / macOS133069492282全仓success；merge ba9e8d49的tree e4ba2f48与候选相同。

本卡未通过P4总闸：订阅OAuth/自动刷新、Qoder私有wire/选项、代理/证书、完整Context发现与压缩策略、剩余工具、Skill/Plugin/Hook、ACP/headless/命令仍待完成；P5完整Bot与Ratatui交互未开始。真实Go服务、真实模型/IdP/OS Vault、多平台安装、完整体验与长时内存未验收。没有发布、安装、迁移个人数据或重启实例；原生执行链不含Bun/Node引擎sidecar。

2026-11-16 模型渠道配置候选 `35e213d1`：先核实基线 `4cf7a4c8` 的 CI43787766212 Linux133039151481 / macOS133039151743 全仓 success，再按 ADR37、`48-provider-model-options.md`、129、131 做 B级补齐，原能力链、权限、Evidence、System Context与持久化边界不动。原生 loader 不再 blanket 拒绝推理、输出上限、缓存和自定义头：Cargo直接嵌入从现有 TS ChannelDescriptor生成的注册表，17个普通API-key渠道 / 19种wire组合经四个原生encoder执行；Responses live seam对齐实际Desktop的声明映射（含mapped-off）与fastMode=priority。模型覆盖渠道的既有优先级、null缓存元数据回退、未知私有选项不注入均经真实TS差分。受保护鉴权/协议头、传输控制头、CRLF及超限请求头明确拒绝；自定义头视为敏感值，case-sensitive object merge后按HTTP语义归一，count/send共用且不重复版本头。Grok仅有订阅auth，不再误当API-key渠道；未知渠道不静默兼容。

完整原生 scoped通过：269 Rust（67公开CLI）、123隔离根731项实际TS往返、171组渠道/请求差分及实际HTTP count/send、9PTY，fmt/workspace clippy/release/boundary/architecture/UI通过。公开CLI覆盖19种组合的模型→read_file→真实grant/ToolResult/Evidence，以及非法头保全原配置→修正后同一任务重试。首次断言误把canonical工具结果当role=tool、误把Gemini模型名当body字段，两次失败夹具保留；按实际segments和URL契约修正，未删除真实工具/Evidence断言。最后仅新增“同名请求头恰好一次”的测试断言，聚焦171组HTTP重跑和clippy通过，生产源码与完整scoped一致。见[模型渠道配置回执](native-cli/evidence/p4-native-model-channel-options-20261116.json)。[CI43794213954](https://github.com/ly-ccx/Peer-Agent/actions/runs/43794213954)已核实Linux133059215802 / macOS133059216064全仓success，merge0556763c的tree与35e213d1相同。

本卡仍不是P4总闸：OpenCode Go模型路由与声明、订阅OAuth/自动刷新、Qoder私有wire/选项、代理/证书、完整Context发现与压缩策略、剩余工具、Skill/Plugin/Hook、ACP/headless/其余命令均待补齐；P5完整Bot和Ratatui交互尚未开始。真实模型/IdP/OS Vault、多平台安装、完整体验和长时内存未验收。未发布、安装、迁移个人数据或重启实例，无Bun/Node引擎sidecar。

2026-11-16 本地打包候选 `4cf7a4c8`：按用户请求，仅对当前 macOS arm64 生成原生测试归档，使用 Cargo featureless release 的 `peer` + `peer-credential-helper`，显式覆盖旧归档脚本的默认 Bun 产物目录。解包字节、执行位、ARM64/system dylib、签名完整性、隔离启动和 Helper ping 均验证；无安装、默认入口替换、用户数据或运行实例变更。归档 6,088,242 字节，SHA256 `6b71189240cad2a2bad6e77aebc1c41cace44900e3bff7d43654aad6a732f0b4`，本地产物位于代码仓 gitignored `target/native-package/tty-hangup-fixed-darwin-arm64/`。

解包测试真实暴露 active input poll 在 PTY master 关闭后忙等、不能返回取消标记的缺陷。旧 featureless 二进制先渲染并等待 input 初始化，再断开终端，2秒未停稳、需测试 owner 强制回收；过早关闭只验证初始化失败，未混作重现。沿 ADR48/129/130/131 的既有终端生命周期，B级选择锁定 Crossterm 的有界 tty poll source（`use-dev-tty`），仍是唯一 poll/read 输入所有者；新包正常退出并额外重复5次。测试驱动同时修复相对输出目录与 guardian 失败后的 child 回收；临时残留的纯草稿进程已按实际可执行文件/cwd/start 身份清理，无任务或工具效果。

最终包 scoped：10启动/退出/结构检查、33解包真实 Runtime 场景（含26 MCP与外部杀进程恢复）、9PTY；源码264 Rust、workspace clippy/fmt、15归档脚本测试及boundary/architecture通过。实际 packaged binary 无故障注入代码，旧 exit77 夹具的失败保留且不弱化断言；它在独立源码全套以测试feature通过，未冒充产物 crash-after-file 覆盖。详见 [本地打包回执](native-cli/evidence/local-native-package-20261116.json)。基线 `c8479317` 的 CI43779685385 两平台全仓 success，merge `f791fe45` tree相同；新源码 CI 单独核对。当前交互 Ratatui 仍是草稿骨架，完整会话/TUI和P4/P5未完成；本卡不等于正式签名/公证、真实模型/IdP/Keychain或多平台安装验收。

2026-11-16 MCP Vault / OAuth 候选 `c8479317`（tree `d028b18c`）：已先核实 `9e634d7b` 的 CI `43758620404` Linux / macOS 全仓 success，merge `00c3c750` 与源 tree 相同，再实施。ADR pass 包括 0001、31、32、36、45、129–131；新增 A级 [ADR132](../knowledge/decisions/132-mcp-vault-and-native-oauth.md) / map 及 superseded 交叉引用先于源码登记（知识提交 `2f4b1f2`）。它扩展 Helper MCP 命名空间和 v2 元数据提交，取代新写入的明文 fallback，保留原授权 / Evidence / unknown 政策。

Desktop-only 迁移严格读取原 v1，每条先通过 Helper 写入并常量时间回读验证，全部成功后才原子发布 v2；失败保留原文件字节、身份、未知字段和旧密文。OAuth clientSecret、tokens、clientInformation、PKCE / discovery 都进入不可变 Vault slot；原生端只消费 v2 / Helper，不解密 Electron。容量写入在既有 16 MiB reader 上限前拒绝，旧 Vault 继续可读；退役 / 孤立加密 slot 暂不自动删除。晚到 Desktop OAuth 回调须 CAS 原代，不能污染轮换后的凭据。

原生 MCP 支持 bearer / header / stdio_env 与有效 OAuth token，真实 grant 后才读取 Helper，连接启动 / 初始化后 / 下一模型请求前复核身份；Helper 取消证明 kill+reap，拒绝不读密钥也不启动 MCP。原生 `mcp auth` / `mcp refresh` 使用锁定官方 SDK，401 metadata pointer → issuer discovery → PKCE/state/resource → 预注册 / DCR → loopback callback → 原子 Vault 新代；不自动开浏览器或重放工具。错误 state 后仍可接收合法 callback，错误 issuer 不交换 token，取消关闭 listener。刷新失败 / token redirect / 超限响应保留原元数据；远端可能已轮换的 token 不承诺仍有效，沿显式重新授权恢复。

最终完整 scoped：264 Rust / 65公开CLI（26 MCP）/ 103根631项实际 TS 读写及 Rust 重读 / 7生产 TS MCP 向量与实际 SDK握手 / 8PTY，另有15项 Desktop凭据、11项 TS Helper、Protocol build/type/336测试、Helper typecheck、全 workspace clippy、release、boundary、architecture/UI与IPC检查通过。实际生产 Desktop reader 核对原生写入的 access/refresh/expiry/client payload；native 登录后再运行真实授权 MCP / Evidence。保留 fixture 路径/包解析、绑定字段、空 redirect、stdout owner、DCR缺字段、脱敏夹具和clippy失败；初始化期间轮换后仍继续认知的真实缺口已修复并保留原断言。最终源码冻结后独立重跑，见 [Vault/OAuth回执](native-cli/evidence/p4-mcp-vault-oauth-20261116.json)。新 [CI43779685385](https://github.com/ly-ccx/Peer-Agent/actions/runs/43779685385) 单独核对，不继承基线绿灯。

本卡不是 P4 总闸：运行时过期或缺失绝对时间的旧 token 要求显式 refresh/auth；原 grant 下的自动刷新 continuation、代理/证书和协议恢复平价仍缺。完整 model auth/private wire/settings、Source catalog/Host discovery、其余 Runtime 工具、Skill/Plugin/Hook、headless/ACP/命令仍待迁移，P5 尚未开始。没有安装、默认切换、个人数据迁移或重启；真实 IdP/模型、系统 Keychain 与多平台安装、完整体验和长时内存仍未验收。原生候选不启动 Bun/Node 引擎 sidecar。

2026-11-16 MCP协议补齐候选 `9e634d7b`：修复Streamable HTTP等待工具结果时不能及时回复服务器ping的实际死等、双向相同请求id被误当终态，以及Tool Result同名字段覆盖协商版本的问题；协议控制流仍受原owner管理，禁止重定向和底层协议NACK自动重试。初始化期间取消记录为cancelled + not_dispatched，已发出的取消仍保留unknown。协议控制请求不产生工具、许可、Evidence或模型用量。ADR131的B级澄清先记录于知识提交 `a49c79e`，既有能力、许可、存储与System Context边界未移动。

保留了真实失败轨迹：ping_queued→server_wait_expired→pong_received、下一次HTTP请求带入工具结果中的伪协议版本、初始化取消误记failed。广门禁的六项失败也保留并调查；模型fixture在创建15秒后退出的边界由16秒真实PTY审批等待独立复现。现改为显式owner控制监听器生命周期，socket读写仍3秒、受控stall仍15秒；审批决定须5秒内成为持久事实，后续完整模型/工具/停稳/记账工作流另有15秒界限，失败时OwnedChild保证清理。原退出码、效果、授权和unknown断言保留。

最终完整scoped为250 Rust / 54公开CLI（15 MCP场景）/ 82原生根493实际TS读写及Rust重读 / 7真实TS MCP归一化向量与SDK调用 / 8PTY；fmt/clippy/release/boundary/architecture通过。含同id/异id服务器ping的两次真实工具调用、控制POST拒绝与取消/关闭socket、伪版本字段仍按原始数据持久化、16秒等待期间续约及允许后正常收尾。详见[MCP双向协议与恢复回执](native-cli/evidence/p4-mcp-duplex-and-recovery-20261116.json)。`b9623558` 的CI `43730831267` 已核实两平台全仓（含Test与Electron smoke）success，merge `182f0806` 的tree与候选一致；该绿灯不覆盖随后复现的新场景。`9e634d7b` 的CI `43758620404` 独立核对，P4总闸仍未通过，P5未启动。

2026-11-15 原生 MCP 执行卡：源码 `613b2cc8` 接通 stdio、Streamable HTTP JSON/SSE 与独立 legacy SSE；后续 `b9623558` 仅补共享 Protocol 类型声明，Rust、lockfile、合同资源及验证脚本完全相同。Provider 仍沿 Manifest→Projection→当前 Host grant→真实 transport→Tool Result/Evidence 执行；初始化后再核对原 grant、registry revision、policy、Goal/binding 和 lease。连接复用并登记真实完成所有者，停止必须 drain；硬退出按完整原 recorder/进程组观测恢复本地句柄，远端效果仍为 `unfenced_external`，不会重放或凭 Git clean 自动收口。未知版本句柄原样保留并阻断恢复；独立范围的后续 worktree 任务可准入，旧 unknown 保留。

最终原生 scoped 门禁为246 Rust（50个公开CLI场景，其中12个新增MCP场景）、76个实际原生根/448项TS读写及Rust重读、7组实际TS结果归一化向量和真实TS SDK握手/调用、8项PTY；fmt/clippy/release/boundary/architecture通过。Protocol补充类型的build/type及336测试通过；原生门禁绑定 `613b2cc8` 的树，类型补充候选的远端CI独立核对。覆盖真实PTY的一次批准/第二次拒绝、非TTY拒绝、初始化期间降权/配置变化、响应业务错误/RPC错误、断连/帧与结果超限、30秒真实超时、SIGTERM、硬退出/未知版本恢复、已知用量不重复及后续任务。脱敏不递归重写替代串，也不能将协议失败改为成功。见[原生MCP执行证据](native-cli/evidence/p4-native-mcp-runtime-20261115.json)。ADR131的句柄/Evidence观测合同见知识提交 `b60d71a`；既有许可、占用与unknown人工收口政策未改变。

此卡只放开未绑定 credentialRef 的既有配置；非 none 的auth仍在模型调用前明确阻断，不降级为无认证。MCP Vault/旧凭据安全迁移、OAuth、代理/证书及协议恢复平价、其余模型auth/private wire、完整Context/压缩策略、剩余能力、Skill/Plugin/Hook、headless/ACP/其余命令与真实模型/平台验收仍缺。P4总闸未通过，因此P5尚未启动；不以MCP scoped通过代替完整Runtime。默认peer、个人数据、运行实例与安装均未改变，无Bun/Node引擎sidecar。

2026-11-15 NR-04 压缩持久化候选：`6afb5882` 已完成追加式 historySelection、TS/Rust v3 projector、原生 summary cognition、落盘后重建重计数、容量 sidecar/index mirror、冷恢复和单次 overflow 恢复；后续 `c69bec11` 仅移除文件尾空行。源码 scoped 为 226 Rust（36 个公开 CLI 场景）、56 根 302 项真实 TS/Rust 往返、Node/Bun 各 11 项容量存储互读，以及 8 项 PTY；完整原生 scoped 门禁通过。daa4c478 的全仓 Linux/macOS CI 已核实成功；新候选全仓 CI 单独核对。该卡不代表 P4 总闸：完整 Source/compaction 策略、OAuth/Qoder/代理证书、MCP/Skill/Plugin/Hook、headless/ACP/其余命令与真实模型/平台验收仍须逐项完成。默认 `peer` 未切换、P5 尚未开始，未安装或迁移个人数据。

下一张 NR-04 MCP 入口卡按 B 级实施：复核 `31-mcp-connection-management.md`、`32-mcp-authentication.md`、`36-mcp-tool-card-title-passthrough.md` 和 ADR131。先迁移既有 registry→Manifest 的有界只读 Adapter，冻结真实 TS 差分；未知版本/损坏源保留并拒绝，不把空 registry 误认为已有外部能力。Manifest 的可见性、来源和 auth metadata 不授予执行权限。空 registry 的真实 Host 准入可接通；非空 inventory 在 transport/credential/PermissionGrant/Evidence 全链未完成前继续明确阻断。stdio、Streamable HTTP 和 legacy SSE 必须分别验证，不能改写 `sse` 的含义；SDK 调研或纯 projector 测试不算外部工具已接通。现有权限、Evidence、System Context 与存储事实边界不移动。

该入口卡源码 `c835a459`：19 组真实 TS Manifest 差分、5 个明确拒绝合同、只读 Store 及两个公开 CLI 场景通过；空 inventory 放开，非空仍阻断，运行中 source identity 变化在下次认知前停稳并保留真实写入及费用。最终冻结 scoped 为 231 Rust / 38 公开 CLI / 58 根 314 TS/Rust 往返 / 8 PTY，完整原生 scoped 门禁、release、fmt/clippy、boundary 和 architecture 通过。详见 [压缩与容量恢复证据](native-cli/evidence/p4-compaction-capacity-recovery-20261115.json)、[MCP 入口证据](native-cli/evidence/p4-mcp-inventory-20261115.json)。c69bec11 的 Linux 全仓通过、macOS Test 15 分钟超时；同版本 Bun1.2.17 本机完整 TUI 为876通过/1跳过/0失败，未复现远端挂起，原因仍未知。原 macOS job 重跑在新候选推送后取消，不记 success；最终候选 CI 独立核对。P4 总闸未通过，P5 未开始。

最终候选全仓回执：`c835a4597864c26ae8d00d3dbd1e24642d3e7f63` 的 CI `43722096748`，Linux job `132836192244` 与 macOS job `132836191923` 均 success（含完整 build、native scoped、type、architecture、全仓 Test 和 Electron smoke）。CI merge `468e23e750b24a01d112c7c4ef9778dd028a5010` 的 tree `4695f7db37a3847cc7cd662e943b8d9c2b001633` 与候选完全一致。该结果验证当前组合源，不倒推 c69bec11 超时原因已修复，也不替代 P4 功能总闸或发布验收。

用户已接受评审稿 116–118；正式 ADR 为 129–131（避免与主线既有编号冲突）。用户要求 P0/P1 自测通过后持续推进至完整原生 CLI，无 Bun/Node sidecar。本账本记录候选与实际结果，不替代 ADR 或 Evidence。

## NR-00 / P0

允许：`scripts/native-cli/` 的隔离审计 / 测量工具、可分享合成 fixtures、知识库实施回执。真实入口为旧版 release CLI 的 classic 与 Bot 两条路径，使用临时数据根与受控 PTY。严禁个人数据 / 凭据 / 运行中实例；现有 8.27 GB 截图未精确复现，长历史渲染与流式链路须分别记录替代范围。

退出：模块可达 / 持久化 / 功能清单；source / binary / fixture 身份；五次短基线曲线与失败；明确待覆盖项。资源目标按 ADR 130 保持。

## NR-01 / P1

允许：Cargo workspace / lockfile、`crates/peer-{cli,protocol,tui}`、`packages/protocol/contracts/native-cli/`、对应 scoped 测试与构建 / 观测脚本。准许所需 Rust 依赖，版本须锁定。终端仅候选 / 草稿，不接管任务、不签发授权、不把用户文本发送给模型。

退出：独立原生二进制；轻量 help/version/doctor 路径；真实 TS/Rust 契约对照；Ratatui 渲染与输入 reducer；真实 PTY 的粘贴、Unicode、resize、Ctrl-C、EOF、panic 恢复与无 Node/Bun 路径；静态依赖规则、fmt/clippy/test/build。缺少真实 IME / 其他平台明确未覆盖，不冒充全产品验收。

## 后续

P1 通过后按方案进入 P2 数据、权限、锁与旧状态恢复；再推进原生工具闭环、Provider、项目代理、空间验收和发布切换。首轮不因骨架通过就将默认 peer 替换为功能不完整候选。

## P0 / P1 回执（2026-11-14）

源码候选 `c24dc465efb8dbce0d00ad3423384978178c5118`，已推送 [Peer-Agent PR 327](https://github.com/ly-ccx/Peer-Agent/pull/327)（draft）。实现基线取开发线 `8b0c9717`，未把此前 `f00c9553` 的独立 Bot 文案提交带入本 PR；旧版基线二进制仍绑定实际编译的 `f00c9553` 与已记录 workspace dist hash。

真实结果见 [结构化回执](native-cli/evidence/p0-p1-20261114.json)。P0 盘点静态包依赖闭包 9 个包、668 源文件（包含可选 / re-export，不冒充运行时动态可达图）。50 轮 / 6.86 MB 正文，classic 与 Bot 各五次有效渲染 / 正常退出；补采 RSS 与 macOS physical footprint。1,000 轮 / 137.21 MB，classic 五次约 1.8 GiB RSS；Bot 五次超过 2 GiB 测量保护上限，保留失败与四次未到正文首帧的事实，不算性能通过。不是用户 8.27 GB 的精确复现。

P1 `node scripts/native-cli/verify.mjs <temporary-output>`：25 项 Rust workspace 测试通过（13 新增原生 + 12 既有 Helper）；fmt / clippy、TS/Rust exit code / 数据根 / approval digest、Module 依赖与 sidecar 静态检查、8 项真实 PTY 通过。新 CLI binary 的 help/version/doctor 在 PATH 无 Node/Bun、无 HOME 配置下通过；Mach-O arm64 仅依赖 libSystem / libiconv。当前仅是不可发送 / 不执行的临时草稿候选，未替换默认 peer。

保留首次 clippy warning、fixture workspace 身份不一致、PTY 观察器和宽字符匹配失败的原因与修正，不称 flake。macOS raw/restore 的 PENDIN 已用 Python 单独重现为内核瞬态标志；termios 其余字段、控制字符、速度均严格比较。真实 IME、Linux/Windows、读屏、真实模型、安装升级、四小时 soak 与完整 Runtime 均未验收。Rust 1.88 为依赖声明下界，实际编译 1.98.1，不声称 MSRV 已测。

## NR-02 / P2（已开始，未验收）

允许：`crates/peer-store`、`crates/peer-protocol` 的 Store 数据对象、Cargo workspace / lock、`scripts/native-cli` 的 TS/Rust 交叉进程夹具与 scoped 检查。依 ADR 129–131 以及既有 ADR 101 / 116 / 120 / 127，实现共享存储与权限地基，不改权限或停止 / unknown 政策。

先做 NR-02a：真实 JSONL / sidecar / revision 的严格有界读取、同名目录锁、现有 Bot policy SQLite / CAS。跨语言真实 Store 对照，覆盖未知 schema、损坏、陈旧 revision、锁争用、取消 / 晚到结果所需身份，不因读取重建个人数据。随后 NR-02b：租约、执行 / grant / Evidence 身份、旧状态恢复与后续准入。未经全部 P2 门禁不开放生产写入或工具执行。

NR-02a 验证补充：允许在现有 macOS/Linux CI job 中追加原生 scoped 验证和工件保全（不改变 required-check ID，不发布、不改版本）；使 Cargo / 跨语言 Store / PTY 检查在同一候选上执行，而非只依赖旧 JS 测试。

## NR-02a 回执（2026-11-14）

源码候选 `e4c5354410c34c039b51da10a6d043d5be64dbe5`；原生 Store 独立 crate，无 CLI 生产写入 / 工具入口。现有 JSONL / streaming sidecar 的严格读取共享 8 MiB 原始预算、65,536 JSON 节点、64 层深度与字符串预算，未知消息字段保留；此接口仅供有界活动历史，不冒充大历史 viewport 已完成。目录锁与既有 `${file}.lock` 互斥，不 TTL 回收。既有 Bot policy SQLite 只读 / CAS，未知 schema、损坏、主体更换拒绝，不创建或自动迁 Full。

`node scripts/native-cli/verify.mjs /tmp/peer-native-p2a-check` 本地 macOS arm64 通过：35 项 Rust workspace 测试（23 原生 + 12 既有 Helper），fmt / clippy / 依赖与 sidecar 边界、14 项真实 TS/Bun/Rust Store 对照与双进程 CAS / 目录锁、8 项真实 PTY。夹具 `peer-native-store-conformance-NvqMxe` 位于系统临时目录，全部合成，无个人数据。PTY 候选 `peer-native` SHA-256 `b00d42e34bce808e3b10435b9e5e5910b7025908daa7a1846f60d37c06a8a9e0`。

失败与修正：SQLite NOFOLLOW 原先拒绝 macOS `/var` 父目录别名，改为规范化父目录并继续拒绝最终文件 symlink；锁 fixture 的双行阶段输出原先被测试驱动当单 JSON 解析，现逐项检查唯一 locked 阶段并解析终行；JSON 节点测试原先误把 8 个值节点计为 9，修正算术并保留重复 key 两次计费断言。没有削弱资源 / 权限断言。

P0/P1 提交 `c24dc465` 的 GitHub Actions run `43553408734`：macOS `ci-macos-14` 与 Linux `ci-ubuntu-latest` 均 success；该 CI 尚未包含新增的 native scoped step。P2a 新提交的远端结果另行记录，不以旧 CI 证明。P2b 租约、执行 / grant / Evidence 身份、凭证 Helper client、旧状态恢复尚未完成；P2 总门禁和完整原生 CLI 未验收。

### NR-02b 首个切片：原生凭证端口

按 ADR 0001 / 129 / 131 保留 Helper v1 和同一签名 / OS Vault 身份。允许新增 `crates/peer-runtime` 的受控 Helper client、Cargo 依赖与协议 fixture；不直接链接 Vault、不替换 Helper、不访问个人凭据。调用路径为 Runtime port → 指定原生 Helper → v1 响应；固定并发 / 请求 / 响应 / 解码 / deadline，取消与失败须 kill + reap，无 stderr / secret 泄露到错误。真实 Helper 只跑隔离根 ping 和无效请求（不触及钥匙串）；可控原生 fixture 验证 get/set/delete、超时、取消、洪泛、坏版本、错误状态和后续调用恢复。之后继续租约 / 执行身份与旧状态恢复，单切片通过不等于 P2 完成。

原生凭证端口回执：源码 `66aa7e2c`，本地 scoped 验证 41 项 Rust 测试（29 原生 + 12 Helper）、14 Store conformance、8 PTY、真实 Helper v1 ping（PATH 无 Node/Bun、隔离根零写入）通过。6 项新增端口测试覆盖合成 get/set/delete、缺失密钥、输入预算、洪泛、坏版本 / 响应 / 状态、受控 Vault 错误、deadline / cancel / caller abort 的 kill + reap、四并发门及后续请求。没有真实 OS Vault 读写或生产 credential 配置验证。进程数据与 Secret 使用零化容器，未承诺第三方 JSON parser / OS / allocator 的所有瞬时副本均可消除。凭证 port 尚未由 CLI 配置入口装配。

### NR-02b 下个切片：Host Lease

按 ADR 85 / 116 / 131 复用 `host.lease` 与 `host.yield` 的原格式、5 秒心跳 / 20 秒 stale、surface=tui；不把租约过期当停稳或工具权限。允许 peer-store 的 lease port / protocol 对象与真实 TS↔Rust 子进程夹具；先验证持有者、续约、过期接手、丢失所有权和坏记录保全，之后由 Runtime / Session Control 装配 drain / writer fence。既有 TS lease 的 read-check-rename 窗口不提供强 CAS，不宣称此切片消灭旧版并发竞态；未经执行 / 资源 ledger fence 和恢复门禁不开放生产执行。

租约存储切片回执：源码 `399ed176`，本地 scoped 检查 46 Rust 测试（34 原生 + 12 Helper）、14 Store + 13 Lease 真实跨进程对照、8 PTY、真实 Helper ping 通过；日志在临时 `peer-native-lease-check.log`。新增 5 Rust 用例覆盖同时抢占、续约、陈旧 handle 不能续约 / 释放新所有者、未知字段、yield 不自动放权、drop 不释放、损坏 / 未知 surface 保全、symlink 拒绝。兼容对照覆盖 TS→Rust→TS lease / yield、真实双进程空闲租约竞争、宿主退出后持有记录与过期接手；不把宿主退出或过期称执行已停稳。首次 `time` deprecated warning 改用明确版本的 `parse_borrowed::<2>`，clippy -D warnings 通过。记录损坏时原生失败关闭，不复制旧 TS 的 parse-error 回收。低层 heartbeat 仍沿既有 read-check-rename，执行 / resource fencing 与 Session Control drain 装配尚未完成，不开放生产写入或执行。

### NR-02b 下个切片：执行身份 / 批准 / Evidence

按 ADR 92 / 101 / 116 / 127 / 131 的现有契约，允许原生 protocol 的 execution identity / resource scope、grant / Evidence 数据结构与同一 TS normalizer / collector / operation-key 的对照；允许 peer-runtime 的 host principal resolver。只搬迁 shape / 身份 / 确定性规则，不让解析成功等于批准，不引入另一个任务或授权系统。恢复与实际工具入口继续等待 canonical Store、Session Control、policy revision 和 execution fence 的真实装配。

身份 / 批准因子 / Evidence 引用切片回执：源码 `9f33d9a25a6e600bf4dc0b3201db448df366cf0c`，54 Rust 测试（42 原生 + 12 Helper）、51 个真实 TS 派生 golden case、14 Store + 13 Lease 双进程、8 PTY、真实 Helper ping、fmt / clippy / 静态依赖 / release build 通过。执行 identity 与 resource scope 严格校验未知字段、安全整数及 UTF-16 长度；principal resolver 只消费 Host 计划投影，未把 shape 当授权；一次性批准因子按完整 scope / policy revision、有界条目和字节、消耗 / 到期释放。Evidence 只收集既有结构字段，保插入顺序，不扫描助手文字或任意输出。完整操作 digest 直接借用 args，转义时逐段限额，不先复制整个参数对象。

新增真实入口用例复现候选无 HOME 时忽略显式 PEER_AGENT_HOME；保留失败日志后修正为先解析覆盖值，并补 PEER_USER_DATA_PATH、BOM / NEL 的 JS trim 对照及零写入断言。最初测试少覆盖此组合，不能用此前通过替代本次修复后的候选检查。另做合成分隔符碰撞探查，旧 TS 的 workspace guard 已拒绝该跨 workspace 输入，未把探查误报为旧版漏洞，也未改旧 TS 权限政策。详见 [P2 地基结构化回执](native-cli/evidence/p2-foundations-20261114.json)。P2 总闸、canonical Store / Session Control / writer fence、持久 grant / Evidence 事务、完整 Runtime 和无 sidecar 功能平价仍未完成。

### NR-02b 下个切片：Session Control 确定性 kernel

已复核 ADR 116 / 120 / 124 / 127 / 131，以及现有 `session-control-kernel.mjs`。允许 peer-runtime 的纯 control reducer、peer-protocol 对应 JSON 序列化 / identity 帮助、Cargo serde_json preserve_order feature 与 TS/Rust golden / 故障序列测试；保持原控制状态、CAS、supersede、cancel 优先、stop receipt 和 minimumExecutorVersion 7/9 规则，不产生真实停止证明。须区别 approval stable-key digest 与 control 的 JSON.stringify digest，保留原对象 key 次序及 JS number / integer-key 顺序；不得以同一个“canonical JSON”代替两种既有语义。持久写入、进程停止和工具准入仍须 canonical Store / Host 装配后另验，不因 reducer 通过就开放执行。

Session Control kernel 回执：源码 `2e48f45ae39eb84e85c166f285279a79a83b4e55`，57 Rust 测试（45 原生 + 12 Helper）、既有跨进程 / PTY / Helper 检查以及 29 组真实 TS 控制转换、7 个 JSON.stringify 摘要向量通过。serde_json 保留输入对象次序；批准摘要仍 UTF-16 stable-key 排序，控制摘要按 JS integer-key / 插入次序与 JS number 编码，未混用算法。覆盖 cancel 优先、supersede、stale revision / epoch、不可变 recorder、缺失 / 无效 stop receipt、原 unknown 保留、停止后 resume 的 shape 规则；不声称 reducer 产生真实停止证明。首次编译借用冲突修为借用原事实、验证后才复制候选；4 项 clippy collapsible-if 修正后 -D warnings 通过，未改断言。

### NR-02b 下个切片：Policy 初始化与旧状态迁移

已复核 ADR 101 / 131 与 `bot-access-policy.mjs` 的实际初始化入口。允许补 peer-store 原生初始化 / 仅首次 legacy 档位迁移 / 已初始化后新 Bot 默认 Ask 注册，及 TS↔Rust SQL fixture；沿同一 access_policy / access_meta、migrated 标记和 bot-access-imported.json 保护。原 read_existing 继续零隐式建库 / 迁移；未知 schema、损坏与主体更换仍拒绝，不能重建或回退 Full。验证新旧初始化互读、已有策略不重迁、导入标记、新 Bot、取消与坏库保全；仍不开放 CLI 生产权限管理入口。

Policy 初始化 / 存量迁移回执：源码 `c8d3a2ae`，64 Rust 测试（52 原生 + 12 Helper）、既有 51 runtime golden + 29 control transitions / 7 摘要、14 Store + 13 Lease + 9 Policy 初始化跨进程检查、8 PTY、真实 Helper ping、fmt / clippy / release build 通过。初始化复用 access_policy/access_meta 和一次性迁移标记；新 Bot 默认 Ask；现有策略不重迁；导入标记阻止继承另一设备 Full；损坏 / 未知 schema / 未知 marker / 错列定义不重建。取消前置检查无写入；并发注册仅一条 revision=1；SQL 单值 1 MiB、SQL 文本 16 KiB、列数 32 的连接限制先于查询，异常值拒绝。初始化枚举上限 4,096 项，超限回滚并报告 POLICY_RESOURCE_LIMIT，不截断为完成。SQL busy 仍 3 秒；同步 Store port 尚待 Host 阻塞任务池 / 取消装配。

保留交叉验证首次失败：旧 TS BotProfileStore 要求非空 displayName 与 avatar 对象，原生 profile reader 初稿漏校验、旧手写夹具也过窄。新增同一坏档案的 TS/Rust 实测后修正，测试正常档案补齐真实字段；不把改 fixture 当已验证旧边界。无生产入口曾调用这条候选权限路径，未读写个人策略；旧 Full / Evidence 未被擅自清理。日志保留于系统临时目录 `peer-native-policy-profile-failure.log` 和 `peer-native-policy-check.log`，最终交叉夹具 `peer-native-policy-init-q0mwKa`；首次 set_limit 的未处理 Result warning 改为错误传播，未忽略检查。

### NR-02b 下个切片：大文档只读字段投影

依 ADR 98 / 130 / 131，允许 peer-protocol 的流式 JSON 字段投影器、peer-store 的文件身份 / 只读 Goal 原文投影及隔离量测。目的：大 Goal 的轨迹 / checkpoint 正文不能为了查几个身份字段整篇进堆。输入用有界 BufReader，未选择字段跳过；Root key 解码、已选择载荷 / 节点 / 字符串、全源字节、嵌套深度与取消均在分配 / 读取中限制。已检查 serde_json 1.0.150 的 IgnoredAny：字符串可无拷贝跳过，但 ignore_value 的 scratch 随嵌套增长，必须由 Reader 深度守卫补上。输出明确为原始字段投影，携 source revision / requiresRuntimeCheck，不代替 normalizePlan、runner-progress 合并、Control / lease、live/unknown 或授权。不得重写源文件，不把新 Reader 误报成大历史视口已完成。

字段投影 / WAL 修复回执：源码 `caedca4364fe69d9f4d225509a672abe58eb81e7`；本地 scoped 验证 71 Rust 测试（59 原生 + 12 Helper）、51 runtime golden、29 control transitions / 7 摘要、14 Store + 13 Lease + 13 Policy 跨进程检查、8 PTY、真实 Helper 隔离 ping、fmt / clippy / release build 通过。128 MiB 合成 Goal 字段扫描五次，RSS 均 2,129,920 bytes，physical footprint 均 1,376,640 bytes，扫描 811–821 ms；二进制重建 hash 未变，与量测一致。源 SHA-256 与原文不变；这不是完整 CLI / viewport / 千轮 / 四小时性能验收。

远端上一候选 `c8d3a2ae` 的 macOS CI success，Linux CI 发现拒绝未知 schema 时的 WAL checkpoint 改写。用原生夹具模拟已提交但未 checkpoint 的 schema 2，macOS 也复现主文件改写，保留 `peer-native-wal-failure.log`。修复为只读事务检查 schema / marker；可写连接先禁用 close checkpoint，事务内再检查，只有成功的已准入事务恢复原 checkpoint 行为。新增 initialize / read / register / update 四条拒绝路径的主文件与 WAL 字节不变断言，全部通过。没有把失败归为 flake，也未削弱文件不变断言。新候选 CI [run 43565605621](https://github.com/ly-ccx/Peer-Agent/actions/runs/43565605621) 尚在运行，不能以旧候选结果代替。

### NR-02b 下个切片：展示历史有界分页

已复核 ADR 57 / 74 / 86 / 98 / 130 / 131 和实际 `jsonl-byte-window.mjs`、`history-source-reader.mjs`。允许 protocol 的原始展示页 / revision 绑定 cursor、peer-store 的逆向有界 JSONL 读取、共享 TS 对照 fixtures 和隔离资源量测。页同时限制记录数、扫描字节、单行 / AST 节点 / 字符串，取消在磁盘读取中生效；cursor 绑定文件身份，陈旧 cursor 明确失效。损坏行需显式诊断，不能悄悄当完整历史；未知字段保留。展示页不是 canonical 模型历史，不合并 streaming sidecar，不产生 grant / Evidence 或执行事实。超大单行先明确报告预算与原文范围，后续块级阅读另验；不把这一切片冒充完整虚拟 transcript 或所有大消息已可浏览。

展示分页回执：源码 `886cfe4372d0b595165a9ee980aedca2cdca0e6b`；77 Rust 测试（65 原生 + 12 Helper）、原有 51 runtime / 29 control / 7 digest、64 跨进程用例（Store 14、Policy 13、Lease 13、Transcript 24）、8 PTY、真实 Helper ping、fmt / clippy / release build 通过。新增 6 Rust 用例覆盖 Unicode 跨块、unknown 字段、坏行 / 非 UTF-8 明确范围、扫描 / 单行 / 解码预算、长前缀尾页成本、取消前置、陈旧 / 跨会话 / 行中 cursor、symlink 与源文件不变。取消检查每个 16 KiB 读块，未把前置取消测试说成真实运行时取消时延验收。

约 1 GiB（1,073,762,880 bytes）合成 JSONL 的尾部 80 行五次均只扫描 81,920 bytes，RSS 2,277,376 bytes、physical footprint 1,556,864 bytes；探针保持已解码页驻留 300 ms 供外部采样，PATH 无 Node/Bun、无 HOME、无子进程，原文 SHA-256 前后一致。内部计时为整毫秒分辨率，五次记录为 0 ms，表示小于该分辨率，不能称零耗时或完整 UI 延迟。大 Goal 同候选重新量测五次 RSS 2,113,536–2,129,920 bytes，812–830 ms。资源探针不是 Ratatui viewport / 模型历史 / 完整 CLI / 长期 soak 验收；超大单行目前明确拒绝，不声称已实现块级正文阅读。

首次对照发现领先空行的 cursor 语义差异：原生初稿在扫到文件头后直接返回 null，旧 TS 返回最老记录 offset，并可能有最后一页空白前缀。保留 fixture，原生恢复同一旧锚点语义，24 项真实对照通过；未改断言为放过差异。完整机器回执见 [P2 Control / Policy / Reader 回执](native-cli/evidence/p2-storage-control-20261114.json)。当前仍未接通 canonical GoalStore、协调 writer fence、持久执行 / grant / Evidence 与 unknown 对账，P2 总闸未通过；不开放共享任务写入、模型请求或工具执行，不切换默认 peer。

最新源码远端验证为 [run 43566467824](https://github.com/ly-ccx/Peer-Agent/actions/runs/43566467824)。后续实际 job step 查询确认 Linux [132361408957](https://github.com/ly-ccx/Peer-Agent/actions/runs/43566467824/job/132361408957) 与 macOS [132361408765](https://github.com/ly-ccx/Peer-Agent/actions/runs/43566467824/job/132361408765) 的 `Native CLI scoped validation` 均 success，原 Linux WAL 失败路径在新候选通过。两平台 Build / Typecheck / Architecture 也 success；全仓 job 仍 in_progress，不能把原生 step 通过说成整条 CI 完成。前一候选 `caedca43` 在本次推送前仍 in_progress，没有记录为通过。

### NR-02b 下个切片：协调日志旧 writer 屏障

依 ADR 104-progressive / 105 / 112 / 116 / 131 与现有 `coordination-writer-fence.mjs` / `coordination-legacy-integrity.mjs`，允许 peer-store 原生 lease 约束的健康 v2 writer promotion、既有 `coordination-fence.json` intent / `.coordination-fence` archive / frozen baseline / legacy seal 读写，以及合成 TS↔Rust 中断恢复夹具。不建立新的日志格式或执行记录。Interface 从 Host 持有的 LeaseToken 取得路径与归属，不接受模型 JSON 作为 owner。文件写入须 fsync + atomic publish，逐阶段重查租约与取消；保留旧 journal / head / manifest / seal，未知 schema、symlink、内容变化和第三方新 head 不得被覆盖。验证六个既有中断点的双向恢复、空项目、既有终态记录保全、旧 writer 实际被目录屏障拒绝及丢失所有权 / 取消 / 损坏拒绝。完成该存储切片仍不等于已有执行已停稳或 P2 执行准入通过。

writer 屏障回执：源码 `6a729852e4a8272005a31fcaff2ea5a4fe4e0a91`；本地完整 scoped 检查 85 Rust（73 原生 + 12 Helper）、78 真实跨进程（新增 14 Fence）、原有 87 golden / control / digest、8 PTY、真实 Helper 隔离 ping、fmt / clippy / release build / 边界检查通过。六个中断点分别覆盖 TS→Rust 和 Rust→TS，原生日志采用受控 `process::exit(77)` 跳过 Drop 模拟进程中断，不声称真实断电；真实 lease / epoch、stale takeover 与目录屏障参与对照。旧终态 work 保留，恢复后由真实 TS v2 Store 写入后续 work 成功；不是原生任务执行已验收。

新增 8 Rust 用例覆盖原文 / 归档 / unknown 元字段不变、旧 append 实际失败、六阶段续接、空基线、不存在 v2 不激活、前置与阶段取消、前置及 intent 后失去租约、损坏证明、symlink、未知 schema、baseline 改写、较新 head / reader-writer floor 保全。初稿的阶段校验遗漏已被新用例实际复现：HeadPublished 后注入 floor=12，错误返回 Promoted；修正为发布前校验允许前态及文件身份、阶段后重查合法前缀，拒绝且保留 floor=12 / 新 head / prepared intent。首次新建发布用 no-clobber；后续文件发布仍遵守既有 lease + read-check-rename 协作，不声称实现了新的跨 Runtime 强 CAS。

保留 fixture 首次误用不存在的 lease.epoch 方法、clippy 的 unused import / manual_contains 失败，修正为读取真实 diagnosticSnapshot 并沿 Host 的 hostId:acquiredAt epoch；未替换成总为 true 的租约。hash/copy 每 256 KiB 检查取消 / 所有权，源扫描上限 2 GiB，元数据有独立预算。Host 仍须串行 prepare、维持 heartbeat 并完成 canonical v2 reducer/head/hash chain 校验后才可调用此 promotion；当前尚无这条原生生产装配，AlreadyProtected 只描述物理屏障，不证明任务已恢复。详见 [结构化回执](native-cli/evidence/p2-writer-fence-20261114.json)。当前新候选 [CI 43568584797](https://github.com/ly-ccx/Peer-Agent/actions/runs/43568584797) 两平台仍 in_progress；不能沿用前一候选的原生 step success。

ADR pass 补充：131 §1 原先笼统写“ADR 104 未接受”，已按同号文件名澄清：未接受的是 bot-capability-visibility，已接受的 progressive storage / writer fence 继续保留；map 同步记录。仅消除歧义，既有边界未变更。此前 Reader 量测仍绑定其回执中的实际源码 / 二进制，不挪用为本次新 Store 二进制的量测。

后续实际查询确认：`6a729852` 的 Linux job [132367759976](https://github.com/ly-ccx/Peer-Agent/actions/runs/43568584797/job/132367759976) 与 macOS job [132367759772](https://github.com/ly-ccx/Peer-Agent/actions/runs/43568584797/job/132367759772) 的 `Native CLI scoped validation` 均 success，包含本次新增 writer fence / 85 Rust / 78 跨进程用例。全仓 CI job 仍 in_progress；未运行完整发布或安装版验收。

## NR-02 剩余实施（2026-11-14 用户再次要求继续至 P3）

按同一已接受方案串行推进：设备级 Resource Ledger / native scope derivation → canonical 当前事实与持久执行 / 授权 / Evidence 提交及恢复 → P2 真实故障与后续准入门禁 → P3 Context/history/Provider/Projection/PermissionGrant/file/Shell/Evidence/持久化真实闭环。不得将已有纯 kernel 或测试探针改称完整 CLI。P3 的确定性 wire 回放与真实模型验收分开记录；不以 TS sidecar 填充任何运行环节。

本卡先允许 peer-store 的 execution-resources.sqlite schema 3 Adapter、与 Policy 共享的有界 SQLite 文件打开防护、原生目录 / 文件 / Git common-dir scope、既有 claim / handle / settlement / closure / retained_unknown / reconciliation 格式及互读 fixture。复核 `116-session-control-and-resource-settlement.md`、`127-unknown-outcome-reconciliation-and-delegated-resolution.md`、`131-native-cli-contract-storage-and-recovery.md`，既有释放 / 授权 / unknown 不重放边界不变。正常与异常至少覆盖多连接 / 跨进程冲突、symlink 和父子目录别名、全资源集原子预留、同 receipt 幂等 / stale revision / late epoch、未结束 handle、unknown 保留 / 授权收口、缺失旧 ledger、未知 schema/WAL 保全、取消与恢复后新任务。源数据全部合成，生产入口在 P2 总门禁前继续关闭。

Resource claim / scope 是集合；跨语言对照在声明前按 resourceRef / claimId 比较集合，Rust 不引入一套 ICU 运行依赖来复制 JS 默认 locale 的显示排列。所有实际身份 / receipt digest 输入和 unknownCalls 的既有有序或 UTF-16 排序语义仍逐字节对照，不借集合比较放宽授权或幂等。原生数据接口不把集合第一项当主目录身份。

Resource Ledger 回执：源码 `c2f19ce5ddb681b9534d38e1a04f8922fa41a4dc`，完整 scoped 验证 93 Rust（81 原生 + 12 既有 Helper）、117 真实跨进程（本卡新增 39 Resource）、32 旧 Node resource 测试、原有 51 runtime golden / 29 control transitions / 7 digest、8 PTY、真实 Helper 隔离 ping、fmt / clippy / release build / 静态边界通过；另行 runtime-node build 与 architecture 检查通过。详见 [结构化回执](native-cli/evidence/p2-resources-20261114.json)。

共享 SQLite 打开器先只读准入再写，未知 schema 的主库 / WAL 保全，连接查询有字节 / 行 / 节点预算。资源集在同一事务预留，claim 与索引列双向核验，receipt exact digest / CAS / late epoch、活动 handle、unknown 保留 / 显式收口、reconciliation evidence 均沿原格式。Host closure 参数不是模型可反序列化的授权值。原生仍未装配生产 authorizer，不开放共享任务执行。

真实互操作发现旧 Node 的文件 claim 在 activate 时被错误当目录，复现 `execution_resource_scope_unknown` 后改为沿既有 claimScope/fileResource；32 项旧测试与 39 项互操作在修复后通过。初次 fixture 的 /var 与 /private/var 期望错误已按真实 TS canonical 输出修正，未放宽 scope 比较。失败日志保留，详见回执。当前候选两平台 CI 尚在运行，不能声称整仓通过。P2 总闸及 P3 实际闭环继续推进，以上不代替 canonical 当前事实、持久批准 / Evidence、停止与恢复装配。

### NR-02 剩余：持久批准与会话提交

依 ADR 57 / 65 / 74 / 85 / 92 / 101 / 116 / 127 / 131，允许补既有 approvals.jsonl 的有界读取 / 同身份状态追加及孤锁保全、ConversationStore 的同格式创建 / CAS 提交 / 幂等和中断恢复 fixture。执行批准仍须 Host 实时 scope / policy revision 检查；历史 approved 不自动成为许可。损坏 / 部分尾行、侧写草稿、未知效果不跳过为成功。持久化只能记录结构事实，不能让 assistant 文字变成 Evidence。既有边界不变，不新建私有执行日志。旧 checkpoint 无法安全解释时按 ADR 131 明确阻断并保留兼容恢复入口；完整 Bot runtime 在 P5 另验。

持久批准 / 会话提交回执：源码 `e1e7af77`，103 Rust、148 真实跨进程、32 旧 resource / 10 旧 approval 测试及原有 golden / control / digest / PTY / Helper / fmt / clippy / release / 静态边界通过；runtime-node build、architecture 通过。补读 ADR `121-desktop-session-windowing-contract.md`：物化 preview 仍是派生展示，Runtime 冷路径 snapshot 不冒充产品 SessionService 的窗口返回。结构化回执与后续 Evidence 卡合记于 [P2 durable facts](native-cli/evidence/p2-durable-facts-20261114.json)。

会话 CAS 同时绑定 contentRevision 与物理源版本；同消息身份 / 同正文返回已有回执，不重复追加。正文 durable 后索引失败返回 STORE_COMMIT_UNCERTAIN，受控 reconcile 只修派生索引，原未完成 tool segment 保留；原本已计数的消息丢失不能修成空会话成功。真实 process::exit(77) 跳过 Drop 的故障留下既有空目录锁；生产不自动清理，夹具确认子进程退出后只 rmdir 已知空锁，再恢复并接收后续消息。此处不是断电测试或原工具效果已结清。

Evidence 登记回执：源码 `7af3ab505cb6efbc7bf8ac2ede45d47da3c244a3`，107 Rust（95 原生 + 12 Helper）、155 真实跨进程（durable 卡 38）、128 旧侧聚焦测试、原有 golden / control / digest / 8 PTY / Helper、fmt / clippy / release / 静态边界、runtime-node build、architecture 均通过。复用 goal-plans/evidence-index.jsonl；校验 call / grant / result 配对，成功结果要求实际 granted=true，只消费既有结构字段；任意输出 / 助手文字不注册。收集器新增直接借用 result 的入口，避免复制整个输出。普通引用沿旧 merge 规则并保未知字段；复杂 Interactive Receipt 保护原记录并明确返回 unsupported，未假称其 Adapter 完成。

旧 TS 批准 writer 忽略目录锁的问题已由新用例复现，失败保留 `/tmp/peer-native-approval-lock-failure.log`。随后同一个 owner / ctime 检查的 Store 文件锁同时供批准与 Evidence writer 使用，与 Rust 空目录锁命名相同；没有 TTL / PID 回收。订阅回调在释放锁后运行，保留重入追加。此修正落实 ADR 131 的双端互斥条款，未改变授权或 Evidence 真值边界。候选 CLI hash 见回执；历史 Reader RSS 仍只绑定旧量测候选，不能移植为本卡验收。

已进一步确认 `c2f19ce5` 两平台 CI 全部步骤（含 Test、Bot shell smoke）均 success。最新 `7af3ab50` 尚待远端检查，不用旧结果替代。P2 总门禁仍未通过：canonical Goal / 协调 prepare、真实授权 / 停止与 unknown 对账装配未完成；P3 原生模型 / 工具闭环仍未开放。

### NR-02 剩余：canonical 协调存储

继续依 ADR 104-progressive / 105 / 112 / 116 / 127 / 131，在既有 coordination-v2 manifest / head / segments / payload_ref / baseline / seal 上实现原生可取消有界验证、reducer seam 与 durable 追加 / 中断恢复。事实源必须是 canonical hash chain，不能拿 derived SQLite 的 revision 自证或把物理屏障称 canonical prepare。未知语义或超预算明确阻断，不能跳过记录得出空状态；不引入第二套任务表 / 执行日志。先过跨语言实际 Store 互读 / 后续任务与 head / tail / lease 故障，再装配执行准入。

canonical 协调存储切片回执：源码 `82ce5819666698b530aa7e9fdd4476dbd004fb4a`，109 Rust（97 原生 + 12 Helper）、210 真实跨进程（本卡新增 55）、128 旧侧聚焦测试、51 runtime golden / 29 control / 7 digest / 新增 29 work-event-delivery 转换、8 PTY、真实 Helper ping、fmt / clippy -D warnings / release / 静态边界、architecture 均通过。完整日志 `/tmp/peer-native-canonical-final2.log`；[结构化回执](native-cli/evidence/p2-canonical-coordination-20261114.json) 记录源、二进制和覆盖限度。

Store 沿既有 manifest / head / segments / payload_ref / seal / frozen baseline 验证逐条 canonical hash chain，检查 head 是已验证前缀，允许完整 durable tail 的 head 暂落后，但在 head checkpoint 前拒绝新追加。snapshot 同时绑定 metadata / 文件身份 / blob 身份及 generation；复制 derived SQLite revision 不构成证明。只读 replay 每 16 KiB 检查取消 / 租约，全读含 blobs 64 MiB、4096 records、单 envelope 64 KiB、单 legacy record / blob 及 state 编码 1 MiB 为显式门限，超限拒绝且不截成完成。

原生可从空目录或可解释 v1 初始化同一 v2 格式，先 replay 后物理 promotion；原生追加后真实 TS backend 补其 derived SQL cache，并继续写入。head 前崩溃 / 完整 tail 未 checkpoint 时原记录保留，旧操作不重放，补 head 后后续 work 可写。语义 floor 先抬 durable head 再抬 manifest；中断时保留较高 floor 并沿现有物理证明续接。未知文件 / 孤儿片段不能初始化为空项目。真实进程 exit(77) 故障与 fixture stale lease takeover 只验证存储，不证明外部进程 / 工具停止。

Runtime 当前支持 work/event/delivery 与既有 Session Control kernel；coordination decision、intent、agent supervision、obligation、history repair 的未搬迁语义返回明确 unsupported，整个 read/append 阻断。实际 TS 创建的合法未支持记录不会被跳过为新空状态，兼容端再次读取后仍保留原事实。P2 总闸仍未过，canonical Goal、剩余 reducer、真实 Host 当前授权 / handle 停稳 / unknown 对账与准入装配继续待办，P3 模型与工具闭环尚未开放。未改变 ADR 104-progressive / 105 / 112 / 116 / 127 / 131 的授权、恢复或存储边界。

保留初次 fixture 构建漏启用 peer-store/test-fixtures、构建失败后误调用旧 probe，以及 70 KiB payload 超过 fixture 自身 64 KiB 请求限制的失败。均不计通过；后续改为 set -e、显式双方 fixture feature 和有界 1 MiB 请求，完整 scoped 流程重跑通过，未放宽生产预算。实现者完成内容 / diff 自审，未称独立评审。较早 `7af3ab50` Linux job 全步骤 success、macOS 原生/build/type/architecture/test/smoke 已 success，最后观察时 report/post 仍运行；最新源码 CI 另验，不挪用旧结果。

最新远端 scoped 结果补记：`82ce5819` 的 [CI 43578026254](https://github.com/ly-ccx/Peer-Agent/actions/runs/43578026254) Linux job 132396468162、macOS job 132396468104 的 Native CLI scoped validation 均 success，包含 109 Rust / 210 跨进程及本卡 55 canonical 用例。最后观察时全仓 job 仍运行、未见失败；不称整仓完成，也不称 P2 / P3 或发布验收通过。

## 2026-11-14 继续 NR-02 至 NR-03

用户再次明确：补齐 canonical Goal、剩余协调 reducer、Host 实时授权 / 停稳 / unknown 对账，P2 总闸通过后直接进入 P3，最终无 Bun / Node sidecar。当前源码 82ce5819、知识 263f170；无在制代码改动。本卡复核 ADR map、`116-session-control-and-resource-settlement.md`、`117-intent-driven-coordination-and-goal-closure.md`、`111-project-agent-duplex-supervision-and-continuity.md`、`127-unknown-outcome-reconciliation-and-delegated-resolution.md`（以页头 Accepted 为准）与 `131-native-cli-contract-storage-and-recovery.md`，本轮为既有契约下的 B 级搬迁，未移动边界。

先补齐 coordination decision / obligation / intent / agent supervision / history reducer 与对应只消费 Host 事实的 admission seam，再补 Goal 与 Host 装配。允许 native Runtime 的领域模块、共享 protocol conformance resources、真实 Store 往返和故障夹具。不把缓存、历史 approved、无进程内 token、时间或助手文本当成授权 / 停稳事实。新增语义均用实际 TS kernel 冻结正常和拒绝分支，并经 canonical journal 冷恢复验证；核验与后续新任务须跨真实 Store / Host seam。P2 未过前不开放生产模型 / 工具写入，不以另一套执行日志或 Node sidecar 填缺口。

### NR-02 canonical Goal / 完整 reducer / Host 停稳切片回执

源码 `0921d673`：补齐 decision / obligation / supervision / intent / history reducer，66 项真实 TS transition、35 项 canonical journal 往返通过。修复空 bucket / observations 的 SQL 读投影差异，并补 history 种入监督事实时最低 executor floor 的回归。Goal execution facts 通过 23 项真实 getPlan 投影、36 项 source / sidecar / active index / 大正文 / 拒绝测试；Goal 仍是执行事实读适配，不宣称完整 CRUD。

Host 新端口组合 canonical Goal / journal / 现有 schema-3 ledger：实时 ancestry / policy / execution / lease / resource 校验，活动批准对象与执行前复核；原生 recorder tuple 与 live token / handle 所有权；停止回执落 canonical journal，超时保留 owner、晚到真实结束可继续结清。11 项集成含真实原生子进程 kill + reap、失败句柄、重启 unknown、epoch 变化、批准时策略变更、Git 干净/脏树及禁止执行过滤器、file-only 策略收口、Shell 拒绝、unknown 保留与后续资源预留。

最终 scoped：129 Rust（含旧 Helper 12）、281 真实存储跨进程、128 旧 focused、8 PTY、Helper 无密钥 ping、fmt / clippy -D warnings / release / 静态边界与 architecture 均通过。详见 [结构化回执](native-cli/evidence/p2-goal-kernels-host-20261114.json)。`82ce5819` 两平台 CI 全部 job 已 success；新候选远端未验收。本次补读 ADR 101 的动态权限主体及 126 被 127 接受扩展的闭包条款，不更改权限或 Evidence 边界。

P2 总闸仍待共享 Goal 执行镜像写域/CAS、closure 镜像中断恢复、剩余 admission 与自动权限/角色语义、完整 Host 启动及已有状态恢复验收。P3 Context / wire / Projection / file / Shell 闭环未接；公开 CLI 仍为终端草稿 spike，不以新 Host 集成测试冒充产品完成。继续补齐上述总闸，再接执行；最终无 Bun/Node sidecar 的要求不变。

`0921d673` 新 CI 43584888148 的 Linux / macOS 均构建成功，但 scoped clippy 失败：CI Rust 1.100 已将 `AtomicUsize.fetch_update` 标为 deprecated，本机 Rust 1.98.1 尚无该告警。补丁 `05c6bc05` 改为兼容既有 MSRV 的 compare-exchange 循环，不放宽 warnings-as-errors；本地完整 scoped 再次通过（129 Rust / 281 跨进程 / 128 旧 focused / 8 PTY）。保留原失败与候选身份，新远端结果待查。

剩余 admission 继续依同一卡实施：纯 coordination decision / intent assessment / intent closure 与 history resumption planner 对照实际 TS，只接受已准入 Host facts。planner 的 checkpoint port 必须先拒绝不兼容的旧 engine/provider checkpoint；测试中的普通 JS 对象不证明原生可恢复，也不得开生产执行。

### NR-02 继续：共享 Goal 执行事实镜像与恢复

依 ADR 101 / 116 / 127 / 131，不改变 Goal 意图、权限或 Evidence 边界：计划为 GoalStore 增加同一 `index.jsonl.lock` 根写事务，TS public mutator、内部 persist/index 与 runner-progress flush 同域；本机原生仅开放 lease + source revision 约束的执行事实镜像端口，保留正文未知字段、sidecar 和 canonical revision/change 通知。复杂 Goal CRUD / workflow 仍归后续功能平价，不借镜像端口暴露任意模型 patch。根锁不按时间/PID回收，回调在释放锁后交付；源变更、未知 schema、超预算大正文、孤锁与缺失 index 都失败关闭。原生 closure 后镜像失败必须从既有 closures / retained_unknowns 对账重试，不另建恢复 journal，不清除 unknown，不重放调用。

实施前追踪确认：当前 TS Goal 写正文/sidecar/index 没有共享原生锁；只加 Rust 锁不能证明互斥。现有 bot-verified resolver 的 SQL closure 也不能代替 Goal 镜像恢复。验证至少包含 TS↔Rust root contention、两实例/进程写后读、callback 重入、runner sidecar 复查、body-before-index/closure-before-mirror 中断、未知字段与 unknown 保全、既有闭包重放恢复及后续任务准入。未验证前该共享写域与生产 P3 入口保持关闭。

### NR-02 总闸回执与 NR-03 启动

源码 `0809f7ca` 的完整 scoped 总闸通过：142 Rust、302 跨进程、131 旧侧 focused、840 权限/角色对照、60 admission、29 history planner、8 PTY、真实 Helper 无密钥 ping、fmt/clippy/release/architecture；TUI 30 项 Host 测试和引用本 checkout 新生成声明的 typecheck 通过。`9596dd03` 补齐纯 admission；`7775d3f4` 补齐共享 Goal 根事务、执行 control/closure 镜像及两阶段中断对账。closure 在旧 normalizer 丢失的真实问题已双端修正，保留失败记录。完整 Goal CRUD/产品工作流仍归 P5。详见 [P2 总闸结构化回执](native-cli/evidence/p2-total-20261114.json)。

7775 的 CI 不计通过：Linux clean-schema 夹具的未知版本仍只在 WAL，已强制 checkpoint 并断言主库版本，再保持原逐字节不变断言；另有独立 uncheckpointed-WAL 保全用例不变。macOS 类型错误来自 Goal bind 丢失 API 返回类型，已泛型保留，未给调用处补 any。首次本地总闸的 PTY guardian 清理卡住，终止该夹具父进程并保留 trace；改为 start_new_session 后在 guardian 内取得 controlling terminal，清理有超时，8 项新目录重跑通过。旧隔离 guardian PID 34341 的内核退出状态未能取样/回收，不算原轮成功；不触碰其它运行实例。9596 的 Mac Electron model switch smoke commit 断言失败仍保留，不称随机失败；新候选 CI 另查。

P2 数据/权限/恢复地基门禁已通过，允许开始 NR-03 原生纵向切片，不代表完整 CLI 或发布验收。补读 ADR 37/55/56/57，沿 129/130/131 搬迁，B 级边界不变：System Context 只经 Source assembler；历史以 canonical projector v2 为准，旧 tool 文字不能驱动新动作；wire 编码独立；模型输出只产生工具意图，Manifest→Projection→Tool Call→实时 Grant→Provider→结构化 Result/Evidence→canonical 会话/预算持久化。先支持一个现有 openai-chat wire 与有界 file/Shell foreground；未迁移的模式/凭据/上下文/旧 checkpoint 必须明确拒绝，不能静默少装上下文或借 Node sidecar 补齐。

NR-03 验收：隔离数据目录、原生 HTTP/SSE transport、真实 Host 权限 allow/deny/策略变化、文件与子进程的超时/取消/kill+reap、写效果前 canonical pending dispatch、Result/Evidence 配对、崩溃后 unknown 不重放、停稳镜像恢复、后续不同任务准入；同一个实际 exec composition root 验证。模型回答只结束执行片段，不构造 Goal 验收或业务完成。真实供应商/OS secrets、其它 wires、完整 Bot 角色和 UI 保持分期验收，不能以控制回放代替。

NR-03 Context 过渡 Adapter 明确：共享 core/work-session 资源从真实 TS Source 生成；workspace/provider 的既有 Source 语义迁移，临时 `native.goal-execution` 只把有界 canonical Goal 完整 JSON 作为 L7 事实呈现，不把未知文件/附件提升为指令，不增加 Goal 验收动作。完整 Goal Runner/项目/Skill/MCP/交互 Sources 尚未搬迁时，生产入口必须拒绝需要这些事实的路径；首条闭环限无这些特殊上下文的 fresh worker fixture。Shell 先暴露明确说明每调用新 shell、仅 foreground 的 Manifest，不能把尚未实现的 persistent session 宣传给模型。

0809 的 Mac CI 43592006532 原生测试触发旧 Helper tamper 夹具：首个随机 Base64 字符本来是 A 时替换 A 没有篡改。b8be67a2 改为解码后 XOR 一个字节并额外断言密文改变，12 Helper 测试通过；没有放宽认证错误断言。新候选 CI 另验。

### NR-02 远端总闸与 NR-03 第一条原生执行回执

P2 候选 `0b2ee6df` 的 [CI 43594616352](https://github.com/ly-ccx/Peer-Agent/actions/runs/43594616352) Linux / macOS 全部 job success，包含 Native、全仓 build/type/architecture/test 和各自 Bot shell smoke。b8 初次 CI 的 fmt 失败另由 0b 修正；旧失败保留，不把它们称通过。P2 总闸完成，完整 Goal CRUD、Bot 产品工作流仍归 P5。

P3 源实现 `cd13f250`，protocol 类型补充 `1eccbec7`：公开 `peer-native exec --plan` 组合 canonical Goal / lease / 协调、真实原生 HTTP/SSE、共享 Source/历史投影、独立 openai-chat encoder、Manifest/Projection、执行前实时 Grant、原生文件与 foreground Shell、配对 Tool Result/Evidence、原 canonical budget 与 managed pause。`recover --plan` 依据已记录的完整 nativeRecorder 与实际 OS 死亡观测停稳；有未结束能力句柄继续阻断。写效果后退出且未留回执的调用保持 unknown，不重放；不同资源的后续新任务可以准入。模型回复/CLI 退出码不构造 Goal 验收。

ADR pass：37-provider-channel-and-wire-protocol-separation、55-shared-system-context-assembler、56-provider-observed-context-accounting、57-canonical-conversation-history-projector、101-bot-owned-access-policy、111-project-agent-duplex-supervision-and-continuity、116-session-control-and-resource-settlement、117-intent-driven-coordination-and-goal-closure、124-legacy-stop-obligation-controlled-resolution、127-unknown-outcome-reconciliation-and-delegated-resolution、129-native-rust-cli-and-ratatui、130-bounded-cli-memory-and-transcript、131-native-cli-contract-storage-and-recovery（均为 knowledge/decisions/ 下的 `.md` 文件）。B 级迁移沿现有边界；新增的可选 nativeRecorder 合同与已确认文件创建身份属于 A 级补充，已分别在知识 `7072691` / `3e03860` 的 ADR 131 与 map 中先行记录，再实施。没有更改授权主体、unknown 闭包或 Goal 验收规则。

新文件正常路径曾被真实公开入口复现为 `execution_resource_busy`：原 missing claim 未随实际创建确认。补充只接受本 Host File Provider 独占创建并对照 owned fd 的身份；在真实配对结果、Evidence 与 dispatch 回执持久化后，ledger 事务核对原 scope / execution / hostEpoch / 当前 inode，更新原 claim revision 与 resource_events 的真实 tool-result 引用。相同身份幂等，既有 inode 变化、外来 Host/执行、unknown、draining/reconciling/released/closed 均拒绝；无推测刷新或强制解锁。

最终源码 `fd981b01`：169 Rust、302 旧存储跨进程、58 项当前 TS 对原生真实数据冷读（17 个隔离根）、131 旧 focused、12 项公开入口和 8 项终端生命周期通过；fmt/clippy/release/boundary/architecture 通过。完整本地回执和候选以 [P3 结构化证据](native-cli/evidence/p3-native-execution-20261114.json) 为准。范围包括实际公开二进制、真实 PTY allow/deny/cancel、Shell timeout/kill+reap、模型网络失败/截断/取消、真实文件效果后硬退出、原生恢复、unknown 保全与后续任务；当前 TS Store 冷读 native 输出及真实 Evidence 配对。TS/Bun 只用于开发对照，原生运行不启动 sidecar。终端/恢复状态同步到两张产品矩阵，自审不称独立审查。

本卡是方案定义的第一条原生闭环，尚非最终 CLI 替换：仅 fresh delegated worker / plain v2 openai-compatible channel / read_file、write_file、foreground bash。未迁移的项目指令、设置/权限清单、Skill/MCP、冻结 memory、嵌套上下文、compaction、其它 wire/auth/代理等明确拒绝。完整交互界面、功能平价、真实供应商和 OS 密钥闭环、安装/签名、长时间内存曲线及 P4–P7 继续待验收。默认 peer 尚未切换，不发布、不安装、不改用户原数据。

NR-03 远端失败保留：`fd981b01` 的 Linux job 132462052721 / CI 43599806661 在既有 `independent_threads_competing_for_a_free_lease_have_one_owner` 失败，第二个 acquire 返回 VersionChanged。静态追踪发现 hard-link 发布的临时别名 unlink 可改变共享 inode ctime，与竞争者严格身份读取存在相交窗口；隔离 inode 诊断确认内容/mtime 不变而 ctime 改变。macOS 原码的 256 轮竞争未复现 CI 原现场；另以确定性 lstat/open 间替换夹具在原码复现同一 VersionChanged 拒绝，修复后返回重新观测到的当前 owner。按 ADR 116/131 的既有租约合同作 B 级修复：仅在 acquire 原有五次上限内，遇到版本变化重新读取当前事实，再重新判断 owner/freshness；不放宽底层文件身份检查，不把 corruption/unknown 当空租约，不改 takeover、lease、stop 或授权边界。扩大原真实线程竞争用例，保留一名 Acquired、一名 Held 的原断言；修复后完整总闸与新候选 CI 另记。

租约修复 `15783800`：确定性原码 VersionChanged 基线已保存，修复后返回当前新 owner；256 轮真实双线程竞争仍是一名 Acquired、一名 Held。完整 scoped 新目录重跑通过：170 Rust / 302 跨进程 / 58 TS 冷读 / 131 旧 focused / 12 公开入口 / 8 PTY，fmt/clippy/release/boundary/architecture 均通过，SHA256 `63cf5bfb0d3b5633e7b4160e498e265811f5c70244dd86bcdbe5168887d2d543`。第一次修复总闸因测试模块位置触发 clippy，已移至末尾，未降级 warnings；原失败保留。新候选 CI 单独核对，fd981b01 的 Linux 失败不计通过。

P3 最终候选 `15783800` 的 [CI 43600632864](https://github.com/ly-ccx/Peer-Agent/actions/runs/43600632864) Linux job 132464474319 / macOS job 132464474532 的 Native CLI scoped validation 均 success，包含修复后的租约竞争和完整原生闭环/恢复。最后观察 Linux 仍在全仓 Test、macOS 在 Typecheck，未见已完成失败；不把两个 Native step 成功记成全仓 job 或发布通过。release 二进制另已核对不含 fixture-only 硬退出注入入口。P2 总闸与 P3 第一条闭环通过，不替代 P4–P7、真实供应商/安装/长期内存和完整体验验收。

## 2026-11-14 P3 全仓复核与 NR-04 启动

用户要求「先确认当前候选的全仓 CI 通过，再按方案推进 P4」「自测通过后继续推进 P5」。`15783800` 的 CI 43600632864 重跑结果：Linux job 132485357863、macOS job 132485356050 全部 success，含 build / Native / type / architecture / test / Bot Electron smoke。原 macOS job 132464474532 的 disclosure reversal 断言失败保留：采样从 316ms 到 617ms，间隔 301ms 跨过全部展开高度；不称原轮通过或已修复生产动画。原码/断言未改，当前源码树与 CI merge d7d8de61 的 tree 完全一致。本地重点场景通过；第一次本地运行仍经原工作区依赖链接，已限定证据，修正为本工作树依赖后重建与隔离场景再次通过。详见 [全仓跟进回执](native-cli/evidence/p3-ci-followup-20261114.json)。用户原数据与应用不变；只清理测试自有进程。

NR-04 按已接受 129–131 与既有 24/25/28/29/30/31/32/35/37/50/55/56/57/58/65/76 分步迁移，尚未写新完成状态。首卡允许 `peer-runtime` 的 wire / transport / model-config 模块、共享 fixtures、真实 TCP/HTTP/SSE 测试与 public exec 闭环；先固定实际 TS encoders、wire resolver、usage、失败与恢复行为，再接入生产调用。编码只在 wire seam；Source / canonical history、权限、Evidence 和 Goal 验收不借协议切换改变，首卡 B 级边界不动。Qoder 的宿主 Node/WASM fallback 必须迁走；若 Helper 或持久化 Interface 需要补充，则按 A 级先改 ADR/map 再实施。

后续卡依次覆盖完整 Context / accounting / compaction 管线、MCP（含 legacy SSE）/ Skill / Plugin / Hook 与生命周期、标准 headless/ACP/命令适配；P4 功能表逐项绑定真实入口和异常/恢复证据，不能以 pure encoder 或 SDK 自带能力算全部完成。允许方案指定的原生依赖（HTTP/TLS、数据解析、官方 MCP/ACP SDK、必要的有界原生适配），需锁版本/MSRV、实际编译和协议对照；不引入厂商 Agent SDK 或 JS 引擎。P5 仅在 P4 对应总闸通过后开始。

NR-04 首卡发现旧 Gemini usage Adapter 重复计算 cache：真实 `sendGeminiStream` 夹具 prompt=20 / cache=5 / output=3 返回 input=20，后续相加得到 28，而供应商 total=23。原失败保存于 `/tmp/peer-native-p4-gemini-usage-before.log`（临时本机证据，非持久制品）。依 Accepted ADR 56 的 disjoint dimensions 作 B 级纠正：uncached input 扣除已包含的 cache；供应商单列的 tool-use prompt / thoughts 分别计入 input / output，不遗漏、不给 cache write 编造 0。依据 [Gemini UsageMetadata](https://aistudio.google.com/api-reference/generate-content#Resource:GenerateContentResponse)，2026-11-14 核对。迁移对照不能把旧计算错误冻结成 Rust 黄金结果；同一原始 usage 用双端真实 Adapter 固定。没有改变上下文准入、计费权威或权限边界。

### NR-04 模型 wire 首卡回执（2026-11-15）

源码 `84007b83` 已推送。四种 wire（Chat / Responses / Anthropic / Gemini）进入同一个 `NativeModel` 及公开 `exec --plan`：原生 HTTP/SSE、Helper v1 API-key 请求头、实际 Provider Source、相同 Manifest/Projection/live Grant/Result/Evidence 与 managed pause。普通文本与工具同时返回时，原生连续性材料只跟随当前执行 / Provider 实例的精确 canonical 身份；完整 assistant 回合一起回传，避免 Anthropic 拆分 thinking/text/tool 或 Gemini 签名文本重复。缓存最多 32 项 / 1 MiB，签名不落盘；重启或事实改变不伪造材料。供应商终止标记立即结束并关闭客户端连接，不等待服务端 EOF；截断、失败终态和不完整参数不进入执行器。共有 normalizer 也保留真实 `redacted_thinking` 块，不把有签名的材料丢成普通历史。

实际 TS Provider 捕获固定 8 份请求/解码/计量，另有 1320 纯 encoder 向量；后者覆盖 reasoning/cache/OAuth 形状，但不等于这些配置已准入。实际配置只开放 plain v2 API-key 基本渠道；高级模型参数、额外渠道 / OAuth / Qoder、自定义头 / 配置代理等仍明确拒绝，不能静默丢配置。默认 `peer` 仍是迁移期入口，原生候选运行无 Bun/Node sidecar。

完整原生 scoped 总闸：179 Rust、302 跨进程 Store、70 当前 TS 冷读（21 个原生根）、134 Node focused、13 公开入口 Rust 测试（含四种真实 wire 的多轮工具），24 个 HTTP 分片组合、4 种原生 Helper 凭据头及注入拒绝、8 PTY；fmt/clippy/release/boundary、全仓 build/typecheck/architecture 与 20 项 TUI Provider focused 通过。失败及修正、精确候选与覆盖限制见 [NR-04 wire 结构化回执](native-cli/evidence/p4-model-wires-20261115.json)。CI 43615775154 正在核对，不将前一候选全绿继承给新候选。

ADR pass：`37-provider-channel-and-wire-protocol-separation.md`、`55-shared-system-context-assembler.md`、`56-provider-observed-context-accounting.md`、`57-canonical-conversation-history-projector.md`、`129-native-rust-cli-and-ratatui.md`、`130-bounded-cli-memory-and-transcript.md`、`131-native-cli-contract-storage-and-recovery.md`；本卡 B 级迁移及同边界修复，不移动权限、Evidence、Context 准入或 Goal 验收。完整 Runtime / 外部协议仍未通过 P4 总闸：继续 default Source / Host discovery、计数与 compaction / usage ledger、OAuth / Qoder、MCP / Skill / Plugin / Hook、headless / ACP / 命令平价；P5 继续受 P4 总闸约束。

NR-04 Context 首卡（实施前）：依 ADR 55/57/129/130/131，B 级迁移已登记的 project.instructions Source 与其有界文件观察，不新增附件或 tool output 的指令提升路径。Source 保留固定文件名、scope/trust、priority、截断说明、排序/hash/snapshot；只有 Host 的当前 workspace/data-home/配置与显式 targetPaths 能选择观察范围，普通文件内容不能自行注册 Source。当前生产先接 workspace 根指令，未迁移的设置/Skill/扩展仍阻断，不把一个 Source 算整个默认 catalog。与实际 TUI Host 对照时，Provider Source target 取 channelId（缺失时 provider selection id），路由 family 独立校验，不用品牌替代渠道事实。覆盖真实公开 exec、指令不能授权工具、文件变化/读取失败、超限、Unicode 截断和 TS Source 差分；24000 UTF-16 单位截断遇到代理对时需保全完整字符，不能把旧孤 surrogate 冻结成跨语言合同。

NR-04 CI 跟进：`84007b83` 的 CI 43615775154 两平台 Native scoped 均 success，随后全仓 Test 因旧 Desktop Gemini 断言 `inputTokens=11` 失败（实际 uncached=8，cache=3；自动隔离重试仍失败）。实现者遗漏了旧断言更新，不称基础噪声。`1f7adc17` 仅修测试：保留原 prompt 11 与 output 7，明确 8+3=11、总量 18、未知 cache write 不编造 0；本地该文件 22 项通过。原失败与后续独立候选分别登记于 wire 回执，不把原轮改记通过。

NR-04 Context 首卡回执：`10c86bd7` 已推送，workspace 根 AGENTS/CLAUDE 通过原注册 Source 接入公开原生 exec；文件内容不能签发 Grant。正常/空/Unicode/截断/缺一文件的实际 TS Source 差分、真实变更中断/坏 UTF-8/超限保全、公开否决工具与同一待准入任务恢复、非普通文件 FIFO 不阻塞均已验证。Source 的共享截断 helper 修复了可复现的半个 surrogate，保留原失败。Provider Source 的 Host 目标值与现有 TUI 入口对齐为 channelId / selection id，独立于路由 family。完整 scoped：184 Rust、302 跨进程、79 TS 冷读（24 根）、157 Node focused、16 公开入口 Rust、8 PTY；7 指令 Source / 14 Provider Context 向量、13 共享 Source focused、build/clippy/架构通过。详见 [Context Source 证据](native-cli/evidence/p4-context-source-20261115.json)。CI 43618145086 尚在核对。当前只开放 workspace 根 Source；完整 catalog、配置/全局/显式目标子目录、计数压缩和外部协议仍未过 P4 总闸，不进入 P5。

NR-04 usage 后续（实施前）：依 ADR 37/56/131 作 B 级观察完整性修复。`usage` 对象存在但缺输入或输出维度时，不能由默认 0 合成已知总量；仍可记录请求及完整结构化工具结果，但 Work budget 必须保留 unknownUsage，后续有 usage 的请求不能抹去该未知。不把供应商部分总量冒充完整 canonical 维度，不引入私有 ledger 或迁动持久化边界。完整 request/turn/lifetime 管线仍是独立待完成项。

NR-04 Instructions 后续（实施前）：ADR pass 为 `55-shared-system-context-assembler.md`、`57-canonical-conversation-history-projector.md`、`129-native-rust-cli-and-ratatui.md`、`130-bounded-cli-memory-and-transcript.md`、`131-native-cli-contract-storage-and-recovery.md`；B 级迁移既有 Source / Host Interface，边界不动。扩展同一 project.instructions 到 typed Host 配置、显式全局开关与显式 targetPaths 的有界发现；实际 TUI 默认不自动打开 global，原生遵守这一点。当前原生 exec 先准入只包含已迁移 prompt 设置的 settings.json，缺省语言和 branch prefix 对照现有 TUI；其它键仍在请求前阻断，损坏 / 新 schema / 非普通文件 / 读取变化保全并明确失败，不借读取重写设置或迁移项目身份。全局 / scoped Source 能力以实际差分测试单列，不把未装配的生产开关或显式目标输入算 Host 已完成。验收覆盖同根真实公开请求、configured guidance 不可授权、未知设置仍阻断、坏设置修正后同一待准入任务可继续，以及全局 / scope 发现次序、去重、越界、Unicode、总预算与取消前置。

NR-04 CI / usage 跟进：`10c86bd7` 的 Linux 全仓 Test 与自动隔离重试均在旧 fixed-result CLI 复合用例超过 Bun 1.2.17 的单测试 5 秒缺省时限；macOS Test success、后续 smoke cancelled，原轮不记全绿。`ea7e8e4d` 将独立命令拆为 12 项自有夹具测试，保留原断言与每项时限，并新增同一引用清理前后身份断言。相同 CI Bun 版本本机 12 pass / 33 assertions；受控每次启动延迟 400ms 的替代复现中，原复合测试 5042ms 超时并终止一个自有子进程，拆分后全文件 8.06 秒 / 单项最长 1530ms 通过。该实验解释累计预算，不声称复现 Linux 调度现场。原生 `e6ae5561` 同时修正部分 usage 缺维度被当已知零的问题：真实工具请求后再有完整 usage，原 unknownUsage 仍保留。完整 scoped 为 186 Rust / 302 Store / 82 TS 冷读（25 根）/ 157 Node focused / 17 公开入口 / 8 PTY。历史部分原始 usage 未保存，不能从聚合预算重建缺失量；未改个人数据、重放请求或编造历史值。完整 request/turn/lifetime ledger 仍待完成。详见 [CI 与 usage 跟进证据](native-cli/evidence/p4-ci-and-usage-followup-20261115.json)。

NR-04 Instructions 后续回执：`f6949bae` 固定了配置指导、显式 global / scoped Source 发现与原生 Host 的 prompt 设置子集。实际 TUI Host + TS Source 对同一自有文件的 28 项跨进程对照，包括真实绝对路径参与的 checksum；缺省值、九种回复语言、截断、路径/去重、显式目标和全局与 workspace 同路径均通过。公开 exec 的配置指导不能批准写入；未知设置、坏编码/JSON、错误类型与新 schema 保留原文件并阻断，修正后同一 ready task 继续；设置 FIFO 及时失败。全局仍默认关闭，尚未新增生产 global/target-path 开关，不把 Source seam 测试算全部 Host 发现已完成。完整 scoped：190 Rust / 302 Store / 91 TS 冷读（28 根）/ 157 Node focused / 19 公开入口 / 28 Source 跨进程 / 8 PTY，fmt/clippy/release/boundary/architecture 通过。详见 [Instructions 发现证据](native-cli/evidence/p4-instruction-discovery-20261115.json)。完整 Context catalog、计数压缩、durable usage 与外部协议继续属于 P4 总闸，P5 未开始。

NR-04 远端总仓复核：`e6ae5561` 的 [CI 43622520379](https://github.com/ly-ccx/Peer-Agent/actions/runs/43622520379) Linux job 132531262083 与 macOS job 132531262439 全部 success，含 Native、全仓 build/type/architecture/Test 与各自 Bot Electron smoke。实际 CI merge `2549e2a0` 的 tree 与 e6 完全相同；macOS annotation 仅为 arm64 runner capacity notice，无失败。Source 新候选 `f6949bae` 已推送，独立 [CI 43624988490](https://github.com/ly-ccx/Peer-Agent/actions/runs/43624988490) 尚在运行，不能继承 e6 的全绿。原 Gemini 旧断言失败与 compound-test 超时均保留；本轮通过不抹除原失败。

NR-04 usage scope（实施前）：复核 Accepted `56-provider-observed-context-accounting.md` Phase 5、`37-provider-channel-and-wire-protocol-separation.md`、`129-native-rust-cli-and-ratatui.md`、`131-native-cli-contract-storage-and-recovery.md`，B 级迁移既有 RuntimeUsageAccounting / tagged UsageAmounts；不移动权限、Evidence、Context authority 或存储边界。原生 Module 对每次实际请求（含 null usage）计数，按 disjoint 维度累计回合，最后 capacity-bearing 单请求独立覆盖，summary 计费但不替代 context observation。公开 exec 成功/轮数耗尽回执使用现有 runtime_turn/provider_request 类型；不把回合总数除以上下文窗口，不将该 JSON 回执冒充 durable usage 或错误回合已恢复。当前 Work budget 的持久计数 / unknown 保持原路径；完整 ledger、异常终态持久化、count/compaction 后续另验。

NR-04 usage scope 回执：`83a0733f` 的 typed ProviderRequestUsage / RuntimeTurnUsage 与原生 RuntimeUsageAccounting 接入公开 exec。实际两次 read_file、三次模型请求，最后一请求 59 与回合 144 分别带 provider_request / runtime_turn tag；后续独立任务从 1 次 / 16 重新开始。部分 usage 后的已知 16 只是已知量，Work budget unknownUsage 仍 true；max_turns 回执保留单请求与真实配对结果。7 份实际 TS 序列 / 17 次观察覆盖 null/zero、cache、原 raw total 不可信、auxiliary summary；summary 仅为 Module seam 测试，原生 compactor 尚未接通。溢出拒绝不改既有累计。复核修正了 lease-loss `.await?` / budget 提前返回跳过观察的路径，并在固定候选重新跑完整 scoped：194 Rust / 302 Store / 97 TS 冷读（30 根）/ 157 Node / 21 公开入口 / 28 Source 跨进程 / 8 PTY，fmt/clippy/release/boundary/architecture 通过。lease-loss 计数分支为静态追踪修正，不声称专门复现竞态；前后 patch、候选和范围见 [usage scope 证据](native-cli/evidence/p4-usage-scopes-20261115.json)。当前 JSON 回执不等于 durable ledger、异常用量已恢复或 Context 占用权威；完整 P4 总闸与 P5 仍待完成。

NR-04 Source 全仓复核：`f6949bae` 的 CI 43624988490，Linux 132538724196 与 macOS 132538724407 全部 success，含完整 Native / build / type / architecture / Test / Electron smoke。CI merge `20e5bc13` 的 tree 与 f694 一致。随后才推送已完成本地 scoped 验证的 usage 候选 83a0733f；新 CI 必须独立核对，不继承此全绿。

usage 候选 `83a0733f` 已推送，独立 [CI 43627852431](https://github.com/ly-ccx/Peer-Agent/actions/runs/43627852431)（Linux 132547656519 / macOS 132547656837）正在执行。本地二进制 SHA256 `4c4a0869ba8194a836ea1217fabab363e1ece130632887752cdc8965ad88bee4`；新 CI 尚未记为通过。P4 总闸仍缺完整 Source catalog/Host discovery、count/compaction/rebuild/recount、durable request/turn/lifetime、OAuth/Qoder、MCP/Skill/Plugin/Hook、headless/ACP/命令；P5 未开始。

2026-11-15 继续前置 CI：83a0733f 的 Linux 全仓 success；macOS Native/build/type/architecture/Test success，最后 Bot smoke 在 accessibility checkSettings 的开关恢复等待超时。保留原失败 job 132547656837、merge 5885ba1d（tree 与83一致）、714451568-byte artifact 14127503675。完整首个 trace entry 已从自有诊断下载前缀解出：call@20911 before=true、input=false、after=true，后端 false→true 后该次操作再次保存 true，表明操作时展示发生了陈旧回滚；不把它直接称 flake。原源码/断言的单 job 重跑仅用于确认候选，不能证明此生产竞态已修复。

前置修复卡（实施前）：复核 `85-project-agent-hosts-inputs-and-surfaces.md`、`129-native-rust-cli-and-ratatui.md`、`131-native-cli-contract-storage-and-recovery.md` 与当前交互/transition标准，B/C级档案只读投影修复，权限/存储/策略边界不移动。允许 Bot details pending reader 失效、catalog read-vs-commit fence、实际调用者装配、确定性迟到读取测试和原 Electron smoke；不改原开关时限/断言，不自动翻转已保存策略。先保存83原实现的复现失败，再验证本地保存回执不能被早发读取覆盖；旧错误保存只呈现当前真值与既有显式修改入口，不推断历史用户意图。

前置修复候选 `6406f7af`：pending details 在真实保存回执后失效并有界重读，catalog 保留读取等待期间发布的 profile。83 原实现的三项迟到读取复现失败已保留，修复后 25 聚焦 / 9 邻接测试与 Desktop type/build 通过。隔离原 Electron smoke 的八种开关主题与原失败的设置恢复均通过；随后因调用方未创建附件输出目录而失败，源诊断 JSON 已验证，补齐目录后原命令重跑中。不称全 smoke 或新 CI 已通过。详见[原始 CI 与修复回执](native-cli/evidence/p4-ci-profile-recovery-20261115.json)。

`6406f7af` 固定 clean source 的原完整 Electron smoke 第二次通过，所有原断言/时限保留：accessibility、diagnostics、streaming、effort-stability、work-surfaces，200 Bot 诊断无错误/私人字段，8 种开关主题通过，owned process 正常退出。第一次附件目录失败仍保留；此源码自测不替代83远端重跑或6406新 CI。

前置 CI 已确认：83a0733f 的 run43627852431 重跑 Linux132676885967 / macOS132676884582 全仓 success，原断言与源码树不变，merge5885ba1d tree1a38894b与83完全一致。随后推送已完成原完整 Electron smoke 的6406修复候选，并按 ADR25/56/129–131 开始 durable ledger 卡。ADR131 的2026-11-15 NR-04补充及map先于代码登记；A 级只收紧 Store 双文件失败恢复，不移动权限/Evidence/Context或Goal签收边界。

NR-04 durable Store 候选 `be497066` 已推送：ADR131 的 A级双文件提交恢复先登记，Rust/Node共享同一 v1意图与锁，真正流式扫描、按原始行补缺失后缀，不截断未知。固定 clean source 的完整 scoped通过：194 Rust / 28 新账本跨进程 / 原302 Store / 97 TS冷读（30根）/ 21公开入口 / 11新Store聚焦 / 8PTY；Store全包145、Desktop用量62、type/build、881 packaged imports与architecture通过。28场景包括双端互相恢复、硬退出与受控孤锁维护、未知保全、并发同id与后续回合。保留重复计费原缺陷和实施中的断言失败，未改旧幂等断言。详见[账本Store回执](native-cli/evidence/p4-durable-ledger-store-20261115.json)。这还不是原生exec持久计费闭环：下一B级卡按同一ADR接成功/错误终态、准入预检、native recover及heartbeat；完整计数/压缩与外部协议仍缺，P4总闸未过，P5未开始。

Host账本卡的实际缺陷基线：完整空回复携带已归一化供应商usage时，现原生ModelError仅有静态码，公开exec错误终态无billing行。新增真实HTTP/公开入口断言失败（不是用编造Tool Result补账）。按 ADR25/37/56/129/131 继续B级Provider error seam：错误可携带有限的已观察UsageAmounts与本次不可变request fingerprint；不携带秘密/原始HTTP正文，不把失败变成成功或可执行调用。终态先停止/排空，再结算已知用量；Store故障仍保留意图，原recover不重放模型/工具。该补充不移动既有权限、Evidence、Context准入、存储格式或Goal验收边界。

NR-04 Host终态账本候选 `9fb1b4ff` 已推送：成功/max_turns/已知错误/取消在真实停稳尝试之后、终态呈现之前落盘；Native recover 修复原提交不重放模型/工具。ModelError保留有限归一化用量及实际send字节指纹，空回复/截断流仍失败，接管时的未完成工具意图未执行而已知用量保留。完整scoped通过：202 Rust / 28公开CLI / 28 Node与28 Bun账本跨进程 / 原302 Store / 127 TS冷读(40根) / 8PTY；fmt/clippy/contracts/release/boundary/architecture通过。实测受控6秒I/O挂起期间5.007秒续约、6.051秒退出；旧断言混合启动与清理导致的失败及分段修正保留，不称flake。详见[Host账本回执](native-cli/evidence/p4-durable-ledger-host-20261115.json)。be497066的CI43673952633两平台全仓success，merge65ad4dbb tree与候选一致。9fb新CI独立核对。终态前硬退出的原始用量仍可能缺失，聚合预算与unknown保留；完整P4未总闸，P5未开始。

下一A卡先登记 ADR131 NR-04 canonical预算观察快照与map，限work_session、billing-only。模型观察先随原Work预算落盘，Loop终止后移入原budget的pending，真实Store回执后CAS清除；stop/unknown/许可不由该快照决定。以解决新执行在工具效果后硬退出时原始用量丢失，不追写旧无分量记录；随后继续count/compaction等P4余项。

NR-04 canonical 用量恢复候选 `0ffdec08`：ADR131 的 A 级预算快照补充与 map 先登记，knowledge `fe555e4` 先于源码交付。真实观察与预算同事务先于工具执行；循环结束后保留 OS recorder 至真实停稳，闭合快照按原账本 id 核对后 CAS 清除。文件效果后硬退出仍一次入账16，原工具 unknown 不变。未来快照先停稳再阻断、原始事实保留；65条按64/1分批核对、重复 recover 无重复账目、随后新任务可准入。逐条确认导致的246.07秒失败和首轮完整验证的 HTTP fixture 存活期耗尽均保留；同Work合并CAS后单项8.32秒，后续任务在恢复后启动独立有界HTTP fixture。补齐连续短操作跨越持久 heartbeat deadline 的续约测试。最终固定候选完整scoped：208 Rust / 32公开CLI / 47原生根254 TS往返（实际saveWork及Rust重读）/ Node28+Bun28账本 / 原302Store / 8PTY，fmt/clippy/contracts/release/boundary/architecture及protocol build/type通过；release无故障注入口。详见[canonical恢复证据](native-cli/evidence/p4-canonical-usage-recovery-20261115.json)。9fb1b4ff的CI43678064980 Linux132702469993/macOS132702470142全仓success，merge50ebfd41 tree与候选一致。0ff新CI独立核对。

下一计数卡（实施前）：复核 ADR37/55/56/57/129/130/131，B 级迁移同一 provider encoder/count seam，权限、Evidence、Context ordering 与持久化边界不动。先冻结不可变 Prepared Request，计数从同一编码对象派生，send 使用原字节和指纹；Anthropic去掉stream/max_tokens，Gemini以generateContentRequest计数，OpenAI维持observed-only。计数失败明确降级，不阻断健康的generation；取消/超时/错误必须有界，不把计数当模型计费、工具或许可。按当前官方 count_tokens / countTokens 文档核对路径与载荷，再做实际HTTP及TS交叉测试。此卡不代替compaction/rebuild/recount与Host完整接线验收；P4总闸未过，P5未开始。

NR-04 不可变计数 Module 候选 `c136ced`：count从同一原生encoder结果派生，send消耗原始字节，PreparedRequest按借用绑定原NativeModel。Anthropic/Gemini计数载荷与30份实际TS Adapter输出一致，真实HTTP验证调用方准备后修改输入不影响count/send、坏计数仍可发送、timeout/cancel关闭socket、OpenAI/OAuth不探测不适用端点。完整scoped为213 Rust / 32公开CLI / 47根254 TS/Rust往返 / Node28+Bun28账本 / 原302Store / 8PTY，fmt/clippy/contracts/release/boundary/architecture通过。保留timeout误分类、阻塞join使Tokio reactor无法处理关闭和clippy类型复杂度的失败，未放松socket断言；详见[计数Module证据](native-cli/evidence/p4-native-count-prepared-20261115.json)。本卡没有把Module测试冒充公开CLI count/compact/rebuild/recount闭环：Host尚未调用计数，计数漂移、压缩、容量快照持久化及外部协议仍属P4余项。0ffdec08的独立CI43682734166仍进行中；新候选CI不继承旧结果。

下一容量卡（实施前）：依 ADR37/55/56/57/129–131 继续 B 级迁移现有 ContextAccountingSnapshot 的权威选择、同请求计数验证与明确降级；不把 runtime_turn/lifetime 充作占用，不改变许可/Evidence或持久化边界。先以实际TS pipeline冻结provider_count_api/observed-only、缺失用量、同指纹漂移、epoch失效和pending行为，再接Native Host。Source尚未接通的容量恢复/压缩/overflow重试继续明确未验收，不用一个占用数字宣告完整P4。

NR-04 容量Host候选 `daa4c478`：公开exec已调用同一不可变请求的count，保留原Host ownership/heartbeat与终态停稳；采用既有ContextAccountingSnapshot分别呈现单请求容量、pending与降级。实际Anthropic/Gemini各两次模型请求、一次真实read_file：count12与observed20的漂移或count404均使后续counter停用，generation继续；账单46不进入容量20，显式窗口1000呈现2%。OpenAI三请求账单144、最后请求59、容量50+cache5=55；窗口未知时percent为null，后续新任务容量12。原误写56的断言失败及夹具 .tmpF2McVy 保留，修正算术后原账单断言不变。context revision用已有index-only seam跟进实际提交，超安全范围拒绝，不再clamp身份。10组实际TS pipeline序列冻结authority/pending/drift/epoch/recount等kernel语义；不把epoch单测冒充真实压缩。最终冻结源码scoped为216 Rust / 33公开CLI / 51根274 TS/Rust往返 / 30计数Adapter向量 / Node28+Bun28账本 / 原302Store / 8PTY；fmt/clippy/contracts/release/boundary/architecture通过。见[容量Host证据](native-cli/evidence/p4-native-capacity-host-20261115.json)。c136的CI43683648966在两端Electron smoke期间被新推送取消，之前build/native/type/architecture/Test成功、无失败步骤，不记全仓success。新候选独立CI待核对。Context容量持久化/恢复、压缩落盘/重建重计数/overflow、完整Context catalog与外部协议尚未总闸，P5未开始。

2026-11-15: daa4c478 CI43685522973 passed Linux132725178298/macOS132725178077 in full. Merge e806eddd and candidate share tree f90c761c. ADR131/57 historySelection/projector3 decision precedes implementation; warm1/cold4 baseline retained outside the repo.
