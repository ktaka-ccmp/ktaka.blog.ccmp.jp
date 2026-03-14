> この記事は [ktaka.blog.ccmp.jp の記事](https://ktaka.blog.ccmp.jp/2026/Oauth2PasskeyFedCM) のクロスポストです。

FedCM (Federated Credential Management) は、ブラウザがネイティブUIで提供するW3C標準の認証APIである。ポップアップやリダイレクトを使わず、ブラウザ自身がアカウント選択画面を表示し、IDプロバイダーと直接通信する。

[oauth2-passkey](https://github.com/ktaka-ccmp/oauth2-passkey) のRustライブラリに、このFedCMログインを実装した記録を紹介する。

---

## FedCMとは

従来のOAuth2 Authorization Code Flowでは、RP（あなたのアプリ）がGoogleのページにリダイレクトし、認証後にコールバックURLに戻ってくる。FedCMでは、`navigator.credentials.get()`を呼ぶだけで、ブラウザが直接Googleと通信してJWT IDトークンを返す。

```text
従来のOAuth2 Authorization Code Flow:
  ボタンクリック -> ポップアップ -> Googleの認証画面
    -> リダイレクト（認可コード付き）
    -> バックエンドがGoogleとコード交換（サーバー間通信）
    -> IDトークン取得 -> 検証 -> セッション確立

FedCM:
  ボタンクリック -> navigator.credentials.get()
    -> ブラウザがネイティブUIでアカウント選択画面を表示
    -> ブラウザがGoogleからJWT IDトークンを直接取得
    -> JSがトークンをバックエンドにPOST -> 検証 -> セッション確立
```

FedCMではブラウザが仲介役になるので、RPからロードしたJavaScriptはアカウントの一覧を見ることもできない。ブラウザがGoogleのセッションCookieを使って、ネイティブUIにアカウント情報を表示し、ユーザーが選択した結果だけがJavaScriptに返される。

## UI比較

![FedCMのアカウント選択画面](画像URL: fedcm-account-chooser.png)
*FedCMのアカウント選択画面（ブラウザがネイティブUIを表示）*

![従来のOAuth2ポップアップ](画像URL: oauth2-popup.png)
*従来のOAuth2 Authorization Code Flow（ポップアップウィンドウでGoogleの認証画面を表示）*

## フロントエンド実装

FedCMのフロントエンド実装は3ステップである。

### 1. Nonceの取得

```javascript
const nonceResponse = await fetch('/api/fedcm/nonce');
const nonceData = await nonceResponse.json();
// { nonce: "ランダム文字列", nonce_id: "キャッシュキー" }
```

### 2. navigator.credentials.get() の呼び出し

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

`mode: 'active'`は`identity`オブジェクトの直下に配置することが重要である。`providers`内に入れるとChromeが無視してpassive modeで動作し、ユーザーがダイアログを閉じるとクールダウンが発生してしまう。

### 3. バックエンドへのトークン送信

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
    // ログイン成功、Set-Cookieヘッダーでセッションクッキーが設定される
    window.location.reload();
}
```

## バックエンド実装

バックエンドの処理は5ステップである。

### 1. JWT検証（署名、iss/aud/exp、nonce）

```rust
fn validate_fedcm_token(token: String, nonce_id: String) -> IdInfo {
    // JWT署名検証、aud/iss/exp検証
    let idinfo = verify_idtoken(token, CLIENT_ID);

    // Nonce検証（単一使用を保証）
    verify_and_consume_nonce(nonce_id, idinfo.nonce);

    idinfo
}
```

JWT検証では以下を確認する:
- **署名検証**: GoogleのJWKS（公開鍵セット）を取得し、JWTヘッダーの`kid`で鍵を選択して署名検証
- **クレーム検証**: `iss`（発行者）、`aud`（Client ID）、`exp`（有効期限）が正しいことを確認
- **Nonce検証**: IDトークン内の`nonce`クレームが事前生成した値と一致することを確認し、検証後にキャッシュから削除して再利用を防ぐ

GoogleのFedCMエンドポイントが返すJWTは、Authorization Code Flowで取得するIDトークンと同じフォーマットである。つまり、既存のOAuth2認証のJWT検証コードをそのまま再利用できる。

### 2-5. ユーザー情報抽出、アカウント検索/作成、セッション作成、Set-Cookieヘッダー返却

これらの処理は従来のOAuth2フローと共通である。詳細は[完全版記事](https://ktaka.blog.ccmp.jp/2026/Oauth2PasskeyFedCM)を参照。

## セキュリティ上の考慮点

FedCMはUX改善をもたらすが、セキュリティモデルが従来のOAuth2/OIDCフローと異なる。

| 項目 | Authorization Code Flow + PKCE | FedCM |
|------|------|------|
| IDトークン取得 | サーバーが認可コードと交換 | ブラウザが直接取得 |
| JavaScriptがアクセスできる情報 | 認可コード（単体では無価値） | JWT IDトークン（認証に使える） |
| XSS攻撃のリスク | 認可コードだけでは認証できない | 有効期限内であれば認証に使える |

筆者の理解では、OAuth2 + PKCEの方がXSS攻撃への耐性が高い。なお、GoogleのOne Tap（GIS SDK）も同じモデルを採用している。

## ブラウザサポート

| ブラウザ | サポート状況 |
|---------|-------------|
| Chrome 108+ | サポート |
| Edge 108+ | サポート |
| Safari | 未サポート（ポップアップにフォールバック） |
| Firefox | 未サポート（ポップアップにフォールバック） |

## まとめ

FedCM実装を通じて明らかになったこと:

- FedCMのフロントエンドはnonce取得 → `navigator.credentials.get()` → バックエンドへPOSTの3ステップ
- バックエンドはJWT検証 → ユーザー情報抽出 → アカウント検索/作成 → セッション作成 → Set-Cookieの流れ。既存のJWT検証コードをそのまま再利用可能
- セキュリティモデルはAuthorization Code Flowと異なり、OAuth2 + PKCEの方がXSS攻撃への耐性が高い。FedCMはUX改善を優先したトレードオフ
- `navigator.credentials.get()`のパラメーターにはGoogle固有の要件があり、`mode: 'active'`の配置など正しい記法が重要

実装例は[oauth2-passkey](https://github.com/ktaka-ccmp/oauth2-passkey)を参照。[デモサイト](https://passkey-demo.ccmp.jp)で実際の動作を試せる。

## リンク

- **完全版記事**: [ktaka.blog.ccmp.jp/2026/Oauth2PasskeyFedCM](https://ktaka.blog.ccmp.jp/2026/Oauth2PasskeyFedCM)
- **ライブデモ**: [passkey-demo.ccmp.jp](https://passkey-demo.ccmp.jp)
- **GitHub**: [ktaka-ccmp/oauth2-passkey](https://github.com/ktaka-ccmp/oauth2-passkey)
- **ドキュメント**: [ktaka-ccmp.github.io/oauth2-passkey](https://ktaka-ccmp.github.io/oauth2-passkey/)

## 参考

- [FedCM W3C Spec](https://www.w3.org/TR/fedcm/)
- [MDN: FedCM API](https://developer.mozilla.org/en-US/docs/Web/API/FedCM_API)
- [Chrome: RP Implementation Guide](https://developer.chrome.com/docs/identity/fedcm/implement/relying-party)
- [Google: FedCM Migration Guide](https://developers.google.com/identity/gsi/web/guides/fedcm-migration)
