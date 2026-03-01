+++
title = "マイKVM環境を晒しておきます。My Jessie on Jessie KVM environment."
date = 2015-10-29
description = "Debian jessie上でlibvirtを使わずに自家製スクリプトでKVM仮想マシンを管理する環境の紹介と使い方。"
path = "2015/10/kvmmy-jessie-on-jessie-kvm-environment.html"
+++

皆さん、こんにちは。もうすっかり秋ですね。

最近、寒暖差が激しいので、お体には気をつけてくださいね。

さてさて、本日は、弊社で使っているDebian Jessie用のKVM環境をご紹介します。

KVMとはKernel Virtual Machineの略で、Linuxのカーネルで実装された仮想マシンハイパーバイザーのことです。一般的には、ハイパーバイザー自体を指すよりも、それを用いた仮想マシンの方式のことを指す場合も多いかと思います。

弊社ではKVMによる仮想環境を用い、各種サーバプログラム、WEBクラスターなどの検証を行っています。最近のLinuxディストリビューションでは、すでに簡単な操作で仮想マシンを立ち上げることが可能です。しかし、kvmが最初にバニラカーネルに組み込まれたlinux-2.6.20の頃から自家製スクリプトでkvm仮想マシンを利用しており、それが使い易く、興味を持ってくれる人もいるかもしれないのでここに公開する次第です。

仮想マシンの抽象化ライブラリであるlibvirtを介さずGUIなども無いので、比較的仕組みが理解しやすくカスタマイズが簡単であることがメリットかと考えています。カーネルの最新機能や最新のqemuに追従することもたやすくできます。

それでですね、ものはここにおいてあります。

