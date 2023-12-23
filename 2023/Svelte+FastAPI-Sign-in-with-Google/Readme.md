<!-- <textarea border-style:dotted="border-style:dotted" class="markdown" disabled="disabled"> -->
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

多くのモダンなウェブサイトでは、Gmailアカウント（Googleアカウント）を利用したユーザーログイン機能が備わっています。
世の中にはGmailアカウントを持つユーザーが多く、これにより多くのユーザーにとって新しいユーザー名やパスワードを覚える必要がなくなり、
セキュリティ面でも優れた選択肢となっています。
SvelteはモダンなJavaScriptフレームワークで、実行時のオーバーヘッドが少なく、
コンパイル時の最適化によって軽量かつ高速なウェブアプリケーションの開発を可能にします。
また、FastAPIはPythonベースの効率的なウェブフレームワークで、非同期処理と自動APIドキュメント生成の機能を備え、
高速でスケーラブルなAPI開発を実現します。
今回、私はSvelteとFastAPIを用いて構築したサンプルウェブサイトにGoogleのサインイン機能を実装する方法を試してみました。
この組み合わせにより、効率的でセキュアなユーザー体験を提供するウェブアプリケーションの構築が可能になります。

## Svelteについて

Svelteは、リッチでインタラクティブなウェブインターフェイスを構築するためのモダンなJavaScriptフレームワークです。コンパイル時に高性能なJavaScriptに変換されるため、ブラウザでの負荷を軽減します。React.jsと比較すると、Svelteは以下の特徴を持ちます：

- **コンパイル時のアプローチ**: Svelteはコンパイル時にUIコンポーネントを最適化し、React.jsが使用する仮想DOMのような実行時のオーバーヘッドを削減します。これにより、実行時に余分なフレームワークのコードをロードする必要がなくなり、パフォーマンスが向上します。
- **宣言的なコーディング**: アプリケーションの状態とUIの連動を宣言的に記述することができ、開発者はUIの見た目に集中できます。
- **簡潔なシンタックス**: SvelteのシンタックスはReact.jsのJSXよりも簡潔で直感的です。これにより、学習曲線が低く、新しい開発者でも迅速に理解し使用することができます。
- **リアクティブな更新**: アプリケーションの状態が変わると、必要な部分のみを自動的に更新し、効率的なレンダリングを実現します。
- **小さなバンドルサイズ**: コンパイル時の最適化により生成されるJavaScriptのバンドルサイズが小さくなり、ページの読み込み速度が向上します。
- **シンプルな状態管理**: SvelteはReact.jsのReactHookに比べて、より簡素化された状態管理を提供し、コードの複雑さを減らします。

## FastAPIの特徴

FastAPIは、PythonでのAPI開発に特化した高速なウェブフレームワークです。その主な特徴は以下のとおりです：

- **高速性**: 非同期処理を完全サポートし、特にI/O処理で高いパフォーマンスを実現します。
- **自動APIドキュメント生成**: SwaggerUIとReDocを利用して、APIのドキュメントを自動で生成します。
- **型ヒントによるデータバリデーション**: Pythonの型ヒントを活用し、リクエストとレスポンスのバリデーションを効率的に行います。
- **依存性注入**: 再利用可能なコンポーネントの統合が容易な依存性注入システムを提供します。
- **セキュリティと認証**: OAuth2をはじめとする複数のセキュリティスキームをサポートし、APIのセキュリティを強化します。

## アーキテクチャ

## Googleサインインの実装

### ステップ1: Google APIコンソールでのOAuth設定

