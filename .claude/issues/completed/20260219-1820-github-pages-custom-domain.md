# Issue: GitHub Pagesでkt.blog.ccmp.jpとしてブログを公開する

## Table of Contents

- [Description](#description)
- [Related Issues](#related-issues)
- [Approach](#approach)
- [Related Files](#related-files)
- [Implementation Tasks](#implementation-tasks)
- [Decision Log](#decision-log)
- [Resolution](#resolution)

## ID: 20260219-1820

## Created: 2026-02-19-18-20

## Closed: 2026-02-19-19-00

## Status: completed

## Priority: high

## Difficulty: medium

## Description

GitHub Actions経由で、リポジトリ https://github.com/ktaka-ccmp/ktaka.blog.ccmp.jp のコンテンツを、カスタムドメイン `kt.blog.ccmp.jp` で GitHub Pages として公開する。

現在、記事は Markdown と HTML 形式で年ごとのディレクトリに格納されている。これらを GitHub Pages で配信できるようにする。

## Related Issues

(なし)

## Approach

1. DNS側で `kt.blog.ccmp.jp` の CNAME レコードを `ktaka-ccmp.github.io.` に向ける
2. GitHub リポジトリの Settings → Pages で Source を GitHub Actions に設定し、Custom domain に `kt.blog.ccmp.jp` を設定
3. GitHub Actions ワークフロー（`.github/workflows/`）を作成し、`actions/upload-pages-artifact` + `actions/deploy-pages` でデプロイ
4. HTTPS は GitHub が Let's Encrypt で自動発行

## Related Files

- `.github/workflows/pages.yml`
- `github-markdown.css`
- `2026/GcpToGitHubPages/Readme.jp.md`

## Implementation Tasks

- [x] DNS に CNAME レコード追加 (`kt.blog.ccmp.jp` → `ktaka-ccmp.github.io.`)
- [x] GitHub Actions ワークフローファイルを作成
- [x] GitHub リポジトリ Settings → Pages でカスタムドメインを設定
- [x] HTTPS の有効化を確認
- [x] デプロイの動作確認

## Decision Log

<!-- APPEND-ONLY: Do not edit or delete existing entries. Add new entries at the bottom. -->

### 2026-02-19: GitHub Pages + カスタムドメインで公開する方針を決定

- Context: ブログコンテンツを独自ドメインで公開したいという要件
- Decision: GitHub Pages + GitHub Actions + カスタムドメイン（CNAME）の構成を採用
- Reason: リポジトリが既に GitHub にあり、GitHub Pages は無料で HTTPS も自動対応。追加のホスティングサービスが不要

## Resolution

GitHub Actions ワークフロー（`.github/workflows/pages.yml`）を作成し、pandoc で Markdown → HTML 変換 + GitHub Pages デプロイを自動化。DNS CNAME レコード追加とカスタムドメイン設定により、`https://kt.blog.ccmp.jp/` でアクセス可能になった。
