# 50. CLI 系统代理回退（macOS）

创建时间: 2026-07-22  
最后更新: 2026-07-22（代码已落地：`apps/tui` 新增 macOS 系统代理读取 + env 回退，bun test 17 pass / tsc EXIT=0）

## 状态

**Accepted（代码已落地）**。

macOS 上即使终端未 `export HTTPS_PROXY`，CLI 也会自动读取系统代理设置；设了环境变量则以环境变量为准；Windows/Linux 维持原有 env-only 行为不变。

## 背景

CLI（`apps/tui`）与 Desktop（`apps/desktop`）的代理来源本来不一致：

| 能力 | Desktop | CLI/TUI（落地前） |
|---|---|---|
| 环境变量代理（`HTTPS_PROXY` 等） | ✅ | ✅ |
| 系统代理（OS / PAC） | ✅ | ❌ |
| 运行时 | Electron（有 Chromium 网络栈） | 纯 Node/Bun |

- Desktop 靠 Electron `session.defaultSession.resolveProxy` + `net.fetch` 天然吃到系统代理（见 `apps/desktop/electron/main/provider-transports/recovering-fetch.mjs`）。
- CLI 侧 `apps/tui/src/provider-transport.ts` 的 `proxyForUrl(url, env)` **只读环境变量**，没有系统代理来源。
- 后果：用户在系统设置里开了代理（Clash/Surge 等），但终端没 `export HTTPS_PROXY` 时，CLI 直连——常表现为「Desktop 能连、CLI 连不上」。

CLI 没有 Electron session，用不了 `resolveProxy` 那套。需要一条独立的、轻量的系统代理读取路径。

## 决策

**给 CLI 增加 macOS 系统代理读取，作为环境变量之后的回退来源；不引入 Electron/Chromium 依赖。**

优先级（每种协议按顺序取第一个非空值）：

```
NO_PROXY bypass（最先判断）
  → 协议专属 env（HTTPS_PROXY / HTTP_PROXY）
  → ALL_PROXY
  → 系统代理（macOS scutil）
```

明确 **不** 做：

- 不接 PAC（自动代理脚本）与 SOCKS——TUI transport 只走 HTTP(S) 代理 URL，PAC/SOCKS 故意忽略。
- 不引入 Electron `net`/`session` 或 Chromium 网络栈到 CLI。
- 不改变环境变量优先与 `NO_PROXY` 语义：系统代理只是**兜底**，不是覆盖。
- 阶段一**仅覆盖 macOS**（对齐现有 macOS-only 的 CA 集成风格）；Windows/Linux 继续 env-only。

## 实现锚点（peer_agent）

| 组件 | 变更 |
|---|---|
| `apps/tui/src/macos-system-proxy.ts` | **新增**模块。`parseSystemProxyConfig(output)` 纯函数解析 `scutil --proxy` 输出为 `{ http?, https? }`（只取显式启用项）；`readMacosSystemProxy({ platform, runCommand })` 命令与平台**可注入**，非 darwin 或任何失败返回空配置。风格对齐 `macos-trusted-certificates.ts`（`execFileSync` + 纯函数可测） |
| `apps/tui/src/provider-transport.ts` | `proxyForUrl(url, env, systemProxy)` 增加系统代理作为**最后回退**，`NO_PROXY` bypass 仍最先判断；`createTuiProviderFetch` 启动时解析一次系统代理并注入，`options.systemProxy` 可注入便于测试 |
| `apps/tui/src/macos-system-proxy.test.ts` | **新增**。多种 scutil 输出 / 未启用 / 无 host / 无端口 / 非 darwin 不执行命令 / 命令抛错回退 |
| `apps/tui/src/provider-transport.test.ts` | 补：env 优先、`NO_PROXY` 命中系统代理仍 bypass、注入系统代理经 `createTuiProviderFetch` 生效 |

## 边界（仍在）

