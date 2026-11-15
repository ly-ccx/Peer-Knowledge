# R5w2：网页独立窗口与实例接续

日期：2026-10-27
状态：源码已实现，待组合验证；未验收。
依据：ADR109 §36；A/B/C。默认右侧工作区不变，显式另开地址副本；未验证保活迁移时不显示移动。

交付：宿主所有的独立网页实例、最小 chrome/preload、受控地址/导航与公开外观；真实 guest 归属校验；Registry/reveal 知道原生窗口和代次；用户返回原会话并确认；关闭不停止任务。

回归设计：宿主来源伪造/会话缺失/非法 URL、限额包括准备中、载入关闭/超时、sender/代次隔离、Registry 单 owner、背景刷新不夺 active、guest 崩溃/销毁清理、file/data/弹窗拒绝；前端状态与地址编辑/IME、局部失败、返回失效/标签已关闭；真实原生窗口联调与登录分区/焦点在授权后执行。

## 源码收口记录（2026-10-27，未验收）

- 先补 ADR109 §36。新增真实 BrowserWindow chrome + 宿主 WebContentsView、独立 browser-resource role、最小专用 preload。每个副本均分配新标签/窗口/代次，实际源 guest 的 host/sender、会话/标签/URL 经宿主复核；限额包括准备中，网页没有 preload/Node/应用 API。默认原会话右侧与 guest 保留，未提供未经验证的保活迁移。
- 支持地址、后退/前进/刷新/停止、真实加载/崩溃反馈、受边界约束的视口、公开外观、显式返回和关闭。地址输入复用 IME guard；事件/启动/动作回执按代次和序号合并，迟到状态不能把新 URL 改回旧页。返回原标签只切换标签不重新 load；标签已关只回原会话，源上下文不可达时局部说明并保留副本。返回请求有 sender/代次/3 秒截止及提交后确认。
- 浏览器 Registry 新增 native window/generation/available 元数据；单实例身份不可覆盖，后台标题/URL 更新不重新夺 active，用户明确选择或真实焦点才切目标。主浏览器注册/注销复核真实 embedded host，guest 销毁自动清理。原生崩溃留下仅限当前活动项的不可用身份，新用户选择清理墓碑。
- reveal 优先实际 native owner，不向主 renderer 借旧 ack；读取当前存活窗口和呈现事实，后台不聚焦，不以 visible=true 代替最小化/隐藏事实。provider 在既有执行/授权/Evidence 链内用单独 continuity policy 收口 native 身份；失效或 await 中换目标不创建 headless、不重跑网页动作。普通 embedded 兼容策略不变，原生动作回执保留真实窗口/代次。
- 退出与异常清理关闭自身 WebContents，不等待远程 beforeunload、不关闭原页，不恢复任务/重跑写入。网页副本不冒充文档历史恢复，不保存正文/表单/执行态。

已编写 Protocol、宿主窗口与生命周期、角色/来源/URL/限额/返回、Registry 墓碑与背景状态、native reveal、provider 失效/换目标不得 fallback、前端迟到状态与原标签保持的用例，更新触及的替身，加入资源组合测试入口。仅内容/diff 自审与正常生成 sandbox preload；未运行测试、构建、类型、架构/IPC 检查或截图/交互回归，不能据此称原生联调通过。R6a 的历史通过不覆盖本包。未提交/推送/重启/发布，原个人现场未操作。

状态：R5w2 源码已实现，待授权后的组合验证；下一包 R8 反馈与上下文准入，R9/R10 仍待实现。
