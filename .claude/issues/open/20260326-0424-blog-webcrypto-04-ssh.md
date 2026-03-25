# Issue: ブログ記事 — SSH 公開鍵認証の仕組み

## Table of Contents

- [Description](#description)
- [Related Issues](#related-issues)
- [Approach](#approach)
- [Related Files](#related-files)
- [Implementation Tasks](#implementation-tasks)
- [Decision Log](#decision-log)
- [Resolution](#resolution)

## ID: 20260326-0424

## Created: 2026-03-26-04-19

## Closed:

## Status: open

## Priority: medium

## Difficulty: small

## Description

Web Crypto API シリーズ。SSH の公開鍵認証を Web Crypto API で再現し、TOFU（Trust On First Use）とチャレンジ署名の仕組みを理解する。

**目的:** `ssh-keygen` → `ssh user@host` で何が起きているか理解する
**結論:** 初回接続時のフィンガープリント確認（TOFU）が信頼の起点。以降はサーバーのチャレンジに秘密鍵で署名して認証

**前提知識:** ECDSA の記事のみ。TLS の記事を読まなくても入れる

## Related Issues

- `20260326-0419` ブログシリーズ — Web Crypto API で学ぶ暗号技術 (parent)
- `20260326-0420` 署名と検証 — ECDSA を体験する (depends on)

## Approach

### 素材

`~/GitHub/daily-journal/ktaka/2026/0324.md` の以下の部分:

- **L550〜L630 付近**: SSH 公開鍵認証の概念実装（TOFU、ユーザー認証フロー）
- **L626〜L700 付近**: 暗号技術比較ノート内の SSH セクション

### 記事構成案

1. **導入** — `ssh-keygen` で鍵を作って `ssh` で接続する。裏で何が起きている？
2. **ステップ1: TOFU** — 初回接続時の「fingerprint を確認しますか？」の意味
3. **ステップ2: チャレンジ署名** — サーバーがランダムデータを送り、クライアントが秘密鍵で署名
4. **コード** — ECDSA を使ってチャレンジ署名を再現
5. **TLS との違い**（表）— CA vs TOFU、一方向 vs 双方向認証
6. **まとめ** — SSH の信頼モデルは「初回の確認」に依存している

## Related Files

- `~/GitHub/daily-journal/ktaka/2026/0324.md` L550〜L700 付近 — SSH 公開鍵認証、比較ノート

## Implementation Tasks

- [ ] 記事ファイル作成
- [ ] コードの動作確認
- [ ] `zola serve` でプレビュー確認

## Decision Log

<!-- APPEND-ONLY: Do not edit or delete existing entries. Add new entries at the bottom. -->

### 2026-03-26: TLS 非依存で読めるようにする

- Context: SSH 記事を TLS の後に置くが、依存させるか
- Decision: ECDSA の記事のみを前提とし、TLS を読まなくても理解できるようにする
- Reason: 読者が興味のある記事から読めるようにする。TLS との比較は補足として入れる

## Resolution
