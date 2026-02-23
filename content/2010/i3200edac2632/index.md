+++
title = "i3200でedacを使うには、カーネルを2.6.32にしなければならない。"
date = 2010-01-16
path = "2010/01/i3200edac2632.html"
+++

メモリが壊れているかな？

BIOSより、DMIログを覗いてみると。。。

> Phoenix cME FirstBIOS Pro Setup Utility
>              Advanced
> +---------+----------------------------------------------------------+---------+
> |         |                      DMI Event Log                       | Help    |
> |---------|----------------------------------------------------------|---------|
> |         |                                                          |         |
> |   Event | 01/16/2010  14:44:12  Pre-Boot Error:                  ^ |ts of    |
> |   Event |     Keyboard Not Functional                            . |og.      |
> |         |                                                        . |         |
> |   View D| 01/16/2010  14:44:46  Single-Bit ECC Errors in DIMM#   . |         |
> |   Event | 01/16/2010  14:45:45  Single-Bit ECC Errors in DIMM#   . |         |
> |         | 01/16/2010  14:45:45  Pre-Boot Error:                  : |         |
> |   Mark D|     Keyboard Not Functional                            : |         |
> |   Clear |                                                        : |         |
> |         | 01/16/2010  14:46:28  Single-Bit ECC Errors in DIMM#   : |         |
> |         | 01/16/2010  14:47:00  Single-Bit ECC Errors in DIMM#   : |         |
> |         | 01/16/2010  14:47:00  Pre-Boot Error:                  : |         |
> |         |     Keyboard Not Functional                            . |         |
> |         |                                                          |         |
> |         |                       [Continue]                         |         |
> |         +----------------------------------------------------------+         |
> |                                                    |                         |
> +------------------------------------------------------------------------------

せっかくなので、linuxのedacで検出してみる。

i3200でedacを使うには、カーネルを2.6.32にしなければならない。
ずっと前からコードはあったので、とっくにマージされていたと思っていました。

モジュールはこれ

> lenny64:~# lsmod |grep edac
> i3200_edac              3599  0

エラー出力

> lenny64:~# dmesg |tail
> EDAC DEBUG: i3200_check: MC0: i3200_check()
> EDAC MC0: CE page 0x0, offset 0x0, grain 1073741824, syndrome 0x54, row 1, channel 0, label "": i3200 CE
> EDAC DEBUG: i3200_check: MC0: i3200_check()
> EDAC MC0: CE page 0x0, offset 0x0, grain 1073741824, syndrome 0x54, row 1, channel 0, label "": i3200 CE
> EDAC DEBUG: i3200_check: MC0: i3200_check()
> EDAC MC0: CE page 0x0, offset 0x0, grain 1073741824, syndrome 0x54, row 1, channel 0, label "": i3200 CE
> EDAC DEBUG: i3200_check: MC0: i3200_check()
> EDAC MC0: CE page 0x0, offset 0x0, grain 1073741824, syndrome 0x54, row 1, channel 0, label "": i3200 CE
> EDAC DEBUG: i3200_check: MC0: i3200_check()
> EDAC MC0: CE page 0x0, offset 0x0, grain 1073741824, syndrome 0x54, row 1, channel 0, label "": i3200 CE
