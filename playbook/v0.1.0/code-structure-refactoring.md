# 代码结构与监督闭环实施记录

创建时间：2026-10-28
最后更新：2026-10-29

状态：R1–R5 实现和本批自测完成；本地功能、性能及产品核验通过，未发布、未安装到用户运行实例。

用户先授权按[结构审查](../../knowledge/experience/peer-code-structure-and-loading-audit.md)建议顺序完成，随后明确要求“全部完成再自测没问题后提 PR”。因此本任务获准提前运行构建、测试、类型、架构、IPC、隔离产品及性能验证。契约为 [ADR 112](../../knowledge/decisions/112-runtime-module-and-loading-boundaries.md)、[ADR 111](../../knowledge/decisions/111-project-agent-duplex-supervision-and-continuity.md)，前置责任投影沿 [ADR 110](../../knowledge/decisions/110-follow-up-responsibility-and-current-list.md)。

## 候选与隔离

原审查基线为 `b6e8fe88c90fc56677a404c641c0978da6a64f92`；原工作区包含其他在途改动，已保存 2,885 个相关文本文件起点与本批增量。交付迁移到当前 `origin/PeerAgent/dev/0.1.0` 的独立 checkout，基线 `e0c87d2db739b168956eb1715047d149642b1f1e`，分支 `codex/runtime-loading-supervision`。18 处合并冲突逐项保留开发线的新资源面板、稳定回调、草稿保存、物理 writer fence 和恢复治理；6 个快照中缺失但实际未变的 CJS 文件不计入改动。

原 dirty checkout、其他任务的代码及知识修改保持原样。本批只纳入 ADR 110 中监督所需的共享投影和消费者；未夹带其他布局/文案任务。知识独立提交，架构文档不回流代码仓。没有发版、合并其他 PR、安装、重启用户当前应用或迁移用户日常数据。

## 工作包

| 工作包 | 实现与边界 |
| --- | --- |
| R1 可见性与读取 | `conversationRefresh`、`useBotList`、`useBotWorkSessions` 合并事件，隐藏时保留 pending、恢复可见补读；`reconcileFacts` 以稳定行身份结构共享，删除完整快照 JSON 比较。后台任务和治理继续运行。 |
| R2 功能加载 | Desktop 页面、设置分区、Classic Chat、Workbench 和低频高亮语言动态导入，局部 loading/error/retry；清除任务详情及资源工作区的静态导入旁路。设置、模型设置、能力、自动化、GoalPanel CSS 随功能入口加载，共享 Frost/工作台层叠入口保留。TUI help/version/exec/ACP 在交互入口前分流，JSX 延迟进入 `interactive-entry`。 |
| R3 深 Module | GoalPlan 拆出领域、文件、事件订阅、Evidence、checkpoint CAS；GoalRunner 拆出规划与核验策略。ChatSurface 拆出会话水合、恢复文案、阅读锚点、附件输入和 Git 环境/弹窗。聊天服务拆出回合上下文与流事件投影，保持原执行顺序和兼容入口。 |
| R4 出口与资源所有权 | runtime-node 增补 storage/models/providers/project-agent 四个构建后子路径，根出口兼容；实际消费者迁移。Qoder SDK 在实际会话内加载；OAuth callback 独立拥有 server/timer/waiter、关闭与迟到回调；价格纯计算切断 log/stats 环；用量日志有界尾读；纯查询不再重写效果幂等账本。索引重建由进程内共享 FIFO 最多并发 4 个 Worker，排队后重查 lease，结束后释放配额。 |
| R5 监督与连续性 | 唯一 followUp、canonical 信箱、父子结构化问题、真实用户问题关联、受控 resume 与执行效果回执、工作笔记/历史/交接准备接入原协议、能力链、Context Source 与协调调度。Desktop/TUI 共用实现。 |

GoalPlanStore 与 ChatSurface 继续承担既有装配，并未因“超过某行数”机械拆空。新增 Module 集中完整职责，不新增第二套执行器或任务引擎。

## 监督事实与恢复

