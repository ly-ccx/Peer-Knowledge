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

## 本机实施与验收

[PR116](https://github.com/ly-ccx/Peer-Agent/pull/116)，干净最终源提交 `87d2945cc2f93f77c198966c3dff16417f34da41`，5个允许代码路径。设置首先显示“机器人模型”，三个常用角色为对话模型、任务执行和复核。仍能选择既有档位或已配置模型，并恢复跟随全局；更多角色及范围保持折叠。说明区分后续回复与新任务，不宣称正在执行的任务即时换模型。

构建、typecheck、architecture通过；Desktop5320项中5315pass、原5skip、0fail/0cancel；独立中英文契约1项，定向desktop-integration/i18n/AST35项通过。[本机门禁](evidence/rc-bot-model-local-gates-20261003.json)。

最终实际原生窗口9壳/12可访问性/7诊断/5回复检查、72更新布局及36回执通过；0页面/主进程授权错误，自有进程已退出。新增检查经生产配置存储在临时数据中建立两项无密钥合成模型，沿实际目录投影、设置DOM和IPC验证固定选择、重新打开保留、切换及继承恢复；另一Bot、全局模型/路由和任务执行/复核角色均不被对话选择覆盖。列表/搜索/Received中位15.274/26.6/54.3ms，原100/150/300ms预算不变。[最终源码窗口报告](evidence/rc-bot-model-source-passed-20261003.json)。这不是安装版或真实模型请求证明。

首轮原生断言同样通过，但“light”截图当时未实际切换浅色，末尾截图又受键盘焦点滚动影响遮到标题。仅修正检查器在真实主题端点和滚动归零后取图，产品CSS不变；[首轮报告保留](evidence/rc-bot-model-source-first-passed-20261003.json)。复查实际截图：[深色首屏](evidence/rc-bot-model-dark-20261003.png)、[浅色首屏](evidence/rc-bot-model-light-20261003.png)、[配置模型菜单](evidence/rc-bot-model-picker-20261003.png)、[窄抽屉下部与固定页签](evidence/rc-bot-model-narrow-20261003.png)。

两平台最终CI37134027413进行中。实际签名RC4尚未更换，不声明新候选或整体Ready。
