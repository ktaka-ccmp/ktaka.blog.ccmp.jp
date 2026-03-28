---
name: crosspost-status
description: 全記事のクロスポスト配信状況を一覧表示する
disable-model-invocation: true
allowed-tools: Read, Glob, Grep, Bash(ls:*), Bash(grep:*)
---

# クロスポスト配信状況

2026 年以降のブログ記事について、各プラットフォームへの配信状況を一覧表示する。

## 手順

1. **ブログ記事を走査**: `content/2026/*/index.md` を一覧取得する。`*En/` で終わるディレクトリは英語版。

2. **各プラットフォームの対応ファイルを確認**:

   新方式（自動デプロイ）と旧方式（手動コピペ）の両方を走査する。

   **Zenn**:
   - 新方式: `articles/` 内のファイルの `canonical_url` で対応を特定
   - 旧方式: `docs/*-zenn/*.md` 内の冒頭クロスポスト注記の URL で対応を特定

   **dev.to**:
   - 新方式: `devto/` 内のファイルの `canonical_url` で対応を特定
   - 旧方式: `docs/*-devto/*.md` 内の `canonical_url` で対応を特定

   **Qiita**:
   - `qiita/public/` 内のファイルの冒頭クロスポスト注記の URL で対応を特定

3. **公開状態を確認**: 対応ファイルが見つかった場合、frontmatter から公開状態を判定:
   - **Zenn**: `published: true` → published、`published: false` → draft
   - **dev.to**: `published: true` → published、`published: false` → draft
   - **Qiita**: `id` が null でない → published（Qiita CLI が投稿後に id を設定する）、`ignorePublish: true` → ignored

4. **テーブルを出力**:

```
| 記事 | 言語 | Blog | Zenn | dev.to | Qiita |
|------|------|------|------|--------|-------|
| ArticleName | JP | ✅ | ✅ published | - | ❌ |
| ArticleNameEn | EN | ✅ | - | ✅ published (docs/) | - |
```

凡例:
- `✅ published` — 公開済み（新方式）
- `✅ published (docs/)` — 公開済み（旧方式、手動コピペ）
- `📝 draft` — 下書き
- `❌` — 未作成（対象プラットフォームにファイルがない）
- `-` — 対象外（JP 記事の dev.to、EN 記事の Zenn/Qiita）

## 対象プラットフォームの判定

- **JP 記事**（`*En/` で終わらないディレクトリ）: Blog, Zenn, Qiita が対象。dev.to は `-`
- **EN 記事**（`*En/` で終わるディレクトリ）: Blog, dev.to が対象。Zenn, Qiita は `-`

## 出力

テーブルをそのままユーザーに表示する。ファイルには書き出さない。
