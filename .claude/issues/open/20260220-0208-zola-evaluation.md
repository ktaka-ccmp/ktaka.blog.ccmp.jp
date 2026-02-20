# Issue: 入稿システム検討 — Zola静的サイトジェネレーター評価・導入

## Table of Contents

- [Description](#description)
- [Related Issues](#related-issues)
- [Approach](#approach)
- [Related Files](#related-files)
- [Implementation Tasks](#implementation-tasks)
- [Decision Log](#decision-log)
- [Resolution](#resolution)

## ID: 20260220-0208

## Created: 2026-02-20-02-08

## Closed:

## Status: open

## Priority: high

## Difficulty: large

## Description

現在のブログは pandoc + GitHub Actions の手動構成。記事追加のたびにワークフローYAMLの編集が必要で、スケーラビリティに問題がある。静的サイトジェネレーター Zola（https://www.getzola.org/）の導入を検討する。

### 現在の課題

- 記事追加ごとに `.github/workflows/pages.yml` を手動編集（mkdir, pandocコマンド, index更新）
- ローカルプレビューが手動（pandoc実行 → ブラウザで開く）
- TOC生成は外部ツール（`gh-md-toc`）に依存
- シンタックスハイライト、RSS、検索、サイトマップなし
- 多言語対応が手動（`.en.md` / `.jp.md` のリンクを自分で管理）

### Zola導入のメリット

| 機能 | 現在 | Zola導入後 |
|------|------|-----------|
| 記事追加 | YAML手動編集 | MDファイル作成のみ（自動検出） |
| ローカルプレビュー | pandoc手動実行 | `zola serve`（ライブリロード） |
| TOC | 外部ツール | 標準搭載 |
| シンタックスハイライト | なし | 標準搭載（syntect） |
| RSS/Atom | なし | 自動生成 |
| 検索 | なし | 標準搭載 |
| サイトマップ | なし | 自動生成 |
| 多言語 | 手動 | 標準搭載（i18n） |
| テーマ | CSS単体 | 150+テーマ |

### Zola導入の懸念点

- 全11記事にfront matter（TOML）追加が必要
- ディレクトリ構造の再編成（`content/` 配下への移動）
- Teraテンプレートエンジンの学習コスト
- テーマ選定・カスタマイズの手間
- Hugo/Jekyllより小さいエコシステム（テーマ150+ vs Hugo 500+）
- pandocのような多フォーマット出力（PDF等）は不可

### URLパス保持

Zolaの `path` front matterでカスタムパス指定可能:
```toml
+++
path = "2026/GcpToGitHubPages"
+++
```
現在のワークフローが `index.html` を出力しているため、ZolaのクリーンURL（`/2026/GcpToGitHubPages/`）と互換。

## Related Issues

- `20260220-0207` 見た目改善 (blocks: Zola判断がアプローチを決定する)
- `20260220-0209` Blogspotコンテンツ移行 (related to: Zola導入ならコンテンツ形式をZola用に変換)
- `20260220-0210` URL変更 (related to: ドメイン切替と同時に進める可能性)

## Approach

段階的に導入を進める:

1. **PoC（概念実証）**: 既存の1記事をZola化して動作確認
   - Zolaインストール、`config.toml` 作成
   - テーマ選定（技術ブログ向け: DeepThought, even 等）
   - `2026/GcpToGitHubPages/Readme.jp.md` をZola形式に変換
   - `zola serve` でローカル確認
   - URLパス保持の検証

2. **既存記事の移行**: 残り10記事をZola形式に変換
   - front matter追加
   - ディレクトリ構造調整
   - 画像・アセットの配置

3. **GitHub Actionsワークフロー更新**: pandocからZolaビルドに切替
   - `shalzz/zola-deploy-action` または手動Zolaビルド
   - CNAME設定の維持

4. **旧ファイルの整理**: 不要になったファイルの削除
   - `gh-md-toc`, `github-markdown.css`（テーマ側で対応）
   - 旧pandocワークフロー

## Related Files

- `.github/workflows/pages.yml` — 現在のpandocベースワークフロー
- `github-markdown.css` — 現在のCSS（Zola移行後は不要）
- `gh-md-toc` — TOCジェネレーター（Zola移行後は不要）
- `2026/GcpToGitHubPages/Readme.jp.md` — PoC対象記事

## Implementation Tasks

- [ ] Zolaインストール・動作確認
- [ ] テーマ候補の選定・比較
- [ ] PoC: 1記事のZola化＋ローカル動作確認
- [ ] URLパス保持の検証
- [ ] 多言語対応の検証（.en.md / .jp.md）
- [ ] 残り記事のZola形式変換
- [ ] GitHub Actionsワークフロー更新
- [ ] 旧ファイル整理

## Decision Log

<!-- APPEND-ONLY: Do not edit or delete existing entries. Add new entries at the bottom. -->

### 2026-02-20: Zola を評価対象として選定

- Context: 入稿システムの改善が必要。現在のpandoc手動構成はスケールしない
- Decision: Zolaを第一候補として評価する（Hugo, Jekyll等は現時点では比較対象外）
- Reason: ユーザーがZolaを候補として提示。Rust製の単一バイナリで依存なし、GitHub Pages対応、URLパス保持可能、多言語対応ありと要件に合致

## Resolution
