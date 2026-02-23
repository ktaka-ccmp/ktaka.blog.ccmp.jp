+++
title = "VAIO X linuxでの輝度調整"
date = 2009-11-09
path = "2009/11/vaio-x-linux.html"
+++

[ここ](http://garin.jp/doc/%E6%A9%9F%E7%A8%AE%E5%88%A5/vaio_type_p/bright)を参考に。

> setpci コマンドで直接設定を行います。 VAIO type P では 00:02.0 F4.B が輝度用のデバイスです。
> 輝度の範囲は 00〜FF(暗い〜明い) です。

VAIO Xでも同じだろうということでやってみると、やはりその通り。輝度調節できました。

最小はB=0だけど、そうすると真っ暗になってしまう。B=10前後がいいところか。
setpci -s 00:02.0 F4.B=10

最大はB=FF。
setpci -s 00:02.0 F4.B=FF

B=10の時の消費電力

> # grep rate  /proc/acpi/battery/BAT0/state
> present rate:            6104 mW

B=FFの時の消費電力

> # grep rate  /proc/acpi/battery/BAT0/state
> present rate:            7628 mW

Lバッテリの場合"design capacity: 33590 mWh"なので、B=10にすれば、5時間ちょっとは使えそうです。

追記 cpufreqdの設定で、ACプラグON/OFFで輝度が変わるようにしました。
/etc/cpufreqd.conf

> [Profile]
> name=Performance High
> minfreq=100%
> maxfreq=100%
> policy=performance
> exec_post=/usr/bin/setpci -s 00:02.0 F4.B=ff
> [/Profile]
>
> [Profile]
> name=Powersave Low
> minfreq=40%
> maxfreq=40%
> policy=powersave
> exec_post=/usr/bin/setpci -s 00:02.0 F4.B=10
> [/Profile]
>
> [Rule]
> name=AC Rule
> ac=on
> profile=Performance High
> [/Rule]
>
> [Rule]
> name=AC Off - Low Battery
> ac=off
> battery_interval=0-100
> profile=Powersave Low
> [/Rule]
