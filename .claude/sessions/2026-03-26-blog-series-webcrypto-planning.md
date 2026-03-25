# Session Snapshot: Web Crypto API ブログシリーズ企画

## Current Task

ジャーナル（0324.md）の暗号技術素材をブログ記事シリーズとして企画し、ブログリポジトリにイシューを作成した。

## Files Modified

### daily-journal（このリポジトリ）
- `README.md` — 新規エントリ追加（Tokyo Rust Show & Tell 発表検討）

### ktaka.blog.ccmp.jp（ブログリポジトリ）
- `.claude/issues/README.md` — イシューテーブルに8件追加（Open 4→12）
- `.claude/issues/open/20260326-0419-blog-series-webcrypto-learn-crypto.md` — **親イシュー**: シリーズ全体構成・素材の在り処・方針
- `.claude/issues/open/20260326-0420-blog-webcrypto-01-ecdsa.md` — 署名と検証: ECDSA を体験する
- `.claude/issues/open/20260326-0421-blog-webcrypto-02-hybrid-encryption.md` — 暗号化と鍵交換: ハイブリッド暗号を体験する
- `.claude/issues/open/20260326-0422-blog-webcrypto-03-tls12.md` — TLS 1.2 ハンドシェイクを再現する
- `.claude/issues/open/20260326-0423-blog-webcrypto-035-tls13.md` — TLS 1.3 で何が変わったか
- `.claude/issues/open/20260326-0424-blog-webcrypto-04-ssh.md` — SSH 公開鍵認証の仕組み
- `.claude/issues/open/20260326-0425-blog-webcrypto-05-passkey.md` — Passkey がフィッシングに強い理由
- `.claude/issues/open/20260326-0426-blog-webcrypto-06-dbsc.md` — DBSC: Cookie を TPM に縛る

### memory
- `.claude/projects/-home-ktaka-GitHub-daily-journal/memory/feedback_blog_style.md` — ブログ記事スタイルの好み
- `.claude/projects/-home-ktaka-GitHub-daily-journal/memory/MEMORY.md` — メモリインデックス作成

## Key Decisions

1. **シリーズ番号は振らない** — 途中で別テーマが入る可能性、中断の可能性があるため。各記事は独立して成立させる
2. **1記事1テーマ・1結論** — 長いテクニカル解説は避け、目的と結論がはっきりする短い記事にする
3. **実行環境は3つ** — ブラウザ DevTools / Bun / Node.js。最初の記事でセットアップ、以降は毎回「Bun でも実行可能」と明記
4. **記事候補の依存関係** — ECDSA の記事だけ読めば SSH / Passkey に飛べる。TLS は ECDSA + ハイブリッド暗号の両方が前提
5. **素材は daily-journal に集約** — `~/GitHub/daily-journal/ktaka/2026/0324.md` に全素材あり。各イシューに行番号範囲を記載済み

## Next Steps

1. ブログリポジトリで ECDSA の記事（`20260326-0420`）から執筆開始
2. 既存ブログ記事のスタイル・Zola テンプレートを確認してから書き始める
3. 両リポジトリの変更をコミット（まだ未コミット）

## Context

- ブログリポジトリ: `~/GitHub/ktaka.blog.ccmp.jp`（Zola + GitHub Pages）
- ジャーナル素材: `~/GitHub/daily-journal/ktaka/2026/0324.md`
  - Web Crypto API メモ: L39〜L313
  - TLS/SSH/Passkey コンセプトコード: L314〜L812
  - 暗号技術比較ノート: L626〜L812
  - DBSC セッション管理: L816〜L970
- Tokyo Rust Show & Tell（2026/03/31）での oauth2-passkey 発表検討もジャーナルにあり、シリーズ記事と相乗効果が期待できる
