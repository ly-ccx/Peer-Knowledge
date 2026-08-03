# Qoder 私有接口渠道说明（qoder-local / qoder-private）

创建时间：2026-08-03
最后更新：2026-08-03

## 1. 这个渠道是什么

「Qoder 私有接口」是 Peer Agent 的一条 LLM 服务渠道，代码侧标识：

- 渠道 ID：`qoder`
- 服务模板 ID：`qoder-local`（P0 清单中的名称，用户可见名为「Qoder 私有接口」）
- 接入分类：本地 / 私有
- 鉴权方式：`qoder_local_auth` / `local_cli`
- 通信协议（wire）：`qoder-private`（唯一允许的 wire）
- 默认推理地址：`https://api2-v2.qoder.sh/model/v1`，默认模型 `auto`

一句话定义：**它不是一个填 API Key 的公开服务，而是复用本机已安装的 Qoder CLI（qodercli）的登录态，走 Qoder 私有推理链路的渠道。**

也就是说：Peer Agent 不向用户要 Qoder 的密钥，而是把「安装并登录过 qodercli 的这台电脑」本身当作凭据来源——读取 qodercli 保存在本机的登录凭据（默认 `~/.qoder/.auth/`），并借用 qodercli 二进制内嵌的 auth wasm 模块对推理请求做签名/加密，然后直接请求 Qoder 的推理端点。

因此它不属于「官方 API Key」也不属于「OAuth 授权登录」模板分类，而是「本地 / 私有」分类：前提全部落在用户本机环境上。

## 2. 前提条件（使用这条渠道前必须满足）

这是本文档最重要的一节。没有满足前提，渠道在 UI 上会直接报错（错误码见第 5 节）。

### 2.1 必须安装 Qoder CLI（qodercli）

- 需要本机存在 `qodercli` 可执行文件（macOS 常见位置如 `~/.local/bin/qodercli`、`/opt/homebrew/bin/qodercli`、`/usr/local/bin/qodercli`，或在 PATH 中可用）。
- 为什么必须装：
  1. 登录凭据（token / userInfo）存在 qodercli 的配置目录里（默认 `~/.qoder`，可用 `QODER_CONFIG_DIR` / `QODER_CLI_HOME` 覆盖）；
  2. 推理请求的签名/加密逻辑不是 Peer Agent 自己实现的，而是运行时从 qodercli 二进制中提取内嵌的 auth wasm 来执行；找不到 qodercli 二进制就无法构造合法请求。

### 2.2 必须先用 qodercli 完成登录

- 在终端执行 qodercli 的登录流程（如 `qodercli` 自带的 login / 账号登录命令），完成账号登录。
- 登录成功后 qodercli 会在配置目录生成：
  - `~/.qoder/.auth/` 下的登录态（token、userInfo、过期时间）；
  - `~/.qoder/.auth/machine_id`（机器 ID，构造请求时需要）；
  - `~/.qoder/.models/<uid>/` 下的加密模型目录缓存（Peer Agent 用它解密得到可选模型列表）。
- 登录态有有效期：Peer Agent 读取时会校验 `expire_time`，已过期（含 60 秒内将过期）会报 `qoder_auth_expired`，需要重新登录。

### 2.3 （可选）用环境变量提供 token

如果不想依赖本机登录文件，也可以直接配置环境变量，优先级高于本地登录态：

- `QODER_ACCESS_TOKEN`
- `QODER_PERSONAL_ACCESS_TOKEN`
- `QODER_PAT`

但注意：即使提供了 token，推理请求仍需要 auth wasm 签名能力，因此「装 qodercli」这一前提不可绕过；环境变量只是替换「token 从哪里来」。

### 2.4 前提自查清单

1. 终端执行 `qodercli --version` 能找到命令（否则先安装 qodercli）；
2. 用 qodercli 登录过，且登录未过期（重新登录一次最稳妥）；
3. `~/.qoder/.auth/` 目录存在且非空；
4. 网络可达 `api2-v2.qoder.sh`。

四项都满足后再在 Peer Agent 中选择「Qoder 私有接口」渠道。

## 3. 工作原理（凭据链路）

按优先级：

1. **环境变量 token**：命中 `QODER_ACCESS_TOKEN` / `QODER_PERSONAL_ACCESS_TOKEN` / `QODER_PAT` 任一非空值即直接使用。
2. **本机 qodercli 登录态**：读取 `resolveQoderConfigDir()`（默认 `~/.qoder`）下的登录文件，解析 token 与 userInfo；校验 `expire_time`，过期抛 `qoder_auth_expired`。

