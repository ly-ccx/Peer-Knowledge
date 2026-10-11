# ADR 92：具体资源授权与执行链继承

创建时间：2026-10-11
状态：Accepted（用户明确要求补齐图片授权，并全局检查权限继承；先记录决策再实现）
级别：A（权限、协议、批准记录），B（Desktop/TUI 执行与恢复），C（授权入口文案）
依赖：ADR 85、88、89、90、91

## 1. 已确认的断点

RC12 的主 Bot 在用户通过普通问题选项表示同意后，读取五张项目外截图仍得到 `image_outside_read_scope`。图片 Provider 在正式 PermissionGrant 请求前硬拒绝 project_agent；普通问题答复本身没有形成宿主授权。不能据此把聊天文本当通行证。

全局审计还发现：Desktop 同一 toolCallId 的批准复用不绑定参数或能力；“允许一次”会被记为同类文件写/Shell 许可；TUI 会话许可仅绑定能力和工作区，未绑定参数；授权条的“一直允许”会批准所有待处理请求。现有一次性恢复批准虽绑定摘要和 session，workspace 未进入索引键；恢复审批检查又排在无审批者拒绝之后。

## 2. 决策与 Module

新增共享 `PermissionInheritance` Module，集中计算授权身份、具体操作摘要、资源批准、有效期与撤回。Desktop/TUI 负责提供宿主身份与现有 ApprovalStore，不能从模型参数取得父会话身份。主 Bot 协调权仍不是权限签发权。

本次资源继承限定为 `local.image.read` 的单一真实图片文件。许可绑定 workspaceId、机器人父会话、真实路径、文件身份（设备、inode、大小、mtime、ctime）、`read_image_for_model` 动作与 30 分钟有效期。无 workspace 身份的普通会话只能在自身会话内复用。委派执行者须从 GoalPlan 的 delegationOrigin 回读 workspace/session/父会话，并检查当前计划没有取消、暂停或被取代；核验者和恢复执行者走同一判断。独立任务不能从另一机器人会话继承。许可不扩大 readableRoots，也不授权目录、其他文件、文本读取、Shell、写入、浏览器、MCP 或密钥。

Provider 在范围外图片读取时进入既有结构化权限入口。项目代理仍限制为只读图片；global full/session 设置不能偷偷批准项目外读图。无人工审批者时先检查有效宿主许可，未命中立即结构化拒绝；不能等待不存在的确认窗口。图片读取前后仍检查真实文件身份、取消和大小/解码上限。

## 3. 用户决定与复用

- “允许”只批准当前操作；后续同类写入或命令不因这次批准获得许可。
- 明确选择本轮图片许可后，宿主记住该具体图片，直属执行者/核验者可在有效期内再次实际读取。入口明确图片会交给当前模型，范围为当前机器人及其任务。旧普通问题答复不迁移成 PermissionGrant。
- “一直允许”只作用于当前展示的请求。自动合并只允许同一宿主身份、相同具体操作；不能批量批准不可见的其他请求。
- 通用 scope/session 批准绑定 capability、参数摘要、conversation/session、workspace；命令程序名称或文件写能力名称不足以复用。
- 同一 toolCallId 的恢复桥还需相同能力、参数、工作区、会话和有效期，最多复用一次。Goal 高风险确认只有宿主明确标注的实际目标能力可复用，不能任意跨能力。
- 下调或更改访问策略清除既有内存批准，并撤回当前宿主记住的图片批准；当前策略、取消、租约与只读闸仍在每次执行时重检。

## 4. 持久化与 Evidence

沿用已登记的 projectRuntime `approvals.jsonl`，扩展可选 `imageReadGrant` Protocol 字段；不新增授权文件、图片副本或 renderer 真值。仅本地用户明确 scope/session 决定可签发可继承图片批准。批准记录保留原 toolCall、主体、范围、有效期与 local_ui 来源。压缩保留未过期的有效图片批准；撤回追加 expired 状态。重启从最新状态回读，不把历史 audit-only 批准推断为资源许可。

