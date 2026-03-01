+++
title = "Debian LinuxのノートパソコンでドトールWiFiにつなぐ"
date = 2021-01-15
description = "Debian Linuxでドトールの無料WiFiに接続するためのwpa_supplicant設定とifupの手順メモ。"
path = "2021/01/debian-linuxwifi.html"
+++

ドトール、エクセルシオールカフェには無料のWiFiサービスがある。Linuxで接続するのにちょっと手間取ったので、やり方をメモしておく。

設定ファイルを作成。

```
/etc/network/interfaces.d/doutor
iface dt inet dhcp
	wpa-ssid "DOUTOR_FREE_Wi-Fi"
	wpa-key-mgmt NONE
```

インターフェースをアップするとDHCP経由でアドレスの取得ができる。

```
ktaka@dyna:~$ sudo ifup wlan0=dt
Internet Systems Consortium DHCP Client 4.4.1
Copyright 2004-2018 Internet Systems Consortium.
All rights reserved.
For info, please visit https://www.isc.org/software/dhcp/

Listening on LPF/wlan0/3c:9c:0f:8d:c8:4a
Sending on   LPF/wlan0/3c:9c:0f:8d:c8:4a
Sending on   Socket/fallback
DHCPDISCOVER on wlan0 to 255.255.255.255 port 67 interval 8
DHCPDISCOVER on wlan0 to 255.255.255.255 port 67 interval 14
DHCPOFFER of 10.68.161.211 from 10.68.128.2
DHCPREQUEST for 10.68.161.211 on wlan0 to 255.255.255.255 port 67
DHCPACK of 10.68.161.211 from 10.68.128.2
bound to 10.68.161.211 -- renewal in 138 seconds.
```

このあとブラウザで任意のページを閲覧しようとするとWEBの認証ページが表示されるので、承諾すればネットワークが使用可能になる。
