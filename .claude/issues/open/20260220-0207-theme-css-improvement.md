# Issue: ブログの見た目改善（テーマ・CSS・レイアウト）

## Table of Contents

- [Description](#description)
- [Related Issues](#related-issues)
- [Approach](#approach)
- [Related Files](#related-files)
- [Implementation Tasks](#implementation-tasks)
- [Decision Log](#decision-log)
- [Resolution](#resolution)

## ID: 20260220-0207

## Created: 2026-02-20-02-07

## Closed:

## Status: open

## Priority: medium

## Difficulty: medium

## Description

現在のブログ（kt.blog.ccmp.jp）は `github-markdown.css` + pandoc の最小構成で、機能的には動作するが、ブログとしての体裁が不十分。

### 現状の問題点

1. **ナビゲーションなし** — ヘッダー/フッター、パンくずリスト、前後記事リンクがない
2. **インデックスページが貧弱** — GitHub Actionsワークフロー内でハードコードされたHTML。記事メタデータ（日付・要約）なし
3. **記事ページのレイアウト不統一** — コンテナ幅制限がインデックスのみで記事ページには適用されていない
4. **コードブロック** — 行番号なし、コピーボタンなし、シンタックスハイライトがpandoc依存
5. **モバイル対応** — 基本的なレスポンシブは効いているが最適化されていない

### 現状で動いているもの

- ダーク/ライトモードの自動切替（`prefers-color-scheme`）
- GitHub風のクリーンなMarkdownレンダリング
- テーブル、リスト、引用等の基本スタイリング

## Related Issues

- `20260220-0208` Zola入稿システム検討 (depends on: Zola導入ならテーマで対応するため、アプローチが大きく変わる)

## Approach

Zola導入の判断を先に行い、それに応じてアプローチを決定する。

**Zola導入する場合:**
- Zolaテーマ（DeepThought, even 等）で対応
- テーマのカスタマイズで要件を満たす

**Zola導入しない場合（pandoc継続）:**
- カスタムCSSの追加（ナビゲーション、レイアウト改善）
- pandocテンプレートの作成（ヘッダー/フッター埋め込み）
- インデックスページの生成スクリプト作成

## Related Files

- `github-markdown.css` — 現在のCSSファイル（28KB, 1196行）
- `.github/workflows/pages.yml` — ビルド・デプロイワークフロー
- `2026/GcpToGitHubPages/Readme.jp.md` — 現在唯一ビルドされている記事

## Implementation Tasks

- [ ] `20260220-0208` Zola導入の判断を待つ
- [ ] アプローチ確定後、具体的なタスクを追加

## Decision Log

<!-- APPEND-ONLY: Do not edit or delete existing entries. Add new entries at the bottom. -->

### 2026-02-20: イシュー作成、Zola判断待ち

- Context: ブログの見た目改善が求められているが、入稿システム変更の検討が並行している
- Decision: Zola導入の判断を先に行い、それに応じてアプローチを決定する
- Reason: Zola導入ならテーマで対応でき、pandoc用にカスタムCSS/テンプレートを作る作業が無駄になる

## Resolution
