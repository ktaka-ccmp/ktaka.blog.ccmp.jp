+++
title = "Implementing ECDSA from Scratch Without Libraries"
date = 2026-03-27
description = "Implementing ECDSA signing and verification using only BigInt — tracing every step of modular arithmetic, elliptic curve point operations, and the signature formula with intermediate values."
path = "en/2026/EcdsaFromScratch"
[extra]
lang = "en"
+++

<p style="text-align: right"><a href="/2026/EcdsaFromScratch">日本語版</a></p>

## Introduction

In the [previous article](/en/2026/WebCryptoEcdsa), we used the Web Crypto API's `crypto.subtle` to sign and verify with ECDSA. The API made it easy, but the internals remained a black box.

In this article, we implement ECDSA signing and verification from scratch using only basic arithmetic and mod — no crypto libraries. We output intermediate values at every step to see exactly what's happening.

The code and explanations in this article were developed through conversation with AI (Claude). The idea of using a small curve to keep all values to two digits, and the structure of showing intermediate values at each step, emerged from that discussion.

---

## Approach: Using a Small Curve

Real ECDSA (P-256) uses 256-bit numbers, but the algorithm is independent of curve size. Here we use `y² = x³ + x + 4 (mod 97)`, a small curve where all values fit in two digits.

```javascript
const p = 97n;  // Finite field prime
const a = 1n;   // Curve parameter a
const b = 4n;   // Curve parameter b
// Curve: y² = x³ + ax + b (mod p)
```

*The `n` suffix on number literals denotes JavaScript's `BigInt` (arbitrary-precision integers).*

---

## The Three Layers of ECDSA

ECDSA signing and verification consists of three layers:

| Layer | Content | Functions to Implement |
|-------|---------|----------------------|
| 1. Modular arithmetic | mod operation, modular inverse | `mod`, `modInverse` |
| 2. Elliptic curve point operations | Point addition, scalar multiplication | `pointAdd`, `scalarMul` |
| 3. ECDSA protocol | Key generation, signing, verification | Combination of above |

We'll implement these from the bottom up.

---

## Layer 1: Modular Arithmetic

All ECDSA calculations are performed in the world of modular arithmetic (mod). Two operations are needed: mod and modular inverse.

### mod Function

JavaScript's `%` is a remainder operator that returns negative results for negative inputs (e.g., `-1n % 3n` → `-1n`). Using `((a % m) + m) % m` ensures the result is always in the range `[0, m)`.

```javascript
const mod = (a, m) => ((a % m) + m) % m;
```

### Modular Inverse

The modular inverse `k⁻¹` is "an integer satisfying `k⁻¹ × k ≡ 1 (mod m)`," used instead of ordinary division. It can be computed using the Extended Euclidean Algorithm.

```javascript
const modInverse = (a, m) => {
  a = mod(a, m);
  let [old_r, r] = [a, m];
  let [old_s, s] = [1n, 0n];
  while (r !== 0n) {
    const q = old_r / r;
    [old_r, r] = [r, old_r - q * r];
    [old_s, s] = [s, old_s - q * s];
  }
  if (old_r !== 1n) throw new Error(`No inverse: gcd(${a}, ${m}) = ${old_r}`);
  return mod(old_s, m);
};
```

For example, `modInverse(37n, 97n)` returns `21n`. Since 37 × 21 = 777 = 97 × 8 + 1, indeed 37 × 21 mod 97 = 1.

<details>
<summary>How the Extended Euclidean Algorithm works</summary>

First, the standard Euclidean algorithm finds the GCD by repeated division. For 37 and 97:

```
97 = 2 × 37 + 23
37 = 1 × 23 + 14
23 = 1 × 14 +  9
14 = 1 ×  9 +  5
 9 = 1 ×  5 +  4
 5 = 1 ×  4 +  1  ← remainder 1 = GCD
 4 = 4 ×  1 +  0  ← done
```

Then trace back from remainder 1 to express it as `37 × ? + 97 × ? = 1`:

