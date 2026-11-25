# ADR 136 工程实施文档：彻底移除 Qoder（本机 CLI）模型渠道与 Gemini OAuth 链路

> 创建时间：2026-11-25  
> 最后更新：2026-11-25  
> 状态：可执行实施规范（供 Codex 直接照单执行与验收）  
> 对应决策：[ADR 136：下线 Qoder（本机 CLI）模型渠道与 Gemini OAuth 链路](../decisions/136-retire-qoder-cli-provider-and-gemini-oauth.md)  
> 关联代码仓：`/Users/yinliang/.codex/worktrees/native-rust-cli/Peer-Agent`（本地分支 `codex/native-rust-cli`，基线 `690c0be6`）  
> 预计瘦身规模：约 **3.8 万行代码与契约夹具**、**6 个 Rust 加密依赖 crate**、**1 个外部 npm SDK 依赖（`@qoder-ai/qoder-agent-sdk`）**

---

## 0. 红线清单：严禁误删的保留项（DO NOT TOUCH）

执行任何删除前，先核对以下两类**必须 100% 完整保留**的模块：

### 0.1 保留「Qoder 市场」（在线 Skill 商店）
下列文件与符号属于 Skills 能力市场，与 Qoder 本机 CLI 模型渠道完全无关，**严禁删除或修改其业务行为**：
- `apps/desktop/renderer/src/capabilities/components/QoderMarketplacePanel.tsx`
- `apps/desktop/renderer/src/capabilities/components/SkillsPanel.tsx`（`view === 'qoder'` 选项与面板）
- `apps/desktop/renderer/src/capabilities/components/marketplace-workspace-target.test.ts`
- `apps/desktop/renderer/src/capabilities/capability-workbench.css`（Qoder 市场样式）
- `apps/desktop/electron/main/qoder-marketplace-service.mjs` 与 `.test.mjs`
- `apps/desktop/electron/main/main.mjs` 中 `qoderMarketplaceService` 相关挂载（第 80 / 403 / 2664–2680 / 3919–3923 行）
- `apps/desktop/electron/main/ipc/register-skills-ipc.mjs` 与 `.test.mjs`
- `apps/desktop/electron/ipc/channels.mjs` 中 `skills:qoder:*` 4 个频道
- `apps/desktop/electron/preload/preload.source.cjs`、`preload.cjs`、`apps/desktop/renderer/src/clientApi.ts`、`apps/desktop/renderer/src/preload/contracts/bootstrapPreloadApi.ts` 中 `queryQoderSkills` / `getQoderSkillDetail` / `installQoderSkill` / `listQoderTaxonomies`
- `packages/protocol/src/skill-marketplace.ts` 中 `Qoder*` 类型
- `packages/runtime-node/src/skill-store.mjs`、`skill-store.uninstall.test.mjs`、`crates/peer-store/src/skill_manage.rs` 中已安装 Skill 来源 `qoder` 的元数据读写兼容

### 0.2 保留普通 Gemini（API Key 模式）与 ChatGPT / Grok OAuth
- 保留 `CHANNEL_IDS.GOOGLE_AI`（`google-ai`）、`defaultWire: 'gemini'`、`authMethods: { api_key: { wire: 'gemini' } }`、`defaults.baseUrl: 'https://generativelanguage.googleapis.com/v1beta'` 及「Gemini 官方 API Key」接入卡片；
- 保留 `gemini-adapter.mjs`、`gemini-encoder.mjs`、`gemini-model-catalog.mjs`、Rust `crates/peer-runtime/src/model/wire/gemini.rs`、`apps/tui/src/gemini-provider.ts` 的 **`api_key` 主路径**，仅剥离其中 `authMethod === 'oauth_google'` / `cloudcode-pa` / `v1internal` / `oauthProjectId` 分支；
- 保留 `oauth_chatgpt` 与 `oauth_grok` 的全部登录、刷新、配额与测试链路。

---

## 1. 第一步：整文件删除清单（按层分组）

