# R5-02：Git 历史正文与同提交导航

创建时间：2026-10-26
最后更新：2026-10-26
状态：当前 R5 / R5a / R6 定向组合验证通过；非完整阶段/发布验收。详情见文末组合验证补记。

## 目标与依赖

历史文件绑定完整提交，与当前文件/其他提交同时打开；当前已删除的历史文件仍可读；嵌套相对链接沿同一仓库和提交，缺失不自动替代。只读查看不动原工作树、索引、任务、模型或权限事实。

分级 A/B/C。依赖 R5-01 代码提交 `a81a049ce677d19c7b05f8fc8835e1d0d305d82f`（PR #221）和知识提交 `a9b241ad3701eea6eb24fb12453b4d52e7075960`（PR #79）；两 PR 尚在评审，按用户明确继续在独立后续分支叠加，不修改其分支，不把依赖称为已合并。代码分支 `codex/resource-workspace-r5-history`；知识分支 `codex/resource-workspace-r5-history-docs`。不发布，不重启日常实例。

## 范围与事实源

允许：protocol/document-reference；Desktop bot-document-reference resolver 与新建历史路径/Git 正文 Module；FileAccess 只读接线、bootstrapPreloadApi 的结果类型；Workbench 的 DocumentSession/revision 规范化与标签身份、版本读取、历史入口组件、ScopedDocumentPage、views/DocumentView、ResourceChanges/resourceComparisonState、ResourceLauncher、useResourcePresentation 与既有 resource-workspace.css；相关测试；本卡、R5 总卡、ADR109 和两份体验矩阵。

不新增 IPC 通道、模型工具或物理存储路径；不改 main.mjs、任务调度、授权刷新、System Context、PermissionGrant、Evidence、模型配置、用户文件和其他本地改动。范围校验仍是现有 resolver；历史普通 blob 由独立 Module 读 Git 对象，不把虚拟文件当允许根。Git 命令必须只读、有界、禁止远端懒取和 replace-object；普通 live 读取保持原约束。

## 体验与恢复

事实源是宿主确认的来源、仓库、提交、准确 tree entry 和 blob；模型文字/分支名/恢复元数据不创造文件存在事实。局部状态包括读取、就绪、缺提交、缺路径、格式不支持、超限、权限/来源失败。复用现有右侧纸面、模式/来源/局部反馈，不加弹层、自动消息或新动效。

用完整 SHA 输入或提交比较的已确认端点明确打开历史标签；历史标签可明确另开当前文件。标签、最近和恢复保留历史身份，来源消失时局部失败。阅读位置按版本/模式恢复；不抢 Composer、IME 或对话阅读锚点。历史页的本地链接保留 repositoryId/commit/task，不能猜其他仓库；目录/子模块不自动导航或执行。

## 回归用例设计

| 组 | 宿主 | 前端 |
| --- | --- | --- |
| H1 历史准确性 | 当前内容不同/已删除时只读目标提交；缺 commit/path 明确失败 | 当前/历史并列，刷新不漂移，标签来源完整可查 |
| H2 范围 | 跨 Bot/任务/仓库拒绝；词法/符号链接逃逸拒绝；缺父目录仍在原根解析 | 缺来源不换对象，历史链接不降级 live |
| H3 Git 安全 | 完整 SHA 校验；准确 literal path；目录/符号链接/gitlink 拒绝；timeout/size/binary/图片字节与条件读取 | 格式/失败局部反馈，不显示假完整正文 |
| H4 导航恢复 | 每次恢复重核仓库/提交 | 嵌套历史 Markdown、行号、最近记录、非法 schema、独立读位/模式、当前文件动作 |
| H5 旧链兼容 | metadataOnly 不读 blob；原 live/目录/比较不变；无 checkout/restore/fetch/write | 原正文/源码/Diff/网页入口保持；迟到不串内容，不发送输入 |

当前普通继续未要求新一轮测试运行，依 Validation Scope 编写用例并作内容/diff 审阅，不自动运行 build、测试、截图或 CI。R5-01 的 51 项/11 图不算本包通过；当前状态不称实现验收。真实 Electron 历史跳转、窄窗长提交、键盘/IME/读位与整个进程恢复待明确要求或发布前验证。

## 本批实现与审阅记录

- 宿主：新增 `historical-document-path.mjs` 和 `git-document-reader.mjs`，现有 Bot/任务/知识库 resolver 只对显式 revision 接受根内虚拟文件定位。Git 读取核对实际仓库、完整 commit、准确 literal tree entry 与普通 blob，按对象大小和实际字节读取，metadataOnly 不读 blob。图片/文本沿既有服务与限额，不进入其他读写/执行接口。
- 命令拒绝缺失安全选项的 Git；清掉继承环境中可改选仓库/对象库的 GIT_DIR 等覆盖，禁止懒取和 replace-object，设置单次 timeout/maxBuffer。实现只读取 Git 对象，不切分支、不 checkout/restore、暂存、提交或抓取远端；本批未运行这些读取来操作日常任务。
- 界面：当前文件的折叠“查看历史版本”沿共享 MotionDetails，输入完整提交 SHA 后显式另开；历史页显示完整提交及独立当前文件动作。历史 Diff 模式不可用并说明原因。比较端点入口沿已确认 SHA，重命名分别采用旧/新路径；新增/删除的缺侧明确不可读。
- 身份：live/不同 commit 去重、独立读位、最近和恢复保留 revision；非法恢复丢弃，不降级 live。嵌套本地链接沿宿主确认仓库/提交/任务来源，外部网页/图片继续沿原入口。经典工作台缺 Bot 上下文时不拿当前文件冒充历史。切换模式保留历史定位输入，不改变 Composer 或对话滚动。
- 新增/扩展用例：真实临时 Git 仓库的删除、当前内容不同、字面路径、特殊 entry、限额/图片/失败缓冲、移动分支、禁用安全标志时拒绝；resolver 的祖先/符号链接逃逸、任务归属；文件服务无 live 回退；前端完整 SHA、同提交导航、旧服务失败关闭、当前/历史并列恢复与显式导航。源码用例未运行，不报告数量或通过结论。

本轮完成内容/diff 自审，`main.mjs`、IPC 通道目录、任务/授权/写入链未改；体验覆盖矩阵同步为实现自审。代码/知识均在 R5-01 之后的独立本地分支，未改 PR #221/#79 的远端提交；未提交推送、未发布、未重启日常应用。后续 R5-03（网页与目录恢复增强）已补源码，未运行验证，见 [实施卡](resource-workspace-r5-recovery.md)。


## 2026-10-26 后续组合验证补记

用户明确要求补跑后，当前 R5 / R5a / R6 组合已完成 Desktop 构建/类型检查、架构/UI/IPC 核对、338 项模块测试及明暗 30 组生产 Electron 联调；31 张图片逐张实现者自审。此记录更新上文“未运行”的实施时状态，不用旧 R5-01 结果背书。定向覆盖、实际修复、失败重跑、保存确认与未覆盖限制见 [组合验证记录](resource-workspace-r5-r6-validation.md)。未发布、未接入个人现场，不表示完整阶段或发布验收通过。
