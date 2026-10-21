# 主 Bot 权限归属：修改明细、评审与验收

创建时间：2026-10-21
最后更新：2026-10-21
依据：[ADR101](../../knowledge/decisions/101-bot-owned-access-policy.md)。用户授权本轮设计、评审、实现与测试；交付范围不含发布或替换日常安装版。
代码基线：`codex/parallel-task-list`，`8f0109d4`；知识基线：本地 `main`。以下路径均相对 Peer-Agent，不保存本机绝对路径。

## 1. 改动明细评审

| 层/文件 | 修改要求 | 容易漏掉的情况 | 通过标准 |
|---|---|---|---|
| protocol 新 `bot-access-policy.ts`、`index.ts` | typed 策略快照、读写请求/错误、审计来源，grant/approval 可选版本 | 客户端伪造父 Bot、传任意未知字段 | runtime 严格校验；不接受客户端指定 owner |
| runtime-node 新 BotAccessPolicy Module | SQLite 事务、单调 revision、CAS、主体绑定、legacy migration、损坏拒绝 | 多进程初始化、归档/删 Bot、换父、同值保存、未知 schema | 原子持久与负向测试通过 |
| `data-store.mjs` | 在 device 的 projectRuntime 注册新库用途 | 设置导出把 Full 带走 | portable 导出不含策略库 |
| `permission-inheritance.mjs` | 保留现有资源范围、扩展策略版本身份 | 4 层父链、循环、无父、legacy 图片许可 | 无效链拒绝，旧资源许可只在初始版本有效 |
| `one-time-approval.mjs` | 恢复许可加入版本匹配 | 改权限后再 resume、降后升复活 | 同参数也不能复用旧版本 |
| Desktop `llm-chat-service.mjs` | 装配共享权限解析 seam，保留 turnProfile/sendMessage 参数表 | 并发主回合、非 Bot ordinary goal、worktree | 每次请求查询，不改全局闸来冒充 Bot |
| Desktop `permission-gate.mjs` | 文件/通用/Shell 三入口统一查当前主体；scope/source/recovery cache 版本化；等待和 validate | 只有图片修了、scope 优先绕过新策略、全局改档撤掉别 Bot | 三入口与长回合、并发和晚到批准测试 |
| `project-agent-application-service.mjs` | 独立 read/update port、当前主体验证、CAS、变更广播、陈旧批准检查 | generic profile 修改提权、存储失败已显示成功、计划批准混淆 | service 返回真实存储快照；不增角色能力 |
| Desktop Host 装配 | 共享数据根与可信 profile/plan store，启动迁移早于执行 | 权限库初始化晚于恢复、两份内存真值 | 多实例同磁盘真值，错误拒绝 |
| IPC 注册/catalog/preload/contracts/clientApi | 新 typed 通道，仅本地已注册 IPC，按生成流程同步 | 远程路由复用、漏 bridge/fallback/mock | ipc:check 和契约测试通过 |
| Bot UI 新控件及状态 reducer/hook | 主输入框权限选择，保存后更新、失败可重试、跨 Bot 响应隔离 | 乐观 Full、切 Bot 后晚到回执、保存中发送、窄窗重叠 | 生产 IPC 窗口交互 + focused state tests |
| 经典任务 UI 新访问控件 seam | 子任务只读继承并可回主 Bot；普通会话保留旧下拉 | 子窗口残留可用旧 handler、停掉任务展示误成可执行 | 主体由宿主回读；原大组件净增受控 |
| i18n / CSS / SVG | 中英解释作用范围、继承、错误、保存中；复用 SVG | icon 字符、隐藏错误、无键盘焦点、长 Bot 名 | conventions/typecheck/截图检查 |
| TUI `tui-host.ts` / `tui-turn-executor.ts` | 同库、每 Provider 读取，Bot session 缓存绑定 revision | 回合开始固定 Full、无审批者先拒绝已授权 read、TUI 全局开关覆盖 Bot | host/turn executor 真调用回归 |
| 远程、Quick Chat、Automation/Probe/Skill/MCP | 审核现有入口不新增提权 | 客户端字段、普通文字/summary 冒充 grant | 负向契约/执行回归，现有显式政策优先 |
| 产品包脚本与测试夹具 | 增加主 Bot 选择、子任务继承、两 Bot 隔离、失败回退、等待中改档 | 旧 Full 夹具只设置全局导致误测、预制卡替代实际请求 | 绑定当前 Bot policy，真实 provider/像素/证据通过 |

