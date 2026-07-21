# peer_agent/docs 迁移清单

创建时间：2026-07-21  
最后更新：2026-07-21（已执行）  
状态：**已执行完成**  
范围：`peer_agent/docs` 逐文件分类 + 实际迁入 `peer-knowledge`、清理代码仓残留、修正 `AGENTS.md`

## 1. 结论摘要

`peer_agent/docs` 与 `peer_agent/knowledge` 已按本清单完成迁移与清理：

| 区域 | 执行后状态 |
|---|---|
| `docs/architecture/` | 本地不存在；`.gitignore` 仍忽略 `docs/architecture/*`；主干在 `peer-knowledge/knowledge/architecture/` |
| `docs/adr/` | 已删除；credential ADR 在知识库 `knowledge/decisions/` |
| `docs/design/` | 已删除；有价值 md 在 `design/product/` 或 `knowledge/specifications/`；fluid-ink 截图在 `design/visual/previews/` |
| `docs/` 根 | 目录已移除 |
| `peer_agent/knowledge/` | 目录已移除；`48-provider-model-options.md` 已迁入知识库 |
| `peer_agent/AGENTS.md` | 架构引用已指向 `peer-knowledge` |

## 2. 执行记录（2026-07-21）

### 2.1 迁入 peer-knowledge（字节校验 OK）

| 源（peer_agent） | 目标（peer-knowledge） |
|---|---|
| `docs/adr/0001-cross-platform-credential-vault.md` | `knowledge/decisions/0001-cross-platform-credential-vault.md` |
| `knowledge/decisions/48-provider-model-options.md` | `knowledge/decisions/48-provider-model-options.md` |
| `docs/design/desktop-cold-start-brand-startup-loader.md` | `design/product/desktop-cold-start-brand-startup-loader.md` |
| `docs/design/desktop-performance-ab-landing.md` | `design/product/desktop-performance-ab-landing.md` |
| `docs/design/fluid-ink-startup-research.md` | `design/product/fluid-ink-startup-research.md` |
| `docs/design/goal-mode-codex-cc-workflow.md` | `design/product/goal-mode-codex-cc-workflow.md` |
| `docs/design/hooks.md` | `knowledge/specifications/hooks.md` |
| `docs/design/message-queue-gap-vs-codex.md` | `design/product/message-queue-gap-vs-codex.md` |
| `docs/design/previews/fluid-ink-dark.png` | `design/visual/previews/fluid-ink-dark.png` |
| `docs/design/previews/fluid-ink-light.png` | `design/visual/previews/fluid-ink-light.png` |

### 2.2 从 peer_agent 删除

- 上述全部已迁 md / png
- 设计原型 HTML：`compact-reasoning-effort-slider.html`、`fluid-ink-drop-prototype.html`、logo/brand/wordmark/tui 相关预览、`update-modal-redesign-preview.html` 等
- 空目录 `docs/`、`knowledge/`

### 2.3 AGENTS.md

- 旧路径 `docs/architecture/*` → `peer-knowledge/knowledge/architecture/*`（15/16 指向 `knowledge/decisions/`）
- 只读偏好改为：知识写 `peer-knowledge`，代码仓不再重建 `docs/architecture/*`

### 2.4 核对命令结果

- `test -f peer-knowledge/.../0001-cross-platform-credential-vault.md` → 存在
- `rg peer-knowledge peer_agent/AGENTS.md` → 命中
- peer_agent 侧 `docs` / `knowledge` 已不存在；残留检查 PASS

## 3. 历史盘点方法（归档）

- 代码仓路径：`/Users/liangyin/Documents/DEV/github/peer_agent`
- 知识库路径：`/Users/liangyin/Documents/MiaoYan/peer-knowledge`
- 原检查项：`find docs`、`git ls-files docs`、知识库主题对照

## 4. 原分类表（执行前快照）

| 源路径 | 原分类 | 执行结果 |
|---|---|---|
| `docs/architecture/*` | 已完成迁走 | 保持 ignore；AGENTS 引用已修 |
| `docs/adr/0001-...` | 迁走 | 已迁 + 源删 |
| `docs/design/*.md`（6 份有价值） | 迁走 | 已迁 + 源删 |
| `docs/design/*.html` / previews | 删除（截图随 research 留档） | HTML 删除；PNG 迁 visual 后删源 |
| `knowledge/decisions/48-...` | 迁走 | 已迁 + 源删 |
| keep | 无 | 无保留项 |

## 5. 对照原则（以后避免再堆回代码仓）

| 内容类型 | 去向 |
|---|---|
| 架构、ADR、规范、经验、运维 SOP | `peer-knowledge` |
| 产品/交互结论、视觉规范 | `peer-knowledge/design/` |
| 一次性 HTML 原型、截图探索 | 默认不进 git；要留档只进知识库 visual，不进代码仓 |
| README / 贡献 / 发布说明 | 可留代码仓 |

## 6. 边界与后续（可选）

已完成：

- ✅ 迁 md + 48 号决策
- ✅ 迁 fluid-ink 截图
- ✅ 清理 peer_agent docs/knowledge
- ✅ 修 AGENTS.md
- ✅ 更新本清单状态

未做（非本目标必做）：

- 未在 `peer_agent` 提交 git commit（工作区变更仍待用户决定是否 commit）
- 未在 `peer-knowledge` 单独提交
- 未给 `peer_agent` 加“文档已迁移”短 README（目录已空，可选）
