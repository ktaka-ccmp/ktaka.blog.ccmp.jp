+++
title = "Try Passwordless Auth: oauth2-passkey Live Demo"
date = 2026-03-01
description = "Introducing oauth2-passkey, a Rust library for passwordless authentication with OAuth2 and Passkeys. Try the live demo at passkey-demo.ccmp.jp."
path = "2026/Oauth2PasskeyDemo"
+++

*A live demo of [oauth2-passkey](https://github.com/ktaka-ccmp/oauth2-passkey), a Rust library that adds OAuth2 + Passkey authentication to your web app with minimal code.*

---

## Live Demo

Try it now: **[passkey-demo.ccmp.jp](https://passkey-demo.ccmp.jp)**

You can:

1. **Sign in with Google** (OAuth2)
2. **Register a Passkey** (fingerprint, Face ID, Windows Hello, etc.)
3. **Sign in with Passkey** next time -- no password, no redirect
4. **Explore the admin panel** (all demo users get admin access)
5. **View login history** with device and authenticator details

Data is stored in memory and resets on server restart, so feel free to experiment.

## What is oauth2-passkey?

[oauth2-passkey](https://crates.io/crates/oauth2-passkey) is a Rust library for adding passwordless authentication to web applications. It combines:

- **OAuth2 (Google)** -- One-click registration and login, familiar to users
- **Passkeys (WebAuthn/FIDO2)** -- Phishing-resistant, biometric login (fingerprint, face, security key)

Users sign up with Google, then optionally add a Passkey for faster daily login. OAuth2 stays as a backup if the device is lost.

## Quick Start

Add oauth2-passkey to your Axum app:

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

The `oauth2_passkey_full_router()` call adds all authentication routes under `/o2p/*`: login page, OAuth2 flow, Passkey registration/authentication, user account management, and admin panel.

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
| **Storage** | SQLite (dev) or PostgreSQL (prod), with Redis or in-memory cache |

## Links

- **Live demo**: [passkey-demo.ccmp.jp](https://passkey-demo.ccmp.jp)
- **GitHub**: [ktaka-ccmp/oauth2-passkey](https://github.com/ktaka-ccmp/oauth2-passkey)
- **crates.io**: [oauth2-passkey](https://crates.io/crates/oauth2-passkey) / [oauth2-passkey-axum](https://crates.io/crates/oauth2-passkey-axum)
- **Documentation**: [ktaka-ccmp.github.io/oauth2-passkey](https://ktaka-ccmp.github.io/oauth2-passkey/)

## Background

This library grew out of a [from-scratch Passkey implementation](/2025/01/implementing-passkeys-authentication-in-rust-axum.html) I wrote in early 2025. That project taught me the WebAuthn protocol deeply, and I decided to package the result into a reusable library with OAuth2 integration, session management, and a complete UI.

More detailed articles about the library architecture, Cloud Run deployment, and async Rust pitfalls encountered along the way are coming soon.
