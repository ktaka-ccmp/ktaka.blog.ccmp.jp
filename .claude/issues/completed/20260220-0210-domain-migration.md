# Issue: ドメイン変更 kt.blog.ccmp.jp → ktaka.blog.ccmp.jp

## Table of Contents

- [Description](#description)
- [Related Issues](#related-issues)
- [Approach](#approach)
- [Related Files](#related-files)
- [Implementation Tasks](#implementation-tasks)
- [Decision Log](#decision-log)
- [Resolution](#resolution)

## ID: 20260220-0210

## Created: 2026-02-20-02-10

## Closed: 2026-02-23

## Status: completed

## Priority: medium

## Difficulty: medium

## Description

現在のGitHub Pagesブログは `kt.blog.ccmp.jp` で公開中。これを `ktaka.blog.ccmp.jp` に変更する。

### 背景

- `ktaka.blog.ccmp.jp` は現在 Blogspot を指している
- `kt.blog.ccmp.jp` は現在 GitHub Pages を指している（`ktaka-ccmp.github.io` へのCNAME）
- Blogspotからのコンテンツ移行完了後、`ktaka.blog.ccmp.jp` をGitHub Pagesに向け替える

### 影響範囲

1. **DNS**: `ktaka.blog.ccmp.jp` のCNAMEをBlogspot → `ktaka-ccmp.github.io` に変更
2. **GitHub Pages設定**: カスタムドメインを `kt.blog.ccmp.jp` → `ktaka.blog.ccmp.jp` に変更
3. **GitHub Actionsワークフロー**: CNAME出力を更新
4. **旧ドメイン `kt.blog.ccmp.jp`**: リダイレクト or 廃止の判断が必要
5. **既存リンク**: `kt.blog.ccmp.jp` への外部リンクが切れる
6. **Blogspot側**: Blogspotのカスタムドメイン設定を解除する必要がある

### 制約

- GitHub Pages単体では301リダイレクト（旧ドメイン→新ドメイン）は提供されない
- `kt.blog.ccmp.jp` からのリダイレクトが必要な場合、別途仕組みが必要（meta refresh、Cloudflare等）

## Related Issues

- `20260220-0209` Blogspotコンテンツ移行 (depends on: コンテンツ移行完了後にドメイン切替を行う)
- `20260220-0208` Zola入稿システム検討 (related to: Zolaの `base_url` 設定変更が必要)
- `20260220-0207` 見た目改善 (related to: ドメイン変更と同時にデザイン刷新も可能)

## Approach

### 前提条件

- `20260220-0209`（Blogspotコンテンツ移行）が完了していること
- 全記事が GitHub Pages から配信可能な状態であること

### 切替手順

1. **事前準備**
   - Blogspotコンテンツ移行の完了確認
   - 全URLの動作テスト（GitHub Pages上で全記事が閲覧可能）
   - 切替手順のリハーサル

2. **Blogspot側設定解除**
   - Blogspot管理画面でカスタムドメイン (`ktaka.blog.ccmp.jp`) を解除
   - Blogspotの元のURL（`xxxx.blogspot.com`）に戻る

3. **DNS変更**
   - `ktaka.blog.ccmp.jp` のCNAMEを `ktaka-ccmp.github.io` に変更
   - TTLを事前に短くしておく（切替前に300秒等に設定）
   - DNS伝播の確認

4. **GitHub Pages設定変更**
   - リポジトリ Settings → Pages → Custom domain を `ktaka.blog.ccmp.jp` に変更
   - HTTPS の有効化確認（Let's Encrypt証明書の自動発行）

5. **ワークフロー更新**
   - `.github/workflows/pages.yml` のCNAME出力を `ktaka.blog.ccmp.jp` に変更
   - Zola使用時は `config.toml` の `base_url` を更新

6. **旧ドメイン対応**
   - `kt.blog.ccmp.jp` の扱いを決定（廃止 or リダイレクト）
   - リダイレクトする場合の方式を決定

7. **事後確認**
   - 全ページの表示確認
   - HTTPS証明書の確認
   - 検索エンジンへのサイトマップ再送信

## Related Files

- `.github/workflows/pages.yml` — CNAME出力箇所
- `CLAUDE.md` — ドメイン参照箇所

## Implementation Tasks

- [x] `20260220-0209` Blogspotコンテンツ移行の完了を待つ
- [x] 切替手順の詳細化・リハーサル
- [x] DNS TTL短縮（切替数日前）
- [x] Blogspotカスタムドメイン解除
- [x] DNS CNAME変更
- [x] GitHub Pagesカスタムドメイン変更
- [x] ワークフロー/設定ファイルのドメイン更新（`config.toml`, `static/CNAME`, `CLAUDE.md`）
- [x] 旧ドメイン（kt.blog.ccmp.jp）の扱い決定・対応 → 廃止
- [x] 全ページ動作確認
- [x] HTTPS確認

## Decision Log

<!-- APPEND-ONLY: Do not edit or delete existing entries. Add new entries at the bottom. -->

### 2026-02-20: コンテンツ移行完了後にドメイン切替を行う方針

- Context: ドメイン変更とコンテンツ移行が同時に必要。順序を決める必要がある
- Decision: Blogspotコンテンツ移行（20260220-0209）を先に完了させ、全記事がGitHub Pagesで閲覧可能な状態になってからドメイン切替を行う
- Reason: ドメインを先に切り替えるとコンテンツ未移行の記事が404になる。ユーザーへの影響を最小化するため、コンテンツ準備完了後に一括切替が適切

### 2026-02-23: 旧ドメイン kt.blog.ccmp.jp を廃止する方針

- Context: 旧ドメインをリダイレクトするか廃止するかの判断が必要だった
- Decision: `kt.blog.ccmp.jp` は廃止とする（リダイレクト不要）
- Reason: ユーザーの判断により、旧ドメインへの外部リンクは少なく、リダイレクトの仕組みを構築するコストに見合わないと判断

## Resolution

ドメイン移行を完了。以下の変更を実施：

1. **手動作業**（ユーザーが実施）:
   - Blogspotカスタムドメイン解除
   - DNS CNAME変更（`ktaka.blog.ccmp.jp` → `ktaka-ccmp.github.io`）
   - GitHub Pages カスタムドメイン設定変更

2. **コード変更**（PR #42, #43 でマージ済み）:
   - `config.toml`: `base_url` を `https://ktaka.blog.ccmp.jp` に変更
   - `static/CNAME`: `ktaka.blog.ccmp.jp` に変更
   - `CLAUDE.md`: ドメイン参照を更新

3. **旧ドメイン**: `kt.blog.ccmp.jp` は廃止（リダイレクトなし）