### 1.1 Rust Crates（约 4,400+ 行）
删除以下全部文件与目录：
- `crates/peer-runtime/src/qoder.rs`
- `crates/peer-runtime/src/qoder/`（整目录删除，含 `account.rs`, `account/tests.rs`, `account_files.rs`, `authentication.rs`, `catalog.rs`, `cryptography.rs`, `endpoint.rs`, `environment.rs`, `inference-public.pem`, `local_auth.rs`, `sensitive_json.rs`, `transport_encoding.rs`）
- `crates/peer-runtime/src/model/wire/qoder.rs`
- `crates/peer-runtime/src/model/wire/qoder/`（整目录删除，含 `messages.rs`）
- `crates/peer-runtime/src/model/stream/qoder.rs`
- `crates/peer-runtime/src/model/stream/qoder/`（整目录删除，含 `shape.rs`, `shape/blocks.rs`）
- `crates/peer-runtime/src/model/qoder_retry.rs`
- `crates/peer-runtime/tests/qoder_formats.rs`
- `crates/peer-cli/tests/native_qoder/`（整目录删除，含 `mod.rs`, `attachments.rs`, `legacy.rs`, `network.rs`, `options.rs`, `retry.rs`, `streams.rs`）

### 1.2 Desktop Electron Main（约 15,000+ 行）
删除以下全部文件：
- `apps/desktop/electron/main/provider-adapters/qoder-local-auth.mjs`
- `apps/desktop/electron/main/provider-adapters/qoder-local-auth.test.mjs`
- `apps/desktop/electron/main/provider-adapters/qoder-model-catalog.mjs`
- `apps/desktop/electron/main/provider-adapters/qoder-model-catalog.test.mjs`
- `apps/desktop/electron/main/provider-adapters/qoder-official-model-catalog.mjs`
- `apps/desktop/electron/main/provider-adapters/qoder-official-model-catalog.test.mjs`
- `apps/desktop/electron/main/provider-adapters/qoder-prepared-route.fixture.mjs`
- `apps/desktop/electron/main/provider-adapters/qoder-private-adapter.mjs`
- `apps/desktop/electron/main/provider-adapters/qoder-private-adapter.test.mjs`
- `apps/desktop/electron/main/provider-adapters/qoder-provider-expansion.mjs`
- `apps/desktop/electron/main/provider-adapters/qoder-provider-expansion.test.mjs`
- `apps/desktop/electron/main/llm-oauth/google-oauth.mjs`
- `apps/desktop/electron/main/llm-oauth/google-oauth.test.mjs`

### 1.3 `packages/runtime-node` & `apps/tui` & Renderer Assets
删除以下全部文件：
- `packages/runtime-node/src/provider-adapters/qoder-local-auth.mjs`
- `packages/runtime-node/src/provider-adapters/qoder-model-catalog.mjs`
- `packages/runtime-node/src/provider-adapters/qoder-official-model-catalog.mjs`
- `packages/runtime-node/src/provider-adapters/qoder-private-adapter.mjs`
- `packages/runtime-node/src/llm-oauth/google-oauth.mjs`
- `apps/tui/src/qoder-private-provider.ts`
- `apps/tui/src/qoder-private-provider.test.ts`
- `apps/desktop/renderer/src/assets/llm-providers/qoder.svg`

### 1.4 Native CLI 契约文件与校验脚本（约 17,000+ 行）
删除以下全部文件：
- `packages/protocol/contracts/native-cli/qoder-caller.json`
- `packages/protocol/contracts/native-cli/qoder-formats.json`
- `packages/protocol/contracts/native-cli/qoder-legacy.json`
- `packages/protocol/contracts/native-cli/qoder-requests.json`
- `packages/protocol/contracts/native-cli/qoder-retry.json`
- `packages/protocol/contracts/native-cli/qoder-streams.json`
- `scripts/native-cli/qoder-caller-contracts.mjs`
- `scripts/native-cli/qoder-format-contracts.ts`
- `scripts/native-cli/qoder-legacy-contracts.ts`
- `scripts/native-cli/qoder-request-contracts.ts`
- `scripts/native-cli/qoder-retry-contracts.ts`
- `scripts/native-cli/qoder-stream-contracts.mjs`

---

## 2. 第二步：依赖瘦身（Cargo & pnpm）

### 2.1 Rust `crates/peer-runtime/Cargo.toml`
已确认以下 6 个加密 crate 在 `crates/peer-runtime` 内**仅被 `qoder/` 使用**，移除它们并更新 `Cargo.lock`：
- `aes`
- `cbc`
- `aes-gcm`
- `hkdf`
- `rsa`
- `md-5`

> 注意：保留 `sha1`（`network/trust.rs` 使用）、`sha2`、`base64`、`zeroize`（`credentials` 与 `model_oauth` 使用）。移除后请执行 `cargo check --workspace --all-targets` 确认零缺依赖、零 unused dependency 告警。

