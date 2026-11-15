# Peer Frost 实现入口与速查

创建时间：历史版本未标注
最后更新：2026-10-23

> 状态：现行规范导航。旧指南已由统一体验规范收敛，避免宋体标题、旧圆角、旧动画名与逐次测试要求继续传播。
> 适用范围：代码仓 `apps/desktop/renderer` 的 UI、样式与交互实现。

## 1. 先读什么

| 内容 | 当前入口 |
|---|---|
| 产品身份与委托链 | [产品北极星](../product/peer-product-alignment.md) |
| 视觉、组件、token、密度和可用性 | [Frost 产品体验规范](../../knowledge/specifications/peer-product-experience-standard.md) |
| 输入、焦点、滚动、授权、结果和恢复 | [人机交互契约](../../knowledge/specifications/peer-human-agent-interaction-contract.md) |
| 动画选型、编排、降级和实际治理覆盖 | [动效体系](../../knowledge/specifications/motion-system.md) |
| 开发、内容/diff 审阅与发布验收 | [开发执行规程](../../playbook/product-experience-development.md) |
| 已批准的部件关系与历史证据 | [统一设计](../product/peer-frost-unified-design.md)、[连续曲线方案](../product/peer-frost-radius-rc6-design-qa.md) |

## 2. 代码速查

- token 真源：`apps/desktop/renderer/src/styles/tokens.css`。优先已有 `--ui-*` 语义与 Frost 正名颜色/材质；现行动效接口 `--za-motion-* / --za-ease-*` 继续有效。
- 标题和正文统一 sans；mono 用于代码。`--font-serif-zh` 是兼容别名，不要求宋体。
- 常规几何：紧凑 8 px、控件/行 12 px、面板/消息/输入框/模态 16 px；使用对应 `--ui-radius-*`。连续曲率消费 `--control-corner / --surface-corner`，不支持时保留普通圆角。
- CTA 石墨；Azure 只做少量印记。状态附文字与 SVG，不能只靠颜色。焦点不得因去框而消失。
- 一层主要分组边界，内部留白/细分隔；必要的独立字段和代码/预览保留边界。普通组不自造阴影；使用既有 card/popover/drag/composer 语义。
- 外壳和临时浮层可用玻璃，长阅读面实色；不嵌套 blur、不对列表项逐个 blur，有关闭透明和不支持时的实色路径。[旧毛玻璃推演](frost-glassmorphism-spec.md)不是当前参数清单。
- SVG 复用 `ui/icons/PeerIcon.tsx`；设置组复用 `ui/settings/SettingsGroup.tsx`；通用动画复用 `styles/motion.css`；退场与焦点使用既有共享 helper。

以上为导航摘要，详细例外、可访问性和状态契约以统一规范为准；不复制另一套数值到组件。token 数值变化在代码仓集中修改，并同步相关规范中的快照，不以修改文档冒充生产落地。

## 3. 交付纪律

普通开发只做内容与 diff 审阅；不自动跑测试、build/type/architecture/IPC、截图或交互回归。用户明确要求时才提前验证，版本/RC 发布前完整执行代码仓 AGENTS 的 release gate 与产品回归。旧版每次修改必跑命令/截图的条款不再有效。

触及的旧路径逐步向共享 seam 收敛。界面不新增执行、授权、Evidence 或存储真源；需要移动这些边界时先按 A/B 级治理，不用“设计统一”扩大本次范围。