## 2. 评审结论与实施门槛

设计自审结论：不能只改输入框。真正需要同时收口的是授权主体、当前策略读取、批准版本、持久恢复和多宿主。采用共享 BotAccessPolicy seam 后，没有必要给 spawn 增加 accessLevel 参数、给中央工具宿主新增能力分支，或把权限写进 prompt。

开始实现前已明确：设备本地库；旧 Bot 冻结原档位；新 Bot Ask；每次操作动态继承；主 Bot/Verifier 只读不变；一次批准不扩散；所有真实策略变化失效旧版本；不自动批准既有等待；普通独立会话继续全局；远程无提权入口。没有把机器测试或实施者自审叫作独立产品验收。

## 3. 分层测试清单

- T01–T08 存储：迁移 Ask/Full/restricted/非法值、幂等、新 Bot、CAS 双实例、磁盘失败、损坏/未来 schema、设备导出隔离、归档/换父。
- T09–T17 身份：根 Bot、直属 Worker、嵌套 Worker、Verifier、普通同路径会话、跨项目/worktree、伪造 profile/plan/session、循环/断链/深度、停止/取代/租约丢失。
- T18–T28 执行：文件/Shell/通用各档位、同一长回合改档、同值保存、Full→Ask→Full、图片解码期间改档、缓存与图片继续上下文、scope 操作隔离、once 恢复、stale 卡、计划批准不变、同时等待互不误批。
- T29–T35 多入口：Desktop 双 Bot 并发、TUI 长回合与 fresh host、Desktop↔TUI 租约转移、经典任务窗口、Quick Chat、远程拒绝修改、Automation/Probe/角色 deny。
- T36–T44 界面：主 Bot 控件、真实保存与重启、失败重试、冲突回读、切 Bot 晚回执、子任务只读并返回主 Bot、主对话真实授权卡、窄窗深浅色、键盘与可访问名称。

测试顺序：先针对缺陷写失败反例 → 实现 → focused tests → 受影响包完整测试 → build/typecheck/architecture/IPC → 标准产品 capture → 逐图写 review.json → verify。保持原 deny/cancel/timeout/stop 测试，不以 skip 或提高阈值换通过。

## 4. 实现评审结论（实施者自审）

本轮为实施者自审，不是独立审查。下列问题在交付前发现并收口；没有降低角色闸、放宽显式拒绝规则或把模型文字当成批准。

