# B5-R 多入口预发布交接（已发布，RC验证继续）

日期：2026-10-02。代码 PR #91 精确tip `31aa7fffcf9e8ec9d214b829861e6be9d96fdd07` 两平台CI36884859784通过，合入 `d90e58c275f56e5414363fc5df42734c14e16cab`；该HEAD的 `v0.1.0-beta.5` 已发布。正式版仍0.0.18。实施边界见 [b5-r-release.md](b5-r-release.md)。

## 已完成的准备与自测

stamp-version更新beta5版本事实、README beta标记、中英说明与changelog。根build/type/architecture/最终完整test均exit0（Desktop5238，5既有skip；Runtime976/TUI749/Gateway200/Protocol227）。版本/来源/changelog/提交HEAD后readiness通过。首次根测试的发布事实断言仍写死beta4，更新为beta5后完整复跑通过，没有跳过；未提交的readiness按HEAD检查版本diff，提交后通过。

真实配置glm-5.3-flash：源码Electron拥有租约，独立Bun TUI为客户端发只读README请求，desktop实际read_file Evidence后post_reply；同时配对真实HTTP/WebSocket设备适配发同项目输入，两次同ID返回首次回执、对话仅一条，Desktop真实模型回复；Desktop退出后TUI获取租约、恢复输入并真实read_file/post_reply。三轮均实读BETA5_HANDOFF_OK，不开写任务，pageErrors0、owned进程正常退出、复制的模型凭据清理。

[脱敏证据](evidence/b5-r-source-multi-entry-20261001.json)：精确准备代码head，真实模型，不是脚本回复。Remote使用test账户、memory identity、loopback socket seam，共享真实宿主facts/queue、不能执行；不冒充已部署OIDC或真实手机。不是安装包证据，最终签名候选版复测/远程真实任务批准提示/产物/npm事实仍待发布后补齐。

## 发布产物和实际安装事实

[Release](https://github.com/ly-ccx/Peer-Agent/releases/tag/v0.1.0-beta.5) publishedAt=2026-10-01T15:46:06Z，14资产。工作流36885978024全部成功：三平台Desktop、两平台CLI、mac签名/公证、npm。下载的mac arm64 ZIP与CLI归档SHA256与Release digest一致；codesign deep strict、stapler、spctl均通过，Developer ID Team82672N97RP。四个npm包公开version/beta均为0.1.0-beta.5，latest仍0.0.18；隔离临时安装CLI实际输出peer 0.1.0-beta.5。[产物证据](evidence/b5-r-release-20261002.json)。

真正发布编译CLI的PTY验证列表/方向键选择/帮助/退出通过，[结果](evidence/b5-r-installed-terminal-20261002.json)及[录屏](evidence/b5-r-installed-terminal-20261002.cast)。不含模型请求。

mac签名发布应用gpt-6-luna实测Desktop/远程读文件、post_reply、同ID回执去重通过；复杂只读任务未成功创建：Responses wire省略strict时供应商将可选字段填空字符串，本地严格validator正确拒绝，无法产生批准卡。GLM还发现供应商超时/不支持工具的失败。此初始安装失败[明确保留](evidence/b5-r-installed-first-failure-20261002.json)，不能宣布发布包全功能ready。PR#92及知识#23已修复Responses编码（保持可选字段可选，未放宽本地验证）；源代码真实模型多入口+批准+接管重跑通过，证据在RC修复交接。Beta5 tag与资产不覆盖；最终RC签名安装包必须重跑同场景。

## 后续退出门禁

B5-01–05实现与Beta5发布完成；RC-01–05、最终签名候选包自测和详细用户手册继续。全功能ready必须绑定候选HEAD、实际包版本及完整矩阵，不能用源码/脚本/发布成功代替。GA仍待负责人连续全面测试。
