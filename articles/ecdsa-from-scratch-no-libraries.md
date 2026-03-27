---
title: "ECDSA の計算をライブラリなしで実装する"
emoji: "🔑"
type: "tech"
topics: ["ecdsa", "cryptography", "javascript", "ellipticcurve"]
published: true
canonical_url: "https://ktaka.blog.ccmp.jp/2026/EcdsaFromScratch"
---

> この記事は [ktaka.blog.ccmp.jp の記事](https://ktaka.blog.ccmp.jp/2026/EcdsaFromScratch) のクロスポストです。

## はじめに

[前回の記事](https://ktaka.blog.ccmp.jp/2026/WebCryptoEcdsa)では、Web Crypto API の `crypto.subtle` を使って ECDSA の署名と検証を体験した。API を呼ぶだけで署名・検証ができたが、内部で何を計算しているかはブラックボックスのままだった。

この記事では、暗号ライブラリを使わず、四則演算と mod だけで ECDSA の署名・検証を実装する。全ステップの中間値を出力し、何が起きているかを確認する。

なお、この記事のコードと解説は AI（Claude）との対話を通じて作成した。小さな曲線を使って全値を 2 桁に収めるアイデアや、中間値を表示して計算過程を追えるようにする構成も、AI との議論の中で生まれたものである。

---

## 方針: 小さな曲線で試す

本物の ECDSA（P-256）では 256bit の巨大な数を扱うが、アルゴリズムは曲線のサイズに依存しない。ここでは `y² = x³ + x + 4 (mod 97)` という小さな曲線を使い、すべての値が 2 桁の整数に収まるようにした。

```javascript
const p = 97n;  // 曲線の法（有限体の素数）
const a = 1n;   // 曲線パラメータ a
const b = 4n;   // 曲線パラメータ b
// 曲線: y² = x³ + ax + b (mod p)
```

※ 数値の末尾の `n` は JavaScript の `BigInt`（任意精度の整数型）を示す。

---

## ECDSA の 3 層構造

ECDSA の署名・検証は、以下の 3 層で構成されている。

| 層 | 内容 | 実装する関数 |
|----|------|-------------|
| 1. モジュラー演算 | mod 演算、モジュラー逆元 | `mod`, `modInverse` |
| 2. 楕円曲線の点の演算 | 点の加算、スカラー倍算 | `pointAdd`, `scalarMul` |
| 3. ECDSA プロトコル | 鍵生成、署名、検証 | 上記の組み合わせ |

これらを下から順に実装していく。

---

## 第 1 層: モジュラー演算

ECDSA の全計算はモジュラー演算（mod）の世界で行われる。必要な演算は 2 つ: mod 演算と、モジュラー逆元である。

### mod 関数

JavaScript の `%` は剰余演算子であり、負の数に対して負の結果を返す（例: `-1n % 3n` → `-1n`）。`((a % m) + m) % m` とすることで、結果を常に `[0, m)` の範囲に収める。

```javascript
const mod = (a, m) => ((a % m) + m) % m;
```

### モジュラー逆元

モジュラー逆元 `k⁻¹` は「`k⁻¹ × k ≡ 1 (mod m)` を満たす整数」で、通常の割り算の代わりに使う。拡張ユークリッド互除法で求められる。

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

例えば `modInverse(37n, 97n)` は `21n` を返す。37 × 21 = 777 = 97 × 8 + 1 なので、確かに 37 × 21 mod 97 = 1 である。

:::details 拡張ユークリッド互除法の仕組み

まず普通のユークリッド互除法で、繰り返し割り算して GCD（最大公約数）を求める。37 と 97 の場合:

```
97 = 2 × 37 + 23
37 = 1 × 23 + 14
23 = 1 × 14 +  9
14 = 1 ×  9 +  5
 9 = 1 ×  5 +  4
 5 = 1 ×  4 +  1  ← 余り 1 = GCD
 4 = 4 ×  1 +  0  ← 終了
```

次に余り 1 から逆にたどり、「37 × ? + 97 × ? = 1」の形に変形する:

```
1 = 5 - 1×4
  = 5 - 1×(9 - 1×5)           = 2×5 - 1×9
  = 2×(14 - 1×9) - 1×9        = 2×14 - 3×9
  = 2×14 - 3×(23 - 1×14)      = 5×14 - 3×23
  = 5×(37 - 1×23) - 3×23      = 5×37 - 8×23
  = 5×37 - 8×(97 - 2×37)      = 21×37 - 8×97
```

つまり `21 × 37 - 8 × 97 = 1` なので、`37 × 21 ≡ 1 (mod 97)`。21 が逆元である。

コード中の `old_r, r` は余りの追跡、`old_s, s` はこの「逆にたどる」係数の計算を同時に行っている。

:::

---

## 第 2 層: 楕円曲線上の点の演算

楕円曲線上の「点の加算」は通常の足し算とは異なる幾何学的な操作である。無限遠点（単位元）の扱いも必要になる。

```javascript
const INFINITY = { x: null, y: null };
const isInfinity = (P) => P.x === null && P.y === null;
```

### 点の加算 P + Q

2 点を通る直線が曲線と交わる第 3 の点を x 軸で反転する。P = Q の場合は接線を使う（点の 2 倍）。式は直線と曲線の方程式を連立して代数的に導かれたもので、四則演算だけで構成されているため、mod p の世界でもそのまま成り立つ。ただし割り算はモジュラー逆元を掛ける操作に置き換え、各計算の結果に mod p を適用する。

```javascript
const pointAdd = (P, Q, a, p) => {
  if (isInfinity(P)) return Q;
  if (isInfinity(Q)) return P;
  if (P.x === Q.x && mod(P.y + Q.y, p) === 0n) return INFINITY;

  // lam = 直線の傾き（点の2倍の場合は接線の傾き）
  let lam;
  if (P.x === Q.x && P.y === Q.y) {
    // 点の2倍: λ = (3x² + a) / (2y)
    lam = mod((3n * P.x * P.x + a) * modInverse(2n * P.y, p), p);
  } else {
    // 異なる2点の加算: λ = (y₂ - y₁) / (x₂ - x₁)
    lam = mod((Q.y - P.y) * modInverse(Q.x - P.x, p), p);
  }
  // 直線と曲線の第3の交点を求め、x軸で反転
  const xr = mod(lam * lam - P.x - Q.x, p);
  const yr = mod(lam * (P.x - xr) - P.y, p);
  return { x: xr, y: yr };
};
```

### スカラー倍算 k · P

G を k 回足し合わせる操作。愚直に k 回ループすると遅いので、ダブル＆アド法を使う。例えば k = 42 は 2 進数で `101010` なので、`42·G = 32·G + 8·G + 2·G` と分解できる。G を繰り返し 2 倍しながら、ビットが 1 の位置で加算することで高速に計算する。引数の `n` は群の位数（曲線上の点の個数に関係する値）で、後述の `findOrder` で求める。

```javascript
const scalarMul = (k, P, a, p, n) => {
  let result = INFINITY;
  let addend = { ...P };  // G, 2G, 4G, 8G, ... と2倍されていく
  k = mod(k, n);
  while (k > 0n) {
    if (k & 1n) result = pointAdd(result, addend, a, p);  // ビットが1なら加算
    addend = pointAdd(addend, addend, a, p);  // 毎回2倍
    k >>= 1n;  // 次のビットへ
  }
  return result;
};
```

---

## 補助関数

ベースポイント G の位数（`n · G = ∞` となる最小の n）を求める関数と、SHA-256 の代わりに使う簡易ハッシュ関数:

```javascript
const findOrder = (G, a, p) => {
  let P = { ...G };
  // Hasseの定理より位数 ≤ p+1+2√p なので p*4 は十分な上限
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

## 曲線パラメータとベースポイント G

本物の P-256 では、NIST が曲線パラメータ (p, a, b) とベースポイント G の座標を仕様書で規定しており、各実装はその値をそのまま使う。ここでは学習目的で、ベースポイント G がどうやって決まるかを見ていく。

:::details 参考: P-256 の実際のパラメータ

```
p   = 0xFFFFFFFF00000001000000000000000000000000FFFFFFFFFFFFFFFFFFFFFFFF
a   = 0xFFFFFFFF00000001000000000000000000000000FFFFFFFFFFFFFFFFFFFFFFFC
b   = 0x5AC635D8AA3A93E7B3EBBD55769886BC651D06B0CC53B0F63BCE3C3E27D2604B
G.x = 0x6B17D1F2E12C4247F8BCE6E563A440F277037D812DEB33A0F4A13945D898C296
G.y = 0x4FE342E2FE1A7F9B8EE7EB4A7C0F9E162BCE33576B315ECECBB6406837BF51F5
n   = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551
```

すべて 256bit の値である。この記事のトイカーブ（p=97, n=89）とはスケールが異なるが、アルゴリズムは全く同じである。

出典: [NIST SP 800-186 — Recommendations for Discrete Logarithm-based Cryptography: Elliptic Curve Domain Parameters](https://csrc.nist.gov/pubs/sp/800/186/final)

:::

### 曲線上の点を見つける

x に 0, 1, 2, ... を順に代入して `x³ + ax + b mod p` を計算し、その値が `y²` になる y が存在するか調べる。

```
x = 0:  x³+x+4 mod 97 =  4  →  y² ≡  4 (mod 97)  →  y = 2, 95   →  (0,2), (0,95)
x = 1:  x³+x+4 mod 97 =  6  →  y² ≡  6 (mod 97)  →  y = 43, 54  →  (1,43), (1,54)
x = 2:  x³+x+4 mod 97 = 14  →  y² ≡ 14 (mod 97)  →  平方根なし（点が存在しない）
x = 3:  x³+x+4 mod 97 = 34  →  y² ≡ 34 (mod 97)  →  平方根なし（点が存在しない）
x = 4:  x³+x+4 mod 97 = 72  →  y² ≡ 72 (mod 97)  →  y = 13, 84  →  (4,13), (4,84)
```

見つかるときは常に y と p−y のペア（2 + 95 = 97 = p）で、x 軸に対して対称な 2 点になる。この曲線には全部で 88 個の点がある（+ 無限遠点 ∞）。

### 位数が素数の点を選ぶ

ECDSA では G の位数（`n · G = ∞` となる最小の n）が素数である必要がある。

```javascript
const isPrime = (n) => {
  if (n < 2n) return false;
  for (let d = 2n; d * d <= n; d++) {
    if (n % d === 0n) return false;
  }
  return true;
};

// 曲線上の点を探索し、位数が素数の点を見つける
for (let x = 0n; x < p; x++) {
  const rhs = mod(x * x * x + a * x + b, p);
  for (let y = 0n; y < p; y++) {
    if (mod(y * y, p) !== rhs) continue;
    const candidate = { x, y };
    const order = findOrder(candidate, a, p);
    if (isPrime(order)) {
      console.log(`G = (${x}, ${y}), 位数 n = ${order}`);
      break;
    }
  }
}
```

群の位数が 89（素数）なので、全 88 点の位数がすべて 89 であり、どの点を G に選んでもよい。今回は G = (0, 2) を採用した。

今回使う曲線パラメータとベースポイントをまとめると:

```javascript
const p = 97n;
const a = 1n;
const b = 4n;
const G = { x: 0n, y: 2n };
```

G が曲線上にあることの検算: 2² mod 97 = 4、0³ + 1·0 + 4 mod 97 = 4。一致する。

---

## 第 3 層: ECDSA プロトコル

ECDSA プロトコルは鍵生成・署名・検証の 3 ステップからなる。

```
鍵生成:  Q = d · G を計算
         Qからdを推測することは困難（離散対数問題）

署名:  {d, k, h, (G, a, p, n)}  →  (r, s)　を計算
検証:  {Q, s, h', (G, a, p, n)} →  r'　を計算

d: 秘密鍵, k: 一時鍵, Q: 公開鍵
r, s: シグネチャ
h, h': メッセージのハッシュ
G, a, p, n: 曲線パラメータ

h' == h（改ざんなし）→ r' == r（検証成功）
h' ≠ h（改ざんあり）→ r' ≠ r（検証失敗）
```

:::details なぜ同じ r に到達するのか

署名と検証はそれぞれ以下を計算する:

```
署名側: R = k·G
        r = R.x mod n
        s = k⁻¹·(h + r·d) mod n
        → シグネチャ (r, s)

検証側: R' = s⁻¹·h'·G + s⁻¹·r·Q
        r' = R'.x mod n
        → r' == r なら検証成功
```

`h' == h` のとき、検証側の点の計算を展開する:

```
R' = s⁻¹·h'·G + s⁻¹·r·Q
   = s⁻¹·h·G + s⁻¹·r·Q       ← h' = h を代入
   = s⁻¹·h·G + s⁻¹·r·(d·G)   ← Q = d·G を代入
   = (s⁻¹·h + s⁻¹·r·d)·G
   = s⁻¹·(h + r·d)·G
   = k·G                       ← s = k⁻¹·(h+r·d) より s⁻¹·(h+r·d) = k

r' = R'.x mod n
   = (k·G).x mod n
   = r                         ← 署名側と同じ
```

よって、`h' == h` のとき `r' == r` となる。

:::

以下、コードで各ステップを確認する。

### 鍵生成

秘密鍵 d を選び、公開鍵 Q = d · G を計算する。d は 1 から n-1 の範囲（この曲線では 1〜88）なら何でもよい。

```javascript
// G=(0,2), a=1, p=97 は前セクションで決定済み
const n = findOrder(G, a, p); // n = 89
const d = 23n;                // 秘密鍵 (1 ≤ d ≤ n-1)
const Q = scalarMul(d, G, a, p, n); // 公開鍵 Q = d · G
console.log(`秘密鍵 d = ${d}`);
console.log(`公開鍵 Q = (${Q.x}, ${Q.y})`);
```

```
秘密鍵 d = 23
公開鍵 Q = (63, 57)
```

d の値を変えると Q も変わる:

```
d = 22  →  Q = (96, 83)
d = 23  →  Q = (63, 57)   ← 今回のデモ
d = 24  →  Q = (56, 3)
d = 25  →  Q = (38, 77)
```

公開鍵 Q = (63, 57) から秘密鍵 d = 23 を逆算するのは、楕円曲線離散対数問題（ECDLP）であり、曲線が大きくなると計算量的に困難になる。

### 署名

秘密鍵 d でメッセージに署名して (r, s) のペアを生成する。まずメッセージをハッシュして数値 h に変換し、一時鍵 k を使って署名値を計算する。

```javascript
const message = "Hello, ECDSA!";
const h = toyHash(message, n);   // h = 85
const k = 42n;                   // 一時鍵（本番では署名ごとに暗号論的乱数を生成）

const R = scalarMul(k, G, a, p, n); // R = (87, 62)
const r = mod(R.x, n);           // r = 87
const kInv = modInverse(k, n);   // k⁻¹ = 53
const s = mod(kInv * (h + r * d), n); // s = 20

console.log(`h = ${h}`);
console.log(`R = (${R.x}, ${R.y})`);
console.log(`k⁻¹ = ${kInv}  (検算: ${k} × ${kInv} mod ${n} = ${mod(k * kInv, n)})`);
console.log(`s = ${kInv} × (${h} + ${r} × ${d}) mod ${n} = ${s}`);
console.log(`署名 (r, s) = (${r}, ${s})`);
```

```
h = 85
R = (87, 62)
k⁻¹ = 53  (検算: 42 × 53 mod 89 = 1)
s = 53 × (85 + 87 × 23) mod 89 = 20
署名 (r, s) = (87, 20)
```

**注意:** 一時鍵 `k` は署名のたびに新しい乱数を生成しなければならない。同じ `k` を異なる署名で使い回すと、2 つの署名から連立方程式を解いて秘密鍵 `d` を算出できてしまう。

### 検証

公開鍵 Q と署名 (r, s) だけで、メッセージの正当性を検証する。秘密鍵 d は不要。

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
console.log(`検証結果: ${valid}`);
```

```
R' = (87, 62)
R'.x mod n = 87,  r = 87
検証結果: true
```

R' の x 座標が r と一致した。署名は正当である。

### 改ざん検知

メッセージを 1 文字変えて（`!` → `?`）同じ署名で検証すると、失敗する。

```javascript
const tampered = "Hello, ECDSA?";
const hBad = toyHash(tampered, n);        // h' = 26 (元の h = 85)

const u1b = mod(hBad * sInv, n);          // u1' = 28
const P1b = scalarMul(u1b, G, a, p, n);
const P2b = scalarMul(u2, Q, a, p, n);       // u2 は変わらず
const Rpb = pointAdd(P1b, P2b, a, p);     // R'' = (0, 95)

const validBad = !isInfinity(Rpb) && mod(Rpb.x, n) === r;
console.log(`R'' = (${Rpb.x}, ${Rpb.y})`);
console.log(`R''.x mod n = ${mod(Rpb.x, n)},  r = ${r}`);
console.log(`検証結果: ${validBad}`);
```

```
R'' = (0, 95)
R''.x mod n = 0,  r = 87
検証結果: false (改ざん検知!)
```

ハッシュ値が 85 → 26 に変わったことで、復元された点の x 座標が 0 になり、r = 87 と一致しなくなった。

---

## まとめ

実装した関数は 4 つだけである: `modInverse`、`pointAdd`、`scalarMul`、`toyHash`。これらの組み合わせで ECDSA の署名・検証が完結する。

ベースポイント G は曲線上の点を探索して位数が素数のものを選ぶことで決まるが、本番では仕様として固定されており、毎回探索するものではない。本物の P-256 との違いは曲線パラメータと数値のサイズ（256bit）だけで、アルゴリズムは全く同じである。

前回は `crypto.subtle.sign()` / `crypto.subtle.verify()` の 1 行で済ませていた処理の中身を、今回はすべて手で書いた。ブラックボックスの中で何が起きているかを確認できたと思う。

---

## 全体コード

以下のシェルコマンドを実行すると `ecdsa-from-scratch.mjs` として保存される。ブラウザの場合は `cat` 行と `EOF` 行を除いた JavaScript 部分を DevTools の Console に貼り付ける。

| 環境 | 実行方法 |
|------|----------|
| **ブラウザ** | DevTools の Console に JavaScript 部分をコピペして実行 |
| **Bun** | `bun ecdsa-from-scratch.mjs` |
| **Node.js** (v19+) | `node ecdsa-from-scratch.mjs` |

```javascript
cat << 'EOF' > ecdsa-from-scratch.mjs
// ============================================================
// ECDSA from Scratch — ライブラリなし・BigInt のみ
// 実行: node ecdsa-from-scratch.mjs / bun ecdsa-from-scratch.mjs
// ============================================================

// --- モジュラー演算 ---
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

// --- 楕円曲線上の点の演算 ---
const INFINITY = { x: null, y: null };
const isInfinity = (P) => P.x === null && P.y === null;

const pointAdd = (P, Q, a, p) => {
  if (isInfinity(P)) return Q;
  if (isInfinity(Q)) return P;
  if (P.x === Q.x && mod(P.y + Q.y, p) === 0n) return INFINITY;
  // lam = 直線の傾き（点の2倍の場合は接線の傾き）
  let lam;
  if (P.x === Q.x && P.y === Q.y) {
    lam = mod((3n * P.x * P.x + a) * modInverse(2n * P.y, p), p);
  } else {
    lam = mod((Q.y - P.y) * modInverse(Q.x - P.x, p), p);
  }
  // 直線と曲線の第3の交点を求め、x軸で反転
  const xr = mod(lam * lam - P.x - Q.x, p);
  const yr = mod(lam * (P.x - xr) - P.y, p);
  return { x: xr, y: yr };
};

const scalarMul = (k, P, a, p, n) => {
  let result = INFINITY;
  let addend = { ...P };  // G, 2G, 4G, 8G, ... と2倍されていく
  k = mod(k, n);
  while (k > 0n) {
    if (k & 1n) result = pointAdd(result, addend, a, p);  // ビットが1なら加算
    addend = pointAdd(addend, addend, a, p);  // 毎回2倍
    k >>= 1n;  // 次のビットへ
  }
  return result;
};

// --- 補助関数 ---
const findOrder = (G, a, p) => {
  let P = { ...G };
  // Hasseの定理より位数 ≤ p+1+2√p なので p*4 は十分な上限
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

// --- 曲線パラメータ ---
const p = 97n;
const a = 1n;
const b = 4n;
const G = { x: 0n, y: 2n };
const fmt = (P) => isInfinity(P) ? "∞" : `(${P.x}, ${P.y})`;

// --- 鍵生成 ---
const n = findOrder(G, a, p);
const d = 23n;
const Q = scalarMul(d, G, a, p, n);
console.log(`【鍵生成】`);
console.log(`  秘密鍵 d = ${d}`);
console.log(`  公開鍵 Q = d · G = ${fmt(Q)}`);

// --- 署名 ---
const message = "Hello, ECDSA!";
const h = toyHash(message, n);
const k = 42n;
const R = scalarMul(k, G, a, p, n);
const r = mod(R.x, n);
const kInv = modInverse(k, n);
const s = mod(kInv * (h + r * d), n);
console.log(`\n【署名】`);
console.log(`  メッセージ: "${message}"`);
console.log(`  h = ${h}, k = ${k}`);
console.log(`  R = k · G = ${fmt(R)}`);
console.log(`  r = R.x mod n = ${r}`);
console.log(`  k⁻¹ = ${kInv}  (検算: ${k} × ${kInv} mod ${n} = ${mod(k * kInv, n)})`);
console.log(`  s = k⁻¹ × (h + r × d) mod n = ${s}`);
console.log(`  署名 (r, s) = (${r}, ${s})`);

// --- 検証 ---
const sInv = modInverse(s, n);
const u1 = mod(h * sInv, n);
const u2 = mod(r * sInv, n);
const P1 = scalarMul(u1, G, a, p, n);
const P2 = scalarMul(u2, Q, a, p, n);
const Rp = pointAdd(P1, P2, a, p);
const valid = !isInfinity(Rp) && mod(Rp.x, n) === r;
console.log(`\n【検証】`);
console.log(`  s⁻¹ = ${sInv}, u1 = ${u1}, u2 = ${u2}`);
console.log(`  R' = u1·G + u2·Q = ${fmt(Rp)}`);
console.log(`  R'.x mod n = ${mod(Rp.x, n)},  r = ${r}`);
console.log(`  検証結果: ${valid}`);

// --- 改ざん検知 ---
const tampered = "Hello, ECDSA?";
const hBad = toyHash(tampered, n);
const u1b = mod(hBad * sInv, n);
const P1b = scalarMul(u1b, G, a, p, n);
const P2b = scalarMul(u2, Q, a, p, n);
const Rpb = pointAdd(P1b, P2b, a, p);
const validBad = !isInfinity(Rpb) && mod(Rpb.x, n) === r;
console.log(`\n【改ざん検知】`);
console.log(`  改ざんメッセージ: "${tampered}"`);
console.log(`  h' = ${hBad} (元の h = ${h})`);
console.log(`  R'' = ${fmt(Rpb)}`);
console.log(`  R''.x mod n = ${mod(Rpb.x, n)},  r = ${r}`);
console.log(`  検証結果: ${validBad}`);
EOF
```
