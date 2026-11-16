# 03 命名读模型与索引算法

创建时间：2026-11-11
最后更新：2026-11-11
状态：详细设计候选。Query拥有派生数据，不能给命令/工具授权。

## 1. 固定结果与来源

所有View共用01的ViewPage，增加 `freshness:'current'|'observed'|'catching_up'`。ready只表示本结果完整符合其source，不承诺未治理的外部修改已被即时发现；`current`还要求原变更journal/index追赶完毕、所选实体强版本匹配。`observed`必须附asOf，不能把旧值伪装为最新、失败变空成功。查询结果永不作为最终授权。

SourceVector的kind固定为 `conversation/plan/coordination/approval/policy/resource/registry/profile/memory/objective/config/evidence/usage/automation/readCursor/executionResource/lease/pendingInput/clientState/shellTask/context`；Control/dispatch属于coordination，Provider目录属于config，context对应原prompt epoch/snapshot版本，表达窗口事件另用01的presentation source。每项是该owner的真实版本，不拿plan版本代替独立Evidence/usage/claim变化。跨32项用 `SnapshotRef{rootId,projectionGeneration,snapshotId,digest}`，snapshot表保存完整有序vector及相关canonical index/journal checkpoint。该ref只用于视图一致性/重新取得源，不用于执行许可。

派生根固定为 `cache/read-models/runtime-v1/<rootId>/`；`catalog.sqlite`放实体头/事件checkpoint，`evidence.sqlite`放按键证据索引，`search.sqlite`放公开搜索；现有interaction索引继续复用其Store内命名空间，不另造正文真源。每个DB在worker更新，查询只打开已发布generation的只读连接。新generation完整提交与source版本检查后才原子切换manifest。

## 2. View目录与字段/上限

字段是闭集；复用既有Protocol行的表达字段，不包含内部rounds、秘密、原生checkpoint或可执行对象。bodyRefs可以继续读取原文，超过预算不静默删除内容。

| View / filter | 行字段、排序/游标 | 默认/最大 / 字节预算 |
|---|---|---|
| `bot.list`：原status/query/pinned | workspaceId、原BotProfile公开字段、avatarRef、preview、status/actionRight、unread、needsYou、attentionExpiresAt、source；原Bot排序 + workspaceId稳定tie-break | 30/100；64KiB |
| `bot.badge`：scope | totalNeedsYou、byWorkspace计数（可选分页）、source、asOf；不返回session/report | 1总计或100项目；16KiB |
| `grants.pending`：workspace/parent/recordKind=obligation或approval | obligation沿原PendingGrant字段、items的sessionId/title/shortId/actions/gaps；approval沿原PendingApproval的call/scope/reason/decision状态字段；均含identity/revision/writer可用性/unknown advisory refs；按createdSeq,kind,id | 20/50；64KiB；单grant items分页 |
| `tasks.list`：workspace/work/anchor/status/includeTerminal/taskKind | 原WorkSessionSummary或TaskOverviewItem的闭集投影，taskKind=session/goal/automationRun/backgroundShell/conversation；原统一生命周期元组、refs与source；updatedAt,kind,id | 30/100；128KiB |
| `session.report`：target={kind:session/plan,id}/sourceRevision | 原报告summary/keyFindings/changedFiles/evidenceRefs/criteria/verdict/acceptance公开字段；大正文为bodyRef；非委派Plan不伪造sessionId | 1；256KiB；每子列表50项 |
| `interaction.window`：conversation/before/anchor | 原公开消息窗口、meta/preview、稳定message/turn IDs、source、hasMore；canonical seq/id | 50/100；256KiB |
| `conversation.list`：原workspace/role/status/parent/query | 原SessionMeta/preview/count字段和source；updatedAt,id或原pinned顺序；不读取正文 | 50/100；64KiB |
| `trace.page`：session/attempt/turn/cursor | 过程seq、event kind、toolCall/name/status、安全preview与原result/evidence/artifact refs；seq,id | 50/100；128KiB |
| `evidence.refs`：planId/conversationId/refs | evidenceRef、canonical record identity、tool/capability、时间、artifact refs与有界元数据；绝不返回原正文 | 50/100；64KiB；refs入参最多100 |
| `search.page`：原scope/public query | bot/message/task/memory身份、公开excerpt、sourceRef、原搜索rank/tie-break；不含private rounds | 20/50；64KiB |
| `resource.window`：既有resourceRef/revision | 原ResourceWindow/ResourceEdit可见切片、版本、只读/可编辑事实与引用；资源service已取得的snapshot | 1；256KiB；缺snapshot明确unavailable |
| `memory.page`：原workspace/status/kind | 原MemoryItem公开字段、来源/冲突/有效性、text或bodyRef、revision；原排序+id | 30/100；128KiB |
| `objectives.page`：workspace/status | 原ProjectObjective、里程碑/观察引用、有界watch状态；原排序+id | 30/100；128KiB |
| `settings.snapshot`：固定section/cursor | 原公开配置、Provider/model capability/eligibility与reasoning字段、已保存revision；凭据仅configured布尔值 | 1 section；256KiB；catalog 50/100 |
| `diagnostics.snapshot`：原workspace/action=read | 原ProjectDiagnostics允许字段、计数/安全error refs、预算/queue指标；原200/20等上限继续取更小值 | 1；128KiB |
| `clientState.get`：kind/key | 原draft/readingAnchor/layout及保存revision；仅本连接受准入的表达scope | 1；64KiB，正文过大用原draft blob ref |
| `usage.page`：原period/provider/model/role | 原聚合计数/费用/缓存命中字段及usage refs，未知计量保持unknown；day/provider/model/role稳定键 | 30/100；128KiB |
| `attention.page`：workspace/原unread与kind | 原AttentionItem公开字段、message/session/work refs、expiresAt/readCursor/source；原attention顺序+id；失效只影响展示，不写已读/签收 | 30/100；64KiB |
| `automation.page`：recordKind=definition或run，原automationId/status | definition沿原AutomationDefinition公开配置/启停/overlap/missed状态；run沿原AutomationRun的状态/dispatch/结果refs，正文bodyRef；updatedAt,kind,id | 30/100；128KiB |
| `tasks.counts`：workspace/conversation/taskKind/status | 原awaiting审批计数及统一任务计数，按conversationId/taskKind/status分桶；不返回报告/正文 | 50/100桶；32KiB；总计独立字段 |
| `pendingInput.peek`：原device/currentWorkspace | 原PendingTask的目标/输入ref、handoff revision、claim/receipt refs；不是用户draft或已发送事实 | 1；64KiB，大正文用原受保护ref |

