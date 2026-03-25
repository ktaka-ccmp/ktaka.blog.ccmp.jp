# Issue: ブログ記事 — Passkey がフィッシングに強い理由

## Table of Contents

- [Description](#description)
- [Related Issues](#related-issues)
- [Approach](#approach)
- [Related Files](#related-files)
- [Implementation Tasks](#implementation-tasks)
- [Decision Log](#decision-log)
- [Resolution](#resolution)

## ID: 20260326-0425

## Created: 2026-03-26-04-19

## Closed:

## Status: open

## Priority: medium

## Difficulty: small

## Description

Web Crypto API シリーズ。Passkey（WebAuthn）の登録・認証フローを Web Crypto API で再現し、なぜフィッシングサイトでは使えないのかを理解する。

**目的:** Passkey がパスワードより安全と言われる技術的根拠を理解する
**結論:** `clientDataJSON` に origin（接続先のドメイン）が含まれるため、偽サイトで作った署名は本物のサーバーで検証が通らない

**前提知識:** ECDSA の記事のみ

## Related Issues

- `20260326-0419` ブログシリーズ — Web Crypto API で学ぶ暗号技術 (parent)
- `20260326-0420` 署名と検証 — ECDSA を体験する (depends on)
- `20260326-0426` DBSC — Cookie を TPM に縛る (next)

## Approach

### 素材

`~/GitHub/daily-journal/ktaka/2026/0324.md` の以下の部分:

- **L630〜L812 付近**: Passkey（WebAuthn）の概念実装 — 登録（attestation）・認証（assertion）フロー、authenticatorData 構造、signCount、origin ベースのフィッシング耐性
- **暗号技術比較ノート内**: Passkey の `clientDataJSON` に origin が入る仕組みのコード例

### 記事構成案

1. **導入** — Passkey は「フィッシングに強い」と言われるが、なぜ？
2. **登録フロー** — サーバーがチャレンジ送信 → ブラウザが鍵ペア生成 → 公開鍵を登録
3. **認証フロー** — サーバーがチャレンジ送信 → ブラウザが秘密鍵で署名 → サーバーが検証
4. **フィッシング耐性の仕組み** — `clientDataJSON` に `origin` が入る → 偽サイトの origin では署名が無効
5. **コード** — Web Crypto API で認証フローを再現、origin を変えると検証失敗するデモ（ブラウザでも Bun でも実行可能）
6. **SSH との違い**（表）— TOFU vs origin 束縛、鍵の保管場所
7. **まとめ** — 秘密鍵がデバイスから出ない + origin 束縛 = フィッシング耐性

## Related Files

- `~/GitHub/daily-journal/ktaka/2026/0324.md` L630〜L812 付近 — Passkey 概念実装、フィッシング耐性

## Implementation Tasks

- [ ] 記事ファイル作成
- [ ] コードの動作確認
- [ ] `zola serve` でプレビュー確認

## Decision Log

<!-- APPEND-ONLY: Do not edit or delete existing entries. Add new entries at the bottom. -->

### 2026-03-26: 「フィッシング耐性」を結論に据える

- Context: Passkey は登録・認証・同期・UX など多くの話題がある
- Decision: この記事は「なぜフィッシングに強いか」だけに絞る
- Reason: 1記事1結論。WebAuthn の全体像は oauth2-passkey の紹介記事（別イシュー）でカバー済み

## Resolution
