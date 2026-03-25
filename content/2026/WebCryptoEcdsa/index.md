+++
title = "署名と検証: Web Crypto API で ECDSA を体験する"
date = 2026-03-26
description = "Web Crypto API の crypto.subtle を使い、ECDSA による電子署名の生成と検証をブラウザ・Bun・Node.js で体験する。"
path = "2026/WebCryptoEcdsa"
+++

## はじめに

インターネットの世界では、TLS、SSH、電子メールの署名など、あらゆる場面で暗号技術が使われている。署名・検証、暗号化・復号、鍵交換——これらの用語は日常的に目にするものの、仕組みをきちんと理解しているかと問われると、正直なところ怪しかった。

そんな中、Web Crypto API というものを知った。ブラウザに標準で組み込まれた暗号 API で、外部ライブラリなしに暗号操作を試すことができる。API がシンプルで、コードを書いて動かしながら学ぶのにちょうどよい。

これを機に、いい加減に理解していた暗号技術の基礎を、コードレベルでちゃんと押さえ直そうと思った。この記事では、電子署名（ECDSA）を取り上げ、署名の生成と検証が実際にどう動くかを確認する。

---

## Web Crypto API とは

Web Crypto API はブラウザに標準で組み込まれた暗号 API である。外部ライブラリを追加することなく、鍵の生成、署名、検証、暗号化、復号といった暗号操作を行える。

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

// 鍵ペアをエクスポート
const privateKey = await crypto.subtle.exportKey("jwk", keyPair.privateKey);
const publicKey = await crypto.subtle.exportKey("jwk", keyPair.publicKey);

// 鍵ペアを出力
console.log("秘密鍵:", privateKey);
console.log("公開鍵:", publicKey);

// 2. 署名するデータ
const message = "Hello, WebCrypto!";
const data = new TextEncoder().encode(message);

// 3. 秘密鍵で署名
const signature = await crypto.subtle.sign(
  { name: "ECDSA", hash: "SHA-256" },
  keyPair.privateKey,
  data
);
console.log("署名(Base64):", btoa(String.fromCharCode(...new Uint8Array(signature))));

// 4. 公開鍵で検証（正常データ）
const isValid = await crypto.subtle.verify(
  { name: "ECDSA", hash: "SHA-256" },
  keyPair.publicKey,
  signature,
  data
);
console.log("検証結果:", isValid); // true

// 5. 改ざんデータで検証
const tampered = new TextEncoder().encode("Hello, WebCrypto! (tampered)");
const isValidTampered = await crypto.subtle.verify(
  { name: "ECDSA", hash: "SHA-256" },
  keyPair.publicKey,
  signature,
  tampered
);
console.log("改ざんデータの検証結果:", isValidTampered); // false
EOF
```

実行結果:

```bash
ktaka@dyna:~$ bun ecdsa.mjs
秘密鍵: {
  crv: "P-256",
  d: "g5s4_UgVImhIbZmV5FBhSFk-BhrnK-S4k9KlmAY4ziM",
  ext: true,
  key_ops: [ "sign" ],
  kty: "EC",
  x: "Lqk0ituprTyXDnWPgCoZBog1Gk8u2Tv6UYhbBFhwioc",
  y: "-g--4yIclRm6wkuiB0rAsmlr9heEomAuZb9wY1hR74k",
}
公開鍵: {
  crv: "P-256",
  ext: true,
  key_ops: [ "verify" ],
  kty: "EC",
  x: "Lqk0ituprTyXDnWPgCoZBog1Gk8u2Tv6UYhbBFhwioc",
  y: "-g--4yIclRm6wkuiB0rAsmlr9heEomAuZb9wY1hR74k",
}
署名(Base64): cqYkTGzmYrFeGmIL8M0bCBuNOqEW4oSCpl5ptovLyl8B/qTlQfVL9+FFNgbA5VU5C+82w/YG7fwGcV1FdjlJtg==
検証結果: true
改ざんデータの検証結果: false
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
