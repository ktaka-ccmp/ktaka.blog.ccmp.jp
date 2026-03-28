---
title: "Understanding ECDSA Signatures with the Web Crypto API"
published: true
description: "Using the Web Crypto API's crypto.subtle to generate and verify ECDSA digital signatures in the browser, Bun, and Node.js."
tags: ecdsa, webcrypto, javascript, cryptography
canonical_url: https://ktaka.blog.ccmp.jp/en/2026/WebCryptoEcdsa
---

## Introduction

Cryptographic techniques are used everywhere on the internet — TLS, SSH, email signatures, and more. Signing, verification, encryption, decryption, key exchange — these terms come up constantly, yet if asked whether I truly understood how they work, the honest answer was: not really.

Then I discovered the Web Crypto API. It's a cryptographic API built into the browser that lets you perform crypto operations without any external libraries. The API is simple enough that you can learn by writing and running code.

This motivated me to properly understand the fundamentals of cryptography at the code level. In this article, we'll look at digital signatures (ECDSA) and see how signing and verification actually work.

---

## What is the Web Crypto API?

The [Web Crypto API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Crypto_API) is a cryptographic API built into the browser. It allows you to perform key generation, signing, verification, encryption, and decryption without any external libraries.

All operations are accessed through the `crypto.subtle` object.

| Method | Purpose |
|--------|---------|
| `crypto.subtle.generateKey()` | Generate key pairs or symmetric keys |
| `crypto.subtle.sign()` | Sign with a private key |
| `crypto.subtle.verify()` | Verify with a public key |
| `crypto.subtle.encrypt()` | Encrypt |
| `crypto.subtle.decrypt()` | Decrypt |
| `crypto.subtle.deriveKey()` | Derive a symmetric key from key exchange |
| `crypto.subtle.exportKey()` | Export a key in JWK or other formats |
| `crypto.subtle.importKey()` | Import an external key |

Each method returns a `Promise`, so you receive results with `await`. In this article, we'll use three: `generateKey`, `sign`, and `verify`.

Main algorithms available with `generateKey`:

| Algorithm | Type | Purpose |
|-----------|------|---------|
| **ECDSA** | Elliptic curve (P-256, etc.) | Signing and verification |
| **RSA-OAEP** | RSA | Encryption and decryption |
| **AES-GCM** | Symmetric key | Authenticated encryption/decryption |
| **ECDH** | Elliptic curve (P-256, etc.) | Key exchange |
| **HMAC** | Symmetric key | Message authentication |

The same `crypto.subtle` is also available in Bun and Node.js (v19+), so the same code runs on the server side as well.

---

## What is a Digital Signature?

A digital signature is a mechanism where you "sign with a private key and verify with a public key." Only the signer can create the signature, but anyone can verify its authenticity.

| Operation | Key Used | Meaning |
|-----------|----------|---------|
| Sign | **Private key** | Proves that you created it |
| Verify | **Public key** | Anyone can confirm authenticity |

In this article, we'll use the Web Crypto API to sign and verify with ECDSA (Elliptic Curve Digital Signature Algorithm).

---

## Code: Key Pair Generation → Signing → Verification

Run the following shell command to save the code as `ecdsa.mjs`. For browsers, paste the JavaScript portion (excluding the `cat` and `EOF` lines) into the DevTools Console.

| Environment | How to Run |
|-------------|-----------|
| **Browser** | Paste the JavaScript portion into the DevTools Console |
| **Bun** | `bun ecdsa.mjs` |
| **Node.js** (v19+) | `node ecdsa.mjs` |

```javascript
cat << 'EOF' > ecdsa.mjs

// 1. Generate key pair (ECDSA, P-256)
const keyPair = await crypto.subtle.generateKey(
  { name: "ECDSA", namedCurve: "P-256" },
  true, // extractable: true to allow key export (use false in production)
  ["sign", "verify"]
);

// 2. Data to sign
const message = "Hello, WebCrypto!";
const data = new TextEncoder().encode(message);

// 3. Sign with private key
const signature = await crypto.subtle.sign(
  { name: "ECDSA", hash: "SHA-256" },
  keyPair.privateKey,
  data
);

// 4. Verify with public key (original data)
const isValid = await crypto.subtle.verify(
  { name: "ECDSA", hash: "SHA-256" },
  keyPair.publicKey,
  signature,
  data
);

// 5. Verify with tampered data
const tamperedMessage = "Hello, WebCrypto! (tampered)";
const tampered = new TextEncoder().encode(tamperedMessage);
const isValidTampered = await crypto.subtle.verify(
  { name: "ECDSA", hash: "SHA-256" },
  keyPair.publicKey,
  signature,
  tampered
);

// Export key pair
const privateKey = await crypto.subtle.exportKey("jwk", keyPair.privateKey);
const publicKey = await crypto.subtle.exportKey("jwk", keyPair.publicKey);

// Output
console.log("Key pair generated:\nPrivate key:", privateKey);
console.log("Public key:", publicKey);

console.log("\nSigning:\nData:", message);
console.log("Signature (Base64):", btoa(String.fromCharCode(...new Uint8Array(signature))));

console.log("\nVerification:\nData:", message);
console.log("Result:", isValid); // true

console.log("\nTampered data verification:\nData:", tamperedMessage);
console.log("Result:", isValidTampered); // false
EOF
```

Sample output:

