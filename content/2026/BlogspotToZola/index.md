+++
title = "Blogspot の記事を Zola + GitHub Pages に移行した"
date = 2026-02-24
description = "Blogspotの107記事をZola + GitHub Pagesに一括移行した手順と、ドメイン切替までの記録。"
path = "2026/BlogspotToZola"
+++

*2008 年から書いてきた Blogspot の 107 記事を、Zola + GitHub Pages に一括移行した記録です。*

---

## はじめに

個人ブログを Google Blogspot から GitHub Pages に移行しました。

[前回の記事](/2026/GcpToGitHubPages)ではコーポレートサイト（ccmp.jp）の GCP → GitHub Pages 移行を紹介しましたが、今回はその続きとして、個人ブログ（ktaka.blog.ccmp.jp）の Blogspot → GitHub Pages 移行についてまとめます。

移行の全体像は次の通りです:

1. **GitHub Pages の立ち上げ** — pandoc + GitHub Actions でまず公開
2. **Zola 導入** — 静的サイトジェネレーターに切り替え
3. **Blogspot 全記事の移行** — 107 記事を一括変換
4. **ドメイン切替** — Blogspot と同じドメインで GitHub Pages を公開

---

## 移行の背景

Blogspot は手軽にブログを始められるサービスですが、技術ブログとして使い続けるにはいくつかの不満がありました。

- **Markdown で書けない**: HTML エディタが基本で、シンタックスハイライトもない
- **変更履歴が残らない**: Git のような差分確認やロールバックができない
- **カスタマイズが面倒**: テンプレートの自由度が低く、何か変えたいときに Blogger の作法を毎回調べ直す必要がある

そして何より、ブログを書こうと思っても、Blogger のエディタを開いて HTML を調整する作業が億劫で、記事を書くモチベーションが上がらないことが一番の問題でした。

一方で、GitHub Pages + Zola なら:

- Markdown でそのまま入稿
- シンタックスハイライト標準搭載
- テンプレートを完全に自作可能
- コンテンツを Git で管理（変更履歴・ロールバック）
- ローカルプレビューが `zola serve` 一発

---

## Phase 1: GitHub Pages の立ち上げ

まず、既存の Markdown 記事を GitHub Pages で公開するところから始めました。

### pandoc + GitHub Actions 構成

GitHub Actions ワークフロー（`.github/workflows/pages.yml`）を作成し、pandoc で Markdown → HTML 変換 + GitHub Pages デプロイを自動化しました。DNS CNAME レコードとカスタムドメイン設定で `kt.blog.ccmp.jp` として暫定公開しました。

### この構成の課題

動くことは動きましたが、運用面で問題がありました:

- **記事追加ごとに YAML 手動編集**: `mkdir`、`pandoc` コマンド、index 更新を毎回ワークフローに追加する必要がある
- **ローカルプレビューが手動**: pandoc を手で実行してブラウザで開く
- **TOC 生成が外部ツール依存**: `gh-md-toc` を別途実行
- **シンタックスハイライトなし**: pandoc のデフォルトでは対応していない
- **RSS/サイトマップなし**: 手動構成では現実的でない

記事が 10 本程度のうちは何とかなりますが、Blogspot の 100 本以上の記事を移行するには、この構成では限界がありました。

---

## Phase 2: Zola 導入

pandoc 手動構成の限界を解消するため、静的サイトジェネレーター Zola を導入しました。

### Zola を選んだ理由

| 項目 | pandoc 手動構成 | Zola 導入後 |
|------|---------------|------------|
| 記事追加 | YAML 手動編集 | MD ファイル作成のみ（自動検出） |
| ローカルプレビュー | pandoc 手動実行 | `zola serve`（ライブリロード） |
| TOC | 外部ツール | 標準搭載 |
| シンタックスハイライト | なし | 標準搭載（syntect） |
| RSS/Atom | なし | 自動生成 |
| 多言語 | 手動リンク管理 | 標準搭載（`index.en.md` で自動認識） |

Zola は Rust 製の単一バイナリで、依存関係なしでインストールできます。Hugo や Jekyll と比べてエコシステムは小さいですが、必要な機能は揃っていました。

### 検証項目

導入前に以下を検証し、全項目をクリアしました:

| 検証項目 | 結果 |
|---------|------|
| ビルド・ローカルプレビュー | OK（`zola serve` でライブリロード対応） |
| URL パス保持 | OK（`path` front matter で任意のパスを指定可能） |
| 多言語対応 | OK（`index.en.md` で自動認識） |
| 画像・動画の扱い | OK（`content/` 内に同居、相対パス参照） |
| シンタックスハイライト | OK（github-dark テーマ） |
| Atom フィード | OK（自動生成） |

### テンプレート自作

