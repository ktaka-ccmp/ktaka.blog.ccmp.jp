# Implementing WebAuthn Passkeys in Rust with Axum

As a developer learning web programming and authentication in Rust, I recently undertook the challenge of implementing WebAuthn Passkeys using the Axum web framework. In this post, I'll share my experience building a basic Passkey authentication system from scratch, without relying on full-featured WebAuthn library crates.

## Understanding WebAuthn and Passkeys

WebAuthn is a W3C standard for passwordless authentication that uses public-key cryptography. The private keys are stored securely on user devices while public keys remain on servers. WebAuthn supports both platform authenticators (like Windows Hello or Touch ID) and roaming authenticators (like security keys).

Passkeys extend WebAuthn by adding seamless account recovery through cloud-synced credentials. They integrate with platform authenticators like Google Password Manager or Apple Keychain, enabling users to authenticate using biometrics or PINs across their devices. This implementation is built on the FIDO2 protocol, which standardizes the authentication flow and user interface.

## The Authentication Flow

WebAuthn authentication involves two main phases: registration and authentication. Let's examine how each phase works and then implement them.

### Registration Flow

During registration, the server first generates a cryptographic challenge and sends it to the client along with registration options. The client then requests its authenticator to create a new key pair and generate an attestation object containing the public key. This attestation object is sent back to the server, which verifies it and stores the public key for future authentication.

```mermaid
sequenceDiagram
    participant C as Client
    participant A as Authenticator
    participant S as Server

    C->>S: POST /register/start (username)
    Note over S: Generate challenge
    Note over S: Create registration options
    S->>C: Return options (challenge, rpId, user info)
    
    C->>A: navigator.credentials.create()
    Note over A: Generate key pair
    Note over A: Sign challenge with private key
    Note over A: Create attestation
    A->>C: Return credential + attestation
    
    C->>S: POST /register/finish
    Note over S: Verify client data
    Note over S: Verify attestation
    Note over S: Extract public key
    Note over S: Store credential
    S->>C: Registration success
```

The attestation object returned by the authenticator contains authenticator data (including the new public key) and an attestation statement that provides information about the authenticator itself. This allows the server to verify the authenticator's authenticity and securely obtain the user's public key.

### Authentication Flow

The authentication process begins with the server generating a new challenge. The authenticator then signs this challenge using the user's private key, and the server verifies the signature using the stored public key.

```mermaid
sequenceDiagram
    participant C as Client
    participant A as Authenticator
    participant S as Server

    C->>S: POST /auth/start
    Note over S: Generate challenge
    Note over S: Get allowed credentials
    S->>C: Return options (challenge, rpId, allowCredentials)
    
    C->>A: navigator.credentials.get()
    Note over A: User verification (if required)
    Note over A: Sign challenge with private key
    A->>C: Return authenticator assertion
    
    C->>S: POST /auth/verify
    Note over S: Verify client data
    Note over S: Verify authenticator data
    Note over S: Verify signature
    S->>C: Authentication success
```

## Client-Side Implementation

Let's examine how to implement the client-side WebAuthn interactions using JavaScript.

### Registration Implementation

The registration process starts by requesting registration options from the server:

```javascript
const response = await fetch('/register/start', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(username)
});
const options = await response.json();
```

The server responds with registration options that include several crucial parameters:

```json
{
    "challenge": "base64url-encoded-random-bytes",
    "rp_id": "example.com",
    "rp": {
        "name": "Example Service",
        "id": "example.com"
    },
    "user": {
        "id": "user-uuid",
        "name": "username",
        "displayName": "display name"
    },
    "pubKeyCredParams": [
        { "type": "public-key", "alg": -7 },  // ES256
        { "type": "public-key", "alg": -257 } // RS256
    ],
    "authenticatorSelection": {
        "authenticatorAttachment": "platform",
        "residentKey": "required",
        "userVerification": "discouraged"
    },
    "timeout": 60000
}
```

The registration options contain several security-critical parameters:

The challenge is a cryptographically random value generated for each registration attempt. It prevents replay attacks by ensuring the authenticator's response is fresh and specifically generated for this registration.

The rp_id (Relying Party ID) binds the credential to your domain, making the credential unusable on other domains and preventing phishing attacks.

The user.id provides a stable identifier for linking credentials to users, particularly important for discoverable credentials (resident keys) that persist across sessions.

The authenticatorSelection parameters control the authenticator's behavior:
- authenticatorAttachment specifies whether to use platform or cross-platform authenticators
- residentKey determines if the credential should be discoverable without server input
- userVerification controls whether biometric/PIN verification is required

Next, we create credentials using these options:

