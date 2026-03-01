# テンプレート構成

Zola のテンプレートエンジンは [Tera](https://keats.github.io/tera/)（Jinja2 に似た構文）。
4ファイルで構成され、すべて `base.html` を継承している。

## 目次

- [継承関係](#継承関係)
- [Zola がテンプレートを選択するルール](#zola-がテンプレートを選択するルール)
- [オーバーライド可能なブロック](#オーバーライド可能なブロック)
- [base.html — 全ページ共通レイアウト](#basehtml--全ページ共通レイアウト)
  - [`<head>` セクション](#head-セクション)
  - [インライン CSS の内容](#インライン-css-の内容)
  - [ライトボックス CSS](#ライトボックス-css)
  - [`<body>` セクション](#body-セクション)
  - [meta ブロックのデフォルト出力](#meta-ブロックのデフォルト出力)
- [page.html — 個別記事ページ](#pagehtml--個別記事ページ)
  - [{% block title %}](#-block-title-l3)
  - [{% block meta %}](#-block-meta-l5-21)
  - [{% block nav_extra %} — 前後記事ナビゲーション](#-block-nav_extra-l23-58--前後記事ナビゲーション)
  - [{% block content %} — 記事本文](#-block-content-l61-119--記事本文)
  - [目次（TOC）描画](#目次toc描画l66-84)
  - [記事下部ナビゲーション](#記事下部ナビゲーションl88-99)
  - [ライトボックス JavaScript](#ライトボックス-javascriptl101-118)
- [index.html — トップページ](#indexhtml--トップページ)
  - [年別グループ分けのロジック](#年別グループ分けのロジック)
- [section.html — 年別セクションページ](#sectionhtml--年別セクションページ)
- [Tera テンプレート構文クイックリファレンス](#tera-テンプレート構文クイックリファレンス)
- [主要な Zola 変数](#主要な-zola-変数)

## 継承関係

```
base.html           全ページ共通レイアウト
├── index.html      トップページ（/）
├── section.html    年別セクション（/2026/ 等）
└── page.html       個別記事（/2026/TmuxForScreenUsers 等）
```

## Zola がテンプレートを選択するルール

| コンテンツファイル | 使用テンプレート |
|---|---|
| `content/_index.md`（ルートセクション） | `index.html` |
| `content/2026/_index.md`（年別セクション） | `section.html` |
| `content/2026/TmuxForScreenUsers/index.md`（記事） | `page.html` |

## オーバーライド可能なブロック

`base.html` が定義する4つのブロックを、子テンプレートが `{% block name %}...{% endblock %}` で差し替える。

| ブロック名 | 場所 | base.html のデフォルト |
|---|---|---|
| `title` | `<title>` タグ内 | `config.title`（"ktaka's blog"） |
| `meta` | `<head>` 内、`<title>` の直後 | サイトレベルの description, OGP, Twitter Card |
| `nav_extra` | ナビバー右側 | 空 |
| `content` | `<main>` タグ内 | 空 |

各テンプレートのオーバーライド状況:

| ブロック | index.html | section.html | page.html |
|---|---|---|---|
| `title` | - | o | o |
| `meta` | - | - | o |
| `nav_extra` | - | - | o |
| `content` | o | o | o |

`-` = base.html のデフォルトをそのまま使用、`o` = オーバーライド

---

## base.html — 全ページ共通レイアウト

### `<head>` セクション

```
L4-5   charset, viewport
L6     {% block title %} — ページタイトル
L7-17  {% block meta %} — meta タグ群（description, OGP, Twitter Card）
L18    Atom フィードリンク（/atom.xml）
L19    CSS 読み込み（github-markdown.css）
L20-62 インライン CSS
```

`<head>` の実際の構造:

```html
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{% block title %}{{ config.title }}{% endblock %}</title>
  {% block meta %}
  <!-- デフォルトの meta タグ（後述） -->
  {% endblock %}
  <link rel="alternate" type="application/atom+xml" title="{{ config.title }}" href="/atom.xml">
  <link rel="stylesheet" href="/github-markdown.css">
  <style>
    /* インライン CSS（後述） */
  </style>
</head>
```

### インライン CSS の内容

#### `body` — ページ全体のレイアウト

```css
body {
  max-width: 800px;
  margin: 0 auto;     /* 左右中央寄せ */
  padding: 20px;
}
```

#### `.markdown-body` — 本文エリア

```css
.markdown-body {
  padding: 20px 0;
}
```

`github-markdown.css` が提供するクラスで、GitHub 風のマークダウンレンダリングスタイルを適用する。
`<main class="markdown-body">` に適用される。

#### `.site-nav` — ナビバー

```css
.site-nav {
  padding: 10px 0;
  border-bottom: 1px solid #eee;
  font-size: 1.5em;
}
.site-nav a {
  text-decoration: none;
  color: #0366d6;       /* GitHub 風のリンク色 */
}
```

### ライトボックス CSS

CSS-only のライトボックスを実現する4つのルール:

```css
/* 通常時は非表示 */
.lightbox {
  display: none;
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;   /* 画面全体を覆う */
  background: rgba(0,0,0,0.85);             /* 半透明の黒背景 */
  z-index: 1000;                             /* 最前面に表示 */
  align-items: center;                       /* 縦中央 */
  justify-content: center;                   /* 横中央 */
}

/* URL フラグメント（#lb-0 等）がターゲットになると表示 */
.lightbox:target {
  display: flex;
}

/* 拡大画像のサイズ制限 */
.lightbox img {
  max-width: 90vw;
  max-height: 90vh;
  object-fit: contain;    /* アスペクト比を維持 */
}

/* 閉じるボタン（×） */
.lightbox .close {
  position: fixed;
  top: 15px; right: 20px;
  color: #fff;
  font-size: 2em;
  text-decoration: none;
}
```

動作の仕組み:
1. 画像クリック → `<a href="#lb-0">` により URL が `#lb-0` に変わる
2. `#lb-0` がターゲットになり `.lightbox:target` が発動 → `display: flex` で表示
3. 閉じるボタンクリック → `history.back()` で URL フラグメントが消える → `display: none` に戻る

実際の `<a>` 要素の生成は `page.html` の JavaScript が行う（後述）。

### `<body>` セクション

```html
<body>
  <nav class="site-nav" style="display: flex; align-items: center;">
    <a href="/">{{ config.title }}</a>
    <a href="/p/p.html" style="margin-left: 20px;">Profile</a>
    <a href="/atom.xml" style="margin-left: 20px;" title="Atom Feed">
      <svg><!-- RSS アイコン SVG --></svg>
    </a>
    {% block nav_extra %}{% endblock %}
  </nav>
  <main class="markdown-body">
    {% block content %}{% endblock %}
  </main>
</body>
```

ナビバーは `display: flex; align-items: center;` で横並び。
`{% block nav_extra %}` は `page.html` でのみオーバーライドされ、前後記事の `← →` 矢印リンクが入る。
`margin-left: auto` により矢印はナビバーの右端に寄せられる（page.html 側で設定）。

### meta ブロックのデフォルト出力

```html
{% block meta %}
<meta name="description" content="{{ config.description }}">
<meta property="og:title" content="{{ config.title }}">
<meta property="og:description" content="{{ config.description }}">
<meta property="og:type" content="website">
<meta property="og:url" content="{{ config.base_url }}">
{% if config.extra.og_image %}
<meta property="og:image" content="{{ config.extra.og_image }}">
{% endif %}
<meta name="twitter:card" content="summary">
{% endblock %}
```

- `og:type` はサイトレベルでは `website`（記事ページでは `article` にオーバーライド）
- `og:image` は `config.extra.og_image` が空文字でなければ出力（現在は空）
- `index.html` と `section.html` はこのデフォルトをそのまま使う
- `page.html` のみオーバーライドして記事固有の値を出力する

---

## page.html — 個別記事ページ

最も複雑なテンプレート。4つのブロックをすべてオーバーライドしている。

### {% block title %}（L3）

```html
{% block title %}{{ page.title }} | {{ config.title }}{% endblock %}
```

出力例: `<title>tmux customization for GNU Screen users | ktaka's blog</title>`

### {% block meta %}（L5-21）

記事固有の meta タグを出力する。

```html
{% block meta %}
{% if page.description %}
<meta name="description" content="{{ page.description }}">
{% else %}
<meta name="description" content="{{ config.description }}">
{% endif %}
<meta property="og:title" content="{{ page.title }}">
<meta property="og:description" content="{% if page.description %}{{ page.description }}{% else %}{{ config.description }}{% endif %}">
<meta property="og:type" content="article">
<meta property="og:url" content="{{ page.permalink }}">
{% if page.extra.og_image %}
<meta property="og:image" content="{{ page.extra.og_image }}">
{% elif config.extra.og_image %}
<meta property="og:image" content="{{ config.extra.og_image }}">
{% endif %}
<meta name="twitter:card" content="summary">
{% endblock %}
```

base.html との違い:

| タグ | base.html（デフォルト） | page.html（オーバーライド） |
|---|---|---|
| `description` | `config.description` | `page.description`（なければ `config.description`） |
| `og:title` | `config.title` | `page.title` |
| `og:description` | `config.description` | `page.description`（なければ `config.description`） |
| `og:type` | `website` | `article` |
| `og:url` | `config.base_url` | `page.permalink` |
| `og:image` | `config.extra.og_image` | `page.extra.og_image` → `config.extra.og_image` の優先順 |

`page.description` は記事の front matter で設定:

```toml
+++
title = "記事タイトル"
date = 2026-03-01
description = "記事の説明文（OGP や検索結果に使われる）"
+++
```

### {% block nav_extra %}（L23-58） — 前後記事ナビゲーション

ナビバー右端に矢印アイコン（SVG）のリンクを表示する。
現在は角丸シェブロン（太め）を採用（16x16、`fill="currentColor"`）。

矢印の SVG アイコンは差し替え可能。候補一覧は[付録: ナビゲーション矢印 SVG 候補](#付録-ナビゲーション矢印-svg-候補)を参照。

```html
{% block nav_extra %}
  {# ... 前後記事の URL/タイトルを計算（後述） ... #}
  <span style="margin-left: auto;">
    {% if newer_url %}<a href="{{ newer_url | trim_end_matches(pat='/') }}"><svg ...><!-- 左矢印 --></svg></a>{% endif %}
    {% if older_url %}<a href="{{ older_url | trim_end_matches(pat='/') }}" style="margin-left: 10px;"><svg ...><!-- 右矢印 --></svg></a>{% endif %}
  </span>
{% endblock %}
```

前後記事の URL/タイトル計算部分:

```html
  {% set root_section = get_section(path="_index.md") %}
  {% set_global older_url = "" %}
  {% set_global older_title = "" %}
  {% set_global newer_url = "" %}
  {% set_global newer_title = "" %}
  {% set_global found = false %}
  {% set_global newest_url = "" %}
  {% set_global newest_title = "" %}
  {% for p in root_section.pages %}
    {% if loop.first %}
      {% set_global newest_url = p.permalink %}
      {% set_global newest_title = p.title %}
    {% endif %}
    {% if found and older_url == "" %}
      {% set_global older_url = p.permalink %}
      {% set_global older_title = p.title %}
    {% endif %}
    {% if p.path == page.path %}
      {% set_global found = true %}
    {% endif %}
    {% if not found %}
      {% set_global newer_url = p.permalink %}
      {% set_global newer_title = p.title %}
    {% endif %}
  {% endfor %}
  {% if not found %}
    {% set_global older_url = newest_url %}
    {% set_global older_title = newest_title %}
    {% set_global newer_url = "" %}
    {% set_global newer_title = "" %}
  {% endif %}
```

#### アルゴリズム

`get_section(path="_index.md")` でルートセクションを取得する。
ルートセクションの全ページリストは日付降順（最新が先頭）で並んでいる:

```
root_section.pages = [最新記事, 2番目, ..., 現在の記事, ..., 最古の記事]
```

1. リストを先頭から順に走査
2. 先頭のページの URL/タイトルを `newest_url`/`newest_title` に記録（フォールバック用）
3. 現在のページ（`p.path == page.path`）を見つけたら `found = true`
4. `found` になる前の最後のページ → `newer_url`（1つ新しい記事）
5. `found` になった後の最初のページ → `older_url`（1つ古い記事）

結果:

| 条件 | ← | → |
|---|---|---|
| 最新記事 | 表示しない | 1つ古い記事 |
| 中間の記事 | 1つ新しい記事 | 1つ古い記事 |
| 最古の記事 | 1つ新しい記事 | 表示しない |

#### `set_global` を使う理由

Tera では `{% for %}` ループ内で `{% set %}` した変数はループ外に持ち出せない。
`{% set_global %}` を使うことでループスコープを超えて値を保持する。

#### ページが見つからなかった場合のフォールバック

年別セクション（`content/2026/_index.md`）に属する記事は `root_section.pages` に含まれない場合がある。
そのとき `found` が `false` のままになるため、フォールバック処理が発動する:

```
older_url = newest_url   （最新記事へのリンク）
newer_url = ""           （← は表示しない）
```

これにより、ルートセクションに属さない記事でも最新記事への `→` リンクが表示される。

#### `margin-left: auto` のトリック

```html
<span style="margin-left: auto;">
```

ナビバーが `display: flex` なので、`margin-left: auto` によりこの `<span>` は
利用可能な余白をすべて左マージンとして吸収し、結果的にナビバーの右端に配置される。

### {% block content %}（L61-119） — 記事本文

```html
{% block content %}
<article>
  <h1>{{ page.title }}</h1>
  {% if page.date %}<time>{{ page.date | date(format="%Y-%m-%d") }}</time>{% endif %}

  {% if page.toc %}
  <nav id="toc">
    <!-- 目次（後述） -->
  </nav>
  {% endif %}

  <div>{{ page.content | safe }}</div>

  <nav style="display: flex; justify-content: space-between; margin-top: 40px; padding-top: 20px; border-top: 1px solid #eee;">
    <!-- 記事下部ナビゲーション（後述） -->
  </nav>
</article>
<script>
  // ライトボックス JavaScript（後述）
</script>
{% endblock %}
```

#### 目次（TOC）描画（L66-84）

Zola が Markdown の見出しから自動生成する `page.toc` を2階層（h2 → h3）で描画する。

```html
{% if page.toc %}
<nav id="toc">
  <h2>Table of Contents</h2>
  <ul>
    {% for h2 in page.toc %}
    <li>
      <a href="{{ h2.permalink }}">{{ h2.title }}</a>
      {% if h2.children %}
      <ul>
        {% for h3 in h2.children %}
        <li><a href="{{ h3.permalink }}">{{ h3.title }}</a></li>
        {% endfor %}
      </ul>
      {% endif %}
    </li>
    {% endfor %}
  </ul>
</nav>
{% endif %}
```

`page.toc` の構造:

```
page.toc = [
  { title: "見出し1", permalink: "#見出し1", children: [
    { title: "子見出し1-1", permalink: "#子見出し1-1", children: [...] },
    ...
  ]},
  ...
]
```

h4 以降のネストがあっても h3 の `children` には含まれるが、テンプレートでは描画しない（2階層まで）。
`page.toc` が空の場合（見出しが無い記事）は `<nav id="toc">` 自体が出力されない。

#### 記事下部ナビゲーション（L88-99）

記事本文の下に前後記事のタイトル付きリンクを表示する。ナビバーと同じ SVG 矢印アイコンを使用し、加えて記事タイトルも表示する。

```html
<nav style="display: flex; justify-content: space-between; margin-top: 40px; padding-top: 20px; border-top: 1px solid #eee;">
  {% if newer_url %}
  <a href="{{ newer_url | trim_end_matches(pat='/') }}"><svg ...><!-- 左矢印 --></svg> {{ newer_title }}</a>
  {% else %}
  <span></span>
  {% endif %}
  {% if older_url %}
  <a href="{{ older_url | trim_end_matches(pat='/') }}">{{ older_title }} <svg ...><!-- 右矢印 --></svg></a>
  {% else %}
  <span></span>
  {% endif %}
</nav>
```

- `display: flex; justify-content: space-between;` で左右に配置
- リンクが片方しかない場合、空の `<span></span>` でレイアウトを維持
- `newer_url` / `older_url` は `{% block nav_extra %}` で計算済みの変数を共有
- `trim_end_matches(pat='/')` で末尾スラッシュを除去（URL の統一）

#### ライトボックス JavaScript（L101-118）

記事内の `<img>` タグを自動的にクリックで拡大表示可能にする。

```javascript
document.querySelectorAll('article img').forEach(function(img, i) {
  if (!img.closest('a')) {
    var id = 'lb-' + i;
    var a = document.createElement('a');
    a.href = '#' + id;
    img.parentNode.insertBefore(a, img);
    a.appendChild(img);
    var overlay = document.createElement('a');
    overlay.id = id;
    overlay.href = '#';
    overlay.className = 'lightbox';
    overlay.innerHTML = '<span class="close">&times;</span><img src="' + img.src + '">';
    overlay.onclick = function(e) { e.preventDefault(); history.back(); };
    document.body.appendChild(overlay);
  }
});
```

処理の流れ:

1. **対象の選択**: `article img` で記事内の全 `<img>` を取得
2. **スキップ判定**: `img.closest('a')` — すでに `<a>` で囲まれている画像はスキップ（外部リンク付き画像等）
3. **トリガーリンクの生成**: 画像を `<a href="#lb-0">` でラップ
   - `insertBefore` + `appendChild` で DOM を組み替え
   - クリックすると URL が `#lb-0` に変わる
4. **オーバーレイの生成**: `<a id="lb-0" class="lightbox">` を `<body>` 末尾に追加
   - 同じ画像の拡大版（`img.src` を再利用）
   - 閉じるボタン `×`（`&times;` エンティティ）
5. **閉じる処理**: `onclick` で `e.preventDefault()` + `history.back()`
   - `history.back()` により URL フラグメントが消え、`:target` が解除される
   - CSS の `.lightbox:target { display: flex }` → `.lightbox { display: none }` に戻る

インデックス `i` は `forEach` のコールバック引数で、0 から始まる連番。
各画像に `lb-0`, `lb-1`, `lb-2`, ... とユニークな ID が振られる。

---

## index.html — トップページ

`content/_index.md` に対応。全記事を年別グループで一覧表示する。

`{% block content %}` のみオーバーライド。

```html
{% extends "base.html" %}

{% block content %}
<h1>{{ section.title }}</h1>

{% set current_year = "" %}
{% for page in section.pages %}
  {% set page_year = page.date | date(format="%Y") %}
  {% if page_year != current_year %}
    {% set_global current_year = page_year %}
    <h2>{{ current_year }}</h2>
  {% endif %}
  <article>
    <h3><a href="{{ page.permalink | trim_end_matches(pat='/') }}">{{ page.title }}</a></h3>
    <time>{{ page.date | date(format="%Y-%m-%d") }}</time>
  </article>
{% endfor %}
{% endblock %}
```

### 年別グループ分けのロジック

1. `current_year` を空文字で初期化
2. `section.pages` を日付降順でループ（Zola のデフォルトソート）
3. 各ページの年（`page.date | date(format="%Y")`）を `page_year` に取得
4. `page_year != current_year` なら年が変わった → `<h2>2026</h2>` を挿入
5. `set_global` で `current_year` を更新（`set` ではループ外に反映されないため）

出力イメージ:

```html
<h1>ktaka's blog</h1>
<h2>2026</h2>
<article><h3><a href="/2026/TmuxForScreenUsers">tmux customization...</a></h3><time>2026-02-28</time></article>
<article><h3><a href="/2026/GrubUsb">Creating GRUB...</a></h3><time>2026-02-15</time></article>
<h2>2025</h2>
<article>...</article>
```

`{% block title %}` をオーバーライドしていないため、
`<title>` は `base.html` のデフォルト（`config.title` = "ktaka's blog"）がそのまま使われる。

---

## section.html — 年別セクションページ

`content/2026/_index.md` 等に対応。その年の記事だけを一覧表示する。

`{% block title %}` と `{% block content %}` をオーバーライド。

```html
{% extends "base.html" %}

{% block title %}{{ section.title }} | {{ config.title }}{% endblock %}

{% block content %}
<h1>{{ section.title }}</h1>

{% for page in section.pages %}
<article>
  <h2><a href="{{ page.permalink | trim_end_matches(pat='/') }}">{{ page.title }}</a></h2>
  {% if page.date %}<time>{{ page.date | date(format="%Y-%m-%d") }}</time>{% endif %}
</article>
{% endfor %}
{% endblock %}
```

`index.html` との違い:
- 年別グループ分けがない（セクション自体が1年分なので不要）
- `{% block title %}` をオーバーライドしている（`2026 | ktaka's blog` 等）
- 各記事は `<h2>` で表示（index.html では `<h3>`、`<h2>` は年見出し）
- `{% if page.date %}` ガードがある（index.html にはない — ルートセクションのページは必ず日付がある前提）

---

## Tera テンプレート構文クイックリファレンス

| 構文 | 意味 |
|---|---|
| `{{ variable }}` | 変数の出力 |
| `{% if condition %}...{% endif %}` | 条件分岐 |
| `{% for item in list %}...{% endfor %}` | ループ |
| `{% block name %}...{% endblock %}` | ブロック定義/オーバーライド |
| `{% extends "base.html" %}` | テンプレート継承 |
| `{% set var = value %}` | ローカル変数の設定 |
| `{% set_global var = value %}` | グローバル変数の設定（ループ内から外に値を持ち出す） |
| `{{ value \| filter }}` | フィルター適用 |
| `{{ date \| date(format="%Y-%m-%d") }}` | 日付フォーマット |
| `{{ url \| trim_end_matches(pat='/') }}` | 末尾スラッシュ除去 |
| `{{ content \| safe }}` | HTML エスケープを無効化（生 HTML を出力） |
| `{{ get_section(path="_index.md") }}` | Zola 組み込み関数（セクション情報の取得） |

## 主要な Zola 変数

| 変数 | 利用可能場所 | 内容 |
|---|---|---|
| `config.title` | 全テンプレート | サイトタイトル |
| `config.base_url` | 全テンプレート | サイトの URL |
| `config.description` | 全テンプレート | サイトの説明文 |
| `config.extra.*` | 全テンプレート | config.toml の [extra] セクション |
| `page.title` | page.html | 記事タイトル |
| `page.date` | page.html | 記事の日付 |
| `page.description` | page.html | 記事の説明文（front matter） |
| `page.content` | page.html | マークダウンから変換された HTML |
| `page.permalink` | page.html | 記事の完全 URL |
| `page.path` | page.html | コンテンツパス |
| `page.toc` | page.html | 自動生成された目次 |
| `page.extra.*` | page.html | front matter の [extra] セクション |
| `section.title` | index/section.html | セクションタイトル |
| `section.pages` | index/section.html | セクション内のページリスト |

---

## 付録: ナビゲーション矢印 SVG 候補

すべて `viewBox="0 0 24 24"` `fill="currentColor"` で統一。サイズは `width`/`height` 属性で調整する（現在 16x16）。

### 現在採用: 角丸シェブロン（太め）

```html
<!-- ← -->
<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
  <path d="M16.62 2.99a1.25 1.25 0 0 0-1.77 0L6.54 11.3a1 1 0 0 0 0 1.41l8.31 8.31a1.25 1.25 0 0 0 1.77-1.77L9.38 12l7.24-7.24a1.25 1.25 0 0 0 0-1.77z"/>
</svg>

<!-- → -->
<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
  <path d="M7.38 2.99a1.25 1.25 0 0 1 1.77 0l8.31 8.31a1 1 0 0 1 0 1.41l-8.31 8.31a1.25 1.25 0 0 1-1.77-1.77L14.62 12 7.38 4.76a1.25 1.25 0 0 1 0-1.77z"/>
</svg>
```

### 候補1: シンプルなシェブロン

```html
<!-- ← -->
<path d="M15.41 7.41L14 6l-6 6 6 6 1.41-1.41L10.83 12z"/>
<!-- → -->
<path d="M10 6L8.59 7.41 13.17 12l-4.58 4.59L10 18l6-6z"/>
```

### 候補2: 矢印（Material Icons 風）

```html
<!-- ← -->
<path d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z"/>
<!-- → -->
<path d="M12 4l-1.41 1.41L16.17 11H4v2h12.17l-5.58 5.59L12 20l8-8z"/>
```

### 候補3: 丸付き矢印

```html
<!-- ← -->
<path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm4 11H9.41l2.29 2.29-1.41 1.41L6.59 13 10.29 9.3l1.41 1.41L9.41 13H16v-2z"/>
<!-- → -->
<path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1.29 13.71l-1.41-1.41L11.59 12H8v-2h3.59L9.3 7.71l1.41-1.41L15.41 11l-4.7 4.71z"/>
```

### 候補4: ダブルシェブロン（スキップ風）

```html
<!-- ← -->
<path d="M18.41 16.59L13.82 12l4.59-4.59L17 6l-6 6 6 6zM6 6h2v12H6z"/>
<!-- → -->
<path d="M5.59 7.41L10.18 12l-4.59 4.59L7 18l6-6-6-6zM16 6h2v12h-2z"/>
```

### 候補5: 三角（再生ボタン風）

```html
<!-- ← -->
<path d="M20 12l-10 7V5z" transform="scale(-1,1) translate(-24,0)"/>
<!-- → -->
<path d="M4 12l10-7v14z" transform="scale(-1,1) translate(-24,0)"/>
```

### 候補6: 細い矢印（ストローク風）

`fill` ではなく `stroke` を使用する。`fill="none"` に変更が必要。

```html
<!-- ← -->
<path d="M14 7l-5 5 5 5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
<!-- → -->
<path d="M10 7l5 5-5 5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
```
