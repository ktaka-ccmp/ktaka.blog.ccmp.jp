# Issue: ブログシリーズ — Web Crypto API で学ぶ暗号技術

## Table of Contents

- [Description](#description)
- [Related Issues](#related-issues)
- [Approach](#approach)
- [Related Files](#related-files)
- [Implementation Tasks](#implementation-tasks)
- [Decision Log](#decision-log)
- [Resolution](#resolution)

## ID: 20260326-0419

## Created: 2026-03-26-04-19

## Closed:

## Status: open

## Priority: high

## Difficulty: large

## Description

Web Crypto API を共通の道具として使い、暗号技術・プロトコルを1つずつ積み上げて理解するブログシリーズを作成する。

**シリーズのコンセプト:**
- コードはブラウザの DevTools、Bun、Node.js いずれでも動く（毎回明記）
- 1記事1テーマ・1結論。目的と結論がはっきりする短い記事
- 前の記事の知識で次が読める積み上げ構造
- 長いテクニカル解説は避け、簡潔に

**記事候補（順序・本数は固定しない。途中で別テーマが入ってもよい）:**

| タイトル案 | 学ぶこと | 読んでおくとよい記事 |
|-----------|---------|-------------------|
| 署名と検証 — ECDSA を体験する | 実行環境セットアップ（Browser/Bun/Node.js）+ 秘密鍵で署名、公開鍵で検証 | なし（最初に書く） |
| 暗号化と鍵交換 — ハイブリッド暗号を体験する | RSA-OAEP、AES-GCM、ECDH。なぜ組み合わせるか | ECDSA の記事 |
| TLS 1.2 ハンドシェイクを再現する | 証明書検証 → 鍵交換 → 暗号化通信の流れ | ECDSA + ハイブリッド暗号 |
| TLS 1.3 で何が変わったか | RTT 削減、証明書暗号化、ECDHE 必須化 | TLS 1.2 の記事 |
| SSH 公開鍵認証の仕組み | TOFU、チャレンジ署名、セッション ID | ECDSA の記事 |
| Passkey がフィッシングに強い理由 | origin 束縛、authenticatorData、signCount | ECDSA の記事 |
| DBSC — Cookie を TPM に縛る | セッション乗っ取り対策、Passkey との相補性 | Passkey の記事 |

**依存関係:** ECDSA の記事だけ読めば SSH / Passkey に飛べる。TLS は ECDSA + ハイブリッド暗号の両方が前提。

## Related Issues

- `20260326-0420` 署名と検証 — ECDSA を体験する (child)
- `20260326-0421` 暗号化と鍵交換 — ハイブリッド暗号を体験する (child)
- `20260326-0422` TLS 1.2 ハンドシェイクを再現する (child)
- `20260326-0423` TLS 1.3 で何が変わったか (child)
- `20260326-0424` SSH 公開鍵認証の仕組み (child)
- `20260326-0425` Passkey がフィッシングに強い理由 (child)
- `20260326-0426` DBSC — Cookie を TPM に縛る (child)

## Approach

### 素材の在り処

ジャーナルリポジトリ `~/GitHub/daily-journal/ktaka/2026/0324.md` に素材が揃っている:

- **Web Crypto API メモ**（L39〜L313）: ECDSA / RSA-OAEP / AES-GCM のコード例（JS）、Python・Rust の同等実装、3言語比較表
- **TLS / SSH / Passkey コンセプトコード**（L314〜L812）: TLS 1.2/1.3、SSH、Passkey の概念実装（JS/Python/Rust）、プロトコルフロー図、横断比較表
- **暗号技術比較ノート**（L626〜L812）: TLS/SSH/Passkey の署名・暗号化・鍵保管・フィッシング耐性の横断比較
- **DBSC セッション管理**（L816〜L970）: DBSC のライフサイクル、HTTP 例、脅威分析、Passkey との相補性

### 記事の書き方ルール

- 各記事は「目的（何を理解したいか）→ コード → 結論」の3部構成
- コードはブラウザの DevTools、Bun、Node.js いずれでも動く（毎回明記）
- 長い解説は避け、表・箇条書き・コードで伝える
- 既存のブログ記事のスタイル・テンプレートに合わせる

### 進め方

1. #1 から順に書く（#4, #5 は #3 完了を待たなくても書ける）
2. 各記事ごとに個別イシューがあるのでそちらを参照

## Related Files

- `~/GitHub/daily-journal/ktaka/2026/0324.md` — 素材（Web Crypto API、TLS/SSH/Passkey、DBSC）

## Implementation Tasks

- [ ] 署名と検証 — ECDSA（`20260326-0420`）← 最初に書く
- [ ] 暗号化と鍵交換 — ハイブリッド暗号（`20260326-0421`）
- [ ] TLS 1.2（`20260326-0422`）
- [ ] TLS 1.3（`20260326-0423`）
- [ ] SSH（`20260326-0424`）
- [ ] Passkey（`20260326-0425`）
- [ ] DBSC（`20260326-0426`）

## Decision Log

<!-- APPEND-ONLY: Do not edit or delete existing entries. Add new entries at the bottom. -->

### 2026-03-26: シリーズ構成を決定

- Context: ジャーナル 0324.md に暗号技術の素材が大量にあり、ブログ記事化を検討
- Decision: Web Crypto API を軸にした積み上げ式シリーズ（全7記事）として構成
- Reason: 長い解説記事は読みにくいので、1記事1テーマ・1結論で小さく分解。Web Crypto API がブラウザで動くため読者が手を動かせる

### 2026-03-26: 記事を個別イシューに分離

- Context: シリーズ全体を1イシューにすると大きすぎる
- Decision: 親イシュー（本イシュー）+ 各記事の子イシュー7件に分離
- Reason: 別のエージェントセッションからでも1記事ずつ着手しやすい

### 2026-03-26: 番号付けをやめてフラット構成に

- Context: 1.1/1.2/2/2.5... と番号を振っていたが、途中で別テーマが入る可能性やシリーズ中断の可能性がある
- Decision: 記事にシリーズ番号は振らない。各記事は独立した記事として成立させる。イシュー内では「読んでおくとよい記事」で依存関係を示す
- Reason: 番号に縛られると柔軟性がなくなる。ブログ記事自体に章立てするわけではない

### 2026-03-26: 実行環境に Bun / Node.js を追加

- Context: 当初はブラウザ DevTools のみを想定していた
- Decision: コードはブラウザ / Bun / Node.js いずれでも動くようにする。最初の記事で3環境のセットアップを説明し、以降は毎回「Bun でも実行可能」と明記
- Reason: Bun でも `crypto.subtle` が使える。ブラウザに限定する必要がない

## Resolution