```
1 = 5 - 1×4
  = 5 - 1×(9 - 1×5)           = 2×5 - 1×9
  = 2×(14 - 1×9) - 1×9        = 2×14 - 3×9
  = 2×14 - 3×(23 - 1×14)      = 5×14 - 3×23
  = 5×(37 - 1×23) - 3×23      = 5×37 - 8×23
  = 5×37 - 8×(97 - 2×37)      = 21×37 - 8×97
```

So `21 × 37 - 8 × 97 = 1`, meaning `37 × 21 ≡ 1 (mod 97)`. The inverse is 21.

In the code, `old_r, r` track the remainders, while `old_s, s` simultaneously compute the "trace-back" coefficients.

</details>

---

## Layer 2: Elliptic Curve Point Operations

"Point addition" on an elliptic curve is a geometric operation different from ordinary addition. We also need to handle the point at infinity (identity element).

```javascript
const INFINITY = { x: null, y: null };
const isInfinity = (P) => P.x === null && P.y === null;
```

### Point Addition P + Q

Draw a line through two points, find the third intersection with the curve, and reflect across the x-axis. When P = Q, use the tangent line (point doubling). The formulas are derived algebraically by solving the line and curve equations simultaneously — they consist only of basic arithmetic, so they work in the mod p world as well. The only difference is that division is replaced by multiplication with the modular inverse, and each result is reduced mod p.

```javascript
const pointAdd = (P, Q, a, p) => {
  if (isInfinity(P)) return Q;
  if (isInfinity(Q)) return P;
  if (P.x === Q.x && mod(P.y + Q.y, p) === 0n) return INFINITY;

  // lam = slope of the line (tangent slope for point doubling)
  let lam;
  if (P.x === Q.x && P.y === Q.y) {
    // Point doubling: λ = (3x² + a) / (2y)
    lam = mod((3n * P.x * P.x + a) * modInverse(2n * P.y, p), p);
  } else {
    // Addition of two distinct points: λ = (y₂ - y₁) / (x₂ - x₁)
    lam = mod((Q.y - P.y) * modInverse(Q.x - P.x, p), p);
  }
  // Find the third intersection with the curve, then reflect across x-axis
  const xr = mod(lam * lam - P.x - Q.x, p);
  const yr = mod(lam * (P.x - xr) - P.y, p);
  return { x: xr, y: yr };
};
```

### Scalar Multiplication k · P

Adding G to itself k times. A naive loop would be slow, so we use the double-and-add method. For example, k = 42 is `101010` in binary, so `42·G = 32·G + 8·G + 2·G`. The algorithm repeatedly doubles G and adds when the corresponding bit is 1. The parameter `n` is the group order (a value related to the number of points on the curve), computed by `findOrder` below.

```javascript
const scalarMul = (k, P, a, p, n) => {
  let result = INFINITY;
  let addend = { ...P };  // doubles each iteration: G, 2G, 4G, 8G, ...
  k = mod(k, n);
  while (k > 0n) {
    if (k & 1n) result = pointAdd(result, addend, a, p);  // add if bit is 1
    addend = pointAdd(addend, addend, a, p);  // double
    k >>= 1n;  // next bit
  }
  return result;
};
```

---

## Helper Functions

A function to find the order of base point G (`n · G = ∞` for the smallest n), and a simple hash function to replace SHA-256:

```javascript
const findOrder = (G, a, p) => {
  let P = { ...G };
  // By Hasse's theorem, order ≤ p+1+2√p, so p*4 is a safe upper bound
  for (let i = 2n; i < p * 4n; i++) {
    P = pointAdd(P, G, a, p);
    if (isInfinity(P)) return i;
  }
  return null;
};

const toyHash = (msg, n) => {
  let h = 0n;
  for (let i = 0; i < msg.length; i++) {
    h = mod(h * 31n + BigInt(msg.charCodeAt(i)), n);
  }
  return h === 0n ? 1n : h;
};
```

---

## Curve Parameters and Base Point G

In real P-256, NIST specifies the curve parameters (p, a, b) and the base point G's coordinates in the standard, and each implementation uses those values directly. Here we walk through how the base point is determined, for learning purposes.