1. **Google APIコンソールへのアクセス**:
   - [Google Cloud Console - 認証情報ページ](https://console.cloud.google.com/apis/credentials)にアクセスします。

2. **OAuth認証情報の作成**:
   - 「CREATE CREDENTIALS」ボタンをクリックします。
   - ドロップダウンから「Create OAuth client ID」を選択します。

3. **OAuthクライアントIDの設定**:
   - アプリケーションタイプとして「Web applicatin」を選択します。
   - 必要な詳細情報（名前など）を入力します。

4. **クライアントIDの保存**:
   - OAuthクライアントIDが作成されると、クライアントIDが提供されます。
   - このクライアントIDを安全に保存しておきます。

5. **承認されたJavaScriptオリジンの設定**:
   - 作成したOAuth 2.0クライアントIDの一覧に戻り、選択します。
   - 「Authorized JavaScript origins」セクションに以下のURLを追加します：
     - `http://localhost`
     - `http://localhost:3000`

6. **詳細については公式ドキュメントを参照**:
   - 詳細については、[Google APIクライアントIDを取得する](https://developers.google.com/identity/gsi/web/guides/get-google-api-clientid)の公式ドキュメントを参照してください。

### ステップ2: Svelteでのフロントエンド実装

Svelteを使用して、ユーザーがGoogleアカウントでログインできるボタンを作成します。ユーザーがこのボタンをクリックすると、Googleの認証ページにリダイレクトされます。

https://github.com/ktaka-ccmp/react-api-oauth2-example/tree/master/google-oauth/frontend-svelte

ログイン機能の実装ポイントについて以下に説明します。

#### axiosのセットアップ

* バックエンドとのセッションを維持するためにcookieを送信する設定、**withCredentials: true**、を行います。
* axiosのinterceptorsで、error処理を行います。バックエンドから**401 Unauthorized**、**403 Forbidden**が返ってきた場合、/loginへリダイレクトします。

apiAxios.js
```
import axios from "axios";
import { navigate } from "svelte-routing";

export const apiAxios = axios.create({
  baseURL: `${import.meta.env.VITE_APP_API_SERVER}`,
  withCredentials: true,
});

apiAxios.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response.status === 401 || error.response.status === 403) {
        console.log(
        "apiAxios failed. Redirecting to /login... from",
        location.pathname
      );
      navigate("/login", { state: { from: location.pathname }, replace: true });
    }
    return Promise.reject(error);
  }
);
```

#### ログインページ

* GoogleのSign-inボタンを表示します。
* OneTapインターフェースも表示します。
* GoogleでSign-in後に、コールバックファンクションbackendAuthを呼び出します。
* backendAuthで、Google Sign-inで得られたレスポンスをhttp://localhost/api/login にpostリクエストを送信します。Google Sign-inに成功した場合には、レスポンスにはログインユーザーのJWTトークンが含まれます。
* バックエンドでのログインが成功した場合、*/api/login*の直前にいたページにリダイレクトします。
* バックエンドでのログインに失敗した場合、apiAxios.interceptorのエラー処理が行われます。すなわち、もう一度*/api/login*ページにリダイレクトされます。

UserLogin.svelte
```
<script>
  import { onMount } from "svelte";
  import { apiAxios } from "../lib/apiAxios";
  import { useLocation, navigate } from "svelte-routing";

  let location = useLocation();
  let origin = $location.state?.from;

  const backendAuth = (response) => {
    const data = JSON.stringify(response, null, 2);

    apiAxios
      .post(`/api/login/`, data)
      .then((res) => {
        navigate(origin, { replace: true });
      });
  };

  onMount(() => {

    google.accounts.id.initialize({
      /* global google */
      client_id: import.meta.env.VITE_APP_GOOGLE_OAUTH2_CLIENT_ID,
      callback: (r) => backendAuth(r),
      ux_mode: "popup",
    });

    google.accounts.id.renderButton(document.getElementById("signInDiv"), {
      theme: "filled_blue",
      size: "large",
      shape: "circle",
    });

    google.accounts.id.prompt();
  });
</script>

<main>
  <h2>Login page</h2>
  <div id="signInDiv"></div>
</main>
```
 
### ステップ3: FastAPIでのバックエンド実装

FastAPIを使用して、Googleからの認証応答を処理するエンドポイントを作成します。認証が成功すると、ユーザーの情報が取得され、セッションが開始されます。

https://github.com/ktaka-ccmp/react-api-oauth2-example/tree/master/google-oauth/backend-fastapi



## 結論

SvelteとFastAPIを組み合わせることで、効率的かつ安全にGoogleのサインイン機能をウェブアプリケーションに統合できることがわかりました。このアプローチは、ユーザビリティとセキュリティの両方を高めるための素晴らしい方法です。

<!-- </textarea> -->
