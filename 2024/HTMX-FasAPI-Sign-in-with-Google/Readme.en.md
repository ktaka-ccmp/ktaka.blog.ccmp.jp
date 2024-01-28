
# Sign in with Google in HTMX+FastAPI

## TLDR

I integrated the "Sign in with Google" button with a sample HTMX+FastAPI web application.
I only needed to put an HTML or JavaScript version of the code snippet from Google's code generator to show the button.
I implemented the FastAPI backend so that it creates a session and set a session_id in a cookie in the following communication.
The app. page shows the navigation bar to indicate the login status, fetched from the backend depending on the login status change, utilizing hx-get, an HTMX method.

## Introduction

I wanted to know how to use the Sign-in with Google feature on a Web page crafted using HTMX+FastAPI.
As for the Sign-in with Google feature itself, it turned out that nothing is HTMX specific but also applies to normal HTML pages with FastAPI.

## HTMX with FastAPI

FastAPI can respond with an HTMX page that is generated from a template.

```python
router = APIRouter()
templates = Jinja2Templates(directory='templates')

@router.get("/spa", response_class=HTMLResponse)
async def spa(request: Request):
    context = {"request": request}
    return templates.TemplateResponse("spa.j2", context)
```

To make the FastAPI return an HTML page, we need to specify `response_class=HTMLResponse` and let the function return `TemplateResponse.`

Here is the template used in the example above.

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

The `{# Header #}` section gets the navigation bar component from the `/auth/auth_navbar` endpoint via AJAX request.
The obtained HTML fraction is placed between `<div id="auth_navbar">` and `</div>.`
The AJAX request is fired upon the initial load of the page or when the browser gets "Hx-Trigger:
showComponent" in the response header.

The `{# Content #}` section gets the content of the page from the `/htmx/content.top` endpoint via AJAX request.
The obtained HTML fraction is placed between `<div id="content_section">` and `</div>.`
The AJAX request is fired upon the initial load of the page.

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
        response.set_cookie(
            key="session_id",
            value=session_id,
            httponly=True,
            max_age=600,
            expires=600,
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

# Conclusion

To be written later.