### 2.2 NPM / pnpm 依赖
移除 `@qoder-ai/qoder-agent-sdk`：
- 根 `package.json`（`onlyBuiltDependencies` / 依赖列表）
- `apps/desktop/package.json`
- `packages/runtime-node/package.json`
- 运行 `pnpm install`（或同步更新 `pnpm-lock.yaml`），确保锁文件干净且不再安装 `@qoder-ai/qoder-agent-sdk`。

---

## 3. 第三步：逐层精准修改清单

### 3.1 Protocol & Native CLI 契约（`packages/protocol/` & `scripts/native-cli/`）
1. **`packages/protocol/src/index.ts`**：
   - `LlmWireProtocol` 移除 `'qoder-private'`；
   - `LlmAuthMethod` 移除 `'oauth_google' | 'qoder_local_auth' | 'local_cli'`（仅保留 `'api_key' | 'oauth_chatgpt' | 'oauth_grok'`）；
   - 订阅额度快照 `provider` 移除 `'gemini' | 'qoder'`；清理 Qoder 积分倍率/资源包专属注释与仅 Qoder 使用的私有字段（先 `rg` 确认无其它消费者再删字段）。
2. **`packages/protocol/contracts/native-cli/` 契约同步更新**：
   - `model-channel-registry.json`：删除 `qoder` 渠道定义；在 `google-ai` 的 `authMethods` 中删除 `oauth_google`（保留 `api_key`）；
   - `model-oauth-registry.json`：删除 `oauth_google` 条目（保留 `oauth_chatgpt`、`oauth_grok`）；
   - `model-oauth.json` & `model-binding.json`：移除 `oauth_google` 契约用例（或通过 `scripts/native-cli/model-oauth-contracts.ts` 重新生成）；
   - `model-wires.json`：移除 `authMethod === 'oauth_google'` 的 Code Assist 用例（用 `scripts/native-cli/wire-contracts.ts` 与 `count-contracts.ts` 同步校验/重生成，确保 Rust `model::wire` 和 `model_count` 契约测试 100% 绿！）。
3. **`scripts/native-cli/verify.mjs`** 及相关契约脚本：
   - 删除 `verify.mjs` 第 62–67 行的 6 条 `qoder-*-contracts` 调用；
   - 同步清理 `scripts/native-cli/channel-contracts.mjs`、`model-catalog-contracts.ts`、`model-oauth-contracts.ts`、`model-oauth-coordination.ts`、`wire-contracts.ts`、`context-contracts.ts` 中的 `qoder` / `oauth_google` 测试用例。

### 3.2 Rust Core（`crates/peer-runtime` & `crates/peer-cli`）
严守 **零 `unsafe`** 原则：
1. **`crates/peer-runtime/src/lib.rs`**：移除 `pub mod qoder;`。
2. **`crates/peer-runtime/src/model.rs` & `model/*.rs`**：
   - 移除 `mod qoder_retry;` 及 `NativeModel::with_qoder(...)`、Qoder 账户字段、Qoder 重试与 10605 慢队列分支；
   - `model/wire/mod.rs`：移除 `mod qoder;`、`Wire::Qoder`、`qoder_context_window`、`qoder_metadata`/`qoder_dialect`/`qoder_session_type` 等 `GenerationOptions` 字段；
   - `model/wire/gemini.rs`：删除第 80–93 行 `if i.options.auth_method.as_deref() == Some("oauth_google")` 的 Code Assist 包装逻辑（保留标准 Gemini `contents` / `tools` / `systemInstruction` / `generationConfig` 编码！）；
   - `model/wire/runtime.rs`、`model/stream.rs`、`model/authentication.rs`、`model/continuation.rs`、`model/error.rs`、`model/retry_seed.rs`、`model/sse.rs`、`model/usage.rs`、`cognition/attempts.rs`、`system_context.rs`：清理全部 `Wire::Qoder` / `qoder` 分支与 `oauth_google` 特殊字段（如 `project_id` / `user_prompt_id`）。
3. **`crates/peer-runtime/src/model_config.rs` & `model_config/channel.rs` & `model_catalog.rs`**：
   - `model_config/channel.rs`：移除 `Wire::Qoder` 受保护 header 规则（`cosy-*` 等）、移除 `matches!(auth, "qoder_local_auth" | "local_cli")`、移除 `Wire::Qoder` 端点、移除 `Wire::Gemini` 的 `if auth == "oauth_google"` `v1internal:streamGenerateContent` 端点与 `project_id` 分支；
   - `model_config.rs`：移除 `Wire::Qoder` 账户加载逻辑；**增加遗留配置安全降级单测**：验证当 `llm-providers.json` 包含历史 `channelId: "qoder"`、`authMethod: "qoder_local_auth"`、`authMethod: "local_cli"` 或 `authMethod: "oauth_google"` 时，解析返回清晰的 `ModelError`（如 `model_channel_unsupported` / `model_auth_unsupported`）而不影响同一配置里其它正常模型（如 OpenAI / Gemini API Key / ChatGPT OAuth）的加载与解析！
   - `model_catalog.rs`：移除 Qoder 与 `oauth_google` 目录分支。