```javascript
const credential = await navigator.credentials.create({
    publicKey: {
        challenge: base64URLToBuffer(options.challenge),
        rp: {
            name: options.rp.name,
            id: options.rp_id
        },
        user: {
            id: base64URLToBuffer(options.user.id),
            name: options.user.name,
            displayName: options.user.displayName
        },
        pubKeyCredParams: options.pub_key_cred_params,
        authenticatorSelection: options.authenticator_selection,
        timeout: options.timeout
    }
});
```

This code creates a new key pair in the authenticator and returns an attestation object containing the public key. The private key never leaves the authenticator, ensuring security.

Finally, we send the attestation object and related data to the server:

```javascript
await fetch('/register/finish', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        id: credential.id,
        rawId: bufferToBase64URL(credential.rawId),
        response: {
            clientDataJSON: bufferToBase64URL(credential.response.clientDataJSON),
            attestationObject: bufferToBase64URL(credential.response.attestationObject)
        },
        type: credential.type,
        user_handle: options.user.id,
    })
});
```

The user_handle is included explicitly to maintain the connection between the credential and the user account, as the attestation itself doesn't contain user identification.

### Authentication Implementation

The authentication process follows a similar pattern. First, we request authentication options:

```javascript
const response = await fetch('/auth/start', {
    method: 'POST'
});
const options = await response.json();
```

The server provides authentication options:

```json
{
    "challenge": "base64url-encoded-random-bytes",
    "timeout": 60000,
    "rp_id": "example.com",
    "allow_credentials": [
        {
            "type": "public-key",
            "id": "base64url-encoded-credential-id"
        }
    ],
    "user_verification": "discouraged",
    "auth_id": "unique-auth-session-id"
}
```

We then request the authenticator to sign the challenge:

```javascript
const assertion = await navigator.credentials.get({
    publicKey: {
        challenge: base64URLToBuffer(options.challenge),
        rpId: options.rp_id,
        allowCredentials: options.allow_credentials.map(cred => ({
            id: base64URLToBuffer(cred.id),
            type: cred.type
        })),
        userVerification: options.user_verification,
        timeout: options.timeout
    }
});
```

If allow_credentials is empty, the authenticator will prompt the user to choose from available discoverable keys.

Finally, we send the signed assertion to the server:

```javascript
await fetch('/auth/verify', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        id: assertion.id,
        rawId: bufferToBase64URL(assertion.rawId),
        response: {
            authenticatorData: bufferToBase64URL(assertion.response.authenticatorData),
            clientDataJSON: bufferToBase64URL(assertion.response.clientDataJSON),
            signature: bufferToBase64URL(assertion.response.signature),
            userHandle: bufferToBase64URL(assertion.response.userHandle)
        },
        type: assertion.type
    })
});
```

## Server Implementation in Rust

The server implementation uses Axum and is organized into several modules for clarity:

```
src/
├── main.rs              # Server setup and routing
├── passkey.rs           # Module definitions
└── passkey/
    ├── attestation.rs   # Attestation verification
    ├── auth.rs          # Authentication handling
    └── register.rs      # Registration handling
```

### State Management

The server maintains state using a shared AppState structure:

```rust
#[derive(Clone)]
pub(crate) struct AppState {
    store: Arc<Mutex<AuthStore>>,
    rng: Arc<rand::SystemRandom>,
    config: AppConfig,
}

#[derive(Default)]
struct AuthStore {
    challenges: HashMap<String, StoredChallenge>,
    credentials: HashMap<String, StoredCredential>,
}

#[derive(Clone)]
struct AppConfig {
    origin: String,
    rp_id: String,
    authenticator_selection: AuthenticatorSelection,
}
```

In a production environment, you would replace the HashMaps with proper database storage, using key-value stores for temporary data like challenges and SQL databases for permanent data like credentials.

### Registration Handler Implementation

The registration process consists of two main functions. The start_registration function generates and stores necessary registration data:

```rust
async fn start_registration(
    State(state): State<AppState>,
    Json(username): Json<String>,
) -> Json<RegistrationOptions> {
    // Generate challenge and create user info
    let mut challenge = vec![0u8; 32];
    state.rng.fill(&mut challenge).unwrap();

    let user_info = PublicKeyCredentialUserEntity {
        id: Uuid::new_v4().to_string(),
        name: username.clone(),
        display_name: username.clone(),
    };

    // Store challenge for verification
    let stored_challenge = StoredChallenge {
        challenge: challenge.clone(),
        user: user_info.clone(),
        timestamp: SystemTime::now()...
    };
    
    let mut store = state.store.lock().await;
    store
        .challenges
        .insert(user_info.id.clone(), stored_challenge);

    // Return registration options
    Json(RegistrationOptions {
        challenge: URL_SAFE.encode(&challenge),
        rp_id: state.config.rp_id.clone(),
        // ...other options
    })
}
```

