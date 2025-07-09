# OAuth2 and OpenID Connect (OIDC) Flow Testing: A Comprehensive Analysis of Response Types and Modes

When implementing OAuth2 authorization and OpenID Connect (OIDC) authentication, developers face numerous configuration choices that significantly impact both security and user experience. While the OAuth2 and OIDC specifications provide guidance, understanding how different combinations of response types and response modes behave in practice requires empirical testing.

This post presents a systematic analysis of OAuth2/OIDC flows using Google's implementation, revealing key insights about token delivery patterns, security implications, and practical recommendations for production deployments.

## The Challenge: Too Many Options, Too Little Clarity

OAuth2 and OpenID Connect (OIDC) offer multiple response types and response modes that serve different purposes:

**OAuth2 Response Types**:
- `code` - Authorization Code Grant (for access tokens)
- `token` - Implicit Grant (direct access tokens)

**OIDC Response Types**:
- `id_token` - Identity tokens for authentication
- `code token`, `code id_token`, `token id_token`, `code token id_token` - Hybrid flows

**Response Modes** (both OAuth2/OIDC):
- `query`, `fragment`, `form_post` - Different delivery methods

This creates a matrix of possibilities: 7 response types × 3 response modes × various scope combinations = 42+ different flow configurations to understand. Rather than rely on documentation alone, I built an automated testing framework to examine how these flows actually behave.

## Methodology: Automated OAuth2/OIDC Flow Testing

I created a Python script that systematically tests all OAuth2/OIDC flow combinations:

```python
# Core testing parameters
RESPONSE_TYPES = ['code', 'token', 'id_token', 'code token', 'code id_token', 'token id_token', 'code token id_token']
RESPONSE_MODES = ['query', 'fragment', 'form_post']
SCOPES = ['profile email', 'openid profile email']
```

The testing framework:

1. **Generates authorization URLs** for each OAuth2/OIDC combination
2. **Opens browser windows** for user authentication
3. **Captures responses** across query parameters, form data, and URL fragments
4. **Performs token exchange** when authorization codes are present (OAuth2 code flow)
5. **Validates ID tokens** when present (OIDC authentication)
6. **Logs comprehensive results** for analysis

This approach provided empirical data on how Google's OAuth2/OIDC implementation handles each flow configuration.

## Key Findings: Response Behavior Patterns

### Pattern 1: Location Predictability

The testing revealed consistent patterns in where tokens are delivered:

**Query/Fragment Modes:**
- Single `code` responses → Query parameters
- Any token-containing responses → URL fragments
- Multiple tokens → Always delivered together

**Form Post Mode:**
- All responses → Form parameters (consistent delivery)

### Pattern 2: Token Grouping

When multiple tokens are requested (`response_type=code token id_token`), they are always delivered together in the same location. You never see mixed delivery like code in query parameters while tokens appear in fragments.

### Pattern 3: OIDC Scope Normalization

Regardless of requested scope, Google's OIDC implementation consistently:
- Adds `openid` scope to all responses (making them OIDC flows)
- Expands scopes to include full URL versions
- Maintains identical behavior for `profile email` vs `openid profile email`
- Always includes identity information when ID tokens are requested

## Detailed Test Results

The comprehensive testing revealed distinct patterns across all response mode and type combinations:

### Query Response Mode Results

| Response Type       | Scope               | Response Location | Returned Tokens                | Token Exchange                |
|--------------------|---------------------|-------------------|-------------------------------|------------------------------|
| code               | profile email       | query params      | code                         | access_token, id_token       |
| code               | openid profile email| query params      | code                         | access_token, id_token       |
| token              | both scopes         | fragment          | access_token                 | none                         |
| id_token           | both scopes         | fragment          | id_token                     | none                         |
| code token         | both scopes         | fragment          | code, access_token           | access_token, id_token       |
| code id_token      | both scopes         | fragment          | code, id_token               | access_token, id_token       |
| token id_token     | both scopes         | fragment          | access_token, id_token       | none                         |
| code token id_token| both scopes         | fragment          | code, access_token, id_token | access_token, id_token       |

### Fragment Response Mode Results

| Response Type       | Scope               | Response Location | Returned Tokens                | Token Exchange                |
|--------------------|---------------------|-------------------|-------------------------------|------------------------------|
| code               | both scopes         | query params      | code                         | access_token, id_token       |
| token              | both scopes         | fragment          | access_token                 | none                         |
| id_token           | both scopes         | fragment          | id_token                     | none                         |
| code token         | both scopes         | fragment          | code, access_token           | access_token, id_token       |
| code id_token      | both scopes         | fragment          | code, id_token               | access_token, id_token       |
| token id_token     | both scopes         | fragment          | access_token, id_token       | none                         |
| code token id_token| both scopes         | fragment          | code, access_token, id_token | access_token, id_token       |

### Form Post Response Mode Results

| Response Type       | Scope               | Response Location | Returned Tokens                | Token Exchange                |
|--------------------|---------------------|-------------------|-------------------------------|------------------------------|
| code               | both scopes         | form params       | code                         | access_token, id_token       |
| token              | both scopes         | form params       | access_token                 | none                         |
| id_token           | both scopes         | form params       | id_token                     | none                         |
| code token         | both scopes         | form params       | code, access_token           | access_token, id_token       |
| code id_token      | both scopes         | form params       | code, id_token               | access_token, id_token       |
| token id_token     | both scopes         | form params       | access_token, id_token       | none                         |
| code token id_token| both scopes         | form params       | code, access_token, id_token | access_token, id_token       |

### Key Observations from Results

