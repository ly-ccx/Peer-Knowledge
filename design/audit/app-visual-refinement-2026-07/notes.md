# App 视觉精致度审计 Notes

> 创建时间：2026-07-06  
> 最后更新：2026-07-06  
> 完整文档：`../../product/app-visual-refinement-audit.md`

## 截图步骤

1. `01-file-tree-overall.png`  
   三栏主界面和 Workbench 文件树。健康度：中等。结构接近任务型桌面产品，但旧 terminal 占位入口、文件树、Composer、消息卡之间视觉语言不一致。

2. `02-unrendered-document.png`  
   旧文件内容源码视图。健康度：偏弱。Markdown 未渲染，像调试器，不像文档阅读面。

3. `03-rendered-document-reference.png`  
   文档渲染参考状态。健康度：较好。文档阅读 + 文件树定位形成明确工作区，但需要和 App 字号/密度系统合并。

4. `04-code-preview-reference.png`  
   源码预览参考状态。健康度：较好。代码区和文件树关系明确，是 Workbench 应该靠近的质量线。

## 主要结论

- 问题不是某个按钮丑，而是产品气质没有收敛。
- 当前同时混有 Codex-like、Electron 工具、后台管理台、历史 Vellum/Frost 四套视觉语言。
- 优先做 token、Workbench、Sidebar、Chat Surface 四个 slice。
- 用户主题色应该只影响 accent / selected / focus / link，不应该染大面积背景或 CTA。

## 证据限制

- 截图无法验证键盘焦点、屏幕阅读器、动态交互、滚动性能。
- `01-file-tree-overall.png` 中的 terminal 占位入口已在后续代码中移除。
