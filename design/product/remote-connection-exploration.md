# 远程连接方案探索（Peer Agent）

> 创建时间：2026-08-12
> 最后更新：2026-08-12

## 1. 背景与问题定义

Peer Agent 的能力在本地（Electron 桌面端 + runtime-gateway + capability provider 链），人在外面（手机、通勤、会议室）时无法查看任务进度、发起任务或审批敏感操作。

本文先定义"远程连接"的边界，避免概念漂移：

- **要做**：远程驱动本地 agent——远端入口（IM / Web / 手机）发出意图，本地执行能力，证据回流远端。
- **不做**：远程桌面（RustDesk / ToDesk 类屏幕流）；不新增隐藏的远程控制通道（违反 ADR 15 的安全姿态）。

参考项目：**cc-connect**（chenhg5/cc-connect，Go，14.9k star，2026-08 仍在活跃更新）。它解决的问题与本文目标同构：把跑在电脑上的本地 AI 编码 agent（Claude Code / Cursor / Gemini CLI / Codex 等）桥接到 IM 平台，实现"无公网 IP 的远程操控"。

## 2. cc-connect 调研结论（基于 main 分支 README 与 docs）

### 2.1 定位与形态

- 本地 daemon 管理 agent 会话；Engine 负责消息路由与会话状态；各平台适配器负责收发。
- 支持的平台：飞书/Lark、钉钉、Telegram、Slack、Discord、LINE、微博私信、Matrix、企业微信等，另提供可选 Web UI。

### 2.2 关键机制：出站拨号，平台即中继

"无需公网 IP"不是 NAT 穿透，而是**所有流量由本地 daemon 主动外连（dial-out）**：

- 飞书 Bot 走 WebSocket 长连接；Telegram 走 getUpdates 长轮询；
- IM 服务器本身充当了中继与身份源，本地零入站端口、零公网暴露。

cloud_web（CWIP v1）平台把自托管网关也做成"一等公民"，三种传输模式：

| transport | 本地角色 | 适用场景 |
|---|---|---|
| `websocket` | WebSocket 客户端主动拨号 | 实时双向，默认首选 |
| `long_poll` | HTTP 客户端阻塞轮询 | 防火墙最友好 |
| `gateway` | HTTP webhook 服务端 | 网关主动推送 |

### 2.3 BridgeProtocol：语言无关的适配器协议

内置 BridgePlatform 暴露 `ws://host:port/bridge/ws`，适配器可用任意语言在运行时接入，无需改 Go 源码：

- 认证：`?token=` / `Authorization: Bearer` / `X-Bridge-Token`，未认证返回 401；
- 语义：消息转换为 core.Platform 调用，Engine 回复经同一 WebSocket 推回；
- 覆盖会话生命周期、文本/图片/文件/卡片/按钮/typing 等能力协商。

### 2.4 安全与隔离

- token 认证、按 project 隔离会话、workspace 隔离（近期 commit 包含 feishu topic workspace isolation）。
- 局限：授权模型主要是"IM 身份 + 白名单"，粒度粗于 peer_agent 的逐操作授权与证据链体系。

### 2.5 局限与代价

- 依赖第三方 IM：限流、消息格式约束、富媒体损失、对话摘要经过第三方服务器；
- 会话状态与桌面端并发的同步是自研复杂度；
- 消息式 UI 表达力弱：长输出、任务卡片、证据面板都难以在 IM 里呈现。

## 3. peer_agent 现状与约束盘点

### 3.1 已有资产（可直接复用）

- **runtime-gateway 已是出站拨号客户端**：`event-protocol.mjs` 定义了 `client.hello` / `client_tool_call.request` 等事件协议，路径 `/api/client/runtime/ws`（可用 `PEER_AGENT_RUNTIME_GATEWAY_WS_PATH` 覆盖），协议版本号 1。这与 cc-connect 的 dial-out 模式**天然同构**——"拨号骨架"已有，缺的是中继端、远端入口和远程授权流。
- capability provider 链已规约化：shell / file / browser / goal / automation / mcp / skill 等本地能力全部走 provider 分发，远程只是新增一个"界面入口"，不需要新开特权通道。
- 证据体系：tool-result / artifact / 权限审查（permission-review）已存在，远程操作可以原样产出证据并回流。

### 3.2 既有约束（必须延续的安全姿态）

- **ADR 31**：远程入站 HTTP/SSE MCP 默认禁用——远程连接必须延续"出站优先、入站默认禁"。
- **ADR 15**：不允许出现隐藏的远程控制通道——远程功能必须显式配对、显式授权、全程留痕。
- 架构基线五原则：模型认知 / 本地能力 / 界面表达 / 契约边界 / 证据治理——远程通道不能破坏这个分离，远端只是新界面。
- opencode 式 client/server 分离 + `/tui` 端点远程驱动（见 `tui-and-hook-design-standard.md`）可作近程参考，但不是跨网远程方案。