4. **`crates/peer-runtime/src/model_oauth/token.rs` & `subscription_quota.rs`**：
   - `model_oauth/token.rs`：移除 `"oauth_google" => value == "google"` 与仅 Google OAuth 使用的 `project()`（如无他用）；
   - `subscription_quota.rs`：移除 `oauth_google` / Code Assist 配额查询分支；
   - `crates/peer-runtime/tests/model_count.rs`：清理 `oauth_google` 计数用例，保留 Gemini API Key 计数用例。
5. **`crates/peer-cli/tests/`**：
   - 移除 `crates/peer-cli/tests/native_episode.rs` 中引用 `native_qoder` 或 Qoder 的部分；
   - 更新 `crates/peer-cli/tests/native_model_oauth/mod.rs`、`login.rs`、`login/reconcile.rs` 移除 `oauth_google` 测试用例（保留 `oauth_chatgpt` 与 `oauth_grok` 测试）。

### 3.3 Credential Helper & `packages/runtime-node` & `packages/runtime-core` & `packages/system-context`
1. **`packages/credential-helper/src/model-oauth-refresh.ts`**：
   - 允许列表从 `['oauth_chatgpt', 'oauth_google', 'oauth_grok']` 收窄为 `['oauth_chatgpt', 'oauth_grok']`；同步检查对应测试。
2. **`packages/runtime-node/src/`**：
   - `index.ts`、`models-public.ts`、`providers-public.ts`：移除所有 `qoder-*` 与 `google-oauth` 导出及 `oauth_google` 常量；
   - `shared-model-config.ts` & `.test.ts`：移除 `qoder` / `qoder_local_auth` / `local_cli` / `oauth_google` 通道与认证逻辑；补充遗留配置安全跳过/拒绝测试；
   - `provider-adapters/gemini-adapter.mjs`、`provider-encoders/gemini-encoder.mjs`、`provider-adapters/context-count-adapter.mjs`、`provider-adapters/openai-chat-adapter.mjs`、`provider-diagnostics/provider-trace-recorder.mjs`、`subscription-quota.mjs`、`data-store.mjs`、`text-inference.mjs`：清理 Qoder 与 `oauth_google` / Code Assist 分支，完整保留 Gemini API Key；
   - `fast-mode.test.ts`：移除 Qoder / `oauth_google` 夹具。
3. **`packages/runtime-core/src/context-accounting-lifecycle.ts`** & **`packages/system-context/src/sources/provider-source.mjs`**：
   - 清理其中的 Qoder 特判分支或过时注释。

### 3.4 Desktop Electron Main（`apps/desktop/electron/main/`）
1. **`provider-channels.mjs` & `.test.mjs`**：
   - 删除 `GEMINI_OAUTH_NAME`、`GEMINI_CODE_ASSIST_BASE_URL`、`QODER_PRIVATE_NAME`、`CHANNEL_IDS.QODER`；
   - 删除 `CHANNEL_DESCRIPTORS[CHANNEL_IDS.QODER]`；
   - 在 `CHANNEL_DESCRIPTORS[CHANNEL_IDS.GOOGLE_AI].authMethods` 中删除 `oauth_google`（**保留 `api_key`**）；
   - 在接入目录卡片列表（`ACCESS_PRESETS` / catalog）中删除 `gemini-oauth` 与 `qoder-local` 两张卡片（**保留 `google-ai` API Key 卡片**）；
   - 移除 `inferChannelId` / `resolveChannel` 中 `oauth_google` 与 `qoder_local_auth` / `local_cli` 推断逻辑；检查 `PROTECTED_HEADER_NAMES` 中是否仍有专属头需清理。
