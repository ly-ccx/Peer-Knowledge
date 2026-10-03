# RC5 评测候选发布

2026-10-03，Accepted。负责人明确要求先发布RC，再进行详细评测。沿既有自主修复、合入授权执行新不可变 `v0.1.0-rc.5`，不发布GA、不移动旧tag或资产。

## 范围

C级发布卡；基于开发线94c31ce6，纳入已经两平台CI并合入的PR113–116：消息表面与主题、引用/回复操作、取消左侧强调线、机器人模型设置首屏及保存/隔离验收。没有运行时、权限、Evidence或存储契约变更。复杂写任务命令描述Evidence快照的独立阻塞保持，负责人现在授权评测候选，不宣称总体Ready。

分支 `PeerAgent/pa/rc5-candidate`，一张发布PR。

## 允许改动

- `scripts/stamp-version.mjs` 已定义的版本事实源集合：VERSION、README.md/README.zh-CN.md、root/apps/managed packages 的package.json、credential-helper Cargo.toml及Cargo.lock；仅经既有stamp修改版本。
- 新 `release-notes/v0.1.0-rc.5.md`：中英修复、升级、验收范围及现存限制。
- README两份候选说明链接；既有changelog生成物，仅由build-changelog生成。
- `scripts/build-changelog.test.mjs`：当前候选断言指向RC5。
- `scripts/rc-upgrade-matrix.mjs` / `.test.mjs`：保留RC4历史毕业检查，加入RC5，受控行数由22增至23；六版真实旧tag来源保持。
- 知识库本卡、rc-release、rc-self-test-report、acceptance-test-guide及`evidence/rc5-*`：明确确定版本与SHA、详细评测步骤、自测事实和未覆盖范围，195既有用例/6流程不减少。

不修改发布workflow、electron-builder、能力/存储/运行时逻辑；不新增依赖。严格发布门禁、签名/公证和平台矩阵保留。

## 退出条件

新版本完整build/typecheck/architecture/test与版本/changelog/readiness通过；干净源原生9壳/12可访问性/7诊断/5回复检查通过；最终两平台CI，通过后按既有授权合入并固定tag。Release全部job成功，核对三平台Desktop及两CLI归档/更新清单/npm固定版本；Mac实际下载SHA、Developer ID/公证、版本和关键UI检查。实际新候选发现/下载与安装证据分列，不注入事件代替真实更新；用户安装数据不得重置。发布与手册链接、现存限制可直接交给负责人评测。

## 源码门禁（2026-10-04）

发布PR[117](https://github.com/ly-ccx/Peer-Agent/pull/117)，干净最终源a402d130d26929ebf7345decb3f2bbefdbeec527。完整build/typecheck/architecture/test、独立AST、版本/changelog/readiness/source-check均通过；桌面5320项中5315pass、原5skip，无首次失败或取消。23项受控升级矩阵保留六个真实旧tag来源；实际源码窗口9壳/12可访问性/7诊断/5回复、72更新布局和36回执通过，Bot模型保存/重开/切换/继承与其他角色、机器人、全局隔离全部通过。中位列表14.579ms、搜索22.6ms、Received52.8ms，原预算不变。见[门禁](evidence/rc5-source-gates-20261004.json)、[窗口](evidence/rc5-source-window-passed-20261004.json)、[矩阵](evidence/rc5-upgrade-matrix-passed-20261004.json)。

最终两平台CI37135649368 attempt1全部通过，实际窗口同为9/12/7/5，无页面/授权错误、自有进程退出。PR117已合入64d20d3409fe406c3cae4044acff9f8b5a7fe45e；source/CI合成merge/实际merge的tree均a57b0fb1bcffc0c2d19764bc0fd1788099d45c6d。合入后readiness/source-check及干净状态再次通过，按授权创建新不可变v0.1.0-rc.5。[CI绑定](evidence/rc5-candidate-ci-binding-20261004.json)。以上是源码范围，签名发布包和真实更新发现尚待后续验证；不宣布已发布或总体Ready。


## 发布完成（2026-10-04）

Release37136323530八job成功、14资产，实际Mac签名/公证及关键界面、CLI版本、npm固定RC5、真实三平台清单、原用户RC4发现并下载RC5已验证；原用户应用保持RC4未安装。完整范围见[当前自测报告](rc-self-test-report.md)。本卡作为评测候选交付完成；复杂任务独立Evidence阻塞和GA门禁继续保持。