既存のテーマは使わず、4 種のテンプレートを自作しました:

- **base.html** — 共通レイアウト（ナビゲーション、CSS）
- **index.html** — トップページ（セクション一覧へリダイレクト）
- **section.html** — 記事一覧（日付降順）
- **page.html** — 記事本文（TOC、前後ナビ、ライトボックス）

CSS は `github-markdown.css` をベースにしており、最小限のスタイルで十分な表示品質を実現しています。

### 移行の実施

- 既存の 11 記事を Zola 形式に変換（TOML front matter 追加、手動 TOC 削除）
- GitHub Actions を pandoc → `zola build` に更新
- 旧ファイル（`gh-md-toc`、ルート CSS、pandoc ワークフロー）を削除

---

## Phase 3: Blogspot 全記事の移行

Zola の基盤が整ったところで、Blogspot の全記事を移行しました。

### エクスポートと変換

Blogspot の記事データは Google Takeout でエクスポートしました。Blogger の管理画面からの XML エクスポートではなく、Google Takeout を使ったのは、HTML 形式で各記事が個別ファイルとして取得できるためです。

変換は Python スクリプトで自動化しました:

```
Google Takeout (HTML) → Python スクリプト → Zola 用 Markdown + 画像
```

スクリプトが行う処理:

1. HTML ファイルの解析
2. TOML front matter の自動生成（title, date, path）
3. HTML → Markdown 変換
4. 画像ファイルのローカルコピーとパス書き換え
5. `content/{year}/{slug}/index.md` として出力

### 配置構造

```
content/
  2008/
    first-post/
      index.md        # 記事本文（Markdown + TOML front matter）
      image/           # 画像
        photo.jpg
    second-post/
      index.md
  2009/
    ...
  2024/
    ...
```

107 記事（うち 1 記事は `draft = true`）を年別ディレクトリに配置しました。

### 品質検証

自動変換した記事の品質を確認するため、Claude Code を使って全 104 記事（draft 除く）を本番 Blogspot サイトと 1 記事ずつ比較しました。各記事について WebFetch で本番ページを取得し、ローカルの Markdown と突き合わせる作業を並列エージェントで実行しています。

結果:

- **100 記事**: 問題なし
- **4 記事を修正**:

| 記事 | 問題 | 対応 |
|------|------|------|
| `2011/blog-post` | 画像 2 枚が未取得 | Blogger CDN からダウンロード（WebP） |
| `2011/hhkb-pro2` | 画像 1 枚が未取得 | Blogger CDN からダウンロード（WebP） |
| `2011/galaxy-blogger` | 画像 1 枚が消失 | Blogger CDN から消失、復元不可 |
| `2011/gnu-tar124ok` | 変換アーティファクト | 空 blockquote・空コードブロックを除去 |

Blogger CDN から消失していた画像が 1 枚ありましたが、それ以外は全記事を正常に移行できました。

---

## Phase 4: ドメイン切替

コンテンツ移行の完了後、ドメインを切り替えました。

Blogspot で使っていたドメイン `ktaka.blog.ccmp.jp` を、そのまま GitHub Pages に向け替えました:

1. Blogspot 管理画面でカスタムドメイン（`ktaka.blog.ccmp.jp`）を解除
2. DNS CNAME を `ktaka-ccmp.github.io` に変更
3. GitHub Pages のカスタムドメイン設定を更新
4. Zola の `config.toml`（`base_url`）と `static/CNAME` を更新

暫定ドメイン `kt.blog.ccmp.jp` は廃止しました。

---

## まとめ

| 項目 | 移行前（Blogspot） | 移行後（Zola + GitHub Pages） |
|------|-------------------|------------------------------|
| 入稿形式 | HTML エディタ | Markdown |
| シンタックスハイライト | なし | あり（github-dark） |
| プレビュー | Blogger のプレビュー機能 | `zola serve`（ローカルでライブリロード） |
| バージョン管理 | なし | Git |
| 画像ホスト | Blogger CDN | リポジトリ内（Git 管理） |
| カスタマイズ | テンプレート制約あり | 完全自作テンプレート |
| RSS/Atom | Blogger 独自形式 | Zola 自動生成 |
| ホスティングコスト | $0 | $0 |

大方の移行作業は 2 日間で完了しました。最も時間がかかったのは Blogspot 全記事の品質検証（104 記事の 1 対 1 比較）ですが、これは Claude Code の並列エージェントに任せたので、待ち時間が大半でした。

今まではブログを書こうと思っても、Blogger のエディタを開いて HTML を調整する作業が面倒で、かなり億劫に感じていました。Markdown なら文章を書くことに集中でき、それがそのままブログに変換されて CDN 配信されるので、記事を書くハードルがかなり下がりました。