| 评审项 | 发现与最后处理 | 可执行证据 |
|---|---|---|
| R01 主体与迁移 | 原全局档位移为设备本地、每 Bot 的追加版本记录；旧 Bot 冻结原档位，新 Bot Ask；同值保存不升版本，双实例 CAS 冲突回读 | `bot-access-policy.test.mjs`：旧值、非法值、重启、新 Bot、双实例、降后升 |
| R02 存储失败 | 不使用会重建损坏库的缓存 helper；未知 schema、迁移中断与不可写目录拒绝；迁移事务不留部分版本或完成标记 | 同文件：损坏、未来 schema、迁移回滚、不可写 |
| R03 导入与导出 | 仅 device 保存权限还不够：导入的 portable 全局 Full 不能在新设备首次迁移时变成 Bot Full。导入前保存收紧标记，已有本机授权不被覆盖 | 同文件：portable export 排除、Full 导入初始化 Ask、后续导入保留本机明确选择 |
| R04 父链与恢复 | 从宿主 Plan/Conversation/Profile 回读 workspace、parent、session；暂停、取消、取代、循环、断链、超深不回退全局 Full；历史展示与执行分开 | 同文件：父链与生命周期；Desktop `chat-runtime/bot-access-policy.test.mjs` |
| R05 三类审批入口 | 文件、通用本地能力、Shell 使用同一主体；scope、source replay、once recovery、图片资源许可绑定版本；旧卡晚到操作不得签发新许可 | Desktop Gate、permission-inheritance、image lifecycle、service 的 stale recovery tests |
| R06 运行中变更 | 不是回合开始复制档位。每次调用回读；每次派发绑定策略版本，在异步 Hook 之后、Provider 执行前再次校验；文件副作用前、图片解码返回前校验 | TUI `project-agent/bot-access-policy.test.ts`：同回合改档、等待关闭、异步 Hook 改档后文件未写；Desktop 实际 PNG 像素撤权 |
| R07 持久旧卡 | 只关闭活跃等待还不够。更改策略后同时退役本 Bot 的旧 open/stale 工具卡；计划批准和独立经典会话不被误关闭。若展示回执落盘失败，版本闸仍禁止旧许可复用 | service test：旧工具卡过期、计划/普通会话保留；恢复批准不复用旧 revision |
| R08 经典会话兼容 | 不能用进程 epoch 作为跨重启图片资源身份。经典资源继续用稳定主体并在改档时持久撤回；Bot 资源绑定持久 revision，不受其他全局改档影响 | 原 `image-permission-inheritance.test.mjs` 与新跨 Bot / 全局切档测试 |
| R09 角色与显式政策 | Full 只影响审批，不开放主 Bot/Verifier 写能力；Probe/Automation、Hook deny、租约和取消仍走既有执行闸；SDK/Provider/Projection 无新增旁路 | 已有 project-agent mode、probe、permission-review、TUI project-tool-provider、host-adapter suites |
| R10 事实追踪 | 只给真实 Provider 返回的 grant 补宿主派发时的策略版本，不另造许可；TUI 文件/Shell grant metadata 保留版本，图片许可保留具体文件范围与 TTL | 真实 Desktop service 工具流水线的 `agentProgress.onToolExecution` 断言；TUI 实际写文件的 grant metadata 断言 |
| R11 UI 真值 | 主 Bot 保存成功才展示新策略，失败保持原值，冲突显示宿主当前版本；切 Bot 后忽略晚回执。保存期间禁用发送并保留草稿；继承任务不能独立保存权限 | `botAccessPolicyState.test.ts`；真实窗口选择/CAS 存储读取/子任务只读/返回主 Bot |
| R12 壳与入口 | 经典壳仍可读 Bot 权限事实，避免把子任务误当全局授权；修改通道仅本地主窗口，Quick Chat 和远程没有提权端口；TUI Bot 使用同库 | IPC catalog、local-only port test、TUI host/turn executor tests |
| R13 UI 与大模块 | 逻辑集中在共享 authority、service、状态控制器和小控件；ChatSurface 保持 3306 行，只替换展示 seam；图标、圆角与 Context 约束保持 | 两个原 ChatSurface 行数测试、typecheck、architecture/UI conventions |

### 4.1 实际实现位置

- 契约：`packages/protocol/src/bot-access-policy.ts`、`index.ts`、`delegation.ts`、`local-image.ts`。
- 共享权威：`packages/runtime-node/src/project-agent/bot-access-policy.mjs`、`permission-inheritance.mjs`、`one-time-approval.mjs`、`approval-store.mjs`，以及 `data-store.mjs` 的导入保护和 device 注册。
- Provider：`packages/runtime-node/src/file-provider.ts`、`shell-provider.ts`，Desktop `local-file-provider.mjs`、`local-shell-provider.mjs` 的执行前校验。
- Desktop 装配：`llm-chat-service.mjs`、`chat-runtime/permission-gate.mjs`、`projected-tool-executor.mjs`、`project-agent/bot-access-policy-service.mjs`、ApplicationService/Host。
- 传输：IPC catalog/registration、生成的 preload、preload TS contract、clientApi；没有新增远程操作。
- 表达：BotAccessControl、useBotAccessPolicy、botAccessPolicyState、BotComposer/BotConversation、ConversationAccessControl、任务现场返回主 Bot 的既有导航接缝与 i18n/CSS。
- TUI：`tui-host.ts`、`project-agent/tui-turn-executor.ts`；只迁移初始化的 authority 及时 close，避免每个执行器保留额外连接。
- 验收：新增核心/服务/状态/TUI 测试与 `bot-access-policy-checks.mjs`；标准产品包加入四张权限截图与必过机器结果。原图片 UI 夹具显式绑定当时的 Bot revision，真实生命周期夹具读取生产 Bot 权限，不再靠 scenario 指定 Full。

