# Issue: ブログ記事 — 暗号化と鍵交換: ハイブリッド暗号を体験する

## Table of Contents

- [Description](#description)
- [Related Issues](#related-issues)
- [Approach](#approach)
- [Related Files](#related-files)
- [Implementation Tasks](#implementation-tasks)
- [Decision Log](#decision-log)
- [Resolution](#resolution)

## ID: 20260326-0421

## Created: 2026-03-26-04-19

## Closed:

## Status: open

## Priority: high

## Difficulty: small

## Description

Web Crypto API シリーズ。RSA-OAEP で鍵を包み、AES-GCM でデータを暗号化するハイブリッド暗号を実装する。

**目的:** なぜ公開鍵暗号と共通鍵暗号を組み合わせるのか理解する
**結論:** 公開鍵暗号は遅いので「鍵だけ」暗号化し、データ本体は高速な共通鍵暗号で暗号化する

**前提知識:** ECDSA の記事（公開鍵・秘密鍵の概念）

## Related Issues

- `20260326-0419` ブログシリーズ — Web Crypto API で学ぶ暗号技術 (parent)
- `20260326-0420` 署名と検証 — ECDSA を体験する (previous)
- `20260326-0422` TLS 1.2 ハンドシェイクを再現する (next)

## Approach

### 素材

`~/GitHub/daily-journal/ktaka/2026/0324.md` の以下の部分:

- **L100〜L175 付近**: RSA-OAEP 暗号化・復号のコード（鍵ペア生成、encrypt/decrypt）
- **L175〜L220 付近**: AES-GCM 暗号化・復号（generateKey、IV 生成、encrypt/decrypt）
- **L220〜L270 付近**: ハイブリッド暗号パターン（AES 鍵を RSA で包む）、DPoP との関係

### 記事構成案

1. **導入** — 前回は署名（認証）を学んだ。今回は暗号化（秘匿）
2. **RSA-OAEP で暗号化・復号** — 公開鍵で暗号化、秘密鍵で復号するコード
3. **AES-GCM で暗号化・復号** — 共通鍵 + IV で高速暗号化
4. **なぜ両方必要か？（ハイブリッド暗号）** — RSA は遅い＆サイズ制限 → AES 鍵だけ RSA で包む
5. **まとめ** — TLS もこの仕組みを使っている（TLS 記事への伏線）

## Related Files

- `~/GitHub/daily-journal/ktaka/2026/0324.md` L100〜L270 付近 — RSA-OAEP、AES-GCM、ハイブリッド暗号

## Implementation Tasks

- [ ] 記事ファイル作成
- [ ] コードの動作確認
- [ ] `zola serve` でプレビュー確認

## Decision Log

<!-- APPEND-ONLY: Do not edit or delete existing entries. Add new entries at the bottom. -->

### 2026-03-26: RSA-OAEP と AES-GCM を1記事にまとめる

- Context: RSA-OAEP 単体と AES-GCM 単体で2記事にする案もあった
- Decision: ハイブリッド暗号の「なぜ両方必要か」が結論なので1記事にまとめる
- Reason: 片方だけでは「だから何？」になる。組み合わせる理由が結論として明確

### 2026-03-26: コードは Bun / Node.js でも実行可能と明記

- Context: ブラウザ DevTools のみを想定していた
- Decision: 毎回「ブラウザでも Bun でも Node.js でも動く」と明記する
- Reason: Bun も crypto.subtle をサポートしている。実行環境の選択肢を増やす

## Resolution
