# R5 / R5a / R6 当前组合验证

日期：2026-10-26
状态：定向组合验证通过；实现者截图自审，非独立审查。未提交、未发布、未接入个人测试实例；不表示完整第二阶段或发布验收通过。

## 对象与结果

用户明确要求“补跑组合验证”。验证对象为代码隔离工作区当前的 R5-01/02/03、R5a、R6 组合源码，包括未提交改动；不是旧 PR HEAD 或此前 R5-01 的结果。

- Node 25.9.0 / pnpm 10.22.0。Desktop 及运行时依赖构建、Desktop 类型检查、IPC 目录核对、架构治理及 UI 圆角/SVG 约束检查通过。
- 组合模块入口覆盖 59 个文件，338 项测试全部通过：0 失败、0 取消、0 跳过。覆盖原第一阶段资源链、历史 blob/范围校验、版本观察与文档读位、目录/网页恢复、领域详情和静态呈现等路径。
- 生产 Electron main/preload/renderer 使用临时 Bot、文件、Git 仓库、Chromium profile 和 loopback 网页；不替换文件 IPC，不访问用户任务，不调用真实模型。R5 原入口明暗各 6 组、后续组合入口明暗各 9 组，共 30 组真实联调断言通过；每个实例按登记身份退出，pageErrors 均为空。
- 最终 31 张图片逐张实现者自审（R5：11 张；后续组合：20 张）。检查同屏纸面、局部版本/失败反馈、正文/源码、历史来源、未保存字段、目录读位、图片与 Diff、网页恢复提示；窄窗检查限于 R5 的 760px 场景。机器断言与逐图说明分别保留，不用截图数量代替全量产品验收。

源码文件指纹：`c4b8d4f22efbe400516d043f7d034a1a3effabb22ae8cfc17cff3435b921a038`。
运行路径文件指纹：`edf7ef3a169c66403b091e4b84a3db0f4b7443cfc8759692e9f3a7063e1e7e6b`。

[可移植回执、脚本/日志/截图哈希与逐图说明](v0.1.0/evidence/resource-workspace-r5-r6-validation-20261026.json)。原始日志、截图和完整机器记录保留在仓库外验证包；不在知识库写个人机器路径。

## 本轮发现与处理

1. **实际构建问题**：新 `DiffLines.tsx` 与既有 `diffLines.ts` 在 macOS 上解析冲突，组件 import 被指向纯解析模块。组件改名为 `DiffRows.tsx`，相应 import 与测试替身同步；修复后重新构建与类型检查通过。没有改解析/权限语义。
2. **验证顺序问题**：最初类型检查与协议构建同时启动，读取了旧 dist，报告缺 revision 类型。运行时依赖构建后顺序重跑，最终类型检查通过；不把首次失败当既有基线。
3. **测试目标问题**：目录读位 hook 的 VM 测试默认按旧 JS 目标编译，Set 展开被转为空数组。测试目标改为与应用一致的 ES2022，保留真实展开分支断言；组合 338 项重新执行通过，未为通过测试删减行为。
4. **重启测试替身问题**：新联调脚本首次在重启后沿用旧 Page 的目录 Locator，误报 target closed。Locator 改为从当前 Page 获取。另脚本退出前必须等待真实地址元数据已落盘，不能把尚在 250ms debounce 窗口中的强制结束当作已保存地址恢复。修正后明暗重跑整个新组合入口，通过。
5. **截图 fixture 问题**：初版 loopback 页缺 UTF-8 声明导致中文乱码，单像素 PNG 也无法审查实际图片区域。修正为明确 charset 的网页和真实 CRC/deflate 的 160×96 PNG，重新 capture 最终图片；早期图片不用于最终通过。

本轮实际应用源码修复只有 Diff 呈现组件命名/导入；其余是可重复验证入口、测试替身与证据整理。没有修改主进程权限/执行协议、任务调度、原文件写入或用户配置。

## 真实联调覆盖

| 包 | 实际证明 |
| --- | --- |
| R5-01 | 宿主按真实字节生成版本；条件读取；变化时保留旧正文与原 DOM/读位；显式采用新版；失败保旧与重试；范围/跨 Bot 拒绝；完整进程重启后正文 320px / 源码 650px 独立恢复 |
| R5-02 | 真 Git blob 与完整提交回执；历史正文和当前正文分标签；嵌套相对链接沿同一提交；显式当前文件入口；历史缺失失败而不换 live |
| R5-03 | 已核目录分支、选择和 440px 位置跨完整进程恢复；切资源时真实 guest 身份与表单保留；完整重启只按已保存 URL 重开并提示限制；真实 guest crash 局部失败、显式重试恢复 |
| R5a | 同一侧栏承载 Bot 设置与资源；返回原设置保留同一个 input DOM、未保存名字与主 Composer 草稿；没有文档覆盖模态；任务/证据路径的领域边界由组合模块及宿主测试覆盖 |
| R6 | 本地 HTML/SVG 无 iframe/执行/隐式资源请求；静态 Markdown 外部图片为显式动作；50,001 行文本限制到 4,000 行并标总数；真实 PNG 解码/缩放/重置；截断 PNG 局部解码失败与重试；真实 Git hunk 与模式元数据退原文 |

## 覆盖限制与剩余验收

- 本轮不是全仓测试、完整 qa:product:capture/verify、安装包验证或发布候选冻结；不声称 CI 或所有第二阶段场景通过。没有独立审查。
- 未调用真实模型，未运行个人任务或真实用户成果写入。任务/Evidence 端到端完整交互、子会话网页前台接续、独立窗口和跨设备仍不在本次 UI 包范围。
- 未覆盖完整 IME/读屏/reduced-motion/键盘矩阵、逐帧动效或所有缩窗组合。密集标签及返回文字在窄栏中省略，完整 title/可访问名称仍保留；辅助导航进一步改善属于 R6a。
- 图片真实 codec 联调覆盖 PNG；其他准入格式目前是头部/限额模块测试。PDF/Office、ICO/AVIF 没有在本轮增加正文/图片 Adapter。
- Browser 重启验证的是**已落盘导航**；不证明在待持久化 debounce 窗口内强制结束进程仍能保留最新地址，也不保证恢复网页表单/页内历史。
- 原日常代码工作区 3098 个路径与知识工作区 1247 个路径的 hash/暂存区、原 Vite/Electron 实例继续复核保全。未同步/重启个人现场，不重跑已完成写入。

## 复现

从代码仓依次运行（截图输出为自动创建的仓库外临时目录）：

```sh
pnpm --filter @peer-agent/desktop build
pnpm --filter @peer-agent/desktop typecheck
pnpm architecture:check
node apps/desktop/scripts/resource-workspace-tests.mjs
node apps/desktop/scripts/resource-workspace-r5-smoke.mjs --dark
node apps/desktop/scripts/resource-workspace-r5-smoke.mjs
node apps/desktop/scripts/resource-workspace-r5-r6-smoke.mjs --dark
node apps/desktop/scripts/resource-workspace-r5-r6-smoke.mjs
```

每次须重新审阅实际图片与回执；改变源码或脚本后不能只改旧回执的绑定。
