# Google OAuth2 and PKCE: Understanding Client Secret Requirements

*A systematic test of Google's OAuth2 PKCE implementation and its implications for different application types.*

**Key Finding**: Google's OAuth2 implementation requires `client_secret` even when using PKCE for Web Application client types, contrary to RFC 7636 standard expectations. This post documents systematic testing that confirms this behavior and provides architectural guidance for developers.

## Background: PKCE and Public Clients

PKCE (Proof Key for Code Exchange) was introduced in RFC 7636 to address security concerns with public clients—applications that cannot securely store credentials, such as mobile apps and single-page applications (SPAs).

The standard OAuth2 flow requires a `client_secret`, but PKCE provides an alternative mechanism:

1. Generate a random `code_verifier`
2. Create a `code_challenge` by hashing the verifier  
3. Send the challenge with the authorization request
4. Exchange the authorization code using the verifier

According to RFC 7636, this should eliminate the need for `client_secret` in public clients.

## Testing Google's Implementation

I conducted a systematic test to understand how Google's OAuth2 endpoints handle PKCE requests using a Web Application client type.

### Test Setup

```bash
#!/bin/bash

# Generate PKCE parameters
code_verifier=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-43)
code_challenge=$(echo -n $code_verifier | openssl dgst -sha256 -binary | openssl base64 | tr -d '\n' | tr '+' '-' | tr '/' '_' | tr -d '=')

echo "=== PKCE Parameters ==="
echo "code_verifier: $code_verifier"
echo "code_challenge: $code_challenge"
echo ""

# OAuth2 settings
client_id='[REDACTED_CLIENT_ID]'
redirect_uri='https://oauth2.example.com/result'

# Generate authorization URL
auth_url="https://accounts.google.com/o/oauth2/v2/auth?redirect_uri=${redirect_uri}&response_type=code&client_id=${client_id}&scope=openid+email+profile&access_type=online&code_challenge=${code_challenge}&code_challenge_method=S256&response_mode=fragment"

echo "=== Authorization URL ==="
echo "$auth_url"
echo ""

echo "=== Token Exchange Command ==="
echo "curl -X POST \\"
echo "  --data-urlencode \"code=\$CODE\" \\"
echo "  --data-urlencode \"client_id=$client_id\" \\"
echo "  --data-urlencode \"redirect_uri=$redirect_uri\" \\"
echo "  --data-urlencode \"code_verifier=$code_verifier\" \\"
echo "  -d 'grant_type=authorization_code' \\"
echo "  https://oauth2.googleapis.com/token"
```

### Test Results

**Authorization Request**: ✅ Successful
Google accepted the PKCE parameters (`code_challenge` and `code_challenge_method=S256`) and returned an authorization code.

**Token Exchange with PKCE only**: ❌ Failed

```bash
curl -X POST \
  --data-urlencode "code=$CODE" \
  --data-urlencode "client_id=[REDACTED_CLIENT_ID]" \
  --data-urlencode "redirect_uri=https://oauth2.example.com/result" \
  --data-urlencode "code_verifier=[REDACTED_VERIFIER]" \
  -d 'grant_type=authorization_code' \
  https://oauth2.googleapis.com/token
```

**Response:**
```json
{
  "error": "invalid_request",
  "error_description": "client_secret is missing."
}
```

## Community Confirmation

This limitation has been documented by the developer community:

