+++
title = "debian jessieをdebootstrapでインストールした時のメモ"
date = 2015-10-14
path = "2015/10/debian-jessiedebootstrap.html"
+++

こんばんは。

ブログを書くのは苦手だけど、なんでもいいから書いてみようシリーズです。

会社ではディスクレスのネットブート環境を作ってあって、新しいOSをインストールする時には、まずディスクレスでOSを立ち上げそのOS上でdebootstrapやyum groupinstallなどを使ってファイルシステムの中身を作成することが多いです。あるいはディスクレスでブートして、あらかじめ作成しておいた標準システムをネットワーク越しrsyncやddでコピーしたりすることもあります。

このようにすることで、毎回ブレの少ない、あるいは全くブレのないイメージを作成することができ、非常に便利です。

今回は、ネットブートした後にDebian jessieをdebootstrapした時のメモです。

そして想定読者は、未来の自分です。（最近前にやったことをすぐに忘れてしまうので^^;）

1. ネットブートしたOS上でやること。

apt.h.ccmp.jp:3142がMIRROR元のURLに挟んであるのは、apt-cacher-ngを間に挟んでaptの転送量を節約するためです。

```
 parted /dev/sda
 mkfs.ext4 /dev/sda1
 mkswap /dev/sda2
 mount /dev/sda1 /mnt/
 apt-get install debootstrap
 time debootstrap --include=openssh-server,openssh-client,rsync,pciutils,tcpdump,strace,libpam-systemd,ntpdate,openntpd jessie /mnt/ http://apt.h.ccmp.jp:3142/ftp.jp.debian.org/debian
 mount -t proc none /mnt/proc/
 mount -t devtmpfs none /mnt/dev/
 mount -t sysfs none /mnt/sys/
 rsync -av  ~/.ssh/ /mnt/root/.ssh/
 vi /mnt/etc/network/interfaces
 vi /mnt/etc/fstab
 echo "root:root" | chpasswd --root /mnt/
 echo "Asia/Tokyo" >  /mnt/etc/timezone
 cp /mnt/usr/share/zoneinfo/Japan /mnt/etc/localtime
 chroot /mnt/
```

/etc/fstabの中身

```
 /dev/sda1       /       ext4   defaults       1   1
 /dev/sda2       swap     swap   defaults       0   0
```

/etc/network/interfacesの中身

```
auto lo
iface lo inet loopback

auto eth0
#iface eth0 inet dhcp

iface eth0 inet static
        address         192.168.60.31
        network         192.168.60.0
        broadcast       192.168.63.255
        netmask         255.255.252.0
        gateway         192.168.60.1

source-directory /etc/network/interfaces.d/
```

2. chroot後にイメージ内でやること

```
 apt-cache search linux-image
 apt-get install linux-image-3.16.0-4-amd64  grub-pc
 apt-get clean
 grub-install /dev/sda
 update-grub
```

以上で、jessieのミニマム環境がインストールできます。
リブートしてちゃんと立ち上がればOKです。

そんなこんなで、立ち上がったOSの容量は。。。

```
 root@jessie64:~# df -h
 Filesystem   Size Used Avail Use% Mounted on
 /dev/root       107G  585M  101G   1% /
```

うーん、こんなもんかなー。
