# Peer Agent 前端与客户端代码全景地图

> 生成时间：2026-07-18 16:39 UTC  
> 分析仓库：`/Users/liangyin/Documents/DEV/github/peer_agent`  
> 分析基线 HEAD：`35580b0fd58661e3a2bbd7c396827e23f6293bfd`  
> 分析性质：**只读静态分析**（不改动关联代码仓）  
> 统计口径：有效源码行 = 物理行（含空行/注释）；测试单独标注；已排除依赖、构建产物、工作树副本与锁文件。

---

## 统计口径与边界

### 层边界定义

| 层 | 路径 | 职责边界 |
|----|------|----------|
| **前端 Renderer** | `apps/desktop/renderer/**` | UI 表达、交互、本地展示态；禁止直接 `fs`/`child_process`/MCP 生命周期 |
| **客户端 Preload** | `apps/desktop/electron/preload/**` | `contextBridge` 暴露 `window.peerAgent`；IPC 白名单桥接 |
| **客户端 Main** | `apps/desktop/electron/main/**` | 本地发现/授权/执行、Runtime Projection、权限、Evidence、会话与 Agent 循环 |
| **桌面壳** | `apps/desktop/*`（非 electron/renderer） | Vite 入口、`index.html`、electron-builder、打包脚本 |
| **共享协议** | `packages/protocol` | 跨层契约类型与消息形状 |
| **共享运行时** | `packages/runtime-core` / `runtime-sdk` / `runtime-node` | Capability Provider、投影、工具宿主抽象 |
| **共享内核** | `packages/chat-kernel` / `task-thread` / `conversation-store` | 聊天内核、任务线程、会话持久化模型 |
| **共享 UI / i18n** | `packages/ui` / `i18n` | 可复用 UI 与文案 |
| **凭证助手** | `packages/credential-helper` | 本地密钥/凭证能力 |
| **能力清单** | `capabilities/*.json` | 本地能力 Manifest（声明，不是执行实现） |
| **TUI（本报告非重点）** | `apps/tui/**` | 终端 UI 应用，与桌面并行 |

### 入口点

| 入口 | 路径 | 说明 |
|------|------|------|
| Electron Main | `apps/desktop/electron/main/main.mjs` | `package.json#main`；创建窗口、注册 IPC、装配服务 |
| Preload | `apps/desktop/electron/preload/preload.cjs` | `contextBridge.exposeInMainWorld('peerAgent', …)` |
| Renderer HTML | `apps/desktop/index.html` | Vite 页面壳 |
| Renderer 应用 | `apps/desktop/renderer/src/App.tsx` 等 | React 应用根 |
| Runtime Projection IPC | `runtime-projection:get` → `buildRuntimeProjection()` | 模型可见工具投影入口 |
| Chat 发送 IPC | `chat:send` → `llmChatService.sendMessage(...)` | 对话主路径 |
| 权限 IPC | `permission:approve` / `permission:deny` | PermissionGrant 决议 |

### 排除规则（统计不计入）

- 目录：`node_modules`, `.git`, `dist`, `build`, `out`, `.vite`, `coverage`, `target`, `.turbo`
- 前缀：`.goal-worktree*`, `.tmp*`, `.qoder*`, `.worktree*`
- 文件：`pnpm-lock.yaml`, `Cargo.lock` 等锁文件
- 测试：`*.test.*` / `*.spec.*` / `__tests__` **单独计数**

---

## 仓库与包全景

### 焦点范围代码规模（前端 + 客户端 + 桌面共享栈）

| 指标 | 数值 |
|------|------|
| 代码文件数（焦点） | 579 |
| 总 LOC（含测试） | 129071 |
| 生产 LOC | 96979 |
| 测试 LOC | 32092 |
| 生产符号数（静态提取） | 2875 |
| IPC 通道数 | 146 |
| Preload `peerAgent` API 键数量 | ~176 |

### 分层 LOC（`.ts/.tsx/.js/.mjs/.cjs/.css/.rs`）

| Layer | Files | Prod files | Test files | Total LOC | Prod LOC | Test LOC |
|-------|------:|-----------:|-----------:|----------:|---------:|---------:|
| frontend-renderer | 259 | 201 | 58 | 52039 | 47205 | 4834 |
| client-main | 233 | 143 | 90 | 59663 | 36616 | 23047 |
| client-preload | 1 | 1 | 0 | 314 | 314 | 0 |
| desktop-shell | 3 | 3 | 0 | 181 | 181 | 0 |
| shared-ui | 1 | 1 | 0 | 84 | 84 | 0 |
| shared-protocol | 7 | 7 | 0 | 2356 | 2356 | 0 |
| shared-chat-kernel | 9 | 7 | 2 | 2203 | 1489 | 714 |
| shared-task-thread | 2 | 1 | 1 | 191 | 116 | 75 |
| shared-i18n | 1 | 1 | 0 | 1783 | 1783 | 0 |
| shared-conversation-store | 3 | 3 | 0 | 870 | 870 | 0 |
| shared-runtime | 58 | 36 | 22 | 8873 | 5654 | 3219 |
| shared-credential-helper | 2 | 1 | 1 | 514 | 311 | 203 |
| capabilities-manifest | 8 | 8 | 0 | 348 | 348 | 0 |

### 包依赖关系（workspace）

```text

@peer-agent/ui -> @peer-agent/i18n
@peer-agent/ui -> @peer-agent/protocol
@peer-agent/task-thread -> @peer-agent/i18n
@peer-agent/task-thread -> @peer-agent/protocol
@peer-agent/runtime-sdk -> @peer-agent/protocol
@peer-agent/runtime-sdk -> @peer-agent/runtime-core
@peer-agent/runtime-node -> @peer-agent/runtime-core
@peer-agent/runtime-node -> @peer-agent/runtime-sdk
@peer-agent/chat-kernel -> @peer-agent/protocol
@peer-agent/i18n -> @peer-agent/protocol
@peer-agent/desktop -> @peer-agent/chat-kernel
@peer-agent/desktop -> @peer-agent/conversation-store
@peer-agent/desktop -> @peer-agent/credential-helper
@peer-agent/desktop -> @peer-agent/i18n
@peer-agent/desktop -> @peer-agent/protocol
@peer-agent/desktop -> @peer-agent/runtime-core
@peer-agent/desktop -> @peer-agent/runtime-node
@peer-agent/desktop -> @peer-agent/runtime-sdk
@peer-agent/desktop -> @peer-agent/task-thread
@peer-agent/desktop -> @peer-agent/ui
```

**Desktop 直接依赖的一方包**：`protocol`, `runtime-core`, `runtime-sdk`, `runtime-node`, `chat-kernel`, `task-thread`, `conversation-store`, `credential-helper`, `i18n`, `ui`。

### 体积 Top 文件

| Path | LOC | Test |
|------|----:|:----:|
| `apps/desktop/renderer/src/chat/styles/chat-surface.css` | 2907 |  |
| `apps/desktop/electron/main/main.mjs` | 2780 |  |
| `apps/desktop/electron/main/goal-plan-store.mjs` | 2479 |  |
| `apps/desktop/electron/main/llm-chat-service.test.mjs` | 2249 | Y |
| `apps/desktop/renderer/src/chat/components/GoalPlanPanel.tsx` | 2051 |  |
| `apps/desktop/renderer/src/chat/components/ChatSurface.tsx` | 2035 |  |
| `apps/desktop/renderer/src/styles/llm-settings.css` | 1998 |  |
| `packages/i18n/src/index.ts` | 1783 |  |
| `apps/desktop/electron/main/goal-runner.mjs` | 1748 |  |
| `apps/desktop/renderer/src/chat/styles/goal-panel.css` | 1653 |  |
| `apps/desktop/renderer/src/styles/settings-page.css` | 1619 |  |
| `apps/desktop/electron/main/context-compactor.mjs` | 1594 |  |
| `apps/desktop/renderer/src/app/components/LlmSettingsPanel.tsx` | 1475 |  |
| `apps/desktop/electron/main/goal-plan-store.test.mjs` | 1441 | Y |
| `apps/desktop/electron/main/llm-config-store.mjs` | 1415 |  |
| `apps/desktop/electron/main/goal-runner.test.mjs` | 1189 | Y |
| `apps/desktop/renderer/src/styles/workbench.css` | 1182 |  |
| `apps/desktop/electron/main/llm-config-store.test.mjs` | 1176 | Y |
| `apps/desktop/electron/main/llm-chat-service.mjs` | 1097 |  |
| `apps/desktop/renderer/src/app/components/McpSettingsPanel.tsx` | 1060 |  |
| `apps/desktop/renderer/src/capabilities/capability-workbench.css` | 1051 |  |
| `apps/desktop/electron/main/context-compactor.test.mjs` | 973 | Y |
| `apps/desktop/renderer/src/styles/sidebar.css` | 882 |  |
| `apps/desktop/electron/main/provider-adapters/qoder-private-adapter.test.mjs` | 880 | Y |
| `packages/protocol/src/index.ts` | 826 |  |
| `apps/desktop/electron/main/conversation-store.test.mjs` | 817 | Y |
| `apps/desktop/electron/main/provider-adapter.test.mjs` | 813 | Y |
| `apps/desktop/electron/main/provider-adapters/qoder-private-adapter.mjs` | 806 |  |
| `apps/desktop/renderer/src/chat/components/Sidebar.tsx` | 795 |  |
| `apps/desktop/renderer/src/styles/tokens.css` | 791 |  |
| `packages/conversation-store/src/index.mjs` | 776 |  |
| `apps/desktop/renderer/src/App.tsx` | 728 |  |
| `apps/desktop/renderer/src/preload/contracts/bootstrapPreloadApi.ts` | 689 |  |
| `apps/desktop/electron/main/provider-encoder.test.mjs` | 668 | Y |
| `apps/desktop/electron/main/runtime-gateway/local-file-provider.mjs` | 656 |  |
| `apps/desktop/renderer/src/chat/hooks/useConversationStreamRouter.ts` | 653 |  |
| `packages/chat-kernel/src/thinking-reducer.ts` | 630 |  |
| `apps/desktop/renderer/src/styles/quick-chat.css` | 599 |  |
| `apps/desktop/electron/main/mcp-client.mjs` | 594 |  |
| `apps/desktop/renderer/src/workbench/views/BrowserView.tsx` | 580 |  |

### 关键观察

1. **客户端 Main** 与 **Renderer** 是两大主体：Main 生产 LOC ~36k、测试 ~23k；Renderer 生产 ~47k、测试 ~4.8k。
2. Main 测试密度显著高于 Renderer。
3. 共享运行时 `packages/runtime-*` 是桌面能力治理的共享底座。
4. Preload 仅 1 文件 / 314 LOC，但是 **IPC 边界的唯一浏览器侧出口**。

---

## 完整文件树与代码行数

> `[T]` = 测试文件。完整逐文件表见本节末。

### Renderer 目录树（摘要）

```text
renderer/  — 259 files, 52039 LOC
└── src/  — 259 files, 52039 LOC
    ├── App.tsx  — 728 LOC
    ├── clientApi.ts  — 186 LOC
    ├── global.d.ts  — 9 LOC
    ├── main.tsx  — 16 LOC
    ├── styles.css  — 28 LOC
    ├── app/  — 56 files, 8865 LOC
    │   ├── [T] gitBranchPrefix.test.ts  — 47 LOC
    │   ├── gitBranchPrefix.ts  — 32 LOC
    │   ├── [T] pageKeepAlive.test.ts  — 30 LOC
    │   ├── runtimeIdentity.ts  — 42 LOC
    │   ├── runtimeLabels.ts  — 13 LOC
    │   ├── components/  — 45 files, 8218 LOC
    │   │   ├── ArchivedConversationsPanel.tsx  — 178 LOC
    │   │   ├── BrandStartupLoader.tsx  — 127 LOC
    │   │   ├── BrandWordmark.tsx  — 41 LOC
    │   │   ├── CapabilitiesPanel.tsx  — 38 LOC
    │   │   ├── CapabilityInventory.tsx  — 37 LOC
    │   │   ├── CascadingMenu.tsx  — 461 LOC
    │   │   ├── ConfiguredModelRow.tsx  — 106 LOC
    │   │   ├── ConfirmProvider.tsx  — 111 LOC
    │   │   ├── Drawer.tsx  — 34 LOC
    │   │   ├── Dropdown.tsx  — 250 LOC
    │   │   ├── FallbackComposer.tsx  — 25 LOC
    │   │   ├── FallbackRuntimeView.tsx  — 34 LOC
    │   │   ├── GeneralPanel.tsx  — 136 LOC
    │   │   ├── GitPanel.tsx  — 85 LOC
    │   │   ├── LlmSettingsPanel.tsx  — 1475 LOC
    │   │   ├── McpSettingsPanel.tsx  — 1060 LOC
    │   │   ├── ModelCatalogDialog.tsx  — 314 LOC
    │   │   ├── ModelSettingsDialog.tsx  — 248 LOC
    │   │   ├── Overlay.tsx  — 111 LOC
    │   │   ├── QuickChatPopover.tsx  — 180 LOC
    │   │   ├── QuickChatTaskCard.tsx  — 97 LOC
    │   │   ├── QuickChatWindow.tsx  — 451 LOC
    │   │   ├── ReleaseNotesView.tsx  — 78 LOC
    │   │   ├── RuntimeFacts.tsx  — 51 LOC
    │   │   ├── SettingsPage.tsx  — 174 LOC
    │   │   └── ... +20 more files
    │   ├── hooks/  — 1 files, 105 LOC
    │   │   └── useMotionPresence.ts  — 105 LOC
    │   └── state/  — 5 files, 378 LOC
    │       ├── [T] quickChatSubmission.test.ts  — 37 LOC
    │       ├── quickChatSubmission.ts  — 20 LOC
    │       ├── useBrandStartupMinHold.ts  — 46 LOC
    │       ├── useDesktopBootstrap.ts  — 110 LOC
    │       └── useUpdater.ts  — 165 LOC
    ├── appearance/  — 9 files, 1565 LOC
    │   ├── AppearancePanel.tsx  — 269 LOC
    │   ├── AppearanceProvider.tsx  — 192 LOC
    │   ├── AppearanceSlider.tsx  — 54 LOC
    │   ├── PaletteSelect.tsx  — 187 LOC
    │   ├── appearance.css  — 431 LOC
    │   ├── appearanceTypes.ts  — 72 LOC
    │   ├── paletteRegistry.ts  — 137 LOC
    │   ├── themePresets.ts  — 99 LOC
    │   └── themeTokens.ts  — 124 LOC
    ├── capabilities/  — 12 files, 1827 LOC
    │   ├── capability-workbench.css  — 1051 LOC
    │   ├── capabilityCatalog.ts  — 97 LOC
    │   ├── types.ts  — 56 LOC
    │   └── components/  — 9 files, 623 LOC
    │       ├── CapabilityCard.tsx  — 33 LOC
    │       ├── CapabilityDetailPanel.tsx  — 87 LOC
    │       ├── CapabilityEmptyState.tsx  — 27 LOC
    │       ├── CapabilitySection.tsx  — 28 LOC
    │       ├── CapabilityTabs.tsx  — 33 LOC
    │       ├── CapabilityWorkbench.tsx  — 102 LOC
    │       ├── SkillUploadDialog.tsx  — 94 LOC
    │       ├── SkillsInstalledPanel.tsx  — 195 LOC
    │       └── SkillsPanel.tsx  — 24 LOC
    ├── chat/  — 130 files, 25034 LOC
    │   ├── components/  — 41 files, 10192 LOC
    │   │   ├── ChatSurface.tsx  — 2035 LOC
    │   │   ├── ComposerDraftControls.tsx  — 254 LOC
    │   │   ├── ComposerTokenUsageDisplay.tsx  — 36 LOC
    │   │   ├── ConversationSearchPalette.tsx  — 331 LOC
    │   │   ├── GoalPlanPanel.tsx  — 2051 LOC
    │   │   ├── MessageQueue.tsx  — 124 LOC
    │   │   ├── Sidebar.tsx  — 795 LOC
    │   │   ├── [T] composerDraftIsolation.test.ts  — 37 LOC
    │   │   ├── goal/  — 9 files, 681 LOC
    │   │   │   ├── ChatGoalApprovalCard.tsx  — 100 LOC
    │   │   │   ├── [T] goalPlanExpansion.test.ts  — 95 LOC
    │   │   │   ├── goalPlanExpansion.ts  — 32 LOC
    │   │   │   ├── [T] goalPlanNextActions.test.ts  — 47 LOC
    │   │   │   ├── goalPlanNextActions.ts  — 44 LOC
    │   │   │   ├── [T] goalPlanTree.test.ts  — 49 LOC
    │   │   │   ├── goalPlanTree.ts  — 51 LOC
    │   │   │   ├── useAwaitingGoalPlans.ts  — 181 LOC
    │   │   │   └── useGoalPlanApproval.ts  — 82 LOC
    │   │   ├── markdown/  — 6 files, 928 LOC
    │   │   │   ├── InlineMarkdown.tsx  — 250 LOC
    │   │   │   ├── MarkdownMessage.tsx  — 175 LOC
    │   │   │   ├── [T] markdownFenceSanitizer.test.ts  — 151 LOC
    │   │   │   ├── markdownFenceSanitizer.ts  — 131 LOC
    │   │   │   ├── markdownParser.ts  — 174 LOC
    │   │   │   └── markdownTypes.ts  — 47 LOC
    │   │   └── thread/  — 18 files, 2920 LOC
    │   │       ├── AssistantContent.tsx  — 485 LOC
    │   │       ├── AttachmentStrip.tsx  — 141 LOC
    │   │       ├── BatchSearchToolCard.tsx  — 138 LOC
    │   │       ├── ChatFindBar.tsx  — 223 LOC
    │   │       ├── ChatHeader.tsx  — 232 LOC
    │   │       ├── ChatHeaderCapabilities.tsx  — 370 LOC
    │   │       ├── ChatTurn.tsx  — 156 LOC
    │   │       ├── ImagePreviewBar.tsx  — 50 LOC
    │   │       ├── InteractionToolCard.tsx  — 86 LOC
    │   │       ├── MessageActionBar.tsx  — 104 LOC
    │   │       ├── MessageRail.tsx  — 78 LOC
    │   │       ├── MessageRichParts.tsx  — 70 LOC
    │   │       ├── PermissionGateStrip.tsx  — 79 LOC
    │   │       ├── ThinkingTimeline.tsx  — 204 LOC
    │   │       ├── [T] TokenUsageDisplay.test.ts  — 41 LOC
    │   │       ├── TokenUsageDisplay.tsx  — 399 LOC
    │   │       ├── effortSlider.ts  — 47 LOC
    │   │       └── interactionContext.ts  — 17 LOC
    │   ├── hooks/  — 13 files, 1396 LOC
    │   │   ├── useConversationMode.ts  — 29 LOC
    │   │   ├── useConversationModelEffort.ts  — 56 LOC
    │   │   ├── useConversationState.ts  — 138 LOC
    │   │   ├── useConversationStreamRouter.ts  — 653 LOC
    │   │   ├── useEffortPreference.ts  — 32 LOC
    │   │   ├── useElapsedTimer.ts  — 20 LOC
    │   │   ├── useExitAnimation.ts  — 29 LOC
    │   │   ├── useListFlip.ts  — 118 LOC
    │   │   ├── useLocalAccessPreference.ts  — 36 LOC
    │   │   ├── useMessageQueue.ts  — 4 LOC
    │   │   ├── useStreamingReport.ts  — 25 LOC
    │   │   ├── useTypewriterStream.ts  — 105 LOC
    │   │   └── useVirtualChatTurns.ts  — 151 LOC
    │   ├── state/  — 65 files, 6873 LOC
    │   │   ├── [T] apiMessageMapping.test.ts  — 178 LOC
    │   │   ├── apiMessageMapping.ts  — 204 LOC
    │   │   ├── [T] attachmentIntake.test.ts  — 42 LOC
    │   │   ├── attachmentIntake.ts  — 47 LOC
    │   │   ├── [T] automaticCompaction.test.ts  — 26 LOC
    │   │   ├── automaticCompaction.ts  — 19 LOC
    │   │   ├── [T] batchSearchLaneView.test.ts  — 131 LOC
    │   │   ├── batchSearchLaneView.ts  — 209 LOC
    │   │   ├── [T] browserToolReveal.test.ts  — 21 LOC
    │   │   ├── browserToolReveal.ts  — 11 LOC
    │   │   ├── [T] chatTurnRenderEquality.test.ts  — 72 LOC
    │   │   ├── chatTurnRenderEquality.ts  — 49 LOC
    │   │   ├── [T] chatTurns.test.ts  — 120 LOC
    │   │   ├── chatTurns.ts  — 112 LOC
    │   │   ├── [T] clientToolCallEvents.test.ts  — 103 LOC
    │   │   ├── clientToolCallEvents.ts  — 141 LOC
    │   │   ├── [T] clientToolEvidence.test.ts  — 86 LOC
    │   │   ├── clientToolEvidence.ts  — 72 LOC
    │   │   ├── [T] coalescedRefresh.test.ts  — 57 LOC
    │   │   ├── coalescedRefresh.ts  — 53 LOC
    │   │   ├── [T] compactionLifecycle.test.ts  — 95 LOC
    │   │   ├── compactionLifecycle.ts  — 52 LOC
    │   │   ├── [T] compactionLiveTailMerge.test.ts  — 79 LOC
    │   │   ├── compactionLiveTailMerge.ts  — 35 LOC
    │   │   ├── [T] compactionStateView.test.ts  — 45 LOC
    │   │   └── ... +40 more files
    │   ├── styles/  — 9 files, 6482 LOC
    │   │   ├── chat-composer.css  — 231 LOC
    │   │   ├── chat-surface.css  — 2907 LOC
    │   │   ├── goal-panel.css  — 1653 LOC
    │   │   ├── markdown.css  — 291 LOC
    │   │   ├── message.css  — 378 LOC
    │   │   ├── permission-gate-strip.css  — 140 LOC
    │   │   ├── sidebar.css  — 364 LOC
    │   │   ├── thread.css  — 169 LOC
    │   │   └── timeline.css  — 349 LOC
    │   └── utils/  — 2 files, 91 LOC
    │       ├── [T] records.test.ts  — 19 LOC
    │       └── records.ts  — 72 LOC
    ├── preload/  — 3 files, 693 LOC
    │   └── contracts/  — 3 files, 693 LOC
    │       ├── bootstrapPreloadApi.ts  — 689 LOC
    │       ├── chatPreloadApi.ts  — 1 LOC
    │       └── peerAgentPreloadApi.ts  — 3 LOC
    ├── settings/  — 1 files, 206 LOC
    │   └── UsageStatsPanel.tsx  — 206 LOC
    ├── styles/  — 20 files, 9335 LOC
    │   ├── base.css  — 91 LOC
    │   ├── card.css  — 14 LOC
    │   ├── composer.css  — 108 LOC
    │   ├── confirm-dialog.css  — 93 LOC
    │   ├── conversation-search.css  — 155 LOC
    │   ├── fallback.css  — 77 LOC
    │   ├── llm-settings.css  — 1998 LOC
    │   ├── motion.css  — 423 LOC
    │   ├── [T] motionPerformance.test.ts  — 16 LOC
    │   ├── overlay.css  — 81 LOC
    │   ├── quick-chat.css  — 599 LOC
    │   ├── [T] quickChatPopoverOutline.test.ts  — 30 LOC
    │   ├── settings-page.css  — 1619 LOC
    │   ├── shell.css  — 463 LOC
    │   ├── sidebar.css  — 882 LOC
    │   ├── [T] startupTransition.test.ts  — 164 LOC
    │   ├── tokens.css  — 791 LOC
    │   ├── tooltip.css  — 70 LOC
    │   ├── updater.css  — 479 LOC
    │   └── workbench.css  — 1182 LOC
    └── workbench/  — 23 files, 3547 LOC
        ├── ResourceTabStrip.tsx  — 100 LOC
        ├── SidebarResizer.tsx  — 148 LOC
        ├── SidebarToggle.tsx  — 47 LOC
        ├── WorkbenchContext.tsx  — 530 LOC
        ├── WorkbenchPanel.tsx  — 291 LOC
        ├── WorkbenchToggle.tsx  — 38 LOC
        ├── [T] browserSessionState.test.ts  — 67 LOC
        ├── browserSessionState.ts  — 135 LOC
        ├── [T] documentSessionState.test.ts  — 89 LOC
        ├── documentSessionState.ts  — 162 LOC
        ├── [T] workbenchBrowserVisibility.test.ts  — 23 LOC
        ├── [T] workbenchOpenState.test.ts  — 29 LOC
        ├── workbenchOpenState.ts  — 33 LOC
        ├── [T] workbenchTabState.test.ts  — 21 LOC
        ├── workbenchTabState.ts  — 27 LOC
        ├── file-preview/  — 5 files, 392 LOC
        │   ├── DiffViewer.tsx  — 102 LOC
        │   ├── MarkdownDocument.tsx  — 147 LOC
        │   ├── SourceViewer.tsx  — 30 LOC
        │   ├── [T] fileTypes.test.ts  — 31 LOC
        │   └── fileTypes.ts  — 82 LOC
        └── views/  — 3 files, 1415 LOC
            ├── BrowserView.tsx  — 580 LOC
            ├── DocumentView.tsx  — 533 LOC
            └── FilesView.tsx  — 302 LOC
```

### Electron Main 目录树（摘要）

```text
main/  — 233 files, 59663 LOC
├── [T] after-sign.test.mjs  — 108 LOC
├── app-menu.mjs  — 137 LOC
├── auto-updater.mjs  — 528 LOC
├── [T] auto-updater.test.mjs  — 61 LOC
├── capability-registry.mjs  — 47 LOC
├── compaction-diagnostic-log.mjs  — 63 LOC
├── [T] context-baseline-recorder.test.mjs  — 84 LOC
├── context-compactor.mjs  — 1594 LOC
├── [T] context-compactor.test.mjs  — 973 LOC
├── conversation-compaction-persistence.mjs  — 55 LOC
├── [T] conversation-compaction-persistence.test.mjs  — 225 LOC
├── conversation-store.mjs  — 1 LOC
├── [T] conversation-store.test.mjs  — 817 LOC
├── data-store.mjs  — 144 LOC
├── [T] data-store.test.mjs  — 145 LOC
├── [T] developer-settings-ipc.test.mjs  — 39 LOC
├── env-loader.mjs  — 31 LOC
├── goal-intake-convergence.mjs  — 43 LOC
├── [T] goal-intake-convergence.test.mjs  — 61 LOC
├── goal-message-router.mjs  — 176 LOC
├── ... +58 more files
├── chat-runtime/  — 31 files, 7274 LOC
│   ├── agent-loop-kernel.mjs  — 255 LOC
│   ├── [T] agent-loop-kernel.test.mjs  — 416 LOC
│   ├── anthropic-agent-loop.mjs  — 308 LOC
│   ├── compaction-coordinator.mjs  — 359 LOC
│   ├── [T] compaction-coordinator.test.mjs  — 579 LOC
│   ├── compaction-registry.mjs  — 77 LOC
│   ├── [T] compaction-registry.test.mjs  — 89 LOC
│   ├── gemini-agent-loop.mjs  — 270 LOC
│   ├── goal-mode-gate.mjs  — 426 LOC
│   ├── [T] goal-mode-gate.test.mjs  — 548 LOC
│   ├── [T] llm-chat-session.test.mjs  — 141 LOC
│   ├── message-sanitizer.mjs  — 141 LOC
│   ├── [T] message-sanitizer.test.mjs  — 212 LOC
│   ├── openai-agent-loop.mjs  — 292 LOC
│   ├── permission-gate.mjs  — 352 LOC
│   ├── [T] permission-gate.test.mjs  — 294 LOC
│   ├── projected-tool-executor.mjs  — 308 LOC
│   ├── [T] projected-tool-executor.test.mjs  — 224 LOC
│   ├── provider-recovery-broker.mjs  — 157 LOC
│   ├── [T] provider-recovery-broker.test.mjs  — 72 LOC
│   └── ... +11 more files
├── llm-oauth/  — 6 files, 1142 LOC
│   ├── google-oauth.mjs  — 263 LOC
│   ├── [T] google-oauth.test.mjs  — 79 LOC
│   ├── grok-oauth.mjs  — 256 LOC
│   ├── [T] grok-oauth.test.mjs  — 173 LOC
│   ├── openai-oauth.mjs  — 286 LOC
│   └── [T] openai-oauth.test.mjs  — 85 LOC
├── prompt/  — 28 files, 3222 LOC
│   ├── context-baseline-recorder.mjs  — 104 LOC
│   ├── index.mjs  — 17 LOC
│   ├── prompt-assembler.mjs  — 134 LOC
│   ├── prompt-snapshot-store.mjs  — 278 LOC
│   ├── prompt-source-registry.mjs  — 39 LOC
│   ├── rendering.mjs  — 7 LOC
│   └── sources/  — 22 files, 2643 LOC
│       ├── attachment-source.mjs  — 111 LOC
│       ├── brainstorming-source.mjs  — 91 LOC
│       ├── [T] brainstorming-source.test.mjs  — 65 LOC
│       ├── context-extension-source.mjs  — 93 LOC
│       ├── continuity-source.mjs  — 81 LOC
│       ├── core-source.mjs  — 65 LOC
│       ├── explorer-source.mjs  — 137 LOC
│       ├── [T] explorer-source.test.mjs  — 64 LOC
│       ├── goal-plan-source.mjs  — 140 LOC
│       ├── [T] goal-plan-source.test.mjs  — 93 LOC
│       ├── goal-runner-source.mjs  — 462 LOC
│       ├── [T] goal-runner-source.test.mjs  — 169 LOC
│       ├── mcp-host-source.mjs  — 122 LOC
│       ├── [T] mcp-host-source.test.mjs  — 90 LOC
│       ├── mode-copy.mjs  — 47 LOC
│       ├── mode-source.mjs  — 64 LOC
│       ├── project-instructions-source.mjs  — 289 LOC
│       ├── provider-source.mjs  — 66 LOC
│       ├── runtime-reminder-source.mjs  — 130 LOC
│       ├── runtime-source.mjs  — 35 LOC
│       └── ... +2 more files
├── provider-adapters/  — 27 files, 5793 LOC
│   ├── anthropic-cli-identity.mjs  — 19 LOC
│   ├── anthropic-messages-adapter.mjs  — 284 LOC
│   ├── gemini-adapter.mjs  — 217 LOC
│   ├── gemini-model-catalog.mjs  — 159 LOC
│   ├── [T] gemini-model-catalog.test.mjs  — 49 LOC
│   ├── grok-build-model-catalog.mjs  — 72 LOC
│   ├── [T] grok-build-model-catalog.test.mjs  — 50 LOC
│   ├── models-dev-registry.mjs  — 138 LOC
│   ├── [T] models-dev-registry.test.mjs  — 88 LOC
│   ├── openai-chat-adapter.mjs  — 545 LOC
│   ├── openai-model-catalog.mjs  — 327 LOC
│   ├── [T] openai-model-catalog.test.mjs  — 268 LOC
│   ├── openai-responses-adapter.mjs  — 287 LOC
│   ├── qoder-local-auth.mjs  — 461 LOC
│   ├── [T] qoder-local-auth.test.mjs  — 42 LOC
│   ├── qoder-model-catalog.mjs  — 249 LOC
│   ├── [T] qoder-model-catalog.test.mjs  — 158 LOC
│   ├── qoder-private-adapter.mjs  — 806 LOC
│   ├── [T] qoder-private-adapter.test.mjs  — 880 LOC
│   ├── qoder-provider-expansion.mjs  — 111 LOC
│   └── ... +7 more files
├── provider-diagnostics/  — 1 files, 273 LOC
│   └── provider-trace-recorder.mjs  — 273 LOC
├── provider-encoders/  — 6 files, 815 LOC
│   ├── gemini-encoder.mjs  — 121 LOC
│   ├── index.mjs  — 12 LOC
│   ├── message-normalizer.mjs  — 65 LOC
│   ├── request-encoder.mjs  — 331 LOC
│   ├── responses-encoder.mjs  — 152 LOC
│   └── [T] responses-encoder.test.mjs  — 134 LOC
├── provider-transports/  — 2 files, 310 LOC
│   ├── grok-fetch.mjs  — 10 LOC
│   └── recovering-fetch.mjs  — 300 LOC
├── runtime-gateway/  — 43 files, 8239 LOC
│   ├── browser-control-registry.mjs  — 122 LOC
│   ├── [T] browser-control-registry.test.mjs  — 98 LOC
│   ├── capability-provider-registry.mjs  — 123 LOC
│   ├── [T] capability-provider-registry.test.mjs  — 91 LOC
│   ├── event-protocol.mjs  — 137 LOC
│   ├── hook-config.mjs  — 6 LOC
│   ├── [T] hook-config.test.mjs  — 60 LOC
│   ├── hook-evidence.mjs  — 25 LOC
│   ├── hook-runner.mjs  — 5 LOC
│   ├── [T] hook-runner.test.mjs  — 62 LOC
│   ├── legacy-llm-local-tool-provider.mjs  — 280 LOC
│   ├── [T] legacy-llm-local-tool-provider.test.mjs  — 203 LOC
│   ├── local-browser-control-provider.mjs  — 429 LOC
│   ├── [T] local-browser-control-provider.test.mjs  — 105 LOC
│   ├── local-file-provider.mjs  — 656 LOC
│   ├── [T] local-file-provider.test.mjs  — 216 LOC
│   ├── local-goal-provider.mjs  — 495 LOC
│   ├── [T] local-goal-provider.test.mjs  — 378 LOC
│   ├── local-interaction-provider.mjs  — 114 LOC
│   ├── [T] local-interaction-provider.test.mjs  — 73 LOC
│   └── ... +23 more files
└── tools/  — 11 files, 1334 LOC
    ├── browser-tool-definitions.mjs  — 221 LOC
    ├── goal-tool-definitions.mjs  — 351 LOC
    ├── index.mjs  — 94 LOC
    ├── interaction-tool-definitions.mjs  — 57 LOC
    ├── legacy-local-tool-definitions.mjs  — 180 LOC
    ├── mcp-tool-definitions.mjs  — 28 LOC
    ├── provider-tool-materializer.mjs  — 44 LOC
    ├── runtime-projection-tool-materializer.mjs  — 162 LOC
    ├── search-tool-definitions.mjs  — 98 LOC
    ├── tool-registry.mjs  — 36 LOC
    └── web-tool-definitions.mjs  — 63 LOC
```

### Preload

preload/  — 1 files, 314 LOC
        314  preload.cjs

### packages 目录树（摘要）

```text
packages/  — 83 files, 16874 LOC
├── chat-kernel/  — 9 files, 2203 LOC
│   └── src/  — 9 files, 2203 LOC
│       ├── [T] chat-kernel.test.ts  — 505 LOC
│       ├── chat-reducer.ts  — 398 LOC
│       ├── confirmation-reducer.ts  — 53 LOC
│       ├── [T] historical-thinking-normalizer.test.ts  — 209 LOC
│       ├── historical-thinking-normalizer.ts  — 224 LOC
│       ├── index.ts  — 6 LOC
│       ├── message-actions.ts  — 27 LOC
│       ├── stream-parser.ts  — 151 LOC
│       └── thinking-reducer.ts  — 630 LOC
├── conversation-store/  — 3 files, 870 LOC
│   ├── scripts/  — 1 files, 12 LOC
│   │   └── build.mjs  — 12 LOC
│   └── src/  — 2 files, 858 LOC
│       ├── index.d.ts  — 82 LOC
│       └── index.mjs  — 776 LOC
├── credential-helper/  — 2 files, 514 LOC
│   └── src/  — 2 files, 514 LOC
│       ├── [T] index.test.ts  — 203 LOC
│       └── index.ts  — 311 LOC
├── i18n/  — 1 files, 1783 LOC
│   └── src/  — 1 files, 1783 LOC
│       └── index.ts  — 1783 LOC
├── protocol/  — 7 files, 2356 LOC
│   └── src/  — 7 files, 2356 LOC
│       ├── chat.ts  — 293 LOC
│       ├── execution.ts  — 308 LOC
│       ├── goal.ts  — 499 LOC
│       ├── index.ts  — 826 LOC
│       ├── memory.ts  — 117 LOC
│       ├── system-context.ts  — 223 LOC
│       └── updater.ts  — 90 LOC
├── runtime-core/  — 15 files, 1487 LOC
│   └── src/  — 15 files, 1487 LOC
│       ├── [T] capability-registry.test.ts  — 79 LOC
│       ├── capability-registry.ts  — 140 LOC
│       ├── contracts.ts  — 301 LOC
│       ├── [T] decision.test.ts  — 21 LOC
│       ├── decision.ts  — 33 LOC
│       ├── [T] evidence.test.ts  — 188 LOC
│       ├── evidence.ts  — 167 LOC
│       ├── [T] hooks.test.ts  — 14 LOC
│       ├── hooks.ts  — 12 LOC
│       ├── index.ts  — 8 LOC
│       ├── [T] permission.test.ts  — 84 LOC
│       ├── permission.ts  — 90 LOC
│       ├── projection-materializers.ts  — 64 LOC
│       ├── [T] projection.test.ts  — 149 LOC
│       └── projection.ts  — 137 LOC
├── runtime-node/  — 29 files, 4933 LOC
│   └── src/  — 29 files, 4933 LOC
│       ├── chatgpt-oauth.ts  — 30 LOC
│       ├── [T] chatgpt-responses-provider.test.ts  — 75 LOC
│       ├── chatgpt-responses-provider.ts  — 165 LOC
│       ├── contracts.ts  — 124 LOC
│       ├── [T] file-provider.test.ts  — 140 LOC
│       ├── file-provider.ts  — 301 LOC
│       ├── [T] host-adapter.test.ts  — 158 LOC
│       ├── host-adapter.ts  — 128 LOC
│       ├── index.ts  — 118 LOC
│       ├── [T] model-catalog.test.ts  — 51 LOC
│       ├── model-catalog.ts  — 58 LOC
│       ├── [T] model-provider-contracts.test.ts  — 62 LOC
│       ├── model-provider-contracts.ts  — 117 LOC
│       ├── node-hook-config.ts  — 81 LOC
│       ├── [T] node-hook-runner.test.ts  — 81 LOC
│       └── ... +14 more files
├── runtime-sdk/  — 14 files, 2453 LOC
│   └── src/  — 14 files, 2453 LOC
│       ├── contracts.ts  — 227 LOC
│       ├── goal-contracts.ts  — 92 LOC
│       ├── [T] goal-controller.test.ts  — 126 LOC
│       ├── goal-controller.ts  — 219 LOC
│       ├── index.ts  — 83 LOC
│       ├── pipeline-contracts.ts  — 170 LOC
│       ├── [T] pipeline.test.ts  — 385 LOC
│       ├── pipeline.ts  — 195 LOC
│       ├── [T] public-api.test.ts  — 61 LOC
│       ├── [T] runtime.test.ts  — 301 LOC
│       ├── runtime.ts  — 179 LOC
│       ├── session-contracts.ts  — 64 LOC
│       ├── [T] session-controller.test.ts  — 144 LOC
│       └── session-controller.ts  — 207 LOC
├── task-thread/  — 2 files, 191 LOC
│   └── src/  — 2 files, 191 LOC
│       ├── index.ts  — 116 LOC
│       └── [T] task-thread.test.ts  — 75 LOC
└── ui/  — 1 files, 84 LOC
    └── src/  — 1 files, 84 LOC
        └── index.tsx  — 84 LOC
```

### 能力 Manifest（`capabilities/`）

| Path | LOC |
|------|----:|
| `capabilities/local.shell.exec.json` | 55 |
| `capabilities/local.shell.stop.json` | 34 |
| `capabilities/local.web.control.click.json` | 46 |
| `capabilities/local.web.control.navigate.json` | 39 |
| `capabilities/local.web.control.readDom.json` | 43 |
| `capabilities/local.web.control.screenshot.json` | 33 |
| `capabilities/local.web.control.type.json` | 51 |
| `capabilities/local.web.fetch.json` | 47 |


### 逐文件行数记录（焦点代码，可核对）

格式：`| path | LOC | layer | test |`

| Path | LOC | Layer | Test |
|------|----:|-------|:----:|
| `apps/desktop/electron/main/after-sign.test.mjs` | 108 | client-main | Y |
| `apps/desktop/electron/main/app-menu.mjs` | 137 | client-main |  |
| `apps/desktop/electron/main/auto-updater.mjs` | 528 | client-main |  |
| `apps/desktop/electron/main/auto-updater.test.mjs` | 61 | client-main | Y |
| `apps/desktop/electron/main/capability-registry.mjs` | 47 | client-main |  |
| `apps/desktop/electron/main/chat-runtime/agent-loop-kernel.mjs` | 255 | client-main |  |
| `apps/desktop/electron/main/chat-runtime/agent-loop-kernel.test.mjs` | 416 | client-main | Y |
| `apps/desktop/electron/main/chat-runtime/anthropic-agent-loop.mjs` | 308 | client-main |  |
| `apps/desktop/electron/main/chat-runtime/compaction-coordinator.mjs` | 359 | client-main |  |
| `apps/desktop/electron/main/chat-runtime/compaction-coordinator.test.mjs` | 579 | client-main | Y |
| `apps/desktop/electron/main/chat-runtime/compaction-registry.mjs` | 77 | client-main |  |
| `apps/desktop/electron/main/chat-runtime/compaction-registry.test.mjs` | 89 | client-main | Y |
| `apps/desktop/electron/main/chat-runtime/gemini-agent-loop.mjs` | 270 | client-main |  |
| `apps/desktop/electron/main/chat-runtime/goal-mode-gate.mjs` | 426 | client-main |  |
| `apps/desktop/electron/main/chat-runtime/goal-mode-gate.test.mjs` | 548 | client-main | Y |
| `apps/desktop/electron/main/chat-runtime/llm-chat-session.test.mjs` | 141 | client-main | Y |
| `apps/desktop/electron/main/chat-runtime/message-sanitizer.mjs` | 141 | client-main |  |
| `apps/desktop/electron/main/chat-runtime/message-sanitizer.test.mjs` | 212 | client-main | Y |
| `apps/desktop/electron/main/chat-runtime/openai-agent-loop.mjs` | 292 | client-main |  |
| `apps/desktop/electron/main/chat-runtime/permission-gate.mjs` | 352 | client-main |  |
| `apps/desktop/electron/main/chat-runtime/permission-gate.test.mjs` | 294 | client-main | Y |
| `apps/desktop/electron/main/chat-runtime/projected-tool-executor.mjs` | 308 | client-main |  |
| `apps/desktop/electron/main/chat-runtime/projected-tool-executor.test.mjs` | 224 | client-main | Y |
| `apps/desktop/electron/main/chat-runtime/provider-recovery-broker.mjs` | 157 | client-main |  |
| `apps/desktop/electron/main/chat-runtime/provider-recovery-broker.test.mjs` | 72 | client-main | Y |
| `apps/desktop/electron/main/chat-runtime/qoder-agent-loop.mjs` | 212 | client-main |  |
| `apps/desktop/electron/main/chat-runtime/qoder-agent-loop.test.mjs` | 325 | client-main | Y |
| `apps/desktop/electron/main/chat-runtime/request-user-input-signal.test.mjs` | 70 | client-main | Y |
| `apps/desktop/electron/main/chat-runtime/response-guard.mjs` | 74 | client-main |  |
| `apps/desktop/electron/main/chat-runtime/response-guard.test.mjs` | 77 | client-main | Y |
| `apps/desktop/electron/main/chat-runtime/runtime-pipeline-adapter.mjs` | 66 | client-main |  |
| `apps/desktop/electron/main/chat-runtime/runtime-pipeline-adapter.test.mjs` | 103 | client-main | Y |
| `apps/desktop/electron/main/chat-runtime/runtime-session-adapter.mjs` | 79 | client-main |  |
| `apps/desktop/electron/main/chat-runtime/runtime-session-adapter.test.mjs` | 66 | client-main | Y |
| `apps/desktop/electron/main/chat-runtime/tool-orchestrator.mjs` | 361 | client-main |  |
| `apps/desktop/electron/main/chat-runtime/tool-orchestrator.test.mjs` | 321 | client-main | Y |
| `apps/desktop/electron/main/compaction-diagnostic-log.mjs` | 63 | client-main |  |
| `apps/desktop/electron/main/context-baseline-recorder.test.mjs` | 84 | client-main | Y |
| `apps/desktop/electron/main/context-compactor.mjs` | 1594 | client-main |  |
| `apps/desktop/electron/main/context-compactor.test.mjs` | 973 | client-main | Y |
| `apps/desktop/electron/main/conversation-compaction-persistence.mjs` | 55 | client-main |  |
| `apps/desktop/electron/main/conversation-compaction-persistence.test.mjs` | 225 | client-main | Y |
| `apps/desktop/electron/main/conversation-store.mjs` | 1 | client-main |  |
| `apps/desktop/electron/main/conversation-store.test.mjs` | 817 | client-main | Y |
| `apps/desktop/electron/main/data-store.mjs` | 144 | client-main |  |
| `apps/desktop/electron/main/data-store.test.mjs` | 145 | client-main | Y |
| `apps/desktop/electron/main/developer-settings-ipc.test.mjs` | 39 | client-main | Y |
| `apps/desktop/electron/main/env-loader.mjs` | 31 | client-main |  |
| `apps/desktop/electron/main/goal-intake-convergence.mjs` | 43 | client-main |  |
| `apps/desktop/electron/main/goal-intake-convergence.test.mjs` | 61 | client-main | Y |
| `apps/desktop/electron/main/goal-message-router.mjs` | 176 | client-main |  |
| `apps/desktop/electron/main/goal-message-router.test.mjs` | 104 | client-main | Y |
| `apps/desktop/electron/main/goal-plan-store.mjs` | 2479 | client-main |  |
| `apps/desktop/electron/main/goal-plan-store.test.mjs` | 1441 | client-main | Y |
| `apps/desktop/electron/main/goal-runner-antidrift.test.mjs` | 293 | client-main | Y |
| `apps/desktop/electron/main/goal-runner-message-persistence.mjs` | 57 | client-main |  |
| `apps/desktop/electron/main/goal-runner-message-persistence.test.mjs` | 91 | client-main | Y |
| `apps/desktop/electron/main/goal-runner.mjs` | 1748 | client-main |  |
| `apps/desktop/electron/main/goal-runner.test.mjs` | 1189 | client-main | Y |
| `apps/desktop/electron/main/host-restart.mjs` | 87 | client-main |  |
| `apps/desktop/electron/main/host-restart.test.mjs` | 75 | client-main | Y |
| `apps/desktop/electron/main/llm-chat-service.mjs` | 1097 | client-main |  |
| `apps/desktop/electron/main/llm-chat-service.test.mjs` | 2249 | client-main | Y |
| `apps/desktop/electron/main/llm-config-store.mjs` | 1415 | client-main |  |
| `apps/desktop/electron/main/llm-config-store.test.mjs` | 1176 | client-main | Y |
| `apps/desktop/electron/main/llm-oauth/google-oauth.mjs` | 263 | client-main |  |
| `apps/desktop/electron/main/llm-oauth/google-oauth.test.mjs` | 79 | client-main | Y |
| `apps/desktop/electron/main/llm-oauth/grok-oauth.mjs` | 256 | client-main |  |
| `apps/desktop/electron/main/llm-oauth/grok-oauth.test.mjs` | 173 | client-main | Y |
| `apps/desktop/electron/main/llm-oauth/openai-oauth.mjs` | 286 | client-main |  |
| `apps/desktop/electron/main/llm-oauth/openai-oauth.test.mjs` | 85 | client-main | Y |
| `apps/desktop/electron/main/llm-prompts.mjs` | 45 | client-main |  |
| `apps/desktop/electron/main/mac-update-url.mjs` | 23 | client-main |  |
| `apps/desktop/electron/main/main.mjs` | 2780 | client-main |  |
| `apps/desktop/electron/main/mcp-client.mjs` | 594 | client-main |  |
| `apps/desktop/electron/main/mcp-client.test.mjs` | 98 | client-main | Y |
| `apps/desktop/electron/main/mcp-credential-store.mjs` | 470 | client-main |  |
| `apps/desktop/electron/main/mcp-credential-store.test.mjs` | 190 | client-main | Y |
| `apps/desktop/electron/main/mcp-integration.test.mjs` | 373 | client-main | Y |
| `apps/desktop/electron/main/mcp-registry.mjs` | 403 | client-main |  |
| `apps/desktop/electron/main/model-credential-client.mjs` | 22 | client-main |  |
| `apps/desktop/electron/main/pending-task-store.mjs` | 147 | client-main |  |
| `apps/desktop/electron/main/pending-task-store.test.mjs` | 116 | client-main | Y |
| `apps/desktop/electron/main/project-index.mjs` | 147 | client-main |  |
| `apps/desktop/electron/main/prompt-assembler.test.mjs` | 509 | client-main | Y |
| `apps/desktop/electron/main/prompt-snapshot-store.test.mjs` | 148 | client-main | Y |
| `apps/desktop/electron/main/prompt/context-baseline-recorder.mjs` | 104 | client-main |  |
| `apps/desktop/electron/main/prompt/index.mjs` | 17 | client-main |  |
| `apps/desktop/electron/main/prompt/prompt-assembler.mjs` | 134 | client-main |  |
| `apps/desktop/electron/main/prompt/prompt-snapshot-store.mjs` | 278 | client-main |  |
| `apps/desktop/electron/main/prompt/prompt-source-registry.mjs` | 39 | client-main |  |
| `apps/desktop/electron/main/prompt/rendering.mjs` | 7 | client-main |  |
| `apps/desktop/electron/main/prompt/sources/attachment-source.mjs` | 111 | client-main |  |
| `apps/desktop/electron/main/prompt/sources/brainstorming-source.mjs` | 91 | client-main |  |
| `apps/desktop/electron/main/prompt/sources/brainstorming-source.test.mjs` | 65 | client-main | Y |
| `apps/desktop/electron/main/prompt/sources/context-extension-source.mjs` | 93 | client-main |  |
| `apps/desktop/electron/main/prompt/sources/continuity-source.mjs` | 81 | client-main |  |
| `apps/desktop/electron/main/prompt/sources/core-source.mjs` | 65 | client-main |  |
| `apps/desktop/electron/main/prompt/sources/explorer-source.mjs` | 137 | client-main |  |
| `apps/desktop/electron/main/prompt/sources/explorer-source.test.mjs` | 64 | client-main | Y |
| `apps/desktop/electron/main/prompt/sources/goal-plan-source.mjs` | 140 | client-main |  |
| `apps/desktop/electron/main/prompt/sources/goal-plan-source.test.mjs` | 93 | client-main | Y |
| `apps/desktop/electron/main/prompt/sources/goal-runner-source.mjs` | 462 | client-main |  |
| `apps/desktop/electron/main/prompt/sources/goal-runner-source.test.mjs` | 169 | client-main | Y |
| `apps/desktop/electron/main/prompt/sources/mcp-host-source.mjs` | 122 | client-main |  |
| `apps/desktop/electron/main/prompt/sources/mcp-host-source.test.mjs` | 90 | client-main | Y |
| `apps/desktop/electron/main/prompt/sources/mode-copy.mjs` | 47 | client-main |  |
| `apps/desktop/electron/main/prompt/sources/mode-source.mjs` | 64 | client-main |  |
| `apps/desktop/electron/main/prompt/sources/project-instructions-source.mjs` | 289 | client-main |  |
| `apps/desktop/electron/main/prompt/sources/provider-source.mjs` | 66 | client-main |  |
| `apps/desktop/electron/main/prompt/sources/runtime-reminder-source.mjs` | 130 | client-main |  |
| `apps/desktop/electron/main/prompt/sources/runtime-source.mjs` | 35 | client-main |  |
| `apps/desktop/electron/main/prompt/sources/verifier-source.mjs` | 168 | client-main |  |
| `apps/desktop/electron/main/prompt/sources/verifier-source.test.mjs` | 61 | client-main | Y |
| `apps/desktop/electron/main/provider-adapter.test.mjs` | 813 | client-main | Y |
| `apps/desktop/electron/main/provider-adapters/anthropic-cli-identity.mjs` | 19 | client-main |  |
| `apps/desktop/electron/main/provider-adapters/anthropic-messages-adapter.mjs` | 284 | client-main |  |
| `apps/desktop/electron/main/provider-adapters/gemini-adapter.mjs` | 217 | client-main |  |
| `apps/desktop/electron/main/provider-adapters/gemini-model-catalog.mjs` | 159 | client-main |  |
| `apps/desktop/electron/main/provider-adapters/gemini-model-catalog.test.mjs` | 49 | client-main | Y |
| `apps/desktop/electron/main/provider-adapters/grok-build-model-catalog.mjs` | 72 | client-main |  |
| `apps/desktop/electron/main/provider-adapters/grok-build-model-catalog.test.mjs` | 50 | client-main | Y |
| `apps/desktop/electron/main/provider-adapters/models-dev-registry.mjs` | 138 | client-main |  |
| `apps/desktop/electron/main/provider-adapters/models-dev-registry.test.mjs` | 88 | client-main | Y |
| `apps/desktop/electron/main/provider-adapters/openai-chat-adapter.mjs` | 545 | client-main |  |
| `apps/desktop/electron/main/provider-adapters/openai-model-catalog.mjs` | 327 | client-main |  |
| `apps/desktop/electron/main/provider-adapters/openai-model-catalog.test.mjs` | 268 | client-main | Y |
| `apps/desktop/electron/main/provider-adapters/openai-responses-adapter.mjs` | 287 | client-main |  |
| `apps/desktop/electron/main/provider-adapters/qoder-local-auth.mjs` | 461 | client-main |  |
| `apps/desktop/electron/main/provider-adapters/qoder-local-auth.test.mjs` | 42 | client-main | Y |
| `apps/desktop/electron/main/provider-adapters/qoder-model-catalog.mjs` | 249 | client-main |  |
| `apps/desktop/electron/main/provider-adapters/qoder-model-catalog.test.mjs` | 158 | client-main | Y |
| `apps/desktop/electron/main/provider-adapters/qoder-private-adapter.mjs` | 806 | client-main |  |
| `apps/desktop/electron/main/provider-adapters/qoder-private-adapter.test.mjs` | 880 | client-main | Y |
| `apps/desktop/electron/main/provider-adapters/qoder-provider-expansion.mjs` | 111 | client-main |  |
| `apps/desktop/electron/main/provider-adapters/qoder-provider-expansion.test.mjs` | 135 | client-main | Y |
| `apps/desktop/electron/main/provider-adapters/sse-line.mjs` | 42 | client-main |  |
| `apps/desktop/electron/main/provider-adapters/sse-line.test.mjs` | 36 | client-main | Y |
| `apps/desktop/electron/main/provider-adapters/subscription-provider-expansion.mjs` | 107 | client-main |  |
| `apps/desktop/electron/main/provider-adapters/subscription-provider-expansion.test.mjs` | 97 | client-main | Y |
| `apps/desktop/electron/main/provider-adapters/tool-arg-progress.mjs` | 72 | client-main |  |
| `apps/desktop/electron/main/provider-adapters/tool-arg-progress.test.mjs` | 94 | client-main | Y |
| `apps/desktop/electron/main/provider-channels.mjs` | 435 | client-main |  |
| `apps/desktop/electron/main/provider-channels.test.mjs` | 175 | client-main | Y |
| `apps/desktop/electron/main/provider-connectivity.mjs` | 38 | client-main |  |
| `apps/desktop/electron/main/provider-connectivity.test.mjs` | 42 | client-main | Y |
| `apps/desktop/electron/main/provider-credential-resolver.mjs` | 166 | client-main |  |
| `apps/desktop/electron/main/provider-credential-resolver.test.mjs` | 204 | client-main | Y |
| `apps/desktop/electron/main/provider-diagnostics/provider-trace-recorder.mjs` | 273 | client-main |  |
| `apps/desktop/electron/main/provider-encoder.test.mjs` | 668 | client-main | Y |
| `apps/desktop/electron/main/provider-encoders/gemini-encoder.mjs` | 121 | client-main |  |
| `apps/desktop/electron/main/provider-encoders/index.mjs` | 12 | client-main |  |
| `apps/desktop/electron/main/provider-encoders/message-normalizer.mjs` | 65 | client-main |  |
| `apps/desktop/electron/main/provider-encoders/request-encoder.mjs` | 331 | client-main |  |
| `apps/desktop/electron/main/provider-encoders/responses-encoder.mjs` | 152 | client-main |  |
| `apps/desktop/electron/main/provider-encoders/responses-encoder.test.mjs` | 134 | client-main | Y |
| `apps/desktop/electron/main/provider-recovery-broker.test.mjs` | 98 | client-main | Y |
| `apps/desktop/electron/main/provider-transports/grok-fetch.mjs` | 10 | client-main |  |
| `apps/desktop/electron/main/provider-transports/recovering-fetch.mjs` | 300 | client-main |  |
| `apps/desktop/electron/main/quick-chat-window.mjs` | 229 | client-main |  |
| `apps/desktop/electron/main/quick-chat-window.test.mjs` | 281 | client-main | Y |
| `apps/desktop/electron/main/recovering-fetch.test.mjs` | 249 | client-main | Y |
| `apps/desktop/electron/main/repetition-detector.mjs` | 129 | client-main |  |
| `apps/desktop/electron/main/repetition-detector.test.mjs` | 93 | client-main | Y |
| `apps/desktop/electron/main/runtime-gateway/browser-control-registry.mjs` | 122 | client-main |  |
| `apps/desktop/electron/main/runtime-gateway/browser-control-registry.test.mjs` | 98 | client-main | Y |
| `apps/desktop/electron/main/runtime-gateway/capability-provider-registry.mjs` | 123 | client-main |  |
| `apps/desktop/electron/main/runtime-gateway/capability-provider-registry.test.mjs` | 91 | client-main | Y |
| `apps/desktop/electron/main/runtime-gateway/event-protocol.mjs` | 137 | client-main |  |
| `apps/desktop/electron/main/runtime-gateway/hook-config.mjs` | 6 | client-main |  |
| `apps/desktop/electron/main/runtime-gateway/hook-config.test.mjs` | 60 | client-main | Y |
| `apps/desktop/electron/main/runtime-gateway/hook-evidence.mjs` | 25 | client-main |  |
| `apps/desktop/electron/main/runtime-gateway/hook-runner.mjs` | 5 | client-main |  |
| `apps/desktop/electron/main/runtime-gateway/hook-runner.test.mjs` | 62 | client-main | Y |
| `apps/desktop/electron/main/runtime-gateway/legacy-llm-local-tool-provider.mjs` | 280 | client-main |  |
| `apps/desktop/electron/main/runtime-gateway/legacy-llm-local-tool-provider.test.mjs` | 203 | client-main | Y |
| `apps/desktop/electron/main/runtime-gateway/local-browser-control-provider.mjs` | 429 | client-main |  |
| `apps/desktop/electron/main/runtime-gateway/local-browser-control-provider.test.mjs` | 105 | client-main | Y |
| `apps/desktop/electron/main/runtime-gateway/local-file-provider.mjs` | 656 | client-main |  |
| `apps/desktop/electron/main/runtime-gateway/local-file-provider.test.mjs` | 216 | client-main | Y |
| `apps/desktop/electron/main/runtime-gateway/local-goal-provider.mjs` | 495 | client-main |  |
| `apps/desktop/electron/main/runtime-gateway/local-goal-provider.test.mjs` | 378 | client-main | Y |
| `apps/desktop/electron/main/runtime-gateway/local-interaction-provider.mjs` | 114 | client-main |  |
| `apps/desktop/electron/main/runtime-gateway/local-interaction-provider.test.mjs` | 73 | client-main | Y |
| `apps/desktop/electron/main/runtime-gateway/local-mcp-provider.mjs` | 269 | client-main |  |
| `apps/desktop/electron/main/runtime-gateway/local-search-aggregate-provider.mjs` | 484 | client-main |  |
| `apps/desktop/electron/main/runtime-gateway/local-search-aggregate-provider.test.mjs` | 151 | client-main | Y |
| `apps/desktop/electron/main/runtime-gateway/local-shell-provider-hook.test.mjs` | 141 | client-main | Y |
| `apps/desktop/electron/main/runtime-gateway/local-shell-provider.mjs` | 535 | client-main |  |
| `apps/desktop/electron/main/runtime-gateway/local-skill-provider.mjs` | 302 | client-main |  |
| `apps/desktop/electron/main/runtime-gateway/local-skill-provider.test.mjs` | 293 | client-main | Y |
| `apps/desktop/electron/main/runtime-gateway/local-tool-host-hook.test.mjs` | 266 | client-main | Y |
| `apps/desktop/electron/main/runtime-gateway/local-tool-host.mjs` | 88 | client-main |  |
| `apps/desktop/electron/main/runtime-gateway/local-web-provider.mjs` | 231 | client-main |  |
| `apps/desktop/electron/main/runtime-gateway/permission-review.mjs` | 173 | client-main |  |
| `apps/desktop/electron/main/runtime-gateway/permission-review.test.mjs` | 95 | client-main | Y |
| `apps/desktop/electron/main/runtime-gateway/projection-guard.mjs` | 40 | client-main |  |
| `apps/desktop/electron/main/runtime-gateway/result-queue.mjs` | 82 | client-main |  |
| `apps/desktop/electron/main/runtime-gateway/shell-artifacts.mjs` | 76 | client-main |  |
| `apps/desktop/electron/main/runtime-gateway/shell-classifier.mjs` | 429 | client-main |  |
| `apps/desktop/electron/main/runtime-gateway/shell-env-snapshot.mjs` | 139 | client-main |  |
| `apps/desktop/electron/main/runtime-gateway/shell-permission-rules.mjs` | 144 | client-main |  |
| `apps/desktop/electron/main/runtime-gateway/shell-redaction.mjs` | 27 | client-main |  |
| `apps/desktop/electron/main/runtime-gateway/shell-task-manager.mjs` | 232 | client-main |  |
| `apps/desktop/electron/main/runtime-gateway/tool-result-factory.mjs` | 50 | client-main |  |
| `apps/desktop/electron/main/runtime-gateway/web-artifacts.mjs` | 82 | client-main |  |
| `apps/desktop/electron/main/runtime-gateway/web-fetch-engine.mjs` | 232 | client-main |  |
| `apps/desktop/electron/main/session-store.mjs` | 103 | client-main |  |
| `apps/desktop/electron/main/settings-store.mjs` | 48 | client-main |  |
| `apps/desktop/electron/main/settings-store.test.mjs` | 60 | client-main | Y |
| `apps/desktop/electron/main/shell-system.test.mjs` | 183 | client-main | Y |
| `apps/desktop/electron/main/shortcut-service.mjs` | 147 | client-main |  |
| `apps/desktop/electron/main/shortcut-service.test.mjs` | 101 | client-main | Y |
| `apps/desktop/electron/main/skill-store.mjs` | 466 | client-main |  |
| `apps/desktop/electron/main/skill-store.test.mjs` | 222 | client-main | Y |
| `apps/desktop/electron/main/subscription-quota.mjs` | 496 | client-main |  |
| `apps/desktop/electron/main/subscription-quota.test.mjs` | 92 | client-main | Y |
| `apps/desktop/electron/main/tool-registry.test.mjs` | 329 | client-main | Y |
| `apps/desktop/electron/main/tools/browser-tool-definitions.mjs` | 221 | client-main |  |
| `apps/desktop/electron/main/tools/goal-tool-definitions.mjs` | 351 | client-main |  |
| `apps/desktop/electron/main/tools/index.mjs` | 94 | client-main |  |
| `apps/desktop/electron/main/tools/interaction-tool-definitions.mjs` | 57 | client-main |  |
| `apps/desktop/electron/main/tools/legacy-local-tool-definitions.mjs` | 180 | client-main |  |
| `apps/desktop/electron/main/tools/mcp-tool-definitions.mjs` | 28 | client-main |  |
| `apps/desktop/electron/main/tools/provider-tool-materializer.mjs` | 44 | client-main |  |
| `apps/desktop/electron/main/tools/runtime-projection-tool-materializer.mjs` | 162 | client-main |  |
| `apps/desktop/electron/main/tools/search-tool-definitions.mjs` | 98 | client-main |  |
| `apps/desktop/electron/main/tools/tool-registry.mjs` | 36 | client-main |  |
| `apps/desktop/electron/main/tools/web-tool-definitions.mjs` | 63 | client-main |  |
| `apps/desktop/electron/main/usage-stats.mjs` | 286 | client-main |  |
| `apps/desktop/electron/main/usage-stats.test.mjs` | 151 | client-main | Y |
| `apps/desktop/electron/main/window-routing.mjs` | 17 | client-main |  |
| `apps/desktop/electron/main/window-routing.test.mjs` | 42 | client-main | Y |
| `apps/desktop/electron/preload/preload.cjs` | 314 | client-preload |  |
| `apps/desktop/renderer/src/App.tsx` | 728 | frontend-renderer |  |
| `apps/desktop/renderer/src/app/components/ArchivedConversationsPanel.tsx` | 178 | frontend-renderer |  |
| `apps/desktop/renderer/src/app/components/BrandStartupLoader.tsx` | 127 | frontend-renderer |  |
| `apps/desktop/renderer/src/app/components/BrandWordmark.tsx` | 41 | frontend-renderer |  |
| `apps/desktop/renderer/src/app/components/CapabilitiesPanel.tsx` | 38 | frontend-renderer |  |
| `apps/desktop/renderer/src/app/components/CapabilityInventory.tsx` | 37 | frontend-renderer |  |
| `apps/desktop/renderer/src/app/components/CascadingMenu.tsx` | 461 | frontend-renderer |  |
| `apps/desktop/renderer/src/app/components/ConfiguredModelRow.tsx` | 106 | frontend-renderer |  |
| `apps/desktop/renderer/src/app/components/ConfirmProvider.tsx` | 111 | frontend-renderer |  |
| `apps/desktop/renderer/src/app/components/Drawer.tsx` | 34 | frontend-renderer |  |
| `apps/desktop/renderer/src/app/components/Dropdown.tsx` | 250 | frontend-renderer |  |
| `apps/desktop/renderer/src/app/components/FallbackComposer.tsx` | 25 | frontend-renderer |  |
| `apps/desktop/renderer/src/app/components/FallbackRuntimeView.tsx` | 34 | frontend-renderer |  |
| `apps/desktop/renderer/src/app/components/GeneralPanel.tsx` | 136 | frontend-renderer |  |
| `apps/desktop/renderer/src/app/components/GitPanel.tsx` | 85 | frontend-renderer |  |
| `apps/desktop/renderer/src/app/components/LlmSettingsPanel.tsx` | 1475 | frontend-renderer |  |
| `apps/desktop/renderer/src/app/components/McpSettingsPanel.tsx` | 1060 | frontend-renderer |  |
| `apps/desktop/renderer/src/app/components/ModelCatalogDialog.tsx` | 314 | frontend-renderer |  |
| `apps/desktop/renderer/src/app/components/ModelSettingsDialog.tsx` | 248 | frontend-renderer |  |
| `apps/desktop/renderer/src/app/components/Overlay.tsx` | 111 | frontend-renderer |  |
| `apps/desktop/renderer/src/app/components/QuickChatPopover.tsx` | 180 | frontend-renderer |  |
| `apps/desktop/renderer/src/app/components/QuickChatTaskCard.tsx` | 97 | frontend-renderer |  |
| `apps/desktop/renderer/src/app/components/QuickChatWindow.tsx` | 451 | frontend-renderer |  |
| `apps/desktop/renderer/src/app/components/ReleaseNotesView.tsx` | 78 | frontend-renderer |  |
| `apps/desktop/renderer/src/app/components/RuntimeFacts.tsx` | 51 | frontend-renderer |  |
| `apps/desktop/renderer/src/app/components/SettingsPage.tsx` | 174 | frontend-renderer |  |
| `apps/desktop/renderer/src/app/components/ShortcutsPanel.tsx` | 257 | frontend-renderer |  |
| `apps/desktop/renderer/src/app/components/SystemInstructionsPanel.tsx` | 105 | frontend-renderer |  |
| `apps/desktop/renderer/src/app/components/Tooltip.tsx` | 160 | frontend-renderer |  |
| `apps/desktop/renderer/src/app/components/UpdateModal.tsx` | 169 | frontend-renderer |  |
| `apps/desktop/renderer/src/app/components/UpdateToast.tsx` | 94 | frontend-renderer |  |
| `apps/desktop/renderer/src/app/components/UpdatesPanel.tsx` | 115 | frontend-renderer |  |
| `apps/desktop/renderer/src/app/components/VersionBadge.tsx` | 171 | frontend-renderer |  |
| `apps/desktop/renderer/src/app/components/cascadingMenuNav.test.ts` | 47 | frontend-renderer | Y |
| `apps/desktop/renderer/src/app/components/cascadingMenuNav.ts` | 27 | frontend-renderer |  |
| `apps/desktop/renderer/src/app/components/llmModelConfiguration.test.ts` | 230 | frontend-renderer | Y |
| `apps/desktop/renderer/src/app/components/llmModelConfiguration.ts` | 275 | frontend-renderer |  |
| `apps/desktop/renderer/src/app/components/llmSubscriptionAuth.test.ts` | 40 | frontend-renderer | Y |
| `apps/desktop/renderer/src/app/components/llmSubscriptionAuth.ts` | 20 | frontend-renderer |  |
| `apps/desktop/renderer/src/app/components/llmSubscriptionQuota.test.ts` | 72 | frontend-renderer | Y |
| `apps/desktop/renderer/src/app/components/llmSubscriptionQuota.ts` | 64 | frontend-renderer |  |
| `apps/desktop/renderer/src/app/components/quickChatPopoverLayout.ts` | 75 | frontend-renderer |  |
| `apps/desktop/renderer/src/app/components/quickChatPopoverPosition.test.ts` | 63 | frontend-renderer | Y |
| `apps/desktop/renderer/src/app/components/releaseNotesHtml.test.ts` | 93 | frontend-renderer | Y |
| `apps/desktop/renderer/src/app/components/releaseNotesHtml.ts` | 208 | frontend-renderer |  |
| `apps/desktop/renderer/src/app/components/updaterInstallCopy.test.ts` | 31 | frontend-renderer | Y |
| `apps/desktop/renderer/src/app/gitBranchPrefix.test.ts` | 47 | frontend-renderer | Y |
| `apps/desktop/renderer/src/app/gitBranchPrefix.ts` | 32 | frontend-renderer |  |
| `apps/desktop/renderer/src/app/hooks/useMotionPresence.ts` | 105 | frontend-renderer |  |
| `apps/desktop/renderer/src/app/pageKeepAlive.test.ts` | 30 | frontend-renderer | Y |
| `apps/desktop/renderer/src/app/runtimeIdentity.ts` | 42 | frontend-renderer |  |
| `apps/desktop/renderer/src/app/runtimeLabels.ts` | 13 | frontend-renderer |  |
| `apps/desktop/renderer/src/app/state/quickChatSubmission.test.ts` | 37 | frontend-renderer | Y |
| `apps/desktop/renderer/src/app/state/quickChatSubmission.ts` | 20 | frontend-renderer |  |
| `apps/desktop/renderer/src/app/state/useBrandStartupMinHold.ts` | 46 | frontend-renderer |  |
| `apps/desktop/renderer/src/app/state/useDesktopBootstrap.ts` | 110 | frontend-renderer |  |
| `apps/desktop/renderer/src/app/state/useUpdater.ts` | 165 | frontend-renderer |  |
| `apps/desktop/renderer/src/appearance/AppearancePanel.tsx` | 269 | frontend-renderer |  |
| `apps/desktop/renderer/src/appearance/AppearanceProvider.tsx` | 192 | frontend-renderer |  |
| `apps/desktop/renderer/src/appearance/AppearanceSlider.tsx` | 54 | frontend-renderer |  |
| `apps/desktop/renderer/src/appearance/PaletteSelect.tsx` | 187 | frontend-renderer |  |
| `apps/desktop/renderer/src/appearance/appearance.css` | 431 | frontend-renderer |  |
| `apps/desktop/renderer/src/appearance/appearanceTypes.ts` | 72 | frontend-renderer |  |
| `apps/desktop/renderer/src/appearance/paletteRegistry.ts` | 137 | frontend-renderer |  |
| `apps/desktop/renderer/src/appearance/themePresets.ts` | 99 | frontend-renderer |  |
| `apps/desktop/renderer/src/appearance/themeTokens.ts` | 124 | frontend-renderer |  |
| `apps/desktop/renderer/src/capabilities/capability-workbench.css` | 1051 | frontend-renderer |  |
| `apps/desktop/renderer/src/capabilities/capabilityCatalog.ts` | 97 | frontend-renderer |  |
| `apps/desktop/renderer/src/capabilities/components/CapabilityCard.tsx` | 33 | frontend-renderer |  |
| `apps/desktop/renderer/src/capabilities/components/CapabilityDetailPanel.tsx` | 87 | frontend-renderer |  |
| `apps/desktop/renderer/src/capabilities/components/CapabilityEmptyState.tsx` | 27 | frontend-renderer |  |
| `apps/desktop/renderer/src/capabilities/components/CapabilitySection.tsx` | 28 | frontend-renderer |  |
| `apps/desktop/renderer/src/capabilities/components/CapabilityTabs.tsx` | 33 | frontend-renderer |  |
| `apps/desktop/renderer/src/capabilities/components/CapabilityWorkbench.tsx` | 102 | frontend-renderer |  |
| `apps/desktop/renderer/src/capabilities/components/SkillUploadDialog.tsx` | 94 | frontend-renderer |  |
| `apps/desktop/renderer/src/capabilities/components/SkillsInstalledPanel.tsx` | 195 | frontend-renderer |  |
| `apps/desktop/renderer/src/capabilities/components/SkillsPanel.tsx` | 24 | frontend-renderer |  |
| `apps/desktop/renderer/src/capabilities/types.ts` | 56 | frontend-renderer |  |
| `apps/desktop/renderer/src/chat/components/ChatSurface.tsx` | 2035 | frontend-renderer |  |
| `apps/desktop/renderer/src/chat/components/ComposerDraftControls.tsx` | 254 | frontend-renderer |  |
| `apps/desktop/renderer/src/chat/components/ComposerTokenUsageDisplay.tsx` | 36 | frontend-renderer |  |
| `apps/desktop/renderer/src/chat/components/ConversationSearchPalette.tsx` | 331 | frontend-renderer |  |
| `apps/desktop/renderer/src/chat/components/GoalPlanPanel.tsx` | 2051 | frontend-renderer |  |
| `apps/desktop/renderer/src/chat/components/MessageQueue.tsx` | 124 | frontend-renderer |  |
| `apps/desktop/renderer/src/chat/components/Sidebar.tsx` | 795 | frontend-renderer |  |
| `apps/desktop/renderer/src/chat/components/composerDraftIsolation.test.ts` | 37 | frontend-renderer | Y |
| `apps/desktop/renderer/src/chat/components/goal/ChatGoalApprovalCard.tsx` | 100 | frontend-renderer |  |
| `apps/desktop/renderer/src/chat/components/goal/goalPlanExpansion.test.ts` | 95 | frontend-renderer | Y |
| `apps/desktop/renderer/src/chat/components/goal/goalPlanExpansion.ts` | 32 | frontend-renderer |  |
| `apps/desktop/renderer/src/chat/components/goal/goalPlanNextActions.test.ts` | 47 | frontend-renderer | Y |
| `apps/desktop/renderer/src/chat/components/goal/goalPlanNextActions.ts` | 44 | frontend-renderer |  |
| `apps/desktop/renderer/src/chat/components/goal/goalPlanTree.test.ts` | 49 | frontend-renderer | Y |
| `apps/desktop/renderer/src/chat/components/goal/goalPlanTree.ts` | 51 | frontend-renderer |  |
| `apps/desktop/renderer/src/chat/components/goal/useAwaitingGoalPlans.ts` | 181 | frontend-renderer |  |
| `apps/desktop/renderer/src/chat/components/goal/useGoalPlanApproval.ts` | 82 | frontend-renderer |  |
| `apps/desktop/renderer/src/chat/components/markdown/InlineMarkdown.tsx` | 250 | frontend-renderer |  |
| `apps/desktop/renderer/src/chat/components/markdown/MarkdownMessage.tsx` | 175 | frontend-renderer |  |
| `apps/desktop/renderer/src/chat/components/markdown/markdownFenceSanitizer.test.ts` | 151 | frontend-renderer | Y |
| `apps/desktop/renderer/src/chat/components/markdown/markdownFenceSanitizer.ts` | 131 | frontend-renderer |  |
| `apps/desktop/renderer/src/chat/components/markdown/markdownParser.ts` | 174 | frontend-renderer |  |
| `apps/desktop/renderer/src/chat/components/markdown/markdownTypes.ts` | 47 | frontend-renderer |  |
| `apps/desktop/renderer/src/chat/components/thread/AssistantContent.tsx` | 485 | frontend-renderer |  |
| `apps/desktop/renderer/src/chat/components/thread/AttachmentStrip.tsx` | 141 | frontend-renderer |  |
| `apps/desktop/renderer/src/chat/components/thread/BatchSearchToolCard.tsx` | 138 | frontend-renderer |  |
| `apps/desktop/renderer/src/chat/components/thread/ChatFindBar.tsx` | 223 | frontend-renderer |  |
| `apps/desktop/renderer/src/chat/components/thread/ChatHeader.tsx` | 232 | frontend-renderer |  |
| `apps/desktop/renderer/src/chat/components/thread/ChatHeaderCapabilities.tsx` | 370 | frontend-renderer |  |
| `apps/desktop/renderer/src/chat/components/thread/ChatTurn.tsx` | 156 | frontend-renderer |  |
| `apps/desktop/renderer/src/chat/components/thread/ImagePreviewBar.tsx` | 50 | frontend-renderer |  |
| `apps/desktop/renderer/src/chat/components/thread/InteractionToolCard.tsx` | 86 | frontend-renderer |  |
| `apps/desktop/renderer/src/chat/components/thread/MessageActionBar.tsx` | 104 | frontend-renderer |  |
| `apps/desktop/renderer/src/chat/components/thread/MessageRail.tsx` | 78 | frontend-renderer |  |
| `apps/desktop/renderer/src/chat/components/thread/MessageRichParts.tsx` | 70 | frontend-renderer |  |
| `apps/desktop/renderer/src/chat/components/thread/PermissionGateStrip.tsx` | 79 | frontend-renderer |  |
| `apps/desktop/renderer/src/chat/components/thread/ThinkingTimeline.tsx` | 204 | frontend-renderer |  |
| `apps/desktop/renderer/src/chat/components/thread/TokenUsageDisplay.test.ts` | 41 | frontend-renderer | Y |
| `apps/desktop/renderer/src/chat/components/thread/TokenUsageDisplay.tsx` | 399 | frontend-renderer |  |
| `apps/desktop/renderer/src/chat/components/thread/effortSlider.ts` | 47 | frontend-renderer |  |
| `apps/desktop/renderer/src/chat/components/thread/interactionContext.ts` | 17 | frontend-renderer |  |
| `apps/desktop/renderer/src/chat/hooks/useConversationMode.ts` | 29 | frontend-renderer |  |
| `apps/desktop/renderer/src/chat/hooks/useConversationModelEffort.ts` | 56 | frontend-renderer |  |
| `apps/desktop/renderer/src/chat/hooks/useConversationState.ts` | 138 | frontend-renderer |  |
| `apps/desktop/renderer/src/chat/hooks/useConversationStreamRouter.ts` | 653 | frontend-renderer |  |
| `apps/desktop/renderer/src/chat/hooks/useEffortPreference.ts` | 32 | frontend-renderer |  |
| `apps/desktop/renderer/src/chat/hooks/useElapsedTimer.ts` | 20 | frontend-renderer |  |
| `apps/desktop/renderer/src/chat/hooks/useExitAnimation.ts` | 29 | frontend-renderer |  |
| `apps/desktop/renderer/src/chat/hooks/useListFlip.ts` | 118 | frontend-renderer |  |
| `apps/desktop/renderer/src/chat/hooks/useLocalAccessPreference.ts` | 36 | frontend-renderer |  |
| `apps/desktop/renderer/src/chat/hooks/useMessageQueue.ts` | 4 | frontend-renderer |  |
| `apps/desktop/renderer/src/chat/hooks/useStreamingReport.ts` | 25 | frontend-renderer |  |
| `apps/desktop/renderer/src/chat/hooks/useTypewriterStream.ts` | 105 | frontend-renderer |  |
| `apps/desktop/renderer/src/chat/hooks/useVirtualChatTurns.ts` | 151 | frontend-renderer |  |
| `apps/desktop/renderer/src/chat/state/apiMessageMapping.test.ts` | 178 | frontend-renderer | Y |
| `apps/desktop/renderer/src/chat/state/apiMessageMapping.ts` | 204 | frontend-renderer |  |
| `apps/desktop/renderer/src/chat/state/attachmentIntake.test.ts` | 42 | frontend-renderer | Y |
| `apps/desktop/renderer/src/chat/state/attachmentIntake.ts` | 47 | frontend-renderer |  |
| `apps/desktop/renderer/src/chat/state/automaticCompaction.test.ts` | 26 | frontend-renderer | Y |
| `apps/desktop/renderer/src/chat/state/automaticCompaction.ts` | 19 | frontend-renderer |  |
| `apps/desktop/renderer/src/chat/state/batchSearchLaneView.test.ts` | 131 | frontend-renderer | Y |
| `apps/desktop/renderer/src/chat/state/batchSearchLaneView.ts` | 209 | frontend-renderer |  |
| `apps/desktop/renderer/src/chat/state/browserToolReveal.test.ts` | 21 | frontend-renderer | Y |
| `apps/desktop/renderer/src/chat/state/browserToolReveal.ts` | 11 | frontend-renderer |  |
| `apps/desktop/renderer/src/chat/state/chatTurnRenderEquality.test.ts` | 72 | frontend-renderer | Y |
| `apps/desktop/renderer/src/chat/state/chatTurnRenderEquality.ts` | 49 | frontend-renderer |  |
| `apps/desktop/renderer/src/chat/state/chatTurns.test.ts` | 120 | frontend-renderer | Y |
| `apps/desktop/renderer/src/chat/state/chatTurns.ts` | 112 | frontend-renderer |  |
| `apps/desktop/renderer/src/chat/state/clientToolCallEvents.test.ts` | 103 | frontend-renderer | Y |
| `apps/desktop/renderer/src/chat/state/clientToolCallEvents.ts` | 141 | frontend-renderer |  |
| `apps/desktop/renderer/src/chat/state/clientToolEvidence.test.ts` | 86 | frontend-renderer | Y |
| `apps/desktop/renderer/src/chat/state/clientToolEvidence.ts` | 72 | frontend-renderer |  |
| `apps/desktop/renderer/src/chat/state/coalescedRefresh.test.ts` | 57 | frontend-renderer | Y |
| `apps/desktop/renderer/src/chat/state/coalescedRefresh.ts` | 53 | frontend-renderer |  |
| `apps/desktop/renderer/src/chat/state/compactionLifecycle.test.ts` | 95 | frontend-renderer | Y |
| `apps/desktop/renderer/src/chat/state/compactionLifecycle.ts` | 52 | frontend-renderer |  |
| `apps/desktop/renderer/src/chat/state/compactionLiveTailMerge.test.ts` | 79 | frontend-renderer | Y |
| `apps/desktop/renderer/src/chat/state/compactionLiveTailMerge.ts` | 35 | frontend-renderer |  |
| `apps/desktop/renderer/src/chat/state/compactionStateView.test.ts` | 45 | frontend-renderer | Y |
| `apps/desktop/renderer/src/chat/state/compactionStateView.ts` | 38 | frontend-renderer |  |
| `apps/desktop/renderer/src/chat/state/composerPersistence.test.ts` | 109 | frontend-renderer | Y |
| `apps/desktop/renderer/src/chat/state/composerPersistence.ts` | 181 | frontend-renderer |  |
| `apps/desktop/renderer/src/chat/state/contextSources.test.ts` | 132 | frontend-renderer | Y |
| `apps/desktop/renderer/src/chat/state/contextSources.ts` | 142 | frontend-renderer |  |
| `apps/desktop/renderer/src/chat/state/conversationLoad.ts` | 130 | frontend-renderer |  |
| `apps/desktop/renderer/src/chat/state/conversationStore.test.ts` | 396 | frontend-renderer | Y |
| `apps/desktop/renderer/src/chat/state/conversationStore.ts` | 352 | frontend-renderer |  |
| `apps/desktop/renderer/src/chat/state/format.test.ts` | 74 | frontend-renderer | Y |
| `apps/desktop/renderer/src/chat/state/format.ts` | 42 | frontend-renderer |  |
| `apps/desktop/renderer/src/chat/state/frameCoalescer.test.ts` | 43 | frontend-renderer | Y |
| `apps/desktop/renderer/src/chat/state/frameCoalescer.ts` | 31 | frontend-renderer |  |
| `apps/desktop/renderer/src/chat/state/historicalLocalRecord.test.ts` | 151 | frontend-renderer | Y |
| `apps/desktop/renderer/src/chat/state/historicalLocalRecord.ts` | 79 | frontend-renderer |  |
| `apps/desktop/renderer/src/chat/state/interactionToolView.test.ts` | 96 | frontend-renderer | Y |
| `apps/desktop/renderer/src/chat/state/interactionToolView.ts` | 73 | frontend-renderer |  |
| `apps/desktop/renderer/src/chat/state/messageRailItems.test.ts` | 73 | frontend-renderer | Y |
| `apps/desktop/renderer/src/chat/state/messageRailItems.ts` | 57 | frontend-renderer |  |
| `apps/desktop/renderer/src/chat/state/permissionGateView.test.ts` | 79 | frontend-renderer | Y |
| `apps/desktop/renderer/src/chat/state/permissionGateView.ts` | 137 | frontend-renderer |  |
| `apps/desktop/renderer/src/chat/state/postTurnCompactionPolicy.test.ts` | 31 | frontend-renderer | Y |
| `apps/desktop/renderer/src/chat/state/preferences.test.ts` | 167 | frontend-renderer | Y |
| `apps/desktop/renderer/src/chat/state/preferences.ts` | 224 | frontend-renderer |  |
| `apps/desktop/renderer/src/chat/state/processingWindow.test.ts` | 85 | frontend-renderer | Y |
| `apps/desktop/renderer/src/chat/state/processingWindow.ts` | 121 | frontend-renderer |  |
| `apps/desktop/renderer/src/chat/state/providerDisplay.test.ts` | 50 | frontend-renderer | Y |
| `apps/desktop/renderer/src/chat/state/providerDisplay.ts` | 26 | frontend-renderer |  |
| `apps/desktop/renderer/src/chat/state/quickChatAttachments.test.ts` | 25 | frontend-renderer | Y |
| `apps/desktop/renderer/src/chat/state/quickChatAttachments.ts` | 14 | frontend-renderer |  |
| `apps/desktop/renderer/src/chat/state/quickChatTasks.test.ts` | 67 | frontend-renderer | Y |
| `apps/desktop/renderer/src/chat/state/quickChatTasks.ts` | 109 | frontend-renderer |  |
| `apps/desktop/renderer/src/chat/state/quickChatWorkspaceIdentity.test.ts` | 17 | frontend-renderer | Y |
| `apps/desktop/renderer/src/chat/state/quickChatWorkspaceIdentity.ts` | 17 | frontend-renderer |  |
| `apps/desktop/renderer/src/chat/state/streamSegments.test.ts` | 349 | frontend-renderer | Y |
| `apps/desktop/renderer/src/chat/state/streamSegments.ts` | 402 | frontend-renderer |  |
| `apps/desktop/renderer/src/chat/state/tokenEstimate.test.ts` | 154 | frontend-renderer | Y |
| `apps/desktop/renderer/src/chat/state/tokenEstimate.ts` | 143 | frontend-renderer |  |
| `apps/desktop/renderer/src/chat/state/types.ts` | 191 | frontend-renderer |  |
| `apps/desktop/renderer/src/chat/state/virtualTurns.test.ts` | 82 | frontend-renderer | Y |
| `apps/desktop/renderer/src/chat/state/virtualTurns.ts` | 125 | frontend-renderer |  |
| `apps/desktop/renderer/src/chat/styles/chat-composer.css` | 231 | frontend-renderer |  |
| `apps/desktop/renderer/src/chat/styles/chat-surface.css` | 2907 | frontend-renderer |  |
| `apps/desktop/renderer/src/chat/styles/goal-panel.css` | 1653 | frontend-renderer |  |
| `apps/desktop/renderer/src/chat/styles/markdown.css` | 291 | frontend-renderer |  |
| `apps/desktop/renderer/src/chat/styles/message.css` | 378 | frontend-renderer |  |
| `apps/desktop/renderer/src/chat/styles/permission-gate-strip.css` | 140 | frontend-renderer |  |
| `apps/desktop/renderer/src/chat/styles/sidebar.css` | 364 | frontend-renderer |  |
| `apps/desktop/renderer/src/chat/styles/thread.css` | 169 | frontend-renderer |  |
| `apps/desktop/renderer/src/chat/styles/timeline.css` | 349 | frontend-renderer |  |
| `apps/desktop/renderer/src/chat/utils/records.test.ts` | 19 | frontend-renderer | Y |
| `apps/desktop/renderer/src/chat/utils/records.ts` | 72 | frontend-renderer |  |
| `apps/desktop/renderer/src/clientApi.ts` | 186 | frontend-renderer |  |
| `apps/desktop/renderer/src/global.d.ts` | 9 | frontend-renderer |  |
| `apps/desktop/renderer/src/main.tsx` | 16 | frontend-renderer |  |
| `apps/desktop/renderer/src/preload/contracts/bootstrapPreloadApi.ts` | 689 | frontend-renderer |  |
| `apps/desktop/renderer/src/preload/contracts/chatPreloadApi.ts` | 1 | frontend-renderer |  |
| `apps/desktop/renderer/src/preload/contracts/peerAgentPreloadApi.ts` | 3 | frontend-renderer |  |
| `apps/desktop/renderer/src/settings/UsageStatsPanel.tsx` | 206 | frontend-renderer |  |
| `apps/desktop/renderer/src/styles.css` | 28 | frontend-renderer |  |
| `apps/desktop/renderer/src/styles/base.css` | 91 | frontend-renderer |  |
| `apps/desktop/renderer/src/styles/card.css` | 14 | frontend-renderer |  |
| `apps/desktop/renderer/src/styles/composer.css` | 108 | frontend-renderer |  |
| `apps/desktop/renderer/src/styles/confirm-dialog.css` | 93 | frontend-renderer |  |
| `apps/desktop/renderer/src/styles/conversation-search.css` | 155 | frontend-renderer |  |
| `apps/desktop/renderer/src/styles/fallback.css` | 77 | frontend-renderer |  |
| `apps/desktop/renderer/src/styles/llm-settings.css` | 1998 | frontend-renderer |  |
| `apps/desktop/renderer/src/styles/motion.css` | 423 | frontend-renderer |  |
| `apps/desktop/renderer/src/styles/motionPerformance.test.ts` | 16 | frontend-renderer | Y |
| `apps/desktop/renderer/src/styles/overlay.css` | 81 | frontend-renderer |  |
| `apps/desktop/renderer/src/styles/quick-chat.css` | 599 | frontend-renderer |  |
| `apps/desktop/renderer/src/styles/quickChatPopoverOutline.test.ts` | 30 | frontend-renderer | Y |
| `apps/desktop/renderer/src/styles/settings-page.css` | 1619 | frontend-renderer |  |
| `apps/desktop/renderer/src/styles/shell.css` | 463 | frontend-renderer |  |
| `apps/desktop/renderer/src/styles/sidebar.css` | 882 | frontend-renderer |  |
| `apps/desktop/renderer/src/styles/startupTransition.test.ts` | 164 | frontend-renderer | Y |
| `apps/desktop/renderer/src/styles/tokens.css` | 791 | frontend-renderer |  |
| `apps/desktop/renderer/src/styles/tooltip.css` | 70 | frontend-renderer |  |
| `apps/desktop/renderer/src/styles/updater.css` | 479 | frontend-renderer |  |
| `apps/desktop/renderer/src/styles/workbench.css` | 1182 | frontend-renderer |  |
| `apps/desktop/renderer/src/workbench/ResourceTabStrip.tsx` | 100 | frontend-renderer |  |
| `apps/desktop/renderer/src/workbench/SidebarResizer.tsx` | 148 | frontend-renderer |  |
| `apps/desktop/renderer/src/workbench/SidebarToggle.tsx` | 47 | frontend-renderer |  |
| `apps/desktop/renderer/src/workbench/WorkbenchContext.tsx` | 530 | frontend-renderer |  |
| `apps/desktop/renderer/src/workbench/WorkbenchPanel.tsx` | 291 | frontend-renderer |  |
| `apps/desktop/renderer/src/workbench/WorkbenchToggle.tsx` | 38 | frontend-renderer |  |
| `apps/desktop/renderer/src/workbench/browserSessionState.test.ts` | 67 | frontend-renderer | Y |
| `apps/desktop/renderer/src/workbench/browserSessionState.ts` | 135 | frontend-renderer |  |
| `apps/desktop/renderer/src/workbench/documentSessionState.test.ts` | 89 | frontend-renderer | Y |
| `apps/desktop/renderer/src/workbench/documentSessionState.ts` | 162 | frontend-renderer |  |
| `apps/desktop/renderer/src/workbench/file-preview/DiffViewer.tsx` | 102 | frontend-renderer |  |
| `apps/desktop/renderer/src/workbench/file-preview/MarkdownDocument.tsx` | 147 | frontend-renderer |  |
| `apps/desktop/renderer/src/workbench/file-preview/SourceViewer.tsx` | 30 | frontend-renderer |  |
| `apps/desktop/renderer/src/workbench/file-preview/fileTypes.test.ts` | 31 | frontend-renderer | Y |
| `apps/desktop/renderer/src/workbench/file-preview/fileTypes.ts` | 82 | frontend-renderer |  |
| `apps/desktop/renderer/src/workbench/views/BrowserView.tsx` | 580 | frontend-renderer |  |
| `apps/desktop/renderer/src/workbench/views/DocumentView.tsx` | 533 | frontend-renderer |  |
| `apps/desktop/renderer/src/workbench/views/FilesView.tsx` | 302 | frontend-renderer |  |
| `apps/desktop/renderer/src/workbench/workbenchBrowserVisibility.test.ts` | 23 | frontend-renderer | Y |
| `apps/desktop/renderer/src/workbench/workbenchOpenState.test.ts` | 29 | frontend-renderer | Y |
| `apps/desktop/renderer/src/workbench/workbenchOpenState.ts` | 33 | frontend-renderer |  |
| `apps/desktop/renderer/src/workbench/workbenchTabState.test.ts` | 21 | frontend-renderer | Y |
| `apps/desktop/renderer/src/workbench/workbenchTabState.ts` | 27 | frontend-renderer |  |
| `apps/desktop/scripts/after-sign.cjs` | 78 | desktop-shell |  |
| `apps/desktop/scripts/verify-packaged-runtime.cjs` | 82 | desktop-shell |  |
| `apps/desktop/vite.config.ts` | 21 | desktop-shell |  |
| `packages/chat-kernel/src/chat-kernel.test.ts` | 505 | shared-chat-kernel | Y |
| `packages/chat-kernel/src/chat-reducer.ts` | 398 | shared-chat-kernel |  |
| `packages/chat-kernel/src/confirmation-reducer.ts` | 53 | shared-chat-kernel |  |
| `packages/chat-kernel/src/historical-thinking-normalizer.test.ts` | 209 | shared-chat-kernel | Y |
| `packages/chat-kernel/src/historical-thinking-normalizer.ts` | 224 | shared-chat-kernel |  |
| `packages/chat-kernel/src/index.ts` | 6 | shared-chat-kernel |  |
| `packages/chat-kernel/src/message-actions.ts` | 27 | shared-chat-kernel |  |
| `packages/chat-kernel/src/stream-parser.ts` | 151 | shared-chat-kernel |  |
| `packages/chat-kernel/src/thinking-reducer.ts` | 630 | shared-chat-kernel |  |
| `packages/conversation-store/scripts/build.mjs` | 12 | shared-conversation-store |  |
| `packages/conversation-store/src/index.d.ts` | 82 | shared-conversation-store |  |
| `packages/conversation-store/src/index.mjs` | 776 | shared-conversation-store |  |
| `packages/credential-helper/src/index.test.ts` | 203 | shared-credential-helper | Y |
| `packages/credential-helper/src/index.ts` | 311 | shared-credential-helper |  |
| `packages/i18n/src/index.ts` | 1783 | shared-i18n |  |
| `packages/protocol/src/chat.ts` | 293 | shared-protocol |  |
| `packages/protocol/src/execution.ts` | 308 | shared-protocol |  |
| `packages/protocol/src/goal.ts` | 499 | shared-protocol |  |
| `packages/protocol/src/index.ts` | 826 | shared-protocol |  |
| `packages/protocol/src/memory.ts` | 117 | shared-protocol |  |
| `packages/protocol/src/system-context.ts` | 223 | shared-protocol |  |
| `packages/protocol/src/updater.ts` | 90 | shared-protocol |  |
| `packages/runtime-core/src/capability-registry.test.ts` | 79 | shared-runtime | Y |
| `packages/runtime-core/src/capability-registry.ts` | 140 | shared-runtime |  |
| `packages/runtime-core/src/contracts.ts` | 301 | shared-runtime |  |
| `packages/runtime-core/src/decision.test.ts` | 21 | shared-runtime | Y |
| `packages/runtime-core/src/decision.ts` | 33 | shared-runtime |  |
| `packages/runtime-core/src/evidence.test.ts` | 188 | shared-runtime | Y |
| `packages/runtime-core/src/evidence.ts` | 167 | shared-runtime |  |
| `packages/runtime-core/src/hooks.test.ts` | 14 | shared-runtime | Y |
| `packages/runtime-core/src/hooks.ts` | 12 | shared-runtime |  |
| `packages/runtime-core/src/index.ts` | 8 | shared-runtime |  |
| `packages/runtime-core/src/permission.test.ts` | 84 | shared-runtime | Y |
| `packages/runtime-core/src/permission.ts` | 90 | shared-runtime |  |
| `packages/runtime-core/src/projection-materializers.ts` | 64 | shared-runtime |  |
| `packages/runtime-core/src/projection.test.ts` | 149 | shared-runtime | Y |
| `packages/runtime-core/src/projection.ts` | 137 | shared-runtime |  |
| `packages/runtime-node/src/chatgpt-oauth.ts` | 30 | shared-runtime |  |
| `packages/runtime-node/src/chatgpt-responses-provider.test.ts` | 75 | shared-runtime | Y |
| `packages/runtime-node/src/chatgpt-responses-provider.ts` | 165 | shared-runtime |  |
| `packages/runtime-node/src/contracts.ts` | 124 | shared-runtime |  |
| `packages/runtime-node/src/file-provider.test.ts` | 140 | shared-runtime | Y |
| `packages/runtime-node/src/file-provider.ts` | 301 | shared-runtime |  |
| `packages/runtime-node/src/host-adapter.test.ts` | 158 | shared-runtime | Y |
| `packages/runtime-node/src/host-adapter.ts` | 128 | shared-runtime |  |
| `packages/runtime-node/src/index.ts` | 118 | shared-runtime |  |
| `packages/runtime-node/src/model-catalog.test.ts` | 51 | shared-runtime | Y |
| `packages/runtime-node/src/model-catalog.ts` | 58 | shared-runtime |  |
| `packages/runtime-node/src/model-provider-contracts.test.ts` | 62 | shared-runtime | Y |
| `packages/runtime-node/src/model-provider-contracts.ts` | 117 | shared-runtime |  |
| `packages/runtime-node/src/node-hook-config.ts` | 81 | shared-runtime |  |
| `packages/runtime-node/src/node-hook-runner.test.ts` | 81 | shared-runtime | Y |
| `packages/runtime-node/src/node-hook-runner.ts` | 191 | shared-runtime |  |
| `packages/runtime-node/src/openai-chat-stream.test.ts` | 138 | shared-runtime | Y |
| `packages/runtime-node/src/openai-chat-stream.ts` | 295 | shared-runtime |  |
| `packages/runtime-node/src/openai-compatible-provider.test.ts` | 130 | shared-runtime | Y |
| `packages/runtime-node/src/openai-compatible-provider.ts` | 113 | shared-runtime |  |
| `packages/runtime-node/src/provider-bundle.test.ts` | 212 | shared-runtime | Y |
| `packages/runtime-node/src/provider-bundle.ts` | 252 | shared-runtime |  |
| `packages/runtime-node/src/provider-contracts.ts` | 86 | shared-runtime |  |
| `packages/runtime-node/src/provider-utils.ts` | 190 | shared-runtime |  |
| `packages/runtime-node/src/shared-model-config.test.ts` | 481 | shared-runtime | Y |
| `packages/runtime-node/src/shared-model-config.ts` | 440 | shared-runtime |  |
| `packages/runtime-node/src/shell-classifier.ts` | 227 | shared-runtime |  |
| `packages/runtime-node/src/shell-provider.test.ts` | 139 | shared-runtime | Y |
| `packages/runtime-node/src/shell-provider.ts` | 350 | shared-runtime |  |
| `packages/runtime-sdk/src/contracts.ts` | 227 | shared-runtime |  |
| `packages/runtime-sdk/src/goal-contracts.ts` | 92 | shared-runtime |  |
| `packages/runtime-sdk/src/goal-controller.test.ts` | 126 | shared-runtime | Y |
| `packages/runtime-sdk/src/goal-controller.ts` | 219 | shared-runtime |  |
| `packages/runtime-sdk/src/index.ts` | 83 | shared-runtime |  |
| `packages/runtime-sdk/src/pipeline-contracts.ts` | 170 | shared-runtime |  |
| `packages/runtime-sdk/src/pipeline.test.ts` | 385 | shared-runtime | Y |
| `packages/runtime-sdk/src/pipeline.ts` | 195 | shared-runtime |  |
| `packages/runtime-sdk/src/public-api.test.ts` | 61 | shared-runtime | Y |
| `packages/runtime-sdk/src/runtime.test.ts` | 301 | shared-runtime | Y |
| `packages/runtime-sdk/src/runtime.ts` | 179 | shared-runtime |  |
| `packages/runtime-sdk/src/session-contracts.ts` | 64 | shared-runtime |  |
| `packages/runtime-sdk/src/session-controller.test.ts` | 144 | shared-runtime | Y |
| `packages/runtime-sdk/src/session-controller.ts` | 207 | shared-runtime |  |
| `packages/task-thread/src/index.ts` | 116 | shared-task-thread |  |
| `packages/task-thread/src/task-thread.test.ts` | 75 | shared-task-thread | Y |
| `packages/ui/src/index.tsx` | 84 | shared-ui |  |


---

## 函数与职责目录

### 提取方法与类别

静态正则提取（非完整 AST）。类别映射到：`function` / `method` / `component` / `hook` / `handler` / `callback` / `constructor` / `getter` / `setter` / `type`。

| category | 含义 |
|----------|------|
| function | 普通函数 / 导出函数 |
| method | 类或对象方法 |
| component | React 组件（PascalCase + tsx 等） |
| hook | React Hook（useX） |
| handler | IPC handler / 事件处理器 |
| callback | onX 回调风格函数 |
| constructor | 构造函数 / 类声明入口 |
| getter / setter | getX / setX 方法 |
| type | interface / type 契约 |

### 符号规模

| Layer | Prod symbols |
|-------|-------------:|
| client-main | 1346 |
| frontend-renderer | 837 |
| shared-runtime | 336 |
| shared-protocol | 229 |
| shared-chat-kernel | 62 |
| shared-conversation-store | 27 |
| shared-credential-helper | 22 |
| shared-task-thread | 5 |
| shared-i18n | 5 |
| shared-ui | 4 |
| client-preload | 2 |

合计生产符号：**2875**（另有测试符号 253）。

### 类别分布

| category | count |
|----------|------:|
| function | 1780 |
| type | 698 |
| handler | 147 |
| component | 133 |
| method | 71 |
| hook | 27 |
| constructor | 8 |
| getter | 7 |
| callback | 4 |

### 关键模块职责导读

#### Renderer

| 区域 | 典型职责 |
|------|----------|
| `renderer/src/App.tsx` | 应用壳、布局、全局装配 |
| `renderer/src/clientApi.ts` | 对 `window.peerAgent` 的类型化封装 |
| `renderer/src/chat/**` | 对话 UI、消息流、Goal 卡片、权限提示 |
| `renderer/src/app/state/**` | 前端展示态 reducers / store |
| `renderer/src/capabilities/**` | 能力面板展示（非执行） |

#### Main

| 区域 | 典型职责 |
|------|----------|
| `main.mjs` | 窗口、IPC 总装、`buildRuntimeProjection`、权限 grant 工厂 |
| `llm-chat-service.mjs` | 模型对话编排、流式事件、permission resolve |
| `chat-runtime/*-agent-loop.mjs` | 各 Provider 的 agent 循环 |
| `chat-runtime/projected-tool-executor.mjs` | 投影工具执行：准入 → 权限 → 本地执行 → Evidence |
| `runtime-gateway/local-tool-host.mjs` | 本地工具宿主 |
| `capability-registry.mjs` / providers | 能力发现与 Provider 适配 |
| `mcp-registry.mjs` | MCP 安装/连接/工具注册 |

### 按文件的函数与职责清单（生产）

表格列：`Line | category | Name | Role | Export`，其中 category 使用 function/method/component/hook/handler 等。


#### `apps/desktop/electron/main/app-menu.mjs` (2 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 58 | function | `resolveLabels` | Function |  |
| 71 | function | `buildAppMenu` | Function | Y |

#### `apps/desktop/electron/main/auto-updater.mjs` (23 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 87 | function | `resolveUpdateChannel` | Function | Y |
| 93 | function | `toUpdaterChannel` | Function |  |
| 98 | function | `applyChannel` | Function |  |
| 112 | function | `initAutoUpdater` | Function | Y |
| 159 | function | `stopAutoUpdater` | Function | Y |
| 167 | function | `normalizePreference` | Parser/normalizer |  |
| 172 | function | `getUpdaterStatus` | Function | Y |
| 193 | function | `setChannelPreference` | Function | Y |
| 204 | function | `checkForUpdates` | Function | Y |
| 221 | function | `downloadUpdate` | Function | Y |
| 247 | function | `downloadUpdateMacManual` | Function |  |
| 316 | function | `getElectronNetFetch` | Function |  |
| 331 | function | `fetchWithProxyFallback` | Function |  |
| 346 | function | `downloadToFile` | Function |  |
| 381 | function | `openInstaller` | Function | Y |
| 410 | function | `openReleasePage` | Function | Y |
| 429 | function | `quitAndInstall` | Function | Y |
| 438 | function | `setPhase` | Function |  |
| 445 | function | `emit` | Function |  |
| 456 | function | `wireEvents` | Function |  |
| 504 | function | `normalizeReleaseNotes` | Parser/normalizer |  |
| 517 | function | `log` | Function |  |
| 522 | function | `safeJson` | Function |  |

#### `apps/desktop/electron/main/capability-registry.mjs` (3 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 4 | function | `readManifest` | Function |  |
| 14 | function | `loadManifests` | Function |  |
| 26 | function | `createCapabilityRegistry` | Function | Y |

#### `apps/desktop/electron/main/chat-runtime/agent-loop-kernel.mjs` (7 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 4 | function | `normalizeAgentLoopMaxTurns` | Parser/normalizer | Y |
| 25 | function | `defaultAgentLoopMaxTurns` | Function |  |
| 29 | function | `hasBillableUsage` | Function |  |
| 38 | function | `createAgentLoopKernel` | Function | Y |
| 182 | function | `isToolResultMessage` | Function |  |
| 191 | function | `appendUserCorrection` | Function |  |
| 200 | function | `handleTerminalTextResponse` | Function | Y |

#### `apps/desktop/electron/main/chat-runtime/anthropic-agent-loop.mjs` (1 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 25 | function | `agentLoopAnthropic` | Function | Y |

#### `apps/desktop/electron/main/chat-runtime/compaction-coordinator.mjs` (10 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 10 | function | `buildCompactionProviderConfig` | Provider | Y |
| 33 | function | `isPromptTooLongResponse` | Function | Y |
| 49 | function | `buildPromptTooLongRecoveryError` | Function | Y |
| 64 | function | `applyMicrocompaction` | Function | Y |
| 77 | function | `shouldShowCompactionStart` | Function |  |
| 90 | function | `computeContextBudget` | Function | Y |
| 148 | function | `contextTokensFromUsageSnapshot` | Function | Y |
| 166 | function | `computeContextInfo` | Function | Y |
| 199 | function | `persistAndNotifyCompaction` | Function |  |
| 232 | function | `runCompactionCheck` | Function | Y |

#### `apps/desktop/electron/main/chat-runtime/compaction-registry.mjs` (5 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 21 | function | `beginCompaction` | Function | Y |
| 36 | function | `updateCompactionProgress` | Function | Y |
| 48 | function | `endCompaction` | Function | Y |
| 62 | function | `getCompaction` | Function | Y |
| 75 | function | `__resetCompactionRegistry` | Function | Y |

#### `apps/desktop/electron/main/chat-runtime/gemini-agent-loop.mjs` (1 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 22 | function | `agentLoopGemini` | Function | Y |

#### `apps/desktop/electron/main/chat-runtime/goal-mode-gate.mjs` (19 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 47 | function | `escapeRegExp` | Function |  |
| 51 | function | `normalizeWorkspacePath` | Parser/normalizer |  |
| 55 | function | `normalizeWorkspaceRoots` | Parser/normalizer |  |
| 67 | function | `resolveTargetPath` | Function |  |
| 75 | function | `isInsideWorkspace` | Function |  |
| 83 | function | `isInsideAnyWorkspace` | Function |  |
| 89 | function | `scopePathCandidates` | Function |  |
| 109 | function | `looksPathLikeScopePattern` | Function |  |
| 117 | function | `matchesScopePattern` | Function |  |
| 139 | function | `evaluateWriteScope` | Function | Y |
| 183 | function | `detectIrreversibleAction` | Function | Y |
| 196 | function | `isHighRiskGoalAction` | Function |  |
| 201 | function | `defaultGoalPlanStore` | Store |  |
| 209 | function | `resolveGoalPlanGate` | Function | Y |
| 232 | function | `resolveActivePlanBoundaries` | Function | Y |
| 248 | function | `resolveActiveGoalExecutionBinding` | Function | Y |
| 288 | function | `evaluateGoalModeGate` | Function | Y |
| 367 | function | `denialMessage` | Function |  |
| 413 | function | `buildGoalModeDenial` | Function | Y |

#### `apps/desktop/electron/main/chat-runtime/message-sanitizer.mjs` (7 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 1 | function | `hasContent` | Function |  |
| 7 | function | `isEmptyAssistantMessage` | Function |  |
| 23 | function | `neutralizeToolCallSyntax` | Function | Y |
| 32 | function | `neutralizeContentBlock` | Function |  |
| 50 | function | `neutralizeMessageContent` | Function |  |
| 81 | function | `normalizeToolCallPairing` | Parser/normalizer |  |
| 129 | function | `sanitizeApiMessages` | Function | Y |

#### `apps/desktop/electron/main/chat-runtime/openai-agent-loop.mjs` (1 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 26 | function | `agentLoopOpenAI` | Function | Y |

#### `apps/desktop/electron/main/chat-runtime/permission-gate.mjs` (15 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 19 | function | `normalizeLocalAccessLevel` | Parser/normalizer |  |
| 23 | function | `compareShellRisk` | Function |  |
| 28 | function | `buildFilePermissionCall` | Function |  |
| 53 | function | `buildShellPermissionCall` | Function |  |
| 78 | function | `buildLocalCapabilityPermissionCall` | Function |  |
| 93 | function | `extractPermissionCommand` | Function |  |
| 106 | function | `normalizePermissionCommandSignature` | Parser/normalizer |  |
| 121 | function | `buildPermissionSignature` | Function |  |
| 130 | function | `buildPermissionScopeKey` | Function |  |
| 136 | function | `createAutoAccessGrant` | Function |  |
| 151 | function | `maybeCreateAutoGrantForFile` | Function |  |
| 160 | function | `shouldAutoApproveShellForAccessLevel` | Function |  |
| 166 | function | `maybeCreateAutoGrantForShell` | Function |  |
| 175 | function | `createAutoScopeGrant` | Function |  |
| 186 | function | `createChatPermissionGate` | Function | Y |

#### `apps/desktop/electron/main/chat-runtime/projected-tool-executor.mjs` (9 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 26 | function | `formatContextResult` | Function |  |
| 30 | function | `createSessionStore` | Store |  |
| 32 | getter | `getSession` | Method |  |
| 38 | function | `executorCapabilityId` | Function |  |
| 44 | function | `resolveSafeWorkspaceRoot` | Function |  |
| 53 | function | `resolveProjectedModelToolCall` | Function | Y |
| 97 | function | `materializeShellExecution` | Function |  |
| 128 | function | `materializeProjectedToolExecution` | Function | Y |
| 155 | function | `executeProjectedModelTool` | Function | Y |

#### `apps/desktop/electron/main/chat-runtime/provider-recovery-broker.mjs` (10 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 38 | function | `describeProviderTarget` | Provider | Y |
| 44 | function | `describeFetchFailure` | Function | Y |
| 54 | function | `isProviderTransportFailure` | Provider | Y |
| 59 | function | `isSameProviderRetryableFailure` | Provider | Y |
| 64 | function | `providerCanRun` | Function | Y |
| 68 | function | `modelKey` | Function |  |
| 72 | function | `orderProviderCandidates` | Provider | Y |
| 97 | function | `canReplayProviderAttempt` | Provider | Y |
| 101 | function | `canRetrySameProviderAttempt` | Provider | Y |
| 105 | function | `createProviderAttemptStream` | Provider | Y |

#### `apps/desktop/electron/main/chat-runtime/qoder-agent-loop.mjs` (4 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 17 | function | `makeAbortError` | Function |  |
| 23 | function | `qoderThinkingOnlyResponseError` | Function |  |
| 28 | function | `qoderThinkingOnlyResponseCorrection` | Function |  |
| 37 | function | `agentLoopQoder` | Function | Y |

#### `apps/desktop/electron/main/chat-runtime/response-guard.mjs` (9 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 10 | function | `hasUnsupportedToolClaim` | Function | Y |
| 24 | function | `hasLiteralToolCallSyntax` | Function | Y |
| 30 | function | `shouldRetryNoToolResponse` | Function | Y |
| 34 | function | `unsupportedToolResponseCorrection` | Function | Y |
| 43 | function | `unsupportedToolResponseError` | Function | Y |
| 48 | function | `thinkingOnlyResponseError` | Function | Y |
| 53 | function | `thinkingOnlyResponseCorrection` | Function | Y |
| 62 | function | `emptyModelResponseError` | Function | Y |
| 67 | function | `emptyModelResponseCorrection` | Function | Y |

#### `apps/desktop/electron/main/chat-runtime/runtime-pipeline-adapter.mjs` (4 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 3 | function | `createDesktopAbortError` | Function | Y |
| 9 | function | `createDesktopPipelineEventAdapter` | Function | Y |
| 14 | method | `emit` | Method |  |
| 28 | function | `runDesktopRuntimePipeline` | Function | Y |

#### `apps/desktop/electron/main/chat-runtime/runtime-session-adapter.mjs` (8 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 3 | function | `requireStreamId` | Function |  |
| 10 | function | `resolveSessionId` | Function |  |
| 16 | function | `createDesktopRuntimeSessionAdapter` | Function | Y |
| 63 | method | `cancelStream` | Method |  |
| 66 | method | `failStream` | Method |  |
| 69 | getter | `getSession` | Method |  |
| 72 | getter | `getActiveTurn` | Method |  |
| 75 | method | `listSessions` | Method |  |

#### `apps/desktop/electron/main/chat-runtime/tool-orchestrator.mjs` (17 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 3 | function | `createToolContext` | Function | Y |
| 30 | function | `safeParseJson` | Parser/normalizer | Y |
| 39 | function | `materializeToolOutput` | Function | Y |
| 53 | function | `isRequestUserInputTool` | Function |  |
| 70 | function | `boundAggregateStreamPayload` | Function |  |
| 100 | function | `fitJsonPreviewWithinLimit` | Function |  |
| 112 | function | `topLevelString` | Function |  |
| 117 | function | `boundGenericJsonStreamPayload` | Function |  |
| 151 | function | `boundToolResultForStream` | Function |  |
| 161 | function | `formatToolResultForStream` | Function | Y |
| 182 | function | `addStringRefs` | Function |  |
| 193 | function | `collectToolEvidenceRefs` | Function | Y |
| 212 | function | `mergeEvidenceRefs` | Function |  |
| 219 | function | `appendEvidenceRefsToToolOutput` | Function | Y |
| 246 | function | `resolveCapabilityDisplayName` | Function | Y |
| 260 | function | `extractToolControlSignal` | Function | Y |
| 268 | function | `executeModelToolCall` | Function | Y |

#### `apps/desktop/electron/main/compaction-diagnostic-log.mjs` (3 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 22 | function | `maskApiKey` | Function |  |
| 29 | function | `describeProvider` | Provider |  |
| 45 | function | `logCompactionDiagnostic` | Function | Y |

#### `apps/desktop/electron/main/context-compactor.mjs` (43 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 133 | function | `resetCircuitBreaker` | Function | Y |
| 137 | function | `isCircuitBreakerTripped` | Function |  |
| 141 | function | `recordCompactionSuccess` | Function |  |
| 145 | function | `recordCompactionFailure` | Function |  |
| 166 | function | `estimateTextTokens` | Function |  |
| 178 | function | `estimateTokensFromMessages` | Function |  |
| 235 | function | `estimateToolsTokens` | Function |  |
| 268 | function | `previewHistoricalText` | Function |  |
| 276 | function | `tryParseJsonObject` | Parser/normalizer |  |
| 288 | function | `pickDefined` | Function |  |
| 296 | function | `compactLocalRefPayload` | Function |  |
| 353 | function | `compactLongHistoricalString` | Function |  |
| 362 | function | `microcompactStringContent` | Function |  |
| 392 | function | `microcompactBlockContent` | Function |  |
| 420 | function | `microcompactMessageContent` | Function |  |
| 445 | function | `microcompactMessagesForContext` | Function | Y |
| 493 | function | `groupMessagesByApiRound` | Function |  |
| 517 | function | `shouldCompact` | Function |  |
| 522 | function | `shouldRunCompaction` | Function |  |
| 534 | function | `messageHasToolResult` | Function |  |
| 539 | function | `messageHasToolUse` | Function |  |
| 544 | function | `toolUseEntries` | Function |  |
| 560 | function | `toolResultIds` | Function |  |
| 573 | function | `findUnclosedToolTailStart` | Function |  |
| 585 | function | `isHumanUserMessage` | Function |  |
| 592 | function | `expandKeepForToolContinuity` | Function |  |
| 609 | function | `findCurrentTurnStart` | Function |  |
| 616 | function | `splitForCompaction` | Function |  |
| 652 | function | `formatOldMessagesForSummary` | Function |  |
| 666 | function | `formatCompactSummary` | Function |  |
| 692 | function | `readSseStream` | Function |  |
| 756 | function | `estimateSummaryChars` | Function |  |
| 781 | function | `summarizeWithLLM` | Function |  |
| 1017 | function | `summarizeOldMessages` | Function |  |
| 1113 | function | `buildHandoffContent` | Function |  |
| 1132 | function | `normalizeContinuityContext` | Parser/normalizer |  |
| 1147 | function | `buildContinuityCarryForwardSummary` | Function |  |
| 1161 | function | `mergeContinuityAndDeltaSummary` | Function |  |
| 1175 | function | `countContinuityMessages` | Function |  |
| 1180 | function | `buildCompactedMessages` | Function |  |
| 1221 | function | `setCompactionAfterTokens` | Function |  |
| 1234 | function | `truncateHeadForRetry` | Function |  |
| 1265 | function | `compactIfNeeded` | Function | Y |

#### `apps/desktop/electron/main/conversation-compaction-persistence.mjs` (3 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 1 | function | `isPendingAssistantMessage` | Function | Y |
| 5 | function | `isCompactionMessage` | Function | Y |
| 9 | function | `buildPersistedCompactedMessages` | Function | Y |

#### `apps/desktop/electron/main/data-store.mjs` (7 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 21 | function | `resolveDataHome` | Function |  |
| 55 | function | `getDataHome` | Function | Y |
| 62 | function | `pathOf` | Function | Y |
| 69 | function | `listEntries` | Function | Y |
| 82 | function | `migrateFromLegacy` | Function | Y |
| 109 | function | `exportBundle` | Function | Y |
| 129 | function | `importBundle` | Function | Y |

#### `apps/desktop/electron/main/env-loader.mjs` (2 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 4 | function | `parseEnvValue` | Parser/normalizer |  |
| 13 | function | `loadLocalEnv` | Function | Y |

#### `apps/desktop/electron/main/goal-intake-convergence.mjs` (2 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 20 | function | `isIntakeContract` | Function | Y |
| 30 | function | `decideIntakeConvergence` | Function | Y |

#### `apps/desktop/electron/main/goal-message-router.mjs` (5 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 48 | function | `normalizeText` | Parser/normalizer |  |
| 52 | function | `matchesAny` | Function |  |
| 56 | function | `classifyGoalMessage` | Function | Y |
| 120 | function | `applyGoalMessageRoute` | Function | Y |
| 144 | function | `routeGoalMessage` | Function | Y |

#### `apps/desktop/electron/main/goal-plan-store.mjs` (53 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 38 | function | `readJsonl` | Function |  |
| 53 | function | `appendJsonl` | Function |  |
| 58 | function | `writeJsonl` | Function |  |
| 65 | function | `writeJsonAtomic` | Function |  |
| 72 | function | `readJson` | Function |  |
| 94 | function | `aggregateProgress` | Function | Y |
| 146 | function | `derivePlanStatus` | Function | Y |
| 209 | function | `updateTaskInTree` | Function |  |
| 227 | function | `taskExistsInTree` | Function |  |
| 241 | function | `findTaskInTree` | Function |  |
| 360 | function | `normalizeStringArray` | Parser/normalizer |  |
| 366 | function | `normalizeOptionalString` | Parser/normalizer |  |
| 372 | function | `normalizeEvidenceRefList` | Parser/normalizer |  |
| 377 | function | `normalizeEvidenceIndexRecord` | Parser/normalizer |  |
| 400 | function | `normalizeWorkflowKind` | Parser/normalizer |  |
| 404 | function | `isSelfDrivenGoal` | Function |  |
| 410 | function | `goalPlanIsSelfDriven` | Function | Y |
| 414 | function | `goalPlanRequiresApproval` | Function | Y |
| 418 | function | `defaultExecutionPolicyForWorkflow` | Function |  |
| 424 | function | `normalizeActivation` | Parser/normalizer |  |
| 454 | function | `normalizeExecutionPolicy` | Parser/normalizer |  |
| 473 | function | `makeDefaultGoalTask` | Function |  |
| 501 | function | `normalizeSuccessCriterion` | Parser/normalizer |  |
| 526 | function | `normalizeSuccessCriteria` | Parser/normalizer |  |
| 535 | function | `normalizeCriterionResult` | Parser/normalizer |  |
| 552 | function | `normalizeCriterionResults` | Parser/normalizer |  |
| 557 | function | `normalizeManualConfirmation` | Parser/normalizer |  |
| 585 | function | `normalizeManualConfirmations` | Parser/normalizer |  |
| 590 | function | `collectManualCriterionIds` | Function |  |
| 598 | function | `normalizeExplorerRequest` | Parser/normalizer |  |
| 644 | function | `normalizeExplorerReport` | Parser/normalizer |  |
| 680 | function | `collectExplorerReportEvidenceRefs` | Function |  |
| 689 | function | `normalizeExplorerRegistryRefs` | Parser/normalizer |  |
| 699 | function | `assertExplorerReportEvidenceRegistered` | Function |  |
| 719 | function | `normalizeExplorerRun` | Parser/normalizer |  |
| 753 | function | `normalizeExploreQuestion` | Parser/normalizer |  |
| 783 | function | `normalizeExplorePlan` | Parser/normalizer |  |
| 799 | function | `countExplorerRuns` | Function |  |
| 808 | function | `computeExplorerBatch` | Function |  |
| 818 | function | `normalizeVerifierTarget` | Parser/normalizer |  |
| 846 | function | `normalizeVerifierIssue` | Parser/normalizer |  |
| 865 | function | `normalizeVerifierReport` | Parser/normalizer |  |
| 883 | function | `normalizeVerifierRun` | Parser/normalizer |  |
| 926 | function | `normalizeRunEvent` | Parser/normalizer |  |
| 950 | function | `normalizeRunTrace` | Parser/normalizer |  |
| 964 | function | `normalizeConversationId` | Parser/normalizer |  |
| 972 | function | `normalizeWorkspacePath` | Parser/normalizer |  |
| 978 | function | `normalizeRunnerState` | Parser/normalizer |  |
| 1074 | function | `normalizePlan` | Parser/normalizer |  |
| 1108 | function | `withRunTraceEvent` | Function |  |
| 1133 | function | `isActivePlan` | Function |  |
| 1137 | function | `isInactivePlan` | Function |  |
| 1141 | function | `createGoalPlanStore` | Store | Y |

#### `apps/desktop/electron/main/goal-runner-message-persistence.mjs` (2 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 16 | function | `createGoalRunnerAssistantPlaceholder` | Function | Y |
| 39 | function | `buildGoalRunnerStreamStartedPayload` | Function | Y |

#### `apps/desktop/electron/main/goal-runner.mjs` (35 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 30 | function | `toPositiveInteger` | Function |  |
| 37 | function | `errorMessage` | Function |  |
| 44 | function | `countToolCalls` | Function |  |
| 51 | function | `normalizeExploreRequests` | Parser/normalizer |  |
| 61 | function | `collectLeafTasks` | Function |  |
| 77 | function | `collectStringSet` | Function |  |
| 85 | function | `collectKnownInvolvedFiles` | Function |  |
| 93 | function | `hasCompletedExplorerReport` | Function |  |
| 98 | function | `collectAutoSuccessCriteria` | Function |  |
| 108 | function | `firstNonEmptyString` | Function |  |
| 115 | function | `buildInspectScope` | Function |  |
| 130 | function | `createDeterministicExplorePlan` | Function | Y |
| 182 | function | `shouldStopForPlan` | Function |  |
| 186 | function | `runnerIsStopped` | Function |  |
| 204 | function | `isIntakeContract` | Function |  |
| 208 | function | `isStartAuthorized` | Function |  |
| 218 | function | `hasCompletedProgress` | Function |  |
| 227 | function | `countLeafEvidence` | Function |  |
| 248 | function | `progressSignal` | Function |  |
| 255 | function | `signalAdvanced` | Function |  |
| 260 | function | `nextPhaseAfterTurn` | Function |  |
| 282 | function | `phaseForIntent` | Function |  |
| 317 | function | `computeReanchorInterval` | Function | Y |
| 327 | function | `shouldReanchor` | Function | Y |
| 336 | function | `computePlanScopeSnapshot` | Function | Y |
| 359 | function | `detectPlanDrift` | Function | Y |
| 385 | function | `normalizeEvidenceRefSet` | Parser/normalizer |  |
| 396 | function | `taskHasIndexedEvidence` | Function |  |
| 402 | function | `criterionEvidenceIsIndexed` | Function |  |
| 407 | function | `collectManualCriteria` | Function |  |
| 414 | function | `latestManualDodConfirmation` | Function |  |
| 447 | function | `evaluateVerificationGate` | Function | Y |
| 560 | function | `collectVerificationEvidenceRefs` | Function |  |
| 582 | function | `summarizeVerificationGate` | Function |  |
| 591 | function | `createGoalRunner` | Function | Y |

#### `apps/desktop/electron/main/host-restart.mjs` (2 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 32 | function | `resolveRestartScript` | Function |  |
| 46 | function | `createHostRestarter` | Function | Y |

#### `apps/desktop/electron/main/llm-chat-service.mjs` (17 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 60 | function | `sleepWithSignal` | Function |  |
| 77 | function | `buildRuntimeTools` | Function |  |
| 106 | function | `resolveRunWorkspacePath` | Function |  |
| 126 | function | `buildGoalWorkspaceBindingExtensions` | Function |  |
| 147 | function | `recordPromptSnapshot` | Function |  |
| 155 | function | `hasBillableUsage` | Function |  |
| 164 | function | `isRequestUserInputToolName` | Function |  |
| 169 | function | `buildAgentRunOutcome` | Function |  |
| 180 | function | `recordConversationUsage` | Function |  |
| 204 | function | `noteNativeReasoningFallback` | Function |  |
| 218 | function | `terminalDanglingNote` | Function |  |
| 224 | function | `finalizeDanglingToolSegments` | Function |  |
| 243 | function | `wrapWebContentsForRuntimeEvents` | Function |  |
| 319 | method | `send` | Method |  |
| 440 | function | `getActiveContextEpochId` | Function |  |
| 450 | function | `getConversationToolContext` | Function |  |
| 461 | function | `createLlmChatService` | Function | Y |

#### `apps/desktop/electron/main/llm-config-store.mjs` (19 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 44 | function | `decryptLegacySecret` | Function |  |
| 57 | function | `secretsEqual` | Function |  |
| 63 | function | `maskApiKey` | Function |  |
| 72 | function | `nextCopyName` | Function |  |
| 101 | function | `parseLegacyTokens` | Parser/normalizer |  |
| 113 | function | `oauthStatusOf` | Function |  |
| 123 | function | `normalizeModelOptionValues` | Parser/normalizer |  |
| 134 | function | `normalizeModelOptions` | Parser/normalizer |  |
| 147 | function | `normalizeAuthMethod` | Parser/normalizer |  |
| 155 | function | `isOAuthAuthMethod` | Function |  |
| 159 | function | `isLocalCliAuthMethod` | Function |  |
| 163 | function | `applyQoderModelMetadata` | Function |  |
| 180 | function | `applyExplicitModelMetadataPatch` | Function |  |
| 221 | function | `createLlmConfigStore` | Store | Y |
| 1309 | function | `testOpenAI` | Function |  |
| 1330 | function | `testOpenAIResponses` | Function |  |
| 1351 | function | `testAnthropic` | Function |  |
| 1372 | function | `testGemini` | Function |  |
| 1390 | function | `testQoderPrivate` | Function |  |

#### `apps/desktop/electron/main/llm-oauth/google-oauth.mjs` (10 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 11 | function | `openInBrowser` | Function |  |
| 27 | function | `base64url` | Function |  |
| 31 | function | `createPkce` | Function |  |
| 37 | function | `extractEmail` | Function |  |
| 49 | function | `toTokenSet` | Function |  |
| 60 | function | `exchangeCode` | Function |  |
| 80 | function | `refreshGoogleAccessToken` | Function | Y |
| 106 | function | `ensureFreshGoogleTokens` | Function | Y |
| 118 | callback | `CALLBACK_HTML` | Function |  |
| 147 | function | `startGoogleBrowserLogin` | Function | Y |

#### `apps/desktop/electron/main/llm-oauth/grok-oauth.mjs` (16 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 17 | function | `nonEmpty` | Function |  |
| 21 | function | `createOAuthError` | Function |  |
| 27 | function | `hasOAuthScope` | Function |  |
| 31 | function | `assertGrokApiScope` | Function |  |
| 40 | function | `readJson` | Function |  |
| 48 | function | `postForm` | Function |  |
| 57 | function | `delay` | Function |  |
| 71 | function | `createGrokNetworkError` | Function |  |
| 80 | function | `requestDeviceCode` | Function |  |
| 112 | function | `pollForTokens` | Function |  |
| 147 | function | `normalizeTokenResponse` | Parser/normalizer |  |
| 168 | function | `fetchUserInfo` | Function |  |
| 178 | function | `startGrokOAuthLogin` | Function | Y |
| 218 | method | `cancel` | Method |  |
| 224 | function | `refreshGrokTokens` | Function | Y |
| 248 | function | `ensureFreshGrokTokens` | Function | Y |

#### `apps/desktop/electron/main/llm-oauth/openai-oauth.mjs` (10 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 18 | function | `openInBrowser` | Function |  |
| 32 | function | `base64url` | Function |  |
| 36 | function | `createPkce` | Function |  |
| 43 | function | `extractAccountId` | Function |  |
| 56 | function | `toTokenSet` | Function |  |
| 68 | function | `exchangeCode` | Function |  |
| 88 | function | `refreshAccessToken` | Function | Y |
| 115 | function | `ensureFreshTokens` | Function | Y |
| 130 | callback | `CALLBACK_HTML` | Function |  |
| 171 | function | `startBrowserLogin` | Function | Y |

#### `apps/desktop/electron/main/llm-prompts.mjs` (4 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 26 | function | `buildRuntimeContext` | Function | Y |
| 30 | function | `buildSystemCorePrompt` | Function | Y |
| 34 | function | `buildSystemContext` | Function | Y |
| 41 | function | `buildSystemPrompt` | Function | Y |

#### `apps/desktop/electron/main/mac-update-url.mjs` (3 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 10 | function | `mapArch` | Function | Y |
| 15 | function | `buildDmgUrl` | Function | Y |
| 21 | function | `buildReleaseUrl` | Function | Y |

#### `apps/desktop/electron/main/main.mjs` (205 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 89 | function | `findWorkspaceRoot` | Function |  |
| 119 | function | `getDesktopIconPath` | Function |  |
| 123 | function | `setDockIcon` | Function |  |
| 166 | function | `mcpCredentialResolver` | Function |  |
| 179 | callback | `closeMcpOAuthCallback` | Function |  |
| 187 | callback | `waitForMcpOAuthCallback` | Function |  |
| 229 | function | `createMcpProbeResponse` | Function |  |
| 238 | function | `persistMcpProbeResult` | Function |  |
| 268 | function | `providerPromptTargetChanged` | Function |  |
| 274 | function | `recordProviderBaseline` | Provider |  |
| 278 | function | `getDefaultProviderView` | Provider |  |
| 286 | function | `normalizeSystemInstructions` | Parser/normalizer |  |
| 290 | function | `recordInstructionBaseline` | Function |  |
| 298 | function | `getActiveContextEpochId` | Function |  |
| 308 | function | `persistCompactionToConversation` | Function |  |
| 328 | function | `continuityContextFromCompactionResult` | Function |  |
| 341 | function | `continuityContextFromMessages` | Function |  |
| 357 | function | `broadcastToAllWindows` | Function |  |
| 364 | function | `getRunnerWebContents` | Function |  |
| 368 | function | `toRuntimeMessages` | Function |  |
| 387 | function | `buildGoalRunnerMessage` | Function |  |
| 392 | function | `buildGoalRunnerReminder` | Function |  |
| 403 | function | `buildExplorerMessage` | Function |  |
| 424 | function | `buildExplorerReminder` | Function |  |
| 438 | function | `buildExplorerContext` | Function |  |
| 452 | function | `collectLeafTaskSummaries` | Function |  |
| 473 | function | `collectExplorerReports` | Function |  |
| 484 | function | `buildVerifierContext` | Function |  |
| 494 | function | `buildVerifierMessage` | Function |  |
| 500 | function | `buildVerifierReminder` | Function |  |
| 512 | function | `createCollectingWebContents` | Function |  |
| 518 | method | `send` | Method |  |
| 527 | getter | `getText` | Method |  |
| 530 | getter | `getEvents` | Method |  |
| 533 | getter | `getTerminal` | Method |  |
| 539 | function | `addEvidenceRefs` | Function |  |
| 550 | function | `tryParseJsonObject` | Parser/normalizer |  |
| 560 | function | `collectExplorerEvidenceRefs` | Function |  |
| 580 | function | `normalizeVerifierIssues` | Parser/normalizer |  |
| 601 | function | `parseVerifierReport` | Parser/normalizer |  |
| 638 | function | `parseExplorerReport` | Parser/normalizer |  |
| 686 | method | `runGoalTurn` | Method |  |
| 810 | method | `runExplorer` | Method |  |
| 851 | method | `runVerifier` | Method |  |
| 900 | function | `buildRuntimeProjection` | Function |  |
| 913 | function | `loadRendererWindow` | Function |  |
| 926 | function | `createQuickChatWindow` | Function |  |
| 963 | handler | `shortcuts:status` | IPC channel `shortcuts:status` |  |
| 964 | handler | `shortcuts:update` | IPC channel `shortcuts:update` |  |
| 966 | handler | `shortcuts:reset` | IPC channel `shortcuts:reset` |  |
| 968 | handler | `quick-chat:hide` | IPC channel `quick-chat:hide` |  |
| 972 | handler | `quick-chat-popover:show` | IPC channel `quick-chat-popover:show` |  |
| 975 | handler | `quick-chat:set-task-card-visible` | IPC channel `quick-chat:set-task-card-visible` |  |
| 978 | handler | `quick-chat:set-content-height` | IPC channel `quick-chat:set-content-height` |  |
| 981 | handler | `quick-chat-popover:hide` | IPC channel `quick-chat-popover:hide` |  |
| 985 | handler | `quick-chat-popover:select` | IPC channel `quick-chat-popover:select` |  |
| 988 | handler | `quick-chat:submit` | IPC channel `quick-chat:submit` |  |
| 1002 | function | `createWindow` | Function |  |
| 1057 | handler | `bootstrap:get` | IPC channel `bootstrap:get` |  |
| 1067 | handler | `session:get` | IPC channel `session:get` |  |
| 1068 | handler | `capabilities:list` | IPC channel `capabilities:list` |  |
| 1069 | handler | `projects:list` | IPC channel `projects:list` |  |
| 1070 | handler | `runtime-projection:get` | IPC channel `runtime-projection:get` |  |
| 1074 | handler | `updater:get-status` | IPC channel `updater:get-status` |  |
| 1075 | handler | `updater:check` | IPC channel `updater:check` |  |
| 1076 | handler | `updater:download` | IPC channel `updater:download` |  |
| 1077 | handler | `updater:install` | IPC channel `updater:install` |  |
| 1080 | handler | `updater:open-installer` | IPC channel `updater:open-installer` |  |
| 1081 | handler | `updater:open-release-page` | IPC channel `updater:open-release-page` |  |
| 1082 | handler | `updater:set-channel` | IPC channel `updater:set-channel` |  |
| 1094 | handler | `settings:get` | IPC channel `settings:get` |  |
| 1095 | handler | `settings:update` | IPC channel `settings:update` |  |
| 1134 | handler | `developer-settings:get` | IPC channel `developer-settings:get` |  |
| 1135 | handler | `developer-settings:update` | IPC channel `developer-settings:update` |  |
| 1143 | handler | `developer-settings:reset` | IPC channel `developer-settings:reset` |  |
| 1147 | handler | `developer-settings:diagnostics` | IPC channel `developer-settings:diagnostics` |  |
| 1156 | handler | `settings:get-sync` | IPC channel `settings:get-sync` |  |
| 1159 | handler | `settings:export` | IPC channel `settings:export` |  |
| 1167 | handler | `settings:import` | IPC channel `settings:import` |  |
| 1180 | function | `rebuildAppMenu` | Function |  |
| 1196 | handler | `locale:set` | IPC channel `locale:set` |  |
| 1204 | function | `createPermissionGrant` | Function |  |
| 1214 | handler | `permission:approve` | IPC channel `permission:approve` |  |
| 1224 | handler | `permission:deny` | IPC channel `permission:deny` |  |
| 1231 | handler | `workspace:list` | IPC channel `workspace:list` |  |
| 1254 | handler | `workspace:ensure-default` | IPC channel `workspace:ensure-default` |  |
| 1277 | handler | `workspace:add` | IPC channel `workspace:add` |  |
| 1301 | handler | `workspace:set-active` | IPC channel `workspace:set-active` |  |
| 1307 | handler | `workspace:remove` | IPC channel `workspace:remove` |  |
| 1315 | handler | `workspace:info` | IPC channel `workspace:info` |  |
| 1323 | handler | `shell:open-path` | IPC channel `shell:open-path` |  |
| 1374 | handler | `git:diff` | IPC channel `git:diff` |  |
| 1492 | handler | `fs:exists` | IPC channel `fs:exists` |  |
| 1531 | handler | `fs:read-dir` | IPC channel `fs:read-dir` |  |
| 1602 | handler | `file:read` | IPC channel `file:read` |  |
| 1673 | handler | `browser:register-webcontents` | IPC channel `browser:register-webcontents` |  |
| 1679 | handler | `browser:unregister-webcontents` | IPC channel `browser:unregister-webcontents` |  |
| 1687 | handler | `conversations:list` | IPC channel `conversations:list` |  |
| 1702 | handler | `conversations:search` | IPC channel `conversations:search` |  |
| 1703 | handler | `conversations:create` | IPC channel `conversations:create` |  |
| 1704 | handler | `conversations:get` | IPC channel `conversations:get` |  |
| 1705 | handler | `conversations:update-title` | IPC channel `conversations:update-title` |  |
| 1706 | handler | `conversations:update-mode` | IPC channel `conversations:update-mode` |  |
| 1707 | handler | `conversations:update-model-effort` | IPC channel `conversations:update-model-effort` |  |
| 1708 | handler | `conversations:append-message` | IPC channel `conversations:append-message` |  |
| 1709 | handler | `conversations:update-last-message` | IPC channel `conversations:update-last-message` |  |
| 1710 | handler | `conversations:replace-messages` | IPC channel `conversations:replace-messages` |  |
| 1711 | handler | `conversations:archive` | IPC channel `conversations:archive` |  |
| 1712 | handler | `conversations:restore` | IPC channel `conversations:restore` |  |
| 1713 | handler | `conversations:pin` | IPC channel `conversations:pin` |  |
| 1714 | handler | `conversations:unpin` | IPC channel `conversations:unpin` |  |
| 1715 | handler | `conversations:reorder-pinned` | IPC channel `conversations:reorder-pinned` |  |
| 1716 | handler | `conversations:auto-archive` | IPC channel `conversations:auto-archive` |  |
| 1720 | handler | `conversations:delete` | IPC channel `conversations:delete` |  |
| 1734 | handler | `conversations:add-usage` | IPC channel `conversations:add-usage` |  |
| 1738 | handler | `goalPlans:list` | IPC channel `goalPlans:list` |  |
| 1743 | handler | `goalPlans:awaiting-counts` | IPC channel `goalPlans:awaiting-counts` |  |
| 1744 | handler | `goalPlans:get` | IPC channel `goalPlans:get` |  |
| 1745 | handler | `goalPlans:create` | IPC channel `goalPlans:create` |  |
| 1746 | handler | `goalPlans:revise` | IPC channel `goalPlans:revise` |  |
| 1748 | handler | `goalPlans:approve` | IPC channel `goalPlans:approve` |  |
| 1759 | handler | `goalPlans:set-status` | IPC channel `goalPlans:set-status` |  |
| 1760 | handler | `goalPlans:record-manual-confirmation` | IPC channel `goalPlans:record-manual-confirmation` |  |
| 1762 | handler | `goalRunner:get-state` | IPC channel `goalRunner:get-state` |  |
| 1763 | handler | `goalRunner:start` | IPC channel `goalRunner:start` |  |
| 1764 | handler | `goalRunner:pause` | IPC channel `goalRunner:pause` |  |
| 1765 | handler | `goalRunner:resume` | IPC channel `goalRunner:resume` |  |
| 1766 | handler | `goalRunner:clear` | IPC channel `goalRunner:clear` |  |
| 1767 | handler | `goalPlans:record-task-evidence` | IPC channel `goalPlans:record-task-evidence` |  |
| 1769 | handler | `goalPlans:delete` | IPC channel `goalPlans:delete` |  |
| 1775 | function | `latestUserTextFromProviderMessages` | Provider |  |
| 1804 | function | `convergeIntakeAfterGoalTurn` | Function |  |
| 1817 | handler | `chat:send` | IPC channel `chat:send` |  |
| 1936 | handler | `chat:abort` | IPC channel `chat:abort` |  |
| 1943 | handler | `chat:stream:reattach` | IPC channel `chat:stream:reattach` |  |
| 1948 | handler | `chat:stream:list-active` | IPC channel `chat:stream:list-active` |  |
| 1954 | handler | `chat:compact` | IPC channel `chat:compact` |  |
| 2124 | handler | `chat:compaction:get` | IPC channel `chat:compaction:get` |  |
| 2127 | handler | `prompt-snapshots:list` | IPC channel `prompt-snapshots:list` |  |
| 2129 | handler | `prompt-snapshots:get` | IPC channel `prompt-snapshots:get` |  |
| 2131 | handler | `prompt-context-epochs:list` | IPC channel `prompt-context-epochs:list` |  |
| 2133 | handler | `prompt-context-epochs:events` | IPC channel `prompt-context-epochs:events` |  |
| 2139 | handler | `prompt-context-epochs:chain` | IPC channel `prompt-context-epochs:chain` |  |
| 2147 | handler | `llm:channels:list` | IPC channel `llm:channels:list` |  |
| 2151 | function | `listProvidersWithSilentOAuthRefresh` | Provider |  |
| 2160 | function | `listGroupsWithSilentOAuthRefresh` | Function |  |
| 2170 | handler | `usage:stats` | IPC channel `usage:stats` |  |
| 2173 | handler | `llm:groups:list` | IPC channel `llm:groups:list` |  |
| 2174 | handler | `llm:list` | IPC channel `llm:list` |  |
| 2176 | handler | `llm:chat:list` | IPC channel `llm:chat:list` |  |
| 2177 | handler | `llm:add` | IPC channel `llm:add` |  |
| 2182 | handler | `llm:update` | IPC channel `llm:update` |  |
| 2190 | handler | `llm:duplicate` | IPC channel `llm:duplicate` |  |
| 2195 | handler | `llm:add-model` | IPC channel `llm:add-model` |  |
| 2199 | handler | `llm:remove` | IPC channel `llm:remove` |  |
| 2210 | handler | `llm:remove-group` | IPC channel `llm:remove-group` |  |
| 2219 | handler | `llm:set-default` | IPC channel `llm:set-default` |  |
| 2228 | handler | `llm:test` | IPC channel `llm:test` |  |
| 2229 | handler | `llm:quota` | IPC channel `llm:quota` |  |
| 2247 | handler | `llm:oauth:start` | IPC channel `llm:oauth:start` |  |
| 2349 | handler | `llm:oauth:open-pending` | IPC channel `llm:oauth:open-pending` |  |
| 2361 | handler | `llm:oauth:cancel` | IPC channel `llm:oauth:cancel` |  |
| 2371 | handler | `llm:models:list` | IPC channel `llm:models:list` |  |
| 2420 | handler | `llm:models:fetch` | IPC channel `llm:models:fetch` |  |
| 2446 | handler | `host:restart` | IPC channel `host:restart` |  |
| 2475 | function | `withWorkspace` | Function |  |
| 2480 | function | `matchWorkspace` | Function |  |
| 2489 | handler | `pending-task:write` | IPC channel `pending-task:write` |  |
| 2492 | handler | `pending-task:consume` | IPC channel `pending-task:consume` |  |
| 2498 | handler | `pending-task:peek` | IPC channel `pending-task:peek` |  |
| 2501 | handler | `pending-task:clear` | IPC channel `pending-task:clear` |  |
| 2507 | handler | `mcp:list-installed` | IPC channel `mcp:list-installed` |  |
| 2508 | handler | `mcp:list-capabilities` | IPC channel `mcp:list-capabilities` |  |
| 2509 | handler | `mcp:list-credentials` | IPC channel `mcp:list-credentials` |  |
| 2510 | handler | `mcp:put-credential` | IPC channel `mcp:put-credential` |  |
| 2511 | handler | `mcp:delete-credential` | IPC channel `mcp:delete-credential` |  |
| 2512 | handler | `mcp:install` | IPC channel `mcp:install` |  |
| 2513 | handler | `mcp:upsert-server` | IPC channel `mcp:upsert-server` |  |
| 2514 | handler | `mcp:uninstall` | IPC channel `mcp:uninstall` |  |
| 2534 | handler | `mcp:set-enabled` | IPC channel `mcp:set-enabled` |  |
| 2535 | handler | `mcp:set-tool-visibility` | IPC channel `mcp:set-tool-visibility` |  |
| 2536 | handler | `mcp:test-connection` | IPC channel `mcp:test-connection` |  |
| 2543 | handler | `mcp:refresh-manifest` | IPC channel `mcp:refresh-manifest` |  |
| 2551 | handler | `mcp:start-oauth` | IPC channel `mcp:start-oauth` |  |
| 2582 | handler | `mcp:finish-oauth` | IPC channel `mcp:finish-oauth` |  |
| 2589 | handler | `mcp:read-resource` | IPC channel `mcp:read-resource` |  |
| 2594 | handler | `mcp:get-prompt` | IPC channel `mcp:get-prompt` |  |
| 2599 | handler | `mcp:connect-and-register` | IPC channel `mcp:connect-and-register` |  |
| 2631 | function | `forwardRuntimeEvent` | Function |  |
| 2635 | function | `emitRuntimeEvent` | Function |  |
| 2643 | function | `flushPendingRuntimeEvents` | Function |  |
| 2691 | handler | `client-tool:execute` | IPC channel `client-tool:execute` |  |
| 2698 | handler | `shell:tasks:list` | IPC channel `shell:tasks:list` |  |
| 2699 | handler | `shell:tasks:stop-active` | IPC channel `shell:tasks:stop-active` |  |
| 2700 | handler | `shell:tasks:stop` | IPC channel `shell:tasks:stop` |  |
| 2701 | handler | `shell:permissions:list` | IPC channel `shell:permissions:list` |  |
| 2702 | handler | `shell:permissions:add` | IPC channel `shell:permissions:add` |  |
| 2705 | handler | `skills:list` | IPC channel `skills:list` |  |
| 2706 | handler | `skills:refresh` | IPC channel `skills:refresh` |  |
| 2707 | handler | `skills:upload` | IPC channel `skills:upload` |  |
| 2711 | handler | `skills:enable` | IPC channel `skills:enable` |  |
| 2715 | handler | `skills:disable` | IPC channel `skills:disable` |  |
| 2720 | handler | `skills:list-available` | IPC channel `skills:list-available` |  |
| 2721 | handler | `skills:link` | IPC channel `skills:link` |  |
| 2725 | handler | `skills:unlink` | IPC channel `skills:unlink` |  |

#### `apps/desktop/electron/main/mcp-client.mjs` (43 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 14 | function | `nowIso` | Function |  |
| 18 | function | `asPlainStringRecord` | Function |  |
| 27 | function | `normalizeAuthContext` | Parser/normalizer |  |
| 41 | function | `authCacheKey` | Function |  |
| 59 | function | `serverKey` | Function |  |
| 78 | function | `normalizeServerConfig` | Parser/normalizer |  |
| 103 | function | `prepareServerConfig` | Function |  |
| 137 | function | `createOAuthProvider` | Provider |  |
| 161 | method | `saveClientInformation` | Method |  |
| 166 | method | `saveTokens` | Method |  |
| 170 | method | `redirectToAuthorization` | Method |  |
| 177 | method | `saveCodeVerifier` | Method |  |
| 182 | method | `codeVerifier` | Method |  |
| 187 | method | `saveDiscoveryState` | Method |  |
| 191 | method | `invalidateCredentials` | Method |  |
| 208 | function | `createTransport` | Function |  |
| 233 | function | `connect` | Function |  |
| 247 | function | `withClient` | Function |  |
| 252 | function | `safeArray` | Function |  |
| 257 | function | `normalizeTool` | Parser/normalizer |  |
| 267 | function | `normalizeResource` | Parser/normalizer |  |
| 276 | function | `normalizePrompt` | Parser/normalizer |  |
| 284 | function | `readServerInfo` | Function |  |
| 304 | function | `discoverMcpManifest` | Function | Y |
| 345 | function | `entryAuthMetadata` | Function |  |
| 351 | function | `errorMessage` | Function |  |
| 355 | function | `isAuthRequiredError` | Function |  |
| 369 | function | `authRequiredProbe` | Function |  |
| 391 | function | `probeMcpConnection` | Function | Y |
| 424 | function | `testMcpConnection` | Function | Y |
| 451 | function | `listMcpTools` | Function | Y |
| 456 | function | `callMcpTool` | Function | Y |
| 465 | function | `readMcpResource` | Function | Y |
| 471 | function | `getMcpPrompt` | Function | Y |
| 477 | function | `startMcpOAuth` | Function | Y |
| 515 | function | `finishMcpOAuth` | Function | Y |
| 528 | function | `textFromContentItem` | Function |  |
| 536 | function | `extractTextContent` | Function |  |
| 541 | function | `normalizeMcpToolResult` | Parser/normalizer | Y |
| 552 | function | `safeStringify` | Function |  |
| 560 | function | `sameServer` | Function |  |
| 571 | function | `disconnectMcp` | Function | Y |
| 581 | function | `disconnectAll` | Function | Y |

#### `apps/desktop/electron/main/mcp-credential-store.mjs` (30 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 13 | function | `nowIso` | Function |  |
| 17 | function | `asString` | Function |  |
| 21 | function | `normalizeRef` | Parser/normalizer |  |
| 27 | function | `idFromRef` | Function |  |
| 32 | function | `validateHeaderName` | Function |  |
| 41 | function | `validateEnvName` | Function |  |
| 50 | function | `normalizeKind` | Parser/normalizer |  |
| 56 | function | `targetForKind` | Function |  |
| 62 | function | `normalizeScopes` | Parser/normalizer |  |
| 67 | function | `normalizeUrl` | Parser/normalizer |  |
| 79 | function | `normalizeOAuthConfig` | Parser/normalizer |  |
| 107 | function | `oauthView` | Function |  |
| 121 | function | `getSafeStorage` | Function |  |
| 125 | function | `canUseSafeStorage` | Function |  |
| 133 | function | `encryptSecret` | Function |  |
| 150 | function | `decryptSecret` | Function |  |
| 158 | function | `secureJson` | Function |  |
| 164 | function | `revealJson` | Function |  |
| 178 | function | `loadCredentialFile` | Function |  |
| 191 | function | `writeCredentialFile` | Function |  |
| 196 | function | `normalizeStoredCredential` | Store |  |
| 219 | function | `metadataFromStored` | Store |  |
| 236 | function | `normalizeCredentialInput` | Parser/normalizer |  |
| 274 | function | `normalizeAuthBinding` | Parser/normalizer |  |
| 286 | function | `ensureCompatible` | Function |  |
| 297 | function | `createMcpCredentialStore` | Store | Y |
| 356 | getter | `getOAuthCredential` | Method |  |
| 370 | method | `updateOAuthCredential` | Method |  |
| 390 | function | `resolveMcpCredentialInjection` | Function | Y |
| 466 | function | `createMcpCredentialResolver` | Function | Y |

#### `apps/desktop/electron/main/mcp-registry.mjs` (17 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 14 | function | `nowIso` | Function |  |
| 18 | function | `registryPath` | Function |  |
| 22 | function | `ensureParent` | Function |  |
| 26 | function | `readJsonFile` | Function |  |
| 37 | function | `writeJsonFile` | Function |  |
| 42 | function | `asString` | Function |  |
| 46 | function | `asStringArray` | Function |  |
| 50 | function | `asRecord` | Function |  |
| 57 | function | `normalizeCredentialRef` | Parser/normalizer |  |
| 63 | function | `normalizeHeaderName` | Parser/normalizer |  |
| 70 | function | `normalizeEnvName` | Parser/normalizer |  |
| 77 | function | `normalizeAuthBinding` | Parser/normalizer |  |
| 95 | function | `slugifyMcpId` | Function | Y |
| 105 | function | `normalizeLegacyItem` | Parser/normalizer |  |
| 147 | function | `normalizeRegistry` | Parser/normalizer |  |
| 155 | function | `toRendererView` | Function |  |
| 219 | function | `createMcpRegistry` | Function | Y |

#### `apps/desktop/electron/main/model-credential-client.mjs` (1 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 12 | function | `createDesktopModelCredentialClient` | Function | Y |

#### `apps/desktop/electron/main/pending-task-store.mjs` (8 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 31 | function | `taskFilePath` | Function |  |
| 42 | function | `writePendingTask` | Function | Y |
| 59 | function | `hasPendingTask` | Function | Y |
| 72 | function | `parsePendingTaskFile` | Parser/normalizer |  |
| 114 | function | `readAndClearPendingTask` | Function | Y |
| 132 | function | `peekPendingTask` | Function | Y |
| 137 | function | `clearPendingTask` | Function | Y |
| 141 | function | `safeRemove` | Function |  |

#### `apps/desktop/electron/main/project-index.mjs` (7 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 5 | function | `safeJson` | Function |  |
| 13 | function | `runGit` | Function |  |
| 26 | function | `readGitState` | Function |  |
| 86 | function | `workspacePackageDirs` | Function |  |
| 109 | function | `toProjectId` | Function |  |
| 113 | function | `createProjectEntry` | Function |  |
| 131 | function | `readProjectIndex` | Function | Y |

#### `apps/desktop/electron/main/prompt/context-baseline-recorder.mjs` (1 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 3 | function | `createContextBaselineRecorder` | Function | Y |

#### `apps/desktop/electron/main/prompt/prompt-assembler.mjs` (7 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 30 | function | `sha256` | Function |  |
| 34 | function | `layerRank` | Function |  |
| 38 | function | `normalizeSection` | Parser/normalizer |  |
| 61 | function | `sortSections` | Function |  |
| 71 | function | `createDefaultPromptSourceRegistry` | Function | Y |
| 92 | function | `renderSystemContext` | Function | Y |
| 96 | function | `assembleSystemContext` | Function | Y |

#### `apps/desktop/electron/main/prompt/prompt-snapshot-store.mjs` (5 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 6 | function | `readJsonl` | Function |  |
| 21 | function | `appendJsonl` | Function |  |
| 26 | function | `readJsonObject` | Function |  |
| 36 | function | `pruneSnapshots` | Function |  |
| 47 | function | `createPromptSnapshotStore` | Store | Y |

#### `apps/desktop/electron/main/prompt/prompt-source-registry.mjs` (2 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 1 | function | `assertSource` | Function |  |
| 19 | function | `createPromptSourceRegistry` | Function | Y |

#### `apps/desktop/electron/main/prompt/rendering.mjs` (2 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 1 | function | `joinPromptSections` | Function | Y |
| 5 | function | `bulletList` | Function | Y |

#### `apps/desktop/electron/main/prompt/sources/attachment-source.mjs` (6 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 3 | function | `normalizeAttachment` | Parser/normalizer |  |
| 25 | function | `formatBytes` | Function |  |
| 37 | function | `formatAttachmentContext` | Function |  |
| 62 | function | `createAttachmentPromptSource` | Function | Y |
| 68 | method | `observe` | Method |  |
| 79 | method | `render` | Method |  |

#### `apps/desktop/electron/main/prompt/sources/brainstorming-source.mjs` (4 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 13 | function | `renderBrainstormingPrompt` | Function | Y |
| 58 | function | `createBrainstormingPromptSource` | Function | Y |
| 64 | method | `observe` | Method |  |
| 77 | method | `render` | Method |  |

#### `apps/desktop/electron/main/prompt/sources/context-extension-source.mjs` (6 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 10 | function | `sanitizeId` | Function |  |
| 16 | function | `normalizeLayer` | Parser/normalizer |  |
| 20 | function | `truncateContent` | Function |  |
| 38 | function | `createContextExtensionPromptSource` | Function | Y |
| 44 | method | `observe` | Method |  |
| 66 | method | `render` | Method |  |

#### `apps/desktop/electron/main/prompt/sources/continuity-source.mjs` (5 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 6 | function | `normalizeContinuityItem` | Parser/normalizer |  |
| 26 | function | `formatContinuityContext` | Function |  |
| 40 | function | `createContinuityPromptSource` | Function | Y |
| 46 | method | `observe` | Method |  |
| 56 | method | `render` | Method |  |

#### `apps/desktop/electron/main/prompt/sources/core-source.mjs` (4 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 10 | function | `renderSystemCorePrompt` | Function | Y |
| 44 | function | `createCorePromptSource` | Function | Y |
| 50 | method | `observe` | Method |  |
| 53 | method | `render` | Method |  |

#### `apps/desktop/electron/main/prompt/sources/explorer-source.mjs` (8 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 17 | function | `asString` | Function |  |
| 21 | function | `asStringArray` | Function |  |
| 32 | function | `normalizeExplorerContext` | Parser/normalizer |  |
| 52 | function | `formatBrief` | Function |  |
| 79 | function | `formatContract` | Function |  |
| 92 | function | `createExplorerPromptSource` | Function | Y |
| 98 | method | `observe` | Method |  |
| 103 | method | `render` | Method |  |

#### `apps/desktop/electron/main/prompt/sources/goal-plan-source.mjs` (7 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 24 | function | `flattenTasks` | Function |  |
| 43 | function | `normalizePlan` | Parser/normalizer |  |
| 58 | function | `formatProgress` | Function |  |
| 66 | function | `formatGoalPlans` | Function |  |
| 90 | function | `createGoalPlanPromptSource` | Function | Y |
| 96 | method | `observe` | Method |  |
| 118 | method | `render` | Method |  |

#### `apps/desktop/electron/main/prompt/sources/goal-runner-source.mjs` (15 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 38 | function | `asString` | Function |  |
| 42 | function | `sanitizeRuntimeText` | Function |  |
| 46 | function | `asStringArray` | Function |  |
| 68 | function | `summarizeCriteria` | Function |  |
| 105 | function | `summarizeTasks` | Function |  |
| 126 | function | `pickCurrentTask` | Function |  |
| 135 | function | `summarizeInspectPlan` | Function |  |
| 156 | function | `normalizePlan` | Parser/normalizer |  |
| 236 | function | `formatBudget` | Function |  |
| 247 | function | `formatFacts` | Function |  |
| 345 | function | `formatIntakeInstructions` | Function |  |
| 366 | function | `formatContract` | Function |  |
| 386 | function | `createGoalRunnerPromptSource` | Function | Y |
| 392 | method | `observe` | Method |  |
| 410 | method | `render` | Method |  |

#### `apps/desktop/electron/main/prompt/sources/mcp-host-source.mjs` (6 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 21 | function | `readHostFacts` | Function |  |
| 54 | function | `formatServerLine` | Function |  |
| 60 | function | `renderContent` | Function |  |
| 95 | function | `createMcpHostPromptSource` | Function | Y |
| 101 | method | `observe` | Method |  |
| 104 | method | `render` | Method |  |

#### `apps/desktop/electron/main/prompt/sources/mode-source.mjs` (5 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 7 | function | `normalizeMode` | Parser/normalizer |  |
| 13 | function | `normalizeEffort` | Parser/normalizer |  |
| 17 | function | `createModePromptSource` | Function | Y |
| 23 | method | `observe` | Method |  |
| 31 | method | `render` | Method |  |

#### `apps/desktop/electron/main/prompt/sources/project-instructions-source.mjs` (12 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 8 | function | `isPlainFile` | Function |  |
| 16 | function | `readProjectInstructionFile` | Function |  |
| 35 | function | `trimInstructionContent` | Function |  |
| 54 | function | `isInsideOrEqual` | Function |  |
| 59 | function | `getDataHomePath` | Function |  |
| 66 | function | `getTargetDirectory` | Function |  |
| 80 | function | `listInstructionDirs` | Function |  |
| 103 | function | `makeSectionId` | Function |  |
| 122 | function | `formatInstructionSection` | Function |  |
| 152 | function | `createProjectInstructionsPromptSource` | Function | Y |
| 219 | method | `observe` | Method |  |
| 251 | method | `render` | Method |  |

#### `apps/desktop/electron/main/prompt/sources/provider-source.mjs` (5 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 17 | function | `normalizeProvider` | Provider |  |
| 21 | function | `normalizeModel` | Parser/normalizer |  |
| 25 | function | `createProviderPromptSource` | Provider | Y |
| 31 | method | `observe` | Method |  |
| 37 | method | `render` | Method |  |

#### `apps/desktop/electron/main/prompt/sources/runtime-reminder-source.mjs` (9 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 10 | function | `sanitizeId` | Function |  |
| 16 | function | `normalizeMode` | Parser/normalizer |  |
| 23 | function | `normalizeEffort` | Parser/normalizer |  |
| 27 | function | `normalizeLayer` | Parser/normalizer |  |
| 31 | function | `fromRuntimeMode` | Function |  |
| 66 | function | `normalizeReminder` | Parser/normalizer |  |
| 82 | function | `createRuntimeReminderPromptSource` | Function | Y |
| 88 | method | `observe` | Method |  |
| 100 | method | `render` | Method |  |

#### `apps/desktop/electron/main/prompt/sources/runtime-source.mjs` (4 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 1 | function | `renderRuntimeContext` | Function | Y |
| 10 | function | `createRuntimePromptSource` | Function | Y |
| 16 | method | `observe` | Method |  |
| 21 | method | `render` | Method |  |

#### `apps/desktop/electron/main/prompt/sources/verifier-source.mjs` (10 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 9 | function | `asString` | Function |  |
| 13 | function | `asStringArray` | Function |  |
| 24 | function | `normalizeTask` | Parser/normalizer |  |
| 34 | function | `normalizeCriterion` | Parser/normalizer |  |
| 47 | function | `normalizeVerifierContext` | Parser/normalizer |  |
| 80 | function | `formatBrief` | Function |  |
| 111 | function | `formatContract` | Function |  |
| 123 | function | `createVerifierPromptSource` | Function | Y |
| 129 | method | `observe` | Method |  |
| 134 | method | `render` | Method |  |

#### `apps/desktop/electron/main/provider-adapters/anthropic-cli-identity.mjs` (1 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 13 | function | `buildClaudeCliIdentityHeaders` | Function | Y |

#### `apps/desktop/electron/main/provider-adapters/anthropic-messages-adapter.mjs` (5 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 7 | function | `parseNestedProviderErrorMessage` | Provider |  |
| 17 | function | `extractAnthropicStreamError` | Function |  |
| 30 | function | `consumeAnthropicStreamLine` | Function |  |
| 108 | function | `consumeAnthropicStream` | Function |  |
| 154 | function | `sendAnthropicMessagesStream` | Function | Y |

#### `apps/desktop/electron/main/provider-adapters/gemini-adapter.mjs` (6 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 7 | function | `extractGeminiStreamError` | Function |  |
| 16 | function | `normalizeGeminiUsage` | Parser/normalizer |  |
| 26 | function | `consumeGeminiPayload` | Function |  |
| 65 | function | `consumeGeminiStreamLine` | Function |  |
| 84 | function | `consumeGeminiStream` | Function |  |
| 119 | function | `sendGeminiStream` | Function | Y |

#### `apps/desktop/electron/main/provider-adapters/gemini-model-catalog.mjs` (3 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 110 | function | `cloneModels` | Function |  |
| 124 | function | `preferGeminiModel` | Function | Y |
| 148 | function | `listGeminiModels` | Function | Y |

#### `apps/desktop/electron/main/provider-adapters/grok-build-model-catalog.mjs` (3 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 20 | function | `buildGrokBuildHeaders` | Function | Y |
| 31 | function | `toModel` | Function |  |
| 50 | function | `listGrokBuildModels` | Function | Y |

#### `apps/desktop/electron/main/provider-adapters/models-dev-registry.mjs` (8 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 9 | function | `finiteNumber` | Function |  |
| 14 | function | `normalizeModelId` | Parser/normalizer |  |
| 18 | function | `normalizeModelsDevEntry` | Parser/normalizer |  |
| 41 | function | `buildModelsDevIndex` | Function |  |
| 60 | function | `fetchModelsDevRegistry` | Function |  |
| 97 | function | `mergeDefinedFallback` | Function |  |
| 105 | function | `enrichModelsWithRegistry` | Function |  |
| 124 | function | `resetModelsDevRegistryCacheForTests` | Function |  |

#### `apps/desktop/electron/main/provider-adapters/openai-chat-adapter.mjs` (15 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 10 | function | `shouldUsePublicOpenAIChatStream` | Function | Y |
| 18 | function | `extractTextLikeDelta` | Function |  |
| 34 | function | `extractOpenAIReasoningDelta` | Function |  |
| 51 | function | `extractOpenAIStreamError` | Function |  |
| 63 | function | `parseJsonObject` | Parser/normalizer |  |
| 74 | function | `extractProviderEnvelopeError` | Provider |  |
| 95 | function | `extractProviderTopLevelError` | Provider |  |
| 113 | function | `streamIdleTimeoutError` | Function |  |
| 119 | function | `readStreamChunk` | Function |  |
| 143 | function | `unwrapProviderStreamEnvelope` | Provider |  |
| 158 | function | `normalizeStreamToolCalls` | Parser/normalizer |  |
| 168 | function | `extractCachedPromptTokens` | Function |  |
| 176 | function | `consumeOpenAIStreamLine` | Function |  |
| 296 | function | `consumeOpenAIStream` | Function | Y |
| 375 | function | `sendOpenAIChatStream` | Function | Y |

#### `apps/desktop/electron/main/provider-adapters/openai-model-catalog.mjs` (9 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 119 | function | `isSubscriptionUsableModel` | Function |  |
| 125 | function | `isChatModel` | Function |  |
| 134 | function | `sortNewestFirst` | Function |  |
| 138 | function | `getSubscriptionModelMetadata` | Function |  |
| 151 | function | `listSubscriptionModels` | Function | Y |
| 161 | function | `isLikelyChatModel` | Function |  |
| 171 | function | `finiteCatalogNumber` | Function |  |
| 176 | function | `normalizeApiModelList` | Parser/normalizer |  |
| 266 | function | `listOpenAICompatibleModels` | Function | Y |

#### `apps/desktop/electron/main/provider-adapters/openai-responses-adapter.mjs` (5 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 20 | function | `extractCachedInputTokens` | Function |  |
| 28 | function | `consumeResponsesEvent` | Function |  |
| 117 | function | `consumeResponsesLine` | Function |  |
| 138 | function | `consumeResponsesStream` | Function |  |
| 175 | function | `sendOpenAIResponsesStream` | Function | Y |

#### `apps/desktop/electron/main/provider-adapters/qoder-local-auth.mjs` (22 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 14 | function | `createQoderAuthError` | Function |  |
| 21 | function | `nonEmpty` | Function |  |
| 26 | function | `tokenFromEnv` | Function |  |
| 34 | function | `resolveQoderConfigDir` | Function | Y |
| 41 | function | `resolveQoderInferenceEndpoint` | Function | Y |
| 61 | function | `existingFile` | Function |  |
| 70 | function | `qoderCliBinaryCandidates` | Function |  |
| 94 | function | `loadEmbeddedWasmBytes` | Function |  |
| 107 | function | `createHeap` | Function |  |
| 112 | method | `add` | Method |  |
| 122 | method | `drop` | Method |  |
| 127 | method | `take` | Method |  |
| 135 | function | `createAuthWasm` | Function |  |
| 359 | method | `credentialStorageDecrypt` | Method |  |
| 362 | method | `modelCacheDecrypt` | Method |  |
| 365 | method | `generateRuntimeAuthFields` | Method |  |
| 372 | function | `getAuthWasm` | Function |  |
| 377 | function | `decryptQoderModelCache` | Function | Y |
| 382 | function | `qoderRuntimeJson` | Function |  |
| 391 | function | `prepareQoderInferRequest` | Function | Y |
| 427 | function | `loadQoderLocalAuth` | Function | Y |
| 458 | function | `loadQoderAccessToken` | Function | Y |

#### `apps/desktop/electron/main/provider-adapters/qoder-model-catalog.mjs` (19 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 13 | function | `catalogCacheKey` | Function |  |
| 17 | function | `modelPath` | Function |  |
| 21 | function | `modelsDir` | Function |  |
| 25 | function | `defaultModelPath` | Function |  |
| 29 | function | `encryptedCatalogCandidates` | Function |  |
| 34 | function | `normalizeContextTierOption` | Parser/normalizer |  |
| 60 | function | `resolveQoderModelOptionProjection` | Function | Y |
| 92 | function | `normalizeModel` | Parser/normalizer |  |
| 116 | function | `pickQoderChatModels` | Function |  |
| 125 | function | `parseQoderModelCatalogText` | Parser/normalizer |  |
| 138 | function | `readLegacyModelCatalog` | Function |  |
| 147 | function | `readLegacyModelCatalogAsync` | Function |  |
| 156 | function | `mergeModelCatalog` | Function |  |
| 169 | function | `readEncryptedCatalog` | Function |  |
| 184 | function | `readEncryptedCatalogSync` | Function |  |
| 202 | function | `getQoderModelCatalog` | Function | Y |
| 217 | function | `getQoderModelMetadata` | Function | Y |
| 223 | function | `listQoderModels` | Function | Y |
| 247 | function | `qoderModelsPathForDebug` | Function | Y |

#### `apps/desktop/electron/main/provider-adapters/qoder-private-adapter.mjs` (25 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 12 | function | `qoderModelServerHost` | Function |  |
| 21 | function | `qoderModelServerBaseUrl` | Function | Y |
| 25 | function | `normalizeQoderPreparedEndpoint` | Parser/normalizer | Y |
| 41 | function | `normalizeQoderModel` | Parser/normalizer | Y |
| 47 | function | `qoderContentPart` | Function |  |
| 68 | function | `qoderContentText` | Function |  |
| 85 | function | `qoderToolCallArguments` | Function |  |
| 99 | function | `qoderToolCall` | Function |  |
| 116 | function | `qoderMessage` | Function |  |
| 141 | function | `qoderMessageHasText` | Function |  |
| 169 | function | `sanitizeQoderToolPairing` | Function | Y |
| 223 | function | `normalizeAssistantTextContent` | Parser/normalizer |  |
| 255 | function | `mergeConsecutiveAssistants` | Function | Y |
| 292 | function | `qoderLastUserText` | Function |  |
| 307 | function | `qoderPrimitiveType` | Function |  |
| 315 | function | `qoderCompatibleSchema` | Function |  |
| 353 | function | `qoderCompatibleTool` | Function |  |
| 368 | function | `qoderCompatibleTools` | Function |  |
| 373 | function | `buildQoderRemoteChatAsk` | Function | Y |
| 444 | function | `getQoderModelMetadataForSend` | Function |  |
| 456 | function | `qoderTurnTaskId` | Function | Y |
| 461 | function | `sendQoderPreparedStream` | Function |  |
| 612 | function | `buildQoderPrivateRequestBody` | Function | Y |
| 644 | function | `buildQoderPrivateHeaders` | Function | Y |
| 654 | function | `sendQoderPrivateStream` | Function | Y |

#### `apps/desktop/electron/main/provider-adapters/qoder-provider-expansion.mjs` (6 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 19 | function | `isQoderLocalProvider` | Provider | Y |
| 25 | function | `makeQoderModelProviderId` | Provider | Y |
| 34 | function | `parseQoderModelProviderId` | Provider | Y |
| 49 | function | `pickPrimaryModelId` | Function |  |
| 62 | function | `expandOneQoderProvider` | Provider | Y |
| 95 | function | `expandQoderProviders` | Provider | Y |

#### `apps/desktop/electron/main/provider-adapters/sse-line.mjs` (3 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 19 | function | `parseSseDataPayload` | Parser/normalizer | Y |
| 28 | function | `createSseAbortError` | Function | Y |
| 34 | function | `throwIfSseReaderAborted` | Function | Y |

#### `apps/desktop/electron/main/provider-adapters/subscription-provider-expansion.mjs` (4 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 22 | function | `isSubscriptionProvider` | Provider | Y |
| 32 | function | `pickPrimaryModelId` | Function |  |
| 46 | function | `expandOneSubscriptionProvider` | Provider | Y |
| 88 | function | `expandSubscriptionProviders` | Provider | Y |

#### `apps/desktop/electron/main/provider-adapters/tool-arg-progress.mjs` (2 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 20 | function | `tryParsePath` | Parser/normalizer |  |
| 42 | function | `emitToolArgProgress` | Function | Y |

#### `apps/desktop/electron/main/provider-channels.mjs` (13 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 209 | function | `normalizeReasoningEffortMap` | Parser/normalizer |  |
| 224 | function | `listChannelDescriptors` | Function | Y |
| 228 | function | `getChannelDescriptor` | Function | Y |
| 232 | function | `inferChannelId` | Function | Y |
| 242 | function | `legacyProviderForWire` | Provider | Y |
| 246 | function | `defaultsForChannel` | Function | Y |
| 251 | function | `normalizeHeaderName` | Parser/normalizer |  |
| 255 | function | `validateCustomHeaders` | Function | Y |
| 267 | function | `mergeHeaders` | Function |  |
| 278 | function | `geminiModelPath` | Function |  |
| 284 | function | `endpointForWire` | Function |  |
| 299 | function | `requiredHeadersFor` | Function |  |
| 325 | function | `resolveChannel` | Function | Y |

#### `apps/desktop/electron/main/provider-connectivity.mjs` (2 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 14 | function | `deriveOAuthStatus` | Function | Y |
| 30 | function | `resolveSubscriptionTestResult` | Function | Y |

#### `apps/desktop/electron/main/provider-credential-resolver.mjs` (5 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 6 | function | `createProviderCredentialError` | Provider | Y |
| 13 | function | `getProviderCredentialErrorCode` | Provider | Y |
| 17 | function | `isOAuthAuthMethod` | Function |  |
| 31 | function | `refreshExpiredOAuthProviders` | Provider | Y |
| 76 | function | `resolveProviderCredential` | Provider | Y |

#### `apps/desktop/electron/main/provider-diagnostics/provider-trace-recorder.mjs` (21 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 8 | function | `nowIso` | Function |  |
| 12 | function | `safeUrlSummary` | Function |  |
| 24 | function | `countBlocks` | Function |  |
| 37 | function | `countSystemCacheBlocks` | Function |  |
| 42 | function | `summarizeRequestBody` | Function |  |
| 71 | function | `truncate` | Function |  |
| 77 | function | `summarizeUsage` | Function |  |
| 87 | function | `summarizeAnthropicFrame` | Function |  |
| 108 | function | `summarizeOpenAIFrame` | Function |  |
| 130 | function | `summarizeOpenAIResponsesFrame` | Function |  |
| 142 | function | `todayKey` | Function |  |
| 146 | function | `traceDir` | Function |  |
| 150 | function | `appendTrace` | Function |  |
| 158 | function | `shouldPersistTrace` | Function |  |
| 167 | function | `createProviderStreamTrace` | Provider | Y |
| 212 | method | `recordResponse` | Method |  |
| 220 | method | `recordSsePayload` | Method |  |
| 247 | method | `recordIgnoredLine` | Method |  |
| 250 | method | `recordDoneMarker` | Method |  |
| 253 | method | `recordParseError` | Method |  |
| 259 | method | `finish` | Method |  |

#### `apps/desktop/electron/main/provider-encoders/gemini-encoder.mjs` (8 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 3 | function | `textPart` | Function |  |
| 8 | function | `imagePart` | Function |  |
| 16 | function | `openAIContentToGeminiParts` | Function |  |
| 29 | function | `positiveTokenLimit` | Function |  |
| 34 | function | `openAIToolsToGeminiTools` | Function |  |
| 46 | function | `parseToolArguments` | Parser/normalizer |  |
| 58 | function | `messageToGeminiContent` | Function |  |
| 94 | function | `encodeGeminiGenerateContentRequest` | Function | Y |

#### `apps/desktop/electron/main/provider-encoders/message-normalizer.mjs` (5 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 1 | function | `parseDataUrl` | Parser/normalizer |  |
| 11 | function | `normalizeOpenAIContent` | Parser/normalizer | Y |
| 27 | function | `normalizeAnthropicContent` | Parser/normalizer | Y |
| 53 | function | `normalizeOpenAIMessages` | Parser/normalizer | Y |
| 60 | function | `normalizeAnthropicMessages` | Parser/normalizer | Y |

#### `apps/desktop/electron/main/provider-encoders/request-encoder.mjs` (13 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 28 | function | `positiveTokenLimit` | Function |  |
| 33 | function | `mappedEffortValue` | Function |  |
| 43 | function | `mappedNumericEffort` | Function |  |
| 53 | function | `anthropicModelUsesEffortConfig` | Function |  |
| 59 | function | `encodeOpenAIChatRequest` | Function | Y |
| 96 | function | `isCacheableTextBlock` | Function |  |
| 111 | function | `markMessageCacheBreakpoint` | Function |  |
| 148 | function | `applyAnthropicCacheControl` | Function | Y |
| 169 | function | `parseToolArgumentsForAnthropic` | Parser/normalizer |  |
| 181 | function | `contentToAnthropicBlocks` | Function |  |
| 188 | function | `toolResultContent` | Function |  |
| 204 | function | `normalizeOpenAIToolHistoryForAnthropic` | Parser/normalizer | Y |
| 274 | function | `encodeAnthropicMessagesRequest` | Function | Y |

#### `apps/desktop/electron/main/provider-encoders/responses-encoder.mjs` (6 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 24 | function | `positiveTokenLimit` | Function |  |
| 29 | function | `mappedEffortValue` | Function |  |
| 35 | function | `textPart` | Function |  |
| 40 | function | `toInputItems` | Function |  |
| 95 | function | `toResponsesTools` | Function |  |
| 111 | function | `encodeOpenAIResponsesRequest` | Function | Y |

#### `apps/desktop/electron/main/provider-transports/grok-fetch.mjs` (1 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 5 | function | `fetchGrokWithConnectionRecovery` | Function | Y |

#### `apps/desktop/electron/main/provider-transports/recovering-fetch.mjs` (14 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 39 | function | `makeConnectTimeoutError` | Function |  |
| 47 | function | `defaultScheduleTimeout` | Function |  |
| 53 | function | `errorDetails` | Function |  |
| 63 | function | `createAbortError` | Function |  |
| 69 | function | `sleep` | Function |  |
| 82 | function | `describeConnectionFailure` | Function | Y |
| 88 | function | `isRecoverableConnectionFailure` | Function | Y |
| 93 | function | `resolveElectronNetFetch` | Function |  |
| 103 | function | `readEnvProxy` | Function |  |
| 120 | function | `resolveSystemProxy` | Function |  |
| 137 | function | `defaultDetectProxy` | Function | Y |
| 150 | function | `channelFailLabel` | Function |  |
| 154 | function | `emitConnectionRecovery` | Function |  |
| 158 | function | `fetchWithConnectionRecovery` | Function | Y |

#### `apps/desktop/electron/main/quick-chat-window.mjs` (5 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 8 | function | `clampQuickChatContentHeight` | Function | Y |
| 15 | function | `resolveQuickChatPopoverSize` | Function | Y |
| 38 | function | `resolveQuickChatBounds` | Function | Y |
| 54 | function | `resolveQuickChatExpandedBounds` | Function | Y |
| 64 | function | `createQuickChatWindowController` | Controller | Y |

#### `apps/desktop/electron/main/repetition-detector.mjs` (4 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 33 | function | `countSubstantiveChars` | Function |  |
| 41 | function | `sanitizePreview` | Function |  |
| 50 | function | `isActionableRepetitionUnit` | Function |  |
| 81 | function | `detectTailRepetition` | Function | Y |

#### `apps/desktop/electron/main/runtime-gateway/browser-control-registry.mjs` (8 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 14 | function | `conversationKey` | Function |  |
| 18 | function | `entryKey` | Function |  |
| 22 | function | `findEntryKeyByWebContentsId` | Function |  |
| 39 | function | `registerBrowserWebContents` | Function | Y |
| 81 | function | `unregisterBrowserWebContents` | Function | Y |
| 104 | function | `getActiveBrowserEntry` | Function | Y |
| 111 | function | `getActiveWebContentsId` | Function | Y |
| 118 | function | `resetBrowserControlRegistryForTests` | Function | Y |

#### `apps/desktop/electron/main/runtime-gateway/capability-provider-registry.mjs` (9 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 6 | function | `assertProvider` | Provider |  |
| 23 | function | `getRequestCapabilityId` | Function |  |
| 27 | function | `getRequestToolCallId` | Function |  |
| 31 | function | `getRequestInput` | Function |  |
| 35 | function | `getRequestMetadata` | Function |  |
| 43 | function | `toCoreRequest` | Function |  |
| 60 | function | `toCoreProvider` | Provider |  |
| 72 | function | `isCapabilityNotFound` | Function |  |
| 76 | function | `createCapabilityProviderRegistry` | Provider | Y |

#### `apps/desktop/electron/main/runtime-gateway/event-protocol.mjs` (13 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 5 | function | `createEventId` | Function | Y |
| 9 | function | `nowIso` | Function | Y |
| 13 | function | `isRuntimeGatewayDisabled` | Function | Y |
| 18 | function | `runtimeGatewayPath` | Function | Y |
| 22 | function | `toWebSocketUrl` | Function | Y |
| 34 | function | `parseGatewayMessage` | Parser/normalizer | Y |
| 48 | function | `createHelloEvent` | Function | Y |
| 66 | function | `createResumeEvent` | Function | Y |
| 79 | function | `createHeartbeatEvent` | Function | Y |
| 89 | function | `createProjectionPublishedEvent` | Function | Y |
| 101 | function | `createAckEvent` | Function | Y |
| 115 | function | `createResultEvent` | Function | Y |
| 127 | function | `createErrorEvent` | Function | Y |

#### `apps/desktop/electron/main/runtime-gateway/hook-evidence.mjs` (2 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 7 | function | `ensureHookEvidenceBase` | Function |  |
| 22 | function | `appendHookEvidence` | Function | Y |

#### `apps/desktop/electron/main/runtime-gateway/legacy-llm-local-tool-provider.mjs` (11 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 21 | function | `formatContextResult` | Function |  |
| 25 | function | `readLegacyArgs` | Function |  |
| 37 | function | `materializeShellProviderResult` | Provider |  |
| 70 | function | `executeLocalShellLegacy` | Function |  |
| 99 | function | `executeLocalFileLegacy` | Function |  |
| 123 | function | `runLegacyTool` | Function |  |
| 163 | function | `statusFromLegacyResult` | Function |  |
| 173 | function | `dataLevelForTool` | Function |  |
| 179 | function | `buildCapabilityResult` | Function |  |
| 206 | function | `createLegacyLlmLocalToolProvider` | Provider | Y |
| 252 | function | `executeLegacyLlmLocalTool` | Function | Y |

#### `apps/desktop/electron/main/runtime-gateway/local-browser-control-provider.mjs` (6 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 40 | function | `dateKey` | Function |  |
| 44 | function | `summarize` | Function |  |
| 50 | function | `hostOf` | Function |  |
| 61 | function | `createBrowserArtifactStore` | Store |  |
| 111 | function | `permissionReason` | Function |  |
| 129 | function | `createLocalBrowserControlProvider` | Provider | Y |

#### `apps/desktop/electron/main/runtime-gateway/local-file-provider.mjs` (24 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 42 | function | `previewText` | Function |  |
| 53 | function | `quoteShellPath` | Function |  |
| 57 | function | `lineCount` | Function |  |
| 62 | function | `formatContextResult` | Function |  |
| 66 | function | `hashContent` | Function |  |
| 70 | function | `resolveToolPath` | Function |  |
| 77 | function | `isInsidePath` | Function |  |
| 82 | function | `ensureWritablePathAllowed` | Function |  |
| 105 | function | `ensureReadablePathAllowed` | Function |  |
| 124 | function | `getFileSnapshot` | Function |  |
| 135 | function | `recordReadState` | Function |  |
| 152 | function | `requireReadState` | Function |  |
| 163 | function | `validateFreshReadState` | Function |  |
| 183 | function | `countOccurrences` | Function |  |
| 196 | function | `truncateText` | Function |  |
| 202 | function | `createUnifiedDiffPreview` | Function |  |
| 256 | function | `formatToolFailure` | Function |  |
| 270 | function | `materializeFileRead` | Function |  |
| 321 | function | `runFileSearch` | Function | Y |
| 420 | function | `runFileTool` | Function |  |
| 566 | function | `statusFromFileResult` | Function |  |
| 576 | function | `buildFileCapabilityResult` | Function |  |
| 605 | function | `readArgs` | Function |  |
| 617 | function | `createLocalFileProvider` | Provider | Y |

#### `apps/desktop/electron/main/runtime-gateway/local-goal-provider.mjs` (7 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 23 | function | `parseArgs` | Parser/normalizer |  |
| 41 | function | `deriveTitle` | Function |  |
| 51 | function | `nonEmptyString` | Function |  |
| 56 | function | `normalizeTasks` | Parser/normalizer |  |
| 75 | function | `summarizeTasks` | Function |  |
| 96 | function | `summarizePlan` | Function |  |
| 110 | function | `createLocalGoalProvider` | Provider | Y |

#### `apps/desktop/electron/main/runtime-gateway/local-interaction-provider.mjs` (2 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 22 | function | `parseArgs` | Parser/normalizer |  |
| 35 | function | `createLocalInteractionProvider` | Provider | Y |

#### `apps/desktop/electron/main/runtime-gateway/local-mcp-provider.mjs` (12 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 15 | function | `parseMcpCapabilityId` | Parser/normalizer |  |
| 26 | function | `safeStringify` | Function |  |
| 34 | function | `previewText` | Function |  |
| 39 | function | `getAuthContext` | Function |  |
| 50 | function | `findMcpTool` | Function |  |
| 54 | function | `normalizeRiskLevel` | Parser/normalizer |  |
| 58 | function | `mcpEffectForRisk` | Function |  |
| 64 | function | `buildCallScope` | Function |  |
| 79 | function | `isToolVisible` | Function |  |
| 85 | function | `permissionGrantFromDecision` | Function |  |
| 106 | function | `createMcpEvidence` | Function |  |
| 130 | function | `createLocalMcpProvider` | Provider | Y |

#### `apps/desktop/electron/main/runtime-gateway/local-search-aggregate-provider.mjs` (14 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 30 | function | `clamp` | Function |  |
| 35 | function | `readArgs` | Function |  |
| 51 | function | `normalizeQueries` | Parser/normalizer |  |
| 89 | function | `emitLane` | Function |  |
| 103 | function | `runLane` | Function |  |
| 180 | function | `laneShape` | Function |  |
| 193 | function | `laneEvent` | Function |  |
| 210 | function | `withTimeout` | Function |  |
| 253 | function | `runWithConcurrency` | Function |  |
| 271 | function | `aggregateMatches` | Function |  |
| 321 | function | `overallStatus` | Function |  |
| 330 | function | `buildAggregateResult` | Function |  |
| 394 | function | `buildBlockedResult` | Function |  |
| 420 | function | `createLocalSearchAggregateProvider` | Provider | Y |

#### `apps/desktop/electron/main/runtime-gateway/local-shell-provider.mjs` (17 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 16 | function | `readShellArgs` | Function |  |
| 32 | function | `nowIso` | Function |  |
| 36 | function | `createGrant` | Function |  |
| 47 | function | `createLocalEvidence` | Function |  |
| 66 | function | `previewText` | Function |  |
| 79 | function | `lineCount` | Function |  |
| 85 | function | `quoteShellPath` | Function |  |
| 89 | function | `buildSuggestedRetrieval` | Function |  |
| 102 | function | `buildLocalToolResultRef` | Function |  |
| 127 | function | `deniedResult` | Function |  |
| 152 | function | `invalidCommandResult` | Function |  |
| 182 | function | `shellRunResult` | Function |  |
| 247 | function | `shellBackgroundStartedResult` | Function |  |
| 280 | function | `shellStopResult` | Function |  |
| 308 | function | `abortedTaskOutput` | Function |  |
| 331 | function | `createLocalShellProvider` | Provider | Y |
| 522 | function | `executeLocalShell` | Function | Y |

#### `apps/desktop/electron/main/runtime-gateway/local-skill-provider.mjs` (3 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 11 | function | `extractUserInput` | Function |  |
| 37 | function | `buildInstructionsEnvelope` | Function |  |
| 135 | function | `createLocalSkillProvider` | Provider | Y |

#### `apps/desktop/electron/main/runtime-gateway/local-tool-host.mjs` (1 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 16 | function | `createLocalToolHost` | Function | Y |

#### `apps/desktop/electron/main/runtime-gateway/local-web-provider.mjs` (3 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 25 | function | `buildScope` | Function |  |
| 39 | function | `summarize` | Function |  |
| 45 | function | `createLocalWebProvider` | Provider | Y |

#### `apps/desktop/electron/main/runtime-gateway/permission-review.mjs` (10 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 9 | function | `requireString` | Function |  |
| 16 | function | `sanitizeMatch` | Function |  |
| 36 | function | `sanitizeScope` | Function |  |
| 58 | function | `sanitizeExpiresAt` | Function |  |
| 67 | function | `sanitizeShellRule` | Function |  |
| 80 | function | `toPermissionDecision` | Function |  |
| 89 | function | `hookFallbackReason` | Function |  |
| 95 | function | `mergeHookDecision` | Function |  |
| 116 | function | `resolveShellDecision` | Function |  |
| 146 | function | `createPermissionReview` | Function | Y |

#### `apps/desktop/electron/main/runtime-gateway/projection-guard.mjs` (1 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 1 | function | `createProjectionGuard` | Function | Y |

#### `apps/desktop/electron/main/runtime-gateway/result-queue.mjs` (3 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 5 | function | `readJsonArray` | Function |  |
| 15 | function | `writeJsonArray` | Function |  |
| 22 | function | `createRuntimeResultQueue` | Function | Y |

#### `apps/desktop/electron/main/runtime-gateway/shell-artifacts.mjs` (3 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 6 | function | `dateKey` | Function |  |
| 10 | function | `capArtifact` | Function |  |
| 21 | function | `createShellArtifactStore` | Store | Y |

#### `apps/desktop/electron/main/runtime-gateway/shell-classifier.mjs` (14 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 71 | function | `isInsideDirectory` | Function |  |
| 76 | function | `normalizeShellCwd` | Parser/normalizer | Y |
| 86 | function | `stripCommandPath` | Function |  |
| 90 | function | `isEnvAssignment` | Function |  |
| 94 | function | `mergeClassification` | Function |  |
| 100 | function | `tokenizeShell` | Function |  |
| 198 | function | `splitSegments` | Function |  |
| 213 | function | `classifyGit` | Function |  |
| 229 | function | `classifyPackageCommand` | Function |  |
| 240 | function | `category` | Function |  |
| 301 | function | `classifySimpleSegment` | Function |  |
| 371 | function | `classifyParsedCommand` | Parser/normalizer |  |
| 400 | function | `classifyShellCommand` | Function | Y |
| 427 | function | `compareRisk` | Function | Y |

#### `apps/desktop/electron/main/runtime-gateway/shell-env-snapshot.mjs` (5 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 34 | function | `getConfigFile` | Function |  |
| 48 | function | `createShellEnvSnapshot` | Function | Y |
| 118 | function | `buildShellSpawnArgs` | Function | Y |
| 131 | function | `cleanupSnapshot` | Function | Y |
| 137 | function | `shellQuote` | Function |  |

#### `apps/desktop/electron/main/runtime-gateway/shell-permission-rules.mjs` (10 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 8 | function | `rulesPath` | Function |  |
| 12 | function | `wildcardToRegExp` | Function |  |
| 20 | function | `normalizeRule` | Parser/normalizer |  |
| 32 | function | `isExpired` | Function |  |
| 36 | function | `matchesRule` | Function |  |
| 53 | function | `loadRules` | Function |  |
| 67 | function | `writeRules` | Function |  |
| 72 | function | `decision` | Function |  |
| 83 | function | `defaultDecision` | Function |  |
| 100 | function | `createShellPermissionRuleStore` | Store | Y |

#### `apps/desktop/electron/main/runtime-gateway/shell-redaction.mjs` (3 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 3 | function | `truncatePreview` | Function | Y |
| 9 | function | `redactShellOutput` | Function | Y |
| 18 | function | `outputRedactions` | Function | Y |

#### `apps/desktop/electron/main/runtime-gateway/shell-task-manager.mjs` (5 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 14 | function | `buildFallbackPath` | Function |  |
| 27 | function | `clampTimeout` | Function |  |
| 33 | function | `appendCapped` | Function |  |
| 39 | function | `terminateChild` | Function |  |
| 51 | function | `createShellTaskManager` | Function | Y |

#### `apps/desktop/electron/main/runtime-gateway/tool-result-factory.mjs` (3 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 4 | function | `nowIso` | Function | Y |
| 8 | function | `createPermissionGrant` | Function | Y |
| 24 | function | `createFailedClientToolResult` | Function | Y |

#### `apps/desktop/electron/main/runtime-gateway/web-artifacts.mjs` (3 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 14 | function | `dateKey` | Function |  |
| 18 | function | `capArtifact` | Function |  |
| 29 | function | `createWebArtifactStore` | Store | Y |

#### `apps/desktop/electron/main/runtime-gateway/web-fetch-engine.mjs` (8 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 24 | function | `normalizeUrl` | Parser/normalizer |  |
| 41 | function | `buildExtractionScript` | Function |  |
| 58 | function | `stripHtml` | Function |  |
| 80 | function | `capContent` | Function |  |
| 86 | function | `loadElectronBrowserWindow` | Function |  |
| 95 | function | `fetchViaBrowserWindow` | Function |  |
| 153 | function | `fetchViaHttp` | Function |  |
| 185 | function | `fetchWebPage` | Function | Y |

#### `apps/desktop/electron/main/session-store.mjs` (4 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 12 | function | `resolveLocalAccessLevel` | Function | Y |
| 24 | function | `resolveDeviceId` | Function |  |
| 44 | function | `resolveLocale` | Function |  |
| 55 | function | `createSessionStore` | Store | Y |

#### `apps/desktop/electron/main/settings-store.mjs` (1 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 17 | function | `createSettingsStore` | Store | Y |

#### `apps/desktop/electron/main/shortcut-service.mjs` (4 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 15 | function | `normalizeShortcut` | Parser/normalizer | Y |
| 24 | function | `validateShortcut` | Function | Y |
| 35 | function | `isKnownAction` | Function |  |
| 45 | function | `createShortcutService` | Function | Y |

#### `apps/desktop/electron/main/skill-store.mjs` (5 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 14 | function | `parseTar` | Parser/normalizer |  |
| 45 | function | `parseFrontmatter` | Parser/normalizer |  |
| 57 | function | `listAttachments` | Function |  |
| 83 | function | `loadSingleSkill` | Function |  |
| 137 | function | `createSkillStore` | Store | Y |

#### `apps/desktop/electron/main/subscription-quota.mjs` (19 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 15 | function | `nowIso` | Function |  |
| 19 | function | `clampPercent` | Function |  |
| 24 | function | `remainingFromUsed` | Function |  |
| 30 | function | `isoFromUnixSeconds` | Function |  |
| 39 | function | `isoFromMaybeDate` | Function |  |
| 51 | function | `windowLabel` | Function |  |
| 59 | function | `failure` | Function |  |
| 68 | function | `readJsonResponse` | Function |  |
| 80 | function | `fetchChatGptUsage` | Function | Y |
| 152 | function | `fetchGeminiQuota` | Function | Y |
| 254 | function | `readVarint` | Function |  |
| 268 | function | `decodeFixed32Float` | Function |  |
| 274 | function | `decodeFixed64Double` | Function |  |
| 280 | function | `collectProtoNumbers` | Function |  |
| 322 | function | `parseGrokGrpcWeb` | Parser/normalizer |  |
| 390 | function | `fetchGrokQuota` | Function | Y |
| 426 | function | `supportsSubscriptionQuota` | Function | Y |
| 430 | function | `fetchProviderSubscriptionQuota` | Provider | Y |
| 494 | function | `clearSubscriptionQuotaCache` | Function | Y |

#### `apps/desktop/electron/main/tools/browser-tool-definitions.mjs` (5 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 74 | function | `navigateTool` | Function |  |
| 98 | function | `clickTool` | Function |  |
| 129 | function | `typeTool` | Function |  |
| 165 | function | `screenshotTool` | Function |  |
| 188 | function | `readDomTool` | Function |  |

#### `apps/desktop/electron/main/tools/index.mjs` (7 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 42 | function | `createDefaultToolRegistry` | Function | Y |
| 48 | function | `createRuntimeToolRegistry` | Function | Y |
| 62 | function | `createRuntimeToolProjection` | Function | Y |
| 80 | function | `listToolDefinitions` | Function | Y |
| 84 | function | `getToolDefinition` | Function | Y |
| 88 | function | `buildOpenAITools` | Function | Y |
| 92 | function | `buildAnthropicTools` | Function | Y |

#### `apps/desktop/electron/main/tools/legacy-local-tool-definitions.mjs` (2 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 13 | function | `readPromptAsset` | Function |  |
| 25 | function | `legacyRuntime` | Function |  |

#### `apps/desktop/electron/main/tools/mcp-tool-definitions.mjs` (3 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 1 | function | `normalizeInputSchema` | Parser/normalizer |  |
| 6 | function | `createMcpToolDefinition` | Function |  |
| 25 | function | `createMcpToolDefinitionsFromRegistry` | Function | Y |

#### `apps/desktop/electron/main/tools/provider-tool-materializer.mjs` (7 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 7 | function | `createRuntimeToolDefinition` | Function | Y |
| 19 | function | `createRuntimeToolDefinitionsFromRegistry` | Function | Y |
| 23 | function | `createModelToolProjectionFromRegistry` | Function | Y |
| 30 | function | `buildOpenAIToolsFromModelProjection` | Function | Y |
| 34 | function | `buildAnthropicToolsFromModelProjection` | Function | Y |
| 38 | function | `buildOpenAIToolsFromRegistry` | Function | Y |
| 42 | function | `buildAnthropicToolsFromRegistry` | Function | Y |

#### `apps/desktop/electron/main/tools/runtime-projection-tool-materializer.mjs` (13 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 9 | function | `nowIso` | Function |  |
| 13 | function | `executorCapabilityId` | Function |  |
| 17 | function | `sourceForCapability` | Function |  |
| 25 | function | `riskForTool` | Function |  |
| 51 | function | `dataLevelForTool` | Function |  |
| 58 | function | `evidencePolicyForTool` | Function |  |
| 77 | function | `manifestFromTool` | Function |  |
| 105 | function | `createRuntimeProjectionFromToolRegistry` | Function | Y |
| 121 | function | `isAvailable` | Function |  |
| 125 | function | `createProjectedToolRegistry` | Function | Y |
| 135 | function | `createModelToolProjectionFromRuntimeProjection` | Function | Y |
| 152 | function | `buildOpenAIToolsFromRuntimeProjection` | Function | Y |
| 158 | function | `buildAnthropicToolsFromRuntimeProjection` | Function | Y |

#### `apps/desktop/electron/main/tools/search-tool-definitions.mjs` (1 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 9 | function | `readPromptAsset` | Function |  |

#### `apps/desktop/electron/main/tools/tool-registry.mjs` (2 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 1 | function | `assertToolDefinition` | Function |  |
| 16 | function | `createToolRegistry` | Function | Y |

#### `apps/desktop/electron/main/usage-stats.mjs` (13 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 14 | function | `finiteNumber` | Function |  |
| 19 | function | `optionalPrice` | Function |  |
| 25 | function | `emptyTokenBucket` | Function | Y |
| 35 | function | `readLifetimeUsage` | Function | Y |
| 52 | function | `addTokenBuckets` | Function | Y |
| 67 | function | `estimateUsageCostUsd` | Function | Y |
| 88 | function | `providerLookupKey` | Function |  |
| 93 | function | `providerGroupKey` | Function |  |
| 98 | function | `buildProviderIndex` | Provider |  |
| 108 | function | `resolveConversationPricing` | Function |  |
| 142 | function | `sortGroupRows` | Function |  |
| 155 | function | `buildUsageStatsSnapshot` | Function | Y |
| 278 | function | `collectUsageStats` | Function | Y |

#### `apps/desktop/electron/main/window-routing.mjs` (2 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 2 | function | `getMainWindowWebContents` | Function | Y |
| 14 | function | `getOAuthWindowWebContents` | Function | Y |

#### `apps/desktop/electron/preload/preload.cjs` (2 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 3 | function | `readInitialSettings` | Function |  |
| 13 | handler | `peerAgent` | Preload bridge `peerAgent` |  |

#### `apps/desktop/renderer/src/App.tsx` (11 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 23 | function | `isEditableTarget` | Function |  |
| 30 | function | `eventMatchesAccelerator` | Function |  |
| 52 | type | `AppPage` | Type/interface |  |
| 53 | type | `ConversationStatus` | Type/interface |  |
| 54 | type | `ConversationView` | Type/interface |  |
| 56 | type | `ConversationMeta` | Type/interface |  |
| 67 | function | `readSystemInstructions` | Function |  |
| 71 | function | `readReplyLanguage` | Function |  |
| 75 | function | `readGitBranchPrefix` | Function |  |
| 79 | component | `App` | React Component | Y |
| 86 | component | `MainApp` | React Component |  |

#### `apps/desktop/renderer/src/app/components/ArchivedConversationsPanel.tsx` (3 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 6 | type | `ArchivedConversationMeta` | Type/interface |  |
| 14 | function | `formatArchivedDate` | Function |  |
| 25 | component | `ArchivedConversationsPanel` | React Component | Y |

#### `apps/desktop/renderer/src/app/components/BrandStartupLoader.tsx` (4 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 11 | type | `ThemeMode` | Type/interface |  |
| 13 | function | `readThemeMode` | Function |  |
| 18 | function | `preloadSidebarLogos` | Function |  |
| 31 | component | `BrandStartupLoader` | React Component | Y |

#### `apps/desktop/renderer/src/app/components/BrandWordmark.tsx` (1 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 1 | component | `BrandWordmark` | React Component | Y |

#### `apps/desktop/renderer/src/app/components/CapabilitiesPanel.tsx` (1 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 15 | component | `CapabilitiesPanel` | React Component | Y |

#### `apps/desktop/renderer/src/app/components/CapabilityInventory.tsx` (1 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 4 | component | `CapabilityInventory` | React Component | Y |

#### `apps/desktop/renderer/src/app/components/CascadingMenu.tsx` (6 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 6 | type | `CascadingMenuGroup` | Type/interface | Y |
| 14 | type | `CascadingMenuItem` | Type/interface | Y |
| 21 | type | `MenuCoords` | Type/interface |  |
| 30 | type | `SubmenuCoords` | Type/interface |  |
| 36 | type | `FocusZone` | Type/interface |  |
| 44 | component | `CascadingMenu` | React Component | Y |

#### `apps/desktop/renderer/src/app/components/ConfiguredModelRow.tsx` (2 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 5 | function | `compactTokens` | Function |  |
| 13 | component | `ConfiguredModelRow` | React Component | Y |

#### `apps/desktop/renderer/src/app/components/ConfirmProvider.tsx` (5 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 18 | type | `ConfirmTone` | Type/interface | Y |
| 20 | type | `ConfirmOptions` | Type/interface | Y |
| 33 | type | `ConfirmContextValue` | Type/interface |  |
| 41 | hook | `useConfirm` | React Hook | Y |
| 47 | component | `ConfirmProvider` | React Component | Y |

#### `apps/desktop/renderer/src/app/components/Drawer.tsx` (1 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 4 | component | `Drawer` | React Component | Y |

#### `apps/desktop/renderer/src/app/components/Dropdown.tsx` (3 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 5 | type | `DropdownOption` | Type/interface | Y |
| 11 | type | `MenuCoords` | Type/interface |  |
| 25 | component | `Dropdown` | React Component | Y |

#### `apps/desktop/renderer/src/app/components/FallbackComposer.tsx` (1 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 5 | component | `FallbackComposer` | React Component | Y |

#### `apps/desktop/renderer/src/app/components/FallbackRuntimeView.tsx` (2 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 10 | type | `FallbackRuntimePage` | Type/interface | Y |
| 12 | component | `FallbackRuntimeView` | React Component | Y |

#### `apps/desktop/renderer/src/app/components/GeneralPanel.tsx` (3 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 28 | function | `readReplyLanguage` | Function |  |
| 33 | type | `GeneralPanelProps` | Type/interface | Y |
| 40 | component | `GeneralPanel` | React Component | Y |

#### `apps/desktop/renderer/src/app/components/GitPanel.tsx` (2 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 10 | type | `GitPanelProps` | Type/interface | Y |
| 23 | component | `GitPanel` | React Component | Y |

#### `apps/desktop/renderer/src/app/components/LlmSettingsPanel.tsx` (15 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 39 | type | `PendingProviderDraft` | Provider |  |
| 48 | type | `FormState` | Type/interface |  |
| 154 | function | `descriptorFor` | Function |  |
| 175 | function | `isLocalCliMethod` | Function |  |
| 179 | function | `defaultAuthMethod` | Function |  |
| 187 | function | `oauthLabel` | Function |  |
| 195 | function | `wireLabel` | Function |  |
| 213 | function | `reasoningStyleLabel` | Function |  |
| 233 | function | `formatModelTokenLimit` | Function |  |
| 240 | function | `formatCustomHeaders` | Function |  |
| 244 | function | `parseCustomHeaders` | Parser/normalizer |  |
| 261 | function | `validateForm` | Function |  |
| 305 | function | `emptyForm` | Function |  |
| 335 | function | `friendlyTestError` | Function |  |
| 389 | component | `LlmSettingsPanel` | React Component | Y |

#### `apps/desktop/renderer/src/app/components/McpSettingsPanel.tsx` (18 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 9 | type | `McpTransportKind` | Type/interface |  |
| 10 | type | `McpAuthMode` | Type/interface |  |
| 16 | type | `McpToolView` | Type/interface |  |
| 24 | type | `McpResourceView` | Type/interface |  |
| 30 | type | `McpPromptView` | Type/interface |  |
| 35 | type | `McpOAuthConfigView` | Type/interface |  |
| 45 | type | `McpCredentialView` | Type/interface |  |
| 57 | type | `McpServerView` | Type/interface |  |
| 81 | function | `serverIdOf` | Function |  |
| 85 | function | `labelForServer` | Function |  |
| 89 | function | `toolNameOf` | Function |  |
| 93 | function | `transportLabel` | Function |  |
| 99 | function | `authLabel` | Function |  |
| 111 | function | `isAuthRequiredMessage` | Function |  |
| 128 | function | `endpointForServer` | Function |  |
| 133 | function | `formatDateTime` | Function |  |
| 140 | type | `McpSettingsPanelProps` | Type/interface |  |
| 147 | component | `McpSettingsPanel` | React Component | Y |

#### `apps/desktop/renderer/src/app/components/ModelCatalogDialog.tsx` (3 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 13 | function | `compactTokens` | Function |  |
| 20 | function | `sourceLabel` | Function |  |
| 27 | component | `ModelCatalogDialog` | React Component | Y |

#### `apps/desktop/renderer/src/app/components/ModelSettingsDialog.tsx` (3 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 18 | type | `ModelSettingsForm` | Type/interface |  |
| 38 | function | `sourceLabel` | Function |  |
| 47 | component | `ModelSettingsDialog` | React Component | Y |

#### `apps/desktop/renderer/src/app/components/Overlay.tsx` (1 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 21 | component | `Overlay` | React Component | Y |

#### `apps/desktop/renderer/src/app/components/QuickChatPopover.tsx` (3 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 13 | type | `InlineQuickChatPopoverState` | Type/interface | Y |
| 17 | type | `QuickChatPopoverProps` | Type/interface |  |
| 28 | component | `QuickChatPopover` | React Component | Y |

#### `apps/desktop/renderer/src/app/components/QuickChatTaskCard.tsx` (1 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 5 | component | `QuickChatTaskCard` | React Component | Y |

#### `apps/desktop/renderer/src/app/components/QuickChatWindow.tsx` (3 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 40 | type | `Workspace` | Type/interface |  |
| 42 | function | `id` | Function |  |
| 46 | component | `QuickChatWindow` | React Component | Y |

#### `apps/desktop/renderer/src/app/components/ReleaseNotesView.tsx` (3 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 15 | component | `ReleaseNotesView` | React Component | Y |
| 24 | function | `renderNodes` | Function |  |
| 28 | function | `renderNode` | Function |  |

#### `apps/desktop/renderer/src/app/components/RuntimeFacts.tsx` (2 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 5 | component | `FactCard` | React Component |  |
| 23 | component | `RuntimeFacts` | React Component | Y |

#### `apps/desktop/renderer/src/app/components/SettingsPage.tsx` (3 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 15 | type | `SettingsSection` | Type/interface |  |
| 16 | type | `SettingsGroup` | Type/interface |  |
| 30 | component | `SettingsPage` | React Component | Y |

#### `apps/desktop/renderer/src/app/components/ShortcutsPanel.tsx` (8 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 4 | type | `ShortcutAction` | Type/interface |  |
| 6 | type | `ShortcutStatus` | Type/interface |  |
| 14 | type | `ShortcutStatusMap` | Type/interface |  |
| 23 | function | `displayShortcut` | Function | Y |
| 45 | function | `acceleratorFromEvent` | Function |  |
| 66 | type | `ShortcutRowProps` | Type/interface |  |
| 79 | component | `ShortcutRow` | React Component |  |
| 146 | component | `ShortcutsPanel` | React Component | Y |

#### `apps/desktop/renderer/src/app/components/SystemInstructionsPanel.tsx` (2 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 5 | function | `readSystemInstructions` | Function |  |
| 17 | component | `SystemInstructionsPanel` | React Component | Y |

#### `apps/desktop/renderer/src/app/components/Tooltip.tsx` (2 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 15 | type | `TooltipPlacement` | Type/interface |  |
| 25 | component | `Tooltip` | React Component | Y |

#### `apps/desktop/renderer/src/app/components/UpdateModal.tsx` (1 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 24 | component | `UpdateModal` | React Component | Y |

#### `apps/desktop/renderer/src/app/components/UpdateToast.tsx` (1 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 17 | component | `UpdateToast` | React Component | Y |

#### `apps/desktop/renderer/src/app/components/UpdatesPanel.tsx` (1 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 16 | component | `UpdatesPanel` | React Component | Y |

#### `apps/desktop/renderer/src/app/components/VersionBadge.tsx` (1 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 25 | component | `VersionBadge` | React Component | Y |

#### `apps/desktop/renderer/src/app/components/cascadingMenuNav.ts` (3 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 4 | type | `CascadingNavItem` | Type/interface | Y |
| 9 | function | `firstEnabledIndex` | Function | Y |
| 16 | function | `stepEnabledIndex` | Function | Y |

#### `apps/desktop/renderer/src/app/components/llmModelConfiguration.ts` (19 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 11 | type | `ModelMetadataSource` | Type/interface | Y |
| 13 | type | `ModelCatalogEntry` | Type/interface | Y |
| 18 | function | `contextWindowDefinition` | Function |  |
| 24 | function | `selectedModelContextWindow` | Function | Y |
| 34 | function | `modelContextWindowRange` | Function | Y |
| 56 | function | `modelMetadataPatch` | Function | Y |
| 81 | function | `metadataSourceFromList` | Function | Y |
| 92 | type | `ModelImportPatch` | Type/interface | Y |
| 105 | function | `buildModelImportPatches` | Function | Y |
| 124 | function | `buildModelCatalog` | Function | Y |
| 138 | type | `ModelSelectionChanges` | Type/interface | Y |
| 144 | function | `metadataValueEqual` | Function |  |
| 151 | function | `modelCatalogMetadataDiffers` | Function | Y |
| 174 | function | `calculateModelSelectionChanges` | Function | Y |
| 195 | function | `formatReasoningEffortMap` | Function | Y |
| 199 | function | `parseReasoningEffortMap` | Parser/normalizer | Y |
| 236 | function | `filterModelCatalog` | Function | Y |
| 245 | function | `updateModelOptionSelection` | Function | Y |
| 258 | function | `modelMetadataCompletion` | Function | Y |

#### `apps/desktop/renderer/src/app/components/llmSubscriptionAuth.ts` (3 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 5 | function | `availableOAuthMethods` | Function | Y |
| 9 | function | `subscriptionLoginLabel` | Function | Y |
| 15 | function | `shouldOpenOAuthModelCatalog` | Function | Y |

#### `apps/desktop/renderer/src/app/components/llmSubscriptionQuota.ts` (4 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 8 | function | `isOAuthMethod` | Function | Y |
| 13 | function | `formatResetAt` | Function | Y |
| 30 | function | `formatQuotaLine` | Function | Y |
| 55 | function | `formatQuotaTooltipLine` | Function | Y |

#### `apps/desktop/renderer/src/app/components/quickChatPopoverLayout.ts` (2 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 16 | function | `resolveQuickChatPopoverVisualSize` | Function | Y |
| 45 | function | `resolveQuickChatPopoverPosition` | Function | Y |

#### `apps/desktop/renderer/src/app/components/releaseNotesHtml.ts` (7 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 16 | type | `ReleaseNotesNode` | Type/interface | Y |
| 20 | type | `ReleaseNotesTag` | Type/interface | Y |
| 77 | function | `decodeEntities` | Function | Y |
| 96 | function | `safeHref` | Function |  |
| 107 | function | `parseReleaseNotesHtml` | Parser/normalizer | Y |
| 174 | function | `normalize` | Parser/normalizer |  |
| 190 | function | `nodesToPlainText` | Function | Y |

#### `apps/desktop/renderer/src/app/gitBranchPrefix.ts` (2 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 21 | function | `resolveGitBranchPrefix` | Function | Y |
| 28 | function | `readGitBranchPrefixFromSettings` | Function | Y |

#### `apps/desktop/renderer/src/app/hooks/useMotionPresence.ts` (4 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 22 | type | `MotionPresenceOptions` | Type/interface | Y |
| 32 | type | `MotionPresenceApi` | Type/interface | Y |
| 48 | function | `prefersReducedMotion` | Function | Y |
| 55 | hook | `useMotionPresence` | React Hook | Y |

#### `apps/desktop/renderer/src/app/runtimeIdentity.ts` (3 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 1 | type | `RuntimeVariant` | Type/interface | Y |
| 3 | type | `RuntimeIdentity` | Type/interface | Y |
| 10 | function | `getRuntimeIdentity` | Function | Y |

#### `apps/desktop/renderer/src/app/runtimeLabels.ts` (1 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 3 | function | `sessionStatusKey` | Function | Y |

#### `apps/desktop/renderer/src/app/state/quickChatSubmission.ts` (2 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 1 | function | `shouldRefreshQuickChatConversationList` | Function | Y |
| 8 | function | `runQuickChatSubmission` | Function | Y |

#### `apps/desktop/renderer/src/app/state/useBrandStartupMinHold.ts` (2 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 9 | function | `prefersReducedMotion` | Function |  |
| 24 | hook | `useBrandStartupMinHold` | React Hook | Y |

#### `apps/desktop/renderer/src/app/state/useDesktopBootstrap.ts` (3 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 13 | type | `DesktopStartupSnapshot` | Type/interface | Y |
| 31 | type | `DesktopBootstrapState` | Type/interface | Y |
| 41 | hook | `useDesktopBootstrap` | React Hook | Y |

#### `apps/desktop/renderer/src/app/state/useUpdater.ts` (2 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 17 | type | `UseUpdaterResult` | Type/interface | Y |
| 38 | hook | `useUpdater` | React Hook | Y |

#### `apps/desktop/renderer/src/appearance/AppearancePanel.tsx` (1 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 26 | component | `AppearancePanel` | React Component | Y |

#### `apps/desktop/renderer/src/appearance/AppearanceProvider.tsx` (6 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 26 | type | `AppearanceContextValue` | Type/interface |  |
| 46 | function | `readSystemScheme` | Function |  |
| 51 | function | `loadSettings` | Function |  |
| 84 | function | `saveSettings` | Function |  |
| 90 | component | `AppearanceProvider` | React Component | Y |
| 186 | hook | `useAppearance` | React Hook | Y |

#### `apps/desktop/renderer/src/appearance/AppearanceSlider.tsx` (1 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 13 | component | `AppearanceSlider` | React Component | Y |

#### `apps/desktop/renderer/src/appearance/PaletteSelect.tsx` (1 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 16 | component | `PaletteSelect` | React Component | Y |

#### `apps/desktop/renderer/src/appearance/appearanceTypes.ts` (9 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 15 | type | `AppearanceMode` | Type/interface | Y |
| 17 | type | `AppearanceScheme` | Type/interface | Y |
| 26 | type | `AppearanceDensity` | Type/interface | Y |
| 31 | type | `AppearanceFontScale` | Type/interface | Y |
| 36 | type | `AppearanceCodeFontSize` | Type/interface | Y |
| 44 | type | `DiffMarkerMode` | Type/interface | Y |
| 49 | type | `CustomSchemeColors` | Type/interface | Y |
| 56 | type | `CustomColors` | Type/interface | Y |
| 61 | type | `AppearanceSettings` | Type/interface | Y |

#### `apps/desktop/renderer/src/appearance/paletteRegistry.ts` (5 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 18 | type | `AppearanceScheme` | Type/interface | Y |
| 21 | type | `SwatchEntry` | Type/interface | Y |
| 27 | type | `PaletteDefinition` | Type/interface | Y |
| 114 | type | `AppearancePalette` | Type/interface | Y |
| 133 | function | `sanitizePalette` | Function | Y |

#### `apps/desktop/renderer/src/appearance/themePresets.ts` (1 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 30 | type | `ThemeSnapshot` | Type/interface | Y |

#### `apps/desktop/renderer/src/appearance/themeTokens.ts` (10 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 24 | function | `isMode` | Function |  |
| 28 | function | `isDensity` | Function |  |
| 32 | function | `isFontScale` | Function |  |
| 36 | function | `isDiffMarkerMode` | Function |  |
| 42 | function | `isHexColor` | Function |  |
| 46 | function | `sanitizeSchemeColors` | Function |  |
| 58 | function | `sanitizeCustomColors` | Function |  |
| 67 | function | `sanitizeCodeFontSize` | Function |  |
| 74 | function | `sanitizeSettings` | Function | Y |
| 98 | function | `applyAppearance` | Function | Y |

#### `apps/desktop/renderer/src/capabilities/capabilityCatalog.ts` (8 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 11 | function | `localizeCapability` | Function |  |
| 15 | function | `sourceLabel` | Function |  |
| 24 | function | `riskTone` | Function |  |
| 30 | function | `tabForCapability` | Function |  |
| 35 | function | `manifestToItem` | Function |  |
| 65 | function | `buildCapabilityWorkbenchItems` | Function | Y |
| 72 | function | `countCapabilityWorkbenchItems` | Function | Y |
| 79 | function | `groupCapabilityItems` | Function | Y |

#### `apps/desktop/renderer/src/capabilities/components/CapabilityCard.tsx` (1 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 3 | component | `CapabilityCard` | React Component | Y |

#### `apps/desktop/renderer/src/capabilities/components/CapabilityDetailPanel.tsx` (2 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 4 | component | `DetailList` | React Component |  |
| 18 | component | `CapabilityDetailPanel` | React Component | Y |

#### `apps/desktop/renderer/src/capabilities/components/CapabilityEmptyState.tsx` (1 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 14 | component | `CapabilityEmptyState` | React Component | Y |

#### `apps/desktop/renderer/src/capabilities/components/CapabilitySection.tsx` (1 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 4 | component | `CapabilitySection` | React Component | Y |

#### `apps/desktop/renderer/src/capabilities/components/CapabilityTabs.tsx` (1 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 8 | component | `CapabilityTabs` | React Component | Y |

#### `apps/desktop/renderer/src/capabilities/components/CapabilityWorkbench.tsx` (2 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 22 | function | `firstItemForTab` | Function |  |
| 26 | component | `CapabilityWorkbench` | React Component | Y |

#### `apps/desktop/renderer/src/capabilities/components/SkillUploadDialog.tsx` (1 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 4 | component | `SkillUploadDialog` | React Component | Y |

#### `apps/desktop/renderer/src/capabilities/components/SkillsInstalledPanel.tsx` (3 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 5 | component | `SkillAvatar` | React Component |  |
| 10 | component | `SkillToggle` | React Component |  |
| 30 | component | `SkillsInstalledPanel` | React Component | Y |

#### `apps/desktop/renderer/src/capabilities/components/SkillsPanel.tsx` (1 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 4 | component | `SkillsPanel` | React Component | Y |

#### `apps/desktop/renderer/src/capabilities/types.ts` (8 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 3 | type | `CapabilityWorkbenchTab` | Type/interface | Y |
| 5 | type | `CapabilityLocality` | Type/interface | Y |
| 7 | type | `CapabilityStatus` | Type/interface | Y |
| 9 | type | `CapabilityTone` | Type/interface | Y |
| 11 | type | `CapabilityWorkbenchItem` | Type/interface | Y |
| 34 | type | `CapabilityWorkbenchCounts` | Type/interface | Y |
| 39 | type | `CapabilityWorkbenchSection` | Type/interface | Y |
| 45 | function | `healthToStatus` | Function | Y |

#### `apps/desktop/renderer/src/chat/components/ChatSurface.tsx` (9 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 127 | hook | `useStableCallback` | React Hook |  |
| 135 | function | `summarizeUserMessageForContext` | Function |  |
| 149 | function | `findCurrentTurnIdForScroll` | Function |  |
| 174 | type | `TokenUsageState` | Type/interface |  |
| 181 | type | `ThreadScrollSnapshot` | Type/interface |  |
| 189 | function | `nextId` | Function |  |
| 193 | function | `usageFromLifetime` | Function |  |
| 207 | function | `loadConversationMessages` | Function |  |
| 294 | component | `ChatSurface` | React Component | Y |

#### `apps/desktop/renderer/src/chat/components/ComposerDraftControls.tsx` (1 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 10 | type | `SlashCommand` | Type/interface |  |

#### `apps/desktop/renderer/src/chat/components/ComposerTokenUsageDisplay.tsx` (3 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 7 | type | `TokenUsageDisplayProps` | Type/interface |  |
| 9 | type | `ComposerTokenUsageDisplayProps` | Type/interface |  |
| 22 | component | `ComposerTokenUsageDisplay` | React Component | Y |

#### `apps/desktop/renderer/src/chat/components/ConversationSearchPalette.tsx` (11 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 6 | type | `SearchConversationHit` | Type/interface | Y |
| 14 | type | `PaletteItem` | Type/interface |  |
| 18 | type | `ConversationSearchPaletteProps` | Type/interface |  |
| 27 | function | `workspaceShortName` | Function |  |
| 34 | function | `normalizeSearchQuery` | Parser/normalizer |  |
| 39 | function | `rankConversationMatch` | Function |  |
| 51 | function | `recencyKey` | Function |  |
| 55 | function | `filterAndRankConversations` | Function |  |
| 82 | function | `loadActiveConversationsForSearch` | Function |  |
| 106 | function | `highlightTitle` | Function |  |
| 125 | component | `ConversationSearchPalette` | React Component | Y |

#### `apps/desktop/renderer/src/chat/components/GoalPlanPanel.tsx` (43 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 24 | function | `normalizeConversationId` | Parser/normalizer |  |
| 30 | type | `GoalChangePayload` | Type/interface |  |
| 39 | function | `shouldRefreshForConversation` | Function |  |
| 57 | function | `patchPlanRunner` | Function |  |
| 80 | function | `isIntakePlan` | Function |  |
| 84 | function | `isDisplayableGoalPlan` | Function |  |
| 99 | type | `GoalPlanPanelProps` | Type/interface |  |
| 134 | function | `statusLabel` | Function |  |
| 152 | function | `statusClass` | Function |  |
| 156 | function | `planExecutionStatus` | Function |  |
| 178 | function | `derivePlanTitle` | Function |  |
| 190 | function | `planStatusLabel` | Function |  |
| 216 | function | `safeProgress` | Function |  |
| 220 | function | `explorerStatusLabel` | Function |  |
| 238 | function | `verifierStatusLabel` | Function |  |
| 256 | function | `verifierTargetLabel` | Function |  |
| 266 | function | `runnerPhaseLabel` | Function |  |
| 312 | function | `manualDodCriteria` | Function |  |
| 323 | function | `latestManualDodConfirmation` | Function |  |
| 339 | function | `buildManualDodConfirmation` | Function |  |
| 373 | function | `runEventLabel` | Function |  |
| 425 | function | `runEventTone` | Function |  |
| 435 | function | `formatRunEventTime` | Function |  |
| 441 | function | `payloadString` | Function |  |
| 449 | function | `compactMeta` | Function |  |
| 486 | function | `codedValueLabel` | Function |  |
| 499 | type | `RunEventSummaryBuilder` | Type/interface |  |
| 611 | function | `runEventSummary` | Function |  |
| 624 | function | `runEventMetaItems` | Function |  |
| 643 | function | `criterionKindLabel` | Function |  |
| 661 | component | `GoalContractSection` | React Component |  |
| 720 | component | `PlanProjectionSection` | React Component |  |
| 805 | component | `RunTraceItem` | React Component |  |
| 830 | component | `RunTraceSection` | React Component |  |
| 898 | component | `TaskNode` | React Component |  |
| 1028 | component | `RunnerSection` | React Component |  |
| 1233 | component | `VerifierItem` | React Component |  |
| 1270 | component | `ExplorerItem` | React Component |  |
| 1308 | type | `CompactApprovalBarProps` | Type/interface |  |
| 1317 | component | `CompactApprovalBar` | React Component |  |
| 1351 | type | `PlanCardProps` | Type/interface |  |
| 1370 | component | `PlanCard` | React Component |  |
| 1504 | component | `GoalPlanPanel` | React Component | Y |

#### `apps/desktop/renderer/src/chat/components/MessageQueue.tsx` (1 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 6 | component | `MessageQueue` | React Component | Y |

#### `apps/desktop/renderer/src/chat/components/Sidebar.tsx` (7 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 17 | type | `ConversationView` | Type/interface |  |
| 19 | type | `ConversationMeta` | Type/interface |  |
| 30 | type | `WorkspaceEntry` | Type/interface |  |
| 36 | type | `WorkspaceInfo` | Type/interface |  |
| 45 | function | `formatRelativeTime` | Function |  |
| 66 | component | `PinIcon` | React Component |  |
| 100 | component | `Sidebar` | React Component | Y |

#### `apps/desktop/renderer/src/chat/components/goal/ChatGoalApprovalCard.tsx` (1 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 21 | component | `ChatGoalApprovalCard` | React Component | Y |

#### `apps/desktop/renderer/src/chat/components/goal/goalPlanExpansion.ts` (3 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 10 | function | `shouldDefaultExpandGoalPlan` | Function | Y |
| 17 | function | `hasPendingGoalApproval` | Function | Y |
| 23 | function | `selectPrimaryGoalPlan` | Function | Y |

#### `apps/desktop/renderer/src/chat/components/goal/goalPlanNextActions.ts` (4 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 3 | type | `GoalPlanNextAction` | Type/interface | Y |
| 5 | type | `GoalPlanNextStep` | Type/interface | Y |
| 16 | function | `getGoalPlanNextStep` | Function | Y |
| 22 | function | `goalPlanNextStepCopy` | Function | Y |

#### `apps/desktop/renderer/src/chat/components/goal/goalPlanTree.ts` (3 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 3 | type | `GoalPlanTreeRow` | Type/interface | Y |
| 9 | function | `buildGoalPlanTreeRows` | Function | Y |
| 39 | function | `goalPlanTreeDepth` | Function | Y |

#### `apps/desktop/renderer/src/chat/components/goal/useAwaitingGoalPlans.ts` (4 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 14 | function | `normalizeConversationId` | Parser/normalizer |  |
| 20 | function | `shouldRefreshForConversation` | Function |  |
| 36 | hook | `useAwaitingGoalPlans` | React Hook | Y |
| 123 | hook | `useAwaitingGoalPlanCounts` | React Hook | Y |

#### `apps/desktop/renderer/src/chat/components/goal/useGoalPlanApproval.ts` (5 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 17 | type | `GoalPlanDecision` | Type/interface | Y |
| 19 | type | `UseGoalPlanApprovalOptions` | Type/interface | Y |
| 30 | type | `UseGoalPlanApprovalResult` | Type/interface | Y |
| 43 | function | `buildApproval` | Function |  |
| 51 | hook | `useGoalPlanApproval` | React Hook | Y |

#### `apps/desktop/renderer/src/chat/components/markdown/InlineMarkdown.tsx` (8 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 11 | function | `findSingleStar` | Function |  |
| 20 | function | `tokenTone` | Function |  |
| 29 | function | `findFontToken` | Function |  |
| 43 | function | `parseFilePathToken` | Parser/normalizer | Y |
| 80 | function | `resolveAbsolutePath` | Function |  |
| 97 | component | `FilePathCode` | React Component |  |
| 183 | function | `renderInlineMarkdown` | Function |  |
| 245 | function | `renderInlineLines` | Function | Y |

#### `apps/desktop/renderer/src/chat/components/markdown/MarkdownMessage.tsx` (3 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 8 | component | `HistoricalPreviewBlock` | React Component |  |
| 58 | component | `CopyableCodeBlock` | React Component |  |
| 97 | component | `MarkdownMessageImpl` | React Component |  |

#### `apps/desktop/renderer/src/chat/components/markdown/markdownFenceSanitizer.ts` (7 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 12 | function | `countCjk` | Function |  |
| 16 | function | `hasCodeSignals` | Function |  |
| 25 | function | `looksLikeProseNotCode` | Function | Y |
| 43 | function | `isFenceOpenLine` | Function |  |
| 47 | function | `isFenceCloseLine` | Function |  |
| 55 | function | `fixUnbalancedPathBacktick` | Function | Y |
| 84 | function | `sanitizeMarkdownFences` | Function | Y |

#### `apps/desktop/renderer/src/chat/components/markdown/markdownParser.ts` (8 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 7 | function | `parseListLine` | Parser/normalizer |  |
| 15 | function | `splitTableRow` | Function |  |
| 43 | function | `isTableDelimiterLine` | Function |  |
| 48 | function | `isTableStart` | Function |  |
| 54 | function | `normalizeTableRow` | Parser/normalizer |  |
| 58 | function | `looksLikeTableRow` | Function |  |
| 62 | function | `isMarkdownBlockStart` | Function |  |
| 74 | function | `parseMarkdownBlocks` | Parser/normalizer | Y |

#### `apps/desktop/renderer/src/chat/components/markdown/markdownTypes.ts` (8 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 1 | type | `MarkdownParagraphBlock` | Type/interface | Y |
| 6 | type | `MarkdownHeadingBlock` | Type/interface | Y |
| 12 | type | `MarkdownListBlock` | Type/interface | Y |
| 19 | type | `MarkdownCodeBlock` | Type/interface | Y |
| 25 | type | `MarkdownQuoteBlock` | Type/interface | Y |
| 30 | type | `MarkdownRuleBlock` | Type/interface | Y |
| 34 | type | `MarkdownTableBlock` | Type/interface | Y |
| 40 | type | `MarkdownBlock` | Type/interface | Y |

#### `apps/desktop/renderer/src/chat/components/thread/AssistantContent.tsx` (16 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 25 | function | `toolProgressLabel` | Function |  |
| 49 | component | `ToolProgressInline` | React Component | Y |
| 60 | component | `LiveToolProgress` | React Component |  |
| 74 | hook | `useAutoCollapsingExpanded` | React Hook |  |
| 90 | function | `buildProcessingSummary` | Function |  |
| 109 | component | `AssistantContentImpl` | React Component |  |
| 220 | type | `ProcessingGroup` | Type/interface |  |
| 222 | function | `isProcessingGroup` | Function |  |
| 226 | component | `ProcessingDetailsSection` | React Component |  |
| 270 | component | `ThinkingTextGroup` | React Component |  |
| 300 | component | `TimelineGroups` | React Component |  |
| 329 | function | `parseToolCallInteractionView` | Parser/normalizer |  |
| 336 | function | `toolArgString` | Function |  |
| 341 | function | `fallbackToolCallLabel` | Function |  |
| 350 | component | `ToolCallCard` | React Component |  |
| 428 | component | `CompactionSummaryCard` | React Component | Y |

#### `apps/desktop/renderer/src/chat/components/thread/AttachmentStrip.tsx` (2 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 8 | component | `AttachmentStrip` | React Component | Y |
| 120 | component | `ImagePreviewOverlay` | React Component | Y |

#### `apps/desktop/renderer/src/chat/components/thread/BatchSearchToolCard.tsx` (2 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 18 | function | `phaseClass` | Function |  |
| 33 | component | `BatchSearchToolCard` | React Component | Y |

#### `apps/desktop/renderer/src/chat/components/thread/ChatFindBar.tsx` (7 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 15 | type | `ChatFindBarProps` | Type/interface |  |
| 27 | type | `HighlightCtor` | Type/interface |  |
| 28 | type | `HighlightRegistry` | Type/interface |  |
| 33 | function | `getHighlightApi` | Function |  |
| 40 | function | `collectRanges` | Function |  |
| 45 | method | `acceptNode` | Method |  |
| 73 | component | `ChatFindBar` | React Component | Y |

#### `apps/desktop/renderer/src/chat/components/thread/ChatHeader.tsx` (2 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 8 | type | `ChatHeaderAction` | Type/interface | Y |
| 25 | component | `ChatHeader` | React Component | Y |

#### `apps/desktop/renderer/src/chat/components/thread/ChatHeaderCapabilities.tsx` (7 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 11 | type | `StatusTone` | Type/interface |  |
| 13 | type | `CapabilityRow` | Type/interface |  |
| 23 | type | `CapabilityService` | Type/interface |  |
| 30 | type | `CapabilityGroup` | Type/interface |  |
| 49 | function | `aggregateTone` | Function |  |
| 84 | function | `healthToTone` | Function |  |
| 107 | component | `ChatHeaderCapabilities` | React Component | Y |

#### `apps/desktop/renderer/src/chat/components/thread/ChatTurn.tsx` (3 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 12 | type | `ChatTurnProps` | Type/interface |  |
| 26 | component | `StreamingElapsedTime` | React Component |  |
| 50 | component | `ChatTurnImpl` | React Component |  |

#### `apps/desktop/renderer/src/chat/components/thread/ImagePreviewBar.tsx` (1 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 1 | component | `ImagePreviewBar` | React Component | Y |

#### `apps/desktop/renderer/src/chat/components/thread/InteractionToolCard.tsx` (1 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 6 | component | `InteractionToolCard` | React Component | Y |

#### `apps/desktop/renderer/src/chat/components/thread/MessageActionBar.tsx` (3 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 4 | type | `MessageActionId` | Type/interface | Y |
| 6 | type | `MessageActionBarProps` | Type/interface |  |
| 15 | component | `MessageActionBar` | React Component | Y |

#### `apps/desktop/renderer/src/chat/components/thread/MessageRail.tsx` (3 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 3 | type | `MessageRailItem` | Type/interface | Y |
| 16 | type | `MessageRailProps` | Type/interface |  |
| 29 | component | `MessageRail` | React Component | Y |

#### `apps/desktop/renderer/src/chat/components/thread/MessageRichParts.tsx` (3 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 5 | function | `actionPrompt` | Function |  |
| 15 | type | `MessageRichPartsProps` | Type/interface |  |
| 21 | component | `MessageRichParts` | React Component | Y |

#### `apps/desktop/renderer/src/chat/components/thread/PermissionGateStrip.tsx` (2 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 6 | type | `PermissionGateStripProps` | Type/interface |  |
| 22 | component | `PermissionGateStrip` | React Component | Y |

#### `apps/desktop/renderer/src/chat/components/thread/ThinkingTimeline.tsx` (9 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 6 | function | `parseToolCardInteractionView` | Parser/normalizer |  |
| 13 | function | `renderToolResult` | Function |  |
| 59 | function | `extractInputArgumentsText` | Function |  |
| 77 | function | `renderToolInput` | Function |  |
| 97 | function | `resolveToolTitle` | Function |  |
| 108 | function | `renderToolStatusBadge` | Function |  |
| 119 | function | `renderToolStream` | Function |  |
| 130 | function | `countRenderedToolCalls` | Function |  |
| 138 | component | `ThinkingTimeline` | React Component | Y |

#### `apps/desktop/renderer/src/chat/components/thread/TokenUsageDisplay.tsx` (2 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 18 | component | `ReasoningEffortSlider` | React Component |  |
| 184 | component | `TokenUsageDisplay` | React Component | Y |

#### `apps/desktop/renderer/src/chat/components/thread/effortSlider.ts` (4 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 10 | function | `effortIndexForLevel` | Function | Y |
| 27 | function | `snapEffortValue` | Function | Y |
| 33 | function | `effortIndexFromValue` | Function | Y |
| 39 | function | `effortLevelForDisplay` | Function | Y |

#### `apps/desktop/renderer/src/chat/components/thread/interactionContext.ts` (1 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 6 | type | `InteractionControl` | Type/interface | Y |

#### `apps/desktop/renderer/src/chat/hooks/useConversationMode.ts` (1 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 17 | hook | `useConversationMode` | React Hook | Y |

#### `apps/desktop/renderer/src/chat/hooks/useConversationModelEffort.ts` (2 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 23 | type | `ConversationModelEffort` | Type/interface | Y |
| 32 | hook | `useConversationModelEffort` | React Hook | Y |

#### `apps/desktop/renderer/src/chat/hooks/useConversationState.ts` (5 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 24 | type | `ConversationActions` | Type/interface | Y |
| 53 | type | `UseConversationStateResult` | Type/interface | Y |
| 59 | hook | `useConversationDraft` | React Hook | Y |
| 76 | hook | `useConversationToolProgress` | React Hook | Y |
| 97 | hook | `useConversationState` | React Hook | Y |

#### `apps/desktop/renderer/src/chat/hooks/useConversationStreamRouter.ts` (5 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 38 | type | `ConversationStreamRouterParams` | Type/interface | Y |
| 51 | function | `appendText` | Function |  |
| 67 | function | `appendThinking` | Function |  |
| 83 | function | `persistMessages` | Function |  |
| 107 | hook | `useConversationStreamRouter` | React Hook | Y |

#### `apps/desktop/renderer/src/chat/hooks/useEffortPreference.ts` (2 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 16 | type | `EffortPreference` | Type/interface | Y |
| 22 | hook | `useEffortPreference` | React Hook | Y |

#### `apps/desktop/renderer/src/chat/hooks/useElapsedTimer.ts` (1 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 12 | hook | `useElapsedTimer` | React Hook | Y |

#### `apps/desktop/renderer/src/chat/hooks/useExitAnimation.ts` (1 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 8 | hook | `useExitAnimation` | React Hook | Y |

#### `apps/desktop/renderer/src/chat/hooks/useListFlip.ts` (2 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 5 | function | `prefersReducedMotion` | Function |  |
| 21 | hook | `useListFlip` | React Hook | Y |

#### `apps/desktop/renderer/src/chat/hooks/useLocalAccessPreference.ts` (2 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 17 | type | `LocalAccessPreference` | Type/interface | Y |
| 23 | hook | `useLocalAccessPreference` | React Hook | Y |

#### `apps/desktop/renderer/src/chat/hooks/useStreamingReport.ts` (1 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 14 | hook | `useStreamingReport` | React Hook | Y |

#### `apps/desktop/renderer/src/chat/hooks/useTypewriterStream.ts` (3 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 17 | type | `TypewriterOptions` | Type/interface | Y |
| 35 | type | `TypewriterController` | Controller | Y |
| 44 | hook | `useTypewriterStream` | React Hook | Y |

#### `apps/desktop/renderer/src/chat/hooks/useVirtualChatTurns.ts` (3 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 9 | type | `UseVirtualChatTurnsOptions` | Type/interface |  |
| 15 | type | `ScrollToTurnOptions` | Type/interface |  |
| 23 | hook | `useVirtualChatTurns` | React Hook | Y |

#### `apps/desktop/renderer/src/chat/state/apiMessageMapping.ts` (12 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 25 | function | `getApiContent` | Function | Y |
| 43 | function | `buildAttachmentText` | Function | Y |
| 69 | function | `getApiMessageContent` | Function | Y |
| 89 | function | `hasApiMessageContent` | Function | Y |
| 98 | function | `hasApiMessagePayload` | Function |  |
| 102 | function | `sanitizeToolCallId` | Function |  |
| 107 | function | `stableToolCallId` | Function |  |
| 115 | function | `safeToolArguments` | Function |  |
| 125 | function | `structuredToolMessages` | Function |  |
| 145 | function | `textMessage` | Function |  |
| 150 | function | `getStructuredApiMessages` | Function |  |
| 188 | function | `toApiMessages` | Function | Y |

#### `apps/desktop/renderer/src/chat/state/attachmentIntake.ts` (3 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 23 | function | `isTextLikeFile` | Function | Y |
| 30 | function | `readAsDataUrl` | Function | Y |
| 40 | function | `readAsText` | Function | Y |

#### `apps/desktop/renderer/src/chat/state/automaticCompaction.ts` (1 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 8 | function | `beginConversationCompaction` | Function | Y |

#### `apps/desktop/renderer/src/chat/state/batchSearchLaneView.ts` (9 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 20 | type | `BatchLanePhase` | Type/interface | Y |
| 28 | type | `BatchSearchLaneView` | Type/interface | Y |
| 37 | type | `BatchSearchAggregateView` | Type/interface | Y |
| 49 | type | `BatchSearchView` | Type/interface | Y |
| 64 | function | `coercePhase` | Function |  |
| 70 | function | `parseMaybeJson` | Parser/normalizer |  |
| 82 | function | `normalizeAggregate` | Parser/normalizer |  |
| 105 | function | `buildBatchSearchView` | Function | Y |
| 186 | function | `lanePhaseLabel` | Function | Y |

#### `apps/desktop/renderer/src/chat/state/browserToolReveal.ts` (1 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 5 | function | `shouldRevealBrowserPanel` | Function | Y |

#### `apps/desktop/renderer/src/chat/state/chatTurnRenderEquality.ts` (2 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 4 | type | `ChatTurnRenderIdentity` | Type/interface | Y |
| 22 | function | `areChatTurnRenderPropsEqual` | Function | Y |

#### `apps/desktop/renderer/src/chat/state/chatTurns.ts` (8 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 3 | type | `ChatTurnMessage` | Type/interface | Y |
| 10 | type | `ChatTurn` | Type/interface | Y |
| 21 | type | `ChatTurnGroupCache` | Type/interface | Y |
| 30 | function | `groupMessagesIntoTurns` | Function | Y |
| 55 | function | `groupMessagesIntoTurnsIncremental` | Function | Y |
| 93 | function | `getTurnUserMessage` | Function | Y |
| 97 | function | `buildMessageTurnIndex` | Function | Y |
| 106 | function | `isLiveChatTurn` | Function | Y |

#### `apps/desktop/renderer/src/chat/state/clientToolCallEvents.ts` (6 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 4 | function | `readString` | Function |  |
| 12 | function | `readConfirmation` | Function |  |
| 18 | function | `normalizeClientToolCall` | Parser/normalizer | Y |
| 77 | function | `normalizeClientToolCallFromToolCallStart` | Parser/normalizer | Y |
| 108 | function | `decodeToolNameToCapabilityId` | Function |  |
| 118 | function | `createUnsupportedClientToolResult` | Function | Y |

#### `apps/desktop/renderer/src/chat/state/clientToolEvidence.ts` (3 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 3 | function | `markClientToolResultReturnedToCloud` | Function | Y |
| 14 | function | `createFailedClientToolResult` | Function | Y |
| 45 | function | `createDeniedClientToolResult` | Function | Y |

#### `apps/desktop/renderer/src/chat/state/coalescedRefresh.ts` (3 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 1 | type | `CoalescedRefreshScheduler` | Type/interface | Y |
| 7 | function | `createCoalescedRefreshScheduler` | Function | Y |
| 46 | method | `dispose` | Method |  |

#### `apps/desktop/renderer/src/chat/state/compactionLifecycle.ts` (3 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 3 | type | `CompactionLifecycleEvent` | Type/interface | Y |
| 9 | function | `belongsToAnotherActiveStream` | Function |  |
| 19 | function | `reduceCompactionLifecycle` | Function | Y |

#### `apps/desktop/renderer/src/chat/state/compactionLiveTailMerge.ts` (3 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 3 | function | `stableSerialize` | Function |  |
| 12 | function | `isSameAssistantLiveTailSnapshot` | Function | Y |
| 22 | function | `mergeLoadedMessagesWithLiveTail` | Function | Y |

#### `apps/desktop/renderer/src/chat/state/compactionStateView.ts` (6 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 3 | type | `SidebarConversationActivity` | Type/interface | Y |
| 8 | function | `isVisibleCompactionState` | Function | Y |
| 14 | function | `compactionProgressPercent` | Function | Y |
| 18 | function | `sidebarConversationActivity` | Function | Y |
| 28 | function | `compactionStateLabel` | Function | Y |
| 34 | function | `sidebarCompactionStateLabel` | Function | Y |

#### `apps/desktop/renderer/src/chat/state/composerPersistence.ts` (18 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 26 | type | `PersistedAttachment` | Type/interface | Y |
| 36 | type | `PersistedEffort` | Type/interface | Y |
| 38 | type | `PersistedQueuedMessage` | Type/interface | Y |
| 45 | type | `PersistedComposerEntry` | Type/interface | Y |
| 53 | type | `ComposerSettingsPort` | Type/interface | Y |
| 60 | type | `ComposerDraftMap` | Type/interface |  |
| 63 | method | `readInitialSettings` | Method |  |
| 67 | method | `updateSettings` | Method |  |
| 80 | function | `isPlainObject` | Function |  |
| 84 | function | `sanitizeEntry` | Function |  |
| 92 | function | `getMap` | Function |  |
| 106 | function | `flushNow` | Function |  |
| 117 | function | `schedulePersist` | Function |  |
| 134 | function | `__setComposerSettingsPort` | Function | Y |
| 145 | function | `flushComposerPersistence` | Function | Y |
| 150 | function | `loadComposerEntry` | Function | Y |
| 160 | function | `saveComposerEntry` | Function | Y |
| 175 | function | `clearComposerEntry` | Function | Y |

#### `apps/desktop/renderer/src/chat/state/contextSources.ts` (6 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 24 | function | `buildAttachmentContext` | Function | Y |
| 44 | function | `buildConversationAttachmentContext` | Function | Y |
| 56 | function | `buildConversationContinuityContext` | Function | Y |
| 71 | function | `buildConfigInstructionContext` | Function | Y |
| 110 | function | `buildReplyLanguageContext` | Function | Y |
| 133 | function | `buildGitBranchPrefixContext` | Function | Y |

#### `apps/desktop/renderer/src/chat/state/conversationLoad.ts` (3 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 29 | function | `nextId` | Function | Y |
| 34 | function | `usageFromLifetime` | Function | Y |
| 56 | function | `loadConversationMessages` | Function | Y |

#### `apps/desktop/renderer/src/chat/state/conversationStore.ts` (8 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 40 | type | `AuthoritativeContext` | Type/interface | Y |
| 46 | type | `ConversationRuntimeState` | Type/interface | Y |
| 100 | function | `resolveConversationBucketId` | Function | Y |
| 114 | function | `areConversationStatesEqualForSurface` | Function | Y |
| 131 | function | `createConversationSurfaceSnapshotReader` | Function | Y |
| 142 | type | `Listener` | Type/interface |  |
| 143 | type | `Patch` | Type/interface |  |
| 151 | constructor | `ConversationStore` | Store | Y |

#### `apps/desktop/renderer/src/chat/state/format.ts` (4 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 9 | function | `formatTime` | Function | Y |
| 18 | function | `formatDuration` | Function | Y |
| 32 | function | `formatBytes` | Function | Y |
| 39 | function | `formatTokenCount` | Function | Y |

#### `apps/desktop/renderer/src/chat/state/frameCoalescer.ts` (2 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 1 | type | `FrameScheduler` | Type/interface | Y |
| 10 | function | `createFrameCoalescer` | Function | Y |

#### `apps/desktop/renderer/src/chat/state/historicalLocalRecord.ts` (5 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 1 | type | `HistoricalLocalRecordSegment` | Type/interface | Y |
| 7 | function | `formatHistoricalLocalRecordForApi` | Function | Y |
| 20 | function | `sanitizeAssistantHistoryTextForApi` | Function | Y |
| 29 | function | `neutralizeToolCallSyntaxForDisplay` | Function | Y |
| 49 | function | `stripHistoricalLocalRecordForDisplay` | Function | Y |

#### `apps/desktop/renderer/src/chat/state/interactionToolView.ts` (6 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 9 | type | `InteractionToolView` | Type/interface | Y |
| 17 | function | `asString` | Function |  |
| 21 | function | `isRequestUserInputTool` | Function |  |
| 26 | function | `parseRawResult` | Parser/normalizer |  |
| 40 | function | `parseInteractionToolView` | Parser/normalizer | Y |
| 61 | function | `parseInteractionToolViewFromCandidates` | Parser/normalizer | Y |

#### `apps/desktop/renderer/src/chat/state/messageRailItems.ts` (3 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 4 | type | `MessageRailItemCache` | Type/interface | Y |
| 10 | function | `buildMessageRailItems` | Function | Y |
| 36 | function | `buildMessageRailItemsIncremental` | Function | Y |

#### `apps/desktop/renderer/src/chat/state/permissionGateView.ts` (12 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 3 | type | `PermissionGateVariant` | Type/interface | Y |
| 10 | type | `PermissionGateView` | Type/interface | Y |
| 22 | function | `isZhLocale` | Function |  |
| 26 | function | `truncatePreview` | Function |  |
| 30 | function | `pickFirstString` | Function |  |
| 38 | function | `extractCommandPreview` | Function |  |
| 59 | function | `extractPathPreview` | Function |  |
| 67 | function | `isHookApproval` | Function |  |
| 71 | function | `isScopeConfirmation` | Function |  |
| 75 | function | `isHighRiskConfirmation` | Function |  |
| 79 | function | `isIrreversibleConfirmation` | Function |  |
| 85 | function | `buildPermissionGateView` | Function | Y |

#### `apps/desktop/renderer/src/chat/state/preferences.ts` (17 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 12 | type | `EffortLevel` | Type/interface | Y |
| 40 | function | `normalizeEffortLevels` | Parser/normalizer | Y |
| 51 | function | `isEffortLevel` | Function | Y |
| 65 | function | `resolvePreferredEffort` | Function | Y |
| 83 | function | `resolveModelSwitchEffort` | Function | Y |
| 100 | function | `resolveModelSwitchState` | Function | Y |
| 130 | function | `readLastModelProviderId` | Provider | Y |
| 141 | function | `writeLastModelProviderId` | Provider | Y |
| 152 | function | `isLocalAccessLevel` | Function | Y |
| 166 | type | `ChatMode` | Type/interface | Y |
| 170 | function | `accessLevelLabel` | Function | Y |
| 177 | function | `accessLevelTitle` | Function | Y |
| 184 | function | `modeLabel` | Function | Y |
| 190 | function | `modeTitle` | Function | Y |
| 196 | function | `effortLabel` | Function | Y |
| 210 | function | `isChatMode` | Function | Y |
| 220 | function | `normalizeChatMode` | Parser/normalizer | Y |

#### `apps/desktop/renderer/src/chat/state/processingWindow.ts` (7 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 7 | type | `ProcessingWindow` | Type/interface | Y |
| 12 | type | `TextWindow` | Type/interface | Y |
| 17 | function | `normalizeTextLimit` | Parser/normalizer |  |
| 22 | function | `windowProcessingText` | Function | Y |
| 44 | function | `previewInlineText` | Function | Y |
| 70 | function | `groupEventCount` | Function |  |
| 78 | function | `windowProcessingGroups` | Function | Y |

#### `apps/desktop/renderer/src/chat/state/providerDisplay.ts` (2 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 11 | function | `getProviderDisplayName` | Provider | Y |
| 19 | function | `getProviderModelDisplayLabel` | Provider | Y |

#### `apps/desktop/renderer/src/chat/state/quickChatAttachments.ts` (2 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 4 | function | `getClipboardFiles` | Function | Y |
| 12 | function | `hasQuickChatContent` | Function | Y |

#### `apps/desktop/renderer/src/chat/state/quickChatTasks.ts` (8 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 5 | type | `QuickChatInteractionTask` | Type/interface | Y |
| 15 | type | `QuickChatPlanTask` | Type/interface | Y |
| 24 | type | `QuickChatTask` | Type/interface | Y |
| 26 | type | `QuickChatTaskConversation` | Type/interface | Y |
| 33 | function | `interactionFromSegment` | Function |  |
| 45 | function | `projectQuickChatTasks` | Function | Y |
| 80 | function | `projectQuickChatPlanTasks` | Function | Y |
| 101 | function | `mergeQuickChatTasks` | Function | Y |

#### `apps/desktop/renderer/src/chat/state/quickChatWorkspaceIdentity.ts` (2 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 1 | type | `QuickChatWorkspaceIdentity` | Type/interface | Y |
| 7 | function | `getQuickChatWorkspaceIdentity` | Function | Y |

#### `apps/desktop/renderer/src/chat/state/streamSegments.ts` (22 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 11 | type | `ToolCallSegment` | Type/interface |  |
| 14 | function | `normalizeStreamSegment` | Parser/normalizer | Y |
| 30 | function | `segmentsSignature` | Function | Y |
| 39 | function | `stableToolCallId` | Function |  |
| 45 | function | `hasArgs` | Function |  |
| 49 | function | `mergeSameToolCallSegment` | Function |  |
| 63 | function | `settlePersistedToolCalls` | Function |  |
| 86 | function | `appendLiveSuffixWithoutDuplicateToolCalls` | Function |  |
| 102 | function | `mergeTextLikeReattachSegment` | Function |  |
| 121 | function | `mergeReattachPrefixSegment` | Function |  |
| 129 | function | `legacyToolCallFromSegment` | Function |  |
| 152 | function | `mergeReattachedSegments` | Function | Y |
| 186 | function | `contentFromSegments` | Function | Y |
| 195 | function | `isEmptyAssistantPlaceholder` | Function | Y |
| 204 | function | `groupSegments` | Function | Y |
| 229 | type | `SplitFinalTextOptions` | Type/interface | Y |
| 244 | function | `splitFinalTextGroup` | Function | Y |
| 273 | function | `getTextContent` | Function | Y |
| 278 | function | `migrateToSegments` | Function | Y |
| 299 | function | `findNextSerializedToolCall` | Function | Y |
| 308 | function | `parseSerializedToolSegments` | Parser/normalizer | Y |
| 388 | function | `markDanglingToolCallsInterrupted` | Function | Y |

#### `apps/desktop/renderer/src/chat/state/tokenEstimate.ts` (8 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 16 | function | `estimateTextTokens` | Function | Y |
| 25 | function | `estimateMessageTokens` | Function | Y |
| 50 | function | `estimateAttachmentTokens` | Function | Y |
| 65 | function | `estimateConversationHistoryTokens` | Function | Y |
| 87 | type | `ConversationTokenEstimateCache` | Type/interface | Y |
| 98 | function | `estimateConversationHistoryTokensIncremental` | Function | Y |
| 133 | function | `estimateDraftTokens` | Function | Y |
| 141 | function | `estimateConversationTokens` | Function | Y |

#### `apps/desktop/renderer/src/chat/state/types.ts` (17 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 13 | type | `ChatAttachment` | Type/interface | Y |
| 27 | type | `QueuedMessage` | Type/interface | Y |
| 35 | type | `ChatApiContentPart` | Type/interface | Y |
| 40 | type | `ChatApiToolCall` | Type/interface | Y |
| 50 | type | `ChatApiMessage` | Type/interface | Y |
| 59 | type | `ContentSegment` | Type/interface | Y |
| 75 | type | `ToolCallLegacy` | Type/interface | Y |
| 86 | type | `CompactionMeta` | Type/interface | Y |
| 105 | type | `CompactionState` | Type/interface | Y |
| 130 | type | `ChatMsg` | Type/interface | Y |
| 150 | type | `TextGroup` | Type/interface | Y |
| 151 | type | `ThinkingGroup` | Type/interface | Y |
| 152 | type | `ToolCallGroup` | Type/interface | Y |
| 153 | type | `SegmentGroup` | Type/interface | Y |
| 156 | type | `TokenUsageState` | Type/interface | Y |
| 168 | type | `ToolProgress` | Type/interface | Y |
| 177 | type | `ProviderRecoveryNotice` | Provider | Y |

#### `apps/desktop/renderer/src/chat/state/virtualTurns.ts` (6 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 4 | type | `VirtualTurnItem` | Type/interface | Y |
| 11 | type | `VirtualTurnRange` | Type/interface | Y |
| 20 | type | `VirtualTurnRangeInput` | Type/interface | Y |
| 30 | function | `normalizedSize` | Parser/normalizer |  |
| 40 | function | `calculateVirtualTurnRange` | Function | Y |
| 113 | function | `estimateVirtualTurnOffset` | Function | Y |

#### `apps/desktop/renderer/src/chat/utils/records.ts` (6 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 1 | function | `isRecord` | Function | Y |
| 8 | function | `compactJson` | Function | Y |
| 22 | function | `compactLine` | Function | Y |
| 28 | function | `collectValuesByKey` | Function | Y |
| 54 | function | `recordString` | Function | Y |
| 62 | function | `recordNumber` | Function | Y |

#### `apps/desktop/renderer/src/clientApi.ts` (3 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 1 | type | `ClientApi` | Type/interface | Y |
| 3 | function | `desktopOnly` | Function |  |
| 7 | function | `unavailableMethod` | Function |  |

#### `apps/desktop/renderer/src/preload/contracts/bootstrapPreloadApi.ts` (13 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 52 | type | `PendingTask` | Type/interface | Y |
| 68 | type | `StreamReattachResult` | Type/interface | Y |
| 108 | type | `GoalRunnerStateView` | Type/interface | Y |
| 119 | type | `LifetimeUsage` | Type/interface | Y |
| 127 | type | `UsageStatsTokenTotals` | Type/interface | Y |
| 135 | type | `UsageStatsGroupRow` | Type/interface | Y |
| 146 | type | `UsageStatsSnapshot` | Type/interface | Y |
| 170 | type | `ActiveStreamProjection` | Type/interface | Y |
| 175 | type | `QuickChatPopoverKind` | Type/interface | Y |
| 177 | type | `QuickChatPopoverItem` | Type/interface | Y |
| 183 | type | `QuickChatPopoverState` | Type/interface | Y |
| 189 | type | `QuickChatPopoverAnchorRect` | Type/interface | Y |
| 196 | type | `BootstrapPreloadApi` | Type/interface | Y |

#### `apps/desktop/renderer/src/preload/contracts/chatPreloadApi.ts` (1 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 1 | type | `ChatPreloadApi` | Type/interface | Y |

#### `apps/desktop/renderer/src/preload/contracts/peerAgentPreloadApi.ts` (1 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 3 | type | `PeerAgentPreloadApi` | Type/interface | Y |

#### `apps/desktop/renderer/src/settings/UsageStatsPanel.tsx` (4 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 9 | function | `formatUsd` | Function |  |
| 18 | function | `formatCount` | Function |  |
| 24 | component | `GroupTable` | React Component |  |
| 88 | component | `UsageStatsPanel` | React Component | Y |

#### `apps/desktop/renderer/src/workbench/ResourceTabStrip.tsx` (4 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 3 | type | `ResourceTabItem` | Type/interface | Y |
| 9 | type | `ResourceTabStripProps` | Type/interface |  |
| 35 | component | `CloseIcon` | React Component |  |
| 39 | component | `ResourceTabStrip` | React Component | Y |

#### `apps/desktop/renderer/src/workbench/SidebarResizer.tsx` (3 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 10 | type | `SidebarResizerProps` | Type/interface |  |
| 14 | component | `ROOT` | React Component |  |
| 28 | component | `SidebarResizer` | React Component | Y |

#### `apps/desktop/renderer/src/workbench/SidebarToggle.tsx` (2 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 3 | type | `SidebarToggleProps` | Type/interface |  |
| 14 | component | `SidebarToggle` | React Component | Y |

#### `apps/desktop/renderer/src/workbench/WorkbenchContext.tsx` (14 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 48 | type | `WorkbenchFilesTarget` | Type/interface | Y |
| 73 | type | `WorkbenchSettingsShape` | Type/interface |  |
| 85 | type | `WorkbenchState` | Type/interface |  |
| 103 | type | `BrowserSessionUpdater` | Type/interface |  |
| 107 | type | `DocumentSessionUpdater` | Type/interface |  |
| 111 | type | `WorkbenchActions` | Type/interface |  |
| 136 | type | `WorkbenchContextValue` | Type/interface |  |
| 140 | function | `clampWidth` | Function |  |
| 149 | function | `clampSidebarWidth` | Function |  |
| 153 | function | `readWorkbenchSettings` | Function |  |
| 160 | type | `WorkbenchProviderProps` | Provider |  |
| 166 | component | `WorkbenchProvider` | React Component | Y |
| 518 | hook | `useWorkbench` | React Hook | Y |
| 528 | hook | `useWorkbenchOptional` | React Hook | Y |

#### `apps/desktop/renderer/src/workbench/WorkbenchPanel.tsx` (3 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 15 | type | `TabDef` | Type/interface |  |
| 82 | type | `WorkbenchPanelProps` | Type/interface |  |
| 87 | component | `WorkbenchPanel` | React Component | Y |

#### `apps/desktop/renderer/src/workbench/WorkbenchToggle.tsx` (2 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 3 | type | `WorkbenchToggleProps` | Type/interface |  |
| 7 | component | `WorkbenchToggle` | React Component | Y |

#### `apps/desktop/renderer/src/workbench/browserSessionState.ts` (14 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 6 | type | `BrowserTabSession` | Type/interface | Y |
| 12 | type | `BrowserSessionState` | Type/interface | Y |
| 17 | type | `BrowserSessionMap` | Type/interface | Y |
| 21 | function | `workbenchSessionKey` | Function | Y |
| 28 | function | `createBrowserTabId` | Function | Y |
| 36 | function | `createBrowserTabSession` | Function | Y |
| 44 | function | `createBrowserSessionState` | Function | Y |
| 48 | function | `normalizeBrowserTab` | Parser/normalizer |  |
| 59 | function | `normalizeBrowserSessionState` | Parser/normalizer | Y |
| 76 | function | `normalizeBrowserSessionMap` | Parser/normalizer | Y |
| 85 | function | `addBrowserTab` | Function | Y |
| 93 | function | `activateBrowserTab` | Function | Y |
| 103 | function | `updateBrowserTab` | Function | Y |
| 123 | function | `closeBrowserTab` | Function | Y |

#### `apps/desktop/renderer/src/workbench/documentSessionState.ts` (15 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 1 | type | `WorkbenchFileMode` | Type/interface | Y |
| 3 | type | `DocumentTabSession` | Type/interface | Y |
| 12 | type | `DocumentSessionState` | Type/interface | Y |
| 17 | type | `DocumentSessionMap` | Type/interface | Y |
| 21 | function | `createDocumentTabId` | Function | Y |
| 29 | function | `createDocumentTabSession` | Function | Y |
| 47 | function | `createDocumentSessionState` | Function | Y |
| 51 | function | `isDocumentMode` | Function |  |
| 55 | function | `normalizeDocumentTab` | Parser/normalizer |  |
| 71 | function | `normalizeDocumentSessionState` | Parser/normalizer | Y |
| 92 | function | `normalizeDocumentSessionMap` | Parser/normalizer | Y |
| 101 | function | `openDocumentTab` | Function | Y |
| 127 | function | `activateDocumentTab` | Function | Y |
| 137 | function | `updateDocumentTabMode` | Function | Y |
| 151 | function | `closeDocumentTab` | Function | Y |

#### `apps/desktop/renderer/src/workbench/file-preview/DiffViewer.tsx` (7 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 3 | type | `LineKind` | Type/interface |  |
| 5 | type | `DiffLine` | Type/interface |  |
| 12 | type | `DiffViewerProps` | Type/interface |  |
| 16 | function | `parseHunkHeader` | Parser/normalizer |  |
| 22 | function | `classifyLine` | Function |  |
| 44 | function | `buildDiffLines` | Function | Y |
| 82 | component | `DiffViewer` | React Component | Y |

#### `apps/desktop/renderer/src/workbench/file-preview/MarkdownDocument.tsx` (6 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 5 | type | `MarkdownDocumentProps` | Type/interface |  |
| 12 | type | `CodeBlockProps` | Type/interface |  |
| 19 | component | `Heading` | React Component |  |
| 36 | component | `CodeBlock` | React Component |  |
| 64 | function | `renderBlock` | Function |  |
| 135 | component | `MarkdownDocument` | React Component | Y |

#### `apps/desktop/renderer/src/workbench/file-preview/SourceViewer.tsx` (2 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 3 | type | `SourceViewerProps` | Type/interface |  |
| 9 | component | `SourceViewer` | React Component | Y |

#### `apps/desktop/renderer/src/workbench/file-preview/fileTypes.ts` (6 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 3 | type | `WorkbenchFileKind` | Type/interface | Y |
| 48 | function | `basename` | Function | Y |
| 54 | function | `extension` | Function | Y |
| 61 | function | `detectFileKind` | Function | Y |
| 71 | function | `defaultModeForKind` | Function | Y |
| 76 | function | `formatJsonForPreview` | Function | Y |

#### `apps/desktop/renderer/src/workbench/views/BrowserView.tsx` (19 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 25 | type | `WebviewElement` | Type/interface |  |
| 39 | type | `WebviewProps` | Type/interface |  |
| 55 | type | `BrowserViewProps` | Type/interface |  |
| 64 | type | `BrowserFailure` | Type/interface |  |
| 70 | type | `BrowserTabRuntimeState` | Type/interface |  |
| 78 | type | `BrowserPageProps` | Type/interface |  |
| 93 | function | `initialRuntime` | Function |  |
| 103 | function | `normalizeInput` | Parser/normalizer |  |
| 116 | function | `displayUrl` | Function |  |
| 121 | function | `tabLabel` | Function |  |
| 145 | component | `IconBack` | React Component |  |
| 149 | component | `IconForward` | React Component |  |
| 153 | component | `IconReload` | React Component |  |
| 157 | component | `IconStop` | React Component |  |
| 161 | component | `IconGo` | React Component |  |
| 165 | component | `IconGlobe` | React Component |  |
| 176 | component | `IconPlus` | React Component |  |
| 180 | component | `BrowserPage` | React Component |  |
| 319 | component | `BrowserView` | React Component | Y |

#### `apps/desktop/renderer/src/workbench/views/DocumentView.tsx` (14 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 22 | type | `DocumentViewProps` | Type/interface |  |
| 31 | type | `DocumentPageProps` | Type/interface |  |
| 38 | type | `GitDiffResult` | Type/interface |  |
| 39 | type | `DiffStatus` | Type/interface |  |
| 40 | type | `FileReadResult` | Type/interface |  |
| 42 | type | `DiffState` | Type/interface |  |
| 48 | type | `ContentState` | Type/interface |  |
| 57 | function | `statusLabel` | Function |  |
| 72 | function | `contentErrorLabel` | Function |  |
| 93 | function | `modeBadge` | Function |  |
| 120 | component | `DocumentIcon` | React Component |  |
| 129 | component | `AddIcon` | React Component |  |
| 133 | component | `DocumentView` | React Component | Y |
| 199 | component | `DocumentPage` | React Component |  |

#### `apps/desktop/renderer/src/workbench/views/FilesView.tsx` (9 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 5 | type | `FilesViewProps` | Type/interface |  |
| 10 | type | `DirEntry` | Type/interface |  |
| 17 | function | `stripTrailingSep` | Function |  |
| 22 | function | `toForward` | Function |  |
| 27 | function | `baseName` | Function |  |
| 37 | function | `buildChain` | Function |  |
| 52 | type | `TreeNodeProps` | Type/interface |  |
| 64 | component | `TreeNode` | React Component |  |
| 161 | component | `FilesView` | React Component | Y |

#### `apps/desktop/renderer/src/workbench/workbenchOpenState.ts` (5 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 3 | type | `WorkbenchOpenMap` | Type/interface | Y |
| 5 | function | `workbenchOpenKey` | Function | Y |
| 9 | function | `normalizeWorkbenchOpenMap` | Parser/normalizer | Y |
| 18 | function | `resolveWorkbenchOpen` | Function | Y |
| 26 | function | `updateWorkbenchOpen` | Function | Y |

#### `apps/desktop/renderer/src/workbench/workbenchTabState.ts` (4 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 1 | type | `WorkbenchTabId` | Type/interface | Y |
| 3 | function | `isWorkbenchTab` | Function |  |
| 13 | function | `normalizeWorkbenchTab` | Parser/normalizer | Y |
| 19 | function | `normalizeWorkbenchTabMap` | Parser/normalizer | Y |

#### `packages/chat-kernel/src/chat-reducer.ts` (14 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 18 | type | `ChatRuntimeAction` | Type/interface | Y |
| 59 | function | `createInitialChatRuntimeState` | Function | Y |
| 73 | function | `createUserMessage` | Function | Y |
| 91 | function | `createAssistantPlaceholder` | Function | Y |
| 104 | function | `isRecord` | Function |  |
| 108 | function | `readString` | Function |  |
| 118 | function | `readNumber` | Function |  |
| 131 | function | `extractContent` | Function |  |
| 148 | function | `recoverContentFromThinkingProcess` | Function |  |
| 157 | function | `recoverCompletedAssistantContent` | Function |  |
| 163 | function | `updateMessage` | Function |  |
| 176 | function | `ensureAssistantMessage` | Function |  |
| 187 | function | `applyStreamEvent` | Function |  |
| 302 | function | `reduceChatRuntime` | Function | Y |

#### `packages/chat-kernel/src/confirmation-reducer.ts` (3 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 6 | function | `replacePendingConfirmation` | Function | Y |
| 16 | function | `removeResolvedConfirmation` | Function | Y |
| 23 | function | `normalizePendingHumanConfirmation` | Parser/normalizer | Y |

#### `packages/chat-kernel/src/historical-thinking-normalizer.ts` (7 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 24 | type | `BackendStepIteration` | Type/interface |  |
| 45 | type | `BackendThinkingStep` | Type/interface |  |
| 52 | type | `BackendThinkingStepsData` | Type/interface | Y |
| 85 | function | `readInputArguments` | Function |  |
| 93 | function | `toToolCard` | Function |  |
| 114 | function | `iterationsFromBackendStepsData` | Function | Y |
| 188 | function | `hydrateThinkingProcessFromBackend` | Function | Y |

#### `packages/chat-kernel/src/message-actions.ts` (1 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 3 | function | `computeMessageActions` | Function | Y |

#### `packages/chat-kernel/src/stream-parser.ts` (11 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 3 | type | `SseParserState` | Type/interface | Y |
| 11 | type | `SseParseResult` | Type/interface | Y |
| 16 | function | `createSseParserState` | Parser/normalizer | Y |
| 24 | function | `parseEventData` | Parser/normalizer |  |
| 36 | function | `dispatchEvent` | Function |  |
| 48 | function | `resetEventFrame` | Function |  |
| 56 | function | `applyLine` | Function |  |
| 101 | function | `parseSseChunk` | Parser/normalizer | Y |
| 119 | function | `flushSseParser` | Parser/normalizer | Y |
| 138 | type | `StreamDelta` | Type/interface | Y |
| 143 | function | `parseServerSentEventLine` | Parser/normalizer | Y |

#### `packages/chat-kernel/src/thinking-reducer.ts` (26 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 13 | function | `isRecord` | Function |  |
| 22 | function | `hasSubstantiveArgs` | Function |  |
| 29 | function | `readString` | Function |  |
| 39 | function | `readNumber` | Function |  |
| 52 | function | `createThinkingProcess` | Function | Y |
| 63 | function | `createIteration` | Function |  |
| 74 | function | `createToolCard` | Function |  |
| 113 | function | `deriveToolCardStatus` | Function |  |
| 127 | function | `createSkillStep` | Function |  |
| 146 | function | `updateLastIteration` | Function |  |
| 181 | function | `shouldStartNewIteration` | Function |  |
| 186 | function | `updateToolCard` | Function |  |
| 204 | function | `hasCompositeKey` | Function |  |
| 209 | function | `appendThinkingContent` | Function |  |
| 234 | function | `appendToolCard` | Function |  |
| 282 | function | `upsertClientToolCard` | Function |  |
| 322 | function | `updateClientToolStatus` | Function |  |
| 335 | function | `appendClientToolStream` | Function |  |
| 353 | function | `finalizeClientToolCard` | Function |  |
| 390 | function | `safeStringify` | Function |  |
| 399 | function | `completeToolCard` | Function |  |
| 410 | function | `appendStep` | Function |  |
| 418 | function | `completeStep` | Function |  |
| 444 | function | `setPendingConfirmation` | Function |  |
| 455 | function | `finishProcess` | Function |  |
| 473 | function | `applyThinkingEvent` | Function | Y |

#### `packages/conversation-store/src/index.d.ts` (9 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 1 | type | `ConversationUsage` | Type/interface | Y |
| 10 | type | `ConversationMeta` | Type/interface | Y |
| 23 | type | `StoredConversation` | Store | Y |
| 27 | type | `ConversationListPage` | Type/interface | Y |
| 34 | type | `ConversationChangeEvent` | Type/interface | Y |
| 43 | type | `ConversationListParams` | Type/interface | Y |
| 54 | type | `ConversationStore` | Store | Y |
| 76 | function | `createConversationStore` | Store | Y |
| 78 | function | `rankConversationMatch` | Function | Y |

#### `packages/conversation-store/src/index.mjs` (18 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 6 | function | `defaultStoreDir` | Store |  |
| 11 | function | `readJsonl` | Function |  |
| 20 | function | `writeJsonl` | Function |  |
| 32 | function | `appendJsonl` | Function |  |
| 37 | function | `writeChangeEvent` | Function |  |
| 47 | function | `withFileLock` | Function |  |
| 69 | function | `normalizeMode` | Parser/normalizer |  |
| 79 | function | `normalizeEffort` | Parser/normalizer |  |
| 87 | function | `normalizeModelProviderId` | Provider |  |
| 91 | function | `normalizeStatus` | Parser/normalizer |  |
| 95 | function | `normalizeStatuses` | Parser/normalizer |  |
| 101 | function | `normalizeMeta` | Parser/normalizer |  |
| 127 | function | `migrateLegacyGoalMode` | Function |  |
| 147 | function | `normalizeSearchQuery` | Parser/normalizer |  |
| 151 | function | `workspaceShortName` | Function |  |
| 163 | function | `rankConversationMatch` | Function | Y |
| 179 | function | `sortByUpdatedAtDesc` | Function |  |
| 187 | function | `createConversationStore` | Store | Y |

#### `packages/credential-helper/src/index.ts` (22 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 10 | type | `CredentialHelperRequest` | Type/interface | Y |
| 16 | type | `CredentialHelperResponse` | Type/interface |  |
| 26 | type | `CredentialHelperTransport` | Type/interface | Y |
| 30 | constructor | `CredentialHelperError` | Class | Y |
| 40 | type | `CredentialHelperPathOptions` | Type/interface | Y |
| 49 | function | `resolveCredentialHelperPath` | Function | Y |
| 83 | type | `SubprocessTransportOptions` | Type/interface | Y |
| 94 | function | `createSubprocessCredentialTransport` | Function | Y |
| 104 | method | `invoke` | Method |  |
| 149 | constructor | `CredentialHelperClient` | Class | Y |
| 204 | function | `modelApiKeyCredentialKey` | Function | Y |
| 208 | function | `modelOauthCredentialKey` | Function | Y |
| 212 | function | `modelCredentialKey` | Function |  |
| 218 | function | `validateRequest` | Function |  |
| 234 | function | `validateCredentialKey` | Function |  |
| 243 | function | `parseResponse` | Parser/normalizer |  |
| 270 | function | `readString` | Function |  |
| 276 | function | `readOptionalString` | Function |  |
| 286 | function | `readNullableString` | Function |  |
| 296 | function | `readBoolean` | Function |  |
| 302 | function | `throwInvalidResponse` | Function |  |
| 309 | function | `isRecord` | Function |  |

#### `packages/i18n/src/index.ts` (5 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 9 | type | `TranslationKey` | Type/interface | Y |
| 582 | type | `TranslationValues` | Type/interface |  |
| 1739 | type | `I18nRuntime` | Type/interface | Y |
| 1747 | function | `resolveLocale` | Function | Y |
| 1764 | function | `createI18n` | Function | Y |

#### `packages/protocol/src/chat.ts` (33 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 8 | type | `ConversationStatus` | Type/interface | Y |
| 10 | type | `ConversationMetadata` | Type/interface | Y |
| 15 | type | `Conversation` | Type/interface | Y |
| 29 | type | `MessageRole` | Type/interface | Y |
| 31 | type | `MessageStatus` | Type/interface | Y |
| 33 | type | `MessageReference` | Type/interface | Y |
| 40 | type | `MessageImage` | Type/interface | Y |
| 47 | type | `AssistantAction` | Type/interface | Y |
| 59 | type | `ChatMessage` | Type/interface | Y |
| 88 | type | `MessageSource` | Type/interface | Y |
| 103 | type | `ConversationCapabilities` | Type/interface | Y |
| 110 | type | `ConversationLineage` | Type/interface | Y |
| 129 | type | `ConversationView` | Type/interface | Y |
| 136 | type | `MessageNodeOrigin` | Type/interface | Y |
| 138 | type | `MessageActions` | Type/interface | Y |
| 146 | type | `ChatRuntimeState` | Type/interface | Y |
| 164 | type | `ChatStreamEvent` | Type/interface | Y |
| 171 | type | `ConversationListData` | Type/interface | Y |
| 178 | type | `MessageListData` | Type/interface | Y |
| 186 | type | `ChatStreamStartResult` | Type/interface | Y |
| 190 | type | `ChatStreamEventEnvelope` | Type/interface | Y |
| 196 | type | `ChatStreamDoneEnvelope` | Type/interface | Y |
| 201 | type | `ChatStreamErrorEnvelope` | Type/interface | Y |
| 207 | type | `ConversationMutationResult` | Type/interface | Y |
| 213 | type | `BranchConversationResult` | Type/interface | Y |
| 218 | type | `ThinkingDetailData` | Type/interface | Y |
| 226 | type | `AgentSummary` | Type/interface | Y |
| 235 | type | `AgentListData` | Type/interface | Y |
| 240 | type | `AssistantSuggestion` | Type/interface | Y |
| 248 | type | `AssistantSuggestionListData` | Type/interface | Y |
| 252 | type | `InlineCompletionData` | Type/interface | Y |
| 278 | function | `isReadOnlyConversation` | Function | Y |
| 282 | function | `buildConversationView` | Function | Y |

#### `packages/protocol/src/execution.ts` (27 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 1 | type | `ExecutionStatus` | Type/interface | Y |
| 9 | type | `HumanConfirmationDecision` | Type/interface | Y |
| 11 | type | `HumanConfirmationTiming` | Type/interface | Y |
| 17 | type | `HumanConfirmationStep` | Type/interface | Y |
| 23 | type | `PendingHumanConfirmation` | Type/interface | Y |
| 34 | type | `ResolvedHumanConfirmation` | Type/interface | Y |
| 43 | type | `MessageSender` | Type/interface | Y |
| 56 | type | `DispatchSubtask` | Type/interface | Y |
| 64 | type | `PendingDispatch` | Type/interface | Y |
| 72 | type | `PendingDispatchResult` | Type/interface | Y |
| 81 | type | `DispatchConfirmResult` | Type/interface | Y |
| 87 | type | `ThinkingBlock` | Type/interface | Y |
| 97 | type | `SkillStep` | Type/interface | Y |
| 109 | type | `NestedSkill` | Type/interface | Y |
| 126 | type | `ClientToolStatus` | Type/interface | Y |
| 147 | type | `ToolCardLane` | Type/interface | Y |
| 166 | type | `ToolCard` | Type/interface | Y |
| 205 | type | `IterationNode` | Type/interface | Y |
| 216 | type | `ThinkingProcess` | Type/interface | Y |
| 232 | type | `ExecutionStatusSnapshot` | Type/interface | Y |
| 248 | type | `ExecutionCotSnapshot` | Type/interface | Y |
| 259 | type | `ExecutionDetailData` | Type/interface | Y |
| 270 | type | `ExecutionResultData` | Type/interface | Y |
| 280 | type | `ExecutionSourceTraceData` | Type/interface | Y |
| 288 | type | `ExecutionListData` | Type/interface | Y |
| 297 | type | `RelatedShadowExecutionListData` | Type/interface | Y |
| 304 | type | `ExecutionCancelResult` | Type/interface | Y |

#### `packages/protocol/src/goal.ts` (43 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 20 | type | `GoalPlanStatus` | Type/interface | Y |
| 32 | type | `GoalWorkflowKind` | Type/interface | Y |
| 41 | type | `GoalActivation` | Type/interface | Y |
| 51 | type | `GoalIntakeResolution` | Type/interface | Y |
| 56 | type | `GoalAskUserReason` | Type/interface | Y |
| 67 | type | `GoalExecutionPolicy` | Type/interface | Y |
| 75 | type | `ExceptionPolicyAction` | Type/interface | Y |
| 78 | type | `ExceptionPolicy` | Type/interface | Y |
| 90 | type | `GoalBoundaries` | Type/interface | Y |
| 96 | type | `GoalTask` | Type/interface | Y |
| 127 | type | `EvidenceIndexRecord` | Type/interface | Y |
| 140 | type | `GoalApproval` | Type/interface | Y |
| 150 | type | `GoalProgress` | Type/interface | Y |
| 160 | type | `GoalRevision` | Type/interface | Y |
| 168 | type | `GoalRunnerStatus` | Type/interface | Y |
| 179 | type | `GoalRunnerIntent` | Type/interface | Y |
| 186 | type | `GoalRunnerPhase` | Type/interface | Y |
| 196 | type | `GoalBlockerAudit` | Type/interface | Y |
| 205 | type | `GoalExplorerProfile` | Type/interface | Y |
| 207 | type | `GoalExplorerStatus` | Type/interface | Y |
| 210 | type | `GoalExplorerRequest` | Type/interface | Y |
| 228 | type | `GoalExplorerFinding` | Type/interface | Y |
| 234 | type | `GoalExplorerReport` | Type/interface | Y |
| 245 | type | `GoalExplorerRun` | Type/interface | Y |
| 260 | type | `GoalExplorerBatch` | Type/interface | Y |
| 268 | type | `GoalExploreQuestion` | Type/interface | Y |
| 281 | type | `GoalExplorePlan` | Type/interface | Y |
| 288 | type | `GoalVerifierStatus` | Type/interface | Y |
| 290 | type | `GoalVerifierTargetKind` | Type/interface | Y |
| 292 | type | `GoalVerifierTarget` | Type/interface | Y |
| 298 | type | `GoalVerifierIssue` | Type/interface | Y |
| 305 | type | `GoalVerifierReport` | Type/interface | Y |
| 315 | type | `GoalVerifierRun` | Type/interface | Y |
| 329 | type | `GoalRunEventType` | Type/interface | Y |
| 353 | type | `GoalRunEvent` | Type/interface | Y |
| 366 | type | `GoalRunTrace` | Type/interface | Y |
| 372 | type | `GoalSuccessCriterionKind` | Type/interface | Y |
| 379 | type | `GoalSuccessCriterion` | Type/interface | Y |
| 388 | type | `GoalCriterionResult` | Type/interface | Y |
| 396 | type | `GoalManualConfirmationKind` | Type/interface | Y |
| 398 | type | `GoalManualConfirmation` | Type/interface | Y |
| 409 | type | `GoalRunnerState` | Type/interface | Y |
| 447 | type | `GoalPlan` | Type/interface | Y |

#### `packages/protocol/src/index.ts` (86 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 1 | type | `LocalAccessLevel` | Type/interface | Y |
| 7 | type | `CapabilityRiskLevel` | Type/interface | Y |
| 15 | type | `DataLevel` | Type/interface | Y |
| 17 | type | `CapabilitySource` | Type/interface | Y |
| 19 | type | `CapabilityHealth` | Type/interface | Y |
| 21 | type | `LocaleCode` | Type/interface | Y |
| 23 | type | `LocalizedText` | Type/interface | Y |
| 25 | type | `JsonSchemaLike` | Type/interface | Y |
| 34 | type | `EvidencePolicy` | Type/interface | Y |
| 40 | type | `CapabilityManifest` | Type/interface | Y |
| 69 | type | `SkillSummary` | Type/interface | Y |
| 82 | type | `AvailableSkillSummary` | Type/interface | Y |
| 94 | type | `SkillLinkResult` | Type/interface | Y |
| 101 | type | `RuntimeProjection` | Type/interface | Y |
| 110 | type | `McpTransportKind` | Type/interface | Y |
| 111 | type | `McpHealthStatus` | Type/interface | Y |
| 112 | type | `McpAuthMode` | Type/interface | Y |
| 113 | type | `McpCredentialKind` | Type/interface | Y |
| 115 | type | `McpOAuthConfigView` | Type/interface | Y |
| 125 | type | `McpAuthBindingView` | Type/interface | Y |
| 133 | type | `McpCredentialMetadataView` | Type/interface | Y |
| 148 | type | `McpCredentialPutRequest` | Type/interface | Y |
| 164 | type | `McpOAuthLoginRequest` | Type/interface | Y |
| 168 | type | `McpOAuthLoginResult` | Type/interface | Y |
| 174 | type | `McpHealthView` | Type/interface | Y |
| 180 | type | `McpToolSummary` | Type/interface | Y |
| 187 | type | `McpResourceSummary` | Type/interface | Y |
| 194 | type | `McpPromptSummary` | Type/interface | Y |
| 200 | type | `LocalMcpServerView` | Type/interface | Y |
| 230 | type | `LocalMcpServerUpsertRequest` | Type/interface | Y |
| 248 | type | `McpConnectionTestResult` | Type/interface | Y |
| 257 | type | `McpConnectionProbeState` | Type/interface | Y |
| 259 | type | `McpConnectionProbeAuthAction` | Type/interface | Y |
| 265 | type | `McpConnectionProbeResult` | Type/interface | Y |
| 279 | type | `McpManifestRefreshResult` | Type/interface | Y |
| 295 | type | `ClientSessionState` | Type/interface | Y |
| 305 | type | `GitProjectState` | Type/interface | Y |
| 316 | type | `WorkspaceProject` | Type/interface | Y |
| 327 | type | `LlmProviderType` | Provider | Y |
| 328 | type | `LlmWireProtocol` | Type/interface | Y |
| 329 | type | `LlmChannelId` | Type/interface | Y |
| 330 | type | `LlmReasoningParamStyle` | Type/interface | Y |
| 337 | type | `LlmReasoningEffortMap` | Type/interface | Y |
| 339 | type | `LlmChannelDescriptor` | Type/interface | Y |
| 374 | type | `LlmAuthMethod` | Type/interface | Y |
| 377 | type | `LlmOAuthConnectionStatus` | Type/interface | Y |
| 379 | type | `LlmOAuthStatus` | Type/interface | Y |
| 386 | type | `LlmSubscriptionQuotaWindow` | Type/interface | Y |
| 398 | type | `LlmSubscriptionQuota` | Type/interface | Y |
| 416 | type | `LlmProviderConfig` | Provider | Y |
| 466 | type | `LlmProviderConfigView` | Provider | Y |
| 483 | type | `LlmModelConfig` | Type/interface | Y |
| 516 | type | `LlmProviderGroupConfig` | Provider | Y |
| 529 | type | `LlmProviderGroupConfigView` | Provider | Y |
| 539 | type | `LlmModelOptionValue` | Type/interface | Y |
| 541 | type | `LlmModelOptionChoice` | Type/interface | Y |
| 550 | type | `LlmModelOptionDefinition` | Type/interface | Y |
| 559 | type | `LlmModelOptionValues` | Type/interface | Y |
| 561 | function | `resolveLlmModelOptionValues` | Function | Y |
| 575 | function | `resolveLlmModelOptionChoice` | Function | Y |
| 584 | type | `LlmModelInfo` | Type/interface | Y |
| 615 | type | `LlmModelListResult` | Type/interface | Y |
| 625 | type | `LlmModelFetchRequest` | Type/interface | Y |
| 633 | type | `LlmProviderTestResult` | Provider | Y |
| 640 | type | `ClientBootstrap` | Type/interface | Y |
| 649 | type | `CapabilitySelection` | Type/interface | Y |
| 655 | type | `ClientToolConfirmation` | Type/interface | Y |
| 663 | type | `RuntimeToolCall` | Type/interface | Y |
| 671 | type | `RuntimeToolResult` | Type/interface | Y |
| 678 | type | `RuntimeExecuteRequest` | Type/interface | Y |
| 686 | type | `RuntimeExecutionContext` | Type/interface | Y |
| 691 | type | `ClientToolCall` | Type/interface | Y |
| 702 | type | `ClientToolCallPollRequest` | Type/interface | Y |
| 711 | type | `ClientToolCallPollResult` | Type/interface | Y |
| 717 | type | `PermissionDuration` | Type/interface | Y |
| 719 | type | `PermissionGrant` | Type/interface | Y |
| 728 | type | `LocalShellExecInput` | Type/interface | Y |
| 736 | type | `LocalShellStopInput` | Type/interface | Y |
| 741 | type | `LocalShellExecResult` | Type/interface | Y |
| 753 | type | `ShellPermissionBehavior` | Type/interface | Y |
| 755 | type | `ShellPermissionRule` | Type/interface | Y |
| 769 | type | `LocalShellProjectionPolicy` | Type/interface | Y |
| 778 | type | `Evidence` | Type/interface | Y |
| 789 | type | `ClientToolResult` | Type/interface | Y |
| 797 | type | `ClientToolResultReport` | Type/interface | Y |
| 806 | type | `AuditEvent` | Type/interface | Y |

#### `packages/protocol/src/memory.ts` (12 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 1 | type | `WorkingMemorySection` | Type/interface | Y |
| 9 | type | `WorkingMemorySnapshotEntry` | Type/interface | Y |
| 19 | type | `WorkingMemorySnapshotJson` | Type/interface | Y |
| 30 | type | `WorkingMemoryPromptSection` | Type/interface | Y |
| 41 | type | `WorkingMemoryData` | Type/interface | Y |
| 51 | type | `MemoryWikiCompileStatus` | Type/interface | Y |
| 52 | type | `MemoryWikiCompileMode` | Type/interface | Y |
| 54 | type | `InitializeConversationMemoryWikiResult` | Type/interface | Y |
| 66 | type | `ConversationMemoryWikiStatus` | Type/interface | Y |
| 83 | type | `ConversationMemoryWikiPage` | Type/interface | Y |
| 103 | type | `ConversationMemoryWikiPageListData` | Type/interface | Y |
| 111 | type | `ConversationMemoryCompileStatus` | Type/interface | Y |

#### `packages/protocol/src/system-context.ts` (22 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 1 | type | `AttachmentContextKind` | Type/interface | Y |
| 3 | type | `AttachmentContextTransport` | Type/interface | Y |
| 9 | type | `AttachmentContextItem` | Type/interface | Y |
| 19 | type | `ContextAttachmentSourceKind` | Type/interface | Y |
| 29 | type | `ContextAttachmentScope` | Type/interface | Y |
| 31 | type | `ContextAttachmentLifecycle` | Type/interface | Y |
| 33 | type | `ContextAttachmentItem` | Type/interface | Y |
| 40 | type | `RuntimeReminderKind` | Type/interface | Y |
| 49 | type | `RuntimeReminderScope` | Type/interface | Y |
| 51 | type | `RuntimeReminderItem` | Type/interface | Y |
| 63 | type | `ContinuityContextItem` | Type/interface | Y |
| 73 | type | `ConfigInstructionContextItem` | Type/interface | Y |
| 81 | type | `ContextExtensionItem` | Type/interface | Y |
| 91 | type | `ChatProviderMessage` | Provider | Y |
| 96 | type | `ChatSendRequest` | Type/interface | Y |
| 128 | type | `PromptSnapshotSectionRef` | Type/interface | Y |
| 135 | type | `PromptSnapshotIndexEntry` | Type/interface | Y |
| 154 | type | `PromptSnapshotRecord` | Type/interface | Y |
| 163 | type | `PromptBaselineRecord` | Type/interface | Y |
| 181 | type | `PromptContextEpochRecord` | Type/interface | Y |
| 200 | type | `PromptContextEpochEventType` | Type/interface | Y |
| 205 | type | `PromptContextEpochEventRecord` | Type/interface | Y |

#### `packages/protocol/src/updater.ts` (6 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 9 | type | `UpdateChannel` | Type/interface | Y |
| 16 | type | `UpdateChannelPreference` | Type/interface | Y |
| 19 | type | `UpdaterPhase` | Type/interface | Y |
| 36 | type | `UpdaterEvent` | Type/interface | Y |
| 55 | type | `UpdaterStatus` | Type/interface | Y |
| 87 | type | `UpdaterSettings` | Type/interface | Y |

#### `packages/runtime-core/src/capability-registry.ts` (6 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 10 | type | `CapabilityRegistryErrorCode` | Type/interface | Y |
| 16 | constructor | `CapabilityRegistryError` | Class | Y |
| 26 | function | `providerCapabilityIds` | Function |  |
| 36 | function | `assertProvider` | Provider |  |
| 57 | type | `CapabilityProviderRegistry` | Provider | Y |
| 66 | function | `createCapabilityProviderRegistry` | Provider | Y |

#### `packages/runtime-core/src/contracts.ts` (42 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 1 | type | `RuntimeCapabilityId` | Type/interface | Y |
| 2 | type | `RuntimeProviderId` | Provider | Y |
| 3 | type | `RuntimeRunId` | Type/interface | Y |
| 4 | type | `RuntimeSessionId` | Type/interface | Y |
| 6 | type | `RuntimeDecision` | Type/interface | Y |
| 8 | type | `RuntimeToolStatus` | Type/interface | Y |
| 16 | type | `RuntimeRiskLevel` | Type/interface | Y |
| 25 | type | `RuntimeModeScope` | Type/interface | Y |
| 27 | type | `RuntimeJsonObject` | Type/interface | Y |
| 29 | type | `RuntimeWorkspaceRef` | Type/interface | Y |
| 35 | type | `RuntimeToolCall` | Type/interface | Y |
| 46 | type | `RuntimeToolError` | Type/interface | Y |
| 53 | type | `RuntimeToolResult` | Type/interface | Y |
| 65 | type | `CapabilityManifest` | Type/interface | Y |
| 76 | type | `CapabilityRequest` | Type/interface | Y |
| 83 | type | `CapabilityResult` | Type/interface | Y |
| 85 | type | `CapabilityProvider` | Provider | Y |
| 97 | type | `CapabilityExecutionContext` | Type/interface | Y |
| 99 | type | `RuntimeExecutionContext` | Type/interface | Y |
| 113 | type | `RuntimeLogger` | Type/interface | Y |
| 120 | type | `PermissionRequest` | Type/interface | Y |
| 128 | type | `PermissionDecision` | Type/interface | Y |
| 135 | type | `PermissionGrant` | Type/interface | Y |
| 146 | type | `PermissionPolicy` | Type/interface | Y |
| 154 | type | `HumanApprovalRequest` | Type/interface | Y |
| 159 | type | `HumanApprovalPort` | Type/interface | Y |
| 166 | type | `PermissionGateway` | Type/interface | Y |
| 178 | type | `HookEventName` | Type/interface | Y |
| 187 | type | `HookDecision` | Type/interface | Y |
| 189 | type | `HookInput` | Type/interface | Y |
| 196 | type | `HookRecord` | Type/interface | Y |
| 208 | type | `HookRunner` | Type/interface | Y |
| 216 | type | `HookPipeline` | Type/interface | Y |
| 218 | type | `EvidenceRef` | Type/interface | Y |
| 220 | type | `EvidenceRecord` | Type/interface | Y |
| 233 | type | `EvidenceBundle` | Type/interface | Y |
| 239 | type | `EvidenceSink` | Type/interface | Y |
| 246 | type | `RuntimeEvent` | Type/interface | Y |
| 278 | type | `RuntimeEventSink` | Type/interface | Y |
| 282 | type | `RuntimeToolDefinition` | Type/interface | Y |
| 291 | type | `RuntimeProjection` | Type/interface | Y |
| 298 | type | `ProjectionMaterializer` | Type/interface | Y |

#### `packages/runtime-core/src/decision.ts` (3 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 9 | function | `compareRuntimeDecision` | Function | Y |
| 13 | function | `mostRestrictiveDecision` | Function | Y |
| 28 | function | `isDecisionAtLeast` | Function | Y |

#### `packages/runtime-core/src/evidence.ts` (14 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 8 | type | `EvidenceRedactor` | Type/interface | Y |
| 10 | type | `RuntimeEvidenceObject` | Type/interface | Y |
| 12 | type | `CreateEvidenceBundleOptions` | Type/interface | Y |
| 26 | type | `AppendEvidenceRecordsOptions` | Type/interface | Y |
| 31 | type | `HookEvidenceRecordSource` | Type/interface | Y |
| 42 | type | `HookEvidenceRecord` | Type/interface | Y |
| 52 | type | `AppendHookEvidenceOptions` | Type/interface | Y |
| 57 | function | `isEvidenceObject` | Function |  |
| 61 | function | `asReadonlyArray` | Function |  |
| 65 | function | `createEvidenceBundle` | Function | Y |
| 83 | function | `applyEvidenceRedactors` | Function | Y |
| 90 | function | `appendEvidenceRecords` | Function | Y |
| 127 | function | `sanitizeHookEvidenceRecord` | Function | Y |
| 139 | function | `appendHookEvidence` | Function | Y |

#### `packages/runtime-core/src/hooks.ts` (2 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 4 | type | `HookDecisionSource` | Type/interface | Y |
| 8 | function | `mostRestrictiveHookDecision` | Function | Y |

#### `packages/runtime-core/src/permission.ts` (10 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 11 | type | `PermissionDecisionLike` | Type/interface | Y |
| 13 | type | `MergePermissionDecisionsOptions` | Type/interface | Y |
| 18 | type | `CreatePermissionGrantDraftOptions` | Type/interface | Y |
| 25 | function | `decisionValue` | Function |  |
| 35 | function | `mostRestrictivePermissionDecision` | Function | Y |
| 41 | function | `mergePermissionDecisions` | Function | Y |
| 60 | function | `isPermissionAllowed` | Function | Y |
| 64 | function | `isPermissionAsking` | Function | Y |
| 68 | function | `isPermissionDenied` | Function | Y |
| 72 | function | `createPermissionGrantDraft` | Function | Y |

#### `packages/runtime-core/src/projection-materializers.ts` (6 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 7 | type | `OpenAIFunctionToolSchema` | Type/interface | Y |
| 16 | type | `AnthropicToolSchema` | Type/interface | Y |
| 22 | function | `toolDescription` | Function |  |
| 26 | function | `toolInputSchema` | Function |  |
| 33 | function | `materializeOpenAITools` | Function | Y |
| 46 | function | `materializeAnthropicTools` | Function | Y |

#### `packages/runtime-core/src/projection.ts` (8 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 8 | type | `RuntimeProjectionErrorCode` | Type/interface | Y |
| 12 | constructor | `RuntimeProjectionError` | Class | Y |
| 22 | type | `CreateRuntimeProjectionOptions` | Type/interface | Y |
| 29 | function | `assertToolDefinition` | Function |  |
| 66 | function | `freezeToolDefinition` | Function |  |
| 81 | function | `isRuntimeToolAvailableInMode` | Function | Y |
| 94 | function | `filterRuntimeToolsForMode` | Function | Y |
| 101 | function | `createRuntimeProjection` | Function | Y |

#### `packages/runtime-node/src/chatgpt-oauth.ts` (1 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 6 | function | `refreshChatGptOAuthTokens` | Function | Y |

#### `packages/runtime-node/src/chatgpt-responses-provider.ts` (7 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 13 | type | `CreateChatGptResponsesProviderOptions` | Provider | Y |
| 22 | function | `messageInput` | Function |  |
| 41 | function | `requestBody` | Function |  |
| 59 | function | `usageOf` | Function |  |
| 67 | function | `consumeResponsesStream` | Function |  |
| 134 | function | `createChatGptResponsesProvider` | Provider | Y |
| 138 | method | `stream` | Method |  |

#### `packages/runtime-node/src/contracts.ts` (11 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 12 | type | `NodeRuntimeSession` | Type/interface | Y |
| 17 | type | `NodeRuntimePermissionResponse` | Type/interface | Y |
| 24 | type | `NodeRuntimeHookPermissionPrompt` | Type/interface | Y |
| 44 | type | `NodeRuntimeCapabilityPermissionPrompt` | Type/interface | Y |
| 66 | type | `NodeRuntimePermissionPrompt` | Type/interface | Y |
| 70 | type | `NodeRuntimeExecutionContext` | Type/interface | Y |
| 76 | type | `NodeRuntimeProviderExecutor` | Provider | Y |
| 90 | type | `NodeRuntimeResultFactory` | Type/interface | Y |
| 104 | type | `CreateNodeRuntimeHostAdapterOptions` | Type/interface | Y |
| 120 | type | `NodeRuntimeApprovalDecision` | Type/interface | Y |
| 124 | type | `NodeRuntimeApprovalRequest` | Type/interface | Y |

#### `packages/runtime-node/src/file-provider.ts` (7 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 84 | function | `relativeDisplayPath` | Function |  |
| 89 | function | `assertExistingPathInsideWorkspace` | Function |  |
| 100 | function | `assertWritePathInsideWorkspace` | Function |  |
| 127 | function | `requireString` | Function |  |
| 139 | function | `cancelledResult` | Function |  |
| 152 | function | `createNodeFileProvider` | Provider | Y |
| 163 | method | `execute` | Method |  |

#### `packages/runtime-node/src/host-adapter.ts` (3 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 13 | function | `resolveLocale` | Function |  |
| 17 | function | `defaultDataLevel` | Function |  |
| 21 | function | `createNodeRuntimeHostAdapter` | Function | Y |

#### `packages/runtime-node/src/model-catalog.ts` (7 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 1 | type | `ModelReasoningEffort` | Type/interface | Y |
| 3 | type | `RuntimePermissionPolicy` | Type/interface | Y |
| 5 | type | `RuntimeModelCatalogEntry` | Type/interface | Y |
| 17 | type | `RuntimeModelSelection` | Type/interface | Y |
| 23 | function | `normalizeModelReasoningEffort` | Parser/normalizer | Y |
| 33 | function | `isRuntimeModelSelectionAvailable` | Function | Y |
| 52 | function | `normalizeRuntimePermissionPolicy` | Parser/normalizer | Y |

#### `packages/runtime-node/src/model-provider-contracts.ts` (15 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 3 | type | `ModelMessageRole` | Type/interface | Y |
| 5 | type | `ModelMessage` | Type/interface | Y |
| 13 | type | `ModelToolDefinition` | Type/interface | Y |
| 19 | type | `ModelToolCall` | Type/interface | Y |
| 25 | type | `ModelUsage` | Type/interface | Y |
| 33 | type | `ModelStreamEvent` | Type/interface | Y |
| 40 | type | `ModelProviderRequest` | Provider | Y |
| 51 | type | `ModelProviderResult` | Provider | Y |
| 58 | type | `ModelProvider` | Provider | Y |
| 62 | type | `ModelCredentialRequest` | Type/interface | Y |
| 67 | type | `ModelCredential` | Type/interface | Y |
| 74 | type | `ModelCredentialPort` | Type/interface | Y |
| 78 | type | `OpenAICompatibleProviderConfig` | Provider | Y |
| 86 | constructor | `ModelCredentialNotFoundError` | Class | Y |
| 96 | function | `resolveOpenAICompatibleProviderConfig` | Provider | Y |

#### `packages/runtime-node/src/node-hook-config.ts` (8 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 11 | type | `LoadNodeHookConfigOptions` | Type/interface | Y |
| 16 | type | `CreateConfiguredNodeHookRunnerOptions` | Type/interface | Y |
| 20 | function | `readJsonIfExists` | Function |  |
| 29 | function | `normalizeHookList` | Parser/normalizer |  |
| 46 | function | `mergeNodeHookConfigs` | Function | Y |
| 62 | function | `getNodeHookConfigPaths` | Function | Y |
| 69 | function | `loadNodeHookConfig` | Function | Y |
| 74 | function | `createConfiguredNodeHookRunner` | Function | Y |

#### `packages/runtime-node/src/node-hook-runner.ts` (16 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 12 | type | `NodeHookEvent` | Type/interface | Y |
| 13 | type | `NodeHookFailureMode` | Type/interface | Y |
| 15 | type | `NodeHookDefinition` | Type/interface | Y |
| 27 | type | `NodeHookConfig` | Type/interface | Y |
| 32 | type | `CreateNodeHookRunnerOptions` | Type/interface | Y |
| 38 | function | `globToRegExp` | Function |  |
| 46 | function | `matchesPattern` | Function |  |
| 51 | function | `argumentsString` | Function |  |
| 61 | function | `matchesNodeHook` | Function | Y |
| 67 | function | `failureDecision` | Function |  |
| 72 | function | `parseDecision` | Parser/normalizer |  |
| 87 | type | `SpawnOutcome` | Type/interface |  |
| 96 | function | `spawnCommand` | Function |  |
| 130 | function | `runNodeHookCommand` | Function |  |
| 166 | function | `createNodeHookRunner` | Function | Y |
| 189 | function | `mostRestrictiveNodeHookDecision` | Function | Y |

#### `packages/runtime-node/src/openai-chat-stream.ts` (15 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 8 | type | `OpenAIChatStreamError` | Type/interface | Y |
| 13 | type | `OpenAIChatStreamResult` | Type/interface | Y |
| 17 | type | `ConsumeOpenAIChatStreamOptions` | Type/interface | Y |
| 31 | constructor | `ModelProviderStreamError` | Provider | Y |
| 41 | type | `OpenAIChunk` | Type/interface |  |
| 73 | type | `MutableToolCall` | Type/interface |  |
| 75 | function | `textLike` | Function |  |
| 90 | type | `OpenAIChoiceDelta` | Type/interface |  |
| 92 | function | `reasoningDelta` | Function |  |
| 109 | function | `usageFrom` | Function |  |
| 125 | function | `streamErrorFrom` | Function |  |
| 133 | function | `normalizeToolCalls` | Parser/normalizer |  |
| 139 | function | `idleTimeoutError` | Function |  |
| 145 | function | `readChunk` | Function |  |
| 165 | function | `consumeOpenAIChatStream` | Function | Y |

#### `packages/runtime-node/src/openai-compatible-provider.ts` (7 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 12 | type | `CreateOpenAICompatibleProviderOptions` | Provider | Y |
| 17 | constructor | `ModelProviderHttpError` | Provider | Y |
| 31 | function | `endpoint` | Function |  |
| 35 | function | `serializeMessage` | Function |  |
| 49 | function | `errorDetail` | Function |  |
| 58 | function | `createOpenAICompatibleProvider` | Provider | Y |
| 64 | method | `stream` | Method |  |

#### `packages/runtime-node/src/provider-bundle.ts` (4 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 32 | function | `manifestToToolDefinition` | Function |  |
| 46 | function | `toCoreContext` | Function |  |
| 71 | function | `createNodeProviderBundle` | Provider | Y |
| 209 | method | `execute` | Method |  |

#### `packages/runtime-node/src/provider-contracts.ts` (7 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 23 | type | `NodeCapabilityApprovalKind` | Type/interface | Y |
| 25 | type | `NodeCapabilityPermissionPrompt` | Type/interface | Y |
| 32 | type | `NodeCapabilityApprovalPort` | Type/interface | Y |
| 36 | type | `NodeFileProviderOptions` | Provider | Y |
| 44 | type | `NodeShellProviderOptions` | Provider | Y |
| 56 | type | `CreateNodeProviderBundleOptions` | Provider | Y |
| 71 | type | `NodeProviderBundle` | Provider | Y |

#### `packages/runtime-node/src/provider-utils.ts` (9 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 18 | type | `NodeProviderRuntimeClock` | Provider | Y |
| 23 | type | `NodeProviderToolResult` | Provider | Y |
| 27 | function | `createProviderRuntimeClock` | Provider | Y |
| 37 | function | `asRecord` | Function | Y |
| 43 | function | `resolveWorkspacePath` | Function | Y |
| 56 | function | `createNodePermissionGrant` | Function | Y |
| 80 | function | `createNodeToolResult` | Function | Y |
| 130 | function | `createNodeResultFactory` | Function | Y |
| 172 | function | `appendNodeHookEvidence` | Function | Y |

#### `packages/runtime-node/src/shared-model-config.ts` (25 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 15 | type | `SharedModelAuthMethod` | Type/interface | Y |
| 22 | type | `StoredModelProvider` | Provider | Y |
| 39 | type | `ChatGptOAuthTokens` | Type/interface | Y |
| 46 | type | `SharedModelCredentialStore` | Store | Y |
| 52 | type | `SharedModelMetadata` | Type/interface | Y |
| 64 | type | `SharedModelSelection` | Type/interface | Y |
| 70 | type | `LoadSharedModelSelectionOptions` | Type/interface | Y |
| 82 | function | `getSharedModelConfigPath` | Function | Y |
| 88 | function | `isRecord` | Function |  |
| 92 | function | `groupKeyOf` | Function |  |
| 104 | function | `parseProviders` | Provider |  |
| 169 | function | `channelFromProvider` | Provider |  |
| 181 | function | `modelFromProvider` | Provider |  |
| 198 | function | `serializeProvidersDocument` | Provider |  |
| 252 | function | `normalizedAuthMethod` | Parser/normalizer |  |
| 264 | function | `credentialIdOf` | Function |  |
| 268 | function | `hasStoredCredential` | Store |  |
| 282 | function | `selectDesktopDefaultProvider` | Provider | Y |
| 295 | function | `selectedProvider` | Provider |  |
| 314 | function | `metadataFromSelected` | Function |  |
| 331 | function | `writeProvidersAtomically` | Provider |  |
| 363 | function | `loadSharedModelMetadata` | Function | Y |
| 371 | function | `loadSharedModelMetadataList` | Function | Y |
| 382 | function | `loadSharedModelSelection` | Function | Y |
| 412 | method | `persistOAuthTokens` | Method |  |

#### `packages/runtime-node/src/shell-classifier.ts` (14 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 12 | type | `NodeShellRiskLevel` | Type/interface | Y |
| 13 | type | `NodeShellCategory` | Type/interface | Y |
| 23 | type | `NodeShellClassification` | Type/interface | Y |
| 57 | function | `insideDirectory` | Function |  |
| 62 | function | `normalizeNodeShellCwd` | Parser/normalizer | Y |
| 73 | function | `stripQuotes` | Function |  |
| 85 | function | `words` | Function |  |
| 94 | function | `commandName` | Function |  |
| 98 | function | `classification` | Function |  |
| 114 | function | `classifySegment` | Function |  |
| 149 | function | `splitCommandSegments` | Function |  |
| 195 | function | `classifyCommandText` | Function |  |
| 205 | function | `classifyNodeShellCommand` | Function | Y |
| 225 | function | `compareNodeShellRisk` | Function | Y |

#### `packages/runtime-node/src/shell-provider.ts` (8 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 46 | type | `ShellOutput` | Type/interface |  |
| 56 | function | `normalizeTimeout` | Parser/normalizer |  |
| 61 | function | `capOutput` | Function |  |
| 68 | function | `runShellCommand` | Function |  |
| 167 | function | `requireCommand` | Function |  |
| 174 | function | `classificationMetadata` | Function |  |
| 186 | function | `createNodeShellProvider` | Provider | Y |
| 200 | method | `execute` | Method |  |

#### `packages/runtime-sdk/src/contracts.ts` (30 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 18 | type | `RuntimeEventProtocolVersion` | Type/interface | Y |
| 20 | type | `RuntimeSdkEventType` | Type/interface | Y |
| 32 | type | `RuntimeSdkToolCall` | Type/interface | Y |
| 33 | type | `RuntimeSdkExecuteRequest` | Type/interface | Y |
| 34 | type | `RuntimeSdkExecutionContext` | Type/interface | Y |
| 35 | type | `RuntimeSdkToolResult` | Type/interface | Y |
| 37 | type | `RuntimeSdkProviderExecution` | Provider | Y |
| 42 | type | `RuntimeSdkHookRecord` | Type/interface | Y |
| 49 | type | `RuntimeSdkHookPayload` | Type/interface | Y |
| 57 | type | `RuntimeSdkHookRunner` | Type/interface | Y |
| 62 | type | `RuntimeSdkPermissionRequest` | Type/interface | Y |
| 73 | type | `RuntimeSdkApprovalDecision` | Type/interface | Y |
| 78 | type | `RuntimeSdkApprovalPort` | Type/interface | Y |
| 85 | type | `RuntimeSdkHostAdapter` | Type/interface | Y |
| 106 | type | `RuntimeSdkEventBase` | Type/interface | Y |
| 119 | type | `RuntimeSdkSessionStartedEvent` | Type/interface | Y |
| 128 | type | `RuntimeSdkMessageDeltaEvent` | Type/interface | Y |
| 134 | type | `RuntimeSdkReasoningDeltaEvent` | Type/interface | Y |
| 140 | type | `RuntimeSdkMessageCompletedEvent` | Type/interface | Y |
| 149 | type | `RuntimeSdkRuntimeErrorEvent` | Type/interface | Y |
| 157 | type | `RuntimeSdkToolStartedEvent` | Type/interface | Y |
| 163 | type | `RuntimeSdkHookCompletedEvent` | Type/interface | Y |
| 172 | type | `RuntimeSdkPermissionRequestedEvent` | Type/interface | Y |
| 179 | type | `RuntimeSdkPermissionResolvedEvent` | Type/interface | Y |
| 186 | type | `RuntimeSdkToolCompletedEvent` | Type/interface | Y |
| 194 | type | `RuntimeSdkEvent` | Type/interface | Y |
| 206 | type | `RuntimeSdkEventInput` | Type/interface | Y |
| 212 | type | `RuntimeSdkEventListener` | Type/interface | Y |
| 214 | type | `RuntimeSdkOptions` | Type/interface | Y |
| 220 | type | `RuntimeSdk` | Type/interface | Y |

#### `packages/runtime-sdk/src/goal-contracts.ts` (12 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 1 | type | `RuntimeGoalStatus` | Type/interface | Y |
| 10 | type | `RuntimeGoalTaskStatus` | Type/interface | Y |
| 18 | type | `RuntimeGoalTaskInput` | Type/interface | Y |
| 23 | type | `RuntimeGoalSuccessCriterion` | Type/interface | Y |
| 27 | type | `RuntimeGoalTaskSnapshot` | Type/interface | Y |
| 35 | type | `RuntimeGoalSnapshot` | Type/interface | Y |
| 49 | type | `RuntimeGoalCreateOptions` | Type/interface | Y |
| 59 | type | `RuntimeGoalTaskExecutionResult` | Type/interface | Y |
| 64 | type | `RuntimeGoalTaskExecutionContext` | Type/interface | Y |
| 72 | type | `RuntimeGoalTaskExecutor` | Type/interface | Y |
| 77 | type | `RuntimeGoalControllerOptions` | Controller | Y |
| 83 | type | `RuntimeGoalController` | Controller | Y |

#### `packages/runtime-sdk/src/goal-controller.ts` (2 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 10 | type | `GoalRecord` | Type/interface |  |
| 17 | function | `createRuntimeGoalController` | Controller | Y |

#### `packages/runtime-sdk/src/pipeline-contracts.ts` (15 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 7 | type | `RuntimePipelineStatus` | Type/interface | Y |
| 13 | type | `RuntimePipelineRunInput` | Type/interface | Y |
| 24 | type | `RuntimePipelineToolCall` | Type/interface | Y |
| 32 | type | `RuntimePipelineToolExecution` | Type/interface | Y |
| 42 | type | `RuntimePipelineTurnContext` | Type/interface | Y |
| 49 | type | `RuntimePipelineContinueTurn` | Type/interface | Y |
| 54 | type | `RuntimePipelineCompletedTurn` | Type/interface | Y |
| 61 | type | `RuntimePipelineToolCallsTurn` | Type/interface | Y |
| 70 | type | `RuntimePipelineTurnResult` | Type/interface | Y |
| 79 | type | `RuntimePipelineModelAdapter` | Type/interface | Y |
| 120 | type | `RuntimePipelineToolExecutor` | Type/interface | Y |
| 132 | type | `RuntimePipelineEventSink` | Type/interface | Y |
| 136 | type | `RuntimePipelineOptions` | Type/interface | Y |
| 149 | type | `RuntimePipelineRunResult` | Type/interface | Y |
| 161 | type | `RuntimePipeline` | Type/interface | Y |

#### `packages/runtime-sdk/src/pipeline.ts` (5 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 13 | function | `normalizeMaxTurns` | Parser/normalizer |  |
| 19 | function | `isAbortError` | Function |  |
| 23 | function | `errorMessage` | Function |  |
| 28 | function | `throwIfAborted` | Function |  |
| 36 | function | `createRuntimePipeline` | Function | Y |

#### `packages/runtime-sdk/src/runtime.ts` (3 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 16 | function | `normalizeRecords` | Parser/normalizer |  |
| 20 | function | `createRuntimeEventId` | Function |  |
| 25 | function | `createRuntimeSdk` | Function | Y |

#### `packages/runtime-sdk/src/session-contracts.ts` (9 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 1 | type | `RuntimeSessionStatus` | Type/interface | Y |
| 2 | type | `RuntimeTurnStatus` | Type/interface | Y |
| 4 | type | `RuntimeSessionTurnSnapshot` | Type/interface | Y |
| 14 | type | `RuntimeSessionSnapshot` | Type/interface | Y |
| 25 | type | `RuntimeSessionStartOptions` | Type/interface | Y |
| 32 | type | `RuntimeSessionResumeOptions` | Type/interface | Y |
| 38 | type | `RuntimeSessionTurnHandle` | Type/interface | Y |
| 51 | type | `RuntimeSessionControllerOptions` | Controller | Y |
| 57 | type | `RuntimeSessionController` | Controller | Y |

#### `packages/runtime-sdk/src/session-controller.ts` (5 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 12 | type | `ActiveTurn` | Type/interface |  |
| 18 | type | `SessionRecord` | Type/interface |  |
| 28 | function | `normalizeReason` | Parser/normalizer |  |
| 32 | function | `snapshotSession` | Function |  |
| 45 | function | `createRuntimeSessionController` | Controller | Y |

#### `packages/task-thread/src/index.ts` (5 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 11 | type | `ThreadEvent` | Type/interface | Y |
| 52 | type | `TaskThread` | Type/interface | Y |
| 58 | function | `now` | Function |  |
| 60 | function | `createToolCallFromCapability` | Function | Y |
| 78 | function | `applyToolResult` | Function | Y |

#### `packages/ui/src/index.tsx` (4 symbols)

| Line | category | Name | Role | Export |
|-----:|----------|------|------|:------:|
| 5 | component | `StatusBadge` | React Component | Y |
| 9 | component | `AccessLevelLabel` | React Component | Y |
| 22 | component | `ToolCallCard` | React Component | Y |
| 50 | component | `ReviewCard` | React Component | Y |


---

## 关键运行时调用链

### 治理主链（架构契约）

```text
Capability Provider
  → Manifest (capabilities/*.json + 运行时注册)
    → Runtime Projection (buildRuntimeProjection / runtime-projection:get)
      → Tool Call (模型 tool_call / projected tool)
        → PermissionGrant (permission:approve|deny / createPermissionGrant)
          → Evidence (tool result / evidence refs)
```

该链路由 Main 拥有；Renderer 只表达与触发，不持有权限真值。

### 应用启动与窗口

```text
Electron 启动
  → apps/desktop/electron/main/main.mjs
    → 初始化 stores / registries / llmChatService / localToolHost
    → createWindow()
      → BrowserWindow + preload.cjs
        → 加载 Vite/打包后的 renderer
          → React App (renderer/src)
            → clientApi / window.peerAgent.*
```

### 对话发送与流式回传

```text
Renderer UI (chat compose)
  → peerAgent.chatSend / clientApi
    → IPC chat:send (main.mjs)
      → (goal mode) goalPlanStore intake/route
      → llmChatService.sendMessage({ messages, webContents, streamId, mode, ... })
        → provider 选择 / adapter
        → agentLoop{OpenAI|Anthropic|Gemini|Qoder}
          → 模型流式事件 → webContents 推送
          → 若 tool_call:
               projected-tool-executor
                 → goal-mode-gate / 能力准入
                 → PermissionGrant 等待或规则匹配
                 → local-tool-host.execute
                 → Evidence / ClientToolResult
                 → 回灌 agent loop
```

### Runtime Projection 与工具暴露

```text
IPC runtime-projection:get
  → buildRuntimeProjection() in main.mjs
    → 聚合 local capabilities + skills + MCP tools + policy
      → 返回模型可见工具清单（非直接执行句柄）
```

### 权限决议

```text
Agent loop / tool executor 需要授权
  → 向 Renderer 发 permission request 事件
    → 用户批准/拒绝 UI
      → peerAgent.approveLocalAction / denyLocalAction
        → IPC permission:approve | permission:deny
          → createPermissionGrant(...)
          → llmChatService.resolvePermissionGrant(toolCallId, grant)
            → 恢复 projected-tool-executor
```

### 本地能力执行

```text
executeProjectedModelTool(...)
  → createLocalToolHost(...)
    → Provider / capabilityId 路由
      → shell / fs / web / browser control / MCP / skill ...
        → 结构化 Tool Result + Evidence
```

### Goal 模式

```text
chat:send (mode=goal)
  → goal 消息路由 (start_intake / append_goal_event / ...)
  → goalPlanStore.createIntakeContract | upsertGoalContract
  → Goal Runner 自驱执行
    → 工具调用仍走 Runtime Projection + PermissionGrant
    → goalPlans:recordTaskEvidence / goal_update_task 等价路径回写 evidenceRefs
```

### IPC 通道分组（共 146）

| 前缀 | 数量 | 示例 |
|------|-----:|------|
| `conversations` | 18 | `conversations:add-usage`, `conversations:append-message`, `conversations:archive`, `conversations:auto-archive`, `conversations:create` …+13 |
| `llm` | 18 | `llm:add`, `llm:add-model`, `llm:channels:list`, `llm:chat:list`, `llm:duplicate` …+13 |
| `mcp` | 17 | `mcp:connect-and-register`, `mcp:delete-credential`, `mcp:finish-oauth`, `mcp:get-prompt`, `mcp:install` …+12 |
| `goalPlans` | 10 | `goalPlans:approve`, `goalPlans:awaiting-counts`, `goalPlans:create`, `goalPlans:delete`, `goalPlans:get` …+5 |
| `skills` | 8 | `skills:disable`, `skills:enable`, `skills:link`, `skills:list`, `skills:list-available` …+3 |
| `updater` | 7 | `updater:check`, `updater:download`, `updater:get-status`, `updater:install`, `updater:open-installer` …+2 |
| `chat` | 6 | `chat:abort`, `chat:compact`, `chat:compaction:get`, `chat:send`, `chat:stream:list-active` …+1 |
| `shell` | 6 | `shell:open-path`, `shell:permissions:add`, `shell:permissions:list`, `shell:tasks:list`, `shell:tasks:stop` …+1 |
| `workspace` | 6 | `workspace:add`, `workspace:ensure-default`, `workspace:info`, `workspace:list`, `workspace:remove` …+1 |
| `goalRunner` | 5 | `goalRunner:clear`, `goalRunner:get-state`, `goalRunner:pause`, `goalRunner:resume`, `goalRunner:start` |
| `settings` | 5 | `settings:export`, `settings:get`, `settings:get-sync`, `settings:import`, `settings:update` |
| `developer-settings` | 4 | `developer-settings:diagnostics`, `developer-settings:get`, `developer-settings:reset`, `developer-settings:update` |
| `pending-task` | 4 | `pending-task:clear`, `pending-task:consume`, `pending-task:peek`, `pending-task:write` |
| `quick-chat` | 4 | `quick-chat:hide`, `quick-chat:set-content-height`, `quick-chat:set-task-card-visible`, `quick-chat:submit` |
| `prompt-context-epochs` | 3 | `prompt-context-epochs:chain`, `prompt-context-epochs:events`, `prompt-context-epochs:list` |
| `quick-chat-popover` | 3 | `quick-chat-popover:hide`, `quick-chat-popover:select`, `quick-chat-popover:show` |
| `shortcuts` | 3 | `shortcuts:reset`, `shortcuts:status`, `shortcuts:update` |
| `browser` | 2 | `browser:register-webcontents`, `browser:unregister-webcontents` |
| `fs` | 2 | `fs:exists`, `fs:read-dir` |
| `permission` | 2 | `permission:approve`, `permission:deny` |
| `prompt-snapshots` | 2 | `prompt-snapshots:get`, `prompt-snapshots:list` |
| `bootstrap` | 1 | `bootstrap:get` |
| `capabilities` | 1 | `capabilities:list` |
| `client-tool` | 1 | `client-tool:execute` |
| `file` | 1 | `file:read` |
| `git` | 1 | `git:diff` |
| `host` | 1 | `host:restart` |
| `locale` | 1 | `locale:set` |
| `projects` | 1 | `projects:list` |
| `runtime-projection` | 1 | `runtime-projection:get` |
| `session` | 1 | `session:get` |
| `usage` | 1 | `usage:stats` |

### 完整 IPC 通道列表

- `bootstrap:get`
- `browser:register-webcontents`
- `browser:unregister-webcontents`
- `capabilities:list`
- `chat:abort`
- `chat:compact`
- `chat:compaction:get`
- `chat:send`
- `chat:stream:list-active`
- `chat:stream:reattach`
- `client-tool:execute`
- `conversations:add-usage`
- `conversations:append-message`
- `conversations:archive`
- `conversations:auto-archive`
- `conversations:create`
- `conversations:delete`
- `conversations:get`
- `conversations:list`
- `conversations:pin`
- `conversations:reorder-pinned`
- `conversations:replace-messages`
- `conversations:restore`
- `conversations:search`
- `conversations:unpin`
- `conversations:update-last-message`
- `conversations:update-mode`
- `conversations:update-model-effort`
- `conversations:update-title`
- `developer-settings:diagnostics`
- `developer-settings:get`
- `developer-settings:reset`
- `developer-settings:update`
- `file:read`
- `fs:exists`
- `fs:read-dir`
- `git:diff`
- `goalPlans:approve`
- `goalPlans:awaiting-counts`
- `goalPlans:create`
- `goalPlans:delete`
- `goalPlans:get`
- `goalPlans:list`
- `goalPlans:record-manual-confirmation`
- `goalPlans:record-task-evidence`
- `goalPlans:revise`
- `goalPlans:set-status`
- `goalRunner:clear`
- `goalRunner:get-state`
- `goalRunner:pause`
- `goalRunner:resume`
- `goalRunner:start`
- `host:restart`
- `llm:add`
- `llm:add-model`
- `llm:channels:list`
- `llm:chat:list`
- `llm:duplicate`
- `llm:groups:list`
- `llm:list`
- `llm:models:fetch`
- `llm:models:list`
- `llm:oauth:cancel`
- `llm:oauth:open-pending`
- `llm:oauth:start`
- `llm:quota`
- `llm:remove`
- `llm:remove-group`
- `llm:set-default`
- `llm:test`
- `llm:update`
- `locale:set`
- `mcp:connect-and-register`
- `mcp:delete-credential`
- `mcp:finish-oauth`
- `mcp:get-prompt`
- `mcp:install`
- `mcp:list-capabilities`
- `mcp:list-credentials`
- `mcp:list-installed`
- `mcp:put-credential`
- `mcp:read-resource`
- `mcp:refresh-manifest`
- `mcp:set-enabled`
- `mcp:set-tool-visibility`
- `mcp:start-oauth`
- `mcp:test-connection`
- `mcp:uninstall`
- `mcp:upsert-server`
- `pending-task:clear`
- `pending-task:consume`
- `pending-task:peek`
- `pending-task:write`
- `permission:approve`
- `permission:deny`
- `projects:list`
- `prompt-context-epochs:chain`
- `prompt-context-epochs:events`
- `prompt-context-epochs:list`
- `prompt-snapshots:get`
- `prompt-snapshots:list`
- `quick-chat-popover:hide`
- `quick-chat-popover:select`
- `quick-chat-popover:show`
- `quick-chat:hide`
- `quick-chat:set-content-height`
- `quick-chat:set-task-card-visible`
- `quick-chat:submit`
- `runtime-projection:get`
- `session:get`
- `settings:export`
- `settings:get`
- `settings:get-sync`
- `settings:import`
- `settings:update`
- `shell:open-path`
- `shell:permissions:add`
- `shell:permissions:list`
- `shell:tasks:list`
- `shell:tasks:stop`
- `shell:tasks:stop-active`
- `shortcuts:reset`
- `shortcuts:status`
- `shortcuts:update`
- `skills:disable`
- `skills:enable`
- `skills:link`
- `skills:list`
- `skills:list-available`
- `skills:refresh`
- `skills:unlink`
- `skills:upload`
- `updater:check`
- `updater:download`
- `updater:get-status`
- `updater:install`
- `updater:open-installer`
- `updater:open-release-page`
- `updater:set-channel`
- `usage:stats`
- `workspace:add`
- `workspace:ensure-default`
- `workspace:info`
- `workspace:list`
- `workspace:remove`
- `workspace:set-active`


---

## 覆盖率与静态分析限制

1. **行数**：物理行计数（含空行与注释），不是“有效业务语句”严格度量；与 `cloc` 的 code/comment 拆分可能不同。
2. **符号提取**：基于正则启发式，非完整 TS/JS AST；多行签名、对象字面量方法、动态 `ipcMain.handle(variable)` 可能漏计；`method` 可能有假阳性。
3. **职责标注**：由命名与路径启发式推断，**不是**作者文档；阅读时以源码为准。
4. **排除**：`.goal-worktree-*` 工作树副本已显式排除（否则会严重污染统计）。
5. **TUI / scripts / docs / crates**：本报告聚焦桌面前端与客户端。
6. **生成文件**：`dist/`、打包产物不计入。
7. **分析未改仓**：报告写入知识库工作区 `peer-knowledge`，不对 `peer_agent` 做实现性修改。

### 覆盖率核对

| 检查项 | 结果 |
|--------|------|
| Renderer 代码文件 | 259 |
| Main 代码文件 | 233 |
| Preload 代码文件 | 1 |
| packages 代码文件 | 83 |
| 焦点逐文件 LOC 表行数 | 579 |
| 生产符号表文件数 | 356 |
| IPC 通道 | 146 |

### 分析元数据

```json
{
  "baseline_head": "35580b0fd58661e3a2bbd7c396827e23f6293bfd",
  "focus_code_files": 579,
  "focus_code_loc": 129071,
  "focus_prod_loc": 96979,
  "focus_test_loc": 32092,
  "prod_symbols": 2875,
  "ipc_channels": 146,
  "report_path": "/Users/liangyin/Documents/MiaoYan/peer-knowledge/knowledge/architecture/peer-agent-frontend-client-code-map.md",
  "excluded": [
    "dist-electron",
    ".peer-agent",
    ".vite",
    ".git",
    "dist",
    "out",
    ".next",
    "coverage",
    "build",
    "node_modules",
    ".turbo",
    "__pycache__",
    "target",
    ".goal-worktree",
    ".tmp",
    ".qoder",
    ".worktree",
    "yarn.lock",
    "package-lock.json",
    "pnpm-lock.yaml",
    "Cargo.lock"
  ]
}
```

---

*本文件为知识库沉淀报告，供架构阅读、onboarding 与复核使用。*
