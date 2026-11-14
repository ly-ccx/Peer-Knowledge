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