构造推理请求时（`prepareQoderInferRequest`）：

- 读取 `~/.qoder/.auth/machine_id`；
- 要求 userInfo 存在（本地登录态路径必须带 userInfo，否则抛 `qoder_local_user_info_required`）；
- 加载 qodercli 内嵌 auth wasm（可用 `QODER_AUTH_WASM_BINARY` 显式指定 wasm 文件），由 wasm 生成 `encrypt_user_info`、`key` 等运行时鉴权字段；
- 由 wasm 完成请求体加密/签名，输出最终发往推理端点的请求；
- 端点可被覆盖（`resolveQoderInferenceEndpoint`），默认即渠道配置里的 `https://api2-v2.qoder.sh/model/v1`。

模型目录来源（`loadQoderModelCatalog`）：

1. 首选解密本机缓存：`~/.qoder/.models/<uid>/catalog*`（用 auth wasm 的 `modelCacheDecrypt` 解密），解析出模型列表（含上下文档位、推理能力等元数据）；
2. 缓存不可用/为空时回退内置的最小目录（当前为单个 `auto` 模型）；
3. 缓存文件不存在或不可读对应 `qoder_models_not_found` / `qoder_models_unavailable` 等错误——典型原因就是 qodercli 从未登录、未同步过模型。

代码位置（peer_agent 仓）：

- 渠道定义：`apps/desktop/electron/main/provider-channels.mjs`（`CHANNEL_IDS.QODER`，label `Qoder 私有接口`）
- 鉴权与请求构造：`packages/runtime-node/src/provider-adapters/qoder-local-auth.mjs`
- 模型目录：`packages/runtime-node/src/provider-adapters/qoder-model-catalog.mjs`
- 协议适配：`apps/desktop/electron/main/provider-adapters/qoder-private-adapter.mjs`
- UI 错误文案：`apps/desktop/renderer/src/app/components/LlmSettingsPanel.tsx`

## 4. 用户侧体验要求（产品设计口径）

- 渠道入口必须说明这是「依赖本机 Qoder CLI 登录态」的私有链路，不是公开 API；
- 添加/启用前展示前提条件（第 2 节），并在检测到缺失时给出对应引导：
  - 未装 qodercli → 引导安装；
  - 未登录/过期 → 引导打开终端登录 qodercli；
- 不要向用户索取任何 Qoder 密钥输入框（这不是 api_key 渠道）；
- 「本地/私有」分类文案只有在端点确实是 Qoder 私有时才准确，注意与 Ollama 这类真本地运行时区分表述。

## 5. 常见错误码与恢复方式

| 错误码 | 含义 | 用户该怎么做 |
|---|---|---|
| `qoder_auth_wasm_not_found` / `qoder_auth_wasm_missing` | 找不到本机 Qoder CLI（qodercli）或无法从中提取 auth wasm | 安装/更新 qodercli，或设置 `QODER_AUTH_WASM_BINARY` |
| `qoder_auth_not_found` / `qoder_auth_token_missing` | 未找到本机 Qoder 登录态 | 先用 qodercli 登录 |
| `qoder_auth_expired` | 本机登录态已过期 | 重新登录 qodercli |
| `qoder_auth_unavailable` | 无法读取本机登录文件（权限/损坏） | 检查 `~/.qoder/.auth/` 权限，重新登录 |
| `qoder_local_user_info_required` | 有 token 但缺 userInfo，无法构造请求 | 用 qodercli 完整登录一次 |
| `qoder_models_not_found` | 本机没有 Qoder 模型目录缓存 | 先登录 qodercli 并同步模型 |
| `qoder_models_unavailable` / `qoder_encrypted_models_unavailable` / `qoder_encrypted_models_empty` / `qoder_models_empty` | 模型缓存存在但不可用/为空 | 确认已登录 qodercli，或本机存在可用模型缓存 |
| `qoder_private_empty_response` | 推理端点返回空响应 | 检查网络/端点是否可达，稍后重试 |

## 6. 相关文档

- 产品主设计：`design/product/ai-service-provider-center.md`（连接流程章节「本地 / 私有路径（Qoder 私有接口）」）
- P0 冻结清单：`design/product/ai-service-provider-center-p0-freeze.md`（`qoder-local` 行）
- 模型选项归一化：`knowledge/decisions/48-provider-model-options.md`（Qoder 上下文档位 contextTier）
- 相关踩坑：`knowledge/experience/cli-desktop-model-binding-id-mismatch.md`（Qoder 组模型 ID 绑定）