### 4.2 范围与实现约束

权限始终由本机 Runtime 保存和判定。Renderer 只持有宿主回执和保存中的交互状态。没有新增 System Context 指令、模型可签发的权限字段、独立执行通道、能力分支、BotProfile 可移植授权、默认子任务提权或远程批准。

已经启动的 Shell/外部副作用不能靠改档位回滚；本次保证后续派发与受控 Provider 执行前校验，不承诺所有第三方 Provider 的跨进程原子撤销。已经进入模型的内容不能被撤回。默认 TUI 没有本地图像解码 Provider，本轮不声称验证 TUI 看图闭环。

## 5. 实际验证记录

固定验证副本全工作区已按串行包执行通过：8,557 passed、5 skipped、0 failed。五项为既有 skip：两项需显式开启的 Electron 专项、三项“已完成计划复用不再经过文字核验阶段”的不适用场景；本轮没有新增 skip。Desktop 主测试 5,610 passed、5 skipped，补充脚本 3 passed；TUI 763 passed；Runtime Node 1,393 passed。原组合源码产品回归完成 201 张逐图自审及 verify；最终独立 PR 提交另完成 193 张逐图自审及 verify，均 passed，指纹和范围分别见 §5.3、§5.4。初次失败和隔离依据保留，详见下列说明。

| 实际命令 | 结果 | 范围 |
|---|---|---|
| `pnpm build` | 通过 | 全工作区，真实 Rust release 助手与 CLI 构建 |
| `pnpm typecheck` | 通过 | 全工作区 TypeScript / JS 检查 |
| `pnpm architecture:check` | 通过 | 架构治理、SVG 与 UI 规范 |
| `pnpm -r --workspace-concurrency=1 --if-present test` | 8,557 passed / 5 skipped / 0 failed | 固定副本最终完整重跑；Node 7,794 + Bun 763 |
| Desktop `ipc:check` | 通过 | 334 canonical channels / 332 preload operations / 291 main registrations |
| `pnpm qa:product:test` | 6 passed | 验收程序拒绝缺审查、旧源码、错截图及未处理 blocker |
| `pnpm ui:test`、`marketplace:test`、`changelog:test`、`upgrade:test` | 通过 | 主工作目录此前完成的根级检查；升级/回退矩阵使用真实 tag 夹具 |
| `git diff --check` | 通过 | 代码与知识变更无空白错误 |

新增 focused 用例共 27 个：共享策略 11、Desktop 权限链 6、ApplicationService 4、renderer 状态控制器 3、TUI 真实 Provider 3；均纳入上述完整测试。实际 Tool Call 的 grant provenance 断言另外加入既有 Desktop 流水线测试，不以测试数量冒充独立场景覆盖。

### 5.1 首次失败与复验

