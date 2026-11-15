# 原生 CLI 迁移实施账本

创建时间：2026-11-14
最后更新：2026-11-15
状态：P0–P3 scoped 总闸通过；P4 实施中，P5 未开始（不代表完整迁移或发布验收）

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
