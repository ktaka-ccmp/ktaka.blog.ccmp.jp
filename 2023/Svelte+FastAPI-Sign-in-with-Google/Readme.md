Table of Contents
=================

* [Table of Contents](#table-of-contents)
* [はじめに](#はじめに)
* [実装するもの](#実装するもの)
* [Svelteでのフロントエンドの実装](#svelteでのフロントエンドの実装)
* [FastAPIでのバックエンド実装](#fastapiでのバックエンド実装)
* [まとめ](#まとめ)

# はじめに

SvelteとFastAPIを使用して構築したサンプルウェブサイトにGoogleのサインイン機能を実装しました。
Google Sign Inに成功した後、バックエンドのAPIサーバーにログインするためには、様々な方法が考えられます。
Googleから受け取ったJWTを、Requestヘッダに`Authorization: "Bearer: JWT"`として送信し、正しいJWTであれば、認証されます。
また、バックエンドでJWTを発行し、`Authorization`ヘッダにセットして認証済みユーザーを識別する方法も一般的です。
しかし、JWTをそのままログインユーザーの識別に利用する場合、JWTの漏洩時に即時の無効化が難しい問題があります。
参考：[Stop using JWT for sessions](http://cryto.net/~joepie91/blog/2016/06/13/stop-using-jwt-for-sessions/)。
そこで、GoogleからJWTを受け取った後、FastAPI側で新たにsession_idを発行し、Cookieを介してセッションを維持する方法で実装しました。

セッション情報はFastAPIのセッションデータベースで管理されており、管理者がいつでもセッションを無効にできます。
また、CookieにSecure属性とHttpOnly属性を付与することで、経路での盗聴防止やJavaScriptからのアクセス防止が可能になり、より安全なWebサイトの構築が可能です。

なお、SvelteもFastAPIも独学で学習中ですので、おかしな点があれば、アドバイスいただけると嬉しいです。

# 実装するもの

認証が実装されると、未ログイン時のアクセスはログインページにリダイレクトされ、そこでGoogleアカウントでログインできます。

<a href="https://raw.githubusercontent.com/ktaka-ccmp/react-api-oauth2-example/master/images/AuthLogin3-2.png"
target="_blank">
<img src="https://raw.githubusercontent.com/ktaka-ccmp/react-api-oauth2-example/master/images/AuthLogin3-2.png"
width="80%" alt="Login page" title="Login page">
</a>

Customerページは、認証に成功した場合にのみ表示できます。

<a href="https://raw.githubusercontent.com/ktaka-ccmp/react-api-oauth2-example/master/images/AuthCustomer.png"
target="_blank">
<img src="https://raw.githubusercontent.com/ktaka-ccmp/react-api-oauth2-example/master/images/AuthCustomer.png"
width="80%" alt="Customer page for authenticated users" title="Customer page for authenticated users">
</a>

FastAPIではSwagger UIによるドキュメントページが自動生成されます。

<a href="https://raw.githubusercontent.com/ktaka-ccmp/react-api-oauth2-example/master/images/fastapi01.png"
target="_blank">
<img src="https://raw.githubusercontent.com/ktaka-ccmp/react-api-oauth2-example/master/images/fastapi01.png"
width="80%" alt="FastAPI OpenAPI doc page" title="FastAPI OpenAPI doc page">
</a>

# Svelteでのフロントエンドの実装

Svelteを使用してフロントエンドを実装します。
バックエンドからcustomerデータを取得し、テーブル表示するページにGoogle OAuth2を利用した認証機能を実装します。

Google Sign Inに成功し、取得したJWTをバックエンドのAPIサーバーに送信します。
バックエンド側では、JWTをベリファイしユーザーアカウントを作成し、session_idをCookieにセットしてレスポンスを返信します。
これ以降、バックエンドへのリクエスト時には、常にCookieにsession_idをセットして送信します。

実装したコードは以下のリポジトリにあります。

* [frontend-svelteのコード](https://github.com/ktaka-ccmp/react-api-oauth2-example/tree/master/google-oauth/frontend-svelte)

ログイン機能の実装ポイントを以下に説明します。

## ルーティング

svelete-routingを利用し、以下のようにルーティングを設定します。

* **/customer**: Customerコンポーネントを表示します。
* **/login**: LoginPageコンポーネントを表示します。

`App.svelte`のサンプルコードは次の通りです。

```svelte
<script>
  import { Router, Link, Route } from "svelte-routing";
  import Top from "./components/Top.svelte";
  import Customer from "./components/Customer.svelte";
  import NoMatch from "./components/NoMatch.svelte";
  import LoginPage from "./components/LoginPage.svelte";

  export let url = "";
</script>

<div class="container-sm">
  <Router {url}>
    <nav>
      <table class="table-borderless table-responsive">
        <tbody>
          <tr><td><Link to="/">Top</Link></td></tr>
          <tr><td><Link to="/customer">Customer</Link></td></tr>
        </tbody>
      </table>
    </nav>

    <div>
      <Route path="/"><Top /></Route>
      <Route path="/customer"><Customer /></Route>
      <Route path="/login"><LoginPage /></Route>
      <Route path="*"><NoMatch /></Route>
    </div>
  </Router>
</div>
```

## ログインページ

GoogleのSign Inボタンを表示し、OneTapインターフェースも利用します。
GoogleでSign In後、コールバックファンクション`backendAuth`を呼び出します。
`backendAuth`では、Google Sign Inで得られたレスポンスを`http://localhost/api/login`に送信します。
レスポンスにはJWTトークンが含まれます。
バックエンドでのログインが成功した場合、直前にいたページにリダイレクトします。
失敗した場合、エラー処理が行われ、再度ログインページにリダイレクトされます。

`LoginPage.svelte`のサンプルコードは次の通りです。

```svelte
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

## axiosインスタンスのセットアップ

`withCredentials: true`をセットすることでaxiosはCookieを送信するようになります。
axiosのinterceptorsでエラー処理を行い、バックエンドから`401 Unauthorized`、`403 Forbidden`が返ってきた場合、`/login`へリダイレクトします。

`apiAxios.js`のサンプルコードは次の通りです。

```javascript
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

## LogoutButtonコンポーネント

Logoutボタンを表示するコンポーネントです。
onMount時に、バックエンドサーバにアクセスし、ログインしているユーザーの情報を取得します。
cookieにsession_idが無い場合、すなわち未ログインの場合にはユーザー情報取得に失敗し、apiAxios.interceptorのエラー処理により、`/login`ページにリダイレクトされます。

```svelte
<script>
  import { onMount } from "svelte";
  import { apiAxios } from "../lib/apiAxios.js";

  let user;

  onMount(() => {
    console.log("Logout Component Mounted");
    getUser();
  });

  const handleLogout = () => {
    user = null;
    apiAxios
      .get(`/api/logout/`)
      .then((res) => {
        console.log("backendLogout", res);
        getUser();
      })
      .catch((error) => console.log("Logout failed: ", error));
  };

  const getUser = () => {
    apiAxios
      .get(`/api/user/`)
      .then((res) => {
        user = res.data;
        console.log("getUser: user:", user);
      })
      .catch((error) => console.log("getUser failed: ", error.response));
  };

  const onLogout = handleLogout;
</script>

<div>
  Authenticated as {user?.username} &nbsp;
  <button type="button" on:click={onLogout}>Sign Out</button>
</div>
```

## Customerコンポーネント

バックエンドサーバからデータを取得し、テーブル表示するコンポーネントです。`LogoutButton` コンポーネントがページ内に配置されているので、未ログインの場合には、`/login` ページにリダイレクトされます。

```svelte
<script>
  import { onMount } from "svelte";
  import { apiAxios } from "../lib/apiAxios";
  import LogoutButton from "./LogoutButton.svelte";

  let customers = [];

  const getCustomers = async () => {
    await apiAxios
      .get(`/api/customer/`)
      .then((res) => {
        customers = res.data.results;
      })
      .catch((error) => {
        console.log(error);
      });
  };

  onMount(async () => {
    getCustomers();
  });
</script>

<LogoutButton />

<h2>This is Customer.</h2>

{#await customers}
  <p>Loading ...</p>
{:then customers}
  <div class="table-responsive">
    <table class="table table-bordered table-hover table-striped">
      <thead class="table-light">
        <tr>
          <th>id</th>
          <th>name</th>
          <th>email</th>
        </tr>
      </thead>
      <tbody>
        {#each customers as cs}
          <tr>
            <td>{cs.id}</td>
            <td>{cs.name}</td>
            <td>{cs.email}</td>
          </tr>
        {/each}
      </tbody>
    </table>
  </div>
{/await}
```

# FastAPIでのバックエンド実装

FastAPIを使用して、バックエンドのAPIサーバを実装します。
フロントエンドから受け取ったJWTを検証し、ユーザーアカウントを作成して、session_idを発行しセッションデータベースに登録します。
作成したsession_idをCookieにセットしてレスポンスを返信します。
受け取ったJWTに対応するユーザーがデータベースに存在しない場合、新たにユーザーを作成します。

認証で保護されたエンドポイントへのリクエストを受け取った場合、Cookieにセットされたsession_idとセッションデータベースを照合し、有効なセッション情報が存在している場合のみ、要求されたデータを返信します。

実装したコードは以下のリポジトリにあります。

* [backend-fastapiのコード](https://github.com/ktaka-ccmp/react-api-oauth2-example/tree/master/google-oauth/backend-fastapi)

ログイン機能の実装ポイントについて以下に説明します。

## /api/loginエンドポイント

フロントエンドからJWTを受け取り、Googleの公開証明書を使用してJWTを検証します。
検証に成功すると、JWT内のemailアドレスを使用してユーザーデータベースにユーザーを登録します。
新しく作成したユーザーの情報とsession_idをセッションデータベースに登録し、Cookieにsession_idをセットしてレスポンスを返します。

auth/auth.py
```
async def VerifyToken(jwt: str):
    try:
        idinfo = id_token.verify_oauth2_token(
            jwt,
            requests.Request(),
            settings.google_oauth2_client_id)
    except ValueError:
        print("Error: Failed to validate JWT token with GOOGLE_OAUTH2_CLIENT_ID=" + settings.google_oauth2_client_id +".")
        return None

    print("idinfo: ", idinfo)
    return idinfo

@router.post("/login")
async def login(request: Request, response: Response, ds: Session = Depends(get_db), cs: Session = Depends(get_cache)):
    body = await request.body()
    jwt = json.loads(body)["credential"]
    if jwt == None:
        return  Response("Error: No JWT found")
    print("JWT token: " + jwt)

    idinfo = await VerifyToken(jwt)
    if not idinfo:
        print("Error: Failed to validate JWT token")
        return  Response("Error: Failed to validate JWT token")

    user = await GetOrCreateUser(idinfo, ds)

    if user:
        user_dict = get_user_by_name(user.name, ds)
        if not user_dict:
            raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail="Error: User not exist in User table in DB.")
        user = UserBase(**user_dict)
        session_id = create_session(user, cs)
        response.set_cookie(
            key="session_id",
            value=session_id,
            httponly=True,
            max_age=1800,
            expires=1800,
        )
    else:
        return Response("Error: Auth failed")
    return {"Authenticated_as": user.name}
```

## アクティブユーザーを判別する関数

FastAPIが受け取ったリクエストのCookieからsession_idを取り出し、セッションデータベース内のエントリと一致すればログイン済みとみなします。
`get_current_active_user`では、disabledのフラグが立っていないか判別し、`get_admin_user`では、adminのフラグが立っているかどうか判別します。

auth/auth.py
```
async def get_current_user(ds: Session = Depends(get_db), cs: Session = Depends(get_cache), session_id: str = Depends(oauth2_scheme)):
    if not session_id:
        return None

    session = get_session_by_session_id(session_id, cs)
    if not session:
        return None

    username = session["name"]
    user_dict = get_user_by_name(username, ds)
    user=UserBase(**user_dict)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="NotAuthenticated")
    if current_user.disabled:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Inactive user")
    return current_user

async def get_admin_user(current_user: User = Depends(get_current_active_user)):
    print("CurrentUser: ", current_user)
    if not current_user.admin:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Admin Privilege Required")
    return current_user
```

## 各種エンドポイントの保護

`Depends(get_current_active_user)`により、`/api/user/`エンドポイントはログインユーザーのみがアクセスできます。

auth/auth.py
```
@router.get("/user/")
async def get_user(user: UserBase = Depends(get_current_active_user)):
    return {"username": user.name, "email": user.email,}
```

`customer/customer.py`で定義されたルートは認証済みユーザーのみ、`admin/user.py`で定義されたルートはAdminユーザーのみがアクセスできます。

main.py
```
import admin.debug, admin.user, auth.auth, auth.debug
import customer.customer

app = FastAPI()

app.include_router(
    customer.customer.router,
    prefix="/api",
    tags=["CustomerForAuthenticatedUser"],
    dependencies=[Depends(auth.auth.get_current_active_user)],
)

app.include_router(
    admin.user.router,
    prefix="/api",
    tags=["AdminOnly"],
    dependencies=[Depends(auth.auth.get_admin_user)],
)
```

# まとめ

SvelteとFastAPIを用いて構築したサンプルウェブサイトにGoogleのサインイン機能を実装しました。
GoogleからJWTを受け取った後、FastAPI側で新たにsession_idを発行し、Cookieを介してセッションを維持する方法で実装しました。
セッション情報はFastAPIのセッションデータベースで管理されており、いつでも管理者がセッションを無効にできます。
また、CookieにSecure属性とHttpOnly属性を付与することで、経路での盗聴防止やJavaScriptからのアクセス防止が可能になり、より安全なWebサイトの構築が可能です。
