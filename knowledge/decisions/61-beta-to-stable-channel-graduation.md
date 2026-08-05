# 61. beta→stable 通道自动毕业决策

## Status

Accepted on 2026-08-03。设计决策已与产品方对齐，落地前仅作为决策记录；实现
待在 `peer_agent` 仓的主进程更新链路中补齐「auto 双通道检查 + 毕业判定」逻辑
（见 §Implementation Notes）。本知识库仅存知识，代码改动一律在代码仓落地。

- 创建时间：2026-08-03
- 最后更新：2026-08-03

## Context

### 现状（基于代码证据）

桌面端更新链路是「CI 分流 → 客户端通道解析 → electron-updater 读 yml」三段：

1. **CI 分流**（`release.yml`）：从 tag 名算通道。`v1.0.0` 无后缀 → stable，
   写 `latest-mac.yml` / `latest.yml`；`v1.0.0-beta.N` → beta，写
   `beta-mac.yml` / `beta.yml`。`generateUpdatesFilesForAllChannels: true`
   让 electron-builder 按版本后缀写对应通道清单。CLI 侧 npm dist-tag 同步
   分 `latest` / `beta`。
2. **客户端通道解析**（`auto-updater.mjs` `resolveUpdateChannel`）：
   偏好三选项 `auto` / `beta` / `stable`。`beta` / `stable` 直接返回；
   `auto` 回退版本号语义 ——
   `PRERELEASE_PATTERN = /-(beta|alpha|rc)\b/i` 命中则读 beta 通道，否则
   读 stable 通道。
3. **UI 入口**（`UpdatesPanel.tsx`）：设置面板「更新」分区有通道下拉框
   （auto / beta / stable），经 preload `updaterSetChannel` → IPC
   `updater:set-channel` → main `setChannelPreference` 落地偏好。

### 问题

当前 `auto` 的回退逻辑只看「当前安装版本号是否含预发布后缀」，**没有「beta
周期已结束就切走」的能力**。后果：

- 用户在 `1.0.0-beta.5`，偏好 `auto` → 一直读 `beta*.yml` → 正式版
  `1.0.0` 发布后，`beta*.yml` 仍指向 beta.5，**auto 用户看不到正式版**，
  不会自动毕业。
- 显式选 `beta` 的测试者被毕业反而是错的（违背显式选择）。

核心缺口：**`auto` 用户缺少「beta 结束后自动切 stable」的毕业机制**，且该
机制必须在客户端做（见 §Alternatives）。

## Decision

### 三选项分流语义

| 偏好 | 语义 | 行为 |
|---|---|---|
| `beta` | 明知是 beta 仍要待在 beta | 一直读 beta 通道，正式版发布也不动，直到下一个 beta 或手动切。**测试者预期。** |
| `stable` | 只要稳定版 | 一直读 stable 通道。 |
| `auto` | 不关心通道，要最合适的路径 | beta 期间跟 beta；对应正式版发布后自动毕业到 stable。 |

关键判断：**`beta` 用户的「不自动毕业」是对的**。显式选 beta 的人大概率是
测试者，选 beta 即想继续吃下一个 beta；正式版一发布就把他切走等于违背显式
选择，破坏信任。`auto` 用户的隐含契约正相反：「我懒得管，你看着办」，那么
beta 线结束后带他走完全符合预期。

### 毕业判定信号

> **auto 用户当前装的是 `x.y.z-beta.n`，当 stable 通道出现一个版本号严格
> 大于当前安装版本时，即视为该 beta 线已毕业，切到 stable。**

该定义天然处理所有边界：

- 用户 `1.0.0-beta.5`，stable 发 `1.0.0` → semver `1.0.0 > 1.0.0-beta.5`
  ✅ 毕业
- 用户 `1.1.0-beta.3`，stable 只有 `1.0.0` → `1.0.0 < 1.1.0-beta.3` ❌
  不毕业，继续读 beta，等 `1.1.0` stable 或下一个 beta
- stable 还没发 → stable 通道无可更新版本 → 继续 beta ✅

### 毕业的单向性

`auto` 用户毕业后从 `1.0.0-beta.5` 升到 `1.0.0` stable，之后版本号不再含
`-beta`，`resolveUpdateChannel` 的回退逻辑会自动把他留在 stable —— **毕业是
单向、一次性的，不会反复横跳**。这是好事，无需额外维护状态。副作用：毕业
后哪怕又有新的 `1.1.0-beta` 出来，auto 用户也不会回 beta，除非手动切。符合
`auto` 的「跟随稳定主线」语义。

### 为什么必须在客户端做，不能 CI 侧做

曾考虑「发正式版时往 `beta*.yml` 也写一条指向正式版」——**否决**。

`beta*.yml` 不区分读者是 `auto` 还是 `beta`。CI 把 stable 写进 beta yml，
显式选 `beta` 的测试者也会被毕业，违背他的选择。毕业逻辑**必须**在客户端，
由 `auto` 用户单独走一条「双通道检查」：先看 stable 有没有更新，有就读
stable；没有再回退 beta。

## Alternatives

| 方案 | 结论 | 理由 |
|---|---|---|
| CI 把 stable 写进 `beta*.yml` | ❌ 否决 | beta yml 不区分 auto/beta 读者，会误毕业显式 beta 测试者 |
| auto 用户毕业后手动切 stable | ❌ 否决 | 违背 auto 「不关心通道」的隐含契约，等于把 auto 退化成 beta |
| 客户端 auto 双通道检查 + 毕业判定 | ✅ 采纳 | 精准只对 auto 生效，beta 显式锁定，符合三选项语义 |

## Implementation Notes

本节为代码仓落地要点，知识库不存代码，仅记实现契约：

1. **改动落点**：`peer_agent` 仓 `apps/desktop/electron/main/auto-updater.mjs`
   的 `checkForUpdates` 检查链路。`resolveUpdateChannel` 的签名可不动。
2. **auto 双通道检查**：偏好为 `auto` 且当前版本含 `-beta` 时，一次检查里
   先查 stable 通道（`latest*.yml`），若存在严格大于当前版本 → 读 stable
   触发毕业更新；否则回退读 beta 通道（`beta*.yml`）。
3. **不碰 beta / stable 偏好**：这两个显式锁定，永远只读单通道。
4. **毕业后无状态维护**：升级到 stable 版本号后，版本号不含 `-beta`，
   `resolveUpdateChannel` 回退自动留在 stable，无需持久化「已毕业」标志。
5. **版本号契约不变**：`publish.sh stable` 取 `VERSION` 文件，`beta` 在其
   上加 `-beta.N`，保证正式版号严格大于 beta 号。不得手工打低于 beta
   基线的正式 tag。

## Consequences

- **正面**：auto 用户「beta 结束自动转正」符合直觉；beta 测试者不被打扰；
  stable 用户无感。三选项语义清晰无歧义。
- **负面**：auto 毕业后不会自动回 beta（需手动切）。判定依赖 semver 严格
  比较，要求版本号纪律。
- **风险**：若发版流程打出低于 beta 基线的正式 tag，毕业判定会误判不毕业。
  由 §Implementation Notes 第 5 条版本号契约约束。
