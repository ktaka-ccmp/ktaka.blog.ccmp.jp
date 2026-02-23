+++
title = "pppoe接続のインターフェース名を変更する　How to rename pppoe interface name."
date = 2015-10-14
path = "2015/10/pppoehow-to-rename-pppoe-interface-name.html"
+++

フレッツ回線などで、linuxルーターからpppoeセッションを張る場合、インターフェース名がppp0、ppp1などとなり、どのプロバイダへの接続なのか判別しづらく不便に感じることがあります。

```
 # ip add show dev ppp0
 8: ppp0:  mtu 1454 qdisc pfifo_fast state UNKNOWN qlen 3
   link/ppp
   inet x.x.x.x peer x.x.x.x/32 scope global ppp0
     valid_lft forever preferred_lft forever
```

ここで、ppp0の部分を任意の名前、例えば接続先のプロバイダ名などにしておけば便利でしょう。Debian Wheezyの場合は次のようにしてやれば、そういうことが可能です。

/etc/network/interfaces

```
 auto irevo
 iface irevo inet ppp
    provider irevo
```

/etc/ppp/peers/irevo

```
 noipdefault
 hide-password
 lcp-echo-interval 20
 lcp-echo-failure 3
 connect /bin/true
 noauth
 persist
 mtu 1492
 noaccomp
 default-asyncmap
 linkname "irevo"
 plugin rp-pppoe.so eth0.10
 user "xxxxx@i-revonet.jp"
```

/etc/ppp/ip-up.d/02ifrename

```
 #!/bin/bash
 ifrename(){
 if [ "$LINKNAME" != "" ]; then
     ip link set $IFNAME down
     ip link set $IFNAME name $LINKNAME
     ip link set $LINKNAME up
 else
     exit
 fi
 }
 if [ "$IFNAME" == "$(/sbin/ip route |grep default | cut -f 3 -d " ")" ]; then
     ifrename
     /sbin/ip route add default dev $LINKNAME
 else
     ifrename
 fi
```

試してみると確かにインターフェース名がirevoになっていることがわかりました。

```
 # ip add show dev irevo
 5: irevo:  mtu 1454 qdisc pfifo_fast state UNKNOWN qlen 3
   link/ppp
   inet x.x.x.x peer x.x.x.x/32 scope global irevo
     valid_lft forever preferred_lft forever
```

Debian Jessie以降ではpppdに以下のページの修正が入っていて、上記の/etc/ppp/peers/irevoで「linkname "irevo"」とあるところを「ifname "irevo"」

などに変更することで、インターフェースの名前を任意に設定することができるそうです。

[https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=458646](https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=458646)

おそらく、こちらの方がpppdが知っている名前を変えずに済み問題が少いでしょう。

早く、ルーターのOSをDebian jessieにしようと思います。