2. **`llm-config-store.mjs` & `.test.mjs`**：
   - 移除 `qoder-local-auth` / `qoder-model-catalog` / `qoder-private-adapter` import 及所有 `isLocalCliAuthMethod`、`isGoogleOAuth`、`qoder_local_auth`、`local_cli`、`oauth_google` 逻辑；
   - **遗留配置文件兼容（CRITICAL）**：在读取现有 `llm-providers.json` 时，遇到已退役条目（`channelId === 'qoder'`、`authMethod` 为 `qoder_local_auth` / `local_cli` / `oauth_google`、`wire === 'qoder-private'`）时，**不崩溃、不损坏文件**，在对外列表/路由中过滤或标记 `disabled: true` + `retired: true`（或安全剔除出激活候选并回退到其它有效默认模型），且禁止通过 `addProvider` / `updateProvider` 新建已退役渠道！
3. **`provider-access-application-service.mjs` & `.test.mjs`**：
   - 移除 `google-oauth.mjs`、`qoder-model-catalog.mjs` import；
   - OAuth 登录方法白名单收窄为 `['oauth_chatgpt', 'oauth_grok']`；
   - 移除所有 `authMethod === 'oauth_google'`、`qoder_local_auth`、`local_cli`、`channelId === 'qoder'` 分支。
4. **其余 Main 服务与测试**：
   - `provider-credential-resolver.mjs` & `.test.mjs`
   - `provider-encoders/gemini-encoder.mjs` & `provider-encoder.test.mjs`（仅删 `oauth_google` Code Assist 包装，保留 Gemini API Key！）
   - `provider-adapters/subscription-provider-expansion.mjs` & `.test.mjs`
   - `provider-adapters/message-sanitizer.mjs` & `.test.mjs`
   - `provider-adapters/models-dev-registry.mjs` & `.test.mjs`
   - `provider-adapters/context-count-adapter.test.mjs`、`provider-adapter.test.mjs`、`provider-connectivity.mjs`
   - `provider-diagnostics/provider-trace-recorder.mjs`、`provider-transports/visual-request-context.test.mjs`
   - `subscription-quota.mjs` & `.test.mjs`
   - `account-usage-service.mjs`、`account-usage-availability.mjs`、`account-usage-auth-routing.test.mjs`
   - `usage-day.mjs` & `.test.mjs`、`usage-request-log.test.mjs`、`usage-stats.test.mjs`
   - `recovering-fetch.test.mjs`、`runtime-gateway/shell-env-snapshot.mjs`、`runtime-gateway/shell-task-manager.mjs`、`scripts/lab-workspace-isolate.mjs`

### 3.5 Desktop Renderer UI（`apps/desktop/renderer/src/`）
1. **`app/components/LlmSettingsPanel.tsx`**：
   - 删除 Qoder（本机 CLI）连接表单、错误文案映射（`qoder_*`）、前置检测提示、模型选择分支；
   - 删除 `oauth_google` / 「Gemini OAuth」登录与表单分支（保留 Google AI / Gemini API Key 表单与 ChatGPT / Grok OAuth 登录！）；
   - 若本机旧配置恰好存在已退役条目，不导致设置面板白屏或报错。
2. **`app/components/llmBrand.ts` & `.test.ts` & `LlmBrandIcon.tsx` & `assets/llm-providers/SOURCES.md`**：
   - 移除 `'qoder'` 品牌枚举、`qoder.svg` import 及单测断言（同步更新 `SOURCES.md`）。
3. **`app/components/llmSubscriptionAuth.ts` & `.test.ts`**：
   - `OAUTH_METHODS` 收窄为 `['oauth_chatgpt', 'oauth_grok']`，移除 `oauth_google` 文案与测试。
4. **`app/components/llmSubscriptionQuota.ts` & `.test.ts` & `accountUsageView.ts`**：
   - 移除 `oauth_google`、`LOCAL_CLI_METHODS`（`qoder_local_auth` / `local_cli`）及 Qoder 积分/资源包格式化分支与测试。
5. **`styles/llm-settings.css` & `chat/styles/chat-surface.css`**：
   - 清理 `/* Qoder / local CLI connect flow */` 等仅 Qoder 使用的死样式。
6. **`chat/state/providerRecoveryText.ts`、`types.ts`、`preferences.ts` & `.test.ts`**：
   - 清理 Qoder 慢队列（10605）专属恢复文案与类型；`preferences.ts` 中泛化的 `supportsReasoning=true && effortLevels=['off']` 退化处理逻辑本身有价值，仅替换注释里的 Qoder 示例文案即可，保留保护逻辑。

