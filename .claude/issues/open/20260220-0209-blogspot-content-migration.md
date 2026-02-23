# Issue: Blogspot（ktaka.blog.ccmp.jp）からのコンテンツ移行

## Table of Contents

- [Description](#description)
- [Related Issues](#related-issues)
- [Approach](#approach)
- [Related Files](#related-files)
- [Implementation Tasks](#implementation-tasks)
- [Decision Log](#decision-log)
- [Resolution](#resolution)

## ID: 20260220-0209

## Created: 2026-02-20-02-09

## Closed:

## Status: open

## Priority: high

## Difficulty: large

## Description

ktaka.blog.ccmp.jp は現在 Google Blogspot で稼働中。10〜50件の記事があり、画像はBlogspot/Google側にホストされている。URLはカスタムパスを使用。

このリポジトリの一部の記事はBlogspotにも公開されているが、**大半の記事はBlogspotの管理画面から直接入稿されたもの**で、このリポジトリには存在しない。

最終目標は、Blogspotの全コンテンツをGitHub Pages（このリポジトリ）に移行し、ktaka.blog.ccmp.jpのドメインをGitHub Pagesに向けること。

### 移行対象

| カテゴリ | 内容 |
|---------|------|
| 記事本文 | Blogspotの全記事（10〜50件、HTML形式） |
| 画像・メディア | Google/Bloggerサーバーにホストされている画像 |
| URLパス | カスタムパス（変更不可の要件） |
| メタデータ | 投稿日、タイトル、ラベル/タグ等 |

### 課題

1. **コンテンツ抽出**: BlogspotからのエクスポートはXML形式（Atom Feed）。HTML→Markdown変換が必要
2. **画像の移行**: Blogspot/Googleサーバー上の画像をダウンロードしてリポジトリ内に配置する必要がある
3. **URLパス保持**: Blogspotのカスタムパスと同じパスでGitHub Pagesから配信する必要がある
4. **HTML→Markdown変換**: Blogspot記事はHTML。Markdown（or Zola用MD）への変換品質が問題
5. **コードブロック**: 技術記事のコードブロックが変換で崩れる可能性
6. **このリポジトリ由来の記事との重複整理**: 一部の記事はリポジトリのMarkdownから作成されており、Blogspot版とリポジトリ版で整合性を取る必要がある

## Related Issues

- `20260220-0208` Zola入稿システム検討 (depends on: 移行先のフォーマットがZola or pandocかで変換方法が変わる)
- `20260220-0210` URL変更 (depends on: コンテンツ移行完了後にドメイン切替を行う)

## Approach

### フェーズ1: 現状調査・棚卸し

1. Blogspotの全記事一覧を取得（管理画面 or XMLエクスポート）
2. 各記事のURL、タイトル、投稿日、画像有無を一覧化
3. このリポジトリに既存の記事との対応関係を整理
4. 移行対象・移行不要（重複）・移行スキップの仕分け

### フェーズ2: エクスポート・変換

1. Blogspot管理画面からXMLエクスポート（設定 → その他 → コンテンツをバックアップ）
2. XMLからHTML記事を抽出
3. HTML→Markdown変換（pandoc or 専用ツール）
4. 画像のダウンロード（`blogger.googleusercontent.com` 等から）
5. 画像パスの書き換え（リポジトリ内の相対パスへ）

### フェーズ3: 変換品質の確認・手動修正

1. 変換後のMarkdownをレンダリングして原文と比較
2. コードブロック、テーブル、リスト等の崩れを手動修正
3. 画像の表示確認

### フェーズ4: URL設計・配置

1. Blogspotのカスタムパスに合わせた出力パスを設計
2. Zola使用時は `path` front matterで指定
3. 全URLの動作テスト

## Related Files

- `.github/workflows/pages.yml` — デプロイワークフロー
- `2013/` 〜 `2026/` — 既存のリポジトリ内記事

## Implementation Tasks

- [ ] Blogspot記事の棚卸し（全記事一覧の作成）
- [ ] リポジトリ既存記事との対応関係整理
- [ ] BlogspotからXMLエクスポート
- [ ] HTML→Markdown変換パイプラインの構築
- [ ] 画像のダウンロード・リポジトリ内配置
- [ ] 画像パスの書き換え
- [ ] 変換品質の確認・手動修正
- [ ] URLパス設計・配置
- [ ] 全記事の動作テスト

## Decision Log

<!-- APPEND-ONLY: Do not edit or delete existing entries. Add new entries at the bottom. -->

### 2026-02-20: Blogspotからの全コンテンツ移行として定義

- Context: 当初「ktaka.blog.ccmp.jpからのコンテンツ移動」として提起。調査の結果、ktaka.blog.ccmp.jpはBlogspotで稼働中で、大半の記事はBlogspot管理画面から直接入稿されたものと判明
- Decision: Blogspot XMLエクスポート → HTML→Markdown変換 → GitHub Pages配置、という移行パイプラインを構築する
- Reason: Blogspot記事はHTMLベースでGoogle側に画像がホストされているため、単純なファイルコピーでは移行できない。体系的なエクスポート・変換プロセスが必要

## Resolution
