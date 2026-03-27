---
name: zenn-crosspost
description: ブログ記事を Zenn にクロスポストする
argument-hint: [記事パス（例: content/2026/WebCryptoEcdsa/index.md）]
disable-model-invocation: true
allowed-tools: Read, Write, Glob, Grep, Bash(zola:*), Bash(ls:*)
---

# Zenn クロスポスト

ブログ記事 `$ARGUMENTS` を Zenn 用に変換して `articles/` に保存する。

## 手順

1. **元記事を読む**: `$ARGUMENTS` を読み、タイトル・description・本文を取得する

2. **Zenn 用 frontmatter に変換**:
   - Zola の TOML frontmatter（`+++`）を Zenn の YAML frontmatter（`---`）に変換
   - 以下のフィールドを設定:
     ```yaml
     ---
     title: "元記事のタイトル"
     emoji: "適切な絵文字"
     type: "tech"
     topics: ["関連トピック", "最大5つ", "小文字"]
     published: false
     canonical_url: "https://ktaka.blog.ccmp.jp/元記事のpath"
     ---
     ```
   - `published: false`（下書き）で作成し、確認後にユーザーが true に変更する

3. **本文を変換**:
   - 冒頭に追加: `> この記事は [ktaka.blog.ccmp.jp の記事](canonical_url) のクロスポストです。`
   - `<p style="text-align: right"><a href="...">English version</a></p>` を削除
   - `<details><summary>...</summary>...</details>` → `:::details タイトル ... :::` に変換
   - ブログ内リンク（`/2026/...`）→ Zenn 内リンク（`/ktaka3/articles/スラッグ`）に変換（対応する Zenn 記事がある場合）。ない場合はブログの絶対 URL（`https://ktaka.blog.ccmp.jp/...`）に変換
   - 画像の相対パス → ブログの絶対 URL に変換（該当がある場合）

4. **ファイル名を決める**:
   - `articles/` に保存
   - スラッグは記事内容から英語のケバブケースで命名（12〜50文字、小文字英数字とハイフンのみ）
   - 例: `articles/webcrypto-ecdsa-signing-verification.md`

5. **確認**:
   - `zola build` で既存サイトに影響がないことを確認
   - ユーザーに作成したファイルのパスと `published` 状態を報告

## Zenn ユーザー情報

- ユーザー名: `ktaka3`
- Zenn 記事 URL: `https://zenn.dev/ktaka3/articles/<スラッグ>`
- Zenn 内リンク: `/ktaka3/articles/<スラッグ>`

## 既存の Zenn 記事

作成前に `articles/` ディレクトリを確認し、既存記事とのリンク関係を把握すること。

## 注意

- `canonical_url` を必ず設定する（SEO で元ブログが正となるように）
- Zenn のトピックは小文字英数字のみ
- emoji は記事の内容に合ったものを 1 つ選ぶ
