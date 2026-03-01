+++
title = "LinuxでのSLAAC IPv6アドレス自動設定"
date = 2020-05-17
description = "LinuxカーネルのSLAAC addr_gen_modeパラメータの各モード（EUI64、RFC7217 SOII等）の違いと設定方法の解説。"
path = "2020/05/linuxslaac-ipv6.html"
+++

Linuxにおいて、SLAACによるIPv6アドレスアサインにはいくつかのモードがあり、以下のカーネルパラメータをセットすることで制御できるようです。

```
addr_gen_mode - INTEGER
	Defines how link-local and autoconf addresses are generated.
	0: generate address based on EUI64 (default)
	1: do no generate a link-local address, use EUI64 for addresses generated
	   from autoconf
	2: generate stable privacy addresses, using the secret from
	   stable_secret (RFC7217)
	3: generate stable privacy addresses, using a random secret if unset
```

モード２のRFC7217形式を利用するためには以下のように、stable_secretをあらかじめセットしておく必要があります。

```
stable_secret - IPv6 address
	This IPv6 address will be used as a secret to generate IPv6
	addresses for link-local addresses and autoconfigured
	ones. All addresses generated after setting this secret will
	be stable privacy ones by default. This can be changed via the
	addrgenmode ip-link. conf/default/stable_secret is used as the
	secret for the namespace, the interface specific ones can
	overwrite that. Writes to conf/all/stable_secret are refused.

	It is recommended to generate this secret during installation
	of a system and keep it stable after that.

	By default the stable secret is unset.
```

[https://www.kernel.org/doc/Documentation/networking/ip-sysctl.txt](https://www.kernel.org/doc/Documentation/networking/ip-sysctl.txt)

#### モード0:

[RFC4291](https://tools.ietf.org/html/rfc4291#appendix-A)形式のアドレスを自動生成します。

```
# echo 0 > /proc/sys/net/ipv6/conf/eth0/addr_gen_mode
# ifdown eth0; ifup eth0
# ip -6 add show dev eth0
4: eth0: &lt;BROADCAST,MULTICAST,UP,LOWER_UP&gt; mtu 1500 state UP qlen 1000
    inet6 fd00::40:c23f:d5ff:fe69:4af3/64 scope global dynamic mngtmpaddr
       valid_lft 86383sec preferred_lft 14383sec
    inet6 fe80::c23f:d5ff:fe69:4af3/64 scope link
       valid_lft forever preferred_lft forever
```

IPv6アドレスはRAから得られたPREFIX(fd00::40/64)と、MACアドレス(c0:3f:d5:69:4a:f3)を変換したEUI64アドレス(c23f:d5ff:fe69:4af3)から生成されていることがわかります。

#### モード1:

アドレスを自動生成しません。

```
# echo 1 > /proc/sys/net/ipv6/conf/eth0/addr_gen_mode
# ifdown eth0; ifup eth0
# ip -6 add show dev eth0
#
```

#### モード2:

Semantically Opaque Interface Identifiers(SOII, [RFC7217](https://tools.ietf.org/html/rfc7217))形式のアドレスを自動生成します。

```
# echo "::" > /proc/sys/net/ipv6/conf/eth0/stable_secret
# echo 2 > /proc/sys/net/ipv6/conf/eth0/addr_gen_mode
# ifdown eth0; ifup eth0
# ip -6 add show dev eth0
4: eth0:  mtu 1500 state UP qlen 1000
    inet6 fd00::40:c81b:6763:31dc:887a/64 scope global dynamic mngtmpaddr stable-privacy
       valid_lft 86398sec preferred_lft 14398sec
    inet6 fe80::df74:fff4:bdf2:e8ae/64 scope link stable-privacy
       valid_lft forever preferred_lft forever
```

IPv6アドレスはRAから得られたPREFIX(fd00::40/64)と、[RFC7217](https://tools.ietf.org/html/rfc7217)に定められた方式で計算されるランダム識別子から生成されます。ランダム識別子は次のような関数から計算されsecret_keyに変更がなければ(すなわちstable_secretがセットされていれば)、毎回同じものになります。

```
RID = F(Prefix, Net_Iface, Network_ID, DAD_Counter, secret_key)
```

#### モード3:

Semantically Opaque Interface Identifiers(SOII, RFC7217形式のアドレスを自動生成します。stable_secretがセットされている場合にはモード2と同じアドレスを生成し、されていない場合にはrandom secretを用いアドレスを生成します。

```
# echo 3 > /proc/sys/net/ipv6/conf/eth0/addr_gen_mode
# ifdown eth0; ifup eth0
# ip -6 add show dev eth0
4: eth0:  mtu 1500 state UP qlen 1000
    inet6 fd00::40:73be:87b2:8746:6bb3/64 scope global dynamic mngtmpaddr stable-privacy
       valid_lft 86395sec preferred_lft 14395sec
    inet6 fe80::ddae:cc16:47e0:156d/64 scope link stable-privacy
       valid_lft forever preferred_lft forever
```

モード2との違いは、stable_secretがセットされていない場合に、毎回異なるランダム識別子からIPv6アドレスが生成されるということです。

addr_gen_modeのパラメータは以下のコマンドでもセットできるようです。

```
ip link set dev eth0 addrgenmode  { eui64 | none | stable_secret | random }
```

#### 参考文献

「クライアントOSのIPv6実装検証から見たネットワーク運用における課題の考察」

[https://www.ipsj.or.jp/dp/contents/publication/36/S0904-R1701.html](https://www.ipsj.or.jp/dp/contents/publication/36/S0904-R1701.html)

「TIPS: 拡張EUI-64を使わないIPv6アドレス生成」

[http://www.drvlabo.jp/wp/archives/1713](http://www.drvlabo.jp/wp/archives/1713)
