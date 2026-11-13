# RI-00：封存F0拆解与补充资格对照

2026-11-13。C级诊断；沿用`00-adr-map.md`、`96-task-execution-responsiveness.md`及仍Proposed的`128-local-runtime-isolation-and-bounded-query-contract.md`，产品/权限/Evidence/存储/System Context边界不变。不是重构或现场开工许可。[原Q/H](runtime-isolation-ri00-formation-e3.md#9-本轮实际qh收据与现场准入结论)及[本轮封存审计与冻结预算](../../playbook/evidence/runtime-isolation-ri00-e3-f0-audit-20261113.json)分别保留。

## 1. 先查封存点，不增加产品读取

原H报告SHA与已提交回执核对后，重算18块、144点，排除每块首点得到126暖点，按原门保留115个兼容点。另11暖点因major/incremental或其它线程CPU拒绝，未删除原始点。10块极差超过15ms，分布在六个F0；不是每一块都不稳定。

18块的兼容最高/最低Evidence用户CPU点，已观察root minor GC次数均分别为12/11；更关键的是GC与12个Evidence调用的重叠位置不同。例如C1 main-A最高点11个Evidence跨度观察到minor，最低点只有7个，Evidence用户CPU差18.797ms，整根用户CPU差12.781ms，根外于Evidence的用户CPU反向变化−6.016ms。计时边界内外的分配/回收相位不能忽略。但这里只记录相关性与成本迁移；GC记录是wall重叠，不能从user CPU减掉它来证明精确GC成本。

仅按root minor次数分层仍有三块超过15ms：T1 main-B同12次组19.707ms，T2 main-B15.610ms，T3 main-A16.973ms。根GC次数也不等于Evidence内GC位置相同。细分到逐位置GC签名通常只剩1–2点，不具备独立验收样本量，不能靠事后分层替换15ms门。T1 main-B的最高/最低整根指令相差约0.99%、周期相差4.58%；T3 main-A对应周期仅相差约0.41%、counter CPU却增加约16.28ms。根内工作量与执行速率代理均变化；PMC只包住整个Supervisor，不能把它们拆成Evidence内部指令/真实核频，也不能断言是哪种系统活动造成。

兼容点自计元数据CPU为0.662–0.993ms；Efficiency层主线程CPU最多0.266ms。没有证据支持“此次暖段极差由主线程大规模转去E核”或简单的元数据CPU相加；这不证明采样器没有状态影响。18块全12遍CPU向量与GC位置保留，不只看中位数。H相邻根间隔161.919–166.344ms；旧C2夹测约154–157ms。两版都明确等待150ms，故不能把“新加了150ms”当解释；新增差别包含排队调度和每点take/序列化/fsync/ACK，跨窗口差异本身不是因果证明。

目前能闭合的是拒绝项来源和观测到的结构：GC进入哪个调用边界不同，加上整根工作量/执行速率波动；尚不能证明这些相位为何形成，更没有解释旧30–40ms。先检验一个确实在两版测量程序中不同的因素，而非同时改预热、间隔、heap、VM或样本数。

## 2. K：只改变排空归档的粒度

唯一因素为probe `take/ACK`：A每点排空，B每8点块后排空。两者都保持同一个setImmediate单槽队列、原生产读图、heap统计、150ms等待、每点PMC、块末3次原生校准、同源输入/输出和默认VM。每个ticket完成记录在ACK ticket前fsync；B只延后完整row batch排空，最多8行，仍受16MiB未ACK上限。没有把完整业务数组传回或留存。A/B都使用相同的完成ticket日志，因此不会把durable ACK与unsafe ACK作为混杂因素。

固定2个target及1个常驻参照，target-1按A/B/B/A，target-2按B/A/A/B，每宿主8次相同预热；每checkpoint仍main-A8→参照8→main-B8。每target四次完整checkpoint是本次归档粒度资格对照，不是原H补样本，不实施Evidence顺序曝光。两种模式都完整跑固定顺序，原失败保留；只有身份/未知成本/预算/元数据损坏立即终止，没有看到绿就提前停、重排或追加。

K使用封存`8cfb68f0`的probe/queue/installer精确源码，不加载A新增入口包装或hook。本轮先冻结K设计，A的功能/映射验证可独立推进；未执行K不得写成K通过，也不能据A通过进入F。后续K须先补齐控制器与counter全程成本收据，不能把旧helper未计量边界按零补账。

支持“逐点排空足以造成本数据资格失败”必须同时满足：两个进程各两次A均仅因暖极差拒绝；各两次B均通过原fast资格（包含所有块≤15ms、校准、PMC、图和差额）；每个进程A/B的最大块极差中位改善至少5ms；A返回时重新失败。任一不满足就不支持这一充分原因，不能把最后一个B绿色挑出作现场入场证。若A/B均失败或时间顺序决定结果，继续保留unknown，不自动改成预热或另一个因素矩阵。

K支持也只说明本测量程序的资格影响，既不说明旧残差，也不自动恢复H形成证据。原六例仍是0/3，不重算。现场仍须自己的F0/F1及自然前史。

## 3. A：入口与信号适配器合同，验证后才能谈现场

实际注册入口限定五个IPC（list/get/list-sessions/get-session/list-obligation-grants）和Directory.list根。必须从实际注册handler的具名闭包定位ports、service、Directory与Supervisor，记录对象相等性和未覆盖项。源码显示Directory.list使用`Supervisor.listByWorkspaceIds`，只包装`Supervisor.list`会漏掉该读者；get/getSession也不能从方法名推断和list相同的读图。不得以空Directory stub的通过冒充生产映射。

Adapter只包装已定位的原函数，保持receiver、原返回值/Promise和原异常；原权限校验链外层不动。入口元数据只含枚举shape、递增seq/parent、epoch、起止与有界首签名栈，不存参数值。同步嵌套与异步父链区分，无法关联的根明确unknown；不把相近时钟推成父子。Directory.list在IPC内为子入口，根外才能记tray-compatible目录根，不能单凭目录被调用宣称用户点击了tray。列表批读必须记录实际命中的reader identity，根外index继续归档；只声明已装配范围。

Signal Adapter消费已归档行，不执行产品查询。固定F0后60秒静默，再用最初5个同源完整自然根的全12遍用户CPU中位作基线；不筛掉minor/major/incremental位置、不滚动重学。单根≥+12ms且≥4%或wall≥2秒只产生signal；单遍+6ms只记定位；新的已映射入口/端口顺序可准入一次首见证而不要求CPU升高。单槽busy合并原因但不追加查询，最多2个不同exposure、无新覆盖8分钟终止；源/产物/owner变化、记录满额、RPC不确定即封存。首见证→旧Q的前后次序不能颠倒，signal不等于G2确认。

固定两个owned验证槽：一个functional Electron验证getter、receiver/Promise/error、同步/异步父链、重入/忙槽/期限/源与owner失配、先fsync后ACK、lease失联恢复；一个生产只读Electron用封存输入、真实服务/注册Module及Directory查询接缝验证五入口与batch reader映射、index顺序、自然信号及方法恢复。没有Runner/模型/写入口；其它不参与映射的消息/审批等依赖明确是空只读替身，不宣称完整Desktop运行。合成CPU数字只在纯策略测试，显式notFieldCause，不向宿主加耗时。生产自然数据若没有signal，只验证它未错误触发，不能伪造形成。

两个槽的原始失败各占预算，不能改名补槽；方法/绑定/队列/端口和源恢复不确定则资格失败。现场Inspector装配仍须核对当前实际对象和安装产物；无法证明的读者标缺并拒绝入场，不能沿用owned对象身份。

## 4. 新预算及账本

用户要求设计新预算并继续补齐适配器。以下是本次新增、执行前冻结的owned额度，不挪用已用完的原Q/H，不重启或接入实际Peer：

| 阶段 | 启动、工作与截止 |
|---|---|
| K | 2 target+1共享reference，≤10分钟，全部读体≤150秒；8次完整checkpoint，共192根加24预热，3次最终语义审计计费。固定A/B/B/A与B/A/A/B；不追加 |
| A | 1 functional+1 production Electron，≤5分钟，全部产品读体≤30秒；功能lease2.5秒/外部恢复15秒截止；最多8入口/256记录/每根64段 |
| 共用 | 新增5次Electron启动，最多2个同时存活，Node控制器和libproc辅助另列；总墙钟15分钟、读体180秒、控制器/辅助CPU20秒，新增逻辑输出256MiB、总journal32MiB、未ACK16MiB；零profile、零强制GC、零VM flags、零替换 |

已用E3 Q5/H7共12次启动、读体133.290262秒全部保留；新增5次后owned计划总帽从28变33，活动墙钟总帽从97变112分钟。新增只为K/A，旧F/R的预算和门不变，不能把未花预算换成H或A补样本。F/R仍未准入；没有K的可用资格策略和完整A验证，不进入现场。成本未知或最后一次同步读越界照录并停止新增，不杀实际应用或抹掉失败。

实现/实际运行候选、失败及恢复另回填；设计文档和通过纯测试都不能冒称K/A已执行或现场归因。RI-00闭合与产品重构的门不变。
