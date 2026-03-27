# Issue: ブログ記事 — ECDSA 記事 2 本の英語版

## Table of Contents

- [Description](#description)
- [Related Issues](#related-issues)
- [Approach](#approach)
- [Related Files](#related-files)
- [Implementation Tasks](#implementation-tasks)
- [Decision Log](#decision-log)
- [Resolution](#resolution)

## ID: 20260327-0200

## Created: 2026-03-27-02-00

## Closed:

## Status: open

## Priority: high

## Difficulty: small

## Description

ECDSA 関連の日本語記事 2 本の英語版を作成する。

1. **Web Crypto API で ECDSA 署名・検証を理解する** → 英語版
2. **ECDSA の計算をライブラリなしで実装する** → 英語版

## Related Issues

- `20260326-0420` Web Crypto API で ECDSA 署名・検証を理解する (completed, 翻訳元)
- `20260327-0100` ECDSA の計算をライブラリなしで実装する (completed, 翻訳元)

## Approach

- 既存の bilingual パターン（`Oauth2PasskeyDemo` / `Oauth2PasskeyDemoEn`）に従う
- `content/2026/WebCryptoEcdsaEn/index.md` — path: `en/2026/WebCryptoEcdsa`
- `content/2026/EcdsaFromScratchEn/index.md` — path: `en/2026/EcdsaFromScratch`
- 日本語版と英語版で相互リンクを追加
- コードブロックはそのまま（コメントは英語に変更）
- 実行結果の日本語出力は英語に変更

## Related Files

- `content/2026/WebCryptoEcdsa/index.md` — 日本語版 1
- `content/2026/EcdsaFromScratch/index.md` — 日本語版 2

## Implementation Tasks

- [ ] WebCryptoEcdsaEn/index.md 作成
- [ ] EcdsaFromScratchEn/index.md 作成
- [ ] 日本語版に英語版へのリンク追加
- [ ] 英語版に日本語版へのリンク追加
- [ ] `zola build` でビルド確認

## Decision Log

<!-- APPEND-ONLY: Do not edit or delete existing entries. Add new entries at the bottom. -->

## Resolution
