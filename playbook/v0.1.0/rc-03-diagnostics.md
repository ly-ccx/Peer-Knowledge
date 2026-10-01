# RC-03 诊断实施边界

创建时间：2026-10-02
状态：Accepted，负责人授权自主完成全部 RC；GA 仍等全面测试。

## 级别与范围

A级 IPC/消息元数据边界先见 ADR 85 RC03；其余 B级投影/宿主装配，C级开发者 UI。单独卡/分支/PR，从已合入 RC01/02 开发线实现；这里先记录实施合同，不以文档代替实际退出证据。

允许文件：

- `packages/protocol/src/project.ts`及协议导出/测试：诊断 DTO 与可选既有 agent-turn timing。
- `packages/runtime-node/src/project-agent/diagnostics.mjs`及测试；`runner.mjs`/测试（既有消息可选时长）；`input-queue.mjs`/`project-inbox.mjs`及测试（有界只读快照）；index 导出。必要的已有 scheduler/watch 只读接口与定向测试。
- `apps/desktop/electron/main/project-agent/diagnostics-export.mjs`及测试；`project-agent-host.mjs`装配、现有 application service/IPC 注册与测试。
- `electron/ipc/channels.mjs`、preload source/生成物、renderer preload 契约/clientApi 及 caller-policy 测试；沿现有 IPC sync/check 脚本，不扩展其他窗口权限。
- `renderer/project-agent/diagnostics/`深展示 Module、现有 DeveloperPanel 替换占位、必要已有 styles，packages/i18n 中英文键。
- 专用 Electron 诊断检查脚本或现有 RC smoke 装配，package.json 与必要 CI 实际验证调用。

main.mjs 净增 0；不增依赖/模型工具/Context 来源，不修改真实用户数据/权限决策/旧会话。诊断只读，不推进队列/租约/批准/Watch。

## 必须证据

脱敏/边界/无副作用/损坏与 unknown/原子失败/取消/窗口准入测试；完整受影响测试、build/typecheck/architecture/IPC check、中英文一致；真实 Electron 保存到隔离文件，检查 JSON 并附脱敏样本。未运行/失败必须保留。