```bash
$ bun ecdsa.mjs
Key pair generated:
Private key: {
  crv: "P-256",
  d: "qTk9mKRBkX5MCnNzGeCvg5sO1vAWe0FLRXHse7QzSlQ",
  ext: true,
  key_ops: [ "sign" ],
  kty: "EC",
  x: "lWH4MQwp7VEMqAKxk_DYef1_ZY4lVciws4nj1wwFANE",
  y: "c_aEH9x91cYmuaatRW5Nys6uFHDBadDZA4IJuPLVQCY",
}
Public key: {
  crv: "P-256",
  ext: true,
  key_ops: [ "verify" ],
  kty: "EC",
  x: "lWH4MQwp7VEMqAKxk_DYef1_ZY4lVciws4nj1wwFANE",
  y: "c_aEH9x91cYmuaatRW5Nys6uFHDBadDZA4IJuPLVQCY",
}

Signing:
Data: Hello, WebCrypto!
Signature (Base64): j3z3keEwOxWWl/7kJ9vWphyQYsY/W78TlCB/b0OuN4jlWCAXmWVwOD9DYyk54C3NG/eZblKt6cNYMf6rg24gUw==

Verification:
Data: Hello, WebCrypto!
Result: true

Tampered data verification:
Data: Hello, WebCrypto! (tampered)
Result: false
```

The code first generates an ECDSA key pair, then signs data with the private key to produce a signature. When verifying the signature using the public key and data, the original data returns `true` while tampered data returns `false`. If even a single byte of data changes, the signature verification fails and tampering is detected. Since the signature cannot be forged from the public key alone, a third party can confirm that "the owner of the private key signed this data."

---

## Key Points

- **ECDSA is for signing only.** It cannot encrypt or decrypt. Encryption requires different algorithms.
- **`extractable: false`** prevents the private key from being exported. This setting is recommended in production.
- **`P-256` (secp256r1)** is a widely used curve on the web and mobile. It's also used in TLS, SSH, and Passkeys.

---

## Summary

The Web Crypto API is a cryptographic API built into the browser, making it easy to experiment with code in the browser console, Bun, or Node.js. Using `crypto.subtle`, we demonstrated the generation and verification of ECDSA digital signatures. We confirmed that the fundamentals of asymmetric cryptography — signing with a private key and verifying with a public key — can be easily tested.

---

{% details Appendix: What Does ECDSA Actually Compute? %}

**Key Pair Generation:**

1. Generate a random integer `d` (`1 ≤ d ≤ n-1`, where n is the curve order) → this is the **private key**
2. Compute a point on the elliptic curve: `Q = d · G` (G is the base point) → this is the **public key**

The private key is just a random number, and the public key is a point derived from it via scalar multiplication on the elliptic curve. Recovering `d` from `Q` and `G` is extremely difficult, so the private key cannot be derived from the public key.

**Signing (private key side):**

1. Hash the data: `h = SHA-256(data)`
2. Generate a random number `k`
3. Compute a point on the elliptic curve: `R = k · G` (G is the base point)
4. `r = R.x mod n` (x-coordinate of R)
5. `s = k⁻¹ × (h + r × private_key) mod n`
6. The signature is the pair `(r, s)`

**Verification (public key side):**

1. Hash the data: `h = SHA-256(data)`
2. `u1 = h × s⁻¹ mod n`
3. `u2 = r × s⁻¹ mod n`
4. Recover a point on the elliptic curve: `R' = u1 · G + u2 · public_key`
5. If `R'.x mod n == r`, return `true`

Verification recovers a point on the elliptic curve from the data hash, `s` from the signature, and the public key, then checks whether its x-coordinate matches `r` from the signature.

**Point Addition and Scalar Multiplication on Elliptic Curves:**

`k · G` is the point obtained by adding the elliptic curve point G to itself k times.

Point addition on elliptic curves is a geometric operation different from ordinary addition.

Point addition (P + Q):
1. Draw a line through two points P and Q on the curve
2. Find the third point where the line intersects the curve
3. Reflect that point across the x-axis → this is `P + Q`

Point doubling (P + P):
1. Draw the tangent line at P
2. Find the point where the tangent intersects the curve
3. Reflect across the x-axis → this is `2P`

Scalar multiplication `k · G` repeats this addition k times (`G + G + G + ... + G`). In practice, the "double-and-add" method computes this efficiently.

Why this works as cryptography:
- Computing `k · G` from `k` and `G` is **fast**
- Recovering `k` from `G` and `k · G` is **extremely difficult** (Elliptic Curve Discrete Logarithm Problem)

This one-way property is the foundation of ECDSA's security.

**About `k⁻¹`:**

`k⁻¹` is the modular inverse of `k` (an integer satisfying `k⁻¹ × k ≡ 1 (mod n)`). Unlike ordinary division (`1/k`), this performs the equivalent of "division" using integers in the `mod n` world.

For a hands-on implementation of these calculations: [Implementing ECDSA from Scratch Without Libraries](https://ktaka.blog.ccmp.jp/en/2026/EcdsaFromScratch)

References:
- [Wikipedia — Elliptic Curve Digital Signature Algorithm](https://en.wikipedia.org/wiki/Elliptic_Curve_Digital_Signature_Algorithm)
- [Practical Cryptography — ECDSA: Sign / Verify](https://cryptobook.nakov.com/digital-signatures/ecdsa-sign-verify-messages)
- [Andrea Corbellini — Elliptic Curve Cryptography: ECDH and ECDSA](https://andrea.corbellini.name/2015/05/30/elliptic-curve-cryptography-ecdh-and-ecdsa/)
{% enddetails %}
