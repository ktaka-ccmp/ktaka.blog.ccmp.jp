+++
title = "Rust 認証ライブラリ oauth2-passkey で FedCM ログイン機能を実装した"
date = 2026-03-13
description = "FedCM ログイン機能の実装記録。ブラウザ標準 API の利用、JWT 検証の再利用、セキュリティのトレードオフ。"
path = "2026/Oauth2PasskeyFedCM"
+++

<p style="text-align: right"><a href="/en/2026/Oauth2PasskeyFedCM">English version</a></p>

FedCM (Federated Credential Management)は、フェデレーション認証をブラウザネイティブのUIで行うためのW3C標準APIである。ポップアップウィンドウやリダイレクトを使わず、ブラウザ自身がアカウント選択画面を表示し、IDプロバイダーと直接通信する。

この記事では、FedCMの仕組み、実装方法、従来のOAuth2 Authorization Code Flowとの違い、そしてセキュリティ上のトレードオフを解説する。

---

## FedCMとは

FedCM (Federated Credential Management)は、フェデレーション認証をブラウザネイティブのUIで行うためのAPIである。ポップアップウィンドウもリダイレクトも使わず、ブラウザ自身がアカウント選択画面を表示する。

従来のOAuth2フローでは、RP(あなたのアプリ)からGoogleのページにリダイレクトし、認証後にコールバックURLに戻ってくる必要があった。FedCMでは、`navigator.credentials.get()`を呼ぶだけで、ブラウザがGoogleと直接通信し、JWTのIDトークンを返す。

```text
従来のOAuth2 Authorization Code Flow:
  ボタンクリック -> ポップアップ -> Google認証画面
    -> リダイレクト(認可コード付き)
    -> バックエンドが認可コードをGoogleと交換 (server-to-server)
    -> IDトークン取得 -> 検証 -> セッション確立

FedCM:
  ボタンクリック -> navigator.credentials.get()
    -> ブラウザがネイティブUIでアカウント選択画面を表示
    -> ブラウザがGoogleからJWT IDトークンを直接取得
    -> JSがトークンをバックエンドにPOST -> 検証 -> セッション確立
```

FedCMではブラウザが仲介役になるので、RPからロードしたJavaScriptはアカウントの一覧を見ることもできない。ブラウザがGoogleのセッションCookieを使って、ネイティブUIにアカウント情報を表示し、ユーザーが選択した結果だけがJavaScriptに返される。

<div style="display: flex; gap: 20px; flex-wrap: wrap;">
  <div style="flex: 1; min-width: 300px;">
    <img width="408" src="/2026/Oauth2PasskeyFedCM/image/fedcm-account-chooser.png" alt="FedCMのブラウザネイティブUI">
    <p><em>FedCMのアカウント選択画面（ブラウザがネイティブUIを表示）</em></p>
  </div>
  <div style="flex: 1; min-width: 300px;">
    <img width="408" src="/2026/Oauth2PasskeyFedCM/image/oauth2-popup.png" alt="従来のOAuth2ポップアップ">
    <p><em>従来のOAuth2 Authorization Code Flow（ポップアップウィンドウでGoogleの認証画面を表示）</em></p>
  </div>
</div>

## 実装方針

