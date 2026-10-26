# 资源工作区第一阶段测试与基础联调记录

创建时间：2026-10-26
最后更新：2026-10-26
状态：当前已实现路径的测试与基础联调通过；不是发布验收，也不包含后续阶段。
代码候选：`cf36905a4e313356b0cbb061be2f8fc250852784`，见 [代码 PR #220](https://github.com/ly-ccx/Peer-Agent/pull/220)。

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

当前任务、已有成果、原应用进程、原工作区文件及索引保留；未重复已完成写入，未合并 PR、未发布。
