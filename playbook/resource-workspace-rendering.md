# R6：只读呈现适配与安全退化

创建时间：2026-10-26
最后更新：2026-10-26
状态：当前 R5 / R5a / R6 定向组合验证通过；非完整阶段/发布验收。详情见文末组合验证补记。

## 范围与目标

接续 R5 / R5a 源码，统一文档 Adapter 的实际能力、图片解码反馈、复杂 Diff 退化和展示预算；安全静态呈现与真实网页分离。B/C 级，只修改 renderer 的文件类型/呈现 kernel、Markdown/Source/Diff/Image 组件、ScopedDocumentPage、经典 DocumentView 的适配接线和必要的 Markdown 本地策略/导航 seam、相关测试/样式及知识矩阵。

不改主进程、Protocol/IPC、权限根、任务、模型、Evidence、System Context 或读取/版本/存储边界；不写原文件、不启动转换器或网页服务；不重启/恢复当前任务，不发布，不认领其他本地改动。

## 状态、事实源与注意力

读取成功仍来自原宿主 receipt；格式支持/展示退化只是 renderer 对已读字节的解释。本地 HTML/SVG 为源码；Markdown 不发隐式远程图片请求；图片有界数据、格式/尺寸核对、解码错误与缩放；复杂 Diff 的原始元数据保留，不生造行号。

超出富文本/逐行展示预算明确说明已显示范围；原文未改、读取版本不变，不将展示结果当 Evidence。恢复旧 preview 模式也遵循静态策略。错误与动作留当前对象，不重挂整页、抢 Composer 或自动滚动。复用 Frost/SVG，无新增动效或权限控件。

## 回归设计

| 组 | 前端 | 宿主/跨层边界 |
| --- | --- | --- |
| P1 静态安全 | HTML/SVG 普通打开与旧 preview 均仅源码；恶意 Markdown/图片无 eager 网络或脚本 | 原只读 IPC/范围/版本检查保持，不新增运行/转换调用 |
| P2 展示预算 | 长 Markdown 退源码，长源码/巨量空行/超长行有界并明确截断；空正文诚实 | 宿主读取限额未扩大；显示预算不回写版本/原文件 |
| P3 Raster | MIME/文件头/尺寸/解码成功与失败；正常/缩放/重置，切资源不串状态 | byte/version receipt 不冒充解码成功；不启用模型看图，不读取远端 URL |
| P4 Diff | 普通 hunk 真实行号；跨文件重置；combined/binary/rename/mode-only 退化并保元数据；超限明确 | 原 Git 比较基准/范围保留；不应用 Patch、暂存或提交 |
| P5 连续性 | 文件模式/读位、详情返回、隐藏/迟到和解码错误局部反馈 | 网页仍原 Browser/Registry，与本地源码路径分离；无任务重跑 |

只编写用例与内容/diff 审阅。实际前后端联调、构建、测试和明暗/缩窗/键盘/图片解码截图留待用户明确要求或发布；不能沿用 R5-01 结果。


## 实施与差异审阅记录

