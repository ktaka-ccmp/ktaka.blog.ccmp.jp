# Issue: ブログ記事 — 署名と検証: ECDSA を体験する

## Table of Contents

- [Description](#description)
- [Related Issues](#related-issues)
- [Approach](#approach)
- [Related Files](#related-files)
- [Implementation Tasks](#implementation-tasks)
- [Decision Log](#decision-log)
- [Resolution](#resolution)

## ID: 20260326-0420

## Created: 2026-03-26-04-19

## Closed:

## Status: open

## Priority: high

## Difficulty: small

## Description

Web Crypto API シリーズの最初の記事。実行環境のセットアップ + `crypto.subtle` を使って ECDSA 署名・検証を体験する。

**目的:** 「秘密鍵で署名、公開鍵で検証」という非対称暗号の基本を、コピペで動くコードで理解する
**結論:** ブラウザ / Bun / Node.js で電子署名が作れる。改ざんされたデータは検証で false になる

**前提知識:** なし（シリーズの入口）

## Related Issues

- `20260326-0419` ブログシリーズ — Web Crypto API で学ぶ暗号技術 (parent)
- `20260326-0421` 暗号化と鍵交換 — ハイブリッド暗号を体験する (next)

## Approach

### 素材

`~/GitHub/daily-journal/ktaka/2026/0324.md` の以下の部分:

- **L41〜L99**: ECDSA の概要テーブル（署名=秘密鍵、検証=公開鍵）、鍵ペア生成・署名・検証の JS コード、改ざん検知のデモ、ポイント解説

### 記事構成案

1. **導入**（2〜3行）
   - 「電子署名」とは何か？ → 秘密鍵で署名、公開鍵で検証
   - この記事のゴール: Web Crypto API で署名を作って検証する

2. **実行環境セットアップ**（シリーズ共通、この記事のみ）
   - **ブラウザ**: DevTools Console にコピペ
   - **Bun**: `bun run script.js`（インストール: `curl -fsSL https://bun.sh/install | bash`）
   - **Node.js**: `node script.js`（v19+ で `crypto.subtle` が使える）
   - 3環境とも `crypto.subtle` が同じ API で動くことを示す

3. **コード: 鍵ペア生成 → 署名 → 検証**
   - ジャーナルの ECDSA コード（L54〜L93）をベースに
   - `crypto.subtle.generateKey` → `crypto.subtle.sign` → `crypto.subtle.verify`
   - 正常データ → true、改ざんデータ → false を見せる

4. **何が起きているか（図 or 表）**
   - 署名: `秘密鍵 + データ → 署名値`
   - 検証: `公開鍵 + データ + 署名値 → true/false`
   - ジャーナルの概要テーブル（L46〜L49）を活用

5. **ポイント**（箇条書き3〜4個）
   - ECDSA は署名専用（暗号化はできない）
   - `extractable: false` で秘密鍵をエクスポート不可にできる
   - DPoP Proof の生成にも使われている（次回以降への伏線）

6. **まとめ**（2〜3行）
   - 公開鍵暗号の「署名・検証」をブラウザ / Bun / Node.js で体験した
   - 次回: 暗号化（RSA-OAEP + AES-GCM）と鍵交換（ECDH）

### 注意点

- コードはブラウザ DevTools / Bun / Node.js いずれでも動くようにする（毎回明記）
- 長い解説は避ける。表・コード・箇条書きで伝える
- 既存のブログ記事のスタイル・Zola テンプレートに合わせること

## Related Files

- `~/GitHub/daily-journal/ktaka/2026/0324.md` L41〜L99 — ECDSA 署名・検証のコードと解説

## Implementation Tasks

- [ ] 記事ファイル作成（content/ 以下、Zola フロントマター付き）
- [ ] コードの動作確認（DevTools で実行）
- [ ] `zola serve` でプレビュー確認

## Decision Log

<!-- APPEND-ONLY: Do not edit or delete existing entries. Add new entries at the bottom. -->

### 2026-03-26: 記事スコープを ECDSA 署名・検証のみに限定

- Context: ジャーナルには RSA-OAEP、AES-GCM、DPoP も含まれている
- Decision: この記事は ECDSA のみ。暗号化は次の記事へ
- Reason: 1記事1テーマ。署名と暗号化を混ぜると焦点がぼやける

## Resolution
