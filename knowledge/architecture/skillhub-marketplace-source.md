# SkillHub Marketplace Source

## Status

Accepted implementation boundary for Peer Agent's Tencent SkillHub remote discovery source.

## Decision

Peer Agent treats Tencent SkillHub as a remote discovery and package-signing source, not as the local installation truth, runtime, permission authority, or license authority.

The governed chain is:

```text
SkillHub API
  -> Desktop SkillHub API client
    -> persistent local metadata index
      -> canonical SkillHub IPC
        -> paginated Renderer presentation
          -> signed ZIP download
            -> signature and content verification
              -> existing Skill Store
                -> Runtime Projection / PermissionGrant / Evidence
```

Renderer never calls SkillHub directly, never persists the remote index, and never installs a ZIP directly.

## Public API contract

Peer Agent uses the public API at `https://api.skillhub.cn`:

- `GET /api/skills?page={page}&pageSize={pageSize}&sortBy={sort}`
- `GET /api/v1/skills/{slug}?namespace={namespace}`
- `GET /api/v1/skills/{slug}/files?version={version}&namespace={namespace}`
- `GET /api/v1/open/platform/keys`
- `GET /api/v1/open/skills/{slug}/versions/{version}/signature?namespace={namespace}`
- `GET /api/download?slug={slug}&version={version}&namespace={namespace}`

Observed constraints:

- `pageSize` is at most `100`.
- The list response supplies `total` and the current page's `skills`; clients must not depend on `totalPages`.
- Remote totals are dynamic and must not be hard-coded.
- Skill identity is the tuple `namespace / slug / version`; the metadata dedupe key is `namespace / slug`.
- Signature verification uses the exact UTF-8 bytes of the API's original `payload` string. Parsing and reserializing the payload before verification is forbidden.
- `public_key_raw_b64` is a Base64-encoded raw 32-byte Ed25519 public key.
- Download responses are ZIP packages. `content_hash` is not the ZIP SHA-256.

Any incompatible API change must fail closed at the adapter boundary instead of leaking unvalidated response fields into IPC or Renderer.

## Local index and full synchronization

Metadata is stored under the Desktop user-data directory:

```text
marketplace/
  skillhub-index.json
  skillhub-index.json.checkpoint.json
  skillhub-index.json.pages/
    000001.json
    000002.json
    ...
```

The store uses two logical snapshots:

- **published snapshot**: the last complete, queryable index in `skillhub-index.json`;
- **pending snapshot**: page shards plus checkpoint for the in-progress generation.

Each remote page is written as its own atomic shard, then the checkpoint advances. This avoids rewriting a 100,000-entry JSON document for every one of roughly 1,000 remote pages. When the final page arrives, page shards are merged and deduplicated by `catalogId`, then atomically published as the new complete index. Pending shards are removed only after publication.

Consequences:

- an interrupted sync resumes from `nextPage` after process restart;
- a failed refresh leaves the last complete snapshot queryable;
- the first sync may expose already-downloaded pending entries until a complete snapshot exists;
- a completed refresh removes entries that disappeared upstream instead of permanently unioning stale records;
- background synchronization starts in the Desktop main process and does not depend on opening the market page;
- the Renderer receives one local page at a time (currently 24 entries), not the full remote corpus.

Search, category filtering, and score/download/update sorting operate on the local index. The release package does not embed the SkillHub corpus or mirror all upstream ZIP files.

## Signed installation

Installation requires an explicit `namespace`, `slug`, and `version`. The Desktop main process performs these checks before calling the existing `installSkillFromZip` seam:

