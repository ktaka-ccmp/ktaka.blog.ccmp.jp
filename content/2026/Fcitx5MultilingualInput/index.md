+++
title = "fcitx5 で日本語・中国語・英語の3言語入力環境を構築する"
date = 2026-03-07
description = "Linux (Debian) で fcitx5 を使い、日本語 (Mozc)・中国語 (Pinyin)・英語を1つのフレームワークで切り替える設定方法。簡繁変換の方法も紹介。"
path = "2026/Fcitx5MultilingualInput"
[extra]
lang = "ja"
+++

*筆者が普段使っている日本語・中国語・英語の3言語入力環境を、fcitx5 でどう設定しているかをまとめました。*

---

## はじめに

複数の言語を日常的に使う場合、入力メソッドの切り替えがスムーズにできるかどうかは作業効率に直結します。

Linux の入力メソッドフレームワークは主に2つあります。

| フレームワーク | 特徴 |
|---|---|
| **fcitx5** | 多言語対応に強く、複数の入力メソッドをグループ化して切り替えられる。多言語環境ではこちらが主流 |
| **ibus** | GNOME のデフォルト。単一言語であれば十分だが、多言語の切り替えは fcitx5 の方がスムーズ |

この記事では、fcitx5 を使って以下の3言語を1つのキーで切り替えられる環境を構築します。

<!-- TODO: タスクトレイのアイコンが keyboard-jp → mozc → pinyin と切り替わるスクリーンショット3枚 or GIF -->


| 言語 | 入力メソッド | 説明 |
|---|---|---|
| 英語 | `keyboard-jp` | JIS 配列キーボードでそのまま英数入力 |
| 日本語 | `mozc` | Google 日本語入力の OSS 版。Linux 日本語入力のデファクトスタンダード |
| 中国語 | `pinyin` | fcitx5 内蔵のピンイン入力エンジン。簡体字・繁体字の両方に対応 |

動作環境は Debian 13 (trixie) + Xfce4 ですが、他のディストリビューションやデスクトップ環境でも手順はほぼ同じです。

---

## パッケージのインストール

必要なパッケージをインストールします。

```bash
sudo apt install fcitx5 fcitx5-mozc fcitx5-chinese-addons
```

| パッケージ | 用途 |
|---|---|
| `fcitx5` | 入力メソッドフレームワーク本体 |
| `fcitx5-mozc` | 日本語入力エンジン（Mozc） |
| `fcitx5-chinese-addons` | 中国語入力のメタパッケージ（pinyin、簡繁変換等を含む） |

`fcitx5-chinese-addons` をインストールすると、依存関係で `fcitx5-pinyin`（ピンイン入力エンジン）や簡繁変換アドオンなども一緒にインストールされます。

---

## 環境変数の設定

fcitx5 をすべてのアプリケーションで使えるようにするため、以下の環境変数が必要です。

```bash
export XMODIFIERS=@im=fcitx
export GTK_IM_MODULE=fcitx
export QT_IM_MODULE=fcitx
```

Debian では `im-config` コマンドで設定するのが標準的な方法です。

```bash
im-config -n fcitx5
```

これにより `~/.xinputrc` に `run_im fcitx5` が書き込まれ、X セッション開始時に `/etc/X11/Xsession.d/70im-config_launch` 経由で環境変数が自動的に設定されます。手動で `~/.xprofile` 等に書く必要はありません。

設定後、ログインし直すと反映されます。

---

## プロファイルの設定

fcitx5 のプロファイル（`~/.config/fcitx5/profile`）で、使用する入力メソッドを定義します。

```ini
[Groups/0]
# Group Name
Name=Default
# Layout
Default Layout=jp
# Default Input Method
DefaultIM=mozc

[Groups/0/Items/0]
# Name
Name=keyboard-jp
# Layout
Layout=

[Groups/0/Items/1]
# Name
Name=mozc
# Layout
Layout=

[Groups/0/Items/2]
# Name
Name=pinyin
# Layout
Layout=

[GroupOrder]
0=Default
```

