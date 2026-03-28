# Issue: Qiita クロスポスト

## Table of Contents

- [Description](#description)
- [Related Issues](#related-issues)
- [Approach](#approach)
- [Related Files](#related-files)
- [Implementation Tasks](#implementation-tasks)
- [Decision Log](#decision-log)
- [Resolution](#resolution)

## ID: 20260328-0300

## Created: 2026-03-28-03-00

## Closed: 2026-03-28

## Status: completed

## Priority: low

## Difficulty: medium

## Description

日本語記事を Qiita にもクロスポストする。

## Related Issues

- `20260328-0100` Zenn クロスポスト — ECDSA 記事 2 本 (open)
- `20260328-0200` dev.to クロスポスト — ECDSA 英語記事 2 本 (open)

## Approach

- `qiita/public/` に Qiita CLI 形式の Markdown を配置
- GitHub Actions で Qiita CLI を直接実行（公式アクションは master に直接 push するため使えない）
- 投稿後の metadata 書き戻しは自動 PR（dev ブランチ向け）で反映
- GIF はブログの `content/` に配置し、ブログ URL で参照

## Related Files

- `qiita/public/oauth2-passkey-demo.md` — Oauth2PasskeyDemo の Qiita 版
- `.github/workflows/qiita-publish.yml` — Qiita 投稿ワークフロー
- `.claude/skills/qiita-crosspost/SKILL.md` — `/qiita-crosspost` スキル

## Implementation Tasks

- [x] 課題の解決策を決める（`--root qiita` でディレクトリ衝突回避、CLI 直接実行で master push 回避）
- [x] Qiita 用記事作成（Oauth2PasskeyDemo）
- [x] GitHub Actions ワークフロー作成
- [x] GIF をブログの content/ に移動
- [x] `/qiita-crosspost` スキル作成
- [x] CLAUDE.md にクロスポスト方針を追記
- [x] Qiita への投稿確認

## Decision Log

<!-- APPEND-ONLY: Do not edit or delete existing entries. Add new entries at the bottom. -->

### 2026-03-28: 調査の結果、課題が多いため deferred

- Context: Zenn + dev.to で JP/EN をカバーしており、Qiita を追加するメリットと課題を検討
- Decision: 保留
- Reason: 以下の課題がある
  1. **canonical_url 非対応** — Qiita の frontmatter に canonical_url がなく、SEO 的に元ブログが正であることを宣言できない
  2. **ディレクトリ衝突** — Qiita CLI のデフォルト出力先 `public/` が Zola の `zola build` 出力先と衝突
  3. **CLI 追加** — Qiita CLI（Node.js）のインストールが必要

### 2026-03-28: 課題を解決して実装

- Context: ユーザーが Qiita への投稿を希望
- Decision: 課題を以下のように解決して実装
  1. canonical_url → 冒頭にクロスポスト注記で代替
  2. ディレクトリ衝突 → `--root qiita` で `qiita/public/` に分離
  3. CLI → GitHub Actions 内で `npm install` して実行
- Reason: ユーザーの要望。3 課題とも実用的な回避策が見つかった

### 2026-03-28: 公式アクションではなく CLI 直接実行を採用

- Context: `increments/qiita-cli/actions/publish@v1` が内部で `git push master` を試み、保護されたブランチで失敗
- Decision: CLI を直接実行し、metadata 書き戻しは自動 PR（dev ブランチ向け）で対応
- Reason: master ブランチが保護されているため直接 push できない

### 2026-03-28: GitHub Actions の PR 作成権限

- Context: `gh pr create` が `GitHub Actions is not permitted to create or approve pull requests` で失敗
- Decision: GitHub リポジトリの Settings → Actions → General → 「Allow GitHub Actions to create and approve pull requests」を有効化
- Reason: ワークフローから PR を自動作成するために必要

## Resolution

Qiita クロスポストの仕組みを構築した。Oauth2PasskeyDemo 記事を Qiita に投稿済み。GitHub Actions + Qiita CLI で自動投稿、metadata 書き戻しは自動 PR で対応。`/qiita-crosspost` スキルも作成。
