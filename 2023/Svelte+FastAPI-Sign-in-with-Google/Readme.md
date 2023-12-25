<!-- <textarea border-style:dotted="border-style:dotted" class="markdown" disabled="disabled"> -->
<!-- <a href="" target="_blank"><img src="" width="30%"></a> -->

Table of Contents
=================

* [はじめに](#はじめに)
* [実装するもの](#実装するもの)
* [Svelteでのフロントエンドの実装](#svelteでのフロントエンドの実装)
   * [ルーティング](#ルーティング)
   * [ログインページ](#ログインページ)
   * [axiosインスタンスのセットアップ](#axiosインスタンスのセットアップ)
   * [LogoutButtonコンポーネント](#logoutbuttonコンポーネント)
   * [Customerコンポーネント](#customerコンポーネント)
* [FastAPIでのバックエンド実装](#fastapiでのバックエンド実装)
   * [/api/loginエンドポイント](#apiloginエンドポイント)
   * [アクティブユーザーを判別する関数](#アクティブユーザーを判別する関数)
   * [各種エンドポイントの保護](#各種エンドポイントの保護)
* [まとめ](#まとめ)

# はじめに

SvelteとFastAPIを用いて構築したサンプルウェブサイトにGoogleのサインイン機能を実装してみました。
Google Sign Inに成功したあとに、バックエンドのAPIサーバにログインするには様々な方法が考えれます。
Googleから受け取ったJWTを、RequestヘッダにAuthorization: "Bearer: JWT"として送信し、正しいJWTであれば、そのままそのまま認証されたものとみなしたり、更に、バックエンドでJWTを発行して、Authorizationヘッダにセットすることで認証済みユーザを識別する方法が、ポピュラーなようです。
しかしながら、JWTをそのままログインユーザの識別に利用する場合、JWTが漏洩した時に、即時の無効化が難しいという問題があります。
(参考: [Stop using JWT for sessions](http://cryto.net/~joepie91/blog/2016/06/13/stop-using-jwt-for-sessions/))
そこで、GoogleからJWTを受け取ったあと、FastAPI側であらたにsession_idを発行し、cookieを介してセッションを維持するやりかたで実装を行いました。

セッション情報はFastAPIのセッションデータベースで管理しているので、いつでも管理者がセッションを無効にすることができます。
またCookieにSecure属性とHttpOnly属性をつけることにより、経路での盗聴を防ぎ、JavaScriptからアクセスも防止することができ、より安全なWebサイトを構築することができます。

なおSvelteもFastAPIも独学で学習中です。もしおかしなとことがありましたら、アドバイス頂けると嬉しいです。

# 実装するもの

認証が実装されると、匿名ユーザーのアクセスはログインページにリダイレクトされ、そこでGoogleアカウントでログインできる。

<a href="" target="_blank">
<img src="https://github.com/ktaka-ccmp/react-api-oauth2-example/blob/master/images/AuthLogin3-2.png" width="80%" alt="Login page" title="Login page">
</a>
![Login page](https://github.com/ktaka-ccmp/react-api-oauth2-example/blob/master/images/AuthLogin3-2.png "Login page")

Customerページは、認証に成功した場合にのみ表示することができます。


<a href="" target="_blank">
<img src="https://github.com/ktaka-ccmp/react-api-oauth2-example/blob/master/images/AuthCustomer.png" width="80%" alt="Customer page for authenticated users" title="Customer page for authenticated users">
</a>
![Customer page for authenticated users](https://github.com/ktaka-ccmp/react-api-oauth2-example/blob/master/images/AuthCustomer.png "Customer page for authenticated users")

FastAPIではSwagger UIによるドキュメントページが自動生成されます。

<a href="" target="_blank">
<img src="https://github.com/ktaka-ccmp/react-api-oauth2-example/blob/master/images/fastapi01.png" width="80%" alt="FastAPI OpenAPI doc page" title="FastAPI OpenAPI doc page">
</a>
![FastAPI](https://github.com/ktaka-ccmp/react-api-oauth2-example/blob/master/images/fastapi01.png "FastAPI OpenAPI doc page")

# Svelteでのフロントエンドの実装

Svelteをフロントエンドを実装します。バックエンドからcustomerデータを取得しテーブル表示するページに、Google OAuth2を利用した認証機能を実装します。

Google Sign Inに成功し、取得したJWTをバックエンドのAPIサーバに送信します。
バックエンド側は、JWTをベリファイしユーザーアカウントを作成し、session_idをcookieにセットしてレスポンスを返信します。
これ以降、バックエンドにリクエストを送る際には、常にcookieにsession_idをセットして、リクエストを送信します。

実装したコードは以下のレポジトリにあります。
* https://github.com/ktaka-ccmp/react-api-oauth2-example/tree/master/google-oauth/frontend-svelte

ログイン機能の実装ポイントについて以下に説明します。

## ルーティング

* svelete-routingを利用します。
* **/customer**はCustomerコンポーネントを表示します。
* **/login**はLoginPageコンポーネントを表示します。

App.svelte
```
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

* GoogleのSign Inボタンを表示します。
* OneTapインターフェースも表示します。
* GoogleでSign In後に、コールバックファンクションbackendAuthを呼び出します。
* backendAuthで、Google Sign Inで得られたレスポンスをhttp://localhost/api/login に送信します。レスポンスにはJWTトークンが含まれます。
* バックエンドでのログインが成功した場合、**/login** の直前にいたページにリダイレクトします。
* バックエンドでのログインに失敗した場合、後述のapiAxios.interceptorのエラー処理が行われます。すなわち、もう一度**/login** ページにリダイレクトされます。

LoginPage.svelte
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

## axiosインスタンスのセットアップ

* **withCredentials: true**をセットすることにより、axiosはcookieを送信するようになります。
* axiosのinterceptorsで、error処理を行います。バックエンドから**401 Unauthorized**、**403 Forbidden** が返ってきた場合、/loginへリダイレクトします。

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

## LogoutButtonコンポーネント

* Logoutボタンを表示するコンポーネントです。
* onMount時に、バックエンドサーバにアクセスし、ログインしているユーザーのユーザー情報を取得します。
* cookieにsession_idが無い場合、すなわち未ログインの場合にはユーザー情報に失敗し、apiAxios.interceptorのエラー処理により、**/login** ページにリダイレクトされます。

```
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
      .catch((error) => console.log("getUser faild: ", error.response));
  };

  const onLogout = handleLogout;
</script>

<div>
  Authenticated as {user?.username} &nbsp;
  <button type="button" on:click={onLogout}>Sign Out</button>
</div>
```

## Customerコンポーネント

* バックエンドサーバからデータを取得し、テーブル表示するコンポーネント。
* **LogoutButton** コンポーネントがページ内に配置されているので、未ログインの場合には、**/login** ページにリダイレクトされる。

```
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
フロントエンドから受け取ったJWTのVerifyに成功した場合、ログインユーザーのsession_idを発行しセッションデータベースに登録します。
作成したsession_idをcookieにセットし、レスポンスを送信します。
受け取ったJWTに対応するユーザーがデータベースに存在しない場合、あらたにユーザーを作成します。

認証で保護されたエンドポイントへのリクエストを受け取った場合、cookieにセットされたsession_idとセッションデータベースを照合し、有効なセッション情報が存在している場合のみ、要求されたデータを返信します。

実装したコードは以下のレポジトリにあります。
* https://github.com/ktaka-ccmp/react-api-oauth2-example/tree/master/google-oauth/backend-fastapi

ログイン機能の実装ポイントについて以下に説明します。

## /api/loginエンドポイント

* フロントエンドからJWTを受け取り、[verify](https://github.com/googleapis/google-auth-library-python/blob/main/google/oauth2/id_token.py#L107)します。verifyにはgoogleのエンドポイントから取得した公開証明書を使います。
* verifyに成功すると、JWT内のemailアドレスを用いusername="emailアドレス"、email="emailアドレス"として、ユーザーデータベースにユーザーを登録します。
* 作成したユーザーの情報と新に作成したsession_idをセッションデータベースに登録します。
* cookieにsession_idをセットし、レスポンスを返します。

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

* FastAPIが受け取ったリクエストのCookieからsession_idを取り出し、セッションデータベース内のエントリと一致すればログイン済みとみなす。
* **get_current_active_user** で、disabledのフラグが立っていないか判別している。
* **get_admin_user** で、adminのフラグが立っているかどうか判別している。

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

* Depends(get_current_active_user) により、**(/api)/user/** エンドポイントはログインユーザーのみがアクセスできる。

auth/auth.py
```
@router.get("/user/")
async def get_user(user: UserBase = Depends(get_current_active_user)):
    return {"username": user.name, "email": user.email,}
```

* **customer/customer.py** で定義されたルートは**dependencies=[Depends(auth.auth.get_current_active_user)]** により、認証済みユーザーのみがアクセスできる。
* **admin/user.py** で定義されたルートは**dependencies=[Depends(auth.auth.get_admin_user)]** により、Adminユーザーのみがアクセスできる。

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

SvelteとFastAPIを用いて構築したサンプルウェブサイトにGoogleのサインイン機能を実装してみました。
、GoogleからJWTを受け取ったあと、FastAPI側であらたにsession_idを発行し、cookieを介してセッションを維持するやりかたで実装を行いました。
セッション情報はFastAPIのセッションデータベースで管理しているので、いつでも管理者がセッションを無効にすることができます。
またCookieにSecure属性とHttpOnly属性をつけることにより、経路での盗聴を防ぎ、JavaScriptからアクセスも防止することができ、より安全なWebサイトを構築することができます。

<!-- </textarea> -->