- pnpm 环境初始为 11，自动尝试升级工作区构建配置；已撤掉自动插入的配置，使用仓库固定 pnpm 10.22.0，没有把依赖批准配置变更交付给用户。
- 初始 Node 24 与并发包压力下，Runtime 的恢复时序一项、TUI 的共享委托集成一项失败；文件隔离复验均通过。改用仓库基线 Node 25，并串行执行工作区包后，完整测试通过；未加超时、未跳过失败用例。
- 旧图片撤回测试暴露经典资源许可未持久撤回，已区分经典稳定主体与 Bot revision，并保留跨重启撤回断言；不是改测试期待来规避撤权。
- Desktop 宿主流水线测试原来用没有持久父子身份的画像。新规则拒绝该画像，测试改为提供宿主 profile/plan/conversation 事实，仍实际走工具流水线，并新增 grant 策略版本断言。
- 两个 ChatSurface 固定行数测试首次失败，已保持原 3306 行，不提高上限。
- 原生凭据助手未构建导致 lab isolation 测试失败；临时工具链实际编译 Debug/Release Rust 助手后复验。未用占位程序、复制安装包二进制或跳过断言。
- 首次窗口夹具错误地用普通会话创建接口传 parent，随后发现缺 capturedAt，以及响应式切换会重建嵌套现场。夹具改用生产 createChildConversation、有效快照与宿主元数据，每个尺寸实际打开并核对继承状态后截图；没有放宽权限或截图断言。
- 第一份完整产品包采集成功并逐图审查 201 张，但共享工作目录在采集/审查期间被其他会话修改。verify 按源码指纹拒绝该包，未修改指纹或绕过校验。随后创建固定验证副本，排除另一项未完成生命周期重构，仅在副本恢复对应基线；原工作目录不回退、不覆盖。组合副本的生命周期测试失败也保留为隔离理由，权限功能以固定副本重新全测和截图。

### 5.2 工具链与数据隔离

本机原 PATH 没有可用 Node/Rust，使用仓库外临时 Node 25.9.0、pnpm 10.22.0、Bun 1.4.3、Rust 1.99.1；没有修改用户 shell 配置。Rust 下载和 crate 源的网络失败在临时工具目录中重试，仓库 Cargo.lock、包锁与用户全局配置不变。Debug/Release 助手和 CLI 只写忽略的本地构建目录，不替换日常安装版。

测试与截图使用临时数据目录，未批准、重置或改写用户真实任务和权限。当前工作区还有另一项独立界面修改（过程布局、历史授权回执表达）；本任务保留这些改动，没有将它们算作权限功能交付。标准产品包已绑定固定组合源码，并逐图据实审查。

### 5.3 产品验收事实

- 标准命令：`pnpm qa:product:capture --output <repo 外临时目录>` → 逐张检查全部 201 张截图并写 `review.json` → `pnpm qa:product:verify --output <同目录>`，最终 passed。
- runId：`e82cb660-d436-4856-accf-a7c41f277259`。
- sourceFingerprint：`b846c550f4cb9f947f3db655f2b7ac03cee24dd92a0e6b28355f0c732e5906fa`。最终隔离副本复现了其他会话开始生命周期重构前的这份源码；没有修改验收指纹、降低断言或复用旧 runId。
- 四张权限截图直接来自生产 renderer、preload 和本地 IPC：主 Bot 选 Full 后宿主存储回读一致，另一 Bot 策略未变；真实父子会话元数据解析成功；子现场无独立权限下拉，键盘可返回正确主 Bot。深色 1280 与浅色 760 均检查。
- 关联回归验证实际图片 Projection、ToolHost、权限门、Electron 像素解码和 Evidence；Full 连读四图无批准卡，Ask 的单次/本轮允许、拒绝、取消、停止和超时均走结构化生命周期。
- `pageErrors=0`、`mainAuthorizationErrors=0`。键盘、可访问名称、焦点返回、窄屏布局与已覆盖的对比度检查通过；单张截图不被用于证明动态性能。
- 评审者为本轮实施者，`independent=false`。没有独立审查或定时无人值守模型审查。
- 未覆盖真实云模型语义质量、真实模型网络时序、已安装 RC、完整屏幕阅读器或长期运行验收。Quick Chat 原生透明窗口的截图不能证明真实桌面合成对比度，作为既有 minor 覆盖限制记录；未将此称为完整无障碍通过。

