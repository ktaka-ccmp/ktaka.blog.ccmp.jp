# Sign in with Google in HTMX+FastAPI

- [Sign in with Google in HTMX+FastAPI](#sign-in-with-google-in-htmxfastapi)
  - [TLDR](#tldr)
  - [Introduction](#introduction)
  - [The resulting page](#the-resulting-page)
  - [Overview of the Implementation](#overview-of-the-implementation)
  - [HTMX with FastAPI](#htmx-with-fastapi)
    - [The navigation bar](#the-navigation-bar)
  - [Show Sign-in with Google button](#show-sign-in-with-google-button)
    - [JavaScript version of the Sign-in component](#javascript-version-of-the-sign-in-component)
    - [HTML version of the Sign-in component](#html-version-of-the-sign-in-component)
    - [The Callback function](#the-callback-function)
  - [Backend endpoint for login](#backend-endpoint-for-login)
    - [BBBB](#bbbb)
  - [Conclusion](#conclusion)

## TLDR

I integrated the "Sign in with Google" button with a sample HTMX+FastAPI web application.
I only needed to put an HTML or JavaScript version of the code snippet from Google's code generator to show the button.
I implemented the FastAPI backend so that it creates a session and set a session_id in a cookie in the following communication.
The app. page shows the navigation bar to indicate the login status, fetched from the backend depending on the login status change, utilizing hx-get, an HTMX method.

## Introduction

As an aspiring full-stack software developer, I've been teaching myself various front-end web technologies recently.
These include React.js, Svelte, and other shiny new JavaScript frameworks, which can sometimes be overwhelming.
I was considering settling on Svelte, thanks to its simplicity in state management, when I discovered a concept called Hypermedia as the Engine of Application State (HATEOAS) and a library named htmx.js.

Initially, I didn't quite grasp how it differed from other technologies.
However, after creating several web pages for practice, I realized I didn't need to switch into a dedicated front-end programming mode.
I felt liberated from the struggle of forcing myself into the React mindset, which always seemed nonsensical to me.
I often questioned, 'Why must I change my mindset every time I create a small piece of a web page?'

With htmx.js, I can simply create a page, and when I need to change parts of it, I just fire an AJAX request using hx-get and swap the DOM elements with HTML fragments in the response.
I understand that as a web application becomes more complex, there might be situations where more feature-rich technologies are necessary.
But now, I'm no longer intimidated by the overwhelming ecosystems of each technology.

Now, I want to know how I can implement the login feature in a web application.
Especially, I wanted to know how to use the Sign-in with Google feature on a Web page crafted using HTMX+FastAPI.
So, I did some research and figured out how to do it.
Since there seems to be a lack of use cases on the web, targeted using it with HTMX, I decided to share what I did.

Although integrating the Sign-in with Google button in an HTMX page is nothing special than incorporating it into a normal HTML page, how to show the status after successful login or logout using the HTMX, and how to maintain a session via cookie generated upon successful verification of the JWT instead of solely relying on JWT for keeping session seemed worthwhile noting, especially for a beginner like me.

Now, I wanted to explore how I could implement a login feature in a web application, specifically using the 'Sign-in with Google' feature on a web page developed with HTMX and FastAPI.
After conducting some research, I figured out how to do it.
Noticing a lack of use cases on the web for this particular combination of technologies, I decided to share my findings.

While integrating the 'Sign-in with Google' button into an HTMX page isn’t much different from incorporating it into a standard HTML page, understanding how to display the status after a successful login or logout using HTMX, and how to maintain a session via a cookie generated upon successful JWT verification—rather than solely relying on the JWT for session management—seemed noteworthy. 
This is particularly true for beginners like myself.

## The resulting page

Put Gif animation here.

## Overview of the Implementation

Create a figure to show OAuth2 flow and session creation.

## HTMX with FastAPI

FastAPI can respond with an HTML page that is generated from a Jinja template.

```python
router = APIRouter()
templates = Jinja2Templates(directory='templates')

@router.get("/spa", response_class=HTMLResponse)
async def spa(request: Request):
    context = {"request": request}
    return templates.TemplateResponse("spa.j2", context)
```

By specifing `response_class=HTMLResponse` and letting the function return `TemplateResponse`, we can make the FastAPI respond with the HTML page below.

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


The section below the `{# Header #}` gets the navigation bar component from the `/auth/auth_navbar` endpoint via AJAX request.
The obtained HTML fraction replaces the content within the `<div id="auth_navbar"></div>` element.
The AJAX request is fired upon the initial load of the page and when the browser gets "Hx-Trigger:
LoginStatusChange" in the response header.

The section below the `{# Content #}` gets the content of the page from the `/htmx/content.top` endpoint via AJAX request.
The obtained HTML fraction replaces the content within the `<div id="content_section"></div>` element.
The AJAX request is fired upon the initial load of the page.


Here the interesting part is that we included htmx attributes, hx-get, hx-target, hx-swap and hx-triggers to fire an AJAX request and swap content of elements with the obtained response.

Those attributes are interpreted and executed by htmx, which is JavaScript library, 

Download htmx.min.js from unpkg.com and add it to the appropriate directory in your project and include it where necessary with a `<script>` tag:

```
<script src="/path/to/htmx.min.js"></script>
```

The meaning of the attributes are summarized as follows:

| Attribut	| Description |
|:---|:---|
| hx-get  | issues a GET request to the given URL  |
| hx-target  | specifies an element for swapping  |
| hx-swap | specifies how content is swapped |
| hx-trigger | specifies the event that triggers the request |

### The navigation bar

## Show Sign-in with Google button

Inside the navigation bar, we place a code for showing the "Sign-in with Google" button.
We can use either the HTML version or the JavaScript version of the code.

### JavaScript version of the Sign-in component

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

- The `client_id`` defines [OAuth 2.0 Client ID](https://developers.google.com/identity/gsi/web/guides/get-google-api-clientid), which is necessary.
- The `callback` defines a JavaScript callback function upon a successful sign-in on the Google side.
- The`ux_mode` defines the mode of Google's sign-in page, which we want to be 'popup' instead of 'redirect'.

The `google.accounts.id.renderButton` division defines the presentation style of the Sign-in with Google button.

- The `data-auto_prompt="false` determines whether to display One tap or not. 

The `google.accounts.id.prompt` method displays the One Tap prompt. 

### HTML version of the Sign-in component

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

### The Callback function

Here is an implementation of the callback function, which should be called upon a successful sign-in on the Google side.

```javascript
<script>
    function onSignIn(response) {
        var xhr = new XMLHttpRequest();
        xhr.open('POST', "{{ login_url }}");
        xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
        xhr.onload = function () {
            console.log("Response from {{ login_url }}: ", xhr.responseText);
            htmx.trigger("#auth_navbar", "LoginStatusChange");
        };
        xhr.send('credential=' + response.credential);
    }
</script>
```

The `onSignIn` function sends JWT received from Google's sign-in page to the `{{ login_url }}`, which is a backend endpoint to handle the received JWT.
The `onSignIn` function also triggers

## Backend endpoint for login

The backend endpoint receives the JWT, verifies it using Google's public certificate and then creates a session to maintain a logged-in status in the following communications.

Here is the code snippet of the backend endpoint, which does:

- verify JWT,
- create the user in the database,
- create a session(, and store it in a session database),
- set the session_id in the cookie,
- then return the response to the front end.

```javascript
@router.post("/login")
async def login(request: Request, ds: Session = Depends(get_db), cs: Session = Depends(get_cache)):

    body = await request.body()
    jwt = dict(urllib.parse.parse_qsl(body.decode('utf-8'))).get('credential')

    idinfo = await VerifyToken(jwt)
    if not idinfo:
        print("Error: Failed to validate JWT token")
        return  Response("Error: Failed to validate JWT token")

    user = await GetOrCreateUser(idinfo, ds)

    if user:
        user_dict = get_user_by_email(user.email, ds)
        if not user_dict:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error: User not exist in User table in DB."
                )
        user = UserBase(**user_dict)
        session_id = create_session(user, cs)

        response = JSONResponse({"Authenticated_as": user.name})
        max_age = 600
        expires = datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age)
        response.set_cookie(
            key="session_id",
            value=session_id,
            httponly=True,
            samesite="lax",
            max_age=max_age,
            expires=expires,
        )

        return response
    else:
        return Response("Error: Auth failed")
```

The VerifyToken function below verifies the JWT from the frontend utilizing the [google oauth2 python library](https://google-auth.readthedocs.io/en/stable/reference/google.oauth2.html).

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

### BBBB

BBB

## Conclusion

To be written later.
