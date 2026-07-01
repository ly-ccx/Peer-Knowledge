# 45. MCP OAuth 配置交互简化：探测即自动配置 + 回调地址只读 + 授权端点自动发现

## Status

Design agreed on 2026-07-01（本文档为设计决策记录，代码改动尚未落地）。

改动范围属渲染层 MCP 设置面板交互，**后端零改动**（关键结论见下）。代码改动一律在
`peer_agent` 仓，本知识库仅作可追溯记录。

- 创建时间：2026-07-01
- 最后更新：2026-07-01
- 关联决策：`knowledge/decisions/32-mcp-authentication.md`、`knowledge/decisions/31-mcp-connection-management.md`
- 目标改动文件：`apps/desktop/renderer/src/app/components/McpSettingsPanel.tsx`

## Context

### 触发问题（用户实测吐槽）

用户在 MCP 设置面板连接一个需要认证的服务器（`o2`，`https://mcp.alibaba-inc.com/o2/mcp`）时，
遇到两个反直觉的交互：

1. **"检测到了却不帮配"**：顶部 banner 已明确提示"已检测到该 MCP 需要身份验证……请展开
   高级设置将认证方式配置为 OAuth 2.0 后再点击'登录授权'"，AUTH 卡片也显示"需要认证（请
   配置 OAuth）"——系统已经知道该用 OAuth，却仍要求用户**手动展开高级设置、手动把认证
   方式改成 OAuth 2.0**，把系统已知的结论甩回给用户重填一遍。

2. **"让用户填本不该填的字段"**：OAuth 配置区要求用户**手填回调地址（redirect URI）**，
   甚至强制必填**授权服务器地址（Authorization Server URL）**。这两者对普通用户是纯实现
   细节，既不知道填什么、填错还会静默失败。

### 代码证据（验证阶段结论）

在 `peer_agent` 仓核对后端 OAuth 链路，得到一个**决定性且优于预期**的结论：

**后端 OAuth 早已是全自动 discovery，前端强制必填的 `authorizationServerUrl` 后端根本不消费。**

- `startMcpOAuth`（`apps/desktop/electron/main/mcp-client.mjs:477`）最终调用
  `auth(provider, { serverUrl: config.url })`——即用 **MCP 服务器 URL** 去自动发现授权
  服务器，走 MCP Authorization 规范的 `.well-known` discovery + 动态注册（DCR）。代码
  注释原文："auth() 会按 MCP Authorization 规范发现授权服务器 / 受保护资源元数据，
  必要时执行动态注册"。
- `createOAuthProvider`（`mcp-client.mjs:137-210`）组装 provider 时只读取
  `redirectUrl / scopes / clientId / clientSecret / clientInformation / codeVerifier /
  tokens / discoveryState`——**通篇未读 `authorizationServerUrl`**。
- `authorizationServerUrl` 在 `mcp-credential-store.mjs` 仅被存储/透传，从未参与 OAuth 流程。
- `discoveryState / saveDiscoveryState` 已完整实现（`mcp-client.mjs:186-202`），discovery
  结果会被持久化缓存。
- 回调地址后端有默认常量兜底（`DEFAULT_OAUTH_REDIRECT_URL`）；`main.mjs:137-138` 自动
  注入 `openAuthorizationUrl = shell.openExternal`，即一键拉起系统浏览器。
- `main.mjs:1800+` 的 `mcp:start-oauth` handler 已实现完整一键链路：挂起 loopback 回调
  监听 → 触发授权发现并开浏览器 → 等 code → `finishMcpOAuth` 换 token → 重新探测持久化。

**修正一处早期误判**：探测结果 `authRequiredProbe`（`mcp-client.mjs:369`）实际只返回
`{ type: 'oauth', message }`，并未真的填 `authorizationUrl`。因此"回填授权地址"这条既不
成立也不需要——后端压根不需要该地址。这让方案 C 的工作量塌缩成"前端别再逼用户填一个
后端用不到的字段"。

## Decision

三项改动全部集中在前端 `McpSettingsPanel.tsx`，后端零改动。

### 改动 1（A）— 回调地址只读化

- Redirect URL 输入框 → 只读展示 + 复制按钮。
- 文案："回调地址（应用固定，如认证服务器要求登记请复制加白名单）"。
- 提交时不再传用户可编辑的 `redirectUrl`，留空交后端默认常量兜底。

### 改动 2（B）— 探测到 OAuth 自动预填（交互取"保留确认步骤"版）

- 探测结果 `auth.type === 'oauth'` 时，自动 `setAuthMode('oauth2')` 并展开高级设置。
- "进行身份验证"按钮点击后：**只切到 OAuth 模式并展开设置**，用户再自行点"登录授权"
  完成登录（保留一次用户确认，不做无停顿的一键直连）。
- banner 文案改为："已检测到需 OAuth，已自动切换为 OAuth 2.0，请点击'登录授权'完成登录"。

### 改动 3（C）— 去掉授权端点强制必填

- 删除 `authorizationServerUrl` 空值抛错的强校验。
- Authorization Server URL 降级为可选/高级项，标注"通常留空自动发现，仅自动发现失败时手动填"。
- 为空则不提交，交后端 SDK discovery。

## Consequences

- 用户在最常见路径下（服务器支持标准 discovery + DCR）**只需点两下**：进行身份验证 →
  登录授权，无需理解任何 OAuth 实现细节。
- 手动填 `authorizationServerUrl` 从"强制"降级为"逃生阀"，仅在自动发现失败时使用。
- 回调地址不再可被用户改坏，消除一类隐性失败。
- 后端零改动 = 回归风险集中在渲染层单文件，验证面收敛。

## 验证方式

- 前端 `apps/desktop` 跑 tsc / lint。
- 有条件时用 `o2` 服务实测完整链路：探测 → 自动切 OAuth → 点登录授权 → 浏览器授权 → 回调 → 工具可见。
