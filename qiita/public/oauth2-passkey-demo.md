---
title: 'パスワードなしの認証を試す: oauth2-passkey ライブデモ'
tags:
  - Rust
  - oauth2
  - 認証
  - passkey
  - WebAuthn
private: false
updated_at: '2026-03-28T15:46:44+09:00'
id: ea549b5d798d1d23b922
organization_url_name: null
slide: false
ignorePublish: false
---

> この記事は [ktaka.blog.ccmp.jp の記事](https://ktaka.blog.ccmp.jp/2026/Oauth2PasskeyDemo) のクロスポストです。

*[oauth2-passkey](https://github.com/ktaka-ccmp/oauth2-passkey) は、OAuth2 と Passkey を組み合わせたパスワードレス認証を、少ないコードで Rust の Web アプリに組み込めるライブラリです。*

デモサイト [passkey-demo.ccmp.jp](https://passkey-demo.ccmp.jp) を用意しました。
実際の操作を2本の動画で紹介し、その後にコードの使い方を説明します。

---

## デモ 1: Google で登録して Passkey を追加

![デモ1: Google登録とPasskey追加](https://ktaka.blog.ccmp.jp/2026/Oauth2PasskeyDemo/video/o2p-demo1.gif)

まず新規ユーザーとしてログインする流れです。

1. ログインページには「Register / Sign in with Google」と「Sign in with Passkey」の2つのボタンがあります。
2. 「Register / Sign in with Google」を押すと、おなじみの Google アカウント選択画面が開きます。
3. Google 認証が終わると、すぐに **「Passkey を作成しますか？」** というダイアログが出ます。これがこのライブラリの特徴の一つである **「Passkey プロモーション」** です。OAuth2 でログインしたユーザーに Passkey の登録を自然に促します。
4. Passkey を作成するとダッシュボードに遷移し、My Account や Admin Panel にアクセスできます。
5. My Account ページでは、ユーザー情報・Passkey 資格情報・連携 OAuth2 アカウント・ログイン履歴を一覧で確認できます。

いつもの Google ログインで始めて、そのまま Passkey も登録できるのがこの仕組みのよいところです。

## デモ 2: Passkey でサインイン

![デモ2: Passkeyでサインイン](https://ktaka.blog.ccmp.jp/2026/Oauth2PasskeyDemo/video/o2p-demo2.gif)

続いて、同じユーザーが Passkey だけでログインする流れです。

1. ログインページで「Sign in with Passkey」を押すと、ブラウザの Passkey ダイアログが表示されます。
2. 指紋や顔認証で本人確認をすれば、それだけでログインが完了します。Google へのリダイレクトもパスワード入力も要りません。
3. ログイン履歴には Passkey と OAuth2 の両方のエントリーが残るので、いつ・どの方法でログインしたか確認できます。

Passkey を一度登録してしまえば、普段のログインはこれだけです。高速で、フィッシングにも強い認証が手に入ります。

## 試してみる

デモサイトはこちらです: **[passkey-demo.ccmp.jp](https://passkey-demo.ccmp.jp)**

- Google でサインイン → Passkey を登録 → Passkey でサインイン、という一連の流れを試せます
- デモでは全ユーザーに管理者権限が付与されるので、管理パネルも自由に操作できます
- ログイン履歴ではデバイスや認証方法の詳細も確認できます

データはメモリ上に保存されていて、サーバー再起動時にリセットされます。気軽にどうぞ。

## oauth2-passkey とは

[oauth2-passkey](https://crates.io/crates/oauth2-passkey) は、Web アプリにパスワードレス認証を追加するための Rust ライブラリです。2種類の認証方式を一つのライブラリで扱えます。

- **OAuth2 (Google)** -- ユーザーにとって馴染みのある、ワンクリックの登録・ログイン
- **Passkeys (WebAuthn/FIDO2)** -- 指紋・顔・セキュリティキーによる、フィッシング耐性のあるログイン

想定する運用フローは、まず Google で登録してもらい、その流れで Passkey も追加してもらう形です。デバイスを紛失した場合でも Google 経由でログインできるので、Passkey 一本に依存するリスクを回避できます。

## クイックスタート

Axum アプリへの組み込みは以下のようになります。

```rust
use axum::{Router, routing::get, response::IntoResponse};
use oauth2_passkey_axum::{AuthUser, oauth2_passkey_full_router};

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    oauth2_passkey_axum::init().await?;

    let app = Router::new()
        .route("/", get(home))
        .route("/protected", get(protected))
        .merge(oauth2_passkey_full_router());

    let listener = tokio::net::TcpListener::bind("0.0.0.0:3001").await?;
    axum::serve(listener, app).await?;
    Ok(())
}

async fn home() -> &'static str {
    "Welcome! Visit /o2p/user/login to sign in"
}

async fn protected(user: AuthUser) -> impl IntoResponse {
    format!("Hello, {}!", user.account)
}
```

`oauth2_passkey_full_router()` を呼ぶと、`/o2p/*` 以下に、ログインページ・OAuth2 フロー・Passkey の登録／認証・ユーザーアカウント管理・管理パネルなど、一式のルートが追加されます。

あとは環境変数で Google OAuth2 のクレデンシャルとセッションシークレットを設定すれば動きます。詳しくは [Getting Started ガイド](https://ktaka-ccmp.github.io/oauth2-passkey/)をご覧ください。

## 機能一覧

| 機能 | 説明 |
|------|------|
| **デュアル認証** | OAuth2 (Google) と Passkeys を一つのライブラリで提供 |
| **組み込み UI** | ログインページ、ユーザーアカウント画面、管理パネル付き |
| **Passkey プロモーション** | OAuth2 ユーザーに Passkey 登録を自然に提案 |
| **ログイン履歴** | IP・User-Agent・認証器の詳細を自動記録 |
| **セッション管理** | セキュアな Cookie、セッション競合ポリシー、強制ログアウト |
| **管理パネル** | ユーザー管理、監査ログ、管理者の誤操作防止 |
| **テーマ** | 9種の CSS テーマを同梱、カスタムテーマにも対応 |
| **ストレージ** | SQLite（開発用）／PostgreSQL（本番用）、キャッシュは Redis またはインメモリに対応 |

## リンク

- **ライブデモ**: [passkey-demo.ccmp.jp](https://passkey-demo.ccmp.jp)
- **GitHub**: [ktaka-ccmp/oauth2-passkey](https://github.com/ktaka-ccmp/oauth2-passkey)
- **crates.io**: [oauth2-passkey](https://crates.io/crates/oauth2-passkey) / [oauth2-passkey-axum](https://crates.io/crates/oauth2-passkey-axum)
- **ドキュメント**: [ktaka-ccmp.github.io/oauth2-passkey](https://ktaka-ccmp.github.io/oauth2-passkey/)

## 背景

このライブラリは、2025年初頭に [Passkey 認証をスクラッチで実装した記事](https://ktaka.blog.ccmp.jp/2025/01/implementing-passkeys-authentication-in-rust-axum.html)がきっかけで生まれました。そのとき WebAuthn プロトコルを一から学んだ経験をもとに、OAuth2 連携・セッション管理・UI を備えた汎用ライブラリとして仕立て直しました。
