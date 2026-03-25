# Issue: ブログ記事 — DBSC: Cookie を TPM に縛る

## Table of Contents

- [Description](#description)
- [Related Issues](#related-issues)
- [Approach](#approach)
- [Related Files](#related-files)
- [Implementation Tasks](#implementation-tasks)
- [Decision Log](#decision-log)
- [Resolution](#resolution)

## ID: 20260326-0426

## Created: 2026-03-26-04-19

## Closed:

## Status: open

## Priority: low

## Difficulty: medium

## Description

Web Crypto API シリーズ。DBSC（Device Bound Session Credentials）の仕組みを解説し、Passkey との相補性を示す。

**目的:** Cookie 盗難（セッションハイジャック）をどう防ぐか理解する
**結論:** TPM に秘密鍵を縛り、短寿命 Cookie + 署名付き JWT で更新。Cookie 単体では無意味になる。Passkey が「ログイン時」の保護、DBSC が「ログイン後」の保護

**前提知識:** Passkey の記事

## Related Issues

- `20260326-0419` ブログシリーズ — Web Crypto API で学ぶ暗号技術 (parent)
- `20260326-0425` Passkey がフィッシングに強い理由 (previous, depends on)

## Approach

### 素材

`~/GitHub/daily-journal/ktaka/2026/0324.md` の以下の部分:

- **L816〜L970**: DBSC の全ライフサイクル — ログイン → 登録（TPM 鍵生成）→ 通常リクエスト → リフレッシュ（JWT 署名）→ Cookie 設計（same-name overwrite）→ キャッシュ設計 → 互換性 → 脅威分析 → Passkey との相補性

### 記事構成案

1. **導入** — Passkey でログインは守れた。でもログイン後の Cookie が盗まれたら？
2. **DBSC の仕組み**（図）— 短寿命 Cookie → 期限切れ → TPM 秘密鍵で署名した JWT で更新
3. **HTTP リクエスト例** — 具体的なヘッダーの流れ
4. **Passkey + DBSC = フルデバイスバインディング**（表）
   - Passkey: ログイン時の認証をデバイスに縛る
   - DBSC: ログイン後のセッションをデバイスに縛る
5. **注意点** — Chrome 限定（W3C 提案段階）、TPM 必須
6. **まとめ** — シリーズ全体の振り返り

### 注意点

- DBSC は W3C 提案段階で Chrome のみ。その旨を明記する
- Web Crypto API でのコード再現は限定的（TPM アクセスはブラウザ API にない）。概念説明中心になる

## Related Files

- `~/GitHub/daily-journal/ktaka/2026/0324.md` L816〜L970 — DBSC セッション管理

## Implementation Tasks

- [ ] 記事ファイル作成
- [ ] `zola serve` でプレビュー確認

## Decision Log

<!-- APPEND-ONLY: Do not edit or delete existing entries. Add new entries at the bottom. -->

### 2026-03-26: シリーズ最終回として Passkey との相補性を結論にする

- Context: DBSC 単体でも記事になるが、シリーズの文脈がある
- Decision: Passkey（#5）からの流れで「ログイン後の保護」として位置づける
- Reason: シリーズの締めくくりとして「認証の全体像」を示せる

## Resolution
