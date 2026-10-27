# 资源工作区第一阶段跨机交接

创建时间：2026-10-26
最后更新：2026-10-26
状态：第一阶段开发交接；已实现路径的测试与基础联调通过，最终 CI 结果见验证记录；未发布。

> 本文件是第一阶段指定提交的历史交接，不是后续 R5–R10 当前 dirty 候选的验证或远端交接凭据。后续累计源码已继续到 R10，最新状态、落点和未验收边界见[源码覆盖表](resource-workspace-source-coverage.md)；其未提交部分不能假定另一台电脑已可获取。

## 领取的两条分支

| 仓库 | 远程分支 | PR 基线 |
|---|---|---|
| Peer-Agent | `codex/resource-workspace-stage1` | `PeerAgent/dev/0.1.0`，起点 `008e149e` |
| Peer-Knowledge | `codex/resource-workspace-stage1-docs` | `main`，起点 `7cf45f6` |

代码交接提交：[`012a005e50784c1855ba815ad5ee5326f020fafb`](https://github.com/ly-ccx/Peer-Agent/commit/012a005e50784c1855ba815ad5ee5326f020fafb)，对应 [代码 PR #220](https://github.com/ly-ccx/Peer-Agent/pull/220)。知识库提交身份以本文件所在配套 PR 为准；两个仓库都要获取。不要只获取最后一次查找/Diff 增量，那会遗漏工作区壳层、来源投影与适配器依赖。两仓按既有同级目录别名放置，或在本机设置 `PEER_KNOWLEDGE_ROOT` / gitignored `.peer-workspace.local.json`；不提交本机路径。

在新电脑自己的干净 checkout 中：

```sh
git fetch origin
git switch --track origin/codex/resource-workspace-stage1
```

知识库对应切换到 `origin/codex/resource-workspace-stage1-docs`。本地若已有同名分支，先检查其与远端差异，再切换；不要重置另一台设备未推送的工作。继续修改后提交并在同一轮推送各自分支，以 origin 对齐。

若 PR 已合并且专题分支被清理，代码改取 `origin/PeerAgent/dev/0.1.0`、知识库改取 `origin/main`，先核对目标线包含上述代码交接提交和 PR #78 的文档，再继续开发；不要为了切分支重置本地改动。合并只转移源码和契约，仍不恢复源电脑任务。

## 先读这些内容

1. 代码仓 `AGENTS.md` 与知识库 `playbook/change-intake.md`。
2. `knowledge/decisions/109-resource-reference-preview-and-artifact-collaboration.md`：接受范围 R1–R4d，尤其 §23 的搜索、歧义、Diff 与实时来源 Interface。
3. `playbook/resource-workspace-implementation.md`：按日期看最新实施记录，旧记录中的缺项可能已在末尾补齐。
4. `playbook/resource-workspace-regression-test-design.md`：G0–G8 前后端与跨层测试设计，不等于已执行结果。
5. 五份既有体验/动效/切换规范及两份矩阵；遵守代码仓当前 Validation Scope。

## 本次代码覆盖

- Bot 真实主会话映射、同屏非模态资源工作区、网页/文档混合标签、“＋”启动器和目录/比较入口。
- 默认侧面打开，优先收机器人导航；用户主动放大，确实不足时才单区往返；关闭归焦和中断退场，保留领域实例。纯图标、32px 控件/8px 等距、16px 纸面与会话一致；设置挤压时保正文读位。
- 文档默认 Markdown 正文，源码/图片/Diff 沿既有适配；知识库和相对来源在已有允许根内解析；歧义候选由用户明确选择。
- 历史和实时 Activity 从同轮成功结构化文件结果生成有界导航提示；规范历史不重写，分页派生索引 schema 4 只重建缓存。
- 显式文件名查找：Bot scoped resolver 先定根；查询 256 字符、40 结果、4000 条目、32 深度；不读正文、不跟随符号链接，部分扫描明确提示。旧服务无 scoped 回执失败关闭。
- Diff 文件索引与完整正文、未暂存/暂存/提交比较、真实任务来源；任务 owner/session/plan 和完整基准 SHA 匹配才比较，缺少隔离工作树不回退项目根；目录导航有面包屑。
- BrowserSession/真实 guest 保活与显式注意力规则沿既有 seam；后台请求不能把正在阅读的文档/目录/Diff 偷换成网页。
- 收尾补充：本地 Markdown 外部图片只作显式入口；确认真实来源后串行刷新；引用支持起始行且模式各记读位；固定比较不追随移动分支，可保留多个独立比较标签；目录代次隔离与宿主有界枚举已补源码。本轮模块测试及真实 Electron 基础联调已通过，范围见验证记录。

代码主要入口：`renderer/src/workbench/ResourceWorkspaceContext.tsx`、`ResourceLauncher.tsx`、`ScopedDocumentPage.tsx`、`ScopedResourceNavigator.tsx`、`ResourceChanges.tsx`（均在 apps/desktop 下）；宿主在 `electron/main/bot-document-reference.mjs`、`file-access-application-service.mjs` 与既有 workspace IPC；来源提示归一在 protocol/resource-reference-hints、runtime turn-activity/history 与 conversation-store 的 reader/worker。

## 拆分与排除

只提交本阶段累计实现及其必要依赖。共享 main、preload API、Protocol Project 和 turn-activity 已逐片段拆分。

本地另有的 Bot 自定义指令、授权刷新、任务生命周期/核验修复、服务商设置等在制改动未纳入本 PR。不能为了让本地试用组合和 PR 相同而把这些文件全部提交。源电脑的分支、索引、未提交文件与运行实例保留；此 PR 在另一个干净 checkout 组织。

## 验证状态与后续

用户明确授权验证。第一阶段固定 40 文件批次最终为 243 项模块测试（零跳过），最终重建的 main/preload/renderer 明暗各 19 项资源联调成功，查看报告专项七项行为通过；构建、Desktop 类型、架构/UI 检查通过。首轮 cf36905a 的 240 项/明暗各 18 项及 16 张截图自审另有精确记录，历史 335 项/20 场景不混计。合并前修复严格图标/无障碍脚本、收起态边框溢出和动画清理等待，并按 ADR109 §25 接上由宿主核对的隔离任务工作树只读来源；最终提交的全量 CI 结果单列于[验证记录](resource-workspace-stage1-validation.md)。

结论仅覆盖本阶段已实现路径，不等于设计表中 G0–G8 全部通过。真实云模型、安装版、完整 IME/读屏/字体/逐帧动效组合及后续阶段未在本批验收；没有重启日常应用、恢复个人任务或重放写入。自动 CI 按对应 SHA 单列，不把本地通过当作 CI 通过。

接手优先级：

1. 接手先核对代码 SHA 与验证记录；代码或依赖改变后，重跑受影响组，不沿用旧日志。
2. 继续补未覆盖的真实模型、安装版、任务来源跨层及 IME/读屏/字体/reduced-motion 等组合；必须使用隔离夹具，不用个人现场任务凑通过。
3. 真正发布前按 Release Gate 合并所有 open PR、冻结最终候选并执行完整构建/测试/类型/架构/IPC/产品回归。当前用户授权在评审无阻断且 CI 成功后合并 #220/#78，未授权发布。
4. R5 及之后的强版本身份、独立窗口与协作编辑/条件写入继续依原方案分期；第一阶段不增加写入、窗口迁移或新模型工具。

## 本地启动与现场连续性

新电脑按代码仓 README 的工具链/依赖要求安装，在本次分支执行 `pnpm install --frozen-lockfile`，需要本地看效果时用标准 `pnpm dev` 构建并启动本机 main/preload/runtime/renderer；仅刷新旧 renderer 不能加载宿主更新。启动代码不等于验证通过。

Git 不包含源电脑现有任务、会话、设置、Evidence、文件系统成果、密钥、浏览器登录态或运行中的进程。本次交接不复制应用数据、不迁移租约、不自动恢复执行。新电脑默认只接管代码开发，不推断自己已接管源电脑任务。

用户约束：保留当前任务和已有成果；禁止重跑已完成的写入；不得把文件路径/助手声明当完成或授权事实；缺失来源、基准或权限要明确反馈。若之后确需迁移任务现场，另按既有宿主租约、存储与恢复契约处理，先核对真实执行/成果记录；此文不授权复制运行中的数据库或让两个宿主同时执行。

本机配置、凭证、应用数据和 node_modules/dist 不进入这两个提交。此次不重启原应用、不运行模型请求或任务恢复，不发布版本。
