# RC：Beta / RC 更新发现诊断

创建时间与最后更新：2026-10-02。状态：PR111修复已合入；最终两平台CI、RC4实际签名包原生检查和原用户人工升级通过。旧客户端与首轮检查脚本失败记录保留；未来自动下载安装另验。

## 实际机制与偏差

产品有 auto / beta / stable 三种偏好；beta 应包括所有预览版本，RC无需增加用户渠道。发布工作流把 beta、alpha、rc 都产出为 beta*.yml；正式版为 latest*.yml。RC2实际 beta-mac.yml 的 version 为0.1.0-rc.2。

实际 electron-updater 6.8.9 GitHubProvider 先遍历GitHub releases.atom，beta筛选却把rc当custom channel跳过，因此Beta5仍选v0.1.0-beta.5，不会访问RC2清单。其channel setter还自动开启allowDowngrade；当前装配未关闭，使RC2＋beta会把Beta5判成可用更新。更换为rc字符串亦不能修复产品的双通道映射：Provider会请求rc-mac.yml，而RC2只有beta-mac.yml。

[联网复现](evidence/rc-update-live-discovery-failed-20261002.json)执行真正Provider选版与AppUpdater资格判断，仅HTTP执行器采用Node适配，读取真实Atom及清单，无安装包下载、用户设置写入或应用替换。原安装Beta5 Provider与当前依赖文件SHA相同。ok=true仅表示探查脚本成功，expectedBehaviorPassed=false表示产品行为失败。

## 当前检查时机

安装应用启动静默检查一次、每小时再检查；应用激活/窗口聚焦距上次检查至少5分钟再查，用户点击检查可主动触发。开发模式默认禁用。auto预发布先探查严格更新的正式版，失败或不存在则回退beta；手动偏好优先。检查只表达可用更新；下载由用户触发，下载后支持重启安装，也配置了退出安装。

## 必须补齐的交付条件

1. 真实Provider必须覆盖Beta5→RC、RC→后续RC、Beta/RC→更高正式版以及已是最高版本；稳定通道排除预发布。
2. 各通道都要求版本严格更新，不因切换渠道或正式版较旧而提示降级；下载/已下载阶段仍受已有相位锁保护。
3. 验证真实发布标签选择、平台清单路径、资产URL及SHA；受控事件/模拟updater不代替真实发布发现。
4. 修新源码不能修已安装Beta5。必须单列旧客户端可达的兼容发布入口（或明确人工安装的迁移方式），实际证明旧版本到新候选可达；不能只发一个旧客户端会跳过的新RC。
5. 保持RC1/RC2不可变，不覆盖已有资产、标签或正式latest；更改发布兼容策略先进入既有决策/发布卡再实施。负责人L11需要实际旧版检查并防降级。

诊断阶段先交付阻塞证据，当时尚无修复代码或新发布资产。机器人侧栏入口PR106是独立表达补修；后续修复与安装结果见下文。


## 2026-10-02 修复进展

Accepted [实施卡](rc-update-provider.md)，B级沿冻结SDK已有custom Provider工厂，实际打包配置提供host/owner/repo/cache。预览选最高有效alpha/beta/rc并读取beta平台清单，清单版本与tag绑定；正式保留latest端点，所有渠道allowDowngrade=false。主进程可用/已下载事件及下载/安装入口重复严格版本校验，拒绝旧包时关闭退出自动安装；原相位锁保留。

PR111源码f2bef5eb/tree66e91b52，本机完整门禁及32项定向测试通过。首轮完整矩阵因VM导入白名单未接新模块失败，实际模块与generic受控feed适配后21项矩阵通过，未改断言。[源码门禁](evidence/rc-update-source-gates-20261002.json)。真实SDK+Node HTTP读取实际已发布Atom/latest/三平台清单，12项通过：Beta5/RC2发现RC3；RC3不提示同版本或旧Beta，旧正式0.0.18不可降级；继承资产URL/SHA512解析通过。[联网修复结果](evidence/rc-update-live-discovery-fixed-20261002.json)。此探查不是包下载/安装或物理Win/Linux，滚动发布资格被受控为true以隔离版本选择。

PR111最终两平台CI36994414880与RC4候选CI36995512881均通过；PR111/112已合入。新不可变RC4发布后，三平台真实清单12项及实际签名macOS包beta/auto/stable检查通过，旧版本/同版本均不可用，下载/安装入口再次拒绝，无更新时退出安装关闭。[RC4真实发现](evidence/rc4-update-live-discovery-passed-20261002.json)、[签名包原生检查](evidence/rc4-installed-updater-passed-20261002.json)。旧RC3错误提示未触发下载；原用户已备份并从官方固定RC4包人工更新，原数据和模型偏好保持，实际重新检查显示最新。[原用户迁移](evidence/rc4-original-user-install-passed-20261002.json)。旧Beta5/RC3被冻结的实现没有被修，先人工安装新候选后才使用新更新器。不移动旧tag/覆盖旧包；未发生的未来RC自动下载/安装不记Pass，复杂任务独立阻塞未改判。
