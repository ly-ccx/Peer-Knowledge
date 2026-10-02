# RC 账户与更新栏排版修复

2026-10-02。C级，按负责人对实际RC3底部截图的修复要求实施。代码分支 `PeerAgent/pa/rc-footer-polish`，基线 `78178d0c`。只改表达，不改变更新通道、模型偏好、权限或运行时事实。现有RC3自动发现/错误降级及复杂核验缺口另卡，不能通过改颜色掩盖。

## 截图问题与设计

1. 账户字符头像与账户名重复，更新栏被拆为松散第二层，版本提示占用过高视觉权重。负责人新截图与本轮实际RC3窗口一致。
2. 合并视觉分组：32px线条用户SVG在左，账户菜单名与次要版本/通道在右对齐。用现有tokens、字体、圆角；版本中性灰，真正更新状态使用独立小图标。复用既有更新动作与向上自定义菜单。
3. 240–360px侧栏，中英文、浅深色和available/downloading/downloaded保持可见、无重叠；菜单焦点、Escape、通道持久化和设置入口同步保持。既有经典VersionBadge不改。

## 允许改动

- `apps/desktop/renderer/src/project-agent/MeMenu.tsx`（局部metadata插槽/排版）
- `apps/desktop/renderer/src/project-agent/BotListShell.tsx`（已有VersionBadge位置）
- `apps/desktop/renderer/src/project-agent/styles/bot-list.css`
- `apps/desktop/renderer/src/ui/icons/PeerIcon.tsx`（现有图标系统中采用官方Lucide user-round路径），新增同目录 `LUCIDE-LICENSE`（来源许可）
- `apps/desktop/scripts/bot-shell-updater-checks.mjs`（实际SVG、分组与尺寸验证及前后截图）
- 本卡、RC自测/指南/证据。无新依赖、IPC、存储、能力、主进程或版本文件改动。

## 验证与交付

先保留实际缺陷截图；在已有生产装配Electron检查中验证SVG账户标记与布局、三种更新阶段/36种环境组合、既有菜单与通道动作。运行受影响桌面完整测试、build/typecheck/architecture、两平台CI，检查截图后评审合入。代码进入下一不可变候选，不改RC3 tag/资产；实际安装复验与自动发现/复杂核验修复单列，未测不写Ready。

状态：实施中。整体GA仍等待负责人全面测试、七天日用与明确批准。
