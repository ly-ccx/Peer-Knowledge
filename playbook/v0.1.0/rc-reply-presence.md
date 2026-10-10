# RC 回复边界与活动文案

创建时间：2026-10-10
最后更新：2026-10-10

## 卡片

用户 2026-10-10 指出：“查看详情”应对齐当前消息气泡右边，运行提示应体现真实阅读、执行或思考进展。分类 C：仅将既有 Activity 的公开事实投影到 Renderer；不改变工具、IPC、Context、PermissionGrant、Evidence 或存储。

代码基线 `013a0a17`（RC10），分支 `PeerAgent/pa/rc-reply-presence`。既有取消专项 PR136 独立待审，本卡不混入它。

## 实施范围

- 回复脚注跟随最后一个可见气泡的实际边界，覆盖流式公开段落、正式回复、窗口和侧栏重排；未出现气泡时仍与输入框对齐。悬停或键盘焦点显示详情，点击仍打开回复侧栏。
- 使用 Activity 的 phase、工具状态和已有脱敏展示摘要；执行前写“准备”，执行中写“正在”，结束不继续宣称执行。已完成工具不冒充当前活动。
- 文件名仅显示有界末段，不公开完整本机路径；命令使用泛称，不披露参数。没有具体活动时显示简短自然文案，不轮播虚构动作，不展示隐含推理。
- 定向状态测试、Electron 的真实流阶段及边界断言、深浅色和窄窗截图。减少动态效果与键盘入口保留。

## 验收与限制

按 product-regression 全套 capture、逐图 AI 自审和 verify；自审不称独立。窗口使用受控模型，经已有宿主事件和 IPC 到 Renderer，不能代表真实模型、已安装版本或完整屏幕阅读器覆盖。最终记录见下。


## 交付与验证

- [PR137](https://github.com/ly-ccx/Peer-Agent/pull/137)，最终代码提交 `0c783b28a8ce99d081f3b004762a3e19c154706d`，已推送。仅本卡范围；PR136 取消专项未混入，当前未合并、未发布 RC。
- 构建、类型检查、架构检查通过；状态、翻译、产品门禁与流控制定向测试 13 项通过。本地全套测试在首个实现提交 `af117a1c` 通过；后续补齐停止/失败消息边界及截图检查，最终提交的全套测试由双平台 CI 验证。
- [最终提交 CI](https://github.com/ly-ccx/Peer-Agent/actions/runs/38021407626)：macOS 14 与 Ubuntu 均通过构建、类型检查、架构检查、全套测试和 Electron 交互检查。
- 完整产品 capture / AI 逐图自审 / verify 通过。最终包 runId `a507ca80-b9dc-4a8c-8b46-882f36271c10`，sourceFingerprint `b5b7410ac4dc599c643b3627d6180947db4c7bf69cdf1caec71e3cc66ce33256`，116 张必需截图均已检查，**实施者自审，independent=false**。
- 10 个几何状态覆盖首段、最后公开段落深浅色、准备读取、读取与侧栏停靠、完成、停止、失败、短问题深浅色。全部实际气泡边界与详情按钮右边相等，最大误差 0 px，均与整列右边保持区分。
- 实际 Activity 准备 / 执行检查得到“准备阅读 README.md”→“正在阅读 README.md”；公开段落显示“正在整理回复”，完成后不留运行文案，循环高光已移除。
- 鼠标悬停单独验证隐藏→显示，键盘进入及返回焦点也通过。为稳定静态截图，两个 `reply-entry-hover-*` 文件在鼠标断言后以焦点保持入口；**不是纯鼠标悬停截图**，截图不能单独证明动画。
- 逐图审查曾发现失败/停止消息位于 `.bot-cards` 内，入口仍对齐整列；已补齐实际消息边界并重跑。早期截图和未通过的 capture 不作为最终验收。

## 产品证据

- [完整逐图自审记录](evidence/rc-reply-presence-product-review-20261010.json)
- [绑定提交、产品包和 CI 的验证事实](evidence/rc-reply-presence-validated-20261010.json)
- [首段进展与气泡边界](evidence/rc-reply-presence-progress-dark-20261010.png)
- [实际读取文件与按需展开参数](evidence/rc-reply-presence-reading-dark-20261010.png)
- [浅色短消息边界与键盘焦点](evidence/rc-reply-presence-short-light-20261010.png)

## 覆盖限制与架构影响

- 受控模型场景与源码 Electron；未验证真实模型质量或网络时序、已安装 RC、完整屏幕阅读器和长期使用。
- 透明快捷窗口 PNG 无法证明 OS 合成后的浅色对比度；现有主聊天问题区焦点边框局部贴近圆角，本次详情入口焦点边框完整。这些既有现象没有被本卡称为已修复。
- C 级 UI 表达改动，没有改变 Runtime、Protocol、IPC、System Context、PermissionGrant、Evidence 或存储边界。技术参数仍在已有详情栏按需查看；活动文案来源于公开结构化状态，不随机轮播虚构行为，也不公开隐含推理。