服务端对limit取min(request,viewMax)，byteBudget同样取更小值；filter schema不接受原生SQL、任意path或新scope。完整内容不能放进单页时只返回显式分片及hasMore，不能声称已返回完整报告/全部grant。

## 3. 索引键与增量投影

| 索引 | 主键/辅助索引 | 增量来源与冷重建 |
|---|---|---|
| bot_heads / attention / attention_counts | workspaceId；status,pinned,sortKey,id；attention(workspaceId,kind,id,expiresAt)；counts(workspaceId,kind) | registry/profile、原preview、Approval/Control/问答/任务head与readCursor；同一投影事务更新受影响Bot和计数；冷worker按source构建 |
| task_heads / task_counts | (taskKind,taskId)；workspace/work/anchor/status/updatedAt/kind/id；适用时sessionId/planId关联；counts(scope,conversation,kind,status) | GoalPlan/conversation/automation/shell原index/change journal + 原control/acceptance/resource事实；先选候选，再构建需要的head，不给非session任务伪造sessionId |
| grant_heads / grant_items | grantId；workspace,parent,status,seq；(grantId,itemSeq) | 原义务/Approval库的已提交版本；只有当前pending项才按sessionId读title，空grant零session hydrate |
| evidence_records | evidenceRef/recordIdentity；planId,seq/ref；conversationId,seq/ref | 原evidence-index.jsonl按完整行offset增量，验证身份/已读边界；每行只归一化一次，投影记录offset/digest/有界metadata |
| reports | (targetKind,targetId,sourceRevision)，targetKind=session或plan；适用时planId关联 | 仅被请求target的canonical报告/结果与证据键；不调用acceptance接口形成读递归；策略/验收字段来自原独立回执 |
| interactions / trace | 原interaction identities/records/messages/links；attempt/turn/seq | 原Conversation版本/sidecar/terminal提交；原公开/内部边界保留，大行用流式选择性解析，不物化rounds |
| conversation_meta | conversationId；workspace/role/status/parent/updatedAt/id及原pinned键 | 原conversation index与物化preview；缺preview标rebuilding，不扫描正文补count |
| search_public | (scope,entityId,sourceVersion)；原公开全文FTS/排序键 | 公开message/task/memory已提交更新；删除同键，重建与增量结果一致，不以UI摘要代替可检索全文 |
| feature_heads | (featureKind,workspaceId,entityId)；status,sortKey,id | memory/objective/config/resource原owner的committed revision；只索引原可公开字段 |
| usage_rollup | (day,provider,model,role,usageId)去重；day/provider/model/role聚合键 | 原usage request日志完整行增量；更正/删除使相关bucket重算，worker重建不改变计费权威 |
| automation_heads / pending_input | (recordKind,id)及automationId/status/updatedAt；pending_input(device,revision) | 原Automation定义/run日志、原pendingTask版本/消费回执；只投影，不触发定时执行/消费/清除 |

生命周期head由现有纯Protocol projector消费一组版本化事实计算；不在Query再写一个状态机。完整验收/criteria计算由M11提交，Query取其回执及必要原始事实；旧记录没有回执时worker可做纯投影，但不能补写passed/accepted。

