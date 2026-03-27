# Issue: ブログ記事 — ECDSA の計算をライブラリなしで実装する

## Table of Contents

- [Description](#description)
- [Related Issues](#related-issues)
- [Approach](#approach)
- [Related Files](#related-files)
- [Implementation Tasks](#implementation-tasks)
- [Decision Log](#decision-log)
- [Resolution](#resolution)

## ID: 20260327-0100

## Created: 2026-03-27-01-00

## Closed: 2026-03-27

## Status: completed

## Priority: high

## Difficulty: medium

## Description

ECDSA の署名・検証を外部ライブラリなしに BigInt だけで実装し、全ステップの中間値を確認できるようにする記事。前回の ECDSA 記事の付録で示した数式を、実際にコードで動かして理解する。

**目的:** ECDSA の署名・検証が「モジュラー演算」「楕円曲線上の点の演算」「署名式・検証式」の 3 層で構成されていることを、コードレベルで確認する
**結論:** 実装に必要な関数は 4 つ（modInverse, pointAdd, scalarMul, toyHash）だけ。P-256 との違いは曲線パラメータと数値サイズだけで、アルゴリズムは同じ

**前提知識:** ECDSA 記事（WebCryptoEcdsa）の付録を読んでいると理解しやすい

## Related Issues

- `20260326-0420` Web Crypto API で ECDSA 署名・検証を理解する (completed, 前提)
- `20260326-0419` ブログシリーズ — Web Crypto API で学ぶ暗号技術 (parent)

## Approach

### 素材

`~/GitHub/daily-journal/ktaka/2026/0327.md` の以下の部分:

- **L53〜L355**: JavaScript 版 ECDSA from scratch（モジュラー演算、点の演算、曲線パラメータ、鍵生成、署名、検証、改ざん検知）
- **L359〜**: Python 版（同じアルゴリズムの Python 移植）

### 記事構成案

1. **導入** — 前回の付録の数式を、実際にコードで動かす
2. **小さな曲線で試す** — y² = x³ + x + 1 (mod 97) を使う理由
3. **モジュラー演算** — mod 関数、モジュラー逆元（拡張ユークリッド互除法）
4. **楕円曲線上の点の演算** — pointAdd, scalarMul（ダブル＆アド）
5. **曲線パラメータとベースポイント G** — 曲線上の点の探索、位数が素数の点を選ぶ
6. **鍵生成** — 秘密鍵 d、公開鍵 Q = d · G
7. **署名** — h, k, R, r, s の計算と中間値
8. **検証** — u1, u2, R' の復元、R'.x == r の確認
9. **改ざん検知** — 1 文字変えると検証失敗
10. **まとめ** — 4 関数で完結、P-256 との違いはパラメータだけ

### 注意点

- 中間値をすべて表示して「何が起きているか」を見せる
- 小さな曲線（mod 97）で全値が 2 桁に収まるようにする
- Python 版は含めるか要検討（記事が長くなりすぎる場合は別記事）

## Related Files

- `~/GitHub/daily-journal/ktaka/2026/0327.md` L53〜L355 — JavaScript 版 ECDSA from scratch
- `~/GitHub/daily-journal/ktaka/2026/ecdsa/ecdsa-from-scratch.mjs` — コードファイル
- `content/2026/WebCryptoEcdsa/index.md` — 前回の ECDSA 記事（付録からリンク予定）

## Implementation Tasks

- [x] 記事ファイル作成（content/2026/EcdsaFromScratch/index.md）
- [x] コードの動作確認
- [x] `zola build` でビルド確認
- [x] `zola serve` でプレビュー確認
- [x] レビュー

## Decision Log

<!-- APPEND-ONLY: Do not edit or delete existing entries. Add new entries at the bottom. -->

### 2026-03-27: 記事スコープを JavaScript 版に限定

- Context: ジャーナルには Python 版もある
- Decision: まず JavaScript 版のみで記事を作成。Python 版は別記事にするか検討
- Reason: 1 記事が長くなりすぎるのを避ける。JavaScript は前回記事と同じ言語で一貫性がある

### 2026-03-27: 記事完成

- Context: ジャーナル素材をベースに記事を執筆・レビュー完了
- Decision: 3 層構造（モジュラー演算 → 点の演算 → ECDSA プロトコル）で解説、全体コードを heredoc で末尾に配置
- Reason: セクションごとの解説を読みつつ、最後に全体をコピペで実行できる構成

## Resolution

記事を公開した。ブランチ: `blog-ecdsa-from-scratch`（dev ベース）