- `Default Layout=jp` — ベースのキーボードレイアウトを JIS 配列に設定
- `DefaultIM=mozc` — デフォルトの入力メソッドを Mozc に設定
- `Items/0`〜`Items/2` — トリガーキーで順に切り替わる入力メソッドの一覧

GUI で設定する場合は `fcitx5-configtool` を使って、Input Method の一覧に keyboard-jp、mozc、pinyin を追加します。

<!-- TODO: fcitx5-configtool の Input Method 一覧画面のスクリーンショット -->

---

## ホットキーの設定

入力メソッドの切り替えキーは `~/.config/fcitx5/config` で設定します。主要な設定項目を抜粋します。

```ini
[Hotkey]
# Skip first input method while enumerating
EnumerateSkipFirst=False

[Hotkey/TriggerKeys]
0=Shift+space

[Hotkey/EnumerateGroupForwardKeys]
0=Control+Shift+Shift_R

[Behavior]
# Share Input State
ShareInputState=No
# Show preedit in application
PreeditEnabledByDefault=True
```

- **TriggerKeys** (`Shift+Space`) — 入力メソッドを順に切り替えるキー。押すたびに keyboard-jp → mozc → pinyin → keyboard-jp ... と循環します
- **EnumerateSkipFirst** (`False`) — `False` にすると keyboard-jp（英語直接入力）も切り替え対象に含まれます。`True` にすると最初の入力メソッドをスキップします
- **EnumerateGroupForwardKeys** (`Control+Shift+Shift_R`) — 入力メソッドグループ全体を切り替えるキー。グループを1つしか使わない場合は不要ですが、将来グループを追加した場合（例: 別のキーボードレイアウト用グループ）に使えます
- **ShareInputState** (`No`) — ウィンドウごとに入力メソッドの状態を独立させます

設定を変更したら fcitx5 を再起動します。`-r` は既存プロセスの置き換え（replace）、`-d` はデーモンとしてバックグラウンド実行です。

```bash
fcitx5 -r -d
```

---

## ピンインで繁体字を入力する

fcitx5-chinese-addons に含まれる「簡繁変換」アドオン（`chttrans`）を使うと、ピンイン入力のまま簡体字と繁体字を切り替えられます。別の入力メソッドを追加する必要はありません。

### 切り替え方法

ピンイン入力中に **`Ctrl+Shift+F`** を押すと、出力が簡体字から繁体字に切り替わります。もう一度押すと簡体字に戻ります。

### 設定の確認

このアドオンは `fcitx5-chinese-addons` に含まれているため、パッケージをインストールしていれば追加設定なしで使えます。`fcitx5-configtool` の Addons タブで「Simplified and Traditional Chinese Translation」が有効になっていることを確認してください。

---

## トラブルシューティング

### プロファイルがリセットされる

まれに、リブート後に `~/.config/fcitx5/profile` がデフォルト（`keyboard-jp` のみ）にリセットされることがあります。原因はクラッシュや異常終了時のプロファイル書き戻し失敗が考えられます。

対策として、正常動作時のプロファイルと設定のバックアップを取っておくことをお勧めします。

```bash
cp ~/.config/fcitx5/profile ~/.config/fcitx5/profile.bak
cp ~/.config/fcitx5/config ~/.config/fcitx5/config.bak
```

### fcitx5 が起動しない・入力できない

環境変数が正しく設定されているか確認します。

```bash
echo $XMODIFIERS    # @im=fcitx であること
echo $GTK_IM_MODULE # fcitx であること
echo $QT_IM_MODULE  # fcitx であること
```

`fcitx5-diagnose` コマンドを実行すると、設定の問題を包括的に診断できます。

---

## まとめ

fcitx5 で日本語・中国語・英語の3言語入力環境を構築しました。

- **fcitx5** — 多言語切り替えに適した入力メソッドフレームワーク
- **mozc** — 日本語入力のデファクトスタンダード
- **pinyin** — 中国語ピンイン入力。`Ctrl+Shift+F` で簡繁変換も可能
- **Shift+Space** 一つで3言語を循環切り替え

設定ファイルは `~/.config/fcitx5/profile`（入力メソッドの構成）と `~/.config/fcitx5/config`（ホットキーや動作設定）の2つだけなので、バックアップも容易です。
