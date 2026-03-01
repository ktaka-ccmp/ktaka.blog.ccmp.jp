# Issue: ブログ記事 — oauth2-passkey デモサイト紹介（軽量版）

## Table of Contents

- [Description](#description)
- [Related Issues](#related-issues)
- [Approach](#approach)
- [Related Files](#related-files)
- [Implementation Tasks](#implementation-tasks)
- [Decision Log](#decision-log)
- [Resolution](#resolution)

## ID: 20260301-1754

## Created: 2026-03-01-17-54

## Closed:

## Status: open

## Priority: high

## Difficulty: small

## Description

oauth2-passkey デモサイト (https://passkey-demo.ccmp.jp) を紹介する軽量な記事を先行投稿する。詳細な技術記事シリーズ（20260301-1750〜1752）の前に、デモサイトの URL を早く世に出すことが目的。

タイトル案: "Try Passwordless Auth: oauth2-passkey Live Demo"

言語: 英語、サイズ: 5-8KB

## Related Issues

- `20260301-1750` Blog: oauth2-passkey Introduction (詳細版、本記事の後に公開)
- `20260301-1751` Blog: Deploying Rust to Cloud Run
- `20260301-1752` Blog: Async Rust Pitfalls

## Approach

短くコンパクトに:
1. What — oauth2-passkey とは（2-3行）
2. Demo — https://passkey-demo.ccmp.jp で試せること（スクリーンショット数枚）
3. How — 簡単な使い方（最小コード例）
4. Links — GitHub, crates.io, docs

## Related Files

- `content/2026/Oauth2PasskeyDemo/index.md` (新規作成)

## Implementation Tasks

- [ ] 記事ディレクトリ作成 (`content/2026/Oauth2PasskeyDemo/`)
- [ ] index.md 執筆
- [ ] スクリーンショット配置（後から追加可）
- [ ] `zola build` で確認

## Decision Log

<!-- APPEND-ONLY: Do not edit or delete existing entries. Add new entries at the bottom. -->

### 2026-03-01: 軽量版を先行投稿

- Context: 詳細な記事シリーズ（3本）の執筆には時間がかかる
- Decision: デモサイト紹介の軽量版を先に投稿する
- Reason: デモサイト URL を早く公開してインデックスされるようにする。詳細記事はこの記事からリンクする形で後から追加

## Resolution