## 4. 方案对比

| 维度 | A. IM 桥接（cc-connect 路线） | B. 自建中继 + 富客户端（CWIP 路线） | C. P2P / 组网直连 |
|---|---|---|---|
| 传输 | 本地出站连 IM Bot API | 本地出站 WS 连自家 relay | WireGuard / Tailscale / QUIC 打洞 |
| 公网/运维成本 | 零 | relay 需部署与维护 | 需辅助节点，打洞不稳定 |
| 客户端 | 复用 IM 现成移动端 | 自研 Web/手机端（任务卡片、证据面板） | 自研 + 组网配置 |
| 身份与授权 | 依赖 IM 账号体系 + 白名单 | 完全自控（配对 token + 设备指纹） | 自控 |
| 表达力 | 弱（消息粒度、富媒体受限） | 强 | 强 |
| 隐私 | 摘要经过第三方 IM | 全链路自控 | 全链路自控 |

**推荐路线：A 起步、B 收敛、C 暂缓。**

- **A 是 MVP**：零公网、零运维、最快验证"人在外面驱动本地 agent"的体验闭环；飞书或 Telegram 二选一先做。
- **B 是长期方向**：与 A 共享同一套 remote-session 事件协议，只是换传输和入口；有了 relay 后 IM 可以退化为通知渠道，Web/手机端承担富交互。
- **C 暂缓**：移动端打洞体验差、复杂度高，收益边际递减。

## 5. 关键设计决策（若落地必须遵守）

1. **远程只是新界面**：远端消息 → 规范化能力事件 → 走现有 capability provider 链执行。远程通道不持有任何高于桌面端的权限。
2. **契约先行**：先定义 remote-session 事件协议（对齐 cc-connect bridge-protocol 的形态）：register/ack、消息类型、能力调用、结果与证据回执、心跳与重连。
3. **证据治理不变**：每次远程操作产出与桌面端同源的 Evidence artifact，回执给远端，桌面端可完整审计。
4. **权限分级**：只读类（查任务/进度/证据）默认放行；写/执行类默认要求配对设备确认，或一次性白名单授权。
5. **安全基线**：出站-only；一次性配对 token + 设备指纹绑定；会话按 workspace 隔离；密钥与 token 不进日志、不回传全文。
6. **多端一致性**：远端会话与桌面端 goal runner 共用同一份任务/证据存储，避免双状态源。

## 6. 分阶段落地（可验收步骤）

- **M0 调研验证**：本地跑通 cc-connect（飞书或 Telegram 任选），记录交互体验、平台限制、可复用的协议件。
  验收：demo 记录 + 结论文档（哪些件可直接借、哪些必须自研）。
- **M1 最小远程通道**：peer_agent 内新增 remote-connector（出站 WS 客户端，复用 `toWebSocketUrl` / 事件协议骨架），对接 cc-connect BridgePlatform 或自建 cloud_web 网关；远端一条消息 → 一次只读能力调用（如任务状态查询）→ 文本回执。
  验收：手机发消息能收到本地 agent 的实时状态回执；证据 artifact 落盘；端到端消息回执测试通过。
- **M2 会话与写操作**：会话状态机、多轮上下文；写操作授权确认流（远端申请 → 桌面端确认或一次性放行）。
  验收：远程可完整驱动一个受限任务并全程留痕；授权流测试用例通过。
- **M3 自有中继 + 富客户端**：自建 relay（复用 CWIP 式协议）、Web/手机端展示任务卡片与证据面板；IM 降级为通知渠道。
  验收：脱离 IM 完成远程控制；relay 集成测试通过。

## 7. 风险与开放问题

- **安全**：token 泄露/重放、IM 账号被盗即等于拿到本地控制权 → 设备指纹绑定 + 敏感操作二次确认。
- **平台稳定性**：飞书消息频控、长连接断线重连策略。
- **隐私**：对话与文件摘要经过第三方 IM → 默认只回执摘要，不回传全文/密钥。
- **本地行为**：mac 休眠/锁屏后的 daemon 行为、多端并发冲突。
- **范围外**：多机互连（A 机控制 B 机）、远程桌面，本期不做。

## 8. 参考资料

- cc-connect 仓库：https://github.com/chenhg5/cc-connect
  - docs/bridge-protocol.zh-CN.md（Bridge 平台协议规范，v1.0-draft）
  - docs/cloud-web.md（CWIP v1，三种传输模式）
- peer_agent 代码仓：
  - AGENTS.md（架构基线五原则）
  - apps/desktop/electron/main/runtime-gateway/event-protocol.mjs（出站 WS 事件协议）
- 本知识库：ADR 15（plugin-skill-mcp-system，禁止隐藏远程控制通道）、ADR 31（mcp-connection-management，远程入站默认禁用）、specifications/tui-and-hook-design-standard.md（opencode 式远程驱动参考）
