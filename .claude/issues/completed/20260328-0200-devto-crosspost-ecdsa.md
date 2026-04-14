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

## Closed: 2026-04-03

## Status: completed

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
- GitHub Actions で自動投稿（`.github/workflows/devto-publish.yml`）
- canonical_url で既存記事を検索し、POST（新規）/ PUT（更新）を自動判定

## Related Files

- `content/2026/WebCryptoEcdsaEn/index.md` — 元記事 1
- `content/2026/EcdsaFromScratchEn/index.md` — 元記事 2
- `docs/Oauth2PasskeyDemo-devto/dev-to-oauth2-passkey-demo.md` — 過去の例

## Implementation Tasks

- [x] WebCryptoEcdsaEn の dev.to 版作成
- [x] EcdsaFromScratchEn の dev.to 版作成
- [x] GitHub Actions ワークフロー作成（canonical_url による POST/PUT 自動判定）
- [x] `/devto-crosspost` スキル作成
- [x] WebCryptoEcdsa を dev.to に投稿（published: true）
- [x] EcdsaFromScratch を dev.to に投稿確認
- [x] dev.to で折りたたみ表示の確認

## Decision Log

<!-- APPEND-ONLY: Do not edit or delete existing entries. Add new entries at the bottom. -->

### 2026-03-28: GitHub Actions で自動投稿を実装

- Context: 手動投稿では更新の追跡が困難
- Decision: canonical_url による既存記事検索 + POST/PUT 自動判定のワークフローを作成
- Reason: .devto-id ファイルの保存・master への自動コミットが不要

### 2026-03-28: dev.to の折りたたみは Liquid タグが必要

- Context: `<details>` タグが dev.to で除去されていた
- Decision: `{% details %}...{% enddetails %}` に変換
- Reason: dev.to は `<details>` HTML をサポートせず、独自の Liquid タグを使う

### 2026-03-28: fetch-depth: 2 が必要

- Context: shallow clone で `HEAD~1` が見えず、ファイル検出に失敗
- Decision: `actions/checkout@v4` に `fetch-depth: 2` を追加
- Reason: マージコミットの親と diff を取るために最低 2 コミット分が必要

## Resolution

dev.to に ECDSA 英語記事 2 本をクロスポスト完了。WebCryptoEcdsaEn、EcdsaFromScratchEn ともに公開確認済み（4/2）。
