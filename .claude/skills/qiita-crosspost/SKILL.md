---
name: qiita-crosspost
description: 日本語ブログ記事を Qiita にクロスポストする
argument-hint: [記事パス（例: content/2026/Oauth2PasskeyDemo/index.md）]
disable-model-invocation: true
allowed-tools: Read, Write, Glob, Grep, Bash(zola:*), Bash(ls:*)
---

# Qiita クロスポスト

日本語ブログ記事 `$ARGUMENTS` を Qiita 用に変換して `qiita/public/` に保存する。

## 手順

1. **元記事を読む**: `$ARGUMENTS` を読み、タイトル・description・本文を取得する

2. **Qiita 用 frontmatter に変換**:
   - Zola の TOML frontmatter（`+++`）を Qiita の YAML frontmatter（`---`）に変換
   - 以下のフィールドを設定:
     ```yaml
     ---
     title: "元記事のタイトル"
     tags:
       - "Tag1"
       - "Tag2"
     private: false
     updated_at: ""
     id: null
     organization_url_name: null
     slide: false
     ignorePublish: false
     ---
     ```
   - tags は最大 5 つ
   - `id: null` で新規記事として投稿される（Qiita CLI が投稿後に id を書き戻す）
   - Qiita は `canonical_url` 非対応

3. **本文を変換**:
   - 冒頭に追加: `> この記事は [ktaka.blog.ccmp.jp の記事](ブログURL) のクロスポストです。`
   - `<p style="text-align: right"><a href="...">English version</a></p>` を削除
   - `<details>` / `<summary>` はそのまま使える（Qiita はサポート）
   - ブログ内リンク（`/2026/...`）→ ブログの絶対 URL（`https://ktaka.blog.ccmp.jp/...`）に変換
   - `<video>` タグ → ブログの GIF URL に置き換え（`https://ktaka.blog.ccmp.jp/.../video/name.gif`）。GIF がなければ mp4 から生成が必要な旨をユーザーに伝える
   - 画像の相対パス → ブログの絶対 URL に変換

4. **ファイルを保存**:
   - ディレクトリ: `qiita/public/`
   - ファイル名: `<スラッグ>.md`
   - 例: `qiita/public/oauth2-passkey-demo.md`

5. **確認**:
   - ユーザーに作成したファイルのパスを報告
   - master にマージすると GitHub Actions（Qiita CLI）が自動投稿することを案内
   - 投稿後に Qiita CLI が frontmatter に `id` と `updated_at` を書き戻し、自動 PR が dev ブランチに作成されることを案内

## GitHub Actions ワークフロー

- `.github/workflows/qiita-publish.yml` が `qiita/public/*.md` の変更を検出して Qiita CLI で投稿
- 投稿後の metadata 書き戻しは自動 PR（dev ブランチ向け）で反映
- `id: null` → 新規投稿、`id: xxx` → 既存記事の更新

## 注意

- Qiita は `canonical_url` に対応していない。冒頭のクロスポスト注記が唯一の元記事への導線
- tags は Qiita のコミュニティタグに合わせる（大文字小文字あり、日本語も可）
- `<video>` タグは使えない。GIF に変換してブログ URL で参照する
- 日本語記事のみ（英語記事は dev.to へ: `/devto-crosspost`）
