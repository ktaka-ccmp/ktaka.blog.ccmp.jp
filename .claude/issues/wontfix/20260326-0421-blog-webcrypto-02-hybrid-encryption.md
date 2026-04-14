# Issue: ブログ記事 — 暗号化と鍵交換: ハイブリッド暗号を体験する

## Table of Contents

- [Description](#description)
- [Related Issues](#related-issues)
- [Approach](#approach)
- [Related Files](#related-files)
- [Implementation Tasks](#implementation-tasks)
- [Decision Log](#decision-log)
- [Resolution](#resolution)

## ID: 20260326-0421

## Created: 2026-03-26-04-19

## Closed: 2026-04-15

## Status: wontfix

## Priority: high

## Difficulty: small

## Description

Web Crypto API シリーズ。RSA-OAEP で鍵を包み、AES-GCM でデータを暗号化するハイブリッド暗号を実装する。

**目的:** なぜ公開鍵暗号と共通鍵暗号を組み合わせるのか理解する
**結論:** 公開鍵暗号は遅いので「鍵だけ」暗号化し、データ本体は高速な共通鍵暗号で暗号化する

**前提知識:** ECDSA の記事（公開鍵・秘密鍵の概念）

## Related Issues

- `20260326-0419` ブログシリーズ — Web Crypto API で学ぶ暗号技術 (parent)
- `20260326-0420` 署名と検証 — ECDSA を体験する (previous)
- `20260326-0422` TLS 1.2 ハンドシェイクを再現する (next)

## Approach

### 素材

`~/GitHub/daily-journal/ktaka/2026/0324.md` の以下の部分:

- **L100〜L175 付近**: RSA-OAEP 暗号化・復号のコード（鍵ペア生成、encrypt/decrypt）
- **L175〜L220 付近**: AES-GCM 暗号化・復号（generateKey、IV 生成、encrypt/decrypt）
- **L220〜L270 付近**: ハイブリッド暗号パターン（AES 鍵を RSA で包む）、DPoP との関係

### 記事構成案

1. **導入** — 前回は署名（認証）を学んだ。今回は暗号化（秘匿）
2. **RSA-OAEP で暗号化・復号** — 公開鍵で暗号化、秘密鍵で復号するコード
3. **AES-GCM で暗号化・復号** — 共通鍵 + IV で高速暗号化
4. **なぜ両方必要か？（ハイブリッド暗号）** — RSA は遅い＆サイズ制限 → AES 鍵だけ RSA で包む
5. **まとめ** — TLS もこの仕組みを使っている（TLS 記事への伏線）

## Related Files

- `~/GitHub/daily-journal/ktaka/2026/0324.md` L100〜L270 付近 — RSA-OAEP、AES-GCM、ハイブリッド暗号

## Implementation Tasks

- [ ] 記事ファイル作成
- [ ] コードの動作確認
- [ ] `zola serve` でプレビュー確認

## Decision Log

<!-- APPEND-ONLY: Do not edit or delete existing entries. Add new entries at the bottom. -->

### 2026-03-26: RSA-OAEP と AES-GCM を1記事にまとめる

- Context: RSA-OAEP 単体と AES-GCM 単体で2記事にする案もあった
- Decision: ハイブリッド暗号の「なぜ両方必要か」が結論なので1記事にまとめる
- Reason: 片方だけでは「だから何？」になる。組み合わせる理由が結論として明確

### 2026-03-26: コードは Bun / Node.js でも実行可能と明記

- Context: ブラウザ DevTools のみを想定していた
- Decision: 毎回「ブラウザでも Bun でも Node.js でも動く」と明記する
- Reason: Bun も crypto.subtle をサポートしている。実行環境の選択肢を増やす

### 2026-04-15: 導入の主旨を確定

- Context: 第1回（ECDSA）との対比をどう書くか
- Decision: 「前回は公開鍵暗号の署名・検証を体験した。今回は同じ公開鍵暗号のもう一つの用途、暗号化・復号を扱う」という流れにする
- Reason: 公開鍵暗号の2大用途（署名 vs 暗号化）を対比させることで位置づけが明確になる。「公開鍵認証」は署名側の話なので、この記事は「秘匿」が目的であると区別する

### 2026-04-15: ECDSA が署名専用であることを導入で明示する

- Context: 前回記事（ECDSA）との橋渡しをどう書くか
- Decision: 導入で「ECDSA は署名専用であり暗号化はできない」と明示し、だから RSA-OAEP + AES-GCM が必要という流れにする
- Reason: ECDSA を使えない理由を言わないと「なぜ別のアルゴリズムを使うのか」が唐突になる

### 2026-04-15: ECDH はこの記事では扱わない

- Context: 楕円曲線で鍵交換する ECDH も暗号化関連アルゴリズムだが、この記事に含めるか
- Decision: この記事では扱わない。TLS 1.3 記事（第3.5回）で自然に登場するのでそこに委ねる
- Reason: この記事のテーマは「RSA-OAEP + AES-GCM のハイブリッド暗号」に絞る。ECDH は「鍵交換」であり暗号化とは別の用途なので混ぜると焦点がぼやける

### 2026-04-15: ハイブリッド暗号の説明方針を確定

- Context: 「ハイブリッド暗号」という言葉の意味を記事中で明示する必要がある
- Decision: RSA-OAEP（公開鍵暗号）で AES 共通鍵を暗号化し、AES-GCM（共通鍵暗号）でデータ本体を暗号化する、という2段構造として説明する。以下のフローを記事に含める：
  ```
  AES共通鍵を生成
    ↓
  データ本体 → AES-GCM で暗号化（速い）
  AES共通鍵 → RSA-OAEP で暗号化（鍵だけなのでサイズ問題なし）
    ↓
  暗号化済みAES鍵 + 暗号化済みデータを送信
  ```
- Reason: 「ハイブリッド」の意味が曖昧なまま進むと結論が伝わらない。RSA 単体の限界（遅い・サイズ制限）と AES 単体の限界（鍵配送問題）を対比させることで「なぜ組み合わせるか」が明確になる

### 2026-04-15: RSA-OAEP をこのシリーズで扱う必要がないと判断、記事を deferred に

- Context: TLS/SSH/Passkey のどれも RSA-OAEP（公開鍵暗号化）を使っておらず、ECDH（鍵交換）と ECDSA（署名）が主役。RSA-OAEP はシリーズの後続記事で登場しない
- Decision: この記事を wontfix に移動。JP ドラフトはイシューに保存。シリーズは ECDSA 記事の次に TLS 1.2 へ直行する
- Reason: 「道具の説明が先」という構成は読者の興味を失わせやすい。アプリケーション（TLS/SSH）の文脈で必要な暗号プリミティブを説明する方が動機が明確になる

## Resolution

記事は公開しないことにした。JP ドラフトのみ以下に保存する。

<details>
<summary>JP 記事ドラフト（2026-04-15 時点）</summary>

+++
title = "暗号化と鍵交換: ハイブリッド暗号を体験する"
date = 2026-04-15
description = "Web Crypto API の crypto.subtle を使い、RSA-OAEP による公開鍵暗号化と AES-GCM による共通鍵暗号化を組み合わせたハイブリッド暗号をブラウザ・Bun・Node.js で体験する。"
path = "2026/WebCryptoHybridEncryption"
+++

<p style="text-align: right"><a href="/en/2026/WebCryptoHybridEncryption">English version</a></p>

## はじめに

[前回の記事](/2026/WebCryptoEcdsa)では、Web Crypto API を使って ECDSA による電子署名の生成と検証を体験した。ECDSA は「秘密鍵で署名し、公開鍵で検証する」仕組みだが、**署名専用**であり暗号化はできない。

データを秘密にする（秘匿）には別のアルゴリズムが必要だ。この記事では、公開鍵暗号の RSA-OAEP と共通鍵暗号の AES-GCM を組み合わせた**ハイブリッド暗号**をコードで確認する。

---

## RSA-OAEP で暗号化・復号

RSA-OAEP は公開鍵暗号の一種で、ECDSA とは逆の使い方をする。

| 操作 | 使う鍵 | 意味 |
|------|--------|------|
| 暗号化 | **公開鍵** | 誰でも暗号化できる |
| 復号 | **秘密鍵** | 受信者だけが復号できる |

署名・検証はできない。

| 環境 | 実行方法 |
|------|----------|
| **ブラウザ** | DevTools の Console に JavaScript 部分をコピペして実行 |
| **Bun** | `bun rsa-oaep.mjs` |
| **Node.js** (v19+) | `node rsa-oaep.mjs` |

```javascript
cat << 'EOF' > rsa-oaep.mjs

// 1. 鍵ペア生成（RSA-OAEP）
const keyPair = await crypto.subtle.generateKey(
  {
    name: "RSA-OAEP",
    modulusLength: 2048,
    publicExponent: new Uint8Array([1, 0, 1]),
    hash: "SHA-256",
  },
  true,
  ["encrypt", "decrypt"]
);

// 2. 公開鍵で暗号化
const message = "Hello, WebCrypto!";
const data = new TextEncoder().encode(message);

const encrypted = await crypto.subtle.encrypt(
  { name: "RSA-OAEP" },
  keyPair.publicKey,
  data
);

// 3. 秘密鍵で復号
const decrypted = await crypto.subtle.decrypt(
  { name: "RSA-OAEP" },
  keyPair.privateKey,
  encrypted
);

console.log("暗号化(Base64):", btoa(String.fromCharCode(...new Uint8Array(encrypted))));
console.log("復号:", new TextDecoder().decode(decrypted));
EOF
```

実行結果:

```bash
$ bun rsa-oaep.mjs
暗号化(Base64): PdGWg0OlQUsYR3GGppsvsfw2kB3Qth5tdteNOoaHLViTf25FSbOKr0gOsFBuEgDhYJvWX3it9kMK5eCXm31PghVzm5aouXyXdzK7lljdLBMjMITFTpCXfnSUtUsm5Nz77dPNgpzZzwNp0ryBgfRv+QmmYnwiMRGS893qAuw5X5KxMXwX3b7NjMSLD+c/zamwOHaCloH6iYwcOMXXb7sNsCrM4gAPJcYYgIQNCJ40IDkTNP4SyKLyFAPjKGDVs2oduclZcDIB15d6/gZPLeAE9CwcAqozSlCmdmvD5oS7+Q4/PUyaj7DoW1Zgo5JviNwfG12dXWXObU0RlbtY37iBgA==
復号: Hello, WebCrypto!
```

公開鍵で暗号化したデータは、対応する秘密鍵でしか復号できない。

---

## AES-GCM で暗号化・復号

AES-GCM は共通鍵暗号で、暗号化と復号に同じ鍵を使う。RSA-OAEP より高速で、データ量の制限もない。また GCM（Galois/Counter Mode）は暗号化と同時に改ざん検知も行う認証付き暗号方式である。

暗号化のたびに一意の IV（初期化ベクトル）が必要で、IV は秘密にしなくてよいが使い回してはいけない。

```javascript
cat << 'EOF' > aes-gcm.mjs

// 1. AES-GCM 共通鍵生成
const key = await crypto.subtle.generateKey(
  { name: "AES-GCM", length: 256 },
  true,
  ["encrypt", "decrypt"]
);

// 2. IV（初期化ベクトル）生成
const iv = crypto.getRandomValues(new Uint8Array(12));

// 3. 暗号化
const message = "Hello, WebCrypto!";
const data = new TextEncoder().encode(message);

const encrypted = await crypto.subtle.encrypt(
  { name: "AES-GCM", iv },
  key,
  data
);

// 4. 復号
const decrypted = await crypto.subtle.decrypt(
  { name: "AES-GCM", iv },
  key,
  encrypted
);

console.log("IV(Base64):", btoa(String.fromCharCode(...iv)));
console.log("暗号化(Base64):", btoa(String.fromCharCode(...new Uint8Array(encrypted))));
console.log("復号:", new TextDecoder().decode(decrypted));
EOF
```

実行結果:

```bash
$ bun aes-gcm.mjs
IV(Base64): dcp0M7a1jJb69+9G
暗号化(Base64): imZKjbRsZFRi1ndnwOq+LQCtO9FRn6W4q8Bo0stAa7yq
復号: Hello, WebCrypto!
```

---

## ハイブリッド暗号: なぜ両方必要か

RSA-OAEP は公開鍵暗号なので鍵配送の問題を解決できるが、**処理が遅く**、暗号化できるデータサイズに上限がある（2048bit 鍵では約 214 バイトまで）。

AES-GCM は**高速**でデータサイズの制限もないが、送信者と受信者が事前に同じ鍵を共有する必要がある。

この問題を解決するのがハイブリッド暗号だ。

```
AES 共通鍵を生成
  ↓
データ本体 → AES-GCM で暗号化（速い・サイズ制限なし）
AES 共通鍵 → RSA-OAEP で暗号化（鍵だけなので小さい）
  ↓
暗号化済み AES 鍵 + IV + 暗号化済みデータを送信

受信側:
暗号化済み AES 鍵 → RSA-OAEP で復号 → AES 鍵を復元
AES 鍵 + IV + 暗号化済みデータ → AES-GCM で復号 → 元のデータ
```

```javascript
cat << 'EOF' > hybrid.mjs

// ===== ハイブリッド暗号: RSA-OAEP + AES-GCM =====

// 1. RSA 鍵ペア生成（受信者側）
const rsaKeyPair = await crypto.subtle.generateKey(
  {
    name: "RSA-OAEP",
    modulusLength: 2048,
    publicExponent: new Uint8Array([1, 0, 1]),
    hash: "SHA-256",
  },
  true,
  ["encrypt", "decrypt"]
);

// 2. AES-GCM 共通鍵を生成（送信者側）
const aesKey = await crypto.subtle.generateKey(
  { name: "AES-GCM", length: 256 },
  true,
  ["encrypt", "decrypt"]
);

// 3. データ本体を AES-GCM で暗号化
const message = "Hello, WebCrypto! これは長いメッセージです。";
const data = new TextEncoder().encode(message);
const iv = crypto.getRandomValues(new Uint8Array(12));

const encryptedData = await crypto.subtle.encrypt(
  { name: "AES-GCM", iv },
  aesKey,
  data
);

// 4. AES 鍵を RSA-OAEP で暗号化（受信者の公開鍵で）
const rawAesKey = await crypto.subtle.exportKey("raw", aesKey);
const encryptedAesKey = await crypto.subtle.encrypt(
  { name: "RSA-OAEP" },
  rsaKeyPair.publicKey,
  rawAesKey
);

console.log("=== 送信データ ===");
console.log("暗号化済み AES 鍵(Base64):", btoa(String.fromCharCode(...new Uint8Array(encryptedAesKey))));
console.log("IV(Base64):", btoa(String.fromCharCode(...iv)));
console.log("暗号化済みデータ(Base64):", btoa(String.fromCharCode(...new Uint8Array(encryptedData))));

// 5. AES 鍵を RSA-OAEP で復号（受信者の秘密鍵で）
const decryptedAesKeyRaw = await crypto.subtle.decrypt(
  { name: "RSA-OAEP" },
  rsaKeyPair.privateKey,
  encryptedAesKey
);

// 6. 復元した AES 鍵でデータ本体を復号
const restoredAesKey = await crypto.subtle.importKey(
  "raw",
  decryptedAesKeyRaw,
  { name: "AES-GCM" },
  false,
  ["decrypt"]
);

const decryptedData = await crypto.subtle.decrypt(
  { name: "AES-GCM", iv },
  restoredAesKey,
  encryptedData
);

console.log("\n=== 復号結果 ===");
console.log("復号:", new TextDecoder().decode(decryptedData));
EOF
```

実行結果:

```bash
$ bun hybrid.mjs
=== 送信データ ===
暗号化済み AES 鍵(Base64): nkijbfnacJNyTPNpAdOZMtu9uz/RlgTbT2ZYmQ+UdFjJi1MqBD5QE52vnyNJERaeHZiv0pD8bVgZnY+EKGvLzdqzyh/6ItVB7LsFiauWgy/nJtEmD0rWCm93RAuEp3sOE56Smlv5Xz+uvIgDqV4eZxoJSqd/28uxxwMdrraD9NBj/PkcPqI42P62Mb9SQ/a1mXLcl4L/F942vwSkDODDpz1fz/oeaFAViDm8rYNdWg082nRvZKR2Em6zIzefwT3a023siTO1gME7HjMMxDNkR0HhzcYzk/U4upWlBfy7ZkaqKWGNxZeN5JCg++V9S2a+g9FWuvuiIaFy6PHoanrlA==
IV(Base64): LWkQgfnoo0WEc6d6
暗号化済みデータ(Base64): VbpWPDgxzZ9vc2cwWif+loXzdSOLQXIc3ZoGygSYXEFWFqaoIXgnTl0AHQd3H+YD7L4U94uwjwJFFQhS9oqgbL3gQmwgYzaCzw==

=== 復号結果 ===
復号: Hello, WebCrypto! これは長いメッセージです。
```

---

## ポイント

- **RSA-OAEP は遅い・サイズ制限あり**。大量データの暗号化には向かない
- **AES-GCM は高速・サイズ制限なし**。ただし鍵の配送問題がある
- **ハイブリッド暗号**は両者の長所を組み合わせる。AES 鍵（小さい）だけ RSA で暗号化し、データ本体は AES で暗号化する
- **IV は使い回し禁止**。同じ鍵と IV の組み合わせを繰り返すと安全性が崩壊する
- TLS や PGP もこのハイブリッド方式を採用している

---

## まとめ

RSA-OAEP（公開鍵暗号）と AES-GCM（共通鍵暗号）を組み合わせたハイブリッド暗号を体験した。「AES 鍵だけ RSA で包み、データ本体は AES で暗号化する」という構造が、現代の暗号通信の基本パターンになっている。

次回は、このハイブリッド暗号が TLS 1.2 のハンドシェイクでどのように使われているかを、Web Crypto API で再現しながら確認する。

</details>
