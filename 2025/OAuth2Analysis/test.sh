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
echo "1. Visit the URL above"
echo "2. Extract the 'code' parameter from the redirect"
echo "3. Run the token exchange command below:"
echo ""

echo "=== Token Exchange Command ==="
echo "curl -X POST \\"
echo "  --data-urlencode \"code=\$CODE\" \\"
echo "  --data-urlencode \"client_id=$client_id\" \\"
echo "  --data-urlencode \"redirect_uri=$redirect_uri\" \\"
echo "  --data-urlencode \"code_verifier=$code_verifier\" \\"
echo "  -d 'grant_type=authorization_code' \\"
echo "  https://oauth2.googleapis.com/token"
