# RC 实时过程与档位稳定性修复

创建时间：2026-10-05
最后更新：2026-10-05
状态：InProgress（两批本机交互验收已通过；追加提交待双平台 CI）
分支：PeerAgent/pa/rc-live-process
源码提交：bcd154232e86e0576a7b20aab099f7cb6a3a9c20（追加）；第一批 d943be3aeae89fb6826bcf8e301a3c4e34d910b8
源码 PR：https://github.com/ly-ccx/Peer-Agent/pull/122
CI：https://github.com/ly-ccx/Peer-Agent/actions/runs/37292590731（双平台通过）
派单来源：负责人 RC6 实测截图与交互修复要求。

## 范围

- 档位提交时保留选择，失败回退并提示；固定最长标签空间，弹层随尺寸更新。
- 同一用户回合实时过程：当前动作扫光、耗时、展开实际步骤、嵌套参数/结果/技术详情；完成交接保留展开状态，停止/失败结束动画并保留事实。
- 深浅主题、760px 窄窗口、键盘与 reduced-motion。
- A 级边界在实现前登记于 [ADR 87](../../knowledge/decisions/87-user-turn-live-process-presentation.md)。B 级 Runner 仅复用既有时钟与 TurnSink；执行/权限/Evidence 路径未变化。

- 追加 C 级展示范围：回复下方区分任务状态、需要用户处理的入口、结果依据；沿用既有 session 读取与通知，实时刷新实际状态。
- 过程/证据使用独立查看面，不再串入概况与记忆。概况展示 Bot 身份、职责、绑定项目与实际配置；记忆优先展示内容，设置与来源按需展开。

## 本卡允许改动（代码仓相对路径）

- `.github/workflows/ci.yml`
- `apps/desktop/renderer/src/chat/components/thread/ReasoningEffortSlider.tsx`
- `apps/desktop/renderer/src/chat/styles/chat-surface.css`
- `apps/desktop/renderer/src/project-agent/BotModelControls.tsx`
- `apps/desktop/renderer/src/project-agent/conversation/BotConversation.tsx`
- `apps/desktop/renderer/src/project-agent/conversation/BotMessageList.tsx`
- `apps/desktop/renderer/src/project-agent/conversation/BotProcess.tsx`
- `apps/desktop/renderer/src/project-agent/conversation/LiveReply.tsx`
- `apps/desktop/renderer/src/project-agent/conversation/ReplyBubble.tsx`
- `apps/desktop/renderer/src/project-agent/drawer/AgentProcessView.tsx`
- `apps/desktop/renderer/src/project-agent/drawer/BotPolicyFields.tsx`
- `apps/desktop/renderer/src/project-agent/drawer/BotSettingsTab.tsx`
- `apps/desktop/renderer/src/project-agent/drawer/agentProcess.test.ts`
- `apps/desktop/renderer/src/project-agent/drawer/agentProcess.ts`
- `apps/desktop/renderer/src/project-agent/state/botActivityState.test.ts`
- `apps/desktop/renderer/src/project-agent/state/botActivityState.ts`
- `apps/desktop/renderer/src/project-agent/state/botConversationState.ts`
- `apps/desktop/renderer/src/project-agent/state/useBotConversation.ts`
- `apps/desktop/renderer/src/project-agent/styles/bot-model-controls.css`
- `apps/desktop/renderer/src/project-agent/styles/bot-process.css`
- `apps/desktop/scripts/bot-effort-stability-checks.mjs`
- `apps/desktop/scripts/bot-shell-accessibility-checks.mjs`
- `apps/desktop/scripts/bot-shell-electron-smoke.mjs`
- `packages/i18n/src/index.ts`
- `packages/protocol/src/index.ts`
- `packages/protocol/src/project.ts`
- `packages/protocol/src/tool-activity-preview.ts`
- `packages/runtime-node/src/project-agent/runner.mjs`
- `packages/runtime-node/src/project-agent/turn-activity.mjs`
- `packages/runtime-node/src/project-agent/turn-activity.test.mjs`
- `scripts/rc-response-interaction-smoke.mjs`

- `apps/desktop/renderer/src/project-agent/BotListShell.tsx`
- `apps/desktop/renderer/src/project-agent/conversation/ReplyContext.tsx`
- `apps/desktop/renderer/src/project-agent/conversation/ReplyAnchors.tsx`
- `apps/desktop/renderer/src/project-agent/conversation/DelegatedWork.tsx`
- `apps/desktop/renderer/src/project-agent/state/botWorkState.ts`
- `apps/desktop/renderer/src/project-agent/state/botWorkState.test.ts`
- `apps/desktop/renderer/src/project-agent/state/drawerContract.test.ts`
- `apps/desktop/renderer/src/project-agent/state/useBotWorkSessions.ts`
- `apps/desktop/renderer/src/project-agent/styles/bot-reply-context.css`
- `apps/desktop/renderer/src/project-agent/drawer/BotProfileDrawer.tsx`
- `apps/desktop/renderer/src/project-agent/drawer/OverviewTab.tsx`
- `apps/desktop/renderer/src/project-agent/drawer/MemoryTab.tsx`
- `apps/desktop/renderer/src/project-agent/styles/bot-drawer.css`
- `apps/desktop/renderer/src/project-agent/styles/bot-conversation.css`
- `apps/desktop/scripts/bot-shell-reply-checks.mjs`
- `apps/desktop/scripts/bot-shell-chat-detail-checks.mjs`
- `apps/desktop/scripts/bot-work-surface-checks.mjs`

## 验证命令

```sh
pnpm --filter @peer-agent/desktop build
pnpm typecheck
pnpm architecture:check
pnpm --filter @peer-agent/runtime-node test
pnpm --filter @peer-agent/protocol test
pnpm --filter @peer-agent/desktop test
pnpm --filter @peer-agent/desktop smoke:bots --streaming --accessibility --effort-stability
```

Mac/Linux 开发线 CI 接入 streaming 与 effort-stability 回归。测试只在独立临时数据和受控认知 seam 运行；不修改用户应用数据。本卡不发布新的版本号。

## 负责人追加反馈验收

详见 [消息与档案的信息归属及实机截图](../../design/product/bot-human-readable-work-surfaces.md) 与 [机器报告](evidence/bot-work-surfaces-qa-20261005.json)。追加仅为 C 级展示修正；子任务状态来自既有本机读取/通知，缺失或失败时说明不可用，展开状态随同一回合保留。
