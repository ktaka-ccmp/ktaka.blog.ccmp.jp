<textarea border-style:dotted="border-style:dotted" class="markdown" disabled="disabled">
<!-- <a href="" target="_blank"><img src="" width="30%"></a> -->

<!-- markdown-toc start - Don't edit this section. Run M-x markdown-toc-refresh-toc -->
**Table of Contents**

- [はじめに](#はじめに)
- [Svelteについて](#svelteについて)
- [FastAPIについて](#fastapiについて)
- [Googleサインインの統合](#googleサインインの統合)
    - [ステップ1: Google Cloud Platformの設定](#ステップ1-google-cloud-platformの設定)
    - [ステップ2: Svelteでのフロントエンド実装](#ステップ2-svelteでのフロントエンド実装)
    - [ステップ3: FastAPIでのバックエンド実装](#ステップ3-fastapiでのバックエンド実装)
- [結論](#結論)

<!-- markdown-toc end -->

## はじめに

近年、ウェブ開発におけるユーザー認証の重要性が高まっています。そこで今回は、人気のあるJavaScriptフレームワーク「Svelte」と、効率的なPythonウェブフレームワーク「FastAPI」を使用して、Googleのサインイン機能を統合する方法を試してみました。

## Svelteについて

Svelteは、宣言的なコードを使ってリッチなインタラクティブなウェブインターフェイスを構築するためのモダンなフレームワークです。Svelteはコンパイル時に高性能なJavaScriptに変換されるため、ブラウザでの負荷が軽減されます。

## FastAPIについて

FastAPIは、高速で、Python 3.6+の型ヒントを使用してAPIを構築するための現代的なウェブフレームワークです。非同期処理に対応しており、開発が迅速かつ簡単になります。

## Googleサインインの統合

### ステップ1: Google Cloud Platformの設定

まず、Google Cloud Platformで新しいプロジェクトを作成し、OAuth 2.0クライアントIDを取得します。これにより、Googleアカウントでの認証情報をアプリケーションで使用できるようになります。

### ステップ2: Svelteでのフロントエンド実装

Svelteを使用して、ユーザーがGoogleアカウントでログインできるボタンを作成します。ユーザーがこのボタンをクリックすると、Googleの認証ページにリダイレクトされます。

  
```
; <<>> DiG 9.18.19-1~deb12u1-Debian <<>> txt ceo.ccmp.jp @miya.ccmp.jp
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NXDOMAIN, id: 61442
;; flags: qr aa rd; QUERY: 1, ANSWER: 0, AUTHORITY: 1, ADDITIONAL: 1
;; WARNING: recursion requested but not available

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 1232
; COOKIE: 9e1067e4bbd3e58b010000006585eee4bb52c093d4ab334f (good)
;; QUESTION SECTION:
;ceo.ccmp.jp.			IN	TXT

;; AUTHORITY SECTION:
ccmp.jp.		600	IN	SOA	miya.ccmp.jp. ktaka.ccmp.jp. 2023031100 3600 600 2419200 600

;; Query time: 7 msec
;; SERVER: 2001:f71:3e60::1#53(miya.ccmp.jp) (UDP)
;; WHEN: Fri Dec 22 20:19:22 JST 2023
;; MSG SIZE  rcvd: 115

```
  
### ステップ3: FastAPIでのバックエンド実装

FastAPIを使用して、Googleからの認証応答を処理するエンドポイントを作成します。認証が成功すると、ユーザーの情報が取得され、セッションが開始されます。

## 結論

SvelteとFastAPIを組み合わせることで、効率的かつ安全にGoogleのサインイン機能をウェブアプリケーションに統合できることがわかりました。このアプローチは、ユーザビリティとセキュリティの両方を高めるための素晴らしい方法です。

</textarea>
