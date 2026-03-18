+++
title = "Cloud Run デプロイを 19 分から 3.5 分に短縮した話"
date = 2026-03-17
description = "Cloud Build を GitHub Actions BuildKit + cargo-chef に置き換えて、Rust プロジェクトのビルド時間を 82% 削減した事例。"
path = "2026/CloudRunDeployOptimization"
+++

Cloud Run で運用している Rust 製認証ライブラリ [oauth2-passkey](https://github.com/ktaka-ccmp/oauth2-passkey) のデモサイト（[passkey-demo.ccmp.jp](https://passkey-demo.ccmp.jp)）のデプロイに約 19 分かかっていた。ビルドパイプラインを Cloud Build から GitHub Actions BuildKit + cargo-chef に置き換えて 3.5 分まで短縮した。

---

## 移行前の構成

`dev` ブランチへの push をトリガーに、GitHub Actions が Cloud Build を呼び出してビルドし、Cloud Run にデプロイする構成だった。

### ワークフロー

```yaml
steps:
  # GCP 認証
  - uses: google-github-actions/auth@v2
    with:
      credentials_json: ${{ secrets.GCP_SA_KEY }}

  - uses: google-github-actions/setup-gcloud@v2

  # Cloud Build にソースをアップロードしてビルド
  - run: gcloud builds submit --config=demo-live/cloudbuild.yaml

  # ビルドしたイメージを Cloud Run にデプロイ
  - run: gcloud run deploy oauth2-passkey-demo ...
```

GitHub Actions はあくまでトリガー役で、実際のビルドは `gcloud builds submit` で Cloud Build に委譲していた。

### Dockerfile

Alpine ベースの Rust イメージでコンパイルし、`scratch`（空のイメージ）にバイナリだけコピーする 2 段構成:

```dockerfile
# Stage 1: ビルド
FROM rust:1.88-alpine AS builder
RUN apk add --no-cache musl-dev cmake make perl
WORKDIR /app
COPY . .
RUN cargo build --release --manifest-path demo-live/Cargo.toml --features bundled-tls

# Stage 2: 実行（バイナリのみ、27 MB）
FROM scratch
COPY --from=builder /app/target/release/demo-live /demo-live
EXPOSE 8080
ENTRYPOINT ["/demo-live"]
```

最終イメージは 27 MB と小さいが、問題は Stage 1 にある。`COPY . .` でソースコード全体をコピーした上で `cargo build` するため、`.rs` ファイルが 1 つでも変わると依存クレート（tokio, axum, sqlx, rustls など数百クレート）を含む**全てを再コンパイル**する。

### なぜ 19 分もかかるのか

**1. キャッシュが効かない**

Cloud Build はビルドごとにクリーンな環境が立ち上がり、Docker のレイヤーキャッシュがビルド間で持ち越されない。毎回フルビルドになる。

**2. マシンスペックが低い**

Cloud Build のデフォルトマシンは 1 vCPU / 3.75 GB RAM。Rust のコンパイルは CPU とメモリを大量に消費するため、このスペックでは非常に遅い。

## 移行先: GitHub Actions + BuildKit

前述の通り、Cloud Build ではどれだけ Dockerfile を工夫してもレイヤーキャッシュが持ち越されず、毎回ゼロからコンパイルすることになる。GitHub Actions + BuildKit に移行すれば、この問題が解決する。BuildKit の `type=gha` キャッシュを使うと、ビルドで生成された Docker レイヤーを GitHub Actions のキャッシュストレージに保存し、次のビルドで復元できる。さらに GitHub Actions ランナーは 4 vCPU / 16 GB RAM と Cloud Build デフォルトの 4 倍のコア数があり、パブリックリポジトリなら無料で使える。

ただし、キャッシュを活かすにはもう一つ工夫が要る。移行前の Dockerfile のように `COPY . .` + `cargo build` では、ソースが変わるたびに依存クレートごとキャッシュが無効になる。「依存クレートのビルド」と「アプリケーションのビルド」を別のレイヤーに分離する必要がある。これを実現するのが cargo-chef である。

### cargo-chef: 依存ビルドとアプリビルドの分離

[cargo-chef](https://github.com/LukeMathWalker/cargo-chef) は、依存クレートのビルドとアプリケーションのビルドを Docker レイヤーとして分離するツールである。3 段階で動作する:

1. **prepare**: `Cargo.toml` / `Cargo.lock` を解析し、依存情報だけを抽出した `recipe.json` を生成
2. **cook**: `recipe.json` を元に依存クレートだけをビルド（ソースコードは不要）
3. **build**: アプリケーション本体をビルド（依存クレートは cook で既にビルド済み）

`recipe.json` にはソースコード（`.rs` ファイル）の内容は含まれない。そのため `Cargo.toml` / `Cargo.lock` が変わらない限り、ソースコードをいくら変更しても依存ビルドのレイヤーはキャッシュヒットする。

### BuildKit と type=gha キャッシュ

[BuildKit](https://github.com/moby/buildkit) は Docker の高機能ビルドバックエンドで、Docker 23.0 以降ではデフォルトのビルダーになっている。従来の Docker ビルドと比べて、並列ビルド、効率的なキャッシュ管理、そして**外部キャッシュバックエンド**への対応が大きな特徴である。

`type=gha` キャッシュは、Docker のレイヤーキャッシュを GitHub Actions のキャッシュストレージに保存・復元する仕組みである。

```yaml
- name: Build and push
  uses: docker/build-push-action@v6
  with:
    cache-from: type=gha,scope=demo-live       # キャッシュから復元
    cache-to: type=gha,mode=max,scope=demo-live # キャッシュに保存
```

- `mode=max`: 最終ステージだけでなく、中間ステージのレイヤーも全てキャッシュする。これがないと cargo-chef の依存レイヤーがキャッシュされない
- `scope=demo-live`: キャッシュのネームスペース。他のワークフローのキャッシュと衝突しない

## 移行後の構成

### Dockerfile

4 段構成の多段ビルドになった:

```dockerfile
# Stage 1: ベースイメージ（Rust + cargo-chef）
FROM rust:1.88-alpine AS chef
RUN apk add --no-cache musl-dev cmake make perl
RUN cargo install cargo-chef
WORKDIR /app

# Stage 2: 依存関係の「レシピ」を作る
FROM chef AS planner
COPY . .
RUN cargo chef prepare --recipe-path recipe.json

# Stage 3: 依存ビルド -> アプリビルド
FROM chef AS builder
COPY --from=planner /app/recipe.json recipe.json
RUN cargo chef cook --release --manifest-path demo-live/Cargo.toml \
    --features bundled-tls --recipe-path recipe.json
COPY . .
RUN cargo build --release --manifest-path demo-live/Cargo.toml --features bundled-tls

# Stage 4: バイナリだけコピー
FROM scratch
COPY --from=builder /app/target/release/demo-live /demo-live
EXPOSE 8080
ENTRYPOINT ["/demo-live"]
```

Stage 3 がキャッシュの肝である。`recipe.json` だけをコピーして依存クレートをビルドし、その後にソースコード全体をコピーしてアプリをビルドする。

**キャッシュの動作:**

| 行 | ソースコードだけ変更 | Cargo.toml/lock も変更 |
|----|---------------------|----------------------|
| `COPY recipe.json` | recipe.json 同じ -> cache hit | recipe.json 変わる -> cache miss |
| `cargo chef cook` | cache hit（依存ビルドスキップ） | 依存クレート全部再ビルド |
| `COPY . .` | ソース変わった -> cache miss | cache miss |
| `cargo build` | アプリ本体だけビルド | アプリ本体ビルド |

`cargo chef cook` は依存クレートのコンパイル成果物を通常の `cargo build` と同じ `target/` 以下に配置する。そのため後続の `cargo build` は「依存は既にビルド済み」と判断し、自分のコードだけコンパイルする。

### ワークフロー

Cloud Build への委譲をやめ、GitHub Actions 上で直接ビルド・プッシュする構成に変わった:

```yaml
steps:
  - uses: actions/checkout@v4

  # --- Docker build & push ---
  - name: Set up Docker Buildx
    uses: docker/setup-buildx-action@v3

  - name: Login to Artifact Registry
    uses: docker/login-action@v3
    with:
      registry: asia-northeast1-docker.pkg.dev
      username: _json_key
      password: ${{ secrets.GCP_SA_KEY }}

  - name: Build and push
    uses: docker/build-push-action@v6
    with:
      context: .
      file: demo-live/Dockerfile
      push: true
      tags: asia-northeast1-docker.pkg.dev/.../oauth2-passkey-demo:latest
      cache-from: type=gha,scope=demo-live
      cache-to: type=gha,mode=max,scope=demo-live

  # --- Cloud Run deploy ---
  - name: Authenticate to Google Cloud
    uses: google-github-actions/auth@v2
    with:
      credentials_json: ${{ secrets.GCP_SA_KEY }}

  - name: Set up Cloud SDK
    uses: google-github-actions/setup-gcloud@v2

  - name: Deploy to Cloud Run
    run: gcloud run deploy ...
```

前半で Docker イメージをビルドして Artifact Registry に push し、後半で GCP に認証して Cloud Run にデプロイする。`docker/login-action` で Artifact Registry に直接ログインするため、GCP 認証はデプロイ時にしか必要ない。

## 結果

| Build | Method | Time |
|-------|--------|------|
| #30 | Cloud Build（旧） | 19m 28s |
| #31 | BuildKit + cargo-chef（1 回目、キャッシュなし） | 11m 24s |
| #32 | BuildKit + cargo-chef（2 回目、キャッシュあり） | 3m 28s |

- Cloud Build -> GitHub Actions BuildKit だけで **19 分 -> 11 分**（CPU 4 倍の効果）
- cargo-chef キャッシュが効いた 2 回目で **11 分 -> 3.5 分**（依存ビルドスキップの効果）
- トータルで **19 分 -> 3.5 分、82% 短縮**

## 注意点

**初回ビルドはキャッシュがない**: 1 回目はキャッシュが空なので cargo-chef のインストール分を含めてフルビルドになる。ただし GitHub Actions ランナーの CPU が Cloud Build より速いため、それでも 11 分に短縮された。

**Cargo.toml/Cargo.lock を変更した場合**: 依存レイヤーのキャッシュが無効になり、依存クレートの再ビルドが走る（約 11 分）。キャッシュの恩恵はソースコードだけの変更時に受けられる。

**IAM ロールの整理**: Cloud Build を使わなくなったため、GitHub Actions 用サービスアカウントから `cloudbuild.builds.editor` と `storage.admin` ロールを削除した。不要になった権限は速やかに剥がすべきである。

## まとめ

Rust プロジェクトの Cloud Run デプロイを高速化するために、Cloud Build から GitHub Actions BuildKit + cargo-chef に移行した。

- cargo-chef で「依存ビルド」と「アプリビルド」を Docker レイヤーとして分離
- BuildKit の `type=gha` キャッシュでビルド間のレイヤーキャッシュを持続
- GitHub Actions ランナーの 4 vCPU で Cloud Build デフォルトの 4 倍のコンパイル速度

結果として、ソースコードだけの変更であれば **19 分 -> 3.5 分（82% 短縮）** を達成した。
