# Session Snapshot: FedCM Direct Integration Blog Post

## Current Task

FedCM (Federated Credential Management) を Google の GIS SDK なしで直接実装した記録をブログ記事化。日本語版・英語版の2記事をドラフトとして作成済み。レビュー・推敲待ち。

## Files Created

- `content/2026/FedCMDirectIntegration/index.md` -- 日本語版ドラフト (`draft = true`)
- `content/2026/FedCMDirectIntegrationEn/index.md` -- 英語版ドラフト (`draft = true`)

## Article Structure (Both Versions)

1. FedCM とは -- OAuth2 Authorization Code Flow とのフロー比較図
2. なぜ SDK なしか -- ライブラリとしての依存関係最小化の判断
3. フロントエンド実装 -- feature detection, `navigator.credentials.get()`, fallback
4. バックエンド実装 -- 50行のモジュール、既存JWT検証インフラの再利用、ユーザー処理パイプライン共有
5. セキュリティ比較 -- Authorization Code Flow vs FedCM のトレードオフ表
6. Google固有の未文書化要件 -- params, JSON-wrapped JWT, nonce移行
7. 注意点 -- active/passive mode配置, ブラウザサポート, Googleの公式スタンス

## Key Design Decisions

- **1記事完結**: 概要から実装まで1記事にまとめる（分割しない）
- **oauth2-passkey への言及**: 記事の主題はFedCM自体の理解と実装パターン。クレートは実装の文脈として自然に言及
- **コードスニペット**: 要所のみ（JS: credentials.get()呼び出し・fallback分岐、Rust: JWT検証50行・パイプライン共有）
- **ハマりポイントの扱い**: 注意点として記載するが、記事の面白さの主軸にはしない。「基本的な理解、リーズナブルな実装こそ面白い」
- **日英別記事**: 翻訳ではなく、各言語に自然な文体・ストーリーで独立記事として作成
- **セキュリティの正直な比較**: 「FedCMの方が安全」とは言わず、トレードオフを明示

## Source Material

実装は `~/GitHub/oauth2-passkey` の `fedcm-integration` ブランチにある:
- `oauth2_passkey/src/oauth2/main/fedcm.rs` -- バックエンドJWT検証（50行）
- `oauth2_passkey/src/coordination/oauth2.rs` -- `fedcm_authorized_core()` + 共有パイプライン
- `oauth2_passkey_axum/static/oauth2.js` -- フロントエンドFedCMフロー
- `docs/src/integration/fedcm.md` -- 詳細なリファレンスドキュメント（記事の下敷き）

## Context: Why This Article Matters

Web検索で確認済み: **FedCMをGIS SDKなしでGoogle IdPに直接実装した記事は、英語・日本語ともにゼロ**。
- 英語: 公式ドキュメント、ベンダー概念記事、SDK移行ガイドのみ
- 日本語: 自作IdPでプロトコルを学ぶ記事が3-4件あるが、RP側のGoogle直接実装はなし
- Google自身が「SDK なしの直接利用は推奨しない」と明言
- FedCM + 任意のバックエンドフレームワーク（Rust含む）の組み合わせ記事もゼロ

## Next Steps

- [ ] `zola serve` でプレビューして表示確認
- [ ] 日本語版の推敲（文体、フローの読みやすさ）
- [ ] 英語版の推敲（同上）
- [ ] スクリーンショットやデモ動画の追加を検討（FedCMのアカウント選択UIなど）
- [ ] `draft = true` を外して公開

## Build Verification

`zola build --drafts` で正常ビルド確認済み（111 -> 114 pages）。
両記事とも正しいパスに生成:
- `/2026/FedCMDirectIntegration` (JP)
- `/en/2026/FedCMDirectIntegration` (EN)
