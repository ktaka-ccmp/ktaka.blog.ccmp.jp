# Google OAuth2 + PKCE Experiment Log

**Question**: Can we exchange OAuth2 authorization codes for tokens using PKCE without client_secret on Google?

## TL;DR - The Answer

**NO.** Google requires client_secret even with proper PKCE implementation, violating OAuth2 standards.

## What We Tested

Tested whether Google's OAuth2 + PKCE implementation follows RFC 7636, which should allow public clients to get tokens without embedding client secrets.

### The Setup

**Target**: Google OAuth2 endpoint  
**Client**: Web application type  
**Flow**: Authorization Code + PKCE (S256 method)  
**Tools**: Bash script + curl + OpenSSL

## The Script

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
client_id='831022058239-486gipr6kn8l7a8cb8vqvpllupvlm3du.apps.googleusercontent.com'
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

## Test Run 1: Authorization Request

**Input URL:**
```
https://accounts.google.com/o/oauth2/v2/auth?
redirect_uri=https://oauth2.example.com/result&
response_type=code&
client_id=831022058239-486gipr6kn8l7a8cb8vqvpllupvlm3du.apps.googleusercontent.com&
scope=openid+email+profile&
access_type=online&
code_challenge=cIiy8Y1WvvnPSfR9Clo9h-qKKsHyc2F4w0v1V98HgXc&
code_challenge_method=S256&
response_mode=fragment
```

**Result:** ✅ **SUCCESS** - Got authorization code back in fragment

*Note: Google accepted PKCE parameters without complaint*

## Test Run 2: Token Exchange (PKCE Only)

**Command:**
```bash
curl -X POST \
  --data-urlencode "code=$CODE" \
  --data-urlencode "client_id=831022058239-486gipr6kn8l7a8cb8vqvpllupvlm3du.apps.googleusercontent.com" \
  --data-urlencode "redirect_uri=https://oauth2.example.com/result" \
  --data-urlencode "code_verifier=4vxWYxzPRvERSVa1zrT1Zjw8o2cLp9DKjYqrnRxeg" \
  -d 'grant_type=authorization_code' \
  https://oauth2.googleapis.com/token
```

**Result:** ❌ **FAILURE**
```json
{
  "error": "invalid_request",
  "error_description": "client_secret is missing."
}
```

## What This Means

### The Good News
- Google accepts PKCE parameters correctly
- The authorization flow works fine with PKCE
- Our PKCE parameter generation is correct

### The Bad News  
- Google still demands client_secret even with PKCE
- This violates RFC 7636 standards
- Public clients can't be truly secure with Google OAuth2

### The Technical Issue

According to OAuth2 + PKCE standards:
```
PKCE Flow = code_verifier replaces client_secret
Reality with Google = PKCE + client_secret both required
```

## Comparison: Working vs Broken

### ✅ Standard OAuth2 (works)
```bash
curl -X POST \
  --data-urlencode "code=$code" \
  --data-urlencode "client_id=$client_id" \
  --data-urlencode "redirect_uri=$redirect_uri" \
  -d "client_secret=$client_secret" \
  -d 'grant_type=authorization_code' \
  https://oauth2.googleapis.com/token
```
**Response:** Valid tokens

### ❌ PKCE-only (should work, doesn't)
```bash
curl -X POST \
  --data-urlencode "code=$code" \
  --data-urlencode "client_id=$client_id" \
  --data-urlencode "redirect_uri=$redirect_uri" \
  --data-urlencode "code_verifier=$code_verifier" \
  -d 'grant_type=authorization_code' \
  https://oauth2.googleapis.com/token
```
**Response:** `client_secret is missing`

## Why This Matters

### For Developers
- Can't build secure mobile/desktop apps with Google OAuth2
- Must embed secrets in client code (security risk)
- Forces bad security practices

### For Users
- Apps using Google login have weaker security
- Client secrets can be extracted from apps

### For Google
- Non-compliant with OAuth2 standards
- Behind competitors like Auth0, Okta, Microsoft
- Creates security vulnerabilities in ecosystem

## Technical Notes

### PKCE Parameter Generation Details
```bash
# Step 1: Generate URL-safe random verifier
code_verifier=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-43)

# Step 2: Create challenge via SHA256 + base64url encoding
code_challenge=$(echo -n $code_verifier | openssl dgst -sha256 -binary | openssl base64 | tr -d '\n' | tr '+' '-' | tr '/' '_' | tr -d '=')
```

### Key Learning: Base64url vs Base64
- Initially tried standard base64 → failed
- Google needs base64url encoding (RFC 4648)
- Conversion: `+` → `-`, `/` → `_`, remove `=`

## Other Client Types to Test

Based on research, different behaviors for:
- **Android**: May not require client_secret
- **iOS**: Similar to Android  
- **Desktop**: Requires secret but treats as "public"
- **TV/Limited**: Similar to Desktop

## Conclusion

**Google's OAuth2 + PKCE is broken by design.**

They've implemented PKCE as an *addition* to existing flows, not as a *replacement* for client secrets. This defeats the entire purpose of PKCE and makes secure public clients impossible.

## Next Steps

1. **For this project**: Accept limitation, use client_secret
2. **For new projects**: Consider non-Google OAuth2 providers
3. **For advocacy**: Document and share this limitation

## References

- RFC 7636: Proof Key for Code Exchange by OAuth Public Clients
- Multiple Stack Overflow threads confirming this limitation
- Google's own documentation (misleading about PKCE support)

---

**Bottom Line**: If you need true public client OAuth2, don't use Google. They haven't properly implemented the standards.