1. Fetch platform keys, version signature, and the exact requested ZIP.
2. Select the response key by `key_id`.
3. Require `algorithm = Ed25519`, `status = active`, `issuer = skillhub.cn`, and a raw 32-byte public key.
4. Verify the Ed25519 signature over the original payload UTF-8 bytes.
5. Parse only after signature verification.
6. Require outer `hash_version = 1`, payload `v = 1`, and payload `issuer = skillhub.cn`.
7. Bind payload `publisher_user_name`, `skill_slug`, and `skill_version` to the requested namespace/slug/version.
8. Require the outer `content_hash`, when present, to equal the signed payload's `content_hash`.
9. Verify ZIP bytes against signed `package_md5`.
10. Reject absolute paths, drive paths, `..`, duplicate entries, symbolic links, excessive entry counts, excessive expanded bytes, and archives without a root or single-wrapper-directory `SKILL.md`.
11. Compute each non-metadata file's SHA-256, sort records by normalized path using bytewise string order, join records as `path:sha256(content)` separated by newline with a final newline, then SHA-256 the resulting UTF-8 bytes.
12. Require the calculated v1 content hash and file count to equal the signed payload.
13. Only then pass the original ZIP buffer to the existing Skill Store.

Ignored metadata for v1 content hashing includes `_meta.json`, `.DS_Store`, `Thumbs.db`, AppleDouble `._*`, and entries under `__MACOSX/`.

MD5 is accepted only because it is part of SkillHub's signed package payload. It is not used as Peer Agent's general artifact integrity primitive and does not replace SHA-256 content verification.

## Key rotation and fail-closed behavior

Peer Agent does not pin today's key as a permanent singleton. It resolves keys from the platform-key response by `key_id`, while requiring an active Ed25519 key issued by `skillhub.cn`.

Installation is rejected for:

- unknown `key_id`;
- inactive key, wrong algorithm, wrong key issuer, or malformed public key;
- unsigned version or invalid signature;
- unknown `hash_version` or payload version;
- wrong payload issuer or identity coordinates;
- outer/payload content-hash disagreement;
- ZIP MD5 mismatch;
- calculated content-hash or file-count mismatch;
- unsafe ZIP structure;
- downstream Skill Store rejection.

A future hash version needs a new verified adapter and test vectors. It must not silently reuse v1.

## Failure and offline behavior

- List/sync network errors set a durable error status and retain the checkpoint.
- If a complete snapshot exists, queries continue to use it while refresh is failing.
- If no complete snapshot exists, already-downloaded pending shards may be queried.
- Installation requires the upstream ZIP, keys, and signature endpoints to be available; discovery cache does not imply offline package installation.
- Sync and installation failures stay local and structured; they do not promote remote responses or ZIP contents into system instructions.

## Trust and license boundary

A valid SkillHub platform signature proves that the payload was signed by an accepted SkillHub platform key and that the downloaded content matches the signed package declaration. It does not prove that:

- the Skill is safe for every user or workspace;
- Peer Agent reviewed its behavior;
- the publisher owns every included asset;
- Peer Agent may mirror or redistribute the ZIP;
- the Skill is licensed for a particular commercial use.

Therefore Peer Agent synchronizes metadata and downloads on demand, but does not include the full remote ZIP corpus in `extraResources` or its static first-party Catalog.

## Verification

Focused verification commands:

```bash
node --test apps/desktop/electron/main/skillhub-api-client.test.mjs
node --test apps/desktop/electron/main/skillhub-marketplace-store.test.mjs
node --test apps/desktop/electron/main/skillhub-verified-installer.test.mjs
node --test apps/desktop/electron/main/ipc/register-skills-ipc.test.mjs
pnpm --filter @peer-agent/desktop ipc:check
pnpm --filter @peer-agent/protocol build
pnpm --filter @peer-agent/desktop typecheck
pnpm --filter @peer-agent/desktop build
```

The installer also has a real upstream sample verification against:

```text
namespace = user_ec205dbb
slug      = web-tools-guide
version   = 1.0.2
key_id    = skillhub-platform-v1
```

The real-sample check uses a non-persisting test callback after verification; it does not install the sample into the user's Skill Store.

## Related knowledge

- `knowledge/architecture/peer-skill-marketplace.md`
- `knowledge/decisions/15-plugin-skill-mcp-system.md`
- `knowledge/decisions/16-skill-call-lifecycle.md`
- `knowledge/architecture/20-architecture-governance.md`