- 消息、问题/答案与恢复义务原子提交到既有 journal/blob。recipient/session/work 索引查询不水合全信箱。Conversation 镜像仅为兼容展示。
- mailbox_only 只入箱；ensure_turn 请求原调度续接。投递、准入、实际效果分开。只有实际 L7 Source 纳入的 ID 可写 observed；未观察事件保持未处理并沿原 checkpoint 推进，不能整批误确认。
- 问题保留 option ID、目标 revision 和一次解决条件；同一子会话仅能有一个开放请求。原生 `post_reply.question` 的关联和请求升级同一事务提交；只有当前真实用户对对应卡片的回答可转交。原生旧卡关闭后，宿主可验证事实并重新关联，不能借此代答或产生权限/验收。
- resume 使用既有 TaskTransition/SessionTakeover/GoalRunner，保留任务、材料、预算和核验义务，更新 epoch。已发出而效果不明保留 unknown，不盲目重放。实际绑定回合才证明执行开始；用户停止、原生人工门、未知工具结果继续阻挡自动恢复。
- 笔记在本工作 runtime 对象内 CAS 写入，完整版本先落不可变内容寻址 blob。历史按父子边界与 native page 有界读取，敏感正文不进入搜索片段，缺源明确失败。交接 `state=prepared/providerWindowChanged=false`；原生压缩/换窗仍归既有 Provider encoder/checkpoint，准备记录不等于已经完成换窗。
- 沿用 schema/storageVersion 2 与物理旧 writer fence；新监督记录要求最小 reader/writer 5。head、丢 manifest/索引重建及维护恢复不得降级。跨设备复制监督状态不属于本批。

## 自测修复

第一轮发现并修复：懒加载类型推断、提取后遗漏的 Git 读模型/声明顺序、TUI supplemental context 字段、真实回合归一化丢失 coordinationBinding、未决问题唯一索引被替换、超过 50 条最近历史时早期消息饥饿、部分事件排序断言、旧夹具未建立 writer fence、已签收报告夹具仍使用新语义下待 Bot 收口的 result_ready。源码位置断言跟随职责迁移，实际能力白名单断言明确包含四项 continuity 能力，并继续禁止文件写入/Shell。

窗口用例等待懒加载控件真实可见后操作，抽屉关闭后等待真实有限动效和布局稳定再测阅读位置，不用固定延迟冒充可用。真实详情组件测试保护不同表达职责：标题按 native 状态本地化并保留接手提示，进展保持具体宿主预算/问题说明；普通子任务 waiting_user 继续使用中性的等待跟进，不覆盖明确人工门。避免用一个泛化格式器同时改写标题、进展与行动权。120 条消息回归逐批观察旧消息，派生索引重建后保持已观察事实。性能夹具显式提供隔离 lease epoch；首次存储准备与五个已迁移数据的冷进程样本分列，保持原性能门槛，不扩大预算。

懒加载首用回归另发现共享样式所有权错误：History 下拉菜单样式原藏在模型设置 CSS，未访问设置时菜单被遮罩挡住。Dropdown、OverflowMenu、共享设置标题现在由各组件导入样式；MCP 面板也直接拥有其专属与共享控件样式。PostCSS 按选择器、祖先规则和声明逐项对照，迁移前后 940 项完全一致。新增样式所有权测试通过，真实 History 首用点击与转移续接通过；未靠预先打开设置掩盖问题。

另一轮完整 Capture 在拒绝图片后的回执重挂载处，单次一秒滚动稳定等待超时。修正测试辅助器在原五秒总期限内重取相同卡片，保留全部授权、状态和 Evidence 断言；六条真实 IPC 路径（单次允许、本轮允许、拒绝、取消、停止、超时）已单独通过。该失败轮截图不作为最终验收。

完整回归横跨本地午夜时还暴露历史夹具日期老化：23:59 写入的“今天”在 00:12 实际界面中正确成为“昨天”，四组断言因此失败。历史场景现在进入时重新标定隔离夹具的日期，保留真实分组和四组断言。新增跨年午夜测试验证刷新后 today/yesterday/week/earlier 齐全、ID/消息与无关索引记录不变，非夹具 home 拒绝写入；夹具测试 7 项通过。未改生产日期分组规则或放宽断言。

最后的共享 UI 补充场景暴露相同的懒加载等待前提：点击外观页后立即统计预览，读到加载中的 0 个控件。脚本改为先等首个预览真实可见，再执行原有 3 个控件、圆角 token 和矩形比例断言；生产代码和断言门槛未变。失败 Capture 保留，最终验收使用修复后的新源码重新生成。

