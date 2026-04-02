---
title: "Web Crypto API で ECDSA 署名・検証を理解する"
tags:
  - "ECDSA"
  - "WebCryptoAPI"
  - "JavaScript"
  - "暗号"
  - "セキュリティ"
private: false
updated_at: ""
id: null
organization_url_name: null
slide: false
ignorePublish: false
---

> この記事は [ktaka.blog.ccmp.jp の記事](https://ktaka.blog.ccmp.jp/2026/WebCryptoEcdsa) のクロスポストです。

## はじめに

インターネットの世界では、TLS、SSH、電子メールの署名など、あらゆる場面で暗号技術が使われている。署名・検証、暗号化・復号、鍵交換——これらの用語は日常的に目にするものの、仕組みをきちんと理解しているかと問われると、正直なところ怪しかった。

そんな中、Web Crypto API というものを知った。ブラウザに標準で組み込まれた暗号 API で、外部ライブラリなしに暗号操作を試すことができる。API がシンプルで、コードを書いて動かしながら学ぶのにちょうどよい。

これを機に、いい加減に理解していた暗号技術の基礎を、コードレベルでちゃんと押さえ直そうと思った。この記事では、電子署名（ECDSA）を取り上げ、署名の生成と検証が実際にどう動くかを確認する。

---

## Web Crypto API とは

[Web Crypto API](https://developer.mozilla.org/ja/docs/Web/API/Web_Crypto_API) はブラウザに標準で組み込まれた暗号 API である。外部ライブラリを追加することなく、鍵の生成、署名、検証、暗号化、復号といった暗号操作を行える。

すべての操作は `crypto.subtle` オブジェクトを通じて呼び出す。

| メソッド | 用途 |
|----------|------|
| `crypto.subtle.generateKey()` | 鍵ペア・共通鍵の生成 |
| `crypto.subtle.sign()` | 秘密鍵で署名 |
| `crypto.subtle.verify()` | 公開鍵で検証 |
| `crypto.subtle.encrypt()` | 暗号化 |
| `crypto.subtle.decrypt()` | 復号 |
| `crypto.subtle.deriveKey()` | 鍵交換から共通鍵を導出 |
| `crypto.subtle.exportKey()` | 鍵を JWK 等の形式でエクスポート |
| `crypto.subtle.importKey()` | 外部の鍵をインポート |

各メソッドは `Promise` を返すため、`await` で結果を受け取る。今回は `generateKey`、`sign`、`verify` の 3 つを使う。

`generateKey` で指定できる主なアルゴリズム:

| アルゴリズム | 種類 | 用途 |
|-------------|------|------|
| **ECDSA** | 楕円曲線（P-256 等） | 署名・検証 |
| **RSA-OAEP** | RSA | 暗号化・復号 |
| **AES-GCM** | 共通鍵 | 暗号化・復号（認証付き） |
| **ECDH** | 楕円曲線（P-256 等） | 鍵交換 |
| **HMAC** | 共通鍵 | メッセージ認証 |

ブラウザだけでなく、Bun や Node.js (v19+) でも同じ `crypto.subtle` が利用できるため、サーバーサイドでも同じコードがそのまま動作する。

---

## 電子署名とは

電子署名は「秘密鍵で署名し、公開鍵で検証する」仕組みである。署名者だけが署名を生成でき、誰でもその正当性を確認できる。

| 操作 | 使う鍵 | 意味 |
|------|--------|------|
| 署名 | **秘密鍵** | 自分が作成したと証明する |
| 検証 | **公開鍵** | 誰でも正当性を確認できる |

この記事では、Web Crypto API を使って ECDSA（楕円曲線デジタル署名アルゴリズム）で署名と検証を体験する。

---

## コード: 鍵ペア生成 → 署名 → 検証

以下のシェルコマンドを実行すると `ecdsa.mjs` として保存される。ブラウザの場合は `cat` 行と `EOF` 行を除いた JavaScript 部分を DevTools の Console に貼り付ける。

| 環境 | 実行方法 |
|------|----------|
| **ブラウザ** | DevTools の Console に JavaScript 部分をコピペして実行 |
| **Bun** | `bun ecdsa.mjs` |
| **Node.js** (v19+) | `node ecdsa.mjs` |

```javascript
cat << 'EOF' > ecdsa.mjs

// 1. 鍵ペア生成（ECDSA, P-256）
const keyPair = await crypto.subtle.generateKey(
  { name: "ECDSA", namedCurve: "P-256" },
  true, // extractable: true で鍵をエクスポート可能（本番環境では false にすべき）
  ["sign", "verify"]
);

// 2. 署名するデータ
const message = "Hello, WebCrypto!";
const data = new TextEncoder().encode(message);

// 3. 秘密鍵で署名
const signature = await crypto.subtle.sign(
  { name: "ECDSA", hash: "SHA-256" },
  keyPair.privateKey,
  data
);

// 4. 公開鍵で検証（正常データ）
const isValid = await crypto.subtle.verify(
  { name: "ECDSA", hash: "SHA-256" },
  keyPair.publicKey,
  signature,
  data
);

// 5. 改ざんデータで検証
const tamperedMessage = "Hello, WebCrypto! (tampered)";
const tampered = new TextEncoder().encode(tamperedMessage);
const isValidTampered = await crypto.subtle.verify(
  { name: "ECDSA", hash: "SHA-256" },
  keyPair.publicKey,
  signature,
  tampered
);

// 鍵ペアをエクスポート
const privateKey = await crypto.subtle.exportKey("jwk", keyPair.privateKey);
const publicKey = await crypto.subtle.exportKey("jwk", keyPair.publicKey);

// 鍵ペアを出力
console.log("鍵ペア生成:\n秘密鍵:", privateKey);
console.log("公開鍵:", publicKey);

console.log("\n署名:\nデータ:", message);
console.log("シグネチャ(Base64):", btoa(String.fromCharCode(...new Uint8Array(signature))));

console.log("\n検証:\nデータ:", message);
console.log("検証結果:", isValid); // true

console.log("\nデータ改ざん→検証:\nデータ:", tamperedMessage);
console.log("検証結果:", isValidTampered); // false
EOF
```

実行結果:

```bash
$ bun ecdsa.mjs
鍵ペア生成:
秘密鍵: {
  crv: "P-256",
  d: "qTk9mKRBkX5MCnNzGeCvg5sO1vAWe0FLRXHse7QzSlQ",
  ext: true,
  key_ops: [ "sign" ],
  kty: "EC",
  x: "lWH4MQwp7VEMqAKxk_DYef1_ZY4lVciws4nj1wwFANE",
  y: "c_aEH9x91cYmuaatRW5Nys6uFHDBadDZA4IJuPLVQCY",
}
公開鍵: {
  crv: "P-256",
  ext: true,
  key_ops: [ "verify" ],
  kty: "EC",
  x: "lWH4MQwp7VEMqAKxk_DYef1_ZY4lVciws4nj1wwFANE",
  y: "c_aEH9x91cYmuaatRW5Nys6uFHDBadDZA4IJuPLVQCY",
}

署名:
データ: Hello, WebCrypto!
シグネチャ(Base64): j3z3keEwOxWWl/7kJ9vWphyQYsY/W78TlCB/b0OuN4jlWCAXmWVwOD9DYyk54C3NG/eZblKt6cNYMf6rg24gUw==

検証:
データ: Hello, WebCrypto!
検証結果: true

データ改ざん→検証:
データ: Hello, WebCrypto! (tampered)
検証結果: false
```

コードでは、まず ECDSA の鍵ペアを生成し、秘密鍵でデータに署名してシグネチャ（署名データ、コード中の `signature`）を得ている。公開鍵とデータを使ってシグネチャを検証すると、元のデータでは `true`、改ざんしたデータでは `false` が返る。データが 1 バイトでも変わればシグネチャとの整合性が崩れるため、改ざんを検知できる。そして公開鍵からシグネチャを偽造することはできないため、「秘密鍵の所有者が署名した」ことを第三者が確認できる仕組みになっている。

---

## ポイント

- **ECDSA は署名専用**。暗号化・復号はできない。暗号化には別のアルゴリズムを使う
- **`extractable: false`** にすると秘密鍵をエクスポートできなくなる。本番環境ではこの設定が推奨される
- **`P-256`（secp256r1）** は Web やモバイルで広く使われている曲線である。TLS、SSH、Passkey でも採用されている

---

## まとめ

Web Crypto API はブラウザに標準で組み込まれた暗号 API で、ブラウザコンソール、Bun、Node.js で簡単にコードを試すことができる。`crypto.subtle` を使い、ECDSA による電子署名の生成と検証を確認した。秘密鍵で署名し、公開鍵で検証するという非対称暗号の基本を、簡単に確認できることがわかった。

---

<details>
<summary>付録: ECDSA の署名・検証で何を計算しているか</summary>

**鍵ペア生成:**

1. ランダムな整数 `d` を生成（`1 ≤ d ≤ n-1`、n は曲線の位数）→ これが**秘密鍵**
2. 楕円曲線上の点を計算: `Q = d · G`（G は曲線の基準点）→ これが**公開鍵**

秘密鍵はただの乱数であり、公開鍵はそこから楕円曲線上のスカラー倍算で導出される点である。`Q` と `G` から `d` を逆算することは極めて困難なため、公開鍵から秘密鍵を割り出すことはできない。

**署名（秘密鍵側）:**

1. データをハッシュする: `h = SHA-256(data)`
2. ランダムな数 `k` を生成
3. 楕円曲線上の点を計算: `R = k · G`（G は曲線の基準点）
4. `r = R.x mod n`（R の x 座標）
5. `s = k⁻¹ × (h + r × 秘密鍵) mod n`
6. シグネチャは `(r, s)` のペア

**検証（公開鍵側）:**

1. データをハッシュする: `h = SHA-256(data)`
2. `u1 = h × s⁻¹ mod n`
3. `u2 = r × s⁻¹ mod n`
4. 楕円曲線上の点を復元: `R' = u1 · G + u2 · 公開鍵`
5. `R'.x mod n == r` なら `true`

検証では、データのハッシュ・シグネチャの `s`・公開鍵から楕円曲線上の点を復元し、その x 座標がシグネチャの `r` と一致するかを確認している。

**楕円曲線上の「点の加算」と「スカラー倍算」:**

`k · G` は、楕円曲線上の点 G を k 回足し合わせた点である。

楕円曲線上の点の加算は、通常の足し算とは異なる幾何学的な操作である。

点の加算（P + Q）:
1. 曲線上の 2 点 P, Q を通る直線を引く
2. その直線が曲線と交わる第 3 の点を見つける
3. その点を x 軸で反転 → これが `P + Q`

点の 2 倍（P + P）:
1. P における接線を引く
2. 接線が曲線と交わる点を見つける
3. x 軸で反転 → これが `2P`

スカラー倍算 `k · G` は、この加算を k 回繰り返す操作である（`G + G + G + ... + G`）。実際には「ダブル＆アド」という手法で高速に計算できる。

暗号として成り立つ理由:
- `k` と `G` から `k · G` を計算するのは**高速**
- `G` と `k · G` から `k` を逆算するのは**極めて困難**（楕円曲線離散対数問題）

この一方向性が ECDSA の安全性の基盤になっている。

**`k⁻¹` について:**

`k⁻¹` は `k` のモジュラー逆元（`k⁻¹ × k ≡ 1 (mod n)` を満たす整数）である。通常の割り算（`1/k`）とは異なり、`mod n` の世界で整数のまま「割り算」に相当する操作を行う。

参考:
- [Wikipedia — Elliptic Curve Digital Signature Algorithm](https://en.wikipedia.org/wiki/Elliptic_Curve_Digital_Signature_Algorithm)
- [Practical Cryptography — ECDSA: Sign / Verify](https://cryptobook.nakov.com/digital-signatures/ecdsa-sign-verify-messages)
- [Andrea Corbellini — Elliptic Curve Cryptography: ECDH and ECDSA](https://andrea.corbellini.name/2015/05/30/elliptic-curve-cryptography-ecdh-and-ecdsa/)
</details>
