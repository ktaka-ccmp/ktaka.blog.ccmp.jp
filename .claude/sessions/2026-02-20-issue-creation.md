# Session Snapshot: ブログ改善イシュー作成

## Current Task

ブログ改善に関する4つのトピックを調査・検討し、イシューとして起票した。

## Files Modified

### 新規作成
- `.claude/issues/open/20260220-0207-theme-css-improvement.md` — 見た目改善イシュー
- `.claude/issues/open/20260220-0208-zola-evaluation.md` — Zola入稿システム評価イシュー
- `.claude/issues/open/20260220-0209-blogspot-content-migration.md` — Blogspotコンテンツ移行イシュー
- `.claude/issues/open/20260220-0210-domain-migration.md` — ドメイン変更イシュー

### 変更
- `.claude/issues/README.md` — Open issues テーブルに4件追加（0→4）

## Key Decisions

1. **依存関係の整理**: Zola評価（0208）が他イシューのアプローチを左右するため、最優先で着手すべき
2. **Blogspot移行の規模感確認**: ktaka.blog.ccmp.jpはBlogspotで稼働中、10〜50件の記事あり。画像はGoogle側ホスト、URLはカスタムパス。大半の記事はBlogspot管理画面から直接入稿されたもの
3. **ドメイン切替はコンテンツ移行完了後**: 404を避けるため、全記事がGitHub Pagesで配信可能になってからドメインを切り替える方針

## Next Steps

- **最優先**: `20260220-0208` Zola評価 — PoCとして1記事をZola化し動作確認
- **並行可**: `20260220-0209` Blogspot棚卸し — Blogspot管理画面からXMLエクスポート、全記事一覧の作成
- **待ち**: `20260220-0207` 見た目改善 — Zola判断後にアプローチ確定
- **待ち**: `20260220-0210` ドメイン変更 — コンテンツ移行完了後

## Context

- リポジトリ: https://github.com/ktaka-ccmp/ktaka.blog.ccmp.jp
- 現在のGitHub Pages URL: https://kt.blog.ccmp.jp/
- 現在のBlogspot URL: https://ktaka.blog.ccmp.jp/
- 最終目標: ktaka.blog.ccmp.jp をGitHub Pages（Zola）で運用し、Blogspot全コンテンツを移行
- リポジトリ内既存記事: 11記事（2013-2026）、うちGitHub Pagesでビルド済みは1記事のみ