逐图审查随后发现原机器断言遗漏的实际裁切：资源主栏是 `overflow:hidden`，原生焦点滚动使其 scrollTop 约 749.5，Bot 壳 top 为负，自动化标题移出视口；document/root/app-shell 的旧检查仍全为 0。先增强真实窗口断言复现失败，再将不拥有阅读滚动的主栏改为 `overflow:clip`。列表、页面、会话及预览继续拥有各自滚动；不添加强制 scrollTo、焦点抢占或动画常数。用户目标是从设置切到功能页时仍看见页面标题和返回入口，既有草稿、内部阅读位置及业务事实源不变。该轮仅机器通过的截图包不予验收。

同一审查又发现窄窗口下 body 的 1024px 最小宽度仍裁切经典聊天输入区；只针对资源栏放开最小宽度不足以解决根因。真实窗口增加 body 几何断言复现后，文档统一适配实际视口，移除资源页特例。原生主窗口的 1040×720 最小尺寸继续由 host 管理，不用 CSS 把文档撑出窗口；组件、滚动容器、草稿和原业务动作保持。

冷恢复 profile 定位到空 work 账本的重复修复扫描与重复元数据读取。协调选择在当前权威快照确认为空时免除只处理既有 work 的扫描；一次 continuation 决策共同检查 work 与 prepared delivery，空闲分支不重复决策，真实回合跨 await 后仍重新检查。新用例验证新任务/投递在下一调用可见，隔离投递继续受阻，pending event 不丢失。存储元数据缓存有界且每次核对文件版本；同尺寸改写并还原 mtime、替换 pointer、未完成 fence 均必须立即阻断。无许可缓存、存储格式修改或跳过日志完整性校验。

## 静态对照与性能

按当前 dev 基线比较源码装配行数（不是运行耗时）：

| 装配模块 | dev 基线 | 本批 |
| --- | ---: | ---: |
| GoalPlanStore | 4,924 | 2,524 |
| GoalRunner | 2,721 | 2,302 |
| llm-chat-service | 2,488 | 1,729 |
| ChatSurface | 3,282 | 2,770 |

原审查的 496→423 模块及 87,892→70,670 行统计来自旧工作区，不能作为当前 dev 的性能对照，也不换算成点击提速百分比。当前产物入口 JS 约 1,358.62 kB（gzip 415.92 kB），Classic Chat 单独为 250.89 kB（gzip 80.59 kB），Workbench 为 129.24 kB；共享入口 CSS 约 683.05 kB。设置、能力、自动化和 Chat CSS 已独立分块。入口仍有大 chunk，后续具体场景分析应依实际 trace，而不是继续按文件大小拆分。

隔离本地性能场景为 200 Bot、10,000 消息、100,000 Inbox 事件、10,000 记忆。最终冻结源码的五个真实样本中位数如下；所有原门槛保持不变，等于门槛仍判失败。

| 路径 | 中位数 | 原门槛 |
| --- | ---: | ---: |
| 冷读列表 | 84.12 ms | 100 ms |
| 搜索 | 134.89 ms | 150 ms |
| durable received | 51.38 ms | 300 ms |
| consume | 72.67 ms | 200 ms |
| memory capability | 22.32 ms | 50 ms |
| 已迁移数据的冷进程恢复 | 819.95 ms | 1,000 ms |
| 每 Bot 增量 RSS | 0.97 MiB | 2 MiB |

首次存储准备单列约 25.69 秒；冷恢复样本仍是 5 个独立进程，包含原有恢复后 GC/内存采样，全部空闲 Bot 模型调用为 0。没有真实模型延迟样本，`localPass=true`、`ready=false`；不能宣称用户安装实例已修复或整体 Ready。

测量过程保留原失败与接线变化。最初旧工作区的 14.74 / 89.41 / 741.41 ms 不能作为当前 dev 或当前 adapter 的最终值。收尾曾测得搜索／冷恢复 247.57 / 1,950.47 ms，另一轮为 250.50 / 2,123.75 ms；CPU profile 定位到严格逐会话读取、恢复重复扫描和存储准备。首次 adapter 校正漏了实际 Desktop 的摘要读取，补齐后冷列表仍超过 100 ms。随后完成只读摘要、公共搜索投影及空闲恢复优化，不把 adapter 校正本身宣传为产品提速。