持久记录：[验收收据与源码文件哈希](evidence/bot-owned-access-policy-20261021/receipt.json)、[全部 201 项图像观察](evidence/bot-owned-access-policy-20261021/review.json)。完整机器包和测试原始日志留在本轮临时产物目录，收据保存其哈希与名称。共享目录中的其他在途重构不包含在此通过结论内；隔离排除列表也保存在收据中，主工作目录未因此回退。

| 已核对关键界面 | 深色宽屏 | 浅色窄屏 |
|---|---|---|
| 主 Bot 权限选择 | [1280](evidence/bot-owned-access-policy-20261021/bot-access-1280-dark.png) | [760](evidence/bot-owned-access-policy-20261021/bot-access-760-light.png) |
| 子 Agent 继承状态 | [1280](evidence/bot-owned-access-policy-20261021/bot-access-child-1280-dark.png) | [760](evidence/bot-owned-access-policy-20261021/bot-access-child-760-light.png) |

### 5.4 PR 交付范围

代码 PR：[Peer-Agent #177](https://github.com/ly-ccx/Peer-Agent/pull/177)，提交 `c67758c78d348aeecef24685bd3a85ce7d05dbb5`。以现有 #174 的 `codex/parallel-task-list` 为叠加基线，PR 自身仅包含 57 个权限相关文件；#174 合入后应将 base 转到 `PeerAgent/dev/0.1.0`。

提交前已从隔离副本移除 #175 的过程留白和 #176 的文字层级/授权回执修改，没有改动原共享目录。权限变更关闭提示在既有 CardView 展示接缝中保留，不依赖新的 ApprovalReceipt；与 #176 后续整合时须保留该提示，原集成方案见 §5.3 对应源码与记录。生命周期重构 ADR102 及其代码不在本组 PR 中。

独立 PR 范围重新执行全工作区 build、typecheck、architecture、IPC 和完整测试，8,557 passed / 5 既有 skipped / 0 failed。随后按该提交重新执行标准产品 capture，逐张检查全部 **193 张**截图，写入具体观察并执行 verify，结果 **passed**。本轮移除了 #175/#176 专有的八张截图，§5.3 的 201 图结果仍只对应原组合源码。

- 最终 runId：`ff8e8f7f-9b42-4618-a72e-4b32f5b78c0f`。
- 最终 sourceFingerprint：`60980ad3c2829e3d38786e63c7b9053f723ad2ead952bd9d786df57db5769805`，对应上述 `c67758c` 提交。
- `machine.ok=true`、`pageErrors=0`、`mainAuthorizationErrors=0`；主 Bot 真实本地 IPC 保存、持久回读、跨 Bot 隔离、子任务只读、返回主 Bot 和键盘操作均通过。
- 审查为实施者自审，`independent=false`；真实模型、安装版、完整读屏与长期使用未覆盖。Quick Chat 透明窗口合成对比度继续作为 minor accepted-limitation 记录。
- 当前叠加 base 不在仓库 CI 的 PR 目标分支过滤范围内，GitHub 尚未触发检查；本地通过不表述为 CI 通过。#174 合入并将 base 调整到开发分支后须确认 CI。

配套知识库 PR：[Peer-Knowledge #56](https://github.com/ly-ccx/Peer-Knowledge/pull/56)。最终持久记录：[提交与验收收据](evidence/bot-owned-access-policy-pr-20261021/receipt.json)、[全部 193 项截图观察](evidence/bot-owned-access-policy-pr-20261021/review.json)。收据包含全部 57 个变更文件的哈希及本轮日志哈希。

| 最终提交关键界面 | 深色宽屏 | 浅色窄屏 |
|---|---|---|
| 主 Bot 权限选择 | [1280](evidence/bot-owned-access-policy-pr-20261021/bot-access-1280-dark.png) | [760](evidence/bot-owned-access-policy-pr-20261021/bot-access-760-light.png) |
| 子 Agent 继承状态 | [1280](evidence/bot-owned-access-policy-pr-20261021/bot-access-child-1280-dark.png) | [760](evidence/bot-owned-access-policy-pr-20261021/bot-access-child-760-light.png) |
