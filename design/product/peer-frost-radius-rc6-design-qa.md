# RC6 连续曲线与灰底正式组件验收

创建时间：2026-10-05。最后更新：2026-10-05。

2026-10-05。C级表面修订；不改变运行时、授权、Evidence或存储边界。以负责人已批准的连续曲线/灰底 Demo 为目标，生产 Renderer 原样加载到隔离 Electron 宿主，不向实机注入 CSS。

## 目标与比较

普通控件 12 px、紧凑控件 8 px、分组/浮层 16 px，支持连续曲线时使用 `superellipse(1.4)`。浅色灰底 #E9EDF2、深色 #2C3440，默认无可见描边/阴影；悬停加深，键盘聚焦保留清楚的蓝色轮廓，强制颜色模式恢复系统边界。菜单保留很轻的阴影，分组保留均匀细边界。侧栏底部分隔线铺满列宽，操作与版本保持内边距。

[完整并排比较](assets/peer-frost-radius-rc6/15-source-production-comparison.jpg)、[等密度控件细节](assets/peer-frost-radius-rc6/16-controls-comparison.jpg)、[抽屉并排比较](assets/peer-frost-radius-rc6/17-drawer-source-production.jpg)。源 1168×724，原生 2560×1720@2x，后者缩为 1280×860@1x后组合；不同容器宽度没有强行等比缩到相同控件尺寸。Demo 含演示工具栏、较少导航和示例内容，生产保留全部合法分区、真实路由值/身份和历史消息。共同层级、字号、行距、表面、控件尺度与箭头位置可直接比较；不声称全页像素相同。

## 发现、修复与复验

- P2：档案入口、头像动作残留旧描边。改为相同灰底紧凑控件，修复后[实机详情](assets/peer-frost-radius-rc6/06-final-drawer-native.jpg)复验。
- P2：所属消息的回答选项残留旧描边。改为灰底、8 px 连续曲线，保留焦点和强制颜色边界；修复后[最终实机](assets/peer-frost-radius-rc6/18-final-options-drawer-native.jpg)与[Demo再次并排比较](assets/peer-frost-radius-rc6/19-final-drawer-comparison.jpg)，表面和紧凑圆角一致；当前生产输入框有焦点，演示输入框无焦点，边界差别属于正确状态。
- CI 窗口首次失败：底栏铺满宽度后，旧断言误把外边缘当作版本对齐线。断言改测实际 content edge，并新增整条分隔线与列边缘的几何检查；保留全部窄栏不溢出/不重叠要求和72种状态布局。

## 已执行的交互

- 浅色标准、深色大字号的通用页与菜单：[浅色](assets/peer-frost-radius-rc6/14-final-general-light-native.jpg)、[深色大字号](assets/peer-frost-radius-rc6/11-dark-large-general-native.jpg)、[展开菜单](assets/peer-frost-radius-rc6/13-final-dark-menu-native.jpg)。字体、主次说明、行间分隔、右端箭头和菜单选中态清楚，无光晕式产品阴影。截图的紫色共享图标/鼠标高亮来自检查工具，不属于产品。
- 发送自由输入：旧选项和需要你计数立即收起，[实机](assets/peer-frost-radius-rc6/07-free-input-native.jpg)。
- 流式正文同一条消息逐段增长，[生成中](assets/peer-frost-radius-rc6/08-stream-native.jpg)；实际停止后部分正文、未完成标记和草稿保留，[停止后](assets/peer-frost-radius-rc6/09-stopped-native.jpg)。受控 Provider 分片，不作为真实订阅模型质量通过。
- 重新打开后本机器人模型/强度保留；历史图片和文件回显保留。模型、附件、隔离、焦点、减少动效和存储路径由完整自动回归与实际 Electron smoke 另行检查。
- 本轮两次原生拖动没有改变窗口尺寸，不算新的1040×760通过；前一轮正式组件窄窗证据继续保留。最终CI另含900px抽屉焦点及240/292/360侧栏状态布局。

## 未计为通过的范围

真实云模型质量、网络稳定性、剪贴板图片的所有格式、跨应用拖放、超大附件、实体手机、生产远程、全量读屏、Windows/Linux交互安装和七天日用。本轮产品语义未简化：回复来源不是一律硬编码为你，任务执行和复核配置独立，通知方式是只读事实。

## 实际发布包复验

不可变RC6发布后，直接下载已签名ZIP并以隔离数据/profile运行原包，不修改asar或CSS。以下为实际发布包截图：[通用设置](assets/peer-frost-radius-rc6/20-signed-rc6-general-native.jpg)、[版本与实际检查更新](assets/peer-frost-radius-rc6/21-signed-rc6-update-native.jpg)、[对话与抽屉](assets/peer-frost-radius-rc6/22-signed-rc6-conversation-drawer-native.jpg)、[引用定位](assets/peer-frost-radius-rc6/23-signed-rc6-quote-locate-native.jpg)。检查更新显示“已是最新·v0.1.0-rc.6”，无旧Beta弹窗；灰底层级、紧凑控件、左右消息/下方回执、滑动分段与原消息定位符合方案。

签名包两条合成历史仅验证表达；未配置模型，模型字段合法禁用，不冒充真实模型执行或Evidence。实际签名与关键模块字节独立核对。自有窗口已退出，原用户应用/数据未替换。[版本绑定、范围与截图hash](../../playbook/v0.1.0/evidence/rc6-published-ui-passed-20261005.json)。

final result: passed
