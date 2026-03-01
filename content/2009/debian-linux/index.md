+++
title = "Debian Linux でイーモバイルD31HW使う"
date = 2009-11-01
description = "Debian LinuxでイーモバイルD31HWをusb_modeswitchとpppで接続する手順。"
path = "2009/11/debian-linux.html"
+++

下り最大21Mbps、上り最大5.8Mbpsのデータ通信カード(スティック)イーモバイルのD31HWを使ってみる。

事前調査によると、このカードは、ストレージとモデムの両方の機能を持っていて、とあるコマンドを送ることによりモードを切り替えられるとのこと。ストレージは、Windowsなどで最初に接続したときに、自動的にデバイスドライバをインストールするためのものであるとのこと。

[http://blog.37to.net/2009/01/ubuntuemobiled21lc/
](http://blog.37to.net/2009/01/ubuntuemobiled21lc/)[http://show-cha.seesaa.net/article/125815364.html](http://show-cha.seesaa.net/article/125815364.html)

カードを接続しlsusb で見ると、以下のエントリが現れる。

>

> Bus 001 Device 004: ID 12d1:1446 Huawei Technologies Co., Ltd.

[ここ](http://www.draisberghof.de/usb_modeswitch/#download)から、usb_modeswitchをダウンロードしインストール。
/etc/usb_modeswitch.conf を以下の内容で作成。

> # Emobile D31HW
> DefaultVendor=  0x12d1
> DefaultProduct= 0x1446
> TargetVendor=   0x12d1
> TargetProduct=  0x1429
>
> MessageEndpoint=0x01
> MessageContent="55534243000000000000000000000011060000000000000000000000000000"

usb_modeswitchを実行すると

> vaiox:~# usb_modeswitch
>
> Looking for target devices ...
> No devices in target mode or class found
> Looking for default devices ...
> Found default devices (1)
> Accessing device 005 on bus 001 ...
> Using endpoints 0x01 (out) and 0x81 (in)
> Inquiring device details; driver will be detached ...
> Looking for active driver ...
> OK, driver found ("usb-storage")
> OK, driver "usb-storage" detached
>
> Received inquiry data (detailed identification)
> -------------------------
> Vendor String: HUAWEI
>  Model String: Mass Storage
> Revision String: 2.31
> -------------------------
>
> Device description data (identification)
> -------------------------
> Manufacturer: Huawei Technologies
>    Product: HUAWEI Mobile
> Serial No.: not provided
> -------------------------
> Setting up communication with interface 0 ...
> Trying to send the message to endpoint 0x01 ...
> OK, message successfully sent
> -> Run lsusb to note any changes. Bye.

lsusbで見てみると

> Bus 001 Device 006: ID 12d1:1429 Huawei Technologies Co., Ltd.

デバイスIDが1446から1429に変わっている。

カーネルモジュールをロードすると、/dev/ttyUSB0,1,2が作成される。

> # ls -la /dev/ttyUSB*
> ls: cannot access /dev/ttyUSB*: No such file or directory
>
> # modprobe usbserial vendor=0x12d1 product=0x1429
>
> # ls -la /dev/ttyUSB*
> crw-rw---- 1 root dialout 188, 0 Nov  2 01:02 /dev/ttyUSB0
> crw-rw---- 1 root dialout 188, 1 Nov  2 01:02 /dev/ttyUSB1
> crw-rw---- 1 root dialout 188, 2 Nov  2 01:02 /dev/ttyUSB2

そして、pppの設定ファイルを作成

/etc/ppp/peers/provider

> user "em@em"
> connect "/usr/sbin/chat -v -f /etc/chatscripts/pap -T *99***1#"
> /dev/ttyUSB0
> 115200
> defaultroute
> persist
> noauth
> usepeerdns

接続してみる

> # pon
> # ps -ef |grep ppp
> root      2404     1  0 01:08 ttyUSB0  00:00:00 /usr/sbin/pppd call provider
> root      2410  2088  0 01:08 pts/5    00:00:00 grep ppp
> # ip add show dev ppp0
> 6: ppp0:
>
>  mtu 1500 qdisc pfifo_fast state UNKNOWN qlen 3
>     link/ppp
>     inet 114.48.27.146 peer 10.64.64.64/32 scope global ppp0

接続できました。

>
