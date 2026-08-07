# Peer Agent 自有 Skill 市场

创建时间：2026-08-06
最后更新：2026-08-06

> 状态：已采纳
> 适用范围：Peer Agent Skill Catalog、Desktop、发布流程与本地 Skill Store

## 目标

Peer Agent 建设自有 Skill 市场。可以借鉴外部项目的采集和静态索引思路，但市场目录、审核状态、安装包、校验和、发布节奏和客户端安装链均由 Peer Agent 控制。

`anbeime/skill` 不是运行时依赖、构建依赖、发布依赖或默认数据源。

## 所有权

| 对象 | 唯一事实源 | 所有者 |
|---|---|---|
| 来源清单 | `peer_agent/marketplace/sources.json` | Peer Agent |
| 审核结果 | `peer_agent/marketplace/reviews.json` | Peer Agent |
| Catalog 协议 | `@peer-agent/protocol` 的 `skill-marketplace.ts` | Peer Agent |
| 静态目录 | `peer_agent/marketplace/dist/catalog.json` | Peer Agent 构建流程 |
| 安装包和 SHA-256 | `peer_agent/marketplace/dist/artifacts/` | Peer Agent 构建流程 |
| 本地安装状态 | `Skill Store` | Desktop 主进程 |
| 当前工作空间是否可用 | workspace mount | Desktop 主进程 |

客户端不以外部网页、README 或第三方目录作为安装真相。

## 目录生成链

```text
sources.json
  -> Source Adapter
    -> SKILL.md discovery
      -> normalize and validate
        -> stable catalogId deduplication
          -> reviews.json admission
            -> deterministic ZIP
              -> size + SHA-256
                -> atomic catalog publish
```

支持的来源适配器：

1. `local-directory`：仓库内由 Peer Agent 直接维护的 Skill。
2. `github-directory`：Peer Agent 明确登记的 GitHub 仓库、revision 和目录。

GitHub 来源必须经过 `sources.json` 登记和 `reviews.json` 审核。外部条目不会因为被抓取到就自动公开。

生成失败时不得覆盖上一版 Catalog。只有所有条目解析、校验、打包成功后才替换 `dist`。

## 审核与供应链边界

只有 `reviewStatus = approved` 的条目进入公开 Catalog。审核记录可以覆盖分类、标签、数据等级和展示名，但 Skill 身份与版本来自包内 `SKILL.md`。

每个公开条目必须包含：

- 稳定的 `catalogId` 和 `skillId`
- 来源 ID、类型、路径，以及远程来源的 repository/revision
- 版本、用途、分类、标签和数据等级
- ZIP 下载位置、大小和 SHA-256
- 审核状态和可选审核时间

构建器拒绝目录逃逸和符号链接。Desktop 安装前再次验证 Catalog 身份、approved 状态、artifact 路径、大小和 SHA-256。

## 客户端接入边界

市场只负责发现和分发，不直接暴露模型工具：

```text
Marketplace Catalog
  -> Desktop marketplace service
    -> verified ZIP
      -> existing Skill Store installSkillFromZip
        -> workspace mount
          -> Local Skill Provider
            -> Runtime Projection
              -> Tool Call / PermissionGrant / Evidence
```

不得从 Renderer 直接使用文件系统或下载并解压安装包。Renderer 只通过 canonical IPC 请求列表、详情和安装。

不得新增绕过 `Skill Store`、Runtime Projection、Permission 或 Evidence 的市场执行路径。

## 发布

Desktop 的 `pack`、`dist`、`dist:mac` 和 `dist:win` 在 electron-builder 前执行 `marketplace:build`。`catalog.json` 和审核后的 ZIP 作为 `extraResources/marketplace` 进入安装包。

开发态 Desktop 从代码仓 `marketplace/dist` 读取；打包态从 `process.resourcesPath/marketplace` 读取。

