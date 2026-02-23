# Session Snapshot: GitHub Pages セットアップ

## Current Task

GitHub Pages でブログ（kt.blog.ccmp.jp）を公開する作業。初期セットアップ完了、イシュークローズ済み。

## Files Modified

### 新規作成
- `CLAUDE.md` — プロジェクト設定
- `.github/workflows/pages.yml` — GitHub Actions ワークフロー（pandoc で md→html 変換、GitHub Pages デプロイ）
- `.claude/commands/issue.md` — `/issue` コマンド定義
- `.claude/commands/backlog.md` — `/backlog` コマンド定義
- `.claude/commands/snapshot.md` — `/snapshot` コマンド定義
- `.claude/issues/README.md` — イシュー管理テンプレート・ルール
- `.claude/issues/completed/20260219-1820-github-pages-custom-domain.md` — 完了イシュー
- `.claude/issues/{open,completed,deferred,wontfix}/.gitkeep`
- `.claude/sessions/.gitkeep`

### 変更
- `~/.claude/CLAUDE.md` — git add/commit をユーザー承認付きで AI 実行可能に緩和（git push は引き続きユーザー専用）

## Key Decisions

1. **GitHub Pages + GitHub Actions + カスタムドメイン（CNAME）** の構成を採用
2. **pandoc** で Markdown → HTML 変換（リポジトリ内の `github-markdown.css` を適用）
3. ワークフローのトリガーは **master ブランチ** への push
4. CNAME ファイルはワークフロー内で動的生成（`echo "kt.blog.ccmp.jp" > _site/CNAME`）
5. oauth2-passkey リポジトリの簡易イシューシステムをそのまま導入

## Next Steps

- 見た目の調整（CSS の適用具合、レイアウト改善）
- 他の記事の追加（ワークフローを拡張して他の年の記事も変換・デプロイ）
- トップページ（index.html）のデザイン改善

## Context

- リポジトリ: https://github.com/ktaka-ccmp/ktaka.blog.ccmp.jp
- 公開URL: https://kt.blog.ccmp.jp/
- 記事URL: https://kt.blog.ccmp.jp/2026/GcpToGitHubPages/
- DNS: `kt.blog.ccmp.jp. IN CNAME ktaka-ccmp.github.io.`
- 現在公開中の記事: `2026/GcpToGitHubPages/Readme.jp.md`（GCP → GitHub Pages 移行記事）のみ