[https://github.com/ktaka-ccmp/kvm-setup-jessie](https://github.com/ktaka-ccmp/kvm-setup-jessie)

Debian jessieで以下のように、

```
 sudo apt-get install make aptitude git -y
 git clone git@github.com:ktaka-ccmp/kvm-setup-jessie.git
 sudo make all
```

- gitとmakeとaptitudeをaptでインストール

- githubからツールをクローン

- make allする

を行えばオッケーです。busyboxとkernelのコンパイル時にmenuconfig画面が表示されますが、通常はそのままExitしてください。

何か思うところがあってカスタマイズしたい場合は、そこでカスタマイズを行ってください。

仮想マシンの実行は、/kvm/sbin/kvmスクリプトで行います。中身を見てもらえばわかりますが、このスクリプトでやっていることは、qemuコマンドの実行と、unix domainソケットを通してのqemuプロセスの制御です。

ではまず、v001という仮想マシンを起動してみます。

```
 root@jessie64:~# kvm create v001
 booting v001 ....
```

v001が生きているかどうかは、次のように確認できます。

```
 root@jessie64:~# kvm chk v001
 QEMU 2.4.0.1 monitor - type 'help' for more information
 (qemu) info status
 VM status: running
 (qemu)
```

次にv002を起動し、状態を確認してみます。

```
 root@jessie64:~# kvm create v002
 booting v002 ....
 root@jessie64:~# kvm chk v002
 QEMU 2.4.0.1 monitor - type 'help' for more information
 (qemu) info status
 VM status: running
 (qemu)
```

稼働中の仮想マシンの一覧は、以下のように確認できます。conのカラムはコンソールソケット、monのカラムはモニターソケット、imgのカラムはVMのイメージファイルの状態を表しています。v001の行を見るとv001 o o uとなっていますが、これはコンソール、モニターの両ソケットが接続可能で、イメージファイルが使用中(VMが稼働中)であることを表しています。

```
 root@jessie64:~# kvm list
 id   con   mon   img
 test  -    -    -
 v001  o    o    u
 v002  o    o    u
```

今度は、v001のコンソールに接続してみます。コンソールに接続するとログインプロンプトが表示されるのでroot/rootでログインします。rootのパスワードはMakefileにベタ書きしてあり、イメージtemplate作成時に設定されます。コンソール接続を終了するには"Ctrl+]"をタイプします。

```
 root@jessie64:~# kvm con v001
 Debian GNU/Linux 8 v001 ttyS0
 v001 login: root
 Password:
 Linux v001 4.2.4-64kvmg01 #1 SMP Wed Oct 28 03:50:51 UTC 2015 x86_64
 The programs included with the Debian GNU/Linux system are free software;
 the exact distribution terms for each program are described in the
 individual files in /usr/share/doc/*/copyright.
 Debian GNU/Linux comes with ABSOLUTELY NO WARRANTY, to the extent
 permitted by applicable law.
 root@v001:~# logout
 Debian GNU/Linux 8 v001 ttyS0
 v001 login:
```

テンプレートイメージ作成時には、/root/.ssh/authorized_keysもコピーしていますので、ホストのマシンと同じ鍵でsshログインすることが可能です。

v001のIPアドレスはinitrdの中で172.16.1.1を決め打ちで設定しています。v002の場合は172.16.1.2、v250の場合は172.16.1.250が割り当てられ、v250を上限にしてあります。

これらのホスト名、IPは、セットアップ時にホストの/etc/hostsに追記してあります。

```
 root@jessie64:~# ssh v001
 The programs included with the Debian GNU/Linux system are free software;
 the exact distribution terms for each program are described in the
 individual files in /usr/share/doc/*/copyright.
 Debian GNU/Linux comes with ABSOLUTELY NO WARRANTY, to the extent
 permitted by applicable law.
 Last login: Thu Oct 29 16:42:31 2015 from 172.16.1.254
 root@v001:~#
```

ゲストマシンからは、ホストマシンのNATを介して外部のネットワークと通信が可能です。

```
 root@v001:~# ping yahoo.jp
 PING yahoo.jp (183.79.227.111) 56(84) bytes of data.
 64 bytes from yjpn110.mobile.vip.ogk.yahoo.co.jp (183.79.227.111): icmp_seq=1 ttl=54 time=13.2 ms
 64 bytes from yjpn110.mobile.vip.ogk.yahoo.co.jp (183.79.227.111): icmp_seq=2 ttl=54 time=13.3 ms
 64 bytes from yjpn110.mobile.vip.ogk.yahoo.co.jp (183.79.227.111): icmp_seq=3 ttl=54 time=13.9 ms
 ^C
 --- yahoo.jp ping statistics ---
 3 packets transmitted, 3 received, 0% packet loss, time 2001ms
 rtt min/avg/max/mdev = 13.224/13.515/13.986/0.349 ms
```

また、同じホスト上の仮想マシン間で通信することも可能です。

```
 root@v001:~# ping v002
 PING v002 (172.16.1.2) 56(84) bytes of data.
 64 bytes from v002 (172.16.1.2): icmp_seq=1 ttl=64 time=1.33 ms
 64 bytes from v002 (172.16.1.2): icmp_seq=2 ttl=64 time=1.89 ms
 64 bytes from v002 (172.16.1.2): icmp_seq=3 ttl=64 time=5.51 ms
 ^C
 --- v002 ping statistics ---
 3 packets transmitted, 3 received, 0% packet loss, time 2003ms
 rtt min/avg/max/mdev = 1.331/2.914/5.519/1.856 ms
```

別ホストからは、直接仮想マシンにアクセスできないようになっていますので、別ホスト上の仮想マシンとは通信できません。もしそうしたい場合は、ブリッジとvlanの設定を工夫することで、通信可能になるでしょう。

仮想マシンを停止したいときは、仮想マシンにログインしpoweroffを実行するか、以下のようにshutdownコマンドを発行します。

```
 root@jessie64:~# kvm shutdown v001
 QEMU 2.4.0.1 monitor - type 'help' for more information
 (qemu) system_powerdown
 (qemu)
 root@jessie64:~# kvm chk v001
 2015/10/29 17:04:52 socat[17586] E connect(5, AF=1 "/kvm/monitor/v001.sock", 24): Connection refused
```

kvm listコマンドで見ると、停止しているv001は以下のように見えます。

```
 root@jessie64:~# kvm list
 id   con   mon   img
 test  -    -    -
 v001  -    -    -
 v002  o    o    u
```

v001のイメージを完全に消したいときは、仮想マシンが停止した状態で、/kvm/data/v001.imgを消してください。

だいたい使い方は以上になります。

どうぞ、よろしくお願いいたします。