1. 本地 HTML / SVG 默认源码，旧 preview 模式恢复同样只渲染文本。经典 DocumentView 的 srcDoc iframe 已移除；普通入口与 Bot 范围入口采用相同格式能力判断。PDF/Office 没有正文 Adapter，明确限制；二进制仍消费原宿主失败，不宣称已转换。
2. MarkdownDocument 增加独立的 local-document 呈现策略，不依赖某个导航 Provider 是否挂载：不自动加载远程图片，也不因本地路径/图片文字触发存在性探测或缩略图读取。普通聊天图片行为保留。显式链接继续走既有入口；Classic 相对导航以当前显示文档目录为基准、沿原根读取，若旧宿主仅回传跨仓库根而没有精确文件路径，禁用相对目标，不猜仓库。
3. 纯展示预算：源码最多 200,000 UTF-16 单元 / 4,000 行；Markdown 富文本最多 100,000 单元 / 2,000 行，单行超过 16,000 单元同样退源码；结构化 Diff 最多 500,000 单元 / 8,000 行，单行超过 16,000 单元退原始源码。最终 SourceViewer 仍应用自己的较小预算。截断不切断 UTF-16 代理对，保留真实总行数并标明受限可见范围；不截断读取 receipt、不回写原文/版本。JSON 排版输入最多 100,000 单元、嵌套 64 层、结果最多 200,000 单元，不能排版时原文保留。
4. Raster Adapter 接受 PNG/JPEG/GIF/WebP/BMP 的 base64 data URL；最多 8 MiB、单轴 16,384、总像素 32,000,000。只扫描至多约 64 KiB 文件头确认 MIME 与尺寸，不能确认时失败关闭。ICO/AVIF 当前未提供头部 Adapter，不宣称支持；可沿原有编辑器入口查看。文件头检查不是完整 codec 验证，浏览器实际解码仍可能失败。失败/重读只作用当前图片；缩放在 25%–400% 范围，切换字节立即回到适应宽度；旧图片 DOM 与迟到事件隔离。
5. Diff 拆分为纯 hunk/退化 kernel、行呈现和文件索引 Module。hunk 数量、零起点、溢出坐标和跨文件游标核对；hunk 内的 `---` / `+++` 为正文，缺少末尾换行标记保留。combined、binary、重命名/模式变更、混合元数据、无法确认的结构均退化为原始文本，不隐去某个只有元数据的文件；没有 Git 分隔标记的多文件格式无法确认归组时同样退化。索引支持按钮点击后的持续全文阅读与收起，悬停只作 80 行快捷预览；所选文件消失明确提示，不换成其他文件或自动滚动。
6. 本包不改主进程、Protocol、IPC、权限根、执行、Evidence、System Context、版本/存储契约；网页继续复用既有真实 guest 与失败/重试入口。没有网页 DOM 注入、预览转换服务、模型看图授权或执行入口。没有新动效，继续沿 Frost/SVG 与原非模态工作区。

### 用例落点与实际状态

- `file-preview/presentationBudget.test.ts`：大量空行、字数/行数边界、代理对、空内容和总行数。
- `file-preview/documentAdapterState.test.ts` / `fileTypes.test.ts`：HTML/SVG 静态策略、缺 Adapter 提示、JSON 排版限额与深度。
- `file-preview/rasterImageState.test.ts`：合成文件头与五种尺寸编码、伪 MIME、远程 URL/SVG、字节/尺寸/像素上限。合成头仅核准入，不能冒充真实解码验收。
- `file-preview/presentationComponents.test.ts`：源码 DOM 有界和转义、超限 Markdown 不进富文本解析、图片解码失败/重试/切图迟到/缩放、Diff 点击后持续阅读与来源消失。
- `file-preview/diffPresentationState.test.ts` / `DiffViewer.test.ts`：hunk 数量/坐标、头样式正文、缺失换行、跨文件重置、复杂及混合 Diff 原始退化，保留既有 hover 清理约束。
- `file-preview/useClassicDocumentNavigation.test.ts`、`chat/components/markdown/inlineMarkdownPreview.test.ts` 与 `ScopedDocumentPage.test.ts`：精确基准目录、未知基准禁用、显式调用/原根、静态图片不 eager 请求、既有版本保留接线。
- 后端本包没有新增/改动；跨层回归仍需将原宿主范围/拒绝、版本 receipt、历史 blob 与这些前端入口联合执行，验证无新读取根和无写入。当前只是设计及用例编码，不等于联调通过。

本轮只作内容/diff 审阅，不运行构建、类型检查、模块测试、截图或交互。真实图片 codec（含长元数据 JPEG、animated 格式）、布局/键盘/读屏/减少动效与 Electron 前后端联调仍待明确验证；不能把 R5-01 的结果用于本包。保留已有 R5-02/03、R5a 的未提交源码，不更新 PR、不重启应用、不重跑当前任务和成果写入、不发布。下一包 R6a 为辅助导航与比较增强（文件/变更辅助侧栏、工作树动态刷新、多来源比较联动），按既有总计划另行收口。


## 2026-10-26 后续组合验证补记

用户明确要求补跑后，当前 R5 / R5a / R6 组合已完成 Desktop 构建/类型检查、架构/UI/IPC 核对、338 项模块测试及明暗 30 组生产 Electron 联调；31 张图片逐张实现者自审。此记录更新上文“未运行”的实施时状态，不用旧 R5-01 结果背书。定向覆盖、实际修复、失败重跑、保存确认与未覆盖限制见 [组合验证记录](resource-workspace-r5-r6-validation.md)。未发布、未接入个人现场，不表示完整阶段或发布验收通过。
