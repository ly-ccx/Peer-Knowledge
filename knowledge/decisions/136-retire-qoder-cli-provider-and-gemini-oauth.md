# ADR 136：下线 Qoder（本机 CLI）模型渠道与 Gemini OAuth 链路（核心瘦身）

创建时间：2026-11-25  
最后更新：2026-11-25（初版定案：全仓彻底移除 Qoder 本机 CLI 私有模型渠道与 Gemini OAuth / Google Code Assist 订阅链路，同时明确保留 Skills「Qoder 市场」与普通 Gemini API Key 渠道）  
状态：Accepted（2026-11-25 用户明确拍板瘦身范围与保留边界，交由 Codex 实施与全量验证，代码实施与发布验收另记）  
级别：A（支持的模型渠道与鉴权契约收窄、Rust Core 依赖与协议减负、遗留本机配置安全降级边界）  
关联：
- [ADR 133：全端统一 Rust Core 与双宿主融合终局架构](./133-unified-rust-core-and-dual-host-architecture.md)
- [ADR 48-provider：渠道模型选项与裁剪基线](./48-provider-model-options.md)
- [ADR 132（在途 PR #133）：MCP Vault v2 与原生 OAuth 边界](./00-adr-map.md)
- [实施设计规范：ADR 136 工程实施文档](../specifications/adr-136-implementation-design.md)

---

## 1. 背景与动机

在向 `v0.1.0` 正式版收敛过程中，两类重维护、低收益的历史模型接入通道正在显著拖累全栈代码体积、安全审计面、第三方依赖与跨端维护成本：

1. **Qoder（本机 CLI / `qoder-private` / `qoder_local_auth` / `local_cli`）**：
   - 依赖私有加密鉴权与逆向本地认证文件（在 Rust 侧额外引入 `aes`、`cbc`、`aes-gcm`、`hkdf`、`rsa`、`md-5` 6 个加密 crate 与 `inference-public.pem`；在 JS/TS 侧引入外部 npm 依赖 `@qoder-ai/qoder-agent-sdk`）；
   - 横跨 Rust `peer-runtime`、`peer-cli`、Electron Main、`packages/runtime-node`、`apps/tui`、Renderer 与 `packages/protocol/contracts/native-cli/qoder-*.json`，累计占用约 **3.7 万行代码与契约夹具**，并伴随大量私有错误码、慢队列轮询与专属重试逻辑。
2. **Gemini OAuth（`oauth_google` / Google 订阅登录 / Code Assist `cloudcode-pa.googleapis.com`）**：
   - 与标准 Gemini API Key（`generativelanguage.googleapis.com/v1beta`）分叉出独立的 OAuth 登录、刷新、`oauthProjectId` 包装请求体、Code Assist SSE 端点与配额查询链路；
   - 在 `packages/protocol/contracts/native-cli/model-wires.json`、`model-oauth.json`、Rust `model_oauth` / `wire/gemini.rs` / `subscription_quota.rs`、Electron Main、`credential-helper`、`apps/tui` 及设置界面中形成持续维护负担。

为此，决定对产品模型接入面执行一次彻底瘦身。

---

## 2. 核心决策：移除范围与强制保留边界

### 2.1 彻底移除（Delete Completely）
1. **Qoder（本机 CLI）模型渠道全链路**：
   - 渠道定义 `CHANNEL_IDS.QODER`（`qoder`）、`qoder-local` 接入卡片、线协议 `qoder-private`、鉴权方式 `qoder_local_auth` / `local_cli`；
   - Rust `crates/peer-runtime/src/qoder*`、`model/wire/qoder*`、`model/stream/qoder*`、`model/qoder_retry.rs`、`tests/qoder_formats.rs` 与 `crates/peer-cli/tests/native_qoder/*`，以及 `crates/peer-runtime/Cargo.toml` 中仅被 Qoder 使用的 6 个加密 crate（`aes`、`cbc`、`aes-gcm`、`hkdf`、`rsa`、`md-5`）；
   - Electron Main / `runtime-node` / `apps/tui` 中的全部 `qoder-local-auth`、`qoder-model-catalog`、`qoder-official-model-catalog`、`qoder-private-adapter`、`qoder-provider-expansion`、`qoder-private-provider` 模块及测试；
   - `@qoder-ai/qoder-agent-sdk` 外部 npm 依赖（根 `package.json`、`apps/desktop/package.json`、`packages/runtime-node/package.json`）；
   - Desktop Renderer 中 Qoder 模型品牌图标 `qoder.svg`、`LlmSettingsPanel` Qoder 连接向导、Qoder 积分/资源包额度展示、Qoder 10605 慢队列恢复文案与样式；
   - `packages/protocol/contracts/native-cli/qoder-*.json` 与 `scripts/native-cli/qoder-*.{ts,mjs}` 契约校验脚本。
2. **Gemini OAuth（`oauth_google` / Code Assist）全链路**：
   - `LlmAuthMethod` 中的 `oauth_google`、Google OAuth 登录流（`google-oauth.mjs`）、`credential-helper` 与 Rust `model_oauth` 中的 `oauth_google` 分支、`oauthProjectId` / `cloudcode-pa.googleapis.com` Code Assist 请求包装与 `v1internal:streamGenerateContent` 端点；
   - `provider-channels.mjs` / `model-channel-registry.json` 中 `google-ai` 的 `oauth_google` 鉴权方式与「Gemini OAuth」独立接入卡片；
   - `subscription-quota` / `account-usage-service` / Rust `subscription_quota.rs` 中针对 `oauth_google` / Gemini 订阅的额度查询分支；
   - Desktop Renderer 中「Gemini OAuth」登录入口、文案与相关单测；
   - `packages/protocol/contracts/native-cli/model-oauth-registry.json`、`model-oauth.json`、`model-binding.json`、`model-wires.json` 中的 `oauth_google` 契约项。

### 2.2 强制保留（DO NOT REMOVE — 零误伤红线）
1. **能力中心「Qoder 市场」（Online Skill Marketplace）完整保留**：
   - 该功能调用 `qoder.com` 公开 Skill 市场接口搜索和安装 Skill ZIP，与 Qoder 本机 CLI 模型渠道完全解耦；
   - 下列资产**严禁删除或破坏**：
     - `apps/desktop/renderer/src/capabilities/components/QoderMarketplacePanel.tsx`
     - `apps/desktop/renderer/src/capabilities/components/SkillsPanel.tsx`（`view === 'qoder'` 分支）
     - `apps/desktop/electron/main/qoder-marketplace-service.mjs` 及 `.test.mjs`
     - `apps/desktop/electron/main/ipc/register-skills-ipc.mjs` 及 `.test.mjs`
     - `apps/desktop/electron/ipc/channels.mjs` 中 `skills:qoder:*` 4 个频道
     - `apps/desktop/electron/preload/preload.source.cjs` / `preload.cjs` / `clientApi.ts` / `bootstrapPreloadApi.ts` 中 `queryQoderSkills` / `getQoderSkillDetail` / `installQoderSkill` / `listQoderTaxonomies`
     - `packages/protocol/src/skill-marketplace.ts` 中 `Qoder*` 类型
     - `packages/runtime-node/src/skill-store.mjs` 及 `crates/peer-store/src/skill_manage.rs` 中的 `qoder` 来源元数据兼容。
2. **普通 Gemini（API Key 模式）完整保留**：
   - `CHANNEL_IDS.GOOGLE_AI`（`google-ai`）、`defaultWire: 'gemini'`、`authMethods: { api_key: { wire: 'gemini' } }`、`https://generativelanguage.googleapis.com/v1beta`、官方 API Key 接入卡片、`gemini-adapter.mjs` / `gemini-encoder.mjs` / `gemini-model-catalog.mjs` / Rust `model/wire/gemini.rs` / `apps/tui/src/gemini-provider.ts` 的 API Key 路径完整保留且须全量测试通过。
3. **其余 OAuth 订阅通道完整保留**：
   - `oauth_chatgpt`（ChatGPT 订阅）与 `oauth_grok`（Grok OAuth）保持原样，不得受本次删减影响。

---

## 3. 遗留本机配置安全降级契约（向后兼容）

已有用户本机 `~/.peer-agent/llm-providers.json` 中可能仍留存历史上配置过的 `channelId: "qoder"`、`authMethod: "qoder_local_auth" | "local_cli"` 或 `authMethod: "oauth_google"` 条目。为避免升级后启动崩溃或模型配置读取失败，必须遵循以下降级契约：

1. **禁止 JSON 反序列化崩溃**：无论 Rust `model_config` 还是 Electron `llm-config-store` / `runtime-node/shared-model-config`，读取包含已退役渠道/鉴权方式的 `llm-providers.json` 时**严禁抛未捕获异常或清空整份配置文件**。
2. **明确隔离与优雅报错**：
   - 列表与路由投影层自动过滤已退役渠道/鉴权条目（或将其标记为不可用/禁用，禁止选为默认模型或新建同类连接），同时确保同一配置文件中其余正常模型（OpenAI / Anthropic / DeepSeek / Gemini API Key / ChatGPT OAuth 等）不受影响；
   - 若某历史会话或 Bot 显式绑定了已退役条目并尝试发请求，返回清晰可理解的受控错误码（如 `unsupported_provider` / `unsupported_auth_method`），引导用户切换至有效模型，绝不 panic。
3. **禁止在运行期触碰本机 `~/.qoder` 或发起 `cloudcode-pa.googleapis.com` 请求**。

---

## 4. 验收标准

1. **零残留校验**：除 §2.2 明确保留的 Skills「Qoder 市场」与 Gemini API Key 路径外，全仓源码、协议、依赖与构建产物中不再残留 Qoder 模型渠道与 Gemini OAuth 代码、配置入口或 UI 卡片。
2. **依赖瘦身**：`crates/peer-runtime/Cargo.toml` 移除不再使用的 6 个加密 crate；`package.json`、`apps/desktop/package.json`、`packages/runtime-node/package.json` 移除 `@qoder-ai/qoder-agent-sdk` 并同步更新锁文件。
3. **双端测试与实机验收**：
   - Rust `cargo test --workspace`（核心 crate）与 `cargo clippy --all-targets -- -D warnings` 全绿（零 `unsafe`）；
   - `packages/protocol`、`packages/credential-helper`、`packages/runtime-node`、`apps/desktop`（Electron Main + Renderer + Typecheck + Vite build）、`apps/tui` 全部相关单测通过；
   - 真实 Electron 设置页截图确认：「模型提供商」添加列表中不再出现「Qoder（本机 CLI）」与「Gemini OAuth」，「Google AI / Gemini（API Key）」「ChatGPT 订阅」「Grok」以及 Skills 页面「Qoder 市场」全部正常可用。
