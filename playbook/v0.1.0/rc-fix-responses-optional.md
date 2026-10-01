# RC 修复：Responses 工具选填语义

状态：实施边界 Accepted，验证中。授权：负责人要求全部完成并在交付前全面自测；必要修复、知识回写和合入由执行方推进，正式版仍须负责人测试确认。

## 分级与范围

A 级 provider wire 契约修复；ADR 28 §9 已 Accepted，先于代码变更记录。
代码分支 `PeerAgent/pa/rc-fix-responses-optional`，知识分支同卡号。

允许文件：`apps/desktop/electron/main/provider-encoders/responses-encoder.mjs`
与 `responses-encoder.test.mjs`。若真实集成揭示另一处原因，应单独记录边界与修复。
不改已发布 beta.5 tag；修复随 RC 候选包交付。

2026-10-02 搜索真实 TUI 路径后补齐范围：
`packages/runtime-node/src/chatgpt-responses-provider.ts` 及其测试、
`packages/runtime-node/src/provider-encoders/responses-encoder.mjs`、
`packages/runtime-node/src/provider-encoder.test.mjs`、
`packages/runtime-node/src/model-provider-contracts.ts`（只新增选填 `strict?: boolean`）。
共享 provider request 的 strict 策略与 ADR 28 §9 相同，不改变 Capability Manifest、
Projection 或 Tool Call 的执行协议。TUI 真实调用走该共享 provider；漏修会导致入口语义分裂。
现有重复 encoder 的后续 seam 是合并到共享实现，本卡不做整套消息编码迁移。

## 必须证明

1. 先写失败测试：未声明 strict 的嵌套 / 扁平工具均显式非 strict，选填字段与 required 不被改写。
2. 显式 true / false 原样保留；参数校验仍拒绝空目标 ID、取代任务 ID和不适用的核验字段。
3. 定向 encoder / adapter / project-agent 工具测试、桌面完整测试、typecheck、architecture check。
4. 真实模型通过本地创建任务、生成计划审批卡，远程只读取「请回电脑批准」摘要；记录首次失败与重跑结果。
5. 两平台 CI 通过后合入。最终安装包回归在 RC 发布卡重新执行。

## 初次失败事实

Beta.5 已签名公证安装包、打包凭据 helper、gpt-6-luna / Responses：桌面读取与远程读取及同 ID 幂等成功；新增远程只读任务在三次非法选填参数后未创建，审批等待超时；该次未继续到 TUI 接管。
失败不得写成多入口全绿。原始测试数据仅存在执行环境的隔离临时目录，持久证据须脱敏。

## 实现与自测交接（2026-10-02）

代码：PR #92，desktop encoder + 共享 encoder + 实际 TUI Responses transport；未声明策略显式 false，显式 boolean 原样保留。provider request 类型只增选填 strict。无新 IPC / capability / dependency / storage；main 净增0。

验证命令与结果：

- `node --test apps/desktop/electron/main/provider-encoders/responses-encoder.test.mjs apps/desktop/electron/main/provider-adapters/openai-responses-adapter.test.mjs packages/runtime-node/src/project-agent/tool-specs.test.mjs`：21 pass。
- `node --test packages/runtime-node/src/provider-encoder.test.mjs packages/runtime-node/src/chatgpt-responses-provider.test.ts`：18 pass；新的共享 schema 测试在修复前失败。
- `pnpm build` 两次通过（共享 provider 修改后重建）。
- `pnpm test`：根全量通过，runtime-node 978、desktop 5241（5236 pass / 原有5 skip）、TUI 749、gateway200、protocol227，其余包及根脚本均通过。
- 类型检查首次暴露测试 fixture 的 find 返回值未缩窄；补 assert.ok 后重跑，不改生产逻辑、不删除测试。最终 `pnpm typecheck` 通过；精确 HEAD CI 待回填，不能用初版 CI 代替。
- `pnpm architecture:check`：最终共享修复通过。

真实 gpt-6-luna 自测见 `evidence/rc-responses-first-20261002.json` 和 `rc-responses-repeat-20261002.json`：先保留接管 harness20秒超时失败，再等待任务回合回复并允许接管过程中的真实恢复回合完成，重跑通过全部多入口步骤；桌面/远程/TUI实际 read_file/post_reply、真实 spawn→本地计划审批、远程摘要只读、同ID一份canonical消息，零pageerror。测试账号/loopback不是生产OIDC；源代码Electron/Bun不是最终安装包。最终RC安装包必须再验。
