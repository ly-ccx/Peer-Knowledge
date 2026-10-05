# RC macOS CLI凭据助手身份补修

创建/更新：2026-10-02。Accepted，沿负责人“全部做完并先自测Ready”的既有修复授权推进。B级：发布装配边界，复用既有Developer ID身份；运行时能力、PermissionGrant、KeyStore和Evidence契约不变。

## 实际失败

RC1 npm安装CLI使用默认同目录助手，Mac解锁后仍超时。相同隔离凭据副本，CLI助手ping5ms成功、get10秒超时；Desktop签名助手get24ms成功、源debug助手13ms成功。[证据](evidence/rc-installed-cli-unlocked-failed-20261002.json)。codesign确认CLI助手为ad-hoc、无Team、标识含构建UUID；Desktop助手Identifier=peer-credential-helper、Team82672N97RP、Developer ID。尚不自动改变钥匙串ACL或放宽超时。

## 方案与允许改动

- `.github/workflows/release.yml`：CLI构建在同tag Desktop产物就绪后，macOS读取已签名公证的mac资产，装入同一个helper；Linux原产物装配不变。用户CLI归档依旧自包含，不要求安装或运行Desktop，满足ADR48；该ADR已有允许后置正式签名的决策，无架构变更。
- `scripts/prepare-macos-cli-helper.mjs`：只在macOS装配，验证版本、严格签名、稳定Identifier、Developer ID和Team；复制到构建CLI同目录，复验SHA/签名，失败即阻断归档，清理本脚本的临时解压目录。禁止拿源debug助手顶替发布助手。
- `scripts/package-cli-archive.test.mjs`：覆盖错版本、ad-hoc/错身份、提取/复制失败与清理、签名后字节保持、装配顺序；既有changelog:test进CI，无新依赖。
- 本卡、RC自测/测试手册、交付状态：记录失败、修复、CI和实际候选安装复验。下一候选rc.2；旧tag及下载资产不改。

## 门禁

先用本次真实RC1 Desktop签名助手与同次真实CLI二进制的隔离装配复现，验证默认助手真实工具读取（仅证明装配方案）。定向、完整构建/typecheck/architecture与两平台CI通过后合入，再发布rc.2并重新下载验证签名/逐字节SHA/npm默认助手/实际CLI与复杂任务、多入口。不记录秘密，不创建另一凭据存储，不调整钥匙串ACL、helper超时或权限策略。正式版仍等负责人全面测试和七天日用。

## 同轮另一个未完成验收

实际RC1 Desktop默认签名助手可以读凭据。双写真实任务已获计划批准、独立worktree有正确输出；A使用Bash精确字节核对作为criterion Evidence，Verifier上下文只见旧read_file快照，最终仍执行中/核验失败。同时项目代理背景回合收到HTTP200的真正空文本/零工具响应，带来源汇报等待超时；未签收/合回。[失败证明](evidence/rc-installed-complex-first-failed-20261002.json)。这些事实继续独立定位，不把两个文件已写等同全流程通过。

## 本轮实施

[PR100](https://github.com/ly-ccx/Peer-Agent/pull/100)已合入 `352649e216bddaaf776f5edeb4670b46015e24e4`；[CI36955000092](evidence/rc-cli-helper-ci-20261002.json)macOS/Linux均通过。实际RC1 CLI二进制保持SHA不变，隔离装配同次签名助手、无helper覆盖后，真实read_file与post_reply成功；临时凭据已清除。[装配证明](evidence/rc-cli-signed-assembly-passed-20261002.json)。首次启动隔离变量错误已作废，自己的可见fixture行已清除、无关registry/conversation行保持相同，审计日志保留。代码补修完成，实际rc.2资产/npm默认助手复验尚未完成，不能宣称Ready。