**Stack Overflow Evidence:**
- [Google OAuth 2.0 Authorization Code (with PKCE) requires a client secret](https://stackoverflow.com/questions/76528208/google-oauth-2-0-authorization-code-with-pkce-requires-a-client-secret) - Multiple developers confirm this requirement
- [Is a Client Secret Required for Google OAuth 2.0 using the PKCE Authorization Flow?](https://stackoverflow.com/questions/78673050/is-a-client-secret-required-for-google-oauth-2-0-using-the-pkce-authorization-fl) - Discussion of Google's non-standard implementation

**Google Cloud Community:**
- [Authorization Code Flow without client secret](https://www.googlecloudcommunity.com/gc/Developer-Tools/Authorization-Code-Flow-without-client-secret/m-p/814109) - A Google representative acknowledges: "Google's Identity Platform as of today does not support public applications under the 'Web Application' profile. Flows always require a client_secret."

**GitHub Issues:**
- [OAuth 2.0 with PKCE still requires client secret](https://github.com/postmanlabs/postman-app-support/issues/9409) - Tool developers encounter this limitation

## Understanding the Implications

### For Server-Side Applications
**Recommendation**: Use the traditional OAuth2 flow with `client_secret` stored securely on your server.

```bash
curl -X POST \
  --data-urlencode "code=$code" \
  --data-urlencode "client_id=$client_id" \
  --data-urlencode "redirect_uri=$redirect_uri" \
  -d "client_secret=$client_secret" \
  -d 'grant_type=authorization_code' \
  https://oauth2.googleapis.com/token
```

This is the intended use case where `client_secret` can be stored securely.

### For Single-Page Applications (SPAs)
**Recommendation**: Limit authentication to `id_token` only and handle API access through your backend.

**Critical Security Warning**: Embedding a `client_secret` in browser code exposes it to anyone with access to the client, which is fundamentally insecure. This is why the OAuth2 standard forbids it for public clients.

For SPAs that cannot securely store `client_secret`:
1. Use the implicit flow or authorization code flow to obtain only `id_token` for user authentication
2. Send the `id_token` to your backend for verification
3. Handle Google API calls from your backend using server-stored credentials

This approach separates authentication (client-side) from API access (server-side).

**Note**: As of this writing, Google's official documentation still directs SPAs toward the [implicit flow](https://developers.google.com/identity/protocols/oauth2/javascript-implicit-flow), which has been deprecated in OAuth 2.1 due to security concerns. This inconsistency in guidance contributes to confusion around best practices.

### For Mobile and Desktop Applications
**Current Reality**: Google's implementation requires embedding `client_secret` in the application code.

Google's documentation acknowledges this: "The process results in a client ID and, in some cases, a client secret, which you embed in the source code of your application. (In this context, the client secret is obviously not treated as a secret.)"

While not ideal from a security perspective, this is Google's intended approach for native applications.

## Technical Implementation Notes

### PKCE Parameter Generation
Google requires base64url encoding for the code challenge:

```bash
# Correct base64url encoding for Google
code_challenge=$(echo -n $code_verifier | openssl dgst -sha256 -binary | openssl base64 | tr -d '\n' | tr '+' '-' | tr '/' '_' | tr -d '=')
```

### Test Configuration
This testing used:
- Web Application client type in Google Cloud Console
- Scopes: `openid email profile`
- Standard OAuth2 endpoints (`https://accounts.google.com/o/oauth2/v2/auth` and `https://oauth2.googleapis.com/token`)
- PKCE method S256

### Different Client Types

Google offers various OAuth2 client types that may have different behaviors:
- **Web Application**: In our testing, always required `client_secret`
- **Android/iOS**: May have different requirements (needs further testing)
- **Desktop**: Reported to require secret but treat as non-confidential
- **TV/Limited Input**: Similar behavior to desktop (based on community reports)

## Summary: Standard vs Reality

According to OAuth2/PKCE standards, public clients should be able to authenticate without embedding secrets. Here's how Google's implementation compares:

| Client Type | Standard PKCE<br>(No Secret Needed) | Google's Reality<br>(Secret Required) | Security Impact |
|-------------|-------------------------------------|---------------------------------------|-----------------|
| **Server-side** | ❌ No (secret required) | ❌ No (secret required) | ✅ Secure (secret stays on server) |
| **SPA (Browser)** | ✅ Yes (recommended) | ❌ No (not supported) | ❌ Secret exposed to users |
| **Mobile/Desktop** | ✅ Yes (recommended) | ❌ No (not supported) | ❌ Secret embedded in app |

**The Problem**: Google requires secrets for all client types, forcing developers to embed credentials in publicly distributed code—exactly what PKCE was designed to prevent.

## Architectural Recommendations

### Hybrid Approach for SPAs
```
Browser (SPA) → Authentication only (id_token)
     ↓
Backend Server → API calls with client_secret
```

### Mobile Applications
If using Google OAuth2 with mobile apps, implement additional security measures:
- Use certificate pinning
- Implement runtime application self-protection (RASP)
- Monitor for application tampering

### Server-Side Applications
Standard OAuth2 flow with proper secret management:
- Store `client_secret` in secure configuration
- Use environment variables or secret management systems
- Rotate credentials regularly

## Community Feedback Welcome

The findings in this post are based on testing with a specific client configuration (Web Application type) and may not represent all possible scenarios. Google's OAuth2 implementation is complex, with different behaviors across client types, API versions, and configuration options.

**If you have different results or experiences**, please share them:
- Have you successfully used PKCE without client_secret with Google OAuth2?
- Do different client types (Android, iOS, Desktop) behave differently?
- Are there specific Google APIs or configurations that work as expected?
- Have there been recent changes to Google's implementation?

This post aims to document one specific finding to help other developers, but the OAuth2 landscape is constantly evolving. Contradicting evidence or alternative approaches would be valuable additions to the community's understanding.

## Conclusion

Google's OAuth2 implementation requires `client_secret` even when using PKCE for Web Application client types, which differs from the RFC 7636 standard. This finding, supported by community reports, indicates a consistent pattern in Google's implementation.

Understanding this behavior helps in choosing appropriate architectural patterns:

- **Server-side applications**: Use standard OAuth2 with secure secret storage
- **SPAs**: Limit to authentication-only flows, handle API access server-side  
- **Mobile/Desktop**: Accept the embedded secret limitation or use hybrid architectures

When implementing OAuth2 with Google, design your architecture around these observed constraints. While other client types may behave differently, the Web Application type consistently requires client secrets alongside PKCE.

## References

1. [RFC 7636 - Proof Key for Code Exchange by OAuth Public Clients](https://tools.ietf.org/html/rfc7636)
2. [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
3. [Google OAuth 2.0 for Mobile & Desktop Apps](https://developers.google.com/identity/protocols/oauth2/native-app)
4. [Google OAuth 2.0 JavaScript Implicit Flow](https://developers.google.com/identity/protocols/oauth2/javascript-implicit-flow)
5. [Manage OAuth Clients - Google Cloud Platform Console Help](https://support.google.com/cloud/answer/15549257)
6. [Stack Overflow: Google OAuth 2.0 Authorization Code (with PKCE) requires a client secret](https://stackoverflow.com/questions/76528208/google-oauth-2-0-authorization-code-with-pkce-requires-a-client-secret)
7. [Google Cloud Community: Authorization Code Flow without client secret](https://www.googlecloudcommunity.com/gc/Developer-Tools/Authorization-Code-Flow-without-client-secret/m-p/814109)
