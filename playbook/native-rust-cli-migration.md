# 原生 CLI 迁移实施账本

创建时间：2026-11-14
最后更新：2026-11-14
状态：实施中，P0/P1 未验收

用户已接受评审稿 116–118；正式 ADR 为 129–131（避免与主线既有编号冲突）。用户要求 P0/P1 自测通过后持续推进至完整原生 CLI，无 Bun/Node sidecar。本账本记录候选与实际结果，不替代 ADR 或 Evidence。

## NR-00 / P0

允许：`scripts/native-cli/` 的隔离审计 / 测量工具、可分享合成 fixtures、知识库实施回执。真实入口为旧版 release CLI 的 classic 与 Bot 两条路径，使用临时数据根与受控 PTY。严禁个人数据 / 凭据 / 运行中实例；现有 8.27 GB 截图未精确复现，长历史渲染与流式链路须分别记录替代范围。

退出：模块可达 / 持久化 / 功能清单；source / binary / fixture 身份；五次短基线曲线与失败；明确待覆盖项。资源目标按 ADR 130 保持。

## NR-01 / P1

允许：Cargo workspace / lockfile、`crates/peer-{cli,protocol,tui}`、`packages/protocol/contracts/native-cli/`、对应 scoped 测试与构建 / 观测脚本。准许所需 Rust 依赖，版本须锁定。终端仅候选 / 草稿，不接管任务、不签发授权、不把用户文本发送给模型。

退出：独立原生二进制；轻量 help/version/doctor 路径；真实 TS/Rust 契约对照；Ratatui 渲染与输入 reducer；真实 PTY 的粘贴、Unicode、resize、Ctrl-C、EOF、panic 恢复与无 Node/Bun 路径；静态依赖规则、fmt/clippy/test/build。缺少真实 IME / 其他平台明确未覆盖，不冒充全产品验收。

## 后续

P1 通过后按方案进入 P2 数据、权限、锁与旧状态恢复；再推进原生工具闭环、Provider、项目代理、空间验收和发布切换。首轮不因骨架通过就将默认 peer 替换为功能不完整候选。