Evidence查找按plan/conversation/ref索引，热查询不再调用listEvidenceIndex全表。外部追加仅读取新增完整行；半行暂不发布。截断/替换/内部损坏、index与journal矛盾触发该source重建/明确damaged，不能沿用旧ready。盲信snapshot或只用TTL命中不允许。

## 4. 当前事实与外部写入

正常Store提交发布revision hint；Query以原journal/index检查实际commit，不把hint当真相。每数据源只有一个catchUp job，128个dirty refs上限；超限标记source namespace dirty并从canonical cursor补读。fswatch通知与已有250ms有界尾部drain共用一个source observer，不给每视图一个轮询器。30秒外部发现审计在worker分页64个源，连续进行到该namespace检查完；不能把一次30秒timer变成全库同步扫描。

每次读取验证catalog/index强版本和所选实体的 `(dev,ino,size,mtimeNs,ctimeNs)`，多源读取结束再次核对，最多2次重试。读取中变化返回version_changed。未治理的直接改文件可能缺索引提示：相关已选实体立即识别，未选实体由fswatch/有界审计发现，期间global排序/计数只能标observed；不能承诺raw write即时全局排序。实际执行永远重新查当前canonical，发现坏/竞争不使用旧View兜底授权。

跨Store不存在全局事务，Query保存完整SourceVector/快照ref；同一行的status/actionRight/control/acceptance使用同一组事实版本。若不能闭合这组版本则rebuilding/version_changed，而不是混拼一行。

live/ended/unknown沿原RuntimeSessionFacts。Query通过受管owner只读live snapshot获取 `{hostGeneration,executionEpoch,observationSeq,observedAt,ownership}`；该端口只读现有live token/handle map，不扫描Store。断线、新代次或超过6秒未能更新观察时转为 `liveObservation unavailable/unknown`，绝不按时间变ended。canonical终态/stopReceipt仍独立存在。

## 5. 分页、索引发布与损坏

每页在只读SQLite snapshot中完成；cursor绑定filter/scope/source generation及最后排序键。除当前generation外最多保留2个旧generation、最长5秒；在途读取数量仍受QQ限制，更老cursor返回CURSOR_EXPIRED并提供原anchorRef。没有纯时间cursor。UI恢复锚点，不擅自回到最新。

重建写唯一temporary generation；逐批commit派生数据，只有schema/完整性/末尾source token再次匹配才发布manifest。SQLITE_BUSY在worker按5/10/20/40/80ms退避，仍忙则返回rebuilding，不阻塞主线程3秒。损坏DB移动到同派生目录的quarantine（最多保留2个generation），保留canonical，重新重建；该操作不触碰策略/资源/command journal权威库。

无法解析的canonical返回damaged和本地detailsRef；不能丢坏行后当完整ready。超大单JSON记录由05的stream tokenizer选取需要字段；Provider/Context真的要求完整且不能准入时明确阻塞。用户仍可读其他公开页/查看诊断，不为索引失败隐藏全部Bot。

## 6. 安全与成本断言

Bot badge只做SUM(attention_counts)与版本检查；空pending grant零task/report/evidence hydrate；tasks页只hydrate所选IDs；report单session；trace/evidence只读明确scope。Query cache键含scope/filter/source/schema/host generation，caller不能以另一个scope复用cache。不存在`includeAll/full:true`产品回退。

Resource缺snapshot需要原受限 `resource.inspect` 用户操作经统一能力链物化，Query本身不执行文件/浏览器能力。Evidence正文给模型仍须原Provider/Projection/Grant路径，Query只给refs/安全元数据；UI对指定Evidence的原受限读取亦不扩大scope。

resource.window的recordKind闭集为原resource/edit/interactiveResult/version/submission/operation/windowHistory/botAvatar；每种沿原公开typed行并带原identity/revision，不把列表冒充单个正文。botAvatar先返回已验证mime/总bytes与scope/source绑定的短期assetRef；同View的chunk请求只接受该ref和offset，每次最多180KiB原字节，以base64连同offset/nextOffset/source返回且总帧≤256KiB。客户端完整收齐≤1MiB图片后构成原data URL，source改变即放弃旧片；不能传路径或在bot.list内塞base64。这拟替代ADR85决策12的单帧返回，图片种类/大小/权限保持。settings.snapshot的section闭集为原settings/developer/providerCatalog/modelRouting/registry/workspace/policy/unknownOutcomePolicy/capabilities/runtimeProjection/integration/inputPrediction/shellPermission/editor/clientSession；所有大catalog分页，秘密只有configured。registry/workspace/权限读取不是任务列表。diagnostics的PromptSnapshot/epoch诊断保留原local角色与内部可见性，只给受限片段/refs，不进入公开搜索/普通会话窗口。

验证计数须包括fs读取字节、JSON归一化/clone次数、SQL扫描行、hydrate数量、队列等待和结果字节。加十倍无关历史后，热页不得增长为全表CPU/读取。首次重建总成本独立记录，不能用热缓存平均值掩盖它。
