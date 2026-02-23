# ktaka's blog

https://ktaka.blog.ccmp.jp

Zola (v0.22.1) で構築し、GitHub Pages で公開しているブログです。

## 新規記事の作成から公開まで

### 1. 記事ディレクトリの作成

`content/YYYY/記事名/` の下に `index.md` を作成します。

```
content/
  2026/
    MyNewArticle/
      index.md        # 記事本文
      image/           # 画像（必要な場合）
        screenshot.png
```

### 2. Front matter の記述

`index.md` の先頭に TOML 形式の front matter を書きます。

```toml
+++
title = "記事タイトル"
date = 2026-02-23
path = "2026/MyNewArticle"
+++

ここから本文をマークダウンで記述...
```

- `title` — 記事タイトル
- `date` — 公開日（`YYYY-MM-DD` 形式、記事一覧のソート順に使用）
- `path` — URL パス（`https://ktaka.blog.ccmp.jp/{path}` になる）

### 3. 画像の配置

画像は記事ディレクトリ内の `image/` に置き、相対パスで参照します。

```markdown
![スクリーンショット](image/screenshot.png)
```

サイズを指定したい場合は HTML の `<img>` タグを使います。

```html
<img src="image/screenshot.png" width="400">
<img src="image/diagram.png" width="80%">
```

### 3.1. 動画の埋め込み

動画は `image/` ディレクトリに置き、`<video>` タグで埋め込みます。

```html
<video width="600" src="image/demo.mp4" controls autoplay loop></video>
```

- `controls` — 再生コントロールを表示
- `autoplay` — 自動再生
- `loop` — ループ再生
- 属性は必要に応じて組み合わせてください

### 4. ローカルプレビュー

```bash
zola serve
```

ブラウザで http://127.0.0.1:1111 を開いて確認。ファイル保存時に自動リロードされます。

### 5. 公開

master ブランチに push（または PR をマージ）すると、GitHub Actions が自動的にビルド・デプロイします。

```
push to master → GitHub Actions (zola build) → GitHub Pages (ktaka.blog.ccmp.jp)
```

## ビルドコマンド

| コマンド | 説明 |
|---------|------|
| `zola serve` | ローカル開発サーバー（ライブリロード付き） |
| `zola build` | 静的サイトを `public/` に生成 |
| `zola check` | リンク切れ等のチェック |

## バイリンガル記事

日英両方の記事を公開する場合、同じディレクトリに `index.md`（日本語）と `index.en.md`（英語）を配置します。

```
content/2024/my-article/
  index.md      # 日本語版
  index.en.md   # 英語版
  image/
```

## 下書き

公開前の記事は front matter に `draft = true` を追加すると、ビルド時に除外されます。

```toml
+++
title = "下書き記事"
date = 2026-02-23
path = "2026/draft-article"
draft = true
+++
```
