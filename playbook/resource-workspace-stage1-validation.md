# 资源工作区第一阶段测试与基础联调记录

创建时间：2026-10-26
最后更新：2026-10-26
状态：当前已实现路径的测试与基础联调通过；不是发布验收，也不包含后续阶段。
首轮验证候选：`cf36905a4e313356b0cbb061be2f8fc250852784`，见 [代码 PR #220](https://github.com/ly-ccx/Peer-Agent/pull/220)。

用户明确授权本轮运行第一阶段测试和前后端联调、修复发现的问题。所有运行均在提交用的独立 checkout、临时数据目录和临时 Git 仓库中进行，不加载日常应用数据或恢复用户任务。

## 结果

| 检查 | 当前结果 | 真实边界 |
|---|---|---|
| Desktop 及其依赖构建 | 通过 | Node 25.9.0；源码构建，不是安装包 |
| Desktop 类型检查 | 通过 | 包含新增组件、测试与 preload Interface |
| 架构、UI 约定、IPC 目录 | 通过 | IPC 目录 336 channels / 334 preload operations / 293 main registrations；不把目录校验当作全部 IPC 行为测试 |
| 第一阶段模块测试 | 40 个测试文件、240 项通过，失败/取消/跳过均为 0 | 引用与 Markdown、文档/浏览器会话和布局、读取代次、比较、目录、宿主服务、IPC 注册、同轮来源、分页历史及 Context Source；不是全仓测试 |
| 真实 Chrome CSS 矩阵 | 已纳入上述 240 项，无跳过 | 独立 headless Chrome，实际 CSS 与节点保留；原生 guest 另由 Electron 检查 |
| 真实 Electron 基础联调 | 明暗各 18 项，共 36 项通过，pageErrors 为 0 | 真实 main / preload / 生产 renderer 构建、临时文件/Git 与真实 WebContents；不调用真实模型 |
| 截图审阅 | 16 张逐张审阅，无本批阻断问题 | 实现者自审，不称独立审查；不代表完整无障碍或逐帧动效验收 |

最终修复后重建了 renderer，重跑类型/架构/UI 校验和模块测试，并在同一源文件组合上分别完成明暗 Electron 联调。旧候选的 335 项测试或 20 个场景没有计入本次结果。Git 提交只固化已验证文件，不修改它们的内容。

## 发现与修复

1. **重复行定位丢失。** `setDocumentSession` 对实时更新也调用 normalizer，原 normalizer 每次把导航 requestId 改成同一个 tab 身份。第一次定位后，新行号或重复点击被 hook 当成旧意图。现在合法 requestId 保留，旧/非法元数据才生成兼容 ID；单元回归经过完整 open → normalize → 再 open → normalize 链。真实 DOM 验证多次行定位及超范围回退。超范围提示移到正文滚动区上方，用户无需滚到长文末尾才能看见。
2. **窄窗横向偏移。** 资源布局已缩到 760px，旧 body 最小宽度仍是 1024px，浏览器焦点滚动使 documentElement 横移 100px，导致内容裁切和 macOS 返回按钮侵入原生控件区域。现在只对当前激活的 Bot 资源页面解除旧 body 最小尺寸；其他页面不适用该选择器。实际测量验证 body 为 760px、documentElement.scrollLeft 为 0、资源四周间距及原生控件避让成立。
3. **过时测试断言。** 一项 service 测试未包含新增的真实 workspaceRoot；三项源码约定断言仍匹配旧 open/width 表达式。已改为当前 interactiveOpen 和限幅 displayedWidth 语义，不降低产品边界。原 Electron 脚本仍假设裸文件名自动打开，已改为先经实际查找结果明确选中。

修复属于既有第一阶段呈现状态与测试适配，不新增权限、允许根、工具执行、存储或 Evidence 真源。

## Electron 实际检查范围

- 非模态打开及空启动器不创建 guest；实际文件名查找经 UI → preload → scoped 宿主返回结果，再选择文件。
- Markdown 正文/源码、长文各模式读位、起始行及重复定位、超范围反馈、本地图片实际解码、缺文件局部错误。
- 同轮短文件名从结构化来源打开；已确认知识库的跨仓库路径及文档内相对链接打开。
- 外部图片在明确点击之前没有 img 节点，也没有受控服务器请求；点击后才经原网页领域打开。
- 真实目录读取；未暂存、暂存和提交比较；移动分支后刷新仍用已确认 SHA；两个独立比较标签互切不覆盖。
- 范围外文件拒绝且秘密正文不进入 DOM；网页与文档互切后 WebContents ID 和页内输入草稿保持。
- resize pointercancel 清理、键盘调整、先收导航再让出空间、主动放大/恢复、紧凑视图往返、关闭归焦与普通切 Bot 隔离。
- 所有查看完成后，临时项目/知识库文件摘要、Git index 字节和 HEAD 与基线一致。只有测试主动移动了临时分支，以反证比较不随之漂移；这不是产品动作。
- 每个 Electron 实例按独立注册的进程身份关闭，记录 exited=true；未使用进程名通杀，也未停止日常实例。

## 截图审阅

每个主题各审阅八张：行号超范围、本地 Markdown 外部图片入口、独立比较标签、宽窗并排、主动展开启动器、工具栏角部、紧凑文档和紧凑启动器。

核对结论：两侧纸面 16px 圆角及上下边界一致；工具栏为 32px 方形图标且三侧实测 8px 内距，静态背景透明；右侧未遮挡宽窗对话与 Composer；紧凑视图有可见返回入口，内容不再横向裁切；长路径可换行、完整比较端点可读，错误反馈局部可见。近期列表纵向滚动，不因列表增长占据底部错误留白。

截图、日志、逐图审阅和 SHA-256 清单保存在本轮本机临时验证包中，不把机器路径写进 Git；跨机应重跑产生自己的包，不把本机路径当远端证据链接。

## 复现与限制

在对应代码候选按仓库工具链准备 Node 25、依赖和 Chrome，执行：

```sh
pnpm install --frozen-lockfile
pnpm --filter @peer-agent/desktop... --workspace-concurrency=1 build
pnpm --filter @peer-agent/desktop typecheck
pnpm architecture:check
node apps/desktop/scripts/resource-workspace-tests.mjs
node apps/desktop/scripts/resource-workspace-smoke.mjs --dark
node apps/desktop/scripts/resource-workspace-smoke.mjs
```

模块批次入口固定这 40 个测试文件，并显式启用真实 Chrome 检查；缺环境应报错，不把跳过算通过。Electron 脚本自行建立临时 Bot、项目、知识库和受控 HTTP 服务，并输出包位置和清理结果。不会发送消息给用户 Bot 或执行模型任务。

本结论限第一阶段已实现路径及其基础联调，不把设计文档里 G0–G8 的所有行统一标成通过。真实云模型、安装包、读屏、完整 IME/字体/动效组合、真实 OS 权限设置和后续 R5–R10 未在本轮验收；任务来源的精确归属/缺基准分支由模块用例验证，没有恢复个人现场任务来凑跨层通过。

首轮验证时当前任务、已有成果、原应用进程、原工作区文件及索引保留；未重复已完成写入，当时未合并 PR、未发布。

## 合并前 CI 复核（2026-10-26）

用户授权在评审无阻断且 CI 成功后合并 PR #220 与知识库 PR #78。上述 240 项/36 项本地验证仍精确对应 `cf36905a4e313356b0cbb061be2f8fc250852784`；不能拿它们冒充后续提交的全量 CI 结果。

该提交的 CI 两端均在完整测试失败，自动单文件重试后仍只有 `iconContract.test.ts` 失败：`useResourcePresentation.ts` 的标题来源列表用了独立字符箭头作为 join 分隔符，被严格 SVG 检查拦截。将该分隔符改为普通分号，比较两端的正文、完整路径、SVG 图标、读取/权限/执行接口均未改变。修正提交为 `18c9ab336704858d22508a25871c47c5737f6898`，本地严格图标及共享约定共 10 项通过；未修改扫描规则或绕过检查。

[CI #841](https://github.com/ly-ccx/Peer-Agent/actions/runs/40254906711) 的 macOS 与 Linux 构建、类型、架构和完整测试成功，随后两端均在窗口回归的同一旧选择器失败：`checkBotMessageLayout` 用 `.bot-profile` 点击设置，而新增工作区按钮复用了该呈现类，Playwright 严格模式匹配到两个控件。没有放宽严格模式或改变产品按钮；相关 15 份脚本中 24 个选择器统一改为按“机器人设置”的可访问名称定位，点击、键盘、焦点与原断言均保留。15 份脚本语法检查通过，继续以隔离实例复跑与 CI 完全相同的窗口命令；专项通过不代替全量结果。

本机完整复跑另外捕捉到收起态 2px 横移：document/body 的 scrollLeft 都为 0，而资源布局 scrollLeft=2、scrollWidth=1282、clientWidth=1280。原因是收起但保留挂载的纸面边框向父层贡献了溢出宽度；状态卡滚入会带动该父层。收起稳定态改为裁掉溢出，退出动画仍由原有 overflow:hidden 处理。新增真实 Chrome 回归检查宽度 1280、scrollWidth 1280、scrollLeft 0 及退出时的裁剪责任；第一阶段批次更新为 241 项通过、零跳过。

材质脚本也按实际外层资源画布检查背景，并增加内部壳透明、不重复着色的断言；减少透明度沿同一外层检查。设置分栏间距与宽度同时过渡时，等待原有几何条件成立后再断言，不放宽间距或用固定 sleep 代替。材质专项复跑通过。完整复跑随后发现旧 `ancestor::section` 查询把隐藏启动器“工具”的标题也算入任务分组；改为最近祖先 `section[1]` 后，生命周期专项 4 个场景通过，仍要求原分组标题“需要你”。

这些修正先固化在 `9d2b69860abfd524a255ab35d8464c31ffdc17a7`。本地完整窗口回归进一步发现旧无障碍脚本还要求设置按钮含可见文字，与已经确认的纯图标要求冲突；改为检查精确 aria-label、title、单个 SVG 和无可见文字，同时对英文切换使用精确 `Bot settings` 名称。键盘、页签、焦点、对比度及持久化断言保留。修正提交为 `72a55f700aef3fc5e58147c29a6a839a0347f10d`，新一轮 CI 自动取消旧 #842，开始[完整 CI #843](https://github.com/ly-ccx/Peer-Agent/actions/runs/40257705393)。最终提交的窗口回归未成功结束前不合并；旧运行和本机专项的通过不能代替它。

知识库 PR #78 的分支没有配置 GitHub Actions workflow，也无提交检查/外部状态；其结论是内容与差异审阅通过，不称“CI 已通过”。配套 7 份文档中 91 个相对链接目标均可定位。日常工作区和运行实例继续保留，不同步/重启应用、不恢复个人任务、不重放写入或发布。


### 任务工作树评审反馈与最终候选

远端评审指出任务比较的真实缺口：renderer 已核对归属并取 worktreePath，但它仍作为普通 Bot 文档交给宿主；默认内部工作树位于应用数据目录，不属于配置根，真实读取返回 scope_denied。先补 ADR109 §25，再由宿主在每次解析重新读取 Session 与 GoalPlan，核对 Bot/Session/Plan/report/delegationOrigin 与完整基准、实际 deliveryBinding。可选 task 来源描述保留到比较、当前文件、相对链接、最近记录和标签恢复；非法恢复不降级为普通引用。只允许该记录根内的既有只读动作，不注册全局内部目录、不修改模型工具/PermissionGrant/Evidence 或执行/写入链。

该修复提交为 `7f4ae9502ce71b18ccdb63eb1236ea2071de7469`。243 项模块测试零跳过；Desktop 及依赖构建、类型、架构/UI 检查通过。新增真实 Electron main/preload/renderer 场景使用配置根以外的临时 Git 工作树与暂停的合成 Session/GoalPlan：从任务来源读 Diff、保留比较标签、打开当前文件、嵌套相对文档、从最近记录返回；不带 task 或伪造 Session 均拒绝。明暗各 19 项，共 38 项通过，pageErrors 为空；临时文件摘要、Git index 与 HEAD 保留，测试实例自行退出。没有使用或恢复个人任务。

`72a55f70` 的本地 CI 同参数完整窗口回归也已成功，含 accessibility/diagnostics/streaming/effort-stability/work-surfaces；它记录修正后的无障碍与其他壳层行为，但不冒充后续任务来源提交的全量结果。`7f4ae950` 的[CI #844](https://github.com/ly-ccx/Peer-Agent/actions/runs/40258413373) macOS 全部成功；Linux 构建、类型、架构、完整测试成功，但窗口回归在 `checkBotCompletionReview` 的直接 `Promise.all(animation.finished)` 等待抛 AbortError。共享 Overlay 的 `useMotionSettled` / `watchVisualMotion` 在入场终态会 cancel Animation 释放 fill，旧测试错误假定捕获的 finished Promise 必然 fulfilled。此失败未被当成可忽略的通过。


最终脚本修正提交 `562efa5ff857e43a20081d6ed8bbbf3e02802380` 改为轮询同一浮层的 is-settled 和实时动画终态，不捕获会在正常取消后拒绝的 Promise；后台任务展开的同类直接等待也改为读取当前有限动画。报告正文、键盘/关闭、窄屏、确认/重试 payload 和任务行状态断言保留；新增 --completion-review-only 仅用于隔离专项，不改变 CI 全量参数或任何产品动效/任务逻辑。独立专项随后补齐明确的初始视口，提交 `012a005e50784c1855ba815ad5ee5326f020fafb`；查看报告专项七项行为均通过，pageErrors 为空、ownedStop.exited=true。最终源码重建后，资源联调再次明暗各 19 项成功（共 38 项），pageErrors 为空，两个实例 ownedStop.exited=true。最终提交的[CI #846](https://github.com/ly-ccx/Peer-Agent/actions/runs/40259866666) 已结束：macOS 与 Linux 均为 success，构建、类型、架构、完整测试和 Electron 窗口回归全部通过。仅按这一最终提交的回执作合并判断。
