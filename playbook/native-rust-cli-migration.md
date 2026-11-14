# 原生 CLI 迁移实施账本

创建时间：2026-11-14
最后更新：2026-11-14
状态：P0 取证 / P1 scoped 自测通过；P2 实施中（不代表完整迁移或发布验收）

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
