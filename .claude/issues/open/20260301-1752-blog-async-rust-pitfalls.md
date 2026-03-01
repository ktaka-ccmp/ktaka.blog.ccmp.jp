# Issue: ブログ記事 — Async Rust の落とし穴（JWKS デッドロック + SQLite Pool）

## Table of Contents

- [Description](#description)
- [Related Issues](#related-issues)
- [Approach](#approach)
- [Related Files](#related-files)
- [Implementation Tasks](#implementation-tasks)
- [Decision Log](#decision-log)
- [Resolution](#resolution)

## ID: 20260301-1752

## Created: 2026-03-01-17-52

## Closed:

## Status: open

## Priority: medium

## Difficulty: medium

## Description

oauth2-passkey を Cloud Run にデプロイした際に発見された2つの非同期 Rust バグをブログ記事にする。tokio::sync::Mutex の JWKS キャッシュデッドロックと、SQLite in-memory 接続プールによる DB 消滅の2つを詳細に解説する。シリーズ3本中の第3弾。

タイトル案: "Async Rust Pitfalls: JWKS Cache Deadlocks and In-Memory SQLite Pool Traps"

言語: 英語

## Related Issues

- `20260301-1750` Blog: oauth2-passkey Introduction (シリーズ第1弾)
- `20260301-1751` Blog: Deploying Rust to Cloud Run (シリーズ第2弾)

## Approach

### アウトライン

1. **Introduction** — Cloud Run デプロイ後に発見された2つのバグ（記事1・2へリンク）
2. **Bug 1: JWKS Cache Deadlock** — tokio::sync::Mutex 再入問題、`if let` での MutexGuard 寿命延長、Redis では発現しない理由、修正方法
3. **Bug 2: SQLite In-Memory Pool Destruction** — idle_timeout/max_lifetime による接続切断 → DB 消滅、min_connections(1) では不十分だった理由、最終修正
4. **Why Both Bugs Only Appeared in Docker** — ローカルでは Redis + ファイル SQLite で隠れていた、タイミング依存
5. **Conclusion** — 非同期 Rust パターンまとめ、記事1・2 へのリンク

### 素材

- ジャーナル 0205.md (2/11 デッドロック詳細分析、2/12 SQLite pool 安定化)
- ジャーナル 0213.md (2/16 v0.3.0 リリースノート)

### スクリーンショット/図

- MutexGuard 寿命の図（if let パターンでガードが保持される範囲）
- SQLite in-memory 接続プールのライフサイクル図
- コード diff（修正前/後）で代替可能

### サイズ目安

12-16KB

## Related Files

- `content/2026/AsyncRustPitfalls/index.md` (新規作成)
- `~/GitHub/daily-journal/ktaka/2026/0205.md` (素材)
- `~/GitHub/daily-journal/ktaka/2026/0213.md` (素材)

## Implementation Tasks

- [ ] 記事ディレクトリ作成 (`content/2026/AsyncRustPitfalls/`)
- [ ] index.md 執筆（front matter + 本文）
- [ ] 図の作成・配置（MutexGuard 寿命、SQLite pool ライフサイクル）
- [ ] 相互リンク設定（記事1・2）
- [ ] `zola build` で確認

## Decision Log

<!-- APPEND-ONLY: Do not edit or delete existing entries. Add new entries at the bottom. -->

### 2026-03-01: ニッチだが価値のある独立記事として位置づけ

- Context: 2つのバグを記事2（デプロイ）に含めるか、独立させるか
- Decision: 独立した第3弾とする
- Reason: tokio Mutex デッドロックや SQLite 接続プール問題は認証やデプロイと独立した汎用的な知見。async Rust や SQLx を使う開発者に深く刺さる内容であり、別記事にすることで異なるコミュニティにもリーチできる

## Resolution
