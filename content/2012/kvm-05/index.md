+++
title = "KVM用のマシンの引越し"
date = 2012-05-29
path = "2012/05/kvm.html"
+++

[先日立ち上げたKVM用のマシン](http://ktaka.blog.clustcom.com/2012_02_01_archive.html)ですが、同じ機種のwindows serverマシンが故障で起動不能になってしまったため、代替機として使用することになってしまいました。そこで、弊社で過去に販売していたIntel製の1Uサーバに引っ越すことにしました。

スペックは

```
CPU: Intel QuadCore Xeon X3440, 2.53GHz, cache 8 MB　
MEM: DDR2 800MHz ECC Unbuffered 2GB x2　
HDD: Seagate ST3320613AS 320GB SATA　
NIC: Intel 82574L / 82578DM
```

と、メモリが若干少ないですが、なかなか素敵なサーバです。メモリは機会を見て増設することにします。

<img src="/2012/05/kvm.html/image/IMG_2028.JPG" width="320" height="240">

<img src="/2012/05/kvm.html/image/IMG_2030.JPG" width="320" height="240">

ちなみに、このサーバの後継機種は[こちら](http://www.clustcom.com/-mainmenu-34/205--ez1ui-e31270)になります。最新のIntel Xeon E3-12xx v2(Ivybridge)シリーズのプロセッサを搭載していて大変コストパフォーマンスに優れています。

引越し作業は次の様にしました。まず、HDDを載せ替えてブートしてみます。ネットワークが認識しなかったので、ホストカーネルをコンパイルし直しe1000eを有効にしました。

このマシンのKVM環境、前回のブログを書いてからそのまま放置していたので、まだ完成していません。

近いうちにちゃんと使えるようにしておきたいと思います。
