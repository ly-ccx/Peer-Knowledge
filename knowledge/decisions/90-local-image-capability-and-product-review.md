# ADR 90：本地图片能力与安装版产品截图审查

创建时间：2026-10-10
最后更新：2026-10-10
状态：Accepted（用户确认已定位的能力断点并明确要求修复；本记录先于实现）
级别：A（能力暴露、图片上下文与 Evidence 边界），B（工具结果与执行连续性）
依赖：ADR 80、83、85、88、89；工程治理与产品北极星

## 1. 问题与目标

安装版 RC10 的任务能够生成产品回归包，但普通 `read_file` 将 PNG 当 UTF-8 文本返回。工具结果的视觉侧带仅接浏览器与受管桌面截图。受管 Desktop 预览 Provider 仅在开发宿主启用，独立预览审查依赖这个 Provider，不能替代安装版中读取已有本地截图的能力。执行者随后报告缺少看图能力并进入等待用户；语义验证只能指出缺少逐图审查和 verify 结果。

目标：主 Bot、执行 Agent、只读 Explorer/Verifier 都能在已授权范围内实际读取本地图片，并将像素交给视觉模型。产品回归的执行者可以审查自己的全部截图，写真实观察并重跑 verify；独立验证者可重新读取同一批截图。用户无需把本机已有截图重复上传。

本决策不以文件名、路径、二进制文本、computed-style 或模型口头声明替代看图事实。`supportsVision` 是配置能力声明，实连验收仍需证据。

## 2. Module 与接口

- `LocalImageProvider`：runtime-node 中的深 Module。Interface 为 `local.image.read`、结构化 path 参数、授权、大小/类型/像素上界、取消/拒绝/失败语义及只含元数据的 Evidence。Implementation 集中在有界文件读取、真实路径检查、格式识别、哈希与视觉侧带构造。
- 图片解码是可注入 Seam；Desktop Adapter 使用 Electron nativeImage 验证 PNG/JPEG；GIF/WebP 使用隔离、不可见、无 Node 权限的 Chromium bitmap decoder。后者只接已授权、有界的图片字节，不接文件路径或模型脚本，不访问网络；超时/取消后销毁。无 decoder 时明确失败，不伪造可读图片。
- `view_image` Tool Definition 与 Manifest 声明 read-only，Runtime Projection 在 chat/plan/goal/explorer/project_agent 允许。后台任务不依赖可见浏览器；安装版也装配该 Provider。
- Protocol 定义本地图片元数据与视觉观察。视觉侧带只在宿主当前回合存活；由 Provider 签发对象身份绑定工具调用，任意工具文本、复制对象或模型参数不能伪造已授权图片。

## 3. 唯一执行链

```text
view_image(path)
 → Runtime Projection: local.image.read
 → Provider: resolve real path / regular file / bounded read
 → PermissionGrant: canonical path + workspace + action + image transfer
 → decode / size and pixel bounds / SHA-256
 → Evidence: path, media type, dimensions, byte count, content hash, artifact ref
 → ephemeral visual observation
 → existing Provider encoder: image content
 → model judgment
```

图片内容始终是事实/user context，不进入 system prompt。新工具规则来自 Tool Definition；无需散落拼接提示词。不得新增 renderer 文件读写、私有模型发送通道或绕过权限的自动上传。

## 4. 权限、边界与资源

- 沿用宿主 permission gate 的本地读取策略。请求明确是读取图片并用于当前模型；无审批者且当前策略需要确认时拒绝，不挂起独立验证者。
- 路径经真实路径解析；符号链接不能冒充 workspace 内文件。授权绑定真实文件路径；读取使用同一文件句柄，前后复核身份与修改时间，修改时失败并可重新读取。
- 仅支持可被 Desktop decoder 实际解码的 PNG/JPEG/GIF/WebP；不执行 SVG、HTML 或任意二进制。默认每图最多 8 MiB、最多 24M 像素；不把多张图片无限塞入一个结果。Agent 分批逐图处理。
- 取消、拒绝、文件缺失、图片损坏、资源超限、类型不支持分别返回结构化失败和 Evidence。失败不返回像素。
- 图片不能授予修改文件权限；objective probe 等受限 profile 继续由执行闸门决定能力准入。

## 5. Evidence、存储与恢复

- 不新增图片副本持久化。图片来源文件保持原位；Evidence 只保存元数据和可重读线索，artifact ref 包含内容哈希。模型图像字节不进入 Tool Result output、UI 工具卡、证据索引或系统快照。
- 本地图片结果的 `modelContext` 和工具编排结果的 `visualObservations` 为不可枚举的宿主侧带；JSON、structuredClone 和事件存储不能带走像素。Runtime SDK 在附加 Hook Evidence 后保留不可枚举侧带的对象身份，避免正常 Hook 令图片消失。消费端仍检查 Provider 签发身份。
- 工具后的图像通过现有视觉侧带进入下一次 Provider 请求；OpenAI Chat/Responses、Anthropic、Gemini、Qoder 共用投递规则。
- 持久执行检查点保留来源路径、哈希与“需要重新读取图片”的明确说明，撤去本地图片像素。恢复后的 Agent 通过真实 `view_image` 再次读取、再次授权，不能从摘要恢复虚假的看图事实。
- 图片工具在内部 Runtime 元数据声明 `resultReplay=fresh_read`；幂等决策接收 `requiresFreshResult`，仅对只读工具重新执行，不复用只有 Evidence refs 的已完成结果。默认工具策略不变，模型不能提交或覆盖这一宿主事实。
- 视觉工具结果不等于模型已经给出验收结论，更不等于用户签收。

