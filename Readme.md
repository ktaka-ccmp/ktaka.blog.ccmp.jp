# Blog原稿

<!-- markdown-toc start - Don't edit this section. Run M-x markdown-toc-refresh-toc -->
**Table of Contents**

- [Blog原稿](#blog原稿)
    - [手順](#手順)

<!-- markdown-toc end -->

## 手順

1. Markdown形式でBlog作成
1. TOC生成: ../../gh-md-toc Readme.md
1. md->html: pandoc Readme.md -o Readme.html
1. blogger記事にコピペ

## 画像

GitHUBのmasterブランチにアップロード下画像を参照する。

```html
<p><a href="https://raw.githubusercontent.com/ktaka-ccmp/ktaka.blog.ccmp.jp/master/2024/Axum-Google-OAuth2-Login/image/fig-1.png"
    target="_blank">
    <img src="https://raw.githubusercontent.com/ktaka-ccmp/ktaka.blog.ccmp.jp/master/2024/Axum-Google-OAuth2-Login/image/fig-1.png"
    width="80%" alt="Sign-in Animation" title="Sign-in Animation"> </a></p>
```

### mermaid diagramをpngに変換

```bash
mkdir image
mmdc -i Readme.en.md -o ./image/fig.png
```

マークダウンの中からmeraid diagramを抽出し、番号をつけて保存してくれる👍

```bash
$ tree image/
image/
├── fig-1.png
├── fig-2.png
├── fig-3.png
└── fig-4.png
```
