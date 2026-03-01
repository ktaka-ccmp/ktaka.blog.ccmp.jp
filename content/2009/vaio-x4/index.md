+++
title = "vaio xの駆動時間は実質4時間位か"
date = 2009-11-03
description = "VAIO XのDebian Linux環境でのバッテリ駆動時間が実質約4時間だった検証結果。"
path = "2009/11/vaio-x4.html"
+++

メーカーのページにL型バッテリ駆動時間は約10時間とあるので期待して購入したvaio xですが、私の環境では、4時間位がいいところのようです。

環境　Debian Linux(カーネル2.6.31.5)

電池の容量は、33590 mWh

> vaiox:/home/ktaka# cat /proc/acpi/battery/BAT0/info
> present:                 yes
> design capacity:         33590 mWh
> last full capacity:      33590 mWh
> battery technology:      rechargeable
> design voltage:          7400 mV
> design capacity warning: 3350 mWh
> design capacity low:     120 mWh
> capacity granularity 1:  0 mWh
> capacity granularity 2:  1 mWh
> model number:
> serial number:
> battery type:            Lion
> OEM info:                Sony Corporation

800MHz動作時の、消費電力は、7669mW

> # cat /proc/acpi/battery/BAT0/state
> present:                 yes
> capacity state:          ok
> charging state:          discharging
> present rate:            7669 mW
> remaining capacity:      4710 mWh
> present voltage:         6928 mV

よって33590/7669 = 4.38 時間が駆動時間。

CPUのクロックは、cpufreqdのおかげで、バッテリ駆動時は800MHzになっている。
ACアダプタ使用時 1.87GHz

> # cat  /sys/devices/system/cpu/cpu{0,1}/cpufreq/cpuinfo_cur_freq
> 1866000
> 1866000

バッテリ駆動時 800MHz

> # cat  /sys/devices/system/cpu/cpu{0,1}/cpufreq/cpuinfo_cur_freq
> 800000
> 800000

cpufreqd.confの内容

> [General]
> pidfile=/var/run/cpufreqd.pid
> poll_interval=2
> verbosity=4
> [/General]
>
> [Profile]
> name=Performance High
> minfreq=100%
> maxfreq=100%
> policy=performance
> #exec_post=echo 8 > /proc/acpi/sony/brightness
> [/Profile]
>
> [Profile]
> name=Powersave Low
> minfreq=40%
> maxfreq=40%
> policy=powersave
> [/Profile]
>
> [Rule]
> name=AC Rule
> ac=on                    # (on/off)
> profile=Performance High
> [/Rule]
>
> [Rule]
> name=AC Off - Low Battery
> ac=off                   # (on/off)
> battery_interval=0-100
> #exec_post=echo 3 > /proc/acpi/sony/brightness
> profile=Powersave Low
> [/Rule]

Poulsbo (GMA 500)のグラフィックドライバ(psb)がバニラカーネルに取り込まれていない。
Ｕｂｕｎｔｕでは、カーネル2.6.28用のドライバが存在するようである。

今はLCDの輝度調節が効かないが、psbが使えれば、輝度を落とすことができ、もう少し長く使えるようになるかもしれない。
