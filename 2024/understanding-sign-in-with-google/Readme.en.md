# Understanding Sign in with Google: Not the OIDC Wrapper You Think It Is


- I believe many people have experience of loging-in a web site/applications using social media accounts, like Google, Facebook or other social media login for authentication.
- Social media authentication is very convienent beacuse users are not required to use a passwords to authenticate tehemselves on that site.
- Rather they can rely on authentication mechanism of social mediea that tends to be very secure.
- It is also beneficial for the develepers of web application to simplify the implementation of login mechanisms, without using magic-link, sms code vrification or use of one time code authenticator.
- Social media authentication on a web site is often implemented using OAuth2 starndard.
- Since the standard itself is rather complicated, developers are required to familialize themself to the standard.
- When you look up the documentation of Google, they have several ways to implement third party authentication depending on type of application.
- For web application they seem to have two type of offering, one with standard OAuth2/OIDC and the other with simplified "Sign in with Google".
- You might assume Sign in with Google was simply a wrapper around OpenID Connect (OIDC).
- But reality is that they are quite different things.


Until recently, I was one of many developers who assumed  Through discussions with fellow developers, I realized this common misconception needed clarification. Let me share what I learned.

> **Note on Documentation**: Google's own [documentation](https://developers.google.com/identity/gsi/web/guides/overview) states that "Sign in with Google is based on OAuth 2.0". However, the same documentation describes it as a proprietary SDK that "aims to offer an easier and more secure experience for developers than the standard OAuth and OpenID Connect protocols". This mixed messaging has contributed to developer confusion. While Sign in with Google might be inspired by OAuth 2.0 concepts, its actual implementation is a proprietary protocol that diverges significantly from standard OAuth 2.0/OIDC flows.

## The Misconception

When we see "Sign in with Google," we typically think:
1. It must be using OAuth 2.0/OpenID Connect under the hood (reinforced by Google's documentation)
2. It's just a simplified API over standard protocols
3. The implementation details don't matter much

## The Reality

Sign in with Google, while described as being "based on OAuth 2.0", is actually a proprietary protocol with its own unique characteristics. Let's compare both implementations:

### Sign in with Google
```javascript
// Simple initialization
google.accounts.id.initialize({
  client_id: 'YOUR_CLIENT_ID',
  callback: handleCredentialResponse
});

// Callback receives:
{
  credential: "eyJhbGci..." // JWT token
  clientId: "..."
  select_by: "..."
}
```

### Standard OIDC
```
1. Authorization Request:
   /authorize?
   response_type=code&
   client_id=...&
   scope=openid profile&
   redirect_uri=...&
   state=...&
   nonce=...

2. Receive authorization code
3. Exchange code for tokens:
   - id_token
   - access_token
   - refresh_token (optional)
```

## Flow Comparisons

### Sign in with Google (Popup Flow):
```
+-------------+  1. Init Sign-in   +----------------+
|   Web App   | ---------------->  |                |
|  (Browser)  |                    |  Google Auth   |
|             | <----------------  |                |
+-------------+  2. ID Token       +----------------+
       |                                   
       | 3. Send ID Token                  
       v                                   
+-------------+  4. Validate Token +----------------+
|  Backend    | --------------->  |  Google APIs    |
|   Server    | <---------------  |                 |
+-------------+  5. Token Info    +----------------+
       |
       | 6. Create Session
       | (Potential security risk:
       |  ID Token transmission)
       v
```

### OIDC Flow:
```
+-------------+  1. Init Auth     +----------------+
|   Web App   | ---------------->  |                |
|  (Browser)  |                    |  Google Auth   |
|             | <----------------  |                |
+-------------+  2. Auth Code      +----------------+
       |                                   ^
       | 3. Send Code                      |
       v                                   |
+-------------+  4. Exchange Code          |
|  Backend    | -------------------------  |
|   Server    | client_id + client_secret  |
|             |                            |
|             | <------------------------- |
|             | 5. ID Token +              |
|             |    Access Token +          |
|             |    Refresh Token           |
+-------------+                            |
       |
       | 6. Create Session
       | (More secure: code-only
       |  transmission to frontend)
       v
```

## Key Differences

1. **Protocol Flow**
   - Sign in with Google: Though inspired by OAuth 2.0, implements a proprietary direct ID token delivery without standard authorization code exchange
   - OIDC: Follows standard OAuth 2.0/OIDC specifications with full authorization code flow

2. **Token Types**
   - Sign in with Google: Limited to ID tokens only, departing from standard OAuth 2.0 token types
   - OIDC: Provides full range of standard OAuth 2.0 tokens: ID token, access token, refresh token, and more

3. **Configuration**
   - Sign in with Google: Minimal setup reflecting its proprietary nature
   - OIDC: Requires full OAuth client configuration following standard specifications

## Security Implications

### Sign in with Google (Popup Mode)
- Frontend receives ID token directly
- ID token must be sent to backend to establish session
- Potential security risk: ID token transmission through frontend
- Limited control over token flow

### Standard OIDC
- Frontend only handles authorization code
- Backend securely exchanges code for tokens using client secret
- More secure: Frontend never handles sensitive tokens
- Complete control over token exchange and session establishment
- Follows security best practices for token handling

## Why This Matters

1. **Security Considerations**
   - Different security models affect your application's security posture
   - While Google's documentation suggests OAuth 2.0 foundations, the actual implementation follows proprietary security patterns
   - Important for compliance requirements that might expect standard OAuth 2.0/OIDC flows

2. **Flexibility**
   - Despite being "based on OAuth 2.0", Sign in with Google's proprietary nature limits its token types and flows
   - OIDC offers more token types and standard flows for different use cases
   - Better control over authentication flow in standard OIDC

3. **Portability**
   - Code written for Sign in with Google won't translate to other providers due to its proprietary nature
   - OIDC implementations are more portable across providers due to standardization
   - Migration between providers becomes more challenging with proprietary protocols

## Conclusion

While Sign in with Google offers a simpler developer experience, its relationship with OAuth 2.0 is more complex than it first appears. Despite Google's documentation describing it as "based on OAuth 2.0", the actual implementation is a proprietary protocol that significantly diverges from standard OAuth 2.0/OIDC flows. 

When choosing between Sign in with Google and standard OIDC, consider:

- Security requirements for token handling
- Need for multiple token types
- Importance of standardization
- Requirements for multi-provider support
- Compliance requirements
- Impact of using a proprietary protocol versus standard OAuth 2.0/OIDC

For applications requiring robust security and standardization, implementing the full OIDC flow might be the better choice, despite the additional complexity. The trade-off between convenience and standards compliance becomes particularly important when considering future maintenance and potential provider changes.

Remember: When it comes to authentication, understanding the true nature of your chosen protocol - whether standard or proprietary - is crucial for making informed architectural decisions.
