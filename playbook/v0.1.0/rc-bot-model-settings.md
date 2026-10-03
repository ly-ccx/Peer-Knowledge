# RC 机器人模型设置入口

2026-10-03，Accepted。负责人要求在机器人档案设置里配置 Bot 模型，沿既有自主修复、自测与合入授权执行。

## 范围与现状

C级：已有 BotProfile.modelPolicy、主进程模型列表投影、update-profile 校验和持久化均保留；只调整设置的表达与入口。当前“模型分工”排在外观和工作方式下面，主角色叫“项目代理”，不容易发现它控制机器人的对话模型。ADR83 的项目策略优先级、能力/范围约束以及任务创建时冻结模型均不变。

代码分支 `PeerAgent/pa/rc-bot-model-settings`，基于 `PeerAgent/dev/0.1.0`。

## 允许改动

- `apps/desktop/renderer/src/project-agent/drawer/BotSettingsTab.tsx`：机器人模型移到设置首屏、外观之前，复用既有保存入口。
- `apps/desktop/renderer/src/project-agent/drawer/BotPolicyFields.tsx`：明确“机器人模型”与“对话模型”，保留任务执行、复核及更多角色/范围的既有控件。
- `packages/i18n/src/index.ts`：对应中英文标题与生效时机说明，不改变全局角色术语。
- `apps/desktop/scripts/bot-shell-electron-smoke.mjs`：在隔离临时数据中经生产配置存储建立两项合成模型，不写真实密钥、不请求模型网络。
- `apps/desktop/scripts/bot-shell-accessibility-checks.mjs`：实际原生设置页选择模型、重新打开读回、切换与恢复继承；证明其他角色、其他机器人和全局配置不变，保留原有可访问性、性能与主题检查。
- 本卡及 `playbook/v0.1.0/evidence/rc-bot-model-*`：保存本机/CI证据与截图。

不新增 IPC、协议、能力、依赖、存储路径；不修改 runtime、main.mjs、发布版本和标签。若发现实际边界需移动，单独评估。

## 验证与退出条件

先构建；运行既有 desktop-integration 模型策略契约与中英文检查，Desktop/i18n完整测试、typecheck、architecture、AST检查；原生隔离 Electron 加 `--accessibility --diagnostics` 检查持久化/隔离与深浅色、窄窗口截图。两平台最终提交 CI 通过，按已有授权合入、同步主工作区。源码验收与安装版/真实模型证明分开报告；整体 RC Ready 不由本 UI 卡认证。
