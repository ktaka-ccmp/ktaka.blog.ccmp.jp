+++
title = "SupermicroのIPMI"
date = 2008-04-28
description = "Supermicroからベーシックなシンプル仕様のIPMIカードが発売された話。"
path = "2008/04/supermicroipmi.html"
+++

最近のIPMIカードは、KVM(Keyboard Video Mouse) over LANとかがついていて、HTTPとか、SSHとか喋るので非常に使いにくかったのですが、古き良き時代のベーシックなIPMIカードが、Supermicroより発売されました。Supermicroのエンジニアにしつこく催促したのが功を奏したのかも知れません。

http://www.supermicro.com/manuals/other/AOC-SIMSOLC-HTC.pdf

UDPの623のみを、SMBusに流すというわかりやすい仕様なので、ホストと同じIPを使うのも問題無さそうな気がします。

ボンディング使用時には、別IPにした方が無難ですが。。。
