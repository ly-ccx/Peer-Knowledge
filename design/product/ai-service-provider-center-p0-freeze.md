# AI 服务商中心 P0 范围冻结

> 创建时间：2026-08-03
> 最后更新：2026-08-03
> 文档状态：Active（实施中）
> 关联产品文档：`design/product/ai-service-provider-center.md`
> 关联代码仓：`/Users/liangyin/Documents/DEV/github/peer_agent`

## 1. P0 目标

把当前 `LlmSettingsPanel` 单面板 Provider 配置，升级为完整 AI 服务接入闭环：

```text
服务商中心 → 添加服务 → 连接配置 → 服务详情 → 模型中心 → 聊天选择器
```

不以“支持多少 Logo”为目标，而以三条主链路完成度为目标。

## 2. P0 必做

1. 产品概念落地：Service Template / Service Connection / Model Instance
2. 设置导航拆分：`服务商` + `模型`
3. 服务商中心：已连接服务卡片、分组、状态、空状态
4. 添加服务目录：按接入方式分类、搜索、支持级别
5. 三条连接路径：
   - 官方 API Key
   - 授权登录（现有 OAuth）
   - 自定义兼容
6. 服务详情：概览 / 模型 / 连接 / 诊断
7. 阶段化连接测试 + 错误分类
8. 模型同步、手动添加、启用/停用、全局默认
9. 状态体系：配置中 / 检查中 / 可用 / 部分可用 / 需要操作 / 不可用 / 已停用
10. 聊天空状态与模型选择器闭环
11. 旧配置无损迁移
12. 密钥脱敏与诊断脱敏

## 3. P0 不做

- 云平台专属流程（Azure / Bedrock / Vertex）完整适配
- 本地运行时自动发现（Ollama / LM Studio）
- 全局健康检查独立页
- 跨服务成本统计
- 多默认模型策略 / 自动路由
- Provider 插件市场
- 把所有预设渠道 Logo 一次性做满原生适配

## 4. 首批服务模板映射（基于现有 channel）

| 服务模板 ID | 用户可见名称 | 接入分类 | 支持级别 | 现有 channelId | authMethod | 备注 |
|---|---|---|---|---|---|---|
| `openai-api` | OpenAI | 官方 API | 原生适配 | `openai` | `api_key` | 默认地址隐藏 |
| `openai-chatgpt` | ChatGPT 订阅 / Codex 账号 | 授权登录 | 原生适配 | `openai` | `oauth_chatgpt` | 订阅登录路径 |
| `anthropic-api` | Anthropic | 官方 API | 原生适配 | `anthropic` | `api_key` | 默认地址隐藏 |
| `google-ai-api` | Google AI / Gemini | 官方 API | 验证兼容 | `google-ai` | `api_key` | 复用现有 Gemini API |
| `google-oauth` | Gemini OAuth | 授权登录 | 验证兼容 | `google-ai` | `oauth_google` | 授权登录路径 |
| `grok-oauth` | Grok 官方 | 授权登录 | 验证兼容 | `grok` | `oauth_grok` | 授权登录路径 |
| `qoder-local` | Qoder 私有接口 | 本地 / 私有 | 验证兼容 | `qoder` | `qoder_local_auth` / `local_cli` | 复用本机 qodercli 登录态走 Qoder 私有推理链路；前提：本机已安装 qodercli 且已登录（见下方说明） |
| `openai-compatible` | OpenAI 兼容 | 自定义兼容 | 自定义兼容 | `openai-compatible` | `api_key` | 允许地址/协议/手动模型 |
| `anthropic-compatible` | Anthropic 兼容 | 自定义兼容 | 自定义兼容 | `anthropic-compatible` | `api_key` | 允许地址/协议/手动模型 |

说明：

- 同一 channel 可对应多个服务模板（例如 OpenAI API Key 与 ChatGPT 订阅）。
- 服务连接是用户真正管理的对象；模板只负责发现和默认配置。
- DeepSeek / 国内套餐等未列入 P0 原生适配清单，用户可通过“OpenAI 兼容 / Anthropic 兼容”接入。

`qoder-local`（Qoder 私有接口）前提条件说明：

- 该渠道不是填 API Key 的公开服务，而是复用本机 Qoder CLI（qodercli）的登录态，请求发往 Qoder 私有推理端点（默认 `https://api2-v2.qoder.sh/model/v1`）。
- 前提一：本机必须已安装 qodercli——Peer 需要从 qodercli 提取登录凭据与请求签名能力（内嵌 auth wasm），缺了它渠道完全不可用。
- 前提二：必须先用 qodercli 完成登录，且登录态未过期——凭据保存在 `~/.qoder/.auth/`；未登录或过期会分别报「未找到本机 Qoder 登录态」「登录已过期」类错误，恢复方式都是重新登录 qodercli。
- 可选：配置 `QODER_ACCESS_TOKEN` / `QODER_PERSONAL_ACCESS_TOKEN` / `QODER_PAT` 环境变量可替代本机登录文件提供 token，但不能替代安装 qodercli。
- 完整说明（凭据链路、模型目录来源、错误码表）见 `knowledge/architecture/qoder-private-channel.md`；产品连接流程见 `design/product/ai-service-provider-center.md` 8.8 节。

## 5. 三条 P0 主链路验收口径

### 5.1 官方 API Key

```text
添加服务 → 选 OpenAI/Anthropic
→ 只填 API Key（名称可改）
→ 测试连接（配置/网络/认证/模型/最小请求）
→ 启用模型并设默认
→ 返回聊天可用
```

### 5.2 授权登录

```text
添加服务 → 选 ChatGPT/Gemini/Grok
→ 浏览器或本机授权
→ 显示账号/套餐摘要（若有）
→ 模型可用
→ 过期后可重新登录
```

### 5.3 自定义兼容

```text
添加服务 → OpenAI/Anthropic 兼容
→ 填名称、地址、Key
→ 同步模型或手动添加模型 ID
→ 最小请求验证
→ 明确“不保证完整兼容”
```

## 6. 代码落点（目标仓）

| 层 | 主要落点 |
|---|---|
| 协议 | `packages/protocol/src/index.ts` |
| 通道/模板 | `apps/desktop/electron/main/provider-channels.mjs` |
| 连通诊断 | `apps/desktop/electron/main/provider-connectivity.mjs` |
| 配置存储 | `apps/desktop/electron/main/llm-config-store.mjs` |
| 设置导航 | `apps/desktop/renderer/src/app/components/SettingsPage.tsx` |
| 服务商 UI | `apps/desktop/renderer/src/app/components/` 新组件，逐步替换 `LlmSettingsPanel.tsx` |
| 模型 UI | 设置“模型”分区 + 现有模型能力复用 |
| 聊天闭环 | 聊天空状态 / 模型选择器相关组件 |

## 7. 兼容策略

- 不破坏现有 `llm-providers.json` 可读性；优先增量迁移。
- 旧 provider config 映射为 Service Connection 语义，底层字段尽量复用。
- UI 改名不强制改底层 channelId。
- 旧设置入口 `model` 若仍保留，P0 中拆成 `providers` + `models`；旧 deep-link 可回退。

## 8. 完成定义（与实施计划一致）

- 设置导航有“服务商”
- UI 有“添加服务”
- 协议/实现出现 `connectionState` / `errorCategory` / `stages`
- 相关设置与 provider 测试通过
- 手动走通三条连接路径与模型中心闭环
