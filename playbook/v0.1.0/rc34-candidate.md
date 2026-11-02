# RC34：任务摘要、停止资源收口与 Terra

创建时间：2026-11-02
最后更新：2026-11-02

状态：最终联合源码验收通过；`v0.1.0-rc.34` 已发布，Release、npm、更新源及Pages已核验。本机已备份并更新为RC34，实际窗口版本与任务披露已核对；原任务仍排队，不能把发布成功当作历史未知调用已解决。

## 范围与边界

用户要求将所有 PR 一起合并、完成发布检查、发一版 RC 并更新本机安装版。本轮审阅并合入全部代码 PR：[#257](https://github.com/ly-ccx/Peer-Agent/pull/257)（旧任务停止确认与目录资源收口）、[#258](https://github.com/ly-ccx/Peer-Agent/pull/258)（GPT-6.1 Terra 订阅模型目录）、[#259](https://github.com/ly-ccx/Peer-Agent/pull/259)（任务默认精简）、[#260](https://github.com/ly-ccx/Peer-Agent/pull/260)（主 Bot 输入表面层次）、[#261](https://github.com/ly-ccx/Peer-Agent/pull/261)（RC34准备与发布场景适配）。对应知识 PR #108、#109、#110 亦已合入。未提交的原工作区文件未被纳入或覆盖。

任务默认仅保留身份、当前状态、简短进度和完整任务入口；创建时间、取消、核验、证据、历史、追问及模型等信息按需展开，同任务刷新保留用户展开选择，切换任务收起。状态仍取宿主结构化事实，不用指令或旧说明覆盖当前停止、阻塞和核验进度。此为 C 级表达变更。

停止收口为 B 级 Runtime 修复：在既有停止屏障、受管句柄、持久化回执及目录资源账本 seam 内恢复可核对的旧取消与接管状态；真实完成晚于诊断期限仍允许收口，已结清回执在资源版本前进后保持幂等重放。活跃句柄、未知调用和新代次继续受保护，不按时间、助手文字或任务终态直接解锁，也不重放未知写入。权限、能力暴露、Evidence 与 System Context 的边界不移动。

Terra 沿原 ChatGPT Responses adapter 和模型目录接入；已有默认选择保持。上下文预设是本地预算，不代表每个订阅账号的上游硬上限。本次发布回归不证明真实 Terra 账号能力或模型质量。继续使用联合协调格式9，升级前保留完整数据备份，Desktop、CLI/TUI、Gateway 使用匹配版本。

## 最终候选与工程门禁

最终提交 `a875cacb06e600cab3f68565ac7324a0779c8fbe`，源码指纹 `ec69e4ecfb7c933bfa3fa04b98aaa1250cfe8fa48d11fc892be4920cdd46617b`。全部 PR 检查成功后合入；冻结时与推标签前再次清点包括 draft、其它目标分支的所有 open PR，两个仓库均为空。[最终主线 CI 41385512309](https://github.com/ly-ccx/Peer-Agent/actions/runs/41385512309) 的 macOS/Linux 作业全部成功。

14项工程门禁完成：build、typecheck、architecture、IPC、Rust build/tests、全套 Node/Bun 测试、产品回归契约、发布源测试/检查、Runtime pack 内容及外部宿主 smoke、readiness、changelog。首轮本地并行 `pnpm test` 的11个 TUI 文件出现失败，逐文件各隔离重跑一次全部通过；未改源码、断言或超时。被中止的 Desktop 与未运行的根测试补齐，Desktop 用 concurrency=2 降低竞争负载，6147项中6142通过、5跳过、0失败、0取消；跳过项不计通过。不能称全套首次通过。

Runtime 外部宿主 smoke 首次遇到个人 npm userconfig 的 EALLOWSCRIPTS；使用独立临时 userconfig 禁用安装脚本后，同一安装/import smoke 通过，个人设置未改。所有初次失败与重跑日志摘要保留。[可移植源码验收](evidence/rc34-source-acceptance.json) 记录日志摘要、PR实际 head/merge、完整逐图意见及最终候选绑定。

## 产品回归

标准包 run `cd6d7ed2-b23b-42e9-94e2-fc5bff18b23d` 的255张必查截图全部实际逐图自审，`qa:product:verify` 在最终源码通过。任务运行/等待/签收/失败默认态、完整任务展开/收起、缺资料/失败/旧资料/重试、取消与焦点、停止/结果未知/已取消/接手、四种核验结论、图片授权生命周期、恢复与收尾均覆盖。划词引用锚定、滚动、离屏关闭、键鼠、草稿、正文边界、宽度重排及停靠断言全部通过；输入建议19项/8图与资源工作区19项/8图重新运行并逐图审查通过，同一源码指纹绑定。

受控源码样本：列表中位13.76ms，可见搜索中位22ms，输入到已收到中位37.5ms；阅读位置5224.5到5223.5，延迟后台事件未重启追随。这不是安装版端到端打字、系统IME、真实模型质量或网络延迟承诺。实现者自审 `independent=false`；未做完整读屏器、长期运行及全部系统输入法验收。Quick Chat 源码 PNG 含透明像素，浅色布局另在中性浅底合成后审阅，不能据此认证安装版原生材质对比。

预冻结本地 full smoke 曾因原生截图期间 hover 丢失未过，保留原失败记录；未针对该事件改源码或断言，最终冻结采集通过同一真实 hover 检查。此前 PR 阶段遇到的停止回执重放、旧展开区定位、inspector display 读取与设置保存忙态问题已在各 PR 修正，不继承旧候选验收。

双语 release notes、CHANGELOG、用户文档、站点及版本文件已提交。`check:changelog` 输出 `changelog data is current (112 releases, 113 JSON files)`。README: updated；版本与预览入口同步，细项留在发布说明及更新日志，不把根README改成逐条变更表。

## 发布与本机安装

发布流水线 [Release 41389202186](https://github.com/ly-ccx/Peer-Agent/actions/runs/41389202186) 的8个作业全部成功；[Pages 41389202183](https://github.com/ly-ccx/Peer-Agent/actions/runs/41389202183) 成功部署。[RC34](https://github.com/ly-ccx/Peer-Agent/releases/tag/v0.1.0-rc.34) 的14项资产均上传且大小非零，双语说明完整。三平台beta更新清单版本、文件、大小及SHA512编码与资产一致；四个公开npm包的精确版本及rc标签均为RC34、latest仍0.0.18，tarball均HTTP200。前两次registry读取仍为旧缓存，第三次读回通过；未覆盖任何公开版本。Pages五条路径HTTP200，manifest.latest.beta为RC34，时间戳有效，版本JSON中英完整。详见 [发布回执](evidence/rc34-publication.json)。

实际下载macOS arm64更新ZIP，SHA256与GitHub资产摘要、SHA512与更新清单均匹配。解压后应用版本、bundle ID及arm64架构正确；严格深度codesign、Developer ID Team 82672N97RP、stapler和Gatekeeper `Notarized Developer ID`全部通过。macOS CLI归档亦实际下载并核对SHA256，执行 `peer --version` 为RC34；helper签名与同次Desktop helper字节摘要一致。未修改全局CLI安装。

确认本机正式安装版未运行后，完整备份应用数据12,784个文件（3,804,539,225字节）及Electron配置24,611个文件（1,441,287,412字节），共37,395个文件；所有文件集合、大小和SHA256一致后才替换应用。保留RC33安装包及替换前应用，不导出或修改系统钥匙串。新应用替换前后严格签名检查通过，并已从正式安装位置启动。

通过原生应用AX和截图实际看到RC34版本、原有机器人及历史。打开现有任务，默认仅身份、状态、短进度和完整任务入口；展开后创建时间、取消、核验和证据可见，再收起恢复精简。未发送消息、创建任务、切换模型或改写个人任务事实。这是安装版启动/版本/基本披露核对，不是255图完整安装版回归，详见 [安装回执](evidence/rc34-installation.json)。

**个人实例残余状态：** 原“移除Workbench顶部重复返回入口与空行”任务安装后仍显示“排队中：正在核对本机资源状态”；资源账本还保留2项历史未知调用的reconciling保护。该状态未被宣称已清空，也未绕过宿主强制解锁；历史未知执行仍需沿既有证据与结果对账。RC34修复可核对停止/资源收口的路径，不证明所有个人历史未知调用已经解决。

源码完整截图包、逐图意见、机器报告、失败和重跑日志已保存为私有归档，PR审阅尝试亦另存私有归档；可移植源码回执记录两份归档的SHA256，不提交个人机器路径或用户数据。原代码/知识工作区未提交内容与无关预览实例均保留。