<details>
<summary>Reference: Actual P-256 parameters</summary>

```
p   = 0xFFFFFFFF00000001000000000000000000000000FFFFFFFFFFFFFFFFFFFFFFFF
a   = 0xFFFFFFFF00000001000000000000000000000000FFFFFFFFFFFFFFFFFFFFFFFC
b   = 0x5AC635D8AA3A93E7B3EBBD55769886BC651D06B0CC53B0F63BCE3C3E27D2604B
G.x = 0x6B17D1F2E12C4247F8BCE6E563A440F277037D812DEB33A0F4A13945D898C296
G.y = 0x4FE342E2FE1A7F9B8EE7EB4A7C0F9E162BCE33576B315ECECBB6406837BF51F5
n   = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551
```

All values are 256-bit. The scale is vastly different from the toy curve in this article (p=97, n=89), but the algorithm is exactly the same.

Source: [NIST SP 800-186 — Recommendations for Discrete Logarithm-based Cryptography: Elliptic Curve Domain Parameters](https://csrc.nist.gov/pubs/sp/800/186/final)

</details>

### Finding Points on the Curve

Substitute x = 0, 1, 2, ... and compute `x³ + ax + b mod p`, checking whether a y exists such that `y² ≡ result (mod p)`.

```
x = 0:  x³+x+4 mod 97 =  4  →  y² ≡  4 (mod 97)  →  y = 2, 95   →  (0,2), (0,95)
x = 1:  x³+x+4 mod 97 =  6  →  y² ≡  6 (mod 97)  →  y = 43, 54  →  (1,43), (1,54)
x = 2:  x³+x+4 mod 97 = 14  →  y² ≡ 14 (mod 97)  →  no square root (no point)
x = 3:  x³+x+4 mod 97 = 34  →  y² ≡ 34 (mod 97)  →  no square root (no point)
x = 4:  x³+x+4 mod 97 = 72  →  y² ≡ 72 (mod 97)  →  y = 13, 84  →  (4,13), (4,84)
```

Points always come in pairs of y and p−y (2 + 95 = 97 = p), symmetric about the x-axis. This curve has 88 points in total (plus the point at infinity ∞).

### Choosing a Point with Prime Order

For ECDSA, the order of G (`n · G = ∞` for the smallest n) must be prime.

```javascript
const isPrime = (n) => {
  if (n < 2n) return false;
  for (let d = 2n; d * d <= n; d++) {
    if (n % d === 0n) return false;
  }
  return true;
};

// Search for a point with prime order
for (let x = 0n; x < p; x++) {
  const rhs = mod(x * x * x + a * x + b, p);
  for (let y = 0n; y < p; y++) {
    if (mod(y * y, p) !== rhs) continue;
    const candidate = { x, y };
    const order = findOrder(candidate, a, p);
    if (isPrime(order)) {
      console.log(`G = (${x}, ${y}), order n = ${order}`);
      break;
    }
  }
}
```

Since the group order is 89 (prime), all 88 points have order 89, and any point can serve as G. We choose G = (0, 2).

Summarizing the curve parameters and base point for this demo:

```javascript
const p = 97n;
const a = 1n;
const b = 4n;
const G = { x: 0n, y: 2n };
```

Verification that G is on the curve: 2² mod 97 = 4, 0³ + 1·0 + 4 mod 97 = 4. They match.

---

## Layer 3: ECDSA Protocol

The ECDSA protocol consists of three steps: key generation, signing, and verification.

```
Key generation:  Compute Q = d · G
                 Recovering d from Q is infeasible (discrete logarithm problem)

Signing:       {d, k, h, (G, a, p, n)}  →  compute (r, s)
Verification:  {Q, s, h', (G, a, p, n)} →  compute r'

d: private key, k: ephemeral key, Q: public key
r, s: signature
h, h': message hash
G, a, p, n: curve parameters

h' == h (no tampering) → r' == r (verification succeeds)
h' ≠ h (tampered)      → r' ≠ r (verification fails)
```

<details>
<summary>Why do they arrive at the same r?</summary>

Signing and verification each compute the following:

```
Signing:      R = k·G
              r = R.x mod n
              s = k⁻¹·(h + r·d) mod n
              → signature (r, s)

Verification: r' = (s⁻¹·h'·G + s⁻¹·r·Q).x mod n
              → r' == r means verification succeeds
```

When `h' == h`, expanding the verifier's point computation:

```
R' = s⁻¹·h'·G + s⁻¹·r·Q
   = s⁻¹·h·G + s⁻¹·r·Q       ← substitute h' = h
   = s⁻¹·h·G + s⁻¹·r·(d·G)   ← substitute Q = d·G
   = (s⁻¹·h + s⁻¹·r·d)·G
   = s⁻¹·(h + r·d)·G
   = k·G                       ← from s = k⁻¹·(h+r·d), so s⁻¹·(h+r·d) = k

r' = R'.x mod n
   = (k·G).x mod n
   = r                         ← same as signing side
```

Therefore, when `h' == h`, `r' == r`.

</details>

The following code demonstrates each step.

### Key Generation

Choose a private key d and compute the public key Q = d · G. d can be any value from 1 to n-1 (1 to 88 for this curve).

```javascript
// G=(0,2), a=1, p=97 were determined in the previous section
const n = findOrder(G, a, p); // n = 89
const d = 23n;                // Private key (1 ≤ d ≤ n-1)
const Q = scalarMul(d, G, a, p, n); // Public key Q = d · G
console.log(`Private key d = ${d}`);
console.log(`Public key Q = (${Q.x}, ${Q.y})`);
```

```
Private key d = 23
Public key Q = (63, 57)
```

Changing d changes Q:

```
d = 22  →  Q = (96, 83)
d = 23  →  Q = (63, 57)   ← this demo
d = 24  →  Q = (56, 3)
d = 25  →  Q = (38, 77)
```

Recovering private key d = 23 from public key Q = (63, 57) is the Elliptic Curve Discrete Logarithm Problem (ECDLP), which becomes computationally infeasible as the curve grows larger.

### Signing

Sign a message with private key d to produce the pair (r, s). First, the message is hashed into a numeric value h, then the signature values are computed using an ephemeral key k.

```javascript
const message = "Hello, ECDSA!";
const h = toyHash(message, n);   // h = 85
const k = 42n;                   // Ephemeral key (use cryptographic random in production)

const R = scalarMul(k, G, a, p, n); // R = (87, 62)
const r = mod(R.x, n);           // r = 87
const kInv = modInverse(k, n);   // k⁻¹ = 53
const s = mod(kInv * (h + r * d), n); // s = 20

console.log(`h = ${h}`);
console.log(`R = (${R.x}, ${R.y})`);
console.log(`k⁻¹ = ${kInv}  (check: ${k} × ${kInv} mod ${n} = ${mod(k * kInv, n)})`);
console.log(`s = ${kInv} × (${h} + ${r} × ${d}) mod ${n} = ${s}`);
console.log(`Signature (r, s) = (${r}, ${s})`);
```

```
h = 85
R = (87, 62)
k⁻¹ = 53  (check: 42 × 53 mod 89 = 1)
s = 53 × (85 + 87 × 23) mod 89 = 20
Signature (r, s) = (87, 20)
```

**Note:** The ephemeral key `k` must be freshly generated for each signature. Reusing the same `k` across different signatures allows an attacker to solve a system of equations and recover the private key `d`.

### Verification

Verify the message using only the public key Q and signature (r, s). The private key d is not needed.

```javascript
const sInv = modInverse(s, n);          // s⁻¹ = 49
const u1 = mod(h * sInv, n);           // u1 = 71
const u2 = mod(r * sInv, n);           // u2 = 80

const P1 = scalarMul(u1, G, a, p, n);     // P1 = (45, 24)
const P2 = scalarMul(u2, Q, a, p, n);     // P2 = (31, 85)
const Rp = pointAdd(P1, P2, a, p);     // R' = (87, 62)

const valid = !isInfinity(Rp) && mod(Rp.x, n) === r;
console.log(`R' = (${Rp.x}, ${Rp.y})`);
console.log(`R'.x mod n = ${mod(Rp.x, n)},  r = ${r}`);
console.log(`Result: ${valid}`);
```

```
R' = (87, 62)
R'.x mod n = 87,  r = 87
Result: true
```

The x-coordinate of R' matches r. The signature is valid.

### Tamper Detection

Changing one character (`!` → `?`) and verifying with the same signature fails.

```javascript
const tampered = "Hello, ECDSA?";
const hBad = toyHash(tampered, n);        // h' = 26 (original h = 85)

const u1b = mod(hBad * sInv, n);          // u1' = 28
const P1b = scalarMul(u1b, G, a, p, n);
const P2b = scalarMul(u2, Q, a, p, n);       // u2 unchanged
const Rpb = pointAdd(P1b, P2b, a, p);     // R'' = (0, 95)

const validBad = !isInfinity(Rpb) && mod(Rpb.x, n) === r;
console.log(`R'' = (${Rpb.x}, ${Rpb.y})`);
console.log(`R''.x mod n = ${mod(Rpb.x, n)},  r = ${r}`);
console.log(`Result: ${validBad}`);
```

```
R'' = (0, 95)
R''.x mod n = 0,  r = 87
Result: false (tampering detected!)
```

The hash changed from 85 to 26, causing the recovered point's x-coordinate to be 0, which doesn't match r = 87.

---

## Summary

We implemented only four functions: `modInverse`, `pointAdd`, `scalarMul`, and `toyHash`. These are all that's needed for ECDSA signing and verification.

The base point G is determined by searching for a curve point with prime order, but in production it's fixed by specification and doesn't need to be searched each time. The only difference from real P-256 is the curve parameters and the size of the numbers (256-bit) — the algorithm is exactly the same.

In the previous article, the internals of `crypto.subtle.sign()` / `crypto.subtle.verify()` were handled in a single line. In this article, we wrote everything by hand and confirmed what's happening inside the black box.

---

## Full Code

Run the following shell command to save it as `ecdsa-from-scratch.mjs`. For browsers, paste the JavaScript portion (excluding the `cat` and `EOF` lines) into the DevTools Console.

| Environment | How to Run |
|-------------|-----------|
| **Browser** | Paste the JavaScript portion into the DevTools Console |
| **Bun** | `bun ecdsa-from-scratch.mjs` |
| **Node.js** (v19+) | `node ecdsa-from-scratch.mjs` |

```javascript
cat << 'EOF' > ecdsa-from-scratch.mjs
// ============================================================
// ECDSA from Scratch — No libraries, BigInt only
// Run: node ecdsa-from-scratch.mjs / bun ecdsa-from-scratch.mjs
// ============================================================

// --- Modular arithmetic ---
const mod = (a, m) => ((a % m) + m) % m;

const modInverse = (a, m) => {
  a = mod(a, m);
  let [old_r, r] = [a, m];
  let [old_s, s] = [1n, 0n];
  while (r !== 0n) {
    const q = old_r / r;
    [old_r, r] = [r, old_r - q * r];
    [old_s, s] = [s, old_s - q * s];
  }
  if (old_r !== 1n) throw new Error(`No inverse: gcd(${a}, ${m}) = ${old_r}`);
  return mod(old_s, m);
};

// --- Elliptic curve point operations ---
const INFINITY = { x: null, y: null };
const isInfinity = (P) => P.x === null && P.y === null;

const pointAdd = (P, Q, a, p) => {
  if (isInfinity(P)) return Q;
  if (isInfinity(Q)) return P;
  if (P.x === Q.x && mod(P.y + Q.y, p) === 0n) return INFINITY;
  let lam;
  if (P.x === Q.x && P.y === Q.y) {
    lam = mod((3n * P.x * P.x + a) * modInverse(2n * P.y, p), p);
  } else {
    lam = mod((Q.y - P.y) * modInverse(Q.x - P.x, p), p);
  }
  const xr = mod(lam * lam - P.x - Q.x, p);
  const yr = mod(lam * (P.x - xr) - P.y, p);
  return { x: xr, y: yr };
};

const scalarMul = (k, P, a, p, n) => {
  let result = INFINITY;
  let addend = { ...P };
  k = mod(k, n);
  while (k > 0n) {
    if (k & 1n) result = pointAdd(result, addend, a, p);
    addend = pointAdd(addend, addend, a, p);
    k >>= 1n;
  }
  return result;
};

// --- Helper functions ---
const findOrder = (G, a, p) => {
  let P = { ...G };
  // By Hasse's theorem, order ≤ p+1+2√p, so p*4 is a safe upper bound
  for (let i = 2n; i < p * 4n; i++) {
    P = pointAdd(P, G, a, p);
    if (isInfinity(P)) return i;
  }
  return null;
};

const toyHash = (msg, n) => {
  let h = 0n;
  for (let i = 0; i < msg.length; i++) {
    h = mod(h * 31n + BigInt(msg.charCodeAt(i)), n);
  }
  return h === 0n ? 1n : h;
};

// --- Curve parameters ---
const p = 97n;
const a = 1n;
const b = 4n;
const G = { x: 0n, y: 2n };
const fmt = (P) => isInfinity(P) ? "∞" : `(${P.x}, ${P.y})`;

// --- Key generation ---
const n = findOrder(G, a, p);
const d = 23n;
const Q = scalarMul(d, G, a, p, n);
console.log(`[Key Generation]`);
console.log(`  Private key d = ${d}`);
console.log(`  Public key Q = d · G = ${fmt(Q)}`);

// --- Signing ---
const message = "Hello, ECDSA!";
const h = toyHash(message, n);
const k = 42n;
const R = scalarMul(k, G, a, p, n);
const r = mod(R.x, n);
const kInv = modInverse(k, n);
const s = mod(kInv * (h + r * d), n);
console.log(`\n[Signing]`);
console.log(`  Message: "${message}"`);
console.log(`  h = ${h}, k = ${k}`);
console.log(`  R = k · G = ${fmt(R)}`);
console.log(`  r = R.x mod n = ${r}`);
console.log(`  k⁻¹ = ${kInv}  (check: ${k} × ${kInv} mod ${n} = ${mod(k * kInv, n)})`);
console.log(`  s = k⁻¹ × (h + r × d) mod n = ${s}`);
console.log(`  Signature (r, s) = (${r}, ${s})`);

// --- Verification ---
const sInv = modInverse(s, n);
const u1 = mod(h * sInv, n);
const u2 = mod(r * sInv, n);
const P1 = scalarMul(u1, G, a, p, n);
const P2 = scalarMul(u2, Q, a, p, n);
const Rp = pointAdd(P1, P2, a, p);
const valid = !isInfinity(Rp) && mod(Rp.x, n) === r;
console.log(`\n[Verification]`);
console.log(`  s⁻¹ = ${sInv}, u1 = ${u1}, u2 = ${u2}`);
console.log(`  R' = u1·G + u2·Q = ${fmt(Rp)}`);
console.log(`  R'.x mod n = ${mod(Rp.x, n)},  r = ${r}`);
console.log(`  Result: ${valid}`);

// --- Tamper detection ---
const tampered = "Hello, ECDSA?";
const hBad = toyHash(tampered, n);
const u1b = mod(hBad * sInv, n);
const P1b = scalarMul(u1b, G, a, p, n);
const P2b = scalarMul(u2, Q, a, p, n);
const Rpb = pointAdd(P1b, P2b, a, p);
const validBad = !isInfinity(Rpb) && mod(Rpb.x, n) === r;
console.log(`\n[Tamper Detection]`);
console.log(`  Tampered message: "${tampered}"`);
console.log(`  h' = ${hBad} (original h = ${h})`);
console.log(`  R'' = ${fmt(Rpb)}`);
console.log(`  R''.x mod n = ${mod(Rpb.x, n)},  r = ${r}`);
console.log(`  Result: ${validBad}`);
EOF
```
