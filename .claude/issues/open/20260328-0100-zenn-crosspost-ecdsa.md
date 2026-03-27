# Issue: Zenn クロスポスト — ECDSA 記事 2 本

## Table of Contents

- [Description](#description)
- [Related Issues](#related-issues)
- [Approach](#approach)
- [Related Files](#related-files)
- [Implementation Tasks](#implementation-tasks)
- [Decision Log](#decision-log)
- [Resolution](#resolution)

## ID: 20260328-0100

## Created: 2026-03-28-01-00

## Closed:

## Status: open

## Priority: high

## Difficulty: small

## Description

ECDSA 日本語記事 2 本を Zenn にクロスポストする。GitHub 連携で `articles/` ディレクトリに Markdown を置けば自動反映される。

1. Web Crypto API で ECDSA 署名・検証を理解する
2. ECDSA の計算をライブラリなしで実装する

## Related Issues

- `20260326-0420` Web Crypto API で ECDSA 署名・検証を理解する (completed)
- `20260327-0100` ECDSA の計算をライブラリなしで実装する (completed)

## Approach

- リポジトリルートに `articles/` ディレクトリを作成（Zenn CLI の規約）
- 元記事の Markdown をコピーし、Zenn 用 frontmatter（YAML）に差し替え
- `canonical_url` を元ブログに設定
- 冒頭に「この記事は ktaka.blog.ccmp.jp のクロスポストです」と明記
- 画像がある場合は外部 URL に差し替え（今回の記事には画像なし）

## Related Files

- `content/2026/WebCryptoEcdsa/index.md` — 元記事 1
- `content/2026/EcdsaFromScratch/index.md` — 元記事 2

## Implementation Tasks

- [x] `articles/` ディレクトリ作成
- [x] WebCryptoEcdsa の Zenn 版作成（`published: true`）
- [x] EcdsaFromScratch の Zenn 版作成（`published: false`、1本目公開後に変更予定）
- [x] `zola build` で既存サイトに影響ないことを確認
- [x] `/zenn-crosspost` スキル作成
- [ ] push 後に Zenn で反映確認
- [ ] EcdsaFromScratch を `published: true` に変更して push

## Decision Log

<!-- APPEND-ONLY: Do not edit or delete existing entries. Add new entries at the bottom. -->

### 2026-03-28: 既存リポジトリに articles/ を追加する方式を採用

- Context: Zenn は articles/ がリポジトリルート固定。別リポジトリか同一リポジトリか選択が必要
- Decision: 既存の Zola ブログリポジトリに articles/ を追加
- Reason: シンプル。Zola は articles/ を無視するので共存可能

### 2026-03-28: 公開順序の制御と /zenn-crosspost スキル作成

- Context: 2本同時に push すると Zenn での表示順が不定
- Decision: 1本目を published: true、2本目を published: false で push。確認後に2本目を公開
- Reason: WebCryptoEcdsa → EcdsaFromScratch の順序を確実にする

- Context: 今後もクロスポストを行う可能性がある
- Decision: `/zenn-crosspost` スキルを作成（`.claude/skills/zenn-crosspost/SKILL.md`）
- Reason: frontmatter 変換、リンク修正、details 記法変換などの手順をスキル化

## Resolution
