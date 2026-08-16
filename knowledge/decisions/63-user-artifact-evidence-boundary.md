# 63. 用户产物与 Evidence 边界

创建时间：2026-08-16

状态：Accepted

级别：A 级（调整 Tool Result、EvidenceIndex 与 GoalTask 验收投影契约）

关联：

- `knowledge/architecture/20-architecture-governance.md`
- `knowledge/decisions/16-skill-call-lifecycle.md`
- `knowledge/decisions/62-automation-runtime-boundary.md`

## 背景

验收任务需要向用户展示代码变更、文件与截图，但 EvidenceIndex 同时包含工具调用回执、Shell stdout、`tool-result://`、`goal-plan://` 与 `goal_update_task` 包装记录。这些记录用于治理，不等于用户产物。

若 Renderer 将所有 Evidence 或 `artifactRefs` 直接展示为产物，会泄露内部 UUID、生成大量“执行证据”条目，并让用户无法判断交付了什么。若包装调用重新登记同一 EvidenceRef 并覆盖原记录，还会丢失原工具的名称和产物元数据。

## 决策

### 1. 两个概念

- **Evidence**：证明本地能力确实执行过的治理事实。可包含 Tool Result、日志、权限、时间、错误和内部检索引用。
- **UserArtifact**：用户可浏览或可定位的交付结果。P0 类型为 `code-change`、`file`、`image`。

UserArtifact 必须由 Capability Provider 的结构化 Tool Result 产生，并作为 Evidence 的受治理元数据持久化。Renderer 不从 stdout、assistant 文本、文件名字符串或任意 URI 猜测产物。

### 2. 运行链

```text
Capability Provider
  -> Tool Result { evidenceRefs, userArtifacts }
    -> EvidenceIndex（保留原工具元数据）
      -> GoalTask.evidenceRefs
        -> TaskOverview UserArtifact 投影
          -> Renderer
```

该链仍服从：

```text
Capability Provider -> Manifest -> Runtime Projection -> Tool Call -> PermissionGrant -> Evidence
```

UserArtifact 不是第二条执行路径，也不是 Renderer 附件数据库。

### 3. Provider 责任

- 文件创建或覆盖：返回 `file` 产物，包含受控绝对路径、显示名和工作区根。
- 文件编辑：返回 `code-change` 产物，指向修改文件，并可带变更摘要。
- Browser/App screenshot：返回 `image` 产物，指向持久化截图文件。
- Shell stdout/stderr/metadata：只作为 Evidence 检索材料，不是 UserArtifact。
- read/search/list 工具默认不产生 UserArtifact。

Provider 只声明自己实际生成或修改的结果，不声明用户输入附件为新产物。

### 4. EvidenceIndex 合并规则

EvidenceRef 是稳定身份。再次记录同一 EvidenceRef 时：

- 不得用空 `artifactRefs`、空 `userArtifacts` 或包装工具名覆盖已有非空值；
- 原始 capability/tool 元数据优先于 `goal_update_task` 等包装调用；
- 新增的非重复 UserArtifact 可合并；
- 冲突记录必须保持可审计，不能静默把原工具改写成包装工具。

GoalTask 只保存 EvidenceRef，不复制 Evidence 或 UserArtifact 真相。

### 5. TaskOverview 投影

TaskOverview 只展示 EvidenceIndex 中的 UserArtifact：

- `code-change` -> 代码变更；
- `file` -> 文件；
- `image` -> 截图。

以下内容不得投影为用户产物：

- `tool-result://`、`goal-plan://`；
- `local-shell-artifact://.../stdout|stderr|metadata`；
- `goal_update_task` 包装回执；
- 未知 URI 或仅有内部 UUID 的记录。

无 UserArtifact 时不渲染产物区块。产物区块默认折叠；图标必须表达文件、代码或图片，不使用类似 checkbox 的空心方框。

### 6. 进程职责

- Capability Provider：产生结构化 UserArtifact。
- Desktop runtime / EvidenceIndex：校验、持久化与合并。
- Goal store：保存任务到 EvidenceRef 的归属。
- TaskOverview aggregator：从 Evidence 投影用户产物。
- Renderer：折叠、分组、打开；不读文件系统、不猜类型。

## 失败与兼容

- 旧 Evidence 无 UserArtifact：继续可审计，但验收卡不显示伪产物。
- UserArtifact 路径不存在：保留审计元数据，界面不提供打开动作或不投影。
- 未知类型：不展示，待 Provider 契约升级。
- 合并失败：保留旧记录并返回失败 Evidence，不以 assistant 文本补偿。

## 后果

正面：

- 用户看到的是交付结果，不是内部执行日志；
- GoalTask、Evidence 与 Renderer 仍保持单一事实链；
- 包装调用不能破坏原工具产物；
- 新 Provider 可通过统一 UserArtifact 契约接入。

代价：

- 文件、编辑、截图 Provider 需要补齐结构化结果；
- 旧任务不会自动拥有历史上未记录的真实产物；
- EvidenceIndex 需要兼容合并与索引升级。

## 有界内容预览

验收卡可为 `code-change` 与 `image` UserArtifact 提供 hover 快速预览，但预览仍是 Provider 产生、EvidenceIndex 治理、TaskOverview 投影的结构化事实，不是 Renderer 对本地路径的二次读取。

```text
UserArtifact.preview =
  { kind: "code", additions, deletions, diffLines[] }
  | { kind: "image", dataUrl, width, height }
```

边界：

- 代码预览来自 `edit_file` 已生成的真实 unified diff；最多 40 行，每行最多 240 个字符。`additions` / `deletions` 基于完整 diff 统计，不含 `+++` / `---` 头行。
- 图片预览只由确认生成图片的主进程 Provider 产生；使用 Electron `nativeImage.resize()` 将最长边限制为 640px，并编码为 PNG/JPEG/WebP data URL。
- 图片 data URL 最大 512KB，只接受 `data:image/png|jpeg|webp`；超过上限则不提供 hover preview，但原始 image UserArtifact 与打开动作仍保留。
- EvidenceIndex 对 preview 做白名单规范化与同 EvidenceRef 合并；未知 preview 类型或非法字段直接丢弃。
- TaskOverview 协议显式投影 preview。Renderer 不使用 `fs`、不加载 `file://`、不从 `openPath` 或 ref 猜内容。
- hover 只用于快速验收；点击仍打开完整代码文件或原图。

## 验收

- 包装调用不会覆盖同 EvidenceRef 的原工具元数据；
- 文件写入、文件编辑和截图测试产生对应 UserArtifact；
- Shell stdout 不产生 UserArtifact；
- TaskOverview 只显示代码变更、文件和截图；
- 无真实产物时不显示产物区块；
- Renderer 默认折叠且不出现 checkbox 式图标；
- 代码 hover 展示真实增删统计与有界 diff，图片 hover 展示主进程生成的有界缩略图。
