# 78. Intake 期武装 UI 交付视觉验证门

创建时间：2026-09-23

状态：Accepted

级别：B 级（不动协议与完成门语义，新增 intake 期分类 seam 并接线既有 ui-delivery-authority / 完成门 / 视觉修复链路）

关联：

- `knowledge/decisions/15-plugin-skill-mcp-system.md`（能力治理链）
- `knowledge/decisions/16-skill-call-lifecycle.md`（调用生命周期）
- peer_agent `apps/desktop/electron/main/runtime-gateway/ui-delivery-authority.mjs`（requirePreview / read / 完成门数据源）
- peer_agent `packages/runtime-node/src/goal-plan-store.mjs`（契约建立/修订 seam）
- peer_agent `packages/runtime-node/src/goal-intake-ui-delivery.mjs`（新分类纯函数）
- peer_agent `packages/runtime-node/src/goal-runner.mjs`（evaluateVerificationGate，fail-closed 语义）
- peer_agent `packages/system-context/src/sources/goal-runner-source.mjs`（武装事实进上下文）

## 背景

视觉验收链路（desktop_preview → ui-delivery-authority.requirePreview → 完成门 `ui_delivery` unmet → 预览 close 阻塞 → 视觉修复循环）在会话 95d2e647 的事故中全程未启动：模型把「隐藏空态下的栏」当纯代码改动交付，只跑了单测就收尾；`requirePreview` 的仅有的两个调用点都在「模型已主动使用预览能力之后」，属于被动武装。唯一的事前约束是 system prompt 里的一句软提示，违反「不把 prompt 指令当唯一执行手段」的治理基线。结果是每次 UI 目标都要用户手动要求截图验证。

## 决策

在 goal 契约生命周期上新增一个**intake 期分类 seam**，把「这事的交付物是 UI 像素」判定前置：

1. **分类是纯函数**（`goal-intake-ui-delivery.mjs`）：输入契约文本（title/goal/tasks/successCriteria），按 UI 表层词汇（权重 2）、渲染层/文件线索与预览线索（权重 1）、独立强视觉信号（权重 3）、负向词（权重 -1）打分；「截图/视觉验证」类元词汇只有与 UI 词汇共现才计分，防「给截图验证加单测」这类元目标误武装。阈值 `score ≥ 2` 且非 meta-only 才 `required`。
2. **判定在 store，武装在宿主**：`goal-plan-store` 在 `createGoalContract` / `promoteIntakeToGoal` / `upsertGoalContract`（intake 原地升级与修订）三个契约写入点调用分类，命中则通过新宿主回调 `onUiDeliveryRequired(plan, verdict, meta)` 通知宿主；intake 未确认态不武装；分类异常绝不阻塞契约写入；无回调宿主（TUI/无预览）为 no-op。
3. **武装复用既有治理链**：desktop 侧回调调用 `ui-delivery-authority.requirePreview(plan, intake 占位指纹, 'desktop')` 落持久化 required 标记；真实预览打开时指纹变化按既有 `identityChanged` 语义重拍。截图执行仍走 `desktop_preview` 工具与授权链——intake 期只立「需要视觉验收」的事实，不绕过 Runtime Projection、不新增能力分支、不改工具投影。
4. **完成门语义不变**：`evaluateVerificationGate` 继续信任 authority 的 host-resolved 状态；authority 缺失或判定元数据残缺时 fail-closed（`ui_delivery_authority_missing`）。机械缺口（任务证据/验收命令）优先浮现，不被视觉门掩盖。
5. **武装状态是事实，进 System Context**：store 暴露只读 `isUiDeliveryRequired(plan)`；goal-runner-source 在 facts 渲染 `visual verification gate: ARMED` 行，模型建计划时即知道要安排截图 + 独立判定，而不是等完成门阻塞或用户催促。旧宿主/读取异常一律降级为未武装，渲染零变化。

## 后果

- UI 类 goal 从「用户手动要求截图」变为「intake 自动武装 + 完成门强制」，用户不再需要重复说「你自己跑一下验证」。
- 分类器是启发式（中英文关键词 + 权重），存在漏判/误判面：漏判由「模型主动开预览 → 既有被动武装」兜底（原链路保留）；误判的代价是多一次视觉验收要求，不会阻塞非 UI goal 的机械完成路径。
- meta-only 护栏防止「造验证机制本身」的 goal 被自我武装，这是本 seam 区别于朴素关键词匹配的关键规则。
- 后续若引入模型参与的意图分类，替换点就是这个纯函数（seam 不变）。