1. **OAuth2 Code Exchange Pattern**: Any flow that includes "code" triggers a token exchange, always returning both access_token and id_token (full OIDC response)
2. **OIDC Response Location Consistency**: Code-only responses go to query_params in query/fragment modes, while any responses containing tokens or ID tokens are delivered via URL fragments (regardless of whether response_mode is query or fragment). Only form_post mode consistently delivers all response types via the specified method.
3. **Scope Independence**: No difference in behavior between "profile email" and "openid profile email" - OpenID scope is always included, making all flows OIDC-compliant

## Security Analysis: Most and Least Recommended OAuth2/OIDC Flows

### 🏆 Most Recommended: Authorization Code Flow with Form Post

**Configuration**: `response_type=code`, `response_mode=form_post`

**Why it's secure:**
- No tokens in URLs or browser history
- Credentials don't appear in server logs
- Backend token exchange enables client authentication (OAuth2)
- Authorization code is short-lived and single-use
- Full OIDC compliance with secure ID token delivery

**Implementation benefits:**
- Simple to implement and debug
- Reliable across all browsers
- No client-side token handling required
- Works for both OAuth2 authorization and OIDC authentication

### ⚠️ Least Recommended: Implicit and OIDC Implicit Flows

**Configuration**: `response_type=token` or `response_type=id_token`

**Security concerns:**
- Tokens/ID tokens exposed in URL fragments
- No client authentication possible
- Higher risk of token leakage
- ID tokens may be logged in browser history (OIDC security risk)

**Functional limitations:**
- No refresh tokens available
- Shorter token lifetimes required
- Limited error handling capabilities
- Deprecated in OAuth 2.1 draft

## Practical Recommendations

### For Web Applications
```javascript
// Recommended: Authorization Code with Form Post + PKCE
const authUrl = `https://accounts.google.com/o/oauth2/v2/auth?` +
  `response_type=code&` +
  `response_mode=form_post&` +
  `client_id=${clientId}&` +
  `redirect_uri=${redirectUri}&` +
  `scope=openid profile email&` +
  `code_challenge=${codeChallenge}&` +
  `code_challenge_method=S256&` +
  `state=${state}`;
```

### For Single Page Applications (SPAs)
```javascript
// Recommended: Authorization Code with PKCE (OAuth2/OIDC)
const authUrl = `https://accounts.google.com/o/oauth2/v2/auth?` +
  `response_type=code&` +
  `response_mode=fragment&` +
  `client_id=${clientId}&` +
  `redirect_uri=${redirectUri}&` +
  `scope=openid profile email&` +
  `code_challenge=${codeChallenge}&` +
  `code_challenge_method=S256&` +
  `state=${state}`;
```

**Note:** Google's current OAuth2 implementation requires `client_secret` during token exchange even with PKCE, which violates RFC 7636 standards. For authentication-only SPAs, where client secret can't be safely stored, consider using `response_type=id_token` to entirely skip token exchange.

### Security Enhancements

Regardless of chosen flow, implement these security measures:

1. **Always use PKCE** for code-based flows (OAuth2/OIDC)
2. **Implement state parameter** for CSRF protection
3. **Use nonce parameter** for OIDC ID token replay protection
4. **Validate redirect URIs** strictly
5. **Keep authorization codes short-lived** (< 10 minutes)
6. **Verify ID token signatures** and claims (OIDC)
7. **Validate token audiences** and issuers

## Response Mode Comparison

| Response Mode | Security | Reliability | Use Case |
|---------------|----------|-------------|----------|
| `form_post` | ✅ Highest | ✅ Excellent | Web applications |
| `fragment` | ⚠️ Medium | ✅ Good | SPAs, mobile apps |
| `query` | ❌ Lowest | ✅ Good | Legacy systems only |

## Testing Your Own OAuth2/OIDC Implementation

The testing framework can be adapted for other OAuth2/OIDC providers:

```python
# Configuration for different providers
PROVIDERS = {
    'google': {
        'auth_endpoint': 'https://accounts.google.com/o/oauth2/v2/auth',
        'token_endpoint': 'https://oauth2.googleapis.com/token'
    },
    'microsoft': {
        'auth_endpoint': 'https://login.microsoftonline.com/common/oauth2/v2.0/authorize',
        'token_endpoint': 'https://login.microsoftonline.com/common/oauth2/v2.0/token'
    }
}
```

## Conclusion

This systematic analysis reveals that OAuth2/OIDC flow selection significantly impacts both security and implementation complexity. Key takeaways:

1. **Form Post mode** provides the best security profile for both OAuth2 and OIDC flows
2. **Authorization code flows** remain the gold standard for secure authentication and authorization
3. **Implicit flows** should be avoided in favor of code-based alternatives (deprecated in OAuth 2.1)
4. **OIDC scope normalization** means most flows become OpenID Connect flows automatically
5. **Consistent testing** is essential for understanding provider-specific behavior

The OAuth2/OIDC landscape continues evolving, with new security enhancements like PKCE and PAR (Pushed Authorization Requests) becoming standard. However, the fundamental principles revealed through this testing remain relevant: prioritize security, minimize token exposure, understand the difference between OAuth2 authorization and OIDC authentication, and thoroughly test your chosen configuration.

For production deployments, always combine empirical testing with security best practices to ensure robust authentication and authorization flows that protect both your application and your users.

---

*The complete testing framework and detailed results are available in the [Gist page](https://gist.github.com/ktaka-ccmp/915a3680f04f1704742f13e898ca668d?permalink_comment_id=5665842#gistcomment-5665842). Feel free to adapt the testing methodology for your own OAuth2 implementations.*
