# B5-05 逐机器人远程授权交接

日期：2026-10-01。状态：已完成并合入。代码PR #90在 `8556ab36` 通过双平台CI [36883768066](https://github.com/ly-ccx/Peer-Agent/actions/runs/36883768066)，知识PR #21合并 `0210b0d`。代码 `8556ab36`，基线B5-04合并 `22c050ce`；实施边界见 [b5-05-remote-grants.md](b5-05-remote-grants.md)。

## 交付与边界

每台机器人两列可查看/可发消息，默认关闭；消息依赖查看，撤销查看清掉消息。保留其他机器人的授权。使用现有BotAvatar / SVG Checkbox / Switch，地址明确保存、授权版本、配对链接与复制错误、最近访问。纯状态Module隔离轮询/保存/卸载竞态。中文/英文资源键完全一致。

共享protocol设置/patch/访问DTO替代renderer局部合同。既有IPC拒绝未知字段、注入版本与畸形顶层参数；本机controller继续校验嵌套授权、先保存再重连，失败连接可手动重新连接。最近访问只读已有device事实，关闭或冷启动不触钥匙串；只导出时间/操作/工作区ID，拒绝非法日期/操作/路径。main净增-1；无新IPC、依赖、执行或存储路径。

## 自测证据

- 根build/typecheck/architecture/test exit0。Runtime976 / Desktop5238（5233pass、5既有skip）/ TUI749 / Gateway200 / Protocol227，0fail。完整测试后仅补日期上限和复选框label，最终summary专项与Desktop build再次通过；最终双平台CI会重跑完整门禁。
- 67专项通过：权限依赖、保存版本/幂等、近期访问、冷启动白名单、旧轮询不能覆盖保存、保存期间不再更新/轮询、卸载后忽略晚回复、错误不被轮询清掉、IPC畸形与未知字段、两语言资源/错误提示。
- 真Electron、两台隔离机器人、生产IPC：初始全关→查看→发消息（版本3）→撤销查看同时撤消息→另一机器人键盘Space开查看（版本5）。SVG4枚、页面error0、无横向溢出。
- 首轮UI脚本选错窗口、第二轮发现缺label导致SVG拦截输入点击；修复label后用可见SVG鼠标点击及键盘完整复测通过。没有跳过控件或强制点击伪造通过。
- [Electron证据](evidence/b5-05-settings-20261001.json) / [截图](evidence/b5-05-settings-20261001.png)。源码Electron/构建renderer，关闭远程、无真实模型/部署OIDC/安装包；这些证据不替代B5-R与RC06。

## 下一步

双平台CI和Review后合入，随后B5-R实际Beta5预发布、RC01–05、详细用户测试文档与安装候选版。GA等待负责人全面测试。
