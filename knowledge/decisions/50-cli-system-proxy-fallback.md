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
