# B4-08 交接记录

创建时间：2026-10-01
最后更新：2026-10-01

## 卡片
B4-08 记忆维护；[实施契约](b4-08-memory-maintenance.md)。负责人授权全部 B4 及必要接入与合入。

## 分支与提交
`PeerAgent/pa/b4-08-memory-maintenance`，dev 基线 54a937d5，代码 8811af15，[代码 #81](https://github.com/ly-ccx/Peer-Agent/pull/81)。

## 改了什么
纯日维护及 device 当日检查点；到期/90 天衰减与固定/职责保护。单值 topic 元数据、权威取代与模糊冲突组、宿主选择真值及既有 typed restore IPC、卡片/记忆页来源状态。实际工作区哈希/HEAD 锚点，变化退出有效检索/新快照，在 L7 独立标待核实；新证据与实际锚点重新准入，旧冻结快照不改。修复既有 search scope 校验拒绝。

## 与卡片的偏差
A 级 ADR 81 Accepted；接入、可选协议字段、数据清单先写实施契约。ADR 的明确新权威取代高于卡片的全量两条冲突描述。无新依赖/IPC 通道/工具，main.mjs 无改动。

## 验证
- `pnpm build`、`pnpm typecheck`、`pnpm architecture:check`、Desktop `ipc:check`、`git diff --check` 通过。
- Runtime 904 通过；System Context 31 通过；Protocol 173 通过。
- 首轮 Desktop 全量一个文件监听超时后隔离重跑 142 全通过；Review 修复后的全量 Desktop 5187 通过、0 失败、5 既有跳过。未新增失败/skip。
- 纯维护、截止/衰减/固定/职责、作用域/冲突选择重启、实际文件哈希和 symlink 越界、旧证据/缺锚点拒绝、有效检索与冻结历史、经典/无租约/关闭、typed IPC/renderer 边界均有定向验证。
- 最终 3116ea77 的双平台 [CI 36838779479](https://github.com/ly-ccx/Peer-Agent/actions/runs/36838779479) 全部通过；知识 Review 指出旧 canonical schema 不符，§4.1 与旧检索/维护措辞已对齐 Beta4，明确长期未实现能力。代码 Review 两条意见已先红后绿修复：单值主题跨 kind 判定、桌面全局搜索同样过滤有效性。最终 8811af15 的 build/typecheck/architecture 和受影响完整包通过，最终提交的双平台 [CI 36839816130](https://github.com/ly-ccx/Peer-Agent/actions/runs/36839816130) 全部通过；两条代码意见和一条知识意见均已修复并关闭。

## 架构影响
MemoryStore、Curator、Provider 和 L7 Source 沿已有接缝；模型不提供权威哈希，不控制维护状态。projects/userMemory 追加可选元数据，projectRuntime 设备维护完成事实已登记。记忆架构 §7.4 对齐实际 Beta4 边界。

## 文档偏差
知识在 companion repo。旧长期架构的 revocation/stale 术语由 §7.4 映射到 Beta4 forgotten/expired/conflicted/needsReverify，不声称已经实现 MM5 或长期全部维护能力。

## 未完成与后续
代码 #81 已按负责人授权合入 dev（8d607ea3），本卡完成。继续已 Accepted ADR 82 的 B4-04/05/06、B4-R。真实模型/UI/打包证据留发布卡，不以脚本测试替代。Beta4 未发布。
