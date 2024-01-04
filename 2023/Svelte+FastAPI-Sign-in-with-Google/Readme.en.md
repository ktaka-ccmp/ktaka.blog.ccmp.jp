Table of Contents
=================
   * [Introduction](#introduction)
   * [What I Implement](#what-i-implement)
   * [Frontend implementation with Svelte](#frontend-implementation-with-svelte)
   * [Backend implementation with FastAPI](#backend-implementation-with-fastapi)
   * [Conclusion](#conclusion)

## Introduction

I have implemented Google Sign-In functionality in a sample website built using Svelte and FastAPI.
There are various methods to authenticate users in the backend API server after a successful Google Sign In.
One common approach is to send the JWT received from Google in the request header as `Authorization: "Bearer: JWT",` and if the JWT is valid, authorization to access resources is granted.
Another typical method involves issuing a JWT on the backend and using it for user authentication in the `Authorization` header.
However, using JWT directly for session management poses a challenge in immediate invalidation if the JWT is leaked. 
Reference: [Stop using JWT for sessions](http://cryto.net/~joepie91/blog/2016/06/13/stop-using-jwt-for-sessions/) .
Therefore, I implemented a method in which, following the receipt of the JWT from Google, FastAPI assigns a new session_id. This session_id is set in a cookie to maintain the session.

The session information is managed in FastAPI's session database, allowing administrators to invalidate sessions anytime.
Additionally, by adding Secure and HttpOnly attributes to the cookies, interception during transmission and access from JavaScript are prevented, enabling the development of a more secure website.

Note: I am self-taught in both Svelte and FastAPI, so I would appreciate any advice on improving anything.

## What I Implement

With authentication implemented, unauthenticated access will redirect to the login page, where you can log in with a Google account.

<a href="https://raw.githubusercontent.com/ktaka-ccmp/google-oauth2-example/v2.1.0/images/AuthLogin3-2.png"
target="_blank">
<img src="https://raw.githubusercontent.com/ktaka-ccmp/google-oauth2-example/v2.1.0/images/AuthLogin3-2.png"
width="80%" alt="Login page" title="Login page">
</a>

The Customer page can only be displayed after successful authentication.

<a href="https://raw.githubusercontent.com/ktaka-ccmp/google-oauth2-example/v2.1.0/images/AuthCustomer.png"
target="_blank">
<img src="https://raw.githubusercontent.com/ktaka-ccmp/google-oauth2-example/v2.1.0/images/AuthCustomer.png"
width="80%" alt="Customer page for authenticated users" title="Customer page for authenticated users">
</a>

In FastAPI, the Swagger UI automatically generates a documentation page.

<a href="https://raw.githubusercontent.com/ktaka-ccmp/google-oauth2-example/v2.1.0/images/fastapi01.png"
target="_blank">
<img src="https://raw.githubusercontent.com/ktaka-ccmp/google-oauth2-example/v2.1.0/images/fastapi01.png"
width="80%" alt="FastAPI OpenAPI doc page" title="FastAPI OpenAPI doc page">
</a>

## Frontend implementation with Svelte

I implemented the frontend JavaScript application using Svelte.
It includes authentication functionality using Google OAuth2 and retrieves customer data from the backend to display in a table.

Upon successful Google Sign-In, the obtained JWT is sent to the backend API server.
The backend verifies the JWT, creates a user account, sets the session_id in a cookie, and returns a response.
Thereafter, the session_id is always sent in the cookie to maintain a session.

The code for this implementation is available in the following repository:

- [frontend-svelte code](https://github.com/ktaka-ccmp/google-oauth2-example/tree/v2.1.0/google-oauth/frontend-svelte)

I will explain the key points of implementing the login functionality below.

### Routing

We use `svelete-routing` to set up routing as follows: 

- **/customer** : Displays the Customer component. 
- **/login** : Displays the LoginPage component.

Sample code for `App.svelte` is as follows:

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

### Login Page

We display Google's Sign-In button and also use the OneTap interface. 
After signing in with Google, the callback function `backendAuth` is called. 
`backendAuth` sends the response obtained from Google Sign-In to `http://localhost/api/login`. 
The response includes the JWT token. 
If the backend login is successful, it redirects to the previous page. 
If it fails, the error is handled and "navigated" back to the login page.

Sample code for `LoginPage.svelte` is as follows:

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

### Setup of Axios Instance

By setting `withCredentials: true`, axios will send cookies.
Axios's interceptors are used for error handling.
If `401 Unauthorized` or `403 Forbidden` are returned from the backend, it navigates to `/login`.

Sample code for `apiAxios.js` is as follows:

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

### LogoutButton Component

This component displays a Logout button.
On mount, it accesses the backend server to get information about the logged-in user.
If there is no session_id in the cookie, meaning the user is not logged in, the attempt to get user information fails, and the user is redirected to the `/login` page due to the error handling in `apiAxios.interceptor`.

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

### Customer Component

This component retrieves data from the backend server and displays it in a table.
Since the `LogoutButton` component is placed on the page, if the user is not logged in, it redirects to the `/login` page.

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

## Backend implementation with FastAPI

I implemented the backend API server using FastAPI. 
It verifies the JWT received from the frontend Javascript apps, creates a user account, issues a session_id, and registers it in the session database. 
The created session_id is set in a cookie and returned in the response. 
The backend API server creates a new user if a user corresponding to the JWT does not exist in the database.

When a request to an endpoint that requires authentication is received, FastAPI checks the session_id set in the cookie against the session database and returns the requested data if valid session information exists.

The code for this implementation is available in the following repository:

- [backend-fastapi code](https://github.com/ktaka-ccmp/google-oauth2-example/tree/v2.1.0/google-oauth/backend-fastapi)

I will explain the key points of implementing the login functionality below.

### /api/login Endpoint

The frontend app sends the JWT, and then the backend FastAPI app verifies it using Google's public certificates.
If verification is successful, the backend FastAPI app registers the user using the email address in the JWT as the username in the user database.
The information of the newly created user and the session_id are registered in the session database, and the session_id is set in a cookie in the response.

Sample code for `auth/auth.py` is as follows:

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

### Function to Determine Active Users

In the `get_current_user` function, FastAPI extracts the session_id from the cookie of the received request and considers the user logged in if it matches an entry in the session database.
The `get_current_active_user` checks whether the user is disabled, and the `get_admin_user` checks whether the user has admin privileges.

Sample code for `auth/auth.py` is as follows:

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

### Protecting Various Endpoints

The `/api/user/` endpoint is accessible only to logged-in users due to `Depends(get_current_active_user)`.

Sample code for `auth/auth.py` is as follows:

```
@router.get("/user/")
async def get_user(user: UserBase = Depends(get_current_active_user)):
    return {"username": user.name, "email": user.email,}
```

Routes defined in `customer/customer.py` are accessible only to authenticated users, and those in `admin/user.py` are accessible only to Admin users.

Sample code for `main.py` is as follows:

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

## Conclusion

I have implemented Google Sign-In functionality in a sample website built using Svelte and FastAPI. 
After receiving the JWT from Google, FastAPI issues a new session_id and maintains the session through cookies. 
The session information is managed in FastAPI's Session database, allowing administrators to invalidate sessions anytime. 
Additionally, adding Secure and HttpOnly attributes to the cookies can prevent interception and JavaScript access, enabling a more secure website development.
