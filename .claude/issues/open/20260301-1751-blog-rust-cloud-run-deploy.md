# Issue: ブログ記事 — Rust アプリを 27MB Docker イメージで Cloud Run にデプロイ

## Table of Contents

- [Description](#description)
- [Related Issues](#related-issues)
- [Approach](#approach)
- [Related Files](#related-files)
- [Implementation Tasks](#implementation-tasks)
- [Decision Log](#decision-log)
- [Resolution](#resolution)

## ID: 20260301-1751

## Created: 2026-03-01-17-51

## Closed:

## Status: open

## Priority: medium

## Difficulty: large

## Description

oauth2-passkey デモサイトの Cloud Run デプロイ過程をブログ記事にする。Docker イメージ最適化（111MB → 27.7MB）、Cloud Run 設定、GitHub Actions 自動デプロイ、プラットフォーム比較を含む。シリーズ3本中の第2弾。

タイトル案: "Deploying a Rust Web App to Cloud Run with a 27MB Docker Image"

言語: 英語

## Related Issues

- `20260301-1750` Blog: oauth2-passkey Introduction (シリーズ第1弾)
- `20260301-1752` Blog: Async Rust Pitfalls (シリーズ第3弾)

## Approach

### アウトライン

1. **Introduction** — デモサイトデプロイの背景（記事1へリンク）
2. **Docker Image Optimization** — debian 111MB → scratch 27.7MB、webpki-roots、bundled-tls feature flag
3. **Cloud Run Deployment** — GCP setup, Secret Manager, Cloud Build, カスタムドメイン
4. **GitHub Actions Auto-Deploy** — サービスアカウント、IAM ロール、Cloud Build ログ問題
5. **Platform Comparison** — Fly.io/Render/Railway/Oracle Cloud/Cloud Run 比較表
6. **Docker Gotchas** — env-file 引用符問題、Alpine musl の注意点
7. **Conclusion** — 記事1・3 へのリンク

### 素材

- ジャーナル 0205.md (2/12 Cloud Run デプロイ、Docker 最適化)
- ジャーナル 0213.md (2/13 GitHub Actions、Cloud Build ログ問題)
- イシュー `~/GitHub/oauth2-passkey/.claude/issues/completed/2026-01-30-demo-site-deployment.md`

### スクリーンショット/図

- Docker イメージサイズ比較表
- Cloud Run コンソール
- GitHub Actions 実行画面
- アーキテクチャ図 (GitHub → Cloud Build → Artifact Registry → Cloud Run)

### サイズ目安

14-18KB

## Related Files

- `content/2026/RustCloudRunDeploy/index.md` (新規作成)
- `~/GitHub/oauth2-passkey/.claude/issues/completed/2026-01-30-demo-site-deployment.md` (素材)
- `~/GitHub/oauth2-passkey/demo-live/Dockerfile` (素材)
- `~/GitHub/oauth2-passkey/demo-live/DEPLOY.md` (素材)
- `~/GitHub/daily-journal/ktaka/2026/0205.md` (素材)
- `~/GitHub/daily-journal/ktaka/2026/0213.md` (素材)

## Implementation Tasks

- [ ] 記事ディレクトリ作成 (`content/2026/RustCloudRunDeploy/`)
- [ ] index.md 執筆（front matter + 本文）
- [ ] スクリーンショット撮影・配置
- [ ] 相互リンク設定（記事1・3）
- [ ] `zola build` で確認

## Decision Log

<!-- APPEND-ONLY: Do not edit or delete existing entries. Add new entries at the bottom. -->

### 2026-03-01: シリーズ第2弾として位置づけ

- Context: デプロイ内容を独立した記事にするか、記事1に含めるか
- Decision: 独立した記事として第2弾に位置づける
- Reason: Docker 最適化や Cloud Run デプロイは認証ライブラリと独立した関心事であり、Rust デプロイや Docker に興味がある別の読者層にもアピールできる

## Resolution