FedCMはブラウザの標準API (`navigator.credentials.get()`)として提供されている。Googleは[GIS SDK](https://developers.google.com/identity/gsi/web)経由での利用を推奨しているが、標準APIであるので、SDKなしで直接呼び出すことができる。

標準APIを直接使う利点は、ライブラリ依存が不要なことと、内部の動作を理解しやすいことである。何がどう動いているかを把握できれば、問題の切り分けも容易になる。

本記事では、[oauth2-passkey](https://github.com/ktaka-ccmp/oauth2-passkey)での実装を例に、FedCMを標準APIとして直接扱う方法を説明する。

## フロントエンドの実装

FedCMのフロントエンド実装は、大きく4つのステップである。

### 1. Nonceの取得

まず、サーバからnonceを取得する。このnonceはリプレイ攻撃を防ぐため、一度だけ使える値である。

```javascript
const nonceResponse = await fetch('/api/fedcm/nonce');
const nonceData = await nonceResponse.json();
// { nonce: "ランダムな文字列", nonce_id: "キャッシュキー" }
```

### 2. navigator.credentials.get()の呼び出し

取得したnonceを使って、FedCMのAPIを呼び出す。

```javascript
const credential = await navigator.credentials.get({
    identity: {
        providers: [{
            configURL: 'https://accounts.google.com/gsi/fedcm.json',
            clientId: OAUTH2_CLIENT_ID,
            params: {
                nonce: nonceData.nonce,
                response_type: 'id_token',
                scope: 'email profile openid',
                ss_domain: window.location.origin,
            },
        }],
        mode: 'active',
        context: 'signin',
    },
    mediation: 'required',  // 自動再認証を防ぎ、常にユーザー操作を要求
});
```

`configURL`はGoogleのFedCM設定ファイルのURLである。ブラウザはここから各エンドポイントの場所を取得する。`params`内の`response_type`、`scope`、`ss_domain`はGoogle固有の要件で、FedCMのW3C仕様には含まれていない(後述)。`ss_domain`には実行環境のオリジン(例: `https://passkey-demo.ccmp.jp`)が入る。

`mode: 'active'`はユーザーのボタンクリックに応答する場合に使う。これが`identity`オブジェクトの直下にあることが重要である。

`mediation: 'required'`は自動再認証を防ぐためのパラメーターである。これを指定することで、ブラウザは常にユーザーにアカウント選択を求める。

### 3. バックエンドへのトークン送信

取得したIDトークンとnonce_idをバックエンドに送信する。

```javascript
const response = await fetch('/api/fedcm/callback', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        token: credential.token,
        nonce_id: nonceData.nonce_id
    })
});

if (response.ok) {
    // ログイン成功、セッションクッキーがSet-Cookieヘッダーで設定される
    window.location.reload();
}
```

バックエンドはこのIDトークンを検証し、セッションを確立する。

### 4. OAuth2へのフォールバック

```javascript
function openPopup() {
    if (isFedCMAvailable()) {
        fedcmLogin().catch(function(err) {
            console.log('FedCM failed, falling back to OAuth2 popup:', err.message);
            openPopupOAuth2();
        });
        return;
    }
    openPopupOAuth2();
}
```

FedCMが失敗した場合(非対応ブラウザ、ユーザーがダイアログを閉じた、エラーなど)は、Promiseの`.catch()`で従来のOAuth2ポップアップフローが自動的に開始される。

## バックエンドの実装

バックエンドの処理は、大きく5つのステップである。

### 1. JWT検証(署名、iss/aud/exp、nonce)

フロントエンドから受け取ったIDトークンはJWT形式であり、署名検証とクレーム検証を行う。

```rust
fn validate_fedcm_token(token: String, nonce_id: String) -> IdInfo {
    // JWT署名検証、aud/iss/exp検証
    let idinfo = verify_idtoken(token, CLIENT_ID);

    // Nonce検証(一度だけ使えることを保証)
    verify_and_consume_nonce(nonce_id, idinfo.nonce);

    idinfo
}
```

JWT検証では以下を確認する。

- **署名検証**: GoogleのJWKS(公開鍵セット)を取得し、JWTヘッダーの`kid`で鍵を選び、署名を検証
- **クレーム検証**: `iss`(発行者)、`aud`(Client ID)、`exp`(有効期限)が正しいかを確認
- **Nonce検証**: IDトークン内の`nonce`クレームが、事前に生成したものと一致するかを確認し、検証後にキャッシュから削除することで再利用を防ぐ

GoogleのFedCMエンドポイントが返すJWTは、Authorization Code Flowで取得するIDトークンと同じ形式である。つまり、既存のOAuth2認証のJWT検証コードをそのまま再利用できる。

### 2. ユーザー情報の抽出

検証済みのIDトークンから、ユーザー情報を取り出す。

```rust
let user_info = UserInfo {
    email: idinfo.email,
    name: idinfo.name,
    provider_user_id: idinfo.sub,  // GoogleのユーザーID
};
```

`IdInfo`には`email`、`name`、`sub`(プロバイダー内のユーザーID)などが含まれており、これを取り出して後続の処理で使う。

### 3. ユーザーの検索または作成

プロバイダーのユーザーIDでアカウントを検索し、存在しなければ新規作成する。

```rust
// プロバイダーのユーザーIDで既存アカウントを検索
let existing_user = db.find_user_by_provider_id(user_info.provider_user_id);

let user_id = match existing_user {
    Some(user) => {
        // 既存ユーザーでログイン
        user.id
    }
    None => {
        // 新規ユーザーを作成
        let new_user = db.create_user(user_info.email, user_info.name);
        db.link_provider(new_user.id, user_info.provider_user_id);
        new_user.id
    }
};
```

既存ユーザーが見つかればそのユーザーIDを使い、見つからなければ新規作成する。

### 4. セッションの作成

ユーザーIDが確定したら、セッションを作成する。

```rust
fn create_session(user_id: String) -> (String, Headers) {
    // セッションIDとCSRFトークンを生成
    let session_id = generate_random_string(32);
    let csrf_token = generate_random_string(32);
    let expires_at = now() + Duration::hours(1);

    // セッションをストアに保存
    let session = Session {
        user_id,
        csrf_token,
        expires_at,
    };
    cache.store(session_id, session, ttl: 24h);

    // Set-Cookieヘッダーを作成
    let headers = Headers::new();
    headers.set_cookie("session_id", session_id, expires_at);

    (session_id, headers)
}
```

セッションIDはランダムに生成され、キャッシュストア(Redisなど)に保存される。CSRFトークンもここで生成し、セッションと紐づけて保存する。

### 5. Set-Cookieヘッダーの返却

作成したセッションクッキーを`Set-Cookie`ヘッダーとしてブラウザに返す。

```rust
// レスポンスを返す
return Response {
    status: 200,
    headers: headers,  // Set-Cookieヘッダーを含む
    body: json!({ "success": true }),
};
```

ブラウザはこのクッキーを次回のリクエストで自動的に送信し、認証状態が維持される。

---

認証後のユーザー処理(アカウントの検索・作成、セッションの発行、ログイン履歴の記録)は、OAuth2と共通の関数を使う。

## セキュリティについて

FedCMはUXの改善をもたらすが、セキュリティモデルは従来のOAuth2/OIDCフローと異なる。

| 観点 | Authorization Code Flow + PKCE | FedCM |
|------|------|------|
| IDトークンの取得 | サーバが認可コードを交換して取得 | ブラウザが直接取得 |
| JavaScriptがアクセスできる情報 | 認可コード(無価値) | JWT IDトークン(認証に使える) |
| XSS攻撃のリスク | 認可コードだけでは認証不可 | 有効期間内なら認証に使える |

筆者の理解では、OAuth2 + PKCEの方がXSS攻撃に対する耐性は高いと考えている。なお、GoogleのOne Tap(GIS SDK)も同じモデルを採用している。

（セキュリティの評価について異なる見解や補足があれば、ぜひ教えてほしい）

## FedCM APIを呼ぶ際の注意

`navigator.credentials.get()`に渡すJSONオブジェクトのパラメータには以下の注意が必要である。

### Google固有の必須フィールド

GoogleのFedCMエンドポイントを使用する場合、`params`オブジェクト内に以下のパラメータが必要である。

| フィールド | 値 | 説明 |
|-----------|-----|------|
| `response_type` | `'id_token'` | GoogleがJWTを返すために必要 |
| `scope` | `'email profile openid'` | 要求するスコープ |
| `ss_domain` | `window.location.origin` | RPのオリジン |

### `mode: 'active'`の記述位置

FedCMにはactive modeとpassive modeがある。active modeはユーザーのボタン操作に応答し、passive modeはページ読み込み時に自動表示する。

active modeを使う場合、`mode: 'active'`は`identity`オブジェクトの直下に置く必要がある。providerオブジェクトの中に置くと、Chromeはそれを無視してpassive modeで動作する。エラーも出ない。

passive modeではユーザーがダイアログを閉じるとクールダウンが発生し、2時間から最長4週間FedCMが使えなくなる。active modeにはこのクールダウンがない。配置を間違えると、ユーザーが一度ダイアログを閉じただけでFedCMが長期間使えなくなる、という問題が起きる。

### その他の注意点

**JSONラップされたJWT:** GoogleのFedCMエンドポイントは、JWTを`{"token":"eyJ..."}`というJSONでラップして返す場合がある。生のJWT文字列ではないので、パースが必要である。

**nonceの`params`移行:** Chrome 143以降、nonceはproviderオブジェクトの直下ではなく`params`オブジェクト内に配置する必要がある。Chrome 145で旧形式は削除された。

## ブラウザサポート

| ブラウザ | 対応状況 |
|---------|---------|
| Chrome 108+ | 対応 |
| Edge 108+ | 対応 |
| Safari | 非対応(ポップアップにフォールバック) |
| Firefox | 非対応(ポップアップにフォールバック) |


## まとめ

FedCMの実装を通じて見えてきたこと:

- FedCMのフロントエンドはnonce取得 → `navigator.credentials.get()` → バックエンドへPOSTの3ステップ。失敗時はOAuth2ポップアップに自動フォールバック
- バックエンドはJWT検証 → ユーザー情報抽出 → ユーザー検索/作成 → セッション作成 → Set-Cookieの流れ。既存のJWT検証コードをそのまま使える
- セキュリティモデルはAuthorization Code Flowと異なり、OAuth2 + PKCEの方がXSS攻撃への耐性は高い。FedCMはUX改善を優先したトレードオフ
- `navigator.credentials.get()`のパラメータにはGoogle固有の要件があり、`mode: 'active'`の配置など正しい記述が重要

実装例は[oauth2-passkey](https://github.com/ktaka-ccmp/oauth2-passkey)を参照。[デモサイト](https://passkey-demo.ccmp.jp)で実際の動作を試せる。

## 参考

- [FedCM W3C Spec](https://www.w3.org/TR/fedcm/)
- [MDN: FedCM API](https://developer.mozilla.org/en-US/docs/Web/API/FedCM_API)
- [Chrome: RP Implementation Guide](https://developer.chrome.com/docs/identity/fedcm/implement/relying-party)
- [Google: FedCM Migration Guide](https://developers.google.com/identity/gsi/web/guides/fedcm-migration)
