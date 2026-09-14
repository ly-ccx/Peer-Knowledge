# 远程接入开发交接

创建时间：2026-09-14
最后更新：2026-09-14

## 接手结论

本轮只交付设计和进度，不修改应用功能、线上认证、钥匙串或用户数据。

首先阅读 [文件凭据与一次授权完整方案](../design/product/remote-access-simple-implementation.md)。用户明确要求降低使用门槛，优先本地文件持久化；不要重新实现一套强制注册、手工复制两串码的默认流程。分 S1（文件存储、兼容旧协议）和 S2（无需账号的扫码授权）开发，不混为一次未经验证的大迁移。

## 代码基线

代码仓：Peer-Agent，分支 `0.0.13`。

- `1f6f8a2b6df228da85260b98e90987073fde4512`：test(desktop): pin remote binding reuse across restarts。
- `e1f4452b`：此前配对显示、连接失败提示等交接提交。
- `41e968bc`：wire the remote read path to a real connector。

当前仍使用 remote-identity-keychain.mjs 保存 Ed25519 seed，setup-remote-access.mjs 通过 identityStore 加载身份，remote-binding.sqlite 保存绑定。已存在跨 setup 实例公钥不变、绑定复用测试。新方案的 identity.json、迁移错误语义、新浏览器授权协议均未实现。

重点文件（相对代码仓）：

- apps/desktop/electron/main/runtime-gateway/setup-remote-access.mjs 与对应测试。
- apps/desktop/electron/main/runtime-gateway/remote-identity-keychain.mjs 与对应测试。
- apps/desktop/electron/main/runtime-gateway/remote-access-controller.mjs。
- apps/desktop/electron/main/runtime-gateway/remote-goal-read.test.mjs。
- apps/desktop/renderer/src/app/components/RemoteAccessPanel.tsx、remoteAccessPresentation.ts。
- packages/runtime-node/src/remote-device-handshake.mjs、remote-device-connection.mjs、remote-device-connector.mjs。
- apps/gateway/src：现有 account、device、binding 与连接集成测试；不是已经上线的新扫码协议。

重要纠正：此前对话曾称 delegation 没有拒绝作用，不应据此删掉授权。此次基线实际通过了撤销、禁止导出、owner、投影和读取后复查测试。

## 验证状态

2026-09-14 本轮实际重跑核心交接命令，53 tests / 53 pass / 0 fail / 0 cancelled，退出码 0：

```sh
node --test \
  apps/desktop/electron/main/runtime-gateway/setup-remote-access.test.mjs \
  apps/desktop/electron/main/runtime-gateway/remote-identity-keychain.test.mjs \
  apps/desktop/electron/main/runtime-gateway/remote-goal-read.test.mjs \
  apps/desktop/renderer/src/app/components/remoteAccessPresentation.test.ts
```

本机证据引用：local-shell-artifact://shell_cf83ca4c-6ebc-4fdf-bfa5-d62a4109b08e。该 artifact 不保证跨机可访问，以上命令才是可重建证据。

历史会话曾验证旧钥匙串实现冷启动后 online=true、同 deviceId、无新 pairing；曾报告 runtime-gateway 270、runtime-node 346、presentation 9 和 typecheck 通过。这些不是本轮真机重测，也不是新文件方案的验收。

历史桌面全量测试未完成：输出存在失败并挂起。此前断言“全部是既有问题”未完成严格基线对照，不应当作已证明归因。不得把不完整输出中的勾号数当最终通过数。新机器先跑核心套件，再按需隔离全量失败，不扩大本轮交付范围。

未验证：文件权限/原子发布/并发、旧数据迁移、无账号协议、扫码 UI、撤销新浏览器授权、Windows/Linux 真机、打包版本。完整方案中的矩阵是待实现测试要求，不是绿灯。

## 另一台电脑开始步骤

知识库当前实际 origin 是 yinLiangDream/Peer-Knowledge，与旧文档里的 ly-ccx 别名不同。本轮沿用实际 tracked remote，不擅自改 origin。两个仓库并排克隆，目录名不限：

```sh
git clone git@github.com:ly-ccx/Peer-Agent.git peer_agent
git clone git@github.com:yinLiangDream/Peer-Knowledge.git peer-knowledge
cd peer_agent
git switch 0.0.13
git pull --ff-only origin 0.0.13
git log -1 --oneline
git merge-base --is-ancestor 1f6f8a2b6df228da85260b98e90987073fde4512 HEAD
# Node >= 22.18，pnpm 使用 packageManager 指定版本
node --version
corepack pnpm install --frozen-lockfile
corepack pnpm build
# 然后运行上面的 53-test 核心命令
```

已有仓库先检查 `git status --short`，有本机修改不要强行切分支或覆盖。知识库使用 `git pull --ff-only origin main`；查看最新提交中本文件和方案是否存在。若 SSH 无权限，先处理 GitHub 授权，不改成未知远端。

pnpm build 是依赖准备，不是宣称本轮已执行构建。若新机平台缺少 Rust/凭据辅助工具或原生依赖，按代码仓 README 安装。不能把新 checkout 缺 dist 的错误归咎业务测试。

## 后续实施顺序

1. 开独立开发分支，实现文件 identityStore 与 S1 状态矩阵；先测试，再改默认接线。
2. 实现显式迁移，保持原公钥、deviceId 与绑定，失败不删除或覆盖。新机只用临时用户数据测试，不读取或迁移原电脑生产身份。
3. S1 通过后单独设计共享 protocol 类型并实现 S2 browser grant；保持旧账号用户兼容。
4. 完成方案中读权限交叉矩阵，再实现扫码 UI；旧服务器没有新协议时明确提示版本不兼容，不能偷偷退回未认证读。
5. 双端真机验证后再发布。线上部署、密码轮换、旧认证退役需要单独操作，不包含在本次文档推送中。

## 不要搬走的本机状态

不要把应用数据目录、seed 文件、钥匙串条目、remote-binding.sqlite、Cookie、secrets.env、临时 SSH/CDP 脚本或诊断日志提交或复制到新电脑。Git 同步的是代码与知识，不是设备身份。新开发电脑有自己的身份；验证旧用户迁移用隔离 fixture。

历史网络曾需要 hosts 绕过公司 DNS/TLS 中间人。它不是产品依赖，也不会随 Git 同步；新机若连不上先查 DNS、证书和代理，不复制硬编码 hosts、不关闭证书校验。不要在交接文档里写口令。

## 本轮 Git 边界

仅提交本文件与完整方案。知识库存在其他主题的修改、未跟踪旧 ADR 和临时文件，均不纳入本次提交；旧 ADR 75 的内容未完整审查，因此也不打包。本次方案自包含，解决其与旧稿方向冲突。代码基线已在远端；本轮没有功能代码修改，不制造空提交。两个仓库同步结果由交付回复给出，不在提交内循环记录自己的 commit hash。