1. **环境变量优先**：显式 `HTTPS_PROXY`/`HTTP_PROXY`/`ALL_PROXY` 始终压过系统代理。
2. **`NO_PROXY` 规则不变**：命中即 bypass，系统代理也不例外。
3. **仅 HTTP(S) 代理 URL**：PAC/SOCKS 不解析。
4. **仅 macOS**：其他平台无系统代理来源，退回 env-only。
5. **失败静默兜底**：`scutil` 不存在/报错/非 darwin 一律当作「无系统代理」，绝不因读取失败而阻断请求。

## 架构影响

改动落在 TUI transport 适配器内部，代理路由仍集中在 `provider-transport.ts` 这一个 seam，没有新增绕过 Runtime Projection 的执行路径，符合「本地负责能力」的分层约束（B 级）。

## 后果

- 正面：macOS CLI 与 Desktop 代理体验对齐；无需手动 `export`；env-only 场景零行为变化。
- 成本：每次启动 CLI 多一次 `scutil --proxy` 子进程调用（macOS，一次性）。
- 待办：Windows（`netsh`/注册表）、Linux（多为 env-only，桌面环境代理来源分散）暂未覆盖，若有需求再单独评估。

## 验证

- `bun test`：**17 pass / 0 fail**（含新增 `macos-system-proxy.test.ts` 与 `provider-transport.test.ts` 回退用例）。
- `tsc -p tsconfig.json --noEmit`：**EXIT=0**。
- 手动：macOS 系统代理开启、终端无 `HTTPS_PROXY` 时 CLI 走系统代理；`export HTTPS_PROXY` 后以 env 为准；`NO_PROXY` 命中仍直连。

## 原生迁移实施约束（2026-11-16，接线前复核）

沿 ADR129/130/131 和实际 `provider-transport.ts` 迁移模型网络 Adapter。B级实施，环境优先、NO_PROXY、能力授权和Evidence边界不变；旧文“启动时只读一次系统代理”由当前实现的逐请求重读取代，避免VPN/代理切换后继续使用旧连接。每次物理请求仍是一次发送；网络配置迁移不增加模型/工具、授权码或refresh的自动重放。

- 模型生成、同请求count以及ChatGPT/Google账号交换/刷新共用一个原生网络Module。环境取构造时的快照；协议专属大写/小写、ALL_PROXY、NO_PROXY与显式PEER_EXTRA_CA_CERTS/NODE_EXTRA_CA_CERTS优先级对照实际TS。NO_PROXY普通host是精确匹配，点/星点前缀才允许子域，端口与全量星号规则保留。不借reqwest默认代理规则替代既有选择。
- macOS继续只读固定scutil HTTP(S)开关；非macOS不查询系统代理。系统查询失败/超限/超时视为无回退；取消停止查询且不能继续直连。固定OS命令有输出、时间和进程清理边界，不接收模型argv，不成为新的工具执行入口。逐请求选择route且不复用旧代理连接；失败不能默默换成直连并重复请求。
- Rustls的内置公共根证书和主机名/TLS验证继续开启。显式extra CA只扩展信任，不替换内置根，不使用accept-invalid。显式路径必须可读取、有界普通文件；错误明确阻断，修复后可以按原任务身份重新准入，不改源配置或凭据。
- macOS额外根保持当前CLI语义：只从user/admin Trust Settings中的非拒绝指纹选择公开证书，未配置/拒绝/损坏项不被当成新增根；OS查询失败保留内置根，不关闭TLS验证。查询只导出公开信任元数据/证书，不读取私钥或模型Vault。临时文件归该查询所有并清理。
- Proxy URL/鉴权值不进入错误详情、终端、Context、Evidence或性能trace；协议仅接受HTTP(S)，未知代理方案拒绝。CA、XML/PEM、代理文本与OS输出都受ADR130有界准入；不以安全默认值掩盖显式坏配置。

验收绑定真实TS路由/NO_PROXY/scutil/CA选择fixtures与原生公开CLI，覆盖实际HTTP代理、HTTPS/自签CA、错误证书/主机名/非法文件、取消和后续同任务准入，以及count/send和模型OAuth单次交换。无Node/Bun运行验证单列。MCP普通transport和MCP OAuth的网络/地址政策另沿ADR31/132迁移；本段不允许借代理绕过OAuth受限DNS/私网/redirect政策，也不把模型网络切片记成完整P4。
