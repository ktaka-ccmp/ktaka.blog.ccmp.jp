+++
title = "Kernel Virtual Machine(kvm)のセットアップ"
date = 2012-02-15
path = "2012/02/kvm.html"
+++

いくつもあるサーバを、仮想化によりまとめることができれば、サーバの保管場所や電気代の節約になる。私の会社ではいくつかのサーバを仮想マシン上で運用している。kvmによる仮想環境の再構築する機会があったので、備忘録的にノウハウというか、工夫した部分について、まとめておきたいと思う。

kvmはそれ用に構築したLinuxカーネルをハイパーバイザーとする仮想マシンである。GuestOSはWindowsやLinuxのみならず、様々なOSがサポートされている。

[http://www.linux-kvm.org/page/Guest_Support_Status](http://www.linux-kvm.org/page/Guest_Support_Status)　

今回はDebianLinux上で、バニラカーネルをkvmホスト用に自前でコンパイルしたものに入れ替え、ゲストOSとしてDebianLinuxを複数動かせるようにする。ゲストOSはWEBサーバなどのネットワークサーバ用途を想定しているので、GUI機能は必要ない。したがって、コンソールログインとSSHログインが可能になれば良しとすることにした。

最近のDebianLinuxでは、おそらく標準でGUIを使ってkvmを利用可能である。しかし、仕事で使うとなると中身や仕組みをできるだけ熟知していたくもあるので、余分な機能で被われたディストリビューション標準のツールをあえて使わないことにした。

ハードウェアは、ちょっと昔のDellT105が遊んでいたので、これを使うことにした。今となってはそれほど強力なマシンではないが、4コアのAMD Opteronを搭載しており、メモリスロットも4つある。これにDDR2 ECC 2GBを4本積んで、8GBのメモリを確保した。

<img src="/2012/02/kvm.html/image/IMG_1596.JPG" width="320" height="240">

<img src="/2012/02/kvm.html/image/IMG_1605.JPG" width="320" height="240">

**1. ハードウェアスペック**
**
**

```
CPU: Quad-Core AMD Opteron 1352,  2.1GHz, cache 512 KB
MEM: DDR2 800MHz ECC Unbuffered 4GB x8
HDD: Seagate ST3320613AS 320GB SATA
NIC: Broadcom NetXtreme BCM5722
```

kvmで仮想マシンを作る場合、IntelのCPUであればIntel VT、AMDのCPUであればAMD-Vに対応している必要がある。CPUのそれらの仮想化支援機能が無ければただの低速エミュレーターになってしまう。

CPUにそれらの機能が備わっているかどうかはメーカーのサイトで確認してもいいし、Linuxが既に動いている実機上で、以下のように確認しても良い。

AMDのマシンであれば、/proc/cpuinfoのflagsを見て、svmというのがあれば良い。

```
root@kvm:~# egrep flags /proc/cpuinfo |head -n 1
flags  : fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca
cmov pat pse36 clflush mmx fxsr sse sse2 ht syscall nx mmxext
fxsr_opt pdpe1gb rdtscp lm 3dnowext 3dnow constant_tsc
rep_good nopl nonstop_tsc extd_apicid pni monitor cx16 popcnt
lahf_lm cmp_legacy svm extapic cr8_legacy abm sse4a misalignsse
3dnowprefetch osvw ibs npt lbrv svm_lock
```

Intelのマシンの場合、vmxというのがあれば良い。

```
ktaka@hana:~$ egrep flags /proc/cpuinfo |head -n 1
flags  : fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge
mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm
pbe syscall nx pdpe1gb rdtscp lm constant_tsc arch_perfmon pebs
bts rep_good nopl xtopology nonstop_tsc aperfmperf pni
pclmulqdq dtes64 monitor ds_cpl vmx smx est tm2 ssse3 cx16 xtpr
pdcm pcid dca sse4_1 sse4_2 popcnt aes lahf_lm ida arat epb
dts tpr_shadow vnmi flexpriority ept vpid
```

**
**

**2. ホストカーネルの構築**

カーネルはkernel.orgにあるlinux-3.2.9をコンパイルして利用する。

[このページ](http://www.linux-kvm.org/page/Tuning_Kernel)にKVMのホストカーネルの構築に必要なコンパイルフラグがまとめてあるので、これを参考にカーネルを構築した。実際には以下の関連フラグを有効にした。

```
CONFIG_CGROUPS=y
CONFIG_CGROUP_DEBUG=y
CONFIG_CGROUP_FREEZER=y
CONFIG_CGROUP_DEVICE=y
CONFIG_CGROUP_CPUACCT=y
CONFIG_CGROUP_MEM_RES_CTLR=y
CONFIG_CGROUP_MEM_RES_CTLR_SWAP=y
CONFIG_CGROUP_MEM_RES_CTLR_SWAP_ENABLED=y
CONFIG_CGROUP_PERF=y
CONFIG_CGROUP_SCHED=y
CONFIG_BLK_CGROUP=m
CONFIG_DEBUG_BLK_CGROUP=y
CONFIG_HIGH_RES_TIMERS=y
CONFIG_HPET_TIMER=y
CONFIG_HPET_EMULATE_RTC=y
CONFIG_COMPACTION=y
CONFIG_MIGRATION=y
CONFIG_KSM=y
CONFIG_HPET=y
CONFIG_HPET_MMAP=y
CONFIG_HAVE_KVM=y
CONFIG_HAVE_KVM_IRQCHIP=y
CONFIG_HAVE_KVM_EVENTFD=y
CONFIG_KVM_APIC_ARCHITECTURE=y
CONFIG_KVM_MMIO=y
CONFIG_KVM_ASYNC_PF=y
CONFIG_VIRTUALIZATION=y
CONFIG_KVM=m
CONFIG_KVM_INTEL=m
CONFIG_KVM_AMD=m
CONFIG_KVM_MMU_AUDIT=y
CONFIG_VHOST_NET=m
```

KVMホスト上でブリッジネットワークを利用するために必要な以下のフラグも有効にした。

```
CONFIG_BRIDGE_NETFILTER=y
CONFIG_BRIDGE=m
CONFIG_BRIDGE_IGMP_SNOOPING=y
CONFIG_STP=m
CONFIG_LLC=m
```

カーネルコンパイル&インストール後、新規カーネルでブートしバージョン確認

```
root@kvm:~# uname  -a
Linux kvm 3.2.9-64kvmh01 #1 SMP Mon Mar 5 21:47:42 JST 2012
x86_64 GNU/Linux
```

関連モジュールの確認

```
root@kvm:~# lsmod |egrep "kvm|bridge"
kvm_amd                71505  0
kvm                   566158  1 kvm_amd
bridge                125971  0
stp                     2987  1 bridge
llc                     8862  2 bridge,stp
```

**3. ホストOSのネットワーク設定**

kvm用のブリッジインターフェースkbr0を作成する。

以下の内容で設定ファイル/etc/network/interfacesを作成する。

```
auto lo kbr0
iface lo inet loopback
iface kbr0 inet static
     bridge_ports    eth0
     bridge_stp      off
     bridge_maxwait  2
     address         192.168.20.9
     netmask         255.255.252.0
     network         192.168.20.0
     broadcast       192.168.20.255
     gateway         192.168.20.1
     pre-up /sbin/ip link set dev eth0 up
```

ホストOSを再起動すると、以下の様な状態になります。

ブリッジの状態確認

```
root@kvm:~# brctl show
bridge name bridge id  STP enabled interfaces
kbr0  8000.0022190601e3 no  eth0
```

ブリッジインターフェースkbr0が作成され、eth0が接続されている。

IPアドレスの確認

```
root@kvm:~# ip add
1: lo: mtu 16436 qdisc noqueue state UNKNOWN
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
2: eth0: mtu 1500 qdisc mq master kbr0 state UP qlen 1000
    link/ether 00:22:19:06:01:e3 brd ff:ff:ff:ff:ff:ff
3: kbr0: mtu 1500 qdisc noqueue state UP
    link/ether 00:22:19:06:01:e3 brd ff:ff:ff:ff:ff:ff
    inet 192.168.20.9/22 brd 192.168.20.255 scope global kbr0
```

ブリッジインターフェースkbr0に192.168.20.9というアドレスが割り当てられている。

**4. qemuのコンパイル**

kvmによる仮想マシンではLinuxハイパーバイザー上で、kvmに対応したqemuエミュレーターを動作させる。qemuエミュレータ上ではwindowsやlinuxなど、サポートされているOSをゲストOSとして起動することが可能である。

当初はkvmに対応したqemuのソースをkvmプロジェクトのサイトから取得する必要があったが、最近ではqemuの本家のソースにkvmのパッチが既にマージされている。

従って、kvmの開発の最先端のソースを利用したいと言うのでなければ、qemuの本家サイトからソースを取ってくれば良い。

```
wget http://wiki.qemu.org/download/qemu-1.0.1.tar.gz
```

普通にtarボールを展開して、コンパイル＆インストールする。

```
tar xf qemu-1.0.1.tar.gz ; cd qemu-1.0.1
./configure  --prefix=/kvm/qemu/qemu-1.0.1/ --enable-kvm
make install

tree -L 2 /kvm/qemu/
/kvm/qemu/
`-- qemu-1.0.1
    |-- bin
    |-- etc
    `-- share

root@kvm:~# /kvm/qemu/qemu-1.0.1/bin/qemu-x86_64 -version
qemu-x86_64 version 1.0,1, Copyright (c) 2003-2008 Fabrice Bellard
```

**5. ゲストOSイメージの作成**

qemuエミュレーター上で動かすゲストLinuxOSイメージを作成する。手順は以下の通り。

- スパースなイメージファイルを作成

- ext4でファイルシステム作成

- debootstrapでOSインストール

- ネットワークやルートパスワードの設定等々細々としたを行う

イメージ作成

```
dd if=/dev/zero of=./kvm.img bs=1024 seek=9999999 count=1
```

  ファイルシステム作成

```
mkfs.ext4 kvm.img
```

  debootstrapでDebianインストール

```
mount -o loop kvm.img /mnt/tmp/
debootstrap --include=openssh-server,openssh-client,\
rsync,pciutils,acpid  squeeze /mnt/tmp/
```

  その他の細々した設定

シリアルコンソール設定

/mnt/tmp/etc/inittab にttyS0の設定を加える

```
T0:23:respawn:/sbin/getty -L ttyS0 19200 vt100
```

BIOSクロックをUTCと見做さない設定(JSTのsystem dateが終了時にBIOSに書き込まれる。仮想マシンでは関係ないかも？)

/mnt/tmp/etc/default/rcS

```
UTC=no
```

ネットワーク設定(DHCPでアドレスを取得するようにする。) 

/mnt/tmp/etc/network/interfaces

```
auto lo eth0
```

```
  iface lo inet loopback
  iface eth0 inet dhcp
```

余計なudevルールの削除

```
rm /mnt/tmp/etc/udev/rules.d/70-persistent-net.rules
```

パスワード初期設定、apt-cache掃除、timezoneをJSTに。

```
chroot /mnt/tmp/
passwd
apt-get clean
dpkg-reconfigure tzdata
```

**6. ゲストカーネルのコンパイル**

kvm上で仮想マシンを動かす場合、ゲストOSは改変不要でハードウェア上で動かす場合のカーネルがそのまま動く。これはしばしば完全仮想化と呼ばれる。しかしながら、仮想マシン用のドライバを使うようにしてやることで、ゲストOSの性能を大幅に向上することが可能である。仮想マシン用のドライバを利用した方法は、しばしば準仮想化と呼ばれる。

今回も準仮想化を使いたいし、なるべく必要最小限のドライバのみを有効にした、シンプルなカーネルを使いたいので、バニラソースからカーネルをコンパイルする。

必要なコンパイルフラグは、ホストカーネルの場合と同様に[このページ](http://www.linux-kvm.org/page/Tuning_Kernel)を参考にして有効にした。結局以下の関連フラグが有効にしてある。

```
CONFIG_HOTPLUG=y
CONFIG_TICK_ONESHOT=y
CONFIG_PARAVIRT_GUEST=y
CONFIG_PARAVIRT_TIME_ACCOUNTING=y
CONFIG_KVM_CLOCK=y
CONFIG_KVM_GUEST=y
CONFIG_PARAVIRT=y
CONFIG_PARAVIRT_SPINLOCKS=y
CONFIG_PARAVIRT_CLOCK=y
CONFIG_PARAVIRT_DEBUG=y
CONFIG_MEMORY_HOTPLUG=y
CONFIG_MEMORY_HOTPLUG_SPARSE=y
CONFIG_MEMORY_HOTREMOVE=y
CONFIG_VIRT_TO_BUS=y
CONFIG_HOTPLUG_CPU=y
CONFIG_ARCH_ENABLE_MEMORY_HOTPLUG=y
CONFIG_ARCH_ENABLE_MEMORY_HOTREMOVE=y
CONFIG_ACPI_HOTPLUG_CPU=y
CONFIG_PCI_MSI=y
CONFIG_VIRTIO_BLK=y
CONFIG_VIRTIO_NET=y
CONFIG_VIRTIO_CONSOLE=y
CONFIG_HW_RANDOM_VIRTIO=y
CONFIG_VIRTIO=y
CONFIG_VIRTIO_RING=y
CONFIG_VIRTIO_PCI=y
CONFIG_VIRTIO_BALLOON=y
CONFIG_VIRTIO_MMIO=y
CONFIG_VIRT_DRIVERS=y
CONFIG_HAVE_KVM=y
```

今回、モジュールを使わずにモノリシックなカーネルにした。コンパイルしたカーネルは、適当決めたディレクトリ/kvm/bootに置いた。

```
root@kvm:~# ls -la /kvm/boot/
total 8728
drwxr-xr-x  2 root root    4096 Mar  8 03:38 .
drwxr-xr-x 10 root root    4096 Mar  6 17:12 ..
-rw-r--r--  1 root root 1105677 Mar  8 03:38 System.map-3.2.9-64kvmg01
-rw-r--r--  1 root root   44798 Mar  8 03:38 config-3.2.9-64kvmg01
-rw-r--r--  1 root root 3152304 Mar  8 03:38 vmlinuz-3.2.9-64kvmg01
```

**

**
7. ゲストOSの起動コマンド

ゲストOSはqemuエミュレーター上で動作する。ゲストOSを起動するには、qemuコマンドを適切なオプションで実行すれば良い。kvmによる仮想マシンは、ホストOS(Linuxハイパーバイザー)上からは単なるqemuプロセスに見える。従って、それぞれのゲストOSがどのくらいのCPU、メモリ等のリソースを消費しているかは、ホストOS上でqemuプロセスがどのくらいそれらのリソースを消費しているかを見れば良い。不要になったゲストOSはいざとなったら、qemuプロセスをkillコマンドでkillすることで、終了させることも可能である。(実際にはもう少し丁寧にshutdownすべきであるが。)

さて、qemuのコマンドのオプションはqemu-system-x86_64 --helpで確認することが可能である。それぞれオプションを試行錯誤し、最終的に我々にとって使い易くしたものが、以下のものである。

```
/kvm/qemu/qemu-kvm-1.0/bin/qemu-system-x86_64 \
--enable-kvm -nographic -daemonize \
-drive file=/kvm/data/kvm.img,if=virtio -m 512 \
-kernel /kvm/boot/vmlinuz-3.2.9-64kvmg01 \
-append "console=ttyS0,19200n8  root=/dev/vda" \
-net nic,vlan=0,macaddr=52:54:00:21:00:01,model=virtio \
-net tap,vlan=0,script=/kvm/etc/qemu-ifup,ifname=hoge \
-serial unix:/tmp/con.sock,server,nowait \
-monitor unix:/tmp/mon.sock,server,nowait
```

以下、それぞれのオプションについて説明する。

**--enable-kvm**　Intel-VT またはAMD-Vのハードウェア仮想化支援機能を利用する

**-nographic**  グラフィカルな出力を無効にし、シリアルをコンソールにリダイレクトする

**-daemonize**　qemuをデーモンとして起動する

**-m 512**　メモリを512MByte 割り当てる

**-smp 1** 　仮想マシンにプロセッサを一つ割り当てる

**-kernel**   ゲストカーネルを指定。イメージの外、ホストOS上に置くことができる

**-append**  カーネルに与えるオプションを指定

**-drive** **file=**　イメージファイルの指定。if=virtioオプションによりパラヴァーチャルなブロックデバイスとして見せる 

**-net nic,vlan=0,macaddr= ,model=virtio**  

NICを作成しvlan=0に接続する。model=virtioオプションによりパラバーチャルなNICに見せる。 

**-net tap,vlan=0,script=/kvm/etc/qemu-ifup,ifname=hoge**  

ホストにtapデバイスhogeを作成しvlan=0に接続する。そしてスクリプト/kvm/etc/qemu-ifupを実行する。

**-serial unix:/tmp/con.sock,server,nowait**   シリアルポートをUNIXドメインソケット/tmp/con.sockにリダイレクトする。

**-monitor unix:/tmp/mon.sock,server,nowait** 

QemuのモニターをUNIXドメインソケット/tmp/mon.sockにリダイレクトする。

serial,monitorのUNIXドメインソケットへのリダイレクトがミソ。

nographic, daemonizeオプションによりバックグラウンドで実行している仮想マシンを/tmp/mon.sock、/tmp/con.sockから制御することが可能である。serial、monitorをtcpやtelnetなどなどのネットワーク接続口にリダイレクトすることも可能であるが、その場合、認証無しでmonitorコンソールアクセスしqemuをコントロールすることができてしまう。UNIXドメインソケットを利用する場合、rootユーザのみにUNIXドメインソケットへの読み書き許可を与えることで、ホストOS上ののrootユーザのみにアクセス許可を与えることができるようになる。

**8. script=/kvm/etc/qemu-ifupで何をしているのか**

**

**

/kvm/etc/qemu-ifupの内容

```
#!/bin/sh
/sbin/ip link set dev $1 up promisc off
/usr/sbin/brctl addif kbr0 $1
```

タップデバイスhogeがブリッジkbr0に接続されている。

```
brctl show
bridge name     bridge id               STP enabled     interfaces
kbr0            8000.0022190601e3       no              eth0
                                                        hoge
```

**9. UNIXドメインソケットへの接続方法**

socatコマンドで接続可能である。

QEMUモニタへの接続

```
socat -,icanon=0,echo=0 unix-connect:/tmp/mon.sock

QEMU 1.0,1 monitor - type 'help' for more information
(qemu)
```

シリアルコンソールへの接続

```
socat -,icanon=0,echo=0 unix-connect:/tmp/con.sock

Debian GNU/Linux 6.0 (none) ttyS0

(none) login:
```

ただし、このままではctl-cでシリアルコンソール内のプロセスを終了しようとしても、socat自身がグナルを受け取ってしまうので、そのプロセスを終了することができない。その様な場合には、intrなを適当なキーに割り当てると良い。

例えば、次の様なラッパスクリプトを利用することで、socatにinterruptシグナルを送る場合のキーバインディングをctl+]に変更することができる。ctl+cを叩いた場合、socat自身gはシグナルとして受け取らず、接続先のプロセスがctl+cをinterruptシグナルとして受け取ることになる。

test_con.sh

```
#!/bin/bash
tty_setting=`stty -g`
stty intr ^]
socat -,icanon=0,echo=0 unix-connect:/tmp/con.sock
stty $tty_setting
```

**A1. 素のqemuとkvmどのくらい速さが違うの？　**

sysbenchと言うベンチマークツールを使って、簡単にCPUベンチマークを実行してみた。

ベンチマークコマンド

```
sysbench --num-threads=24 --test=cpu --cpu-max-prime=10000 run
```

素のqemu　(qemu-system-x86_64 .... )

```
Test execution summary:
    total time:                          58.5005s
```

kvmオプション付き　(qemu-system-x86_64 **--enable-kvm** .... )

```
Test execution summary:
    total time:                          17.3854s
```

約3.4倍高速であった。

**A2. qemu-kvmと本家qemuどちらを使うべき？(2012/3現在)**

以前は、kvmを使うためには、それ用にパッチの当たったqemuを使う必要があったが、現在kvmサポートパッチは本家qemuにマージされている。しかしながら、wiki.qemu.org/downloadの他にも、sourceforgeにqemu-kvmが存在している。

そこで、sysbenchでベンチマークしてみた。

ベンチマークコマンド

```
sysbench --num-threads=24 --test=cpu --cpu-max-prime=10000 run
```

qemu-1.0.1の場合(--enable-kvmオプション付き)

```
Test execution summary:
    total time:                          17.3854s
```

qemu-kvm-1.0の場合

```
Test execution summary:
    total time:                          17.2720s
```

大きな差は見られない。

以上、kvmによる仮想マシンの構築について、備忘録的にまとめた。

部分的であれ記載した情報がお役に立てば幸いである。
