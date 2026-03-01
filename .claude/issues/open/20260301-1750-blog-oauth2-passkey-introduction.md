# Issue: ブログ記事 — oauth2-passkey ライブラリ紹介 + デモサイト宣伝

## Table of Contents

- [Description](#description)
- [Related Issues](#related-issues)
- [Approach](#approach)
- [Related Files](#related-files)
- [Implementation Tasks](#implementation-tasks)
- [Decision Log](#decision-log)
- [Resolution](#resolution)

## ID: 20260301-1750

## Created: 2026-03-01-17-50

## Closed:

## Status: open

## Priority: high

## Difficulty: large

## Description

oauth2-passkey ライブラリのデモサイト (https://passkey-demo.ccmp.jp) を宣伝するブログ記事を執筆する。ライブラリの機能紹介、クイックスタート、デモサイトのウォークスルーを含む。シリーズ3本中の第1弾で、最も重要な記事。

タイトル案: "oauth2-passkey: Passwordless Authentication for Rust in Minutes"

言語: 英語（既存の認証/Rust 関連記事はすべて英語）

## Related Issues

- `20260301-1751` Blog: Deploying Rust to Cloud Run (シリーズ第2弾)
- `20260301-1752` Blog: Async Rust Pitfalls (シリーズ第3弾)

## Approach

### アウトライン

1. **Introduction** — パスワード認証の問題、2025 Passkeys 記事からの発展
2. **What oauth2-passkey Does** — 機能一覧テーブル
3. **Quick Start** — `oauth2_passkey_full_router()` の最小コード例
4. **Live Demo** — https://passkey-demo.ccmp.jp ウォークスルー + スクリーンショット
5. **Key Features** — Passkey promotion, Login history, Theme system, Admin UI, Demo mode
6. **Architecture Overview** — コア crate + axum crate の層構造
7. **What's Next** — 記事2・3 へのリンク、GitHub/crates.io リンク

### 素材

- ジャーナル 0205.md (2/7 README, 2/10 Passkey promotion, 2/14 Demo mode)
- ジャーナル 0213.md (2/16 v0.3.0 リリース)
- ジャーナル 0127.md (unified router API)
- 2025 Passkeys 記事（前編として参照）

### スクリーンショット/図

- デモサイトログイン画面
- ユーザーダッシュボード
- Passkey 登録モーダル
- 管理画面
- アーキテクチャ図

### サイズ目安

15-18KB

## Related Files

- `content/2026/Oauth2PasskeyIntroduction/index.md` (新規作成)
- `content/2025/01/implementing-passkeys-authentication-in-rust-axum/index.md` (参照)
- `~/GitHub/oauth2-passkey/README.md` (素材)
- `~/GitHub/daily-journal/ktaka/2026/0205.md` (素材)
- `~/GitHub/daily-journal/ktaka/2026/0213.md` (素材)
- `~/GitHub/daily-journal/ktaka/2026/0127.md` (素材)

## Implementation Tasks

- [ ] 記事ディレクトリ作成 (`content/2026/Oauth2PasskeyIntroduction/`)
- [ ] index.md 執筆（front matter + 本文）
- [ ] スクリーンショット撮影・配置
- [ ] 相互リンク設定（記事2・3、2025 Passkeys 記事）
- [ ] `zola build` で確認

## Decision Log

<!-- APPEND-ONLY: Do not edit or delete existing entries. Add new entries at the bottom. -->

### 2026-03-01: 記事シリーズの言語と構成を決定

- Context: デモサイト宣伝のためのブログ記事をどう構成するか
- Decision: 英語で3本のシリーズ（紹介、デプロイ、落とし穴）とし、本記事を第1弾とする
- Reason: 既存の認証/Rust 記事はすべて英語。crates.io やグローバル Rust コミュニティへの発信には英語が最適。1本にまとめると長くなりすぎ、宣伝効果が薄まる

## Resolution
