# RC 账户与更新栏排版修复

2026-10-02。C级，按负责人对实际RC3底部截图的修复要求实施。代码分支 `PeerAgent/pa/rc-footer-polish`，基线 `78178d0c`。只改表达，不改变更新通道、模型偏好、权限或运行时事实。现有RC3自动发现/错误降级及复杂核验缺口另卡，不能通过改颜色掩盖。

## 截图问题与设计

1. 账户字符头像与账户名重复，更新栏被拆为松散第二层，版本提示占用过高视觉权重。负责人新截图与本轮实际RC3窗口一致。
2. 负责人本轮进一步明确：底部不显示“自动”或其他更新通道；更新通道仅在设置中显示。底部账户SVG与“我”居左，版本号居最右，空闲时排成一行。用现有tokens、字体、圆角；版本中性灰，真正更新状态使用独立小图标。复用既有更新动作。
3. 240–360px侧栏，中英文、浅深色和available/downloading/downloaded保持可见、无重叠；账户菜单、Escape、设置中的三种通道持久化保持。既有经典VersionBadge不改，只在机器人外壳停止传入showChannel。

## 允许改动

- `apps/desktop/renderer/src/project-agent/MeMenu.tsx`（局部metadata插槽/排版）
- `apps/desktop/renderer/src/project-agent/BotListShell.tsx`（已有VersionBadge位置）
- `apps/desktop/renderer/src/project-agent/styles/bot-list.css`
- `apps/desktop/renderer/src/ui/icons/PeerIcon.tsx`（现有图标系统中采用官方Lucide user-round路径），新增同目录 `LUCIDE-LICENSE`（来源许可）
- `apps/desktop/scripts/bot-shell-updater-checks.mjs`（实际SVG、分组与尺寸验证及前后截图）
- 本卡、RC自测/指南/证据。无新依赖、IPC、存储、能力、主进程或版本文件改动。

## 验证与交付

先保留实际缺陷截图；在已有生产装配Electron检查中验证SVG账户标记与布局、三种更新阶段/36种环境组合、既有菜单与通道动作。运行受影响桌面完整测试、build/typecheck/architecture、两平台CI，检查截图后评审合入。代码进入下一不可变候选，不改RC3 tag/资产；实际安装复验与自动发现/复杂核验修复单列，未测不写Ready。

## 本机交接

代码[PR110](https://github.com/ly-ccx/Peer-Agent/pull/110)，`9aa202ba`、tree `13a013cd73602830998b95db59348e0bd9e81d01` 已推送；最终两平台CI36991456384与评审待完成。

按负责人最新指示停止传入showChannel：底部账户与版本空闲一行，实际高度45px；账户头像保持点击菜单入口，版本组始终靠右，设置三种通道可用且持久化。72次布局检查（中英文/浅深色/240、292、360px/三更新阶段/正常与长版本）和9壳、11可访问性、7诊断检查通过，页面和授权错误0，自有进程退出。list16.24ms、search25.10ms、Received57.50ms均保持原预算。[窗口证据](evidence/rc-footer-settings-only-window-passed-20261002.json)。

开发预览采用测试Electron的版本号，不能作为实际安装版本证据：

![空闲底部](evidence/rc-footer-idle-dark-20261002.png)

![下载中窄侧栏](evidence/rc-footer-progress-dark-narrow-20261002.png)

![安装入口窄侧栏](evidence/rc-footer-install-dark-narrow-20261002.png)

`pnpm --filter @peer-agent/desktop build`、`pnpm typecheck`、`pnpm architecture:check`通过。桌面完整5302项中5296pass、1订阅计时超时、原5skip；按仓库规则独立重跑goal-plan-store文件142/142pass，另跑i18n AST 1/1pass，未新增skip或放宽条件。[本机门禁](evidence/rc-footer-local-gates-20261002.json)。初始SVG失败、旧设计一次GC通信异常、最新通道缺陷失败及误用旧dist的首轮失败保留；旧设计有界原样重跑通过，最新修改重新构建后通过。[失败历史](evidence/rc-footer-failure-history-20261002.json)。

状态：本机补修通过，CI/评审中。实际安装应用仍为RC3旧底部；新排版进入下一不可变候选。自动发现和复杂核验仍有独立阻塞，整体尚未Ready。GA仍等待负责人全面测试、七天日用与明确批准。