存储失败不签发可继承许可。过期、撤回、文件变化、任务停止和主体不符不继承。工具结果保留真实 PermissionGrant 的 grantId 与结构化范围，Evidence 仍沿原工具链生成；像素只进入宿主视觉侧带。用户/Agent 普通文本和报告不参与授权判定。

## 5. 验收

先用聚焦回归复现：范围外主 Bot 图片请求被硬拒绝、批准一次被扩大、同编号不同参数/能力误放行、TUI 同能力不同操作误放行；修复后全部红转绿。

验证图片批准→主 Bot→子执行者→Verifier→重启恢复的真实 Provider 像素链；另一 workspace/父会话、不同文件、变更文件、取消任务、无审批者、过期、撤回及存储失败拒绝。验证主 Bot/只读 Verifier 写闸、objective probe 与自动化政策不被继承覆盖。运行受影响包完整测试、build/typecheck/architecture；授权入口变更执行产品截图逐图自审及 verify。

明确真实模型、日常安装版、独立审查覆盖边界。此次不改旧任务完成事实，不发布 RC，不替换日常安装版。回滚时旧 ApprovalStore 读者忽略新可选字段；新版不为旧记录补造资源许可。

## 6. 全局审计与实现落点

| 路径 | 原问题 / 核对结果 | 本次处理 |
| --- | --- | --- |
| Desktop 图片 Provider / 项目代理闸 | 范围外图片在人工授权前硬拒绝；带 workspacePath 的图片请求还可能被派到文本文件授权 | 改走 local.image.read 的正式 PermissionGrant，具体文件身份进入参数摘要；项目代理仍不能接收 global full/session 自动许可 |
| 主 Bot → Worker → Verifier → 重启 | 历史批准不提供图片资源真值，无 approver 时先拒绝 | 共享模块核对宿主计划、父 Bot 与 session；现有批准日志存资源授权，继承命中后才判断是否需要 approver |
| 一次授权 / 通用会话授权 | 文件写、命令名称或能力相同便复用 | once 不进 scope 缓存；scope/session 绑定具体参数、能力、会话、计划和工作区；恢复簿键补 workspace |
| Goal 前置确认 → Provider | 同 toolCallId 可跨能力与参数复用 | 限一次桥接；确认处记录宿主投影出的实际能力；Provider 参数规范化只沿同一次宿主外层参数桥接 |
| 并发主回合 | 会话工具上下文缓存被不同回合改写角色、目标路径、权限与回调 | 每回合 fork 上下文，只共享工具缓存；角色、授权与目标字段各自独立 |
| 本地授权条 / Bot 授权卡 | “一直允许”批准所有排队请求；陈旧图片卡缺资源授权入口 | 只决定当前展示操作；图片卡明确读取并交给模型、具体文件、当前 Bot 及任务、30 分钟；重启后同样持久签发 |
| 撤回 / 文件变化 / 解码期间 | 已缓存许可可能继续返回像素 | 改访问策略清空缓存并撤回图片批准；Provider 读取前与返回像素前重检授权；文件身份变化拒绝 |
| TUI | 同一 session 相同能力批准不同参数；chat mode 下角色边界未再次核对；toolContext 未传入 Node Runtime | 同一操作摘要隔离；当前角色和 mode 共同执行能力闸；转交权限上下文、检查取消和租约 |
| MCP / Skill / Hook / 自动化 / objective probe | 核对各 Provider 的宿主策略及执行闸，不从模型说明取得批准 | 不新增图片之外的资源继承，不将 Shell/文本/图像许可互换；原自动化、只读及 probe 执行拒绝保持 |

普通非委派 Goal 只能沿自身宿主绑定会话使用资源许可，不能伪称另一 Bot 的父身份。局部 UI 只提交用户决定，主进程和共享 Runtime 保存并执行权限真值。