修复窗口裁切后的混合轮仍有一次搜索 152.44 ms 超标，五次为 65.84 / 135.27 / 152.44 / 194.01 / 202.91 ms，同时冷恢复为 800.25 ms。该报告独立保留。补充 profile 没有证明记忆写入是唯一原因；还发现通用 `await fn()` 计时器把同步 API 返回后的排队微任务算进耗时。先用可控时钟复现同步操作 5 ms 被记成 100 ms，再修正为同步在返回结束、异步在实际 settlement 结束；四项计时器与门槛测试通过。原冷读列表／搜索／输入／记忆交替负载继续保留，不插入强制 GC、不删除样本、不减少数据量，也不排除操作内部的 GC 成本。该修改校正测量口径，不计作产品提速；最终表使用修复后的同一混合场景，原报告和 profile 分列保留。

公共搜索保留完整公开正文，排除私有过程、工具参数与越界会话；版本变化／删除仍重新投影。新用例核对完整搜索文档等价、200 会话温读、旧 type/messageKind、冻结只读值及 Unicode 边界。实际宿主集成进一步验证新消息更新可搜索、私有过程不进入结果，查询不再走严格历史批量入口。

完整测试范围采用分段回执，不能写成一条从头到尾全绿的命令。较早 root 范围完成各 workspace 及 marketplace/changelog/upgrade；TUI 817 项／93 文件通过。最后完整构建和 ConversationStore 111 项通过；runtime 1,575 项中两条旧空账本次数断言按 4→1 收紧，相关 28 项通过，150 ms 调度用例整文件隔离重跑 9/9 通过（4.06 秒）。Desktop 6,101 项范围有 5 项既有跳过；旧 corpus 批量读次数按 1→0 收紧并补公共正文新鲜度／私有过程断言，真实集成整文件 36 项通过；并行搜索原 40 秒超时后整文件隔离 10/10 通过（1.09 秒）；尾部 3 项通过。较早 TUI 并行 5 秒超时的整文件隔离为 15/15、3.27 秒。最后类型、架构/IPC、UI 规则 8 项通过；计时辅助器最后单独 4 项通过。所有原时限与原失败日志保留，未把未运行或跳过的检查写成通过。

## 最终验证回执

最终产品包 runId 为 `ec311a87-4a14-41e0-9d51-7f285837fb5d`，源码内容指纹为 `873f4fd57b7c850d83a07ac91079606a84ce8f796a75306b8103d6c720f4b2fd`。全部 252 张必需截图逐张审阅并绑定原图 SHA-256；2026-10-29 标准 Verify 返回 `passed`。审阅由实现者 Codex 执行，`independent=false`。机器交互与最终图片共同核对了恢复、问答、权限、任务状态、懒加载、窗口布局和阅读连续性；未把旧源码截图包沿用到当前候选。

本批构建、类型、架构/IPC、分段完整测试范围及最终局部检查的实际记录见上节。[交付回执](../../knowledge/experience/evidence/2026-10-29-runtime-supervision/receipt.json)绑定最终代码提交、产品结果、性能原始样本与日志哈希；[逐图审阅](../../knowledge/experience/evidence/2026-10-29-runtime-supervision/product-review.json)、[产品核验](../../knowledge/experience/evidence/2026-10-29-runtime-supervision/product-result.json)和[性能报告](../../knowledge/experience/evidence/2026-10-29-runtime-supervision/local-performance.json)可直接复核。受控模型、源码 Electron 和隔离数据不能替代真实 Provider、安装包、升级迁移、跨平台及完整读屏验收；`localPass=true` 不变更 `ready=false`。

采用已安装的 ub-mode 原则完成职责提取、边界收束和有意义的失败复现。当前工具集中没有 crapper/dryer/mutator 对应工具，未生成或推测这些工具的评分；已有测试/类型/架构检查与实际产物分别记录，不冒充其结果。

行动顺序为读取 Skill/契约并保存起点 → R1–R5 实现 → 独立 dev 候选迁移 → 自测、定位和修复 → 冻结候选、完整验证 → 提交并推送 → PR。临时日志、增量和测量产物留在仓外；知识文档仅提交本批决策、必要前置责任投影、引用与回执。
