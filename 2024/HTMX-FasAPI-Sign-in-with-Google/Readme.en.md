<!-- # Sign in with Google in HTMX+FastAPI -->

- [TL;DR](#tldr)
- [Introduction](#introduction)
- [What I Implemented](#what-i-implemented)
  - [Anonymous User Page](#anonymous-user-page)
  - [Authenticated User Page](#authenticated-user-page)
- [HTMX with FastAPI](#htmx-with-fastapi)
- [Authentication Overview](#authentication-overview)
- [Frontend Auth](#frontend-auth)
  - [Sign-in with Google button](#sign-in-with-google-button)
    - [JavaScript Version](#javascript-version)
    - [HTML Version](#html-version)
  - [The Callback Function](#the-callback-function)
- [Backend Auth](#backend-auth)
- [Conclusion](#conclusion)

# TL;DR

The "Sign in with Google" button has been integrated into a sample HTMX+FastAPI web application. Either an HTML or JavaScript version of a code snippet from Google's code generator is included in the HTML to display the button. The FastAPI backend has been configured to create a session from the JWT and set "Set-Cookie: session_id" in the header, enabling subsequent communications to maintain the login status through a session cookie. Thanks to HTMX functionality, the application page can dynamically fetch the navigation bar upon a change in login status, indicating whether the user is logged in.

# Introduction

As an aspiring full-stack software developer, I've been teaching myself various front-end web technologies recently.
These include React.js, Svelte, and other shiny new JavaScript frameworks, which can sometimes be overwhelming.
I was considering settling on Svelte, thanks to its simplicity in state management, when I discovered a concept called Hypermedia as the Engine of Application State (HATEOAS) and a library named htmx.js.

Initially, I didn't quite grasp how it differed from other technologies.
However, after creating several web pages for practice, I realized I didn't need to switch into a dedicated front-end programming mode.
I felt liberated from the struggle of forcing myself into the React mental model, which always seemed nonsensical to me.
I often questioned, 'Why must I change my mental model every time I create a small piece of a web page?'

With htmx.js, I can simply create a page, and when I need to change parts of it, I just fire an AJAX request using hx-get and swap the DOM elements with HTML fragments in the response.
I understand that as a web application becomes more complex, there might be situations where more feature-rich technologies are necessary.
But now, I'm no longer intimidated by the overwhelming ecosystems of each technology.

Now, I wanted to explore how I could implement a login feature in a web application, specifically using the 'Sign-in with Google' feature on a web page developed with HTMX and FastAPI.
So, I did a bit of research and figured out how to do it.
Noticing a lack of use cases on the web for this particular combination of technologies, I decided to share my findings.

While integrating the 'Sign-in with Google' button into an HTMX page isn’t much different from incorporating it into a standard HTML page, the following aspects seemed particularly noteworthy:

- How to display the status after a successful login or logout using HTMX.
- The handling of the JWT after a successful login on Google's side.
- How to maintain a session via a cookie generated upon successful JWT verification, rather than solely relying on the JWT for session management.

These points are especially relevant for beginners like myself.

# What I Implemented

The webpage I developed using FastAPI and HTMX is shown in the figure below.
This page integrates a 'Sign-in with Google' option, enhancing user experience and offering a secure login method.

<!--
<a href=""
target="_blank">
<img src=""
width="80%" alt="" title="">
</a>
-->

<!--
<a href="https://raw.githubusercontent.com/ktaka-ccmp/ktaka.blog.ccmp.jp/master/2024/HTMX-FasAPI-Sign-in-with-Google/"
target="_blank">
<img src="https://raw.githubusercontent.com/ktaka-ccmp/ktaka.blog.ccmp.jp/master/2024/HTMX-FasAPI-Sign-in-with-Google/"
width="80%" alt="" title="">
</a>
-->

<a href="https://raw.githubusercontent.com/ktaka-ccmp/ktaka.blog.ccmp.jp/master/2024/HTMX-FasAPI-Sign-in-with-Google/image/FastAPI-HTMX-Google-OAuth043.gif"
target="_blank">
<img src="https://raw.githubusercontent.com/ktaka-ccmp/ktaka.blog.ccmp.jp/master/2024/HTMX-FasAPI-Sign-in-with-Google/image/FastAPI-HTMX-Google-OAuth043.gif"
width="80%" alt="Sign-in Animation" title="Sign-in Animation">
</a>

The process begins when a user clicks on the Google logo.
A pop-up window appears, guiding them through the Google account selection and authentication process, which is then executed seamlessly in the background.

After logging in, the webpage dynamically updates the navigation bar to include the user's Google account icon.
Additionally, menu elements like 'Secret#1' become accessible, revealing exclusive content with a single click.

Logging out is just as intuitive.
Clicking the 'Exit' icon signs the user out, reverting the navigation bar to its default state for anonymous visitors.

The source code is on [my Github repo.](https://github.com/ktaka-ccmp/fastapi-htmx-google-oauth/tree/master)


## Anonymous User Page

The figure below shows a screenshot of anonymou user page to be explained more in detail.
The page consists of a navigation bar and content section.
On the navigation bar, anonymous user icon, menus including the ones to secret pages and Google Sign-in button are shown.
In this example Secret#1 menu is disabled. The Secret#2 menu is not disabled, however clicking it will return access forbiden error.

The section below the navigation bar is the content section showing "Incremental hx-get demo" page, which is acessible by both anonymous and authenticated user.

<a href="https://raw.githubusercontent.com/ktaka-ccmp/ktaka.blog.ccmp.jp/master/2024/HTMX-FasAPI-Sign-in-with-Google/image/page1.drawio.png"
target="_blank">
<img src="https://raw.githubusercontent.com/ktaka-ccmp/ktaka.blog.ccmp.jp/master/2024/HTMX-FasAPI-Sign-in-with-Google/image/page1.drawio.png"
width="90%" alt="Anonymous User Page" title="Anonymous User Page">
</a>


## Authenticated User Page

The figure below shows a screenshot of authenticated user page, which also consists of a navigation bar and content section.
 Shown on the navigation bar are the user's Google acount icon, menus including the ones to secret pages and Sign-out button.
When the user is authenticated, the menus to the secret pages are both acessible and both return the contents.

The section below the navigation bar is the content section showing the content of the secret#1 page which is acessible only by authenticated users.

<a href="https://raw.githubusercontent.com/ktaka-ccmp/ktaka.blog.ccmp.jp/master/2024/HTMX-FasAPI-Sign-in-with-Google/image/page2.drawio.png"
target="_blank">
<img src="https://raw.githubusercontent.com/ktaka-ccmp/ktaka.blog.ccmp.jp/master/2024/HTMX-FasAPI-Sign-in-with-Google/image/page2.drawio.png"
width="90%" alt="Authenticated User Page" title="Authenticated User Page">
</a>

# HTMX with FastAPI

FastAPI can respond with an HTML page that is generated from a Jinja template. The following code specifies that when the FastAPI server receives a get request to `/spa`, it will respond with a HTML page generated from a Jinja template `spa.j2`.

```python
router = APIRouter()
templates = Jinja2Templates(directory='templates')

@router.get("/spa", response_class=HTMLResponse)
async def spa(request: Request):
    context = {"request": request}
    return templates.TemplateResponse("spa.j2", context)
```

Shown below is what the `spa.j2` looks like.

```jinja
<!DOCTYPE html>
<html lang="en">

{% include 'head.j2' %}

<body>
  {# Header #}
  <header>
    <div id="auth_navbar" hx-get="/auth/auth_navbar" hx-target="#auth_navbar" hx-swap="innerHTML"
      hx-trigger="load, LoginStatusChange">
    </div>
  </header>

  {# Content #}
  <div class="container" id="content_section" hx-get="/htmx/content.top" hx-target="#content_section" hx-swap="innerHTML"
    hx-trigger="load">
  </div>

</body>

</html>
```

In the body section, there are two sub-sections, one is wrapped by `<header></header>` and the other is wrapped by `<div></div>`.

The section wrapped by `<header></header>` is to load the navigation bar in a responsive manner.
When we focus on this section, we find unfamiliar attributes, hx-get, hx-target, hx-swap and hx-trigger.
These are the attributes that are interpreted by HTMX JavaScript library loaded in `head.j2`.

The meaning of the attributes are summarized as follows:

| Attribut | Description |
|:---|:---|
| hx-get  | issues a GET request to the given URL  |
| hx-target  | specifies an element for swapping  |
| hx-swap | specifies how content is swapped |
| hx-trigger | specifies the event that triggers the request |

<a name="LoginStatusChange"></a>
So in this case, the HTMX library will issue a get request to `/auth/auth_navbar` endpoint upon this section's first load and when the page receives response with "HX-Trigger: LoginStatusChange" in header for a HTMX AJAX request.
The HTMX library will then replace the content inside the `<div>` section with `id="auth_navbar"`.

The `<div>` section just below the `{# Content #}` is to load the main contents of the page dynamically.
It also has the same set of HTMX attributes summarized in the table above.
In this case the HTMX library will issue a get request to `/htmx/content.top` endpoint only upon this section's first load.
The HTMX library will then replace the content inside the `<div>` section with `id="content_section"`.

To have the HTMX attribute properly interpreted, we need to add a `<script>` tag in the document head, like:

```
<head>
  <script defer src="https://unpkg.com/htmx.org@1.9.10"></script>
</head>
``` 

The document head is included from the file, `head.j2` in the same directory as:
```
{% include 'head.j2' %}
```

These are the examples of basic usage of HTMX and FastAPI with Jinja templating.

# Authentication Overview

The figure below shows a schematic diagram depicting the flow of the authentication process.

<a href="https://raw.githubusercontent.com/ktaka-ccmp/ktaka.blog.ccmp.jp/master/2024/HTMX-FasAPI-Sign-in-with-Google/image/htmx-fastapi01.drawio.png"
target="_blank">
<img src="https://raw.githubusercontent.com/ktaka-ccmp/ktaka.blog.ccmp.jp/master/2024/HTMX-FasAPI-Sign-in-with-Google/image/htmx-fastapi01.drawio.png"
width="80%" alt="Sign-in flow" title="Sign-in flow">
</a>

1. When a user clicks 'Sign-in with Google', an authentication request is sent to Google.
2. Upon successful authentication, the user's credentials are returned as a JSON Web Token (JWT) to the page.
3. JavaScript code on the page forwards the JWT to `/auth/login`, an authentication endpoint prepared using FastAPI.
4. The JWT is then verified using a certificate fetched from Google.
5. A user corresponding to the JWT is created in the SQLite database, if one does not already exist.
6. A new session is also created and stored in the database.
7. FastAPI sends a response with a header containing the entry "Set-Cookie: session_id=xxxxxx."

Thereafter, "Cookie: session_id=xxxxxx" is always set in subsequent communications, until the cookie expires or until the user explicitly hits the logout button on the web page.

# Frontend Auth

## Sign-in with Google button

To show a `Sign-in with Google button` we need to use a JavaScript library by Google, and place a code snipet somewhere in the HTML.

In order to load the JavaScript library, the likes of the following `<script>` tag need to be added in the document head.

```
<head>
  <script src="https://accounts.google.com/gsi/client" async></script>
</head>
```

The code snippet that should be placed in the page has two versions, one is a JavaScript version and the other is an HTML version.
We can use either of these.

Inside the navigation bar, we place a code for showing the "Sign-in with Google" button.
We can use either the HTML version or the JavaScript version of the code.

### JavaScript Version

```javascript
<script>
    google.accounts.id.initialize({
        client_id: "{{ client_id }}",
        callback: onSignIn,
        ux_mode: "popup",
    });

    google.accounts.id.renderButton(document.getElementById("signInDiv"), {
        theme: "outline",
        size: "large",
        shape: "circle",
        type: "icon",
    });

    {# google.accounts.id.prompt(); #}

</script>

<div id="signInDiv"></div>
```

The google.accounts.id.initialize functiondefines the initialization and behavior of the Sign-in process.

- The `client_id` defines [OAuth 2.0 Client ID](https://developers.google.com/identity/gsi/web/guides/get-google-api-clientid), which is necessary.
- The `callback` defines a JavaScript callback function upon a successful sign-in on the Google side.
- The`ux_mode` defines the mode of Google's sign-in page, which we want to be 'popup' instead of 'redirect'.

The `google.accounts.id.renderButton` division defines the presentation style of the Sign-in with Google button.

- The `data-auto_prompt="false` determines whether to display One tap or not.

The `google.accounts.id.prompt` method displays the One Tap prompt.

### HTML Version

```html
<script src="https://accounts.google.com/gsi/client" async></script>

<div id="g_id_onload"
     data-client_id="{{ client_id }}",
     data-context="signin"
     data-ux_mode="popup"
     data-callback=onSignIn
     data-close_on_tap_outside="true"
     data-itp_support="true"
     data-auto_prompt="false"
     >
</div>

<div class="g_id_signin"
     data-type="icon"
     data-shape="square"
     data-theme="outline"
     data-size="large"
     >
</div>
```

The `<div id="g_id_onload">` division defines the initialization and behavior of the Sign-in process.

- data-client_id="{{ client_id }}" defines [OAuth 2.0 Client ID](https://developers.google.com/identity/gsi/web/guides/get-google-api-clientid), which is necessary.

- The `data-ux_mode="popup"` defines the mode of Google's sign-in page, which we want to be 'popup' instead of 'redirect' which is more intrusive.
- The `data-callback=onSignIn` defines a JavaScript callback function upon a successful sign-in on the Google side.
- The `data-auto_prompt="false` determines whether to display One tap or not.

The `<div id="g_id_sigin">` division defines the presentation style of the Sign-in with Google button.

## The Callback Function

Here is an implementation of the callback function to forward the JWT to the backend. 

```javascript
<script>
    function onSignIn(response) {
        htmx.ajax('POST', '{{ login_url }}',
            { values: { 'credential': response.credential }, swap: 'none' })
    }
</script>
```

The `onSignIn` function sends JWT received from Google's sign-in page to the `{{ login_url }}`, which is a backend endpoint to handle the received JWT.

# Backend Auth

The backend endpoint receives the JWT, verifies it using Google's public certificate and then creates a session to maintain a logged-in status in the following communications.

Here is the code snippet of the backend endpoint, which does:

- VerifyToken: verify JWT,
- GetOrCreateUser: create the user in the database,
- create_session: create a session and store it in a session database,
- response.set_cookie: set the session_id in the cookie,
- then return the response to the front end.

```python
@router.post("/login")
async def login(request: Request, ds: Session = Depends(get_db), cs: Session = Depends(get_cache)):

    body = await request.body()
    jwt = dict(urllib.parse.parse_qsl(body.decode('utf-8'))).get('credential')

    idinfo = await VerifyToken(jwt)
    if not idinfo:
        print("Error: Failed to validate JWT token")
        return  Response("Error: Failed to validate JWT token")

    user = await GetOrCreateUser(idinfo, ds)
    if not user:
        print("Error: Failed to GetOrCreateUser")
        return  Response("Error: Failed to GetOrCreateUser for the JWT")

    session_id = create_session(user, cs)
    if not session_id:
        print("Error: Failed to create session for", user.name)
        return  Response("Error: Failed to create session for"+user.name)

    max_age = 600
    expires = datetime.now(timezone.utc) + timedelta(seconds=max_age)

    response = JSONResponse({"Authenticated_as": user.name})
    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        samesite="lax",
        max_age=max_age,
        expires=expires,
    )
    response.headers["HX-Trigger"] = "LoginStatusChange"

    return response
```

Please note that there is a line setting "HX-Trigger: LoginStatusChange" in the response header to trigger hx-get to `/auth/auth_navbar` causing a reload of navigation bar[(see above)](#LoginStatusChange).

The VerifyToken function below verifies the JWT from the frontend utilizing the [google oauth2 python library](https://google-auth.readthedocs.io/en/stable/reference/google.oauth2.id_token.html).

```python
from google.oauth2 import id_token
from google.auth.transport import requests

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
```

# Conclusion

In this post, I shared what I learnt to integrate `Sign-in with Google` feature with HTMX+FastAPI web application.
I only needed to put an HTML or JavaScript version of the code snippet from Google's code generator to show the button.
I implemented the FastAPI backend so that it creates a session and set a session_id in a cookie in the following communication.
The app. page shows the navigation bar to indicate the login status, fetched from the backend upon change of the login status utilizing hx-get, an HTMX method.


P.S.
I'm a resident of Japan looking for remote Job overseas.
I'm also willing to take on-site position in North America, AU, EU, etc., if there's VISA support.