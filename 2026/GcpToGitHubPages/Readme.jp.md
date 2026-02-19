# コーポレートサイトを GCP から GitHub Pages に移行して月額 $23 → $0 にした話

*Joomla CMS + wget による静的サイト生成パイプラインが、ホスティング移行をシンプルにしてくれた事例。*

## Table of Contents

- [はじめに](#はじめに)
- [移行前の構成: Joomla CMS + GCP](#移行前の構成-joomla-cms--gcp)
  - [CMS 入稿 → 静的 HTML 生成というアーキテクチャ](#cms-入稿--静的-html-生成というアーキテクチャ)
  - [このアーキテクチャのメリット](#このアーキテクチャのメリット)
- [移行先の検討: GitHub Pages vs Netlify](#移行先の検討-github-pages-vs-netlify)
  - [候補の選定基準](#候補の選定基準)
  - [ステージング検証](#ステージング検証)
  - [比較結果](#比較結果)
- [本番移行の実施](#本番移行の実施)
- [GCP インフラの撤去](#gcp-インフラの撤去)
- [まとめ](#まとめ)

---

## はじめに

自社のコーポレートサイト（ccmp.jp）を GCP 上の VM + Cloud Load Balancer + Cloud CDN の構成から GitHub Pages に移行し、月額約 $23 のホスティングコストを $0 にした。

移行がスムーズにいった最大の要因は、もともと Joomla CMS で入稿しつつ、配信は静的 HTML で行う構成を採っていたことだった。ホスティング先が変わっても、入稿ワークフローには一切手を入れる必要がなかった。

## 移行前の構成: Joomla CMS + GCP

### CMS 入稿 → 静的 HTML 生成というアーキテクチャ

コーポレートサイトのコンテンツは Joomla CMS で管理している。ただし、Joomla を本番サーバで動かしているわけではない。入稿から配信までの流れは次のようになっている:

```
[Joomla CMS] → wget でクローリング → 静的 HTML 生成 → GitHub リポジトリに push
                                                          ↓
                                                  本番サーバで git pull → nginx 配信
```

1. **入稿**: ローカル環境の Joomla CMS で記事を作成・編集
2. **静的化**: `wget` で CMS の出力をクローリングし、静的 HTML ファイルとして `localhost/` ディレクトリに出力
3. **デプロイ**: 生成した HTML を GitHub リポジトリにマージし、GCP VM 上で `git pull` → nginx で配信

本番環境には PHP も MySQL も不要で、純粋な静的ファイル配信のみだった。前段に Cloud Load Balancer と Cloud CDN を配置し、キャッシュによるレスポンス高速化と VM への負荷軽減を行っていた。

### このアーキテクチャのメリット

この「CMS で入稿、配信は静的 HTML」というアーキテクチャには、当初から以下のメリットがあった:

**入稿者にやさしい**: 記事の作成・編集は Joomla の WYSIWYG エディタで行える。Markdown や HTML を直接書く必要がなく、非エンジニアでも入稿できる。

**CMS の便利さを維持しつつ脆弱性を排除**: Joomla や WordPress などの CMS は頻繁に脆弱性が報告され、攻撃の標的になりやすい。しかしこの構成では CMS はローカル環境でのみ動作し、本番にはPHP も MySQL も存在しない。入稿者は CMS の WYSIWYG エディタやテンプレート機能をそのまま使えるが、攻撃者から見える本番環境は単なる静的ファイルだけ。CMS の利便性とセキュリティを両立できる。

**ホスティングの自由度が高い**: 配信するのは単なる静的ファイルなので、ホスティング先を自由に選べる。今回の GCP → GitHub Pages の移行でも、入稿フロー側は一切変更なしで済んだ。

**バージョン管理**: 静的 HTML を GitHub リポジトリで管理しているため、変更履歴の追跡やロールバックが容易。

そして、今回このメリットが最大限に活きた。移行作業はホスティング先の変更だけで完結し、コンテンツのワークフローには一切手を入れずに済んだ。

## 移行先の検討: GitHub Pages vs Netlify

### 候補の選定基準

移行先の条件は以下の通り:

- **月額 $0**: 無料の静的ホスティングサービス
- **カスタムドメイン対応**: ccmp.jp（apex ドメイン）で運用
- **HTTPS 対応**: TLS 証明書の自動発行・更新
- **IPv6 対応**: apex ドメインでも IPv6 到達可能
- **自社 NS 維持**: DNS のネームサーバは変更しない

Cloudflare Pages は NS 移管が原則必要なため、自社 NS 維持の要件と衝突し不採用とした。GitHub Pages と Netlify の 2 候補でステージング検証を行った。

### ステージング検証

それぞれサブドメインでステージング環境を構築し、実際の動作を検証した。

**GitHub Pages（stg-g.ccmp.jp）**: GitHub Actions ワークフローで `localhost/` を Pages にデプロイ。CNAME と `.nojekyll` はワークフロー内で動的生成する構成とした（コンテンツ生成時に `rm -rf localhost/` されるため、ファイルを直接置けない）。全項目問題なし。

**Netlify（stg-n.ccmp.jp）**: Netlify Free プランでは Organization 所有のプライベートリポジトリの Git 連携が不可（Pro $19/月が必要）。GitHub Actions から `netlify deploy --prod` で CLI デプロイする方式で回避した。また、`wget` が生成するファイル名に `?` や `#` が含まれており Netlify が拒否するため、デプロイ前にクリーンアップが必要だった。

### 比較結果

| 項目 | GitHub Pages | Netlify Free |
|------|-------------|-------------|
| 月額 | $0 | $0 |
| apex ドメイン A レコード | 4 IP | 1 IP のみ |
| **apex ドメイン IPv6** | **OK（AAAA 4 IP）** | **NG（AAAA 非公開）** |
| Git 連携 | ネイティブ | CLI 回避策が必要 |
| ファイル名制約 | なし | `?` `#` 不可 |

**GitHub Pages を採用**。決め手は apex ドメインでの IPv6 対応、ネイティブ Git 連携、ファイル名制約がない点。なお、CDN については GitHub Pages も Fastly ベースの CDN を内蔵しており、Cloud CDN を別途構築する必要がなくなった。

## 本番移行の実施

ステージング検証で問題がないことを確認した翌日に本番移行を実施した。

1. GitHub Actions ワークフローの CNAME をステージング用からプロダクション用（`ccmp.jp`）に変更
2. GitHub の Settings → Pages → Custom domain を `ccmp.jp` に設定（DNS 切替前に実施し、TLS 証明書の発行を最速化）
3. 自社 NS で ccmp.jp の A/AAAA レコードを GitHub Pages の IP に切替
4. `www.ccmp.jp` の CNAME を追加（GitHub Pages が www → apex の自動リダイレクトを提供）
5. 動作確認: HTTPS、Clean URL、リダイレクト、IPv4/IPv6 すべて OK

TLS 証明書について:
- GitHub Pages は DNS が向いた時点で自動的に Let's Encrypt 証明書を発行する
- 旧 GCP VM の証明書との衝突はない（Let's Encrypt は同一ドメインに複数証明書を許可）
- GCP 側の証明書は自然に期限切れになるだけで、手動対応は不要

## GCP インフラの撤去

本番移行の完了後、旧 GCP インフラを管理していた Terraform プロジェクトの撤去を行った。

このプロジェクトは Terraform 0.12.24 で構築されたもので、tfstate が空の状態だったため、まず `terraform import` で GCP 上の全 20 リソースを state に取り込み、tf ファイルを現状に同期させた上で `terraform destroy` を実行した。

削除したリソース:
- VPC、サブネット、ファイアウォールルール
- GCE インスタンス、インスタンスグループ
- HTTP/HTTPS ロードバランサー、IPv4/IPv6 フォワーディングルール
- 固定 IP アドレス（IPv4/IPv6）
- SSL 証明書 9 個

再構築が必要になった場合に備え、Terraform コードと手順書（REBUILD.md, TEARDOWN.md）はリポジトリに残してある。再構築時には旧 Let's Encrypt（certbot + cron）から GCP マネージド SSL 証明書への移行を推奨する旨も記載した。

## まとめ

| 項目 | 移行前（GCP） | 移行後（GitHub Pages） |
|------|-------------|---------------------|
| 月額コスト | 約 $23 | $0 |
| TLS 証明書 | Let's Encrypt 手動更新 | 自動発行・更新 |
| IPv6 | 対応 | 対応 |
| デプロイ | git pull + nginx | GitHub Actions 自動デプロイ |
| インフラ運用 | VM・LB・CDN の管理が必要 | 不要 |

今回の移行で改めて実感したのは、**入稿と配信を分離するアーキテクチャの強さ**だった。Joomla CMS による入稿ワークフローは一切変更せず、ホスティング先だけを差し替えることで移行が完了した。コンテンツ管理と配信基盤を疎結合にしておくことで、将来また別のホスティングサービスに移る場合でも同様にスムーズな移行ができる。

もし「CMS は使いたいけど静的ホスティングのメリットも享受したい」という状況であれば、CMS + wget による静的サイト生成パイプラインは検討に値するアプローチだと思う。
