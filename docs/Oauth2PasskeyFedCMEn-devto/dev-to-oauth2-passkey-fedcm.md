---
title: "Implementing FedCM Login: Browser-Native Authentication Without Popups"
published: true
description: "Implementation record of FedCM login in the oauth2-passkey Rust library: using the browser standard API, reusing JWT validation, and security trade-offs."
tags: rust, webauthn, authentication, fedcm
canonical_url: https://ktaka.blog.ccmp.jp/en/2026/Oauth2PasskeyFedCM
---

FedCM (Federated Credential Management) is a W3C standard API that enables federated authentication through browser-native UI. Instead of popup windows or redirects, the browser itself displays an account chooser and communicates directly with the identity provider.

This article explains how I implemented FedCM in the [oauth2-passkey](https://github.com/ktaka-ccmp/oauth2-passkey) Rust library, how it differs from the traditional OAuth2 flow, and the security trade-offs involved.

---

## What is FedCM?

In the traditional OAuth2 Authorization Code Flow, the RP (your app) redirects to Google's page, and after authentication, returns to a callback URL. With FedCM, you simply call `navigator.credentials.get()`, the browser communicates directly with Google, and returns a JWT ID token.

```text
Traditional OAuth2 Authorization Code Flow:
  Button click -> Popup -> Google auth page
    -> Redirect (with authorization code)
    -> Backend exchanges code with Google (server-to-server)
    -> Obtain ID token -> Validate -> Establish session

FedCM:
  Button click -> navigator.credentials.get()
    -> Browser displays native UI account chooser
    -> Browser obtains JWT ID token directly from Google
    -> JS posts token to backend -> Validate -> Establish session
```

With FedCM, the browser acts as an intermediary, so JavaScript loaded from the RP cannot see the list of accounts. The browser uses Google's session cookies to display account information in the native UI, and only returns the user's selected result to JavaScript.

## UI Comparison

![Image description](IMAGE_URL: fedcm-account-chooser.png)
*FedCM account chooser (browser displays native UI)*

![Image description](IMAGE_URL: oauth2-popup.png)
*Traditional OAuth2 Authorization Code Flow (displays Google auth page in popup window)*

## Frontend Implementation

The FedCM frontend implementation consists of three steps.

### 1. Obtaining a Nonce

```javascript
const nonceResponse = await fetch('/api/fedcm/nonce');
const nonceData = await nonceResponse.json();
// { nonce: "random string", nonce_id: "cache key" }
```

### 2. Calling navigator.credentials.get()

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
    mediation: 'required',  // Prevent auto re-authn, always require user interaction
});
```

It's important that `mode: 'active'` is placed directly under the `identity` object. If placed inside the provider object, Chrome ignores it and operates in passive mode, causing a cooldown when the user closes the dialog.

### 3. Sending the Token to the Backend

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
    // Login successful, session cookie set via Set-Cookie header
    window.location.reload();
}
```

## Backend Implementation

The backend processing consists of five steps.

### 1. JWT Validation (signature, iss/aud/exp, nonce)

```rust
fn validate_fedcm_token(token: String, nonce_id: String) -> IdInfo {
    // JWT signature validation, aud/iss/exp validation
    let idinfo = verify_idtoken(token, CLIENT_ID);

    // Nonce validation (ensures single use)
    verify_and_consume_nonce(nonce_id, idinfo.nonce);

    idinfo
}
```

JWT validation verifies the following:
- **Signature verification**: Fetch Google's JWKS (public key set), select the key using the `kid` in the JWT header, and verify the signature
- **Claim validation**: Verify that `iss` (issuer), `aud` (Client ID), and `exp` (expiration) are correct
- **Nonce validation**: Verify that the `nonce` claim in the ID token matches the pre-generated value, then delete it from the cache after verification to prevent reuse

The JWT returned by Google's FedCM endpoint is in the same format as the ID token obtained through the Authorization Code Flow. This means existing OAuth2 authentication JWT validation code can be reused as-is.

### 2-5. User Info Extraction, Account Lookup/Creation, Session Creation, Set-Cookie Response

These steps are common with the traditional OAuth2 flow. See the [full article](https://ktaka.blog.ccmp.jp/en/2026/Oauth2PasskeyFedCM) for details.

## Security Considerations

FedCM brings UX improvements, but its security model differs from the traditional OAuth2/OIDC flow.

| Aspect | Authorization Code Flow + PKCE | FedCM |
|------|------|------|
| ID token acquisition | Server exchanges authorization code | Browser obtains directly |
| JavaScript-accessible information | Authorization code (worthless) | JWT ID token (usable for authentication) |
| XSS attack risk | Authorization code alone cannot authenticate | Usable for authentication within validity period |

In my understanding, OAuth2 + PKCE has higher resistance to XSS attacks. Note that Google's One Tap (GIS SDK) also adopts the same model as FedCM.

## Browser Support

| Browser | Support |
|---------|---------|
| Chrome 108+ | Supported |
| Edge 108+ | Supported |
| Safari | Not supported (falls back to popup) |
| Firefox | Not supported (falls back to popup) |

## Summary

What became clear through implementing FedCM:

- The FedCM frontend is a 3-step process: nonce acquisition → `navigator.credentials.get()` → POST to backend
- The backend follows: JWT validation → user info extraction → user search/creation → session creation → Set-Cookie. Existing JWT validation code can be reused as-is
- The security model differs from the Authorization Code Flow; OAuth2 + PKCE has higher resistance to XSS attacks. FedCM is a trade-off that prioritizes UX improvement
- Parameters for `navigator.credentials.get()` have Google-specific requirements, and correct notation such as `mode: 'active'` placement is crucial

See [oauth2-passkey](https://github.com/ktaka-ccmp/oauth2-passkey) for implementation examples. Try the actual behavior at the [demo site](https://passkey-demo.ccmp.jp).

## Links

- **Full article**: [ktaka.blog.ccmp.jp/en/2026/Oauth2PasskeyFedCM](https://ktaka.blog.ccmp.jp/en/2026/Oauth2PasskeyFedCM)
- **Live demo**: [passkey-demo.ccmp.jp](https://passkey-demo.ccmp.jp)
- **GitHub**: [ktaka-ccmp/oauth2-passkey](https://github.com/ktaka-ccmp/oauth2-passkey)
- **Documentation**: [ktaka-ccmp.github.io/oauth2-passkey](https://ktaka-ccmp.github.io/oauth2-passkey/)

## References

- [FedCM W3C Spec](https://www.w3.org/TR/fedcm/)
- [MDN: FedCM API](https://developer.mozilla.org/en-US/docs/Web/API/FedCM_API)
- [Chrome: RP Implementation Guide](https://developer.chrome.com/docs/identity/fedcm/implement/relying-party)
- [Google: FedCM Migration Guide](https://developers.google.com/identity/gsi/web/guides/fedcm-migration)
