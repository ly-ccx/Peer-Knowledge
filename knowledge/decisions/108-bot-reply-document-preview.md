# 108. Bot 回复文件引用的有界只读预览

创建时间：2026-10-24
最后更新：2026-10-25
状态：Accepted（本轮用户授权，本地试用；不是发布验收）
级别：A，扩展既有 UI 文件读取契约的可选引用形态，明确资源边界。

## 目标与事实来源

用户点击 Bot 回复的文件引用，在应用内查看真实文件；Markdown 默认正文，可切换只读源码。存在性和内容由宿主读取决定，模型写出的路径不是产物存在、执行成功、权限或 Evidence。文档内容仅为只读用户资源，不进入 System Context，不自动执行 HTML/脚本、调用工具或获得模型读取权限。

## 现有链路与边界

复用 typed readFile / file:read / FileAccessApplicationService 和既有文本大小、二进制检查。追加可选 BotDocumentReference（workspaceId、path、可选 relativeTo），由宿主使用 Bot directory/registry 绑定真实项目根；不接受 renderer 提供新授权根，不新增 IPC channel、模型工具、Grant、权限存储、Capability Provider 或文件执行路径。现有普通工作台 readFile 调用保持兼容；Bot 引用分支在既有读取前增加严格资源核对。

允许当前 Bot 项目、用户已登记的工作区，以及该项目已经确认的 companion knowledge 根；renderer 不能凭引用新增根或工作区。知识库按既有 PEER_KNOWLEDGE_ROOT、本地 gitignored .peer-workspace.local.json、项目同级 Peer-Knowledge/peer-knowledge、已登记多根工作区的顺序解析；显式配置无效必须报错，不悄悄切换。必须核对 Git origin 是 ly-ccx/Peer-Knowledge（HTTPS/SSH 同一身份）；不枚举磁盘、不注册新工作区、不写设置。多个同级候选不唯一时明确歧义，不猜一个。

绝对路径必须属于上述根；相对路径只按当前 Bot 根/明确的预览来源文件解析，Peer-Knowledge 前缀只映射已确认 companion 根。先做词法边界判断，再 realpath 核对根/目标，阻止 ../ 与符号链接越界；不因模型提供的路径扩权。relativeTo 亦须是上述范围内的真实文件。权限不足、缺失、目录、过大、二进制、未知项目、歧义或根不可用都返回结构化状态，内容为空；不提升权限、不创建/写入文件、不把 OS 错误冒充成功。

## 展示与恢复

Bot 对话使用独立的文档预览 Context，将路径候选接成可键盘访问的按钮/链接；只在用户点击后读取，不在渲染普通路径时自动探测。复用 Drawer/Overlay 的归焦、Escape、动效和静态降级，复用既有 MarkdownDocument / SourceViewer，不挂整套工作台或执行/编辑功能。打开失败在同一预览中说明原因并提供重试；快速切换/关闭废弃迟到结果，Bot 切换重置临时预览，不抢对话草稿、滚动或默认打开文件。Markdown 内文件链接沿同一范围重新校验，网页链接仍沿现有外链策略。

2026-10-25 过渡补充（C 级）：预览消费既有 slide-inline 基元，使用大抽屉的 slow 入场与 medium 退场，沿既有位移上限与 RTL。共享 useMotionSettled 解除监听时不再取消 CSS 所有的入场，避免开发 StrictMode effect 重跑跳过动画；完成、偏好变化、后台或降级仍用 visualMotion 收尾。读取/刷新与内部路径切换不重播入场，不增加组件定时器，关闭沿 Overlay 的退场、静态终态与归焦。

## 验证范围

已补宿主边界、缺失/权限/软链接/跨库/歧义、路径解析以及动画观察器重跑/减少动效用例；迟到读取复用既有资源取消逻辑。日常只做内容/diff 审阅，按当前用户 Validation Scope 不运行测试、构建检查或截图/交互回归。必要的 preload 运行产物与实验室重载属于本地交付，不是发布验收；完整门禁继续发布 E13。本轮按用户授权提交并推送至现有 PR，不发布新版本；其他本地改动保留。
