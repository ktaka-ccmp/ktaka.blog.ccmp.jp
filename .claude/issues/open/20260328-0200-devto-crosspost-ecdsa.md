# Issue: dev.to クロスポスト — ECDSA 英語記事 2 本

## Table of Contents

- [Description](#description)
- [Related Issues](#related-issues)
- [Approach](#approach)
- [Related Files](#related-files)
- [Implementation Tasks](#implementation-tasks)
- [Decision Log](#decision-log)
- [Resolution](#resolution)

## ID: 20260328-0200

## Created: 2026-03-28-02-00

## Closed:

## Status: open

## Priority: high

## Difficulty: small

## Description

ECDSA 英語記事 2 本を dev.to にクロスポストする。

1. Understanding ECDSA Signatures with the Web Crypto API
2. Implementing ECDSA from Scratch Without Libraries

## Related Issues

- `20260327-0200` ECDSA 記事 2 本の英語版 (completed)
- `20260328-0100` Zenn クロスポスト — ECDSA 記事 2 本 (open)

## Approach

- 既存パターン（`docs/<ArticleName>-devto/`）に従い、dev.to 用 Markdown を作成
- YAML frontmatter に `canonical_url` を設定
- 過去の例: `docs/Oauth2PasskeyDemo-devto/dev-to-oauth2-passkey-demo.md`
- Web UI で投稿（API 自動化は将来検討）

## Related Files

- `content/2026/WebCryptoEcdsaEn/index.md` — 元記事 1
- `content/2026/EcdsaFromScratchEn/index.md` — 元記事 2
- `docs/Oauth2PasskeyDemo-devto/dev-to-oauth2-passkey-demo.md` — 過去の例

## Implementation Tasks

- [ ] WebCryptoEcdsaEn の dev.to 版作成
- [ ] EcdsaFromScratchEn の dev.to 版作成
- [ ] dev.to で投稿・確認

## Decision Log

<!-- APPEND-ONLY: Do not edit or delete existing entries. Add new entries at the bottom. -->

## Resolution
