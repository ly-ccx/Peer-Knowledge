# RC35：旧派发自占用恢复与取消回执收口

创建时间：2026-11-02
最后更新：2026-11-02

状态：最终联合源码已通过全量发布检查与产品自审；RC35已发布，公开资产、包内修复、签名公证及本机更新均已核对。原任务尊重较新的用户取消并已收口，Peer目录无未释放占用；不宣称其它目录的历史未知调用已清空。

## 修复范围与实际状态

RC34 的发布成功没有解决现场原任务的排队自阻塞，不能当作该修复已经交付。RC35 沿原派发 Evidence、规范完整 Tool Result 和 completed 协调操作恢复已成功派发的事实，再通过既有停止屏障结清尚未启动子任务的同源保护。原任务身份、历史、预算和权限保持，不重放调用；未知 Shell 结果、活体及无关目录保护不会按时间或任务终态直接清除。契约扩充和宿主影响见 [ADR116 §16](../../knowledge/decisions/116-session-control-and-resource-settlement.md#16-成功派发回执与排队自阻塞恢复2026-11-02)。

本轮合入全部代码 PR：[#262](https://github.com/ly-ccx/Peer-Agent/pull/262)（成功派发后排队自阻塞恢复）、[#263](https://github.com/ly-ccx/Peer-Agent/pull/263)（批量取消回执按输入和任务区分）、[#264](https://github.com/ly-ccx/Peer-Agent/pull/264)（回复下方原任务引用及“回复时”状态）、[#265](https://github.com/ly-ccx/Peer-Agent/pull/265)（完整发布说明）。知识 PR112 已先合入。原代码和知识工作区的未提交内容没有被扫入发布。

现场目标在验证期间已通过产品被取消。最新取消决定优先：不为证明队列推进而重启已取消任务。候选宿主启动后实际读取原 Plan、停止回执和设备资源账本：取消 completed，runner/scheduler idle，unknownCalls 为空，原 claim released，Peer 目录无未释放占用。对当前账本的一致性副本调用原调度准入，允许同目录新执行。该检查没有创建新的个人任务或调用模型/工具。

更早的一致性快照仍保留原 queued 形状，已在最终源码上通过原规范历史/Evidence/协调存储和普通 supervisor 冷恢复，原执行器入口恰好一次、身份不变、屏障 settled；执行器只记录入口，没有实际模型或工具执行。它不代替当前个人实例或正式安装验证。另一个目录的一条历史 Shell 结果仍未知，原保护保留，不能宣称全设备未知调用已清空。

## 最终候选与检查

候选 `4a58e2846875f85de69915764a127096721c5b0d`，预发布基线 `PeerAgent/dev/0.1.0`，源码指纹 `72b1a73b7ff99a8fb6b343a1a2938a86f54e87e6059f6a78a68426d875346ae3`。冻结及推标签前所有 open PR（含 draft、其它目标分支）均为空；[最终 CI 41407008849](https://github.com/ly-ccx/Peer-Agent/actions/runs/41407008849) 的 macOS/Linux 作业成功。

14项门禁全部通过：完整 build、typecheck、architecture、IPC、Rust build/tests、全套 Node/Bun 测试、产品回归契约、发布源测试/检查、Runtime pack 内容与外部宿主 smoke、readiness、changelog。全套按包串行调度，Desktop 文件 concurrency=2，未改断言或超时；Runtime Node 1753通过、TUI 817通过，Desktop 6150项中6145通过、5项既有跳过、0失败。最终组合候选首轮通过；前序候选和 PR 的失败仍另列保留，不混为首轮全程通过。

标准产品包 `8f7014e5-55b3-4f61-b6b1-7eb083fae3d9` 的255张必查图实际逐张自审，verify 通过；输入建议19项/8图及资源工作区19项/8图也重新运行、逐张自审并绑定同一源码。默认任务首层只有当前进度、状态及完整任务入口，取消/核验/证据等资料按需展开。新任务引用支持键盘打开原任务、保留草稿和历史“回复时”状态；引用原文与任务入口各用其语义位置。

受控源码样本中位数：列表27.45ms，可见搜索38.90ms，输入至“已收到”37.5ms；后台延迟事件未恢复自动追随，读位5284至5283。实现者自审 `independent=false`；不证明真实模型能力、网络速度、正式安装版完整交互、全部系统IME、读屏器或长期运行。Quick Chat 透明源码 PNG 另在中性浅底合成后审阅，不能当作原生材质验收。

双语 release notes、CHANGELOG、站点用户文档及版本已提交。README: updated；更新预发布版本说明，细节留在用户文档和发布说明。完整逐图意见、PR head/merge、日志摘要与失败限定见 [源码验收回执](evidence/rc35-source-acceptance.json)。私有源码包归档包含所有必查图、机器报告、自审和工程日志，不含个人数据备份或钥匙串导出。

## 发布与安装

发布流水线 [Release 41413520373](https://github.com/ly-ccx/Peer-Agent/actions/runs/41413520373) 的8个作业及 [Pages 41413520372](https://github.com/ly-ccx/Peer-Agent/actions/runs/41413520372) 最终全部成功，绑定同一标签与候选。[RC35](https://github.com/ly-ccx/Peer-Agent/releases/tag/v0.1.0-rc.35) 的14项资产均完整上传并有摘要；三平台beta更新清单的版本、文件、大小及SHA512编码一致。四个公开npm包的精确版本和rc标签为RC35，latest仍0.0.18，tarball可达；Pages五条路径、manifest最新beta及中英文版本内容均读回通过。

首轮macOS核验在向Apple票据服务查询时发生NSURLErrorDomain -1005断网，stapler返回Error 68；失败阻止了Release/npm作业。保留原失败日志后，在未改标签、源码或签名门禁的条件下重跑失败作业，签名、公证及后续发布全部通过。npm最初两次读回尚未包含新版本，第三次传播后通过。不能称发布全程首轮通过。详见 [发布回执](evidence/rc35-publication.json)。

实际下载macOS arm64 ZIP，SHA256与GitHub资产摘要、SHA512与更新清单均匹配；版本、bundle ID和arm64架构正确，严格深度codesign、Developer ID Team 82672N97RP、stapler及Gatekeeper Notarized Developer ID全部通过。对7个修复路径核对实际app.asar：Runtime模块按标签源码和固定TypeScript 5.9.3编译选项比较，Electron宿主直接比较源码，包内摘要均匹配。CLI归档亦实际下载核对，`peer --version`为RC35，helper签名及字节摘要与同次Desktop一致；没有替换全局CLI。

先完整备份个人数据并核对，再以候选宿主观察当前取消事实；正式替换前只对该已登记候选进程请求正常退出，未停止其它隔离实例。再次完整备份应用数据12,930个文件（3,867,412,912字节）和Electron配置24,611个文件（1,441,292,432字节），文件集合、大小及SHA256全部一致。保留RC34应用及前后两份完整数据备份，不导出或修改系统钥匙串。正式应用替换前后严格签名检查通过，并从正式位置启动。

安装后核对应用版本RC35、真实进程路径、原项目宿主租约与新鲜心跳；原任务继续保持cancelled及cancellation completed，停止屏障settled、unknownCalls为空，Peer目录未释放占用为0。对当前一致性账本副本调用同一调度准入仍允许新执行，未重启已取消任务、未修改个人JSON/SQLite事实，也未创建新个人任务或调用模型/工具。另一目录的一条历史Shell未知结果仍受原范围保护。详见 [安装回执](evidence/rc35-installation.json)。

这是正式安装版版本、宿主与实际取消/资源状态核对；没有将255图源码自审说成完整安装版UI回归，也没有声称真实模型执行、系统IME或读屏器验收。源码归档、原失败、发布核验与安装记录保留在私有证据中，可移植回执不含个人机器路径、任务标识或用户历史内容。
