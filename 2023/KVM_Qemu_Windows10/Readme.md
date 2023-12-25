Table of Contents
=================

   * [はじめに](#はじめに)
   * [Windows10インストール](#windows10インストール)
      * [事前準備](#事前準備)
         * [インストールメディア、virtioドライバのダウンロード](#インストールメディアvirtioドライバのダウンロード)
         * [必要パッケジージのインストール](#必要パッケジージのインストール)
         * [インストール先ドライブのイメージファイル作成](#インストール先ドライブのイメージファイル作成)
         * [不具合回避](#不具合回避)
      * [仮想マシンの起動とWindowsのインストール](#仮想マシンの起動とwindowsのインストール)
   * [仮想マシンの利用](#仮想マシンの利用)
      * [ライセンス認証](#ライセンス認証)
      * [ホストLinuxのネットワーク設定](#ホストlinuxのネットワーク設定)
      * [仮想マシンの起動コマンドライン](#仮想マシンの起動コマンドライン)
   * [まとめ](#まとめ)

## はじめに

最近Debian Linuxをインストールしたノートパソコン上に、KVM仮想マシンのゲストOSとして、Windows10をインストールする機会がありました。
はじめはGUI形式のvirt-managerをつかって、ボタンをポチポチ押しながらゲストOSをインストールしていました。
しかし、調べていくうちに、qemuコマンドラインのみで仮想マシンを起動しWindowsをインストールする方法にたどり着いたので、それについてまとめておこうと思います。
  
virt-managerは非常に便利ですが、libvirtやそれが依存する数多くのパッケージをインストールし、libvirtdなどをデーモンとして動かしておかなければなりません。
qemuコマンドラインのみでWindowsをインストールする方法をおさえておけば、本来不必要だったものをインストールしなくて済みますし、構成がシンプルであるため動作の仕組みが容易に理解でき、なにかトラブルがあった場合にも比較的容易にデバッグが可能になると期待できます。

## Windows10インストール

### 事前準備

#### インストールメディア、virtioドライバのダウンロード

まず、あらかじめ必要なものをダウンロードしておきます。
* Windows10のインストールメディアWin10_22H2_Japanese_x64.isoを、[Microsoftのページ](https://www.microsoft.com/ja-jp/software-download/windows10ISO)からダウンロードする。
* virtioドライバをが必要になるので、[Fedoraのページ](https://fedorapeople.org/groups/virt/virtio-win/direct-downloads/archive-virtio/)からダウンロードします。今回は、この記事の執筆時点で最新のvirtio-win-0.1.229.isoを利用しました。

#### 必要パッケジージのインストール
  
```
sudo apt-get install qemu-system-x86 virt-viewer
```

#### インストール先ドライブのイメージファイル作成
Windowsのインストール先として、40Gbyteのqcow2イメージファイルを作成します。
```
qemu-img create -f qcow2 win10.qcow2 40G
```

#### 不具合回避

後述のコマンドラインで仮想マシンを起動しようとすると、以下のようなエラーメッセージが出て、仮想マシンが起動できない。
```
qemu-system-x86_64: info: Launching display with URI: spice+unix:///tmp/.BHI811/spice.sock
qemu-system-x86_64: Failed to launch spice+unix:///tmp/.BHI811/spice.sock URI: Operation not supported
qemu-system-x86_64: You need a capable Spice client, such as virt-viewer 8.0
```

これを回避するために/root/.config/mimeapps.listに以下の行を追加する。
```
[Added Associations]
x-scheme-handler/spice+unix=remote-viewer.desktop
```


### 仮想マシンの起動とWindowsのインストール

以下のコマンドで仮想マシンを起動すると、Windowsのインストーラーウィンドウが現れますので、画面の指示に従ってインストールを進めます。
```
sudo qemu-system-x86_64 \
  -machine q35,accel=kvm \
  -m 8192 -cpu host \
  -smp 6,sockets=1,dies=1,cores=6,threads=1 \
  -display spice-app \
  -rtc base=localtime,clock=host \
  -drive file=./win10pro.qcow2,if=virtio,format=qcow2,discard=unmap \
  -drive file=./Win10_22H2_Japanese_x64.iso,index=0,media=cdrom \
  -drive file=./virtio-win-0.1.229.iso,index=1,media=cdrom

  ```

* 最初はインストール先のドライブが見えないですが、ドライバーの読み込み→E:ドライブ→amd64→win10ディレクトリを選択しOKを押すと、virtioドライバが読み込まれ、ドライブ0が見えるようになります。
* Windows10のインストールメディアにはいくつかのバージョンのWindowsが入っており、プロダクトキーの入力をスキップすると、インストールするバージョンを選択できるようになります。HomeかProかをそこで選択します。
* Windowsのインストールを進めると、Microsoftアカウントへのサインインを求められますが、ローカルアカウントを作成し次に進めます。
* ローカルアカウント作成の選択肢が提示されない場合は、メールアドレスにno@thankyou.com、パスワードに適当な文字列を入力するといったんサインインに失敗し、ローカルアカウント作成ができるようになるようです。
* 上記の仮想マシン起動コマンドではネットワークの設定を行っていないので、いずれにせよWindowsサインインは行われないはずです。
* Windowsセットアップ完了後、Windows上でE:ドライブ（virtio-win-0.1.229）を開きます。そこにあるインストーラを起動し、virtioドライバをインストールしておきます。

以上で、Windows10がインストールされたKVM用のqcow2イメージができあがります。
  
  <a href="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjMNDMl1ktluDNjThzpRU_ofKyib4MDPEpTyaIzR4p0xDpUGUhSzWvJ17_Sy7iUQeGjOgrVcK1V2UiqdOtv6FGFuEzPreRMYHNN6wbQI3T9kfcWkXccRZd3HTCiKPyRWY-_8wSomn2aBSxXwVUgPUw17-bQnBklLsVP5tJe4clUH0UzHBbRw5IboxqB/s1920/KVM_Win10pro01.png" target="_blank"><img src="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjMNDMl1ktluDNjThzpRU_ofKyib4MDPEpTyaIzR4p0xDpUGUhSzWvJ17_Sy7iUQeGjOgrVcK1V2UiqdOtv6FGFuEzPreRMYHNN6wbQI3T9kfcWkXccRZd3HTCiKPyRWY-_8wSomn2aBSxXwVUgPUw17-bQnBklLsVP5tJe4clUH0UzHBbRw5IboxqB/s1920/KVM_Win10pro01.png" width="45%"></a>
  <a href="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgPv7yX7d5eWuv_mNzsb2bCXsLl0FoWXVCDD9HwnKzNXfloJT_pk_ZPxBnOX26uOxFSKwf9QL4MXVX-O0yVE1VGXuPc71nohgm8PkFm3jPWwvq_OnJwah-EDUMPjoRlq_pqXjkTVQnFSCaEXbXLwiczgI9mXTLuwCbIv3dJAllPddU4KaZCzOVErbpO/s1920/KVM_Win10pro02.png" target="_blank"><img src="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgPv7yX7d5eWuv_mNzsb2bCXsLl0FoWXVCDD9HwnKzNXfloJT_pk_ZPxBnOX26uOxFSKwf9QL4MXVX-O0yVE1VGXuPc71nohgm8PkFm3jPWwvq_OnJwah-EDUMPjoRlq_pqXjkTVQnFSCaEXbXLwiczgI9mXTLuwCbIv3dJAllPddU4KaZCzOVErbpO/s1920/KVM_Win10pro02.png" width="45%"></a>

## 仮想マシンの利用

### ライセンス認証

  基本的に仮想マシン一台ごとにライセンスが必要ですので、仮想マシンのWindows上でプロダクトキーを入力し、ライセンス認証を行います。Windowsを消し、Linuxをインストールしたノートパソコン上では、プリインストールしてあったWindowsのプロダクトキーが利用可能であると思われます。しかし、あまり不正確なことはここに書けないので参考にしたリンクのみを以下に示します。

  * http://blog.yottun8.com/archives/794
  * https://orebibou.com/ja/home/201905/20190527_001/
  	* https://superuser.com/questions/1313241/install-windows-10-from-an-unbooted-oem-drive-into-virtualbox
  	* https://gist.github.com/Informatic/49bd034d43e054bd1d8d4fec38c305ec

### ホストLinuxのネットワーク設定
  
  仮想マシンのネットワーク接続についてはいくつもやり方があります。私の場合、ゲストOSがWindowsであるかLinuxにあるかに関わらず、以下の方式を好んで利用しています。
  * 仮想マシン用のブリッジを予め作成しておき、仮想マシンの起動時にそこにアタッチする。
  * 外部へはSNAT(MASQUERADE)で接続する。
  * ネットワークアドレスは、10.0.0.0/24を利用する。
  * 仮想マシン上ではその帯域の固定IPを利用する。
  * DNSサーバは、ホストOSが使っているのと同じもの利用する。

  ブリッジインターフェースの作成は、Linuxのネットワーク設定ファイルに書いておき、ノートパソコン起動時に自動的に設定が行われます。

```
/etc/network/interfaces.d/kbr0
auto kbr0
iface kbr0 inet static
	bridge_ports none
	bridge_fd 0
	bridge_maxwait 0
	address 10.0.0.254
	netmask 255.255.255.0
	up /etc/network/masquerade.sh

  ```
  
  iptables natの設定
  ```
/etc/network/masquerade.sh 

#!/bin/bash

if ! iptables -t nat -C POSTROUTING -o eth0 -j MASQUERADE > /dev/null 2>&1 ; then 
	iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
fi

  ```

仮想マシン起動時に仮想マシンのネットワークインターフェースをホストLinuxのブリッジにアタッチするためのスクリプトも用意しておきます。
```
/etc/network/qemu-ifup

#!/bin/sh

bridge=kbr0
/sbin/ip link set dev $1 up promisc off
/sbin/brctl addif $bridge $1

  ```

### 仮想マシンの起動コマンドライン


ネットワーク接続込のコマンドライン。
```
sudo qemu-system-x86_64 \
  -machine q35,accel=kvm \
  -m 8192 -cpu host \
  -smp 6,sockets=1,dies=1,cores=6,threads=1 \
  -display spice-app \
  -rtc base=localtime,clock=host \
  -drive file=./win10pro.qcow2,if=virtio,format=qcow2,discard=unmap \
  -device virtio-net-pci,netdev=dev1,mac=52:54:00:11:00:12,id=net1 \
  -netdev tap,id=dev1,vhost=on,script=/etc/network/qemu-ifup

  ```

そして、仮想マシンの起動後、Windows上でIPアドレス、DNSサーバー等の設定を行います。

## まとめ

QEMUコマンドのみでKVM仮想マシンを起動し、Windows10をインストールする方法についてまとめました。
ネット上にはvirshコマンドラインや、virt-managerのGUIでのインストール方法はよく見かけますが、qemuコマンドのみでのやり方はあまり多くないようです。
余計なものはなるべくインストールしたくない人、ソフトウェアスタックをミニマムにして中身を理解しながら使いたい人のお役に立てば幸いです。
  
