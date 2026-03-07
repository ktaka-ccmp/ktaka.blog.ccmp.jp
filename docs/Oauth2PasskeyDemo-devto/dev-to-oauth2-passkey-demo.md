---
title: "Try Passwordless Auth: oauth2-passkey Live Demo"
published: true
description: "Introducing oauth2-passkey, a Rust library for passwordless authentication with OAuth2 and Passkeys. Try the live demo at passkey-demo.ccmp.jp."
tags: rust, webauthn, authentication, passkeys
canonical_url: https://ktaka.blog.ccmp.jp/en/2026/Oauth2PasskeyDemo
---

*A live demo of [oauth2-passkey](https://github.com/ktaka-ccmp/oauth2-passkey), a Rust library that adds OAuth2 and Passkey authentication to your web app with minimal code.*

Two short videos below walk through the demo at [passkey-demo.ccmp.jp](https://passkey-demo.ccmp.jp) — first registering via Google and adding a Passkey, then signing in using only the Passkey.

---

## Demo 1: Register with Google and Add a Passkey

![Image description](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/iwbedbkv5fnodagp9jzu.gif)

Here's what happens in the video:

1. The **login page** offers two options: "Register / Sign in with Google" and "Sign in with Passkey".
2. Clicking **"Register / Sign in with Google"** opens the standard Google account chooser and consent screen.
3. Immediately after Google authentication, the app prompts: **"Create a passkey to sign in?"** — this is the *Passkey promotion* feature, encouraging OAuth2 users to register a Passkey for faster future logins.
4. After creating the Passkey, the user lands on the **Dashboard** with links to My Account and Admin Panel.
5. The **My Account** page shows User Information, Passkey Credentials, linked OAuth2 Accounts, and Recent Login History.

The key idea: users start with the familiarity of Google sign-in, then immediately gain the speed and security of Passkeys.

## Demo 2: Sign in with Passkey

![Image description](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/n7qn8ivp9puil7qcs8or.gif)

Now the same user signs in again, this time with their Passkey:

1. On the **login page**, clicking **"Sign in with Passkey"** triggers the browser's built-in Passkey dialog.
2. After biometric verification (fingerprint, face, etc.), the user is **logged in instantly** — no redirect to Google, no password.
3. The **Login History** now shows both the Passkey login and the earlier OAuth2 login, so users can review their full authentication history.

This is the daily login experience: fast, phishing-resistant, and free of external dependencies once the Passkey is registered.

## Try It Yourself

Try it now: **[passkey-demo.ccmp.jp](https://passkey-demo.ccmp.jp)**

- Sign in with Google, register a Passkey, then sign in with just the Passkey
- Explore the admin panel (all demo users get admin access)
- View login history with device and authenticator details

Data is stored in memory and resets on server restart, so feel free to experiment.

## What is oauth2-passkey?

[oauth2-passkey](https://crates.io/crates/oauth2-passkey) is a Rust library for adding passwordless authentication to web applications. It combines:

- **OAuth2 (Google)** — One-click registration and login, familiar to users
- **Passkeys (WebAuthn/FIDO2)** — Phishing-resistant, biometric login (fingerprint, face, security key)

Users sign up with Google, then optionally add a Passkey for faster daily logins. OAuth2 remains available as a fallback if a device is lost.

## Quick Start

Add oauth2-passkey to your Axum application:

```rust
use axum::{Router, routing::get, response::IntoResponse};
use oauth2_passkey_axum::{AuthUser, oauth2_passkey_full_router};

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    oauth2_passkey_axum::init().await?;

    let app = Router::new()
        .route("/", get(home))
        .route("/protected", get(protected))
        .merge(oauth2_passkey_full_router());

    let listener = tokio::net::TcpListener::bind("0.0.0.0:3001").await?;
    axum::serve(listener, app).await?;
    Ok(())
}

async fn home() -> &'static str {
    "Welcome! Visit /o2p/user/login to sign in"
}

async fn protected(user: AuthUser) -> impl IntoResponse {
    format!("Hello, {}!", user.account)
}
```

The `oauth2_passkey_full_router()` call adds all authentication routes under `/o2p/*`, including the login page, OAuth2 flow, Passkey registration and authentication, user account management, and the admin panel.

Set a few environment variables (Google OAuth2 credentials, session secret) and you're ready to go. See the [Getting Started guide](https://ktaka-ccmp.github.io/oauth2-passkey/) for details.

## Features

| Feature | Description |
|---------|-------------|
| **Dual auth** | OAuth2 (Google) + Passkeys in one library |
| **Built-in UI** | Login page, user account, admin panel |
| **Passkey promotion** | Prompts OAuth2 users to register a Passkey |
| **Login history** | Records IP, User-Agent, authenticator details |
| **Session management** | Secure cookies, conflict policies, force logout |
| **Admin panel** | User management, audit trail, admin safeguards |
| **Theme system** | 9 built-in CSS themes + custom theme support |
| **Storage** | SQLite (development) or PostgreSQL (production), with Redis or in-memory caching |

## Links

- **Live demo**: [passkey-demo.ccmp.jp](https://passkey-demo.ccmp.jp)
- **GitHub**: [ktaka-ccmp/oauth2-passkey](https://github.com/ktaka-ccmp/oauth2-passkey)
- **crates.io**: [oauth2-passkey](https://crates.io/crates/oauth2-passkey) / [oauth2-passkey-axum](https://crates.io/crates/oauth2-passkey-axum)
- **Documentation**: [ktaka-ccmp.github.io/oauth2-passkey](https://ktaka-ccmp.github.io/oauth2-passkey/)

## Background

This library grew out of a [from-scratch Passkey implementation](https://ktaka.blog.ccmp.jp/2025/01/implementing-passkeys-authentication-in-rust-axum.html) I wrote in early 2025. That project gave me a deep understanding of the WebAuthn protocol, and I decided to package the result into a reusable library with OAuth2 integration, session management, and a complete UI.
