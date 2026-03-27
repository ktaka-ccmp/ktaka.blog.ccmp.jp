# Issue Tracking

This directory contains issue/task tracking files for the project.

## Current Issues

<!-- AUTO-UPDATED: Do not edit manually. Updated by /issue command. -->

### Open (11)

| ID | Priority | Difficulty | Title |
|----|----------|------------|-------|
| `20260326-0419` | high | large | [シリーズ — Web Crypto API で学ぶ暗号技術](open/20260326-0419-blog-series-webcrypto-learn-crypto.md) |
| `20260326-0421` | high | small | [暗号化と鍵交換 — ハイブリッド暗号を体験する](open/20260326-0421-blog-webcrypto-02-hybrid-encryption.md) |
| `20260326-0422` | medium | medium | [TLS 1.2 ハンドシェイクを再現する](open/20260326-0422-blog-webcrypto-03-tls12.md) |
| `20260326-0423` | medium | small | [TLS 1.3 で何が変わったか](open/20260326-0423-blog-webcrypto-035-tls13.md) |
| `20260326-0424` | medium | small | [SSH 公開鍵認証の仕組み](open/20260326-0424-blog-webcrypto-04-ssh.md) |
| `20260326-0425` | medium | small | [Passkey がフィッシングに強い理由](open/20260326-0425-blog-webcrypto-05-passkey.md) |
| `20260326-0426` | low | medium | [DBSC — Cookie を TPM に縛る](open/20260326-0426-blog-webcrypto-06-dbsc.md) |
| `20260301-1754` | high | small | [ブログ記事 — oauth2-passkey デモサイト紹介（軽量版）](open/20260301-1754-blog-demo-site-announcement.md) |
| `20260301-1750` | high | large | [ブログ記事 — oauth2-passkey ライブラリ紹介 + デモサイト宣伝](open/20260301-1750-blog-oauth2-passkey-introduction.md) |
| `20260301-1751` | medium | large | [ブログ記事 — Rust アプリを 27MB Docker イメージで Cloud Run にデプロイ](open/20260301-1751-blog-rust-cloud-run-deploy.md) |
| `20260301-1752` | medium | medium | [ブログ記事 — Async Rust の落とし穴（JWKS デッドロック + SQLite Pool）](open/20260301-1752-blog-async-rust-pitfalls.md) |

### Completed (8)

| ID | Title |
|----|-------|
| `20260327-0200` | [ECDSA 記事 2 本の英語版](completed/20260327-0200-blog-ecdsa-english-versions.md) |
| `20260327-0100` | [ECDSA の計算をライブラリなしで実装する](completed/20260327-0100-blog-ecdsa-from-scratch.md) |
| `20260326-0420` | [Web Crypto API で ECDSA 署名・検証を理解する](completed/20260326-0420-blog-webcrypto-01-ecdsa.md) |
| `20260301-0801` | [ブログ記事のmetaタグ（description・OGP）をテンプレートに組み込む](completed/20260301-0801-meta-tags-ogp.md) |
| `20260220-0210` | [ドメイン変更 kt.blog.ccmp.jp → ktaka.blog.ccmp.jp](completed/20260220-0210-domain-migration.md) |
| `20260220-0209` | [Blogspot（ktaka.blog.ccmp.jp）からのコンテンツ移行](completed/20260220-0209-blogspot-content-migration.md) |
| `20260220-0208` | [入稿システム検討 — Zola静的サイトジェネレーター評価・導入](completed/20260220-0208-zola-evaluation.md) |
| `20260219-1820` | [GitHub Pagesでkt.blog.ccmp.jpとしてブログを公開する](completed/20260219-1820-github-pages-custom-domain.md) |

### Wontfix (0)

| ID | Title |
|----|-------|

### Deferred (1)

| ID | Title |
|----|-------|
| `20260220-0207` | [ブログの見た目改善（テーマ・CSS・レイアウト）](deferred/20260220-0207-theme-css-improvement.md) |

<!-- END AUTO-UPDATED -->

## Directory Structure

```
.claude/issues/
├── open/           # Active issues
├── completed/      # Resolved issues
├── wontfix/        # Closed without implementation
├── deferred/       # Postponed issues
└── README.md       # This file
```

Issues are organized by status. When status changes, move the file to the appropriate directory.

## File Naming Convention

New issues use the timestamp-based format:

```text
YYYYMMDD-HHMM-<short-slug>.md
```

Example: `20260210-1430-login-history-enhancement.md`

## Issue ID Format

New issues use a timestamp-based ID:

```text
YYYYMMDD-HHMM
```

- `YYYYMMDD`: Creation date
- `HHMM`: Creation time (24h format)

Example: `20260210-1430`, `20260210-1545`

## Issue Template

```markdown
# Issue: <Title>

## Table of Contents

- [Description](#description)
- [Related Issues](#related-issues)
- [Approach](#approach)
- [Related Files](#related-files)
- [Implementation Tasks](#implementation-tasks)
- [Decision Log](#decision-log)
- [Resolution](#resolution)

## ID: YYYYMMDD-HHMM

## Created: YYYY-MM-DD-HH-MM

## Closed:

## Status: open | completed | wontfix | deferred

## Priority: high | medium | low

## Difficulty: small | medium | large

## Description

<What needs to be done and why>

## Related Issues

- `YYYYMMDD-HHMM` <Title> (relationship: e.g., depends on, related to, supersedes)

## Approach

<Current plan for implementation>

## Related Files

- `path/to/file`

## Implementation Tasks

- [ ] <Task 1>
- [ ] <Task 2>

## Decision Log

<!-- APPEND-ONLY: Do not edit or delete existing entries. Add new entries at the bottom. -->

### YYYY-MM-DD: <Short summary of decision>

- Context: <What prompted this decision>
- Decision: <What was decided>
- Reason: <Why this was chosen over alternatives>

## Resolution

<What was done to resolve this issue>
```

## Section Update Rules

| Section | Update Rule |
|---------|------------|
| Created | Written once at creation |
| Closed | Written once when issue is resolved or closed |
| Description | Freely updatable |
| Related Issues | Freely updatable |
| Approach | Freely updatable (always reflects current plan) |
| Related Files | Freely updatable |
| Implementation Tasks | Freely updatable |
| **Decision Log** | **Append-only -- never edit or delete existing entries** |
| Resolution | Written once when issue is resolved |

The **Decision Log** preserves the history of design decisions, approach changes, and
rejected alternatives. When updating other sections (especially Approach), always add
a corresponding Decision Log entry explaining what changed and why.

## Status Values

| Status | Directory | Description |
|--------|-----------|-------------|
| `open` | `open/` | New or in-progress |
| `completed` | `completed/` | Resolved and committed |
| `wontfix` | `wontfix/` | Closed without implementation |
| `deferred` | `deferred/` | Postponed for later |

## Commands

- `/issue` - Create or update an issue
- `/backlog` - View all open issues
- `/snapshot` - Create a session snapshot (different from issues)

## Workflow

1. Create new issue in `open/` directory
2. **Update this README's "Current Issues" table** (increment count, add row)
3. Work on the issue
4. When resolved, update Resolution section and move to `completed/`
5. If postponed, move to `deferred/`

**Important**: Always update the README table when creating, completing, or moving issues.

## Difference from Sessions

- **Sessions** (`.claude/sessions/`): Work context snapshots for transferring between machines
- **Issues** (`.claude/issues/`): Task/bug tracking that persists across sessions