### 3.6 `apps/tui`（遗留 TS TUI 同步清理，保持全仓编译通过）
- 更新 `apps/tui/src/desktop-provider-adapters.ts`、`gemini-provider.ts` & `.test.ts`（仅删 `oauth_google`，保留 Gemini API Key）、`provider-wire-matrix.ts` & `.test.ts`、`tui-runtime.ts`、`chat-controller.ts`、`tui-subscription-quota.ts` & `.test.ts`、`model-config.test.ts`、`tui-model-selection.test.ts`、`tool-result-summary.test.ts`。

---

## 4. 验收门禁清单（Codex 必须逐项跑通）

### 4.1 零残留静态审计
执行以下命令，确认除了 **§0.1 Skills「Qoder 市场」** 明确保留文件外，没有任何模型渠道层残留：
```bash
rg -il "qoder" apps crates packages scripts package.json | grep -v "/dist/"
rg -il "oauth_google|gemini[_-]?oauth|oauth[_-]?gemini|google-oauth|cloudcode-pa|code.?assist|qoder_local_auth|qoder-private" apps crates packages scripts package.json | grep -v "/dist/"
```
预期结果：
- 第一条命令**仅允许命中** §0.1 列的 Skills「Qoder 市场」文件；
- 第二条命令应为 **0 命中**（除了显式处理历史 `llm-providers.json` 退役条目的兼容过滤逻辑及其单测外，无任何活跃路径残留）。

### 4.2 Rust 编译、Clippy 与单测门禁
```bash
export PATH="$HOME/.nvm/versions/node/v25.9.0/bin:$HOME/.cargo/bin:$PATH"
cargo test -p peer-protocol --lib
cargo test -p peer-store --lib
cargo test -p peer-runtime
cargo test -p peer-project-agent --lib
cargo test -p peer-core-rpc --lib
cargo test -p peer-cli --test native_model_oauth
cargo clippy --workspace --all-targets -- -D warnings
```
全部必须通过且零 `unsafe`、零警告。

### 4.3 JS/TS 单测、Typecheck 与构建门禁
```bash
export PATH="$HOME/.nvm/versions/node/v25.9.0/bin:$HOME/.cargo/bin:$PATH"
pnpm --filter @peer-agent/protocol test
pnpm --filter @peer-agent/credential-helper test
node --test "packages/runtime-node/src/*.test.{js,mjs,ts}" "packages/runtime-node/src/**/*.test.{js,mjs,ts}"
node --test "apps/desktop/electron/main/**/*.test.mjs"
node --test "apps/desktop/renderer/src/app/components/llm*.test.ts" "apps/desktop/renderer/src/capabilities/components/marketplace-workspace-target.test.ts"
pnpm --filter @peer-agent/desktop typecheck
pnpm --filter @peer-agent/desktop exec vite build
node apps/desktop/scripts/verify-overlay-backdrop-filter.mjs
```

### 4.4 真实 Electron 实机截图验收（隔离临时 `PEER_AGENT_HOME`，Light + Dark）
启动真实 Electron 窗口并实际查看截图：
1. **模型设置 → 添加提供商列表（浅色 + 深色）**：
   - 确认「Qoder（本机 CLI）」卡片已消失、「本地服务」若无其它条目不留空分组（或仅展示实际存在的本地服务如 Ollama）；
   - 确认「Gemini OAuth」卡片已消失；
   - 确认「Google AI / Gemini（API Key）」「ChatGPT 订阅」「Grok」「OpenAI / Anthropic / DeepSeek」均正常展示。
2. **遗留配置兼容场景**：
   - 在临时 `PEER_AGENT_HOME/llm-providers.json` 中预置 1 条历史 `qoder_local_auth`、1 条历史 `oauth_google`、1 条正常 `openai` API Key，启动应用确认零报错、零白屏、正常模型可用。
3. **能力中心 → Skills →「Qoder 市场」标签**：
   - 确认「Qoder 市场」选项与面板完整存在、无崩溃回归。

### 4.5 本地打包与 PR 规范
1. 重新打包并校验本地 macOS 应用（输出至独立目录以免干扰用户正在运行的旧实例，或先检查进程）：
   ```bash
   CSC_IDENTITY_AUTO_DISCOVERY=false pnpm --filter @peer-agent/desktop dist:mac
   pnpm --filter @peer-agent/desktop verify:packaged
   ```
2. 在本地 `codex/native-rust-cli` 提交干净后，**另建功能分支**（如 `refactor/retire-qoder-cli-and-gemini-oauth`）推送并创建指向 `codex/native-rust-cli` 的独立 PR（**不得直接 push `codex/native-rust-cli`**）。
