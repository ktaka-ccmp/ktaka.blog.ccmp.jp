---
name: devto-crosspost
description: 英語ブログ記事を dev.to にクロスポストする
argument-hint: [記事パス（例: content/2026/WebCryptoEcdsaEn/index.md）]
disable-model-invocation: true
allowed-tools: Read, Write, Glob, Grep, Bash(zola:*), Bash(ls:*)
---

# dev.to クロスポスト

英語ブログ記事 `$ARGUMENTS` を dev.to 用に変換して `docs/` に保存する。

## 手順

1. **元記事を読む**: `$ARGUMENTS` を読み、タイトル・description・本文を取得する

2. **dev.to 用 frontmatter に変換**:
   - Zola の TOML frontmatter（`+++`）を dev.to の YAML frontmatter（`---`）に変換
   - 以下のフィールドを設定:
     ```yaml
     ---
     title: "元記事のタイトル"
     published: false
     description: "元記事の description"
     tags: tag1, tag2, tag3, tag4
     canonical_url: https://ktaka.blog.ccmp.jp/元記事のpath
     ---
     ```
   - `published: false`（下書き）で作成
   - tags は最大 4 つ、カンマ区切り

3. **本文を変換**:
   - `<p style="text-align: right"><a href="...">日本語版</a></p>` を削除
   - `<details><summary>タイトル</summary>...</details>` → `{% details タイトル %}...{% enddetails %}` に変換（dev.to は `<details>` を除去するため Liquid タグを使う）
   - ブログ内リンク（`/en/2026/...` や `/2026/...`）→ ブログの絶対 URL（`https://ktaka.blog.ccmp.jp/...`）に変換
   - 画像の相対パス → ブログの絶対 URL に変換（該当がある場合）

4. **ファイルを保存**:
   - ディレクトリ: `devto/`
   - ファイル名: `dev-to-<スラッグ>.md`
   - 例: `devto/dev-to-webcrypto-ecdsa.md`

5. **確認**:
   - ユーザーに作成したファイルのパスと `published` 状態を報告
   - master にマージすると GitHub Actions が自動で dev.to に投稿することを案内

## GitHub Actions ワークフロー

- `.github/workflows/devto-publish.yml` が `devto/*.md` の変更を検出して自動投稿
- `canonical_url` で既存記事を検索し、あれば PUT（更新）、なければ POST（新規）
- `published: false` → 下書き、`published: true` → 公開
- 公開/非公開の変更もファイルを編集して push すれば自動反映

## 注意

- `canonical_url` を必ず設定する（SEO で元ブログが正となるように）
- dev.to の `<details>` は機能しない。必ず `{% details %}...{% enddetails %}` を使う
- tags は最大 4 つ
- dev.to は英語記事のみ（日本語記事は Zenn へ: `/zenn-crosspost`）
