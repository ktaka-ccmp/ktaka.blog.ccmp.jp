# Blog原稿

**Table of Contents**

- [Blog原稿](#blog原稿)
  - [手順](#手順)

<!-- markdown-toc end -->

## 手順

1. Markdown形式でBlog作成
1. TOC生成: ../../gh-md-toc Readme.md
   1. ( cat README.md | ../../gh-md-toc -)?
1. md->html: pandoc Readme.md -o Readme.html
1. or: pandoc -s -c ../../github-markdown.css Readme.en.md -o Readme.en.html --metadata title="....."
1. blogger記事にコピペ