## 6. 产品审查与任务闭环

本地回归包和受管预览是两个现有来源。安装版通过 `view_image` 审查已有包；开发宿主仍可使用受管预览及其独立宿主审查。不能直接移除 `isPackaged` 限制来把开发构建/启动能力暴露到正式宿主。

任务继续沿用 capture → 实际逐图读取 → 具体 review.json → verify 的产品协议。执行者如实标记自审；独立验证者重新读取图片和报告，不把自审叫独立。既有工作会话的 Verifier 使用相同只读图片工具。工具入口缺失造成的基础设施问题，不应默认要求用户上传截图；失败回执需明确事实和可重试动作。

无需自动签收、绕过完成门或修改用户存储中的停住任务。旧任务在新版恢复后沿现有 continuation 接着审查已有产物；用户的真实权限决策、暂停与取消仍然有效。

## 7. read_file 兼容

普通文本读取保持既有行为。检测到受支持图片字节时返回结构化 `image_requires_view_image` 和重读提示，避免将二进制乱码送进文本上下文。不能把一次普通文件授权偷偷扩张成图像发送授权。

## 8. 验收矩阵

1. 安装版模式也投影 view_image；后台 work_session 与只读 verifier 可用；开发 Desktop preview 仍按原边界限制。
2. 实际 PNG 文件经 Manifest → Projection → Provider → PermissionGrant → Evidence → 下一次模型请求变为图片内容块；路径或乱码不算通过。
3. PNG/JPEG/GIF/WebP 可解码、缺失/损坏/错误类型/过大/像素过大、符号链接越界、批准/拒绝/无审批者、取消及读中修改。
4. 不能由伪造工具结果或拷贝观察对象绕过图片准入；输出、Evidence、检查点不保存 base64。
5. 各 Provider wire 保留图片和配对工具结果；检查点恢复后明确重新读取，不能漏掉来源。
6. 合成产品包多图逐张实际投递，写具体观察，verify 成功；缺图或哈希变化失败。模型使用受控适配器时如实声明，不称为真实服务验证。
7. 全局类型检查、架构检查、受影响包完整测试。安装候选用隔离用户数据验证，不覆写日常应用或个人数据；不自动发布 RC。

## 9. 回滚

移除新工具投影与 Provider 可回滚能力暴露，既有文件/附件/预览不需迁移。保留 `read_file` 的图片拒绝回执可避免再次输出乱码。缺少视觉入口时报告基础设施事实，不伪填 review，不宣布产品验收通过。

## 10. 实施与验证记录（2026-10-10）

实现位于代码分支 `codex/local-image-vision`，以 `codex/independent-agent-delegation` 为依赖。没有改 Renderer、日常用户数据、版本号或开发预览限制。Provider、Protocol、默认 Runtime Projection、只读任务策略、四类模型编码、持久检查点、幂等恢复及 Runtime SDK Hook 侧带均已接通。

- 受影响包完整测试：Protocol、runtime-core、runtime-sdk、runtime-node、Desktop 合计 7,037 项通过，5 项环境跳过，无失败或取消。最后路径兼容和文本读取前缀修正另跑 19 项聚焦测试，全部通过。
- 完整构建、全局 typecheck、architecture:check 和 SVG/圆角约定检查通过。
- `apps/desktop/scripts/local-image-runtime-smoke.mjs` 在真实 Electron 中运行：实际解码 PNG/JPEG/GIF/WebP；两张颜色不同的图片通过工具链进入下一次 HTTP 模型请求；经文件工具写审查记录；合成回归包 verify 通过，缺图/哈希变化被拒绝；已完成图片工具重新执行并重新返回像素；Evidence、事件序列化及检查点不持久化图片字节。
- macOS arm64 隔离打包候选的原始主入口启动通过。另在候选的独立副本中替换测试入口，使用同一打包模块运行上述图片闭环；该覆盖称为“打包模块受控入口验证”，不冒称日常安装版的真实用户会话已完成。

验证由实施者完成，非独立审查。HTTP 模型服务为受控测试适配器，未实连云端真实模型；合成图片包用于链路验收，不替代产品设计的逐图 AI 审查。未发布 RC，也未替换日常安装版。旧任务继续沿原有权限和 continuation 恢复，未手工修改其完成或签收状态。

## 11. 范围外图片授权补齐（2026-10-11）

RC12 现场暴露的普通问答与正式图片批准断点，按 [ADR 92](92-scoped-permission-inheritance.md) 修复：范围外读图进入正式授权卡，具体图片许可可沿同一 Bot 的宿主委派链继承，并在重启后回读。旧聊天中的同意不自动迁移；文本读取许可不扩成图像发送许可。取消、撤回、过期、文件变化与存储失败均不能返回像素。详细审计矩阵及本轮验收记录见 ADR 92。