TUI 的本次验收重点是具体操作许可、恢复和角色边界；默认 TUI 尚无内置本地图片解码 Provider，不宣称其视觉 UI 或真实图像模型闭环已被验证。

## 7. 实施与验收记录（2026-10-11）

代码交付：[Peer-Agent PR #151](https://github.com/ly-ccx/Peer-Agent/pull/151)，追加提交 `09b51770323a5f2b73a9e600a331e35d8f669bcf`。前一提交的委托核验生命周期修复继续适用；本 ADR 补上图片正式授权与继承，并修正全局审计发现的通用操作复用问题。

### 契约与运行回归

- 三项越权用例在修复前实际失败：同一 toolCallId 改能力/参数/主体仍放行、一次文件批准扩大到另一文件、scope 缓存未隔离操作；修复后通过。
- 真实 `LocalImageProvider` 路径输出 PNG 模型侧带，确认主 Bot → 子执行者 → Verifier → ApprovalStore 压缩/重启后仍使用原授权 grantId。解码适配器为受控测试，不代表真实云模型理解质量。
- 不同 workspace/父 Bot/文件、文件身份变化、取消/暂停/被取代的计划、未授权普通 Goal、无审批者、过期、撤回、保存失败与解码期间撤回均拒绝。权限真值和像素来源仍由本地链提供。
- Desktop 同一操作显式 scope 复用与不同参数重新询问、宿主 Goal 确认桥限次与实际能力、并发回合权限上下文隔离均覆盖。
- TUI 覆盖具体操作、workspace/session 恢复隔离及 project_agent 角色在 chat mode 下的写闸；默认 TUI 无本地图像 Provider，视觉闭环不在此验收范围。
- 全仓 `pnpm test`：8,301 passed、5 skipped、0 failed、0 cancelled；Runtime 1,225、Desktop 5,503 + i18n 1、TUI 760。最终授权文案修改另通过 i18n 构建与测试。
- `pnpm build`、`pnpm typecheck`、`pnpm architecture:check`、UI 图标/圆角约束与 diff 检查通过。

初次全仓重跑暴露旧测试仍期待宽泛文件授权，已改为具体文件批准并追加不同文件重新询问断言；并发重建 dist 曾引起缺导出，单文件及稳定源码串行完整重跑后通过。未放宽权限闸或把失败记为预期通过。

### 产品回归

正式产物包 `/tmp/peer-permission-product-v4`，`qa:product:capture` 与 `qa:product:verify` 均通过。Run ID：`d777c2df-d9d8-4667-821a-dfc6ab7eca16`；源码指纹：`da28c147c6c5e9c5bc23c51f14a881f559e87fa02657f3eeeb2302f9ab0fe7d9`。捕获期间代码文件稳定；main 场景启动时记录前一 Git HEAD，期间仅提交相同文件，后续独立场景记录当前提交，最终文件指纹校验通过。

AI 实施者实际检查全部 145 张必需截图，逐图记录观察；`independent=false`，没有称为独立审查。新增深色 1280 与浅色 760 图片授权卡明确区分“仅这一次 / 本轮允许此图片 / 拒绝”，显示具体路径、交给当前模型、当前机器人及任务、30 分钟有效期。机器交互使用生产 CardView → IPC → ApplicationService → ApprovalStore，键盘 Enter 签发资源授权，并确认另一排队写请求仍未批准。长路径在窄窗口换行，不产生横向溢出。

两项既有次要限制记录在 review.json：透明 Quick Chat 的离屏 PNG 无法证明原生浅色合成对比度；旧侧栏失败摘要仍可能带 response_ 技术前缀。均不改变本次图片权限真值或阻止授权动作。

覆盖为源码 Electron、隔离数据和受控模型。键盘与 reduced motion 场景通过，未覆盖完整读屏、真实 Provider 的网络时序、安装版 RC 或长期运行。用户日常源码、当前 RC12 与真实用户授权/任务数据未修改。
