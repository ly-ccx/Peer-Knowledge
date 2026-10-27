# R7：交付关联与历史表达

日期：2026-10-26
状态：核心源码与内容/diff 自审完成，待定向验证；R7 未构建/运行测试/截图。
分级：A/B，先补 ADR 109 §33，再实现同一 Evidence inspection 边界与 DocumentSession 的可选来源引用。

## 用户目标与事实源

用户从任务/回复的真实 Evidence 看见这次交付的文件、代码或图片，并能区分保存的历史预览与现在磁盘上的文件。Provider → Tool Result → EvidenceIndex.userArtifacts 是唯一事实源；Goal/Session 只给归属，renderer 只路由和呈现。没有 UserArtifact 时不创建交付区块，stdout 和 assistant 文本不生成产物。

只读 inspection 的 context 按 Bot/任务失败关闭；原无 context 调用兼容但不返回新增交付投影。每次打开当前文件仍走原 file reader，不扩根、不绕 Runtime 或权限。正文关联标签只存稳定引用对，恢复必核；不是新内容/授权/执行或成果数据库。

## 交互与恢复

- 交付列表默认折叠；保存的代码摘要/图片预览单独标识。没有完整历史正文明确说明，不能拿当前文件替代。
- 显式“打开当前文件”接同一非模态工作区，保留原 Evidence 返回上下文；嵌套链接和 Git 历史不自动继承交付归属。
- 关联丢失、范围拒绝或旧服务不支持时局部提示并可重试，已有文档/草稿/任务保留，不重跑写入或自动替换来源。
- Frost/SVG、共享 MotionDetails 与既有读位/焦点行为；不增加自动滚动、蒙层、对话发送或验收动作。

## 回归设计

| 组 | 宿主/契约 | 前端/跨层 |
| --- | --- | --- |
| D1 真源 | 仅 UserArtifact，拒绝普通 artifactRefs/stdout/文本；有界类型/字段/预览 | 无产物不显示；历史摘要和当前文件分开 |
| D2 归属 | Bot 主会话、合法 Plan/Session；错 Bot/任务/缺 report 拒绝；拒绝前不读正文工件 | 自动携带实际任务引用，不能丢上下文降级 |
| D3 恢复 | 索引删除/读取失败不假造版本 | 普通/不同交付标签独立、非法恢复丢弃、恢复后重核、嵌套不继承 |
| D4 安全与连续性 | 打开仍旧 scoped reader；不加根、不写成果 | 明确当前内容、历史缺失、原 Evidence 回链、局部失败/重试、读位/草稿不丢 |

日常仅编写用例与内容/diff 自审。当前“测试后推进 R7”的测试对象是 R6a；不将其结果登记为 R7 已通过。R7 前后端联调/截图与发布验收待后续明确要求或发布前运行。


## 本轮实现记录

- Protocol：既有 `ProjectAgentEvidenceReadRequest` 增加可选 context；结果增加有界 `EvidenceDelivery` 与明确归属状态。稳定引用对 `EvidenceDeliveryBinding` 只作导航来源，当前文件引用仍是原 `BotDocumentReference`，不扩展文件读取范围。
- 宿主：独立 `evidence-deliveries` Module 从索引投影，先核 Bot 主会话或真实 Plan/Session/report，再允许 Evidence body 读取。仅 8 项合法 UserArtifact；代码摘要最多 41 行/每行 240 字符，安全图片预览有单项与总预算。旧请求保持原摘要行为；无记录和错归属不回退 external/无 context 读取。
- 前端：EvidenceView 在默认折叠的“本次交付”中显示保存预览，明确完整历史正文缺失；当前文件按钮经原工作区/范围校验打开。任务详情保留 sessionId+planId；Bot/reply 按宿主事实派生实际任务归属。
- 文档：来源引用对参与标签去重与恢复，普通文件与不同交付记录独立；恢复重新核对记录/路径/任务，错误只显示关联未确认，当前正文保留。记录内直接展示按需读取的原 Evidence 摘要；原详情仍在同进程通过原返回入口保留，跨启动不伪造旧 Drawer 或复制 Evidence 正文。
- 已编写宿主的纯投影/归属/读前拒绝/旧协议/预览边界用例，前端的引用恢复/标签身份/错路径与任务/旧服务、保存摘要和显式打开及关联失败用例；登记到组合入口，未运行。只作内容/diff 实现者自审。

限制：本包不增加完整文件历史快照存储、内部工件的新读取根、任务完成/验收或交付登记动作。没有历史正文仍缺失；已存缩略图或 Diff 片段不能还原完整原件。当前 R7 尚无构建、类型、模块运行或 Electron 截图结论。348 项与 16 图为本包开始前的 R6a 来源，不覆盖 R7。

兼容审阅发现既有 Objective Watch Evidence 使用自身注册表而非 Goal EvidenceIndex。本包增加只读、同 Bot 核验的专用 Adapter，保留合法旧观察正文；任务 context/错 Bot 拒绝，永不投影 UserArtifact。对应正反用例已补、未运行。