The finish_registration function handles credential verification and storage:

```rust
async fn finish_registration(
    State(state): State<AppState>,
    Json(reg_data): Json<RegisterCredential>,
) -> Result<&'static str, (StatusCode, String)> {
    let mut store = state.store.lock().await;

    // Verify the challenge and client data
    verify_client_data(&state, &reg_data, &store).await?;

    // Extract the public key from attestation
    let public_key = extract_credential_public_key(&reg_data, &state)?;

    // Store credential with user info
    let credential_id = base64url_decode(&reg_data.raw_id)?;
    let stored_user = store.challenges.get(&reg_data.user_handle)?.user.clone();

    store.credentials.insert(
        reg_data.raw_id.clone(),
        StoredCredential {
            credential_id,
            public_key,
            counter: 0,
            user: stored_user,
        },
    );

    // Remove used challenge
    store.challenges.remove(&reg_data.user_handle);

    Ok("Registration successful")
}
```

This function performs several critical security checks:
1. Verifies that the client data matches expectations (challenge, origin, operation type)
2. Extracts and verifies the public key from the attestation object
3. Stores the credential with associated user information
4. Removes the used challenge to prevent replay attacks

### Authentication Handler Implementation

The authentication process also uses two main functions. The start_authentication function initiates the process:

```rust
async fn start_authentication(
    State(state): State<AppState>
) -> Json<AuthenticationOptions> {
    // Generate new challenge
    let mut challenge = vec![0u8; 32];
    state.rng.fill(&mut challenge).unwrap();

    // Create auth ID for this session
    let auth_id = Uuid::new_v4().to_string();

    // Store challenge for verification
    let stored_challenge = StoredChallenge {
        challenge: challenge.clone(),
        user: Default::default(),
        timestamp: SystemTime::now()...
    };

    let mut store = state.store.lock().await;
    store.challenges.insert(auth_id.clone(), stored_challenge);

    // Return auth options
    Json(AuthenticationOptions {
        challenge: URL_SAFE.encode(&challenge),
        rp_id: state.config.rp_id.clone(),
        // ... other options
    })
}
```

The verify_authentication function validates the authentication attempt:

```rust
async fn verify_authentication(
    State(state): State<AppState>,
    Json(auth_response): Json<AuthenticatorResponse>,
) -> Result<&'static str, (StatusCode, String)> {
    // Verify client data
    let client_data = ParsedClientData::from_base64(&auth_response.response.client_data_json)?;
    client_data.verify(&state, &stored_challenge.challenge)?;

    // Verify authenticator data
    let auth_data = AuthenticatorData::from_base64(&auth_response.response.authenticator_data)?;
    auth_data.verify(&state)?;

    // Verify signature
    let credential = store.credentials.get(&auth_response.id)?;
    let public_key = UnparsedPublicKey::new(verification_algorithm, &credential.public_key);
    public_key.verify(&signed_data, &signature)?;

    Ok("Authentication successful")
}
```

This function performs three main security checks:

1. Verifies the client data (challenge, origin, operation type)
2. Validates the authenticator data (RP ID hash, user presence, verification status)
3. Verifies the signature using the stored public key

If these verifications are successful, a session can be created and the user is regarded as logged in.

## What's Next

While this basic implementation demonstrates the core concepts of WebAuthn Passkeys, several enhancements would make it production-ready:

### Authentication Improvements
The system could integrate with OAuth2/OIDC providers like Google, enabling single sign-on and unified account management. This would allow users to seamlessly link their Passkey credentials with existing accounts.

### Infrastructure
The current in-memory storage would need to be replaced with proper databases - SQL for user credentials and Redis for temporary challenge states. This would provide the scalability and persistence needed for production use.

### Testing
A comprehensive test suite would need to verify the security properties of the system, including proper challenge verification, attestation validation, and session management.

## Conclusion

Building a WebAuthn Passkey implementation from scratch was an enlightening experience that provided deep insights into both modern authentication and Rust web development. The experience showed how standards like WebAuthn and tools like Rust can make secure authentication more accessible to developers, while still demanding careful attention to security considerations.

While implementing core functionality from scratch proved to be an invaluable learning experience, production systems should rely on established, well-tested WebAuthn libraries that have undergone security audits. The insights gained from this exercise, however, will prove valuable when working with these production libraries, as understanding WebAuthn's internals helps make better architectural decisions.
