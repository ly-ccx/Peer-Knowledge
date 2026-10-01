# B4-08 记忆维护实施契约

创建时间：2026-10-01
最后更新：2026-10-01

## 基线、授权与分级
负责人授权自行完成全部 B4、必要接入与合入。A 级，ADR 81 Accepted。代码分支 `PeerAgent/pa/b4-08-memory-maintenance`，独立内核在 B4-07 最终提交 f2a6d321 之上准备；宿主热点待 B4-07 合入再接。知识基线 B4-07 284aaba。没有新增依赖。

## 维护与存储
- MemoryStore 保留现有 expired/conflicted 协议状态；只追加版本，旧 jsonl 不重写。新增可选 expiresAt、topicKey/topicValue、conflictsWith/conflictId、supersededBy、needsReverify 与 fileAnchors（相对路径、内容哈希、观察提交）；规范化、复制与导出必须保留。
- 到期失效；inferred preference 90 天未使用按 lastUsedAt/createdAt 衰减。pinned 与 responsibility 不自动过期。用户撤销和过期/冲突不被检索、快照或简报视为有效事实。
- 日维护沿已有小结时钟、项目租约和恢复屏障运行，不调用模型；device projectRuntime/<id>/memory-maintenance.json 保存当日完成事实。失败可重试，写入幂等；经典界面、已归档、无租约或记忆关闭不维护。
- Verified 条目的文件锚点由宿主读实际工作区文件并计算哈希/HEAD，限定工作区内真实路径，拒绝越界和超限；Curator 可提出路径，不能伪造哈希。相关文件后续内容/提交变化标 needsReverify；简报列入独立“可能已过时”区，退出 clean verified 检索与新任务快照。已冻结快照保留原事实版本。新 verified 候选经原证据准入后可以更新事实；维护不自行声称验证成功。

## 冲突与 ADR 优先级
Curator 输出可选 topicKey/topicValue 标记同一单值主题，宿主确定比较；文字不同本身不构成矛盾。按 Accepted ADR 81 决策 4，明确更新的 verified/stated 记录可取代旧条目，保留旧版本与 supersededBy。不能确定取代的同主题互斥值，两条均 conflicted，宿主投影稳定冲突卡与记忆页选择；用户保留一条后另一条 forgotten，选择沿类型化既有 project-memory:restore 请求的冲突选择字段，记忆真值仍在 store。卡内双方陈述/来源可见，解决不能改其他项目。

## 必要路径
原卡 maintenance/conflict/memory-store/card-projection/记忆页；补既有 memory admission/Curator、MemoryProvider 工具 schema、快照/检索、已注册 project-memory Context Source、protocol memory 可选字段与现有 restore 请求、preload 已有类型、renderer drawerState、i18n、Desktop project-memory-service、project-facts 与 Host 的日维护装配、runtime exports 及聚焦/集成测试。新增文件锚点读取 adapter 放在 memory 模块并复用既有 HEAD 读取接缝。DATA_STORE_ENTRIES 不新增根条目，更新 projectRuntime 注释与知识清单。无新 IPC 通道/工具；main.mjs 不改。

## 退出验证
过期/90 天衰减/固定与职责例外、不同作用域隔离、同主题同值/互斥值/权威新值取代、冲突选择和重启持久、文件变更待核实/越界/纯维护无模型、简报警示/有效检索与快照、日维护/经典/无租约/关闭、完整受影响包、build/typecheck/architecture/ipc 和双平台 CI。