当前版本使用随 Desktop 发布的静态 Catalog。未来如增加远程增量更新，应保持相同协议、校验和与审核边界，并增加签名、回滚和缓存策略；不能把第三方目录 URL 直接配置为客户端运行时真相。

## SkillHub 远程发现源

腾讯 SkillHub 是远程发现源，不是 Peer Agent 的本地安装真相或运行时。Desktop 主进程通过公开结构化 API 全量分页同步元数据，将索引原子写入 `userData/marketplace/skillhub-index.json`；Renderer 仅查询本地分页结果，不加载十万级全集。同步检查点保存 `nextPage`，网络失败保留已落盘索引，并可从失败页继续。

远程链路为：

```text
SkillHub API (pageSize <= 100)
  -> Desktop API client
    -> persistent local metadata index
      -> canonical IPC page/search/sort query
        -> Renderer presentation
```

索引键是 `namespace/slug`。远程 `total` 是动态值，不写死；ZIP 不预下载、不随 Desktop 打包，也不作为全量镜像保存。离线时市场继续展示最后一次成功同步的本地索引，同步错误只更新状态，不清空可用数据。

安装必须显式携带 `namespace`、`slug` 和 `version`，并按以下顺序完成后才能调用现有 `Skill Store`：

1. 获取平台 active keys 和指定版本 signature。
2. 使用 `key_id` 选择 Ed25519 key；公钥是 Base64 编码的 raw 32-byte key。
3. 直接验证 API 返回的原始 `payload` UTF-8 字节，禁止 JSON 重排后验签。
4. 校验 payload 的 `issuer = skillhub.cn`、发布 namespace、slug、version 和外层 `content_hash`。
5. 下载指定坐标 ZIP，验证 payload 中 `package_md5`。
6. 安全读取 ZIP，拒绝绝对路径、目录逃逸、符号链接、重复路径、超大文件数和超大解压总量，并要求根目录存在 `SKILL.md`。
7. 按 SkillHub hash v1 规则对非元数据文件计算 SHA-256，按规范化路径做字节序排序，将 `path:sha256(content)` 记录以换行连接并保留末尾换行，再计算聚合 SHA-256；结果必须与签名 payload 的 `content_hash` 和 `file_count` 一致。精确规则与测试向量见 `knowledge/architecture/skillhub-marketplace-source.md`。
8. 仅在全部校验通过后调用 `skillStore.installSkillFromZip`。

Ed25519 平台签名证明发布内容由 SkillHub 平台签发，不等同于 Peer Agent 安全审核，也不授予再分发许可证。未知 `key_id`、非 active key、issuer 变化或新 `hash_version` 必须 fail closed；公钥轮换由平台 keys 接口按 key ID 选择，不把当前 key 固化为永久唯一密钥。

## 验证要求

每次改动至少验证：

```bash
pnpm marketplace:build
pnpm marketplace:test
node --test apps/desktop/electron/main/skill-marketplace-service.test.mjs \
  apps/desktop/electron/main/ipc/register-skills-ipc.test.mjs \
  apps/desktop/electron/ipc/registration-inventory.test.mjs
pnpm --filter @peer-agent/protocol build
pnpm --filter @peer-agent/desktop typecheck
pnpm --filter @peer-agent/desktop build
```

并确认生成的 `catalog.json` 与 `sources.json` 不包含未批准的运行时依赖来源。

## 非目标

- 不镜像或批量安装未经审核的第三方 Skill。
- 不把外部聚合仓库当成 Peer Agent 的后端服务。
- 不允许市场条目直接成为模型可见工具。
- 不在 Renderer 保存权限、安装状态或审核真相。
- 当前阶段不实现在线账户、付费、评分、评论和远程自动更新。

## 关联资料

- `knowledge/decisions/15-plugin-skill-mcp-system.md`
- `knowledge/decisions/16-skill-call-lifecycle.md`
- `knowledge/decisions/58-local-skill-scope-and-workspace-mounting.md`
- 关联代码仓：`/Users/liangyin/Documents/DEV/github/peer_agent`
