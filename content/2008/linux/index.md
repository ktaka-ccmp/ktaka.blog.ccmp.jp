+++
title = "本家Linuxカーネルに採用されました！"
date = 2008-11-07
path = "2008/11/linux.html"
+++

うちのmitake君が書いてくれたEDACドライバが、メインラインカーネルに採用になりました。
http://www.kernel.org/pub/linux/kernel/v2.6/testing/ChangeLog-2.6.28-rc3

> commit df8bc08c192f00f155185bfd6f052d46a728814a
> Author: Hitoshi Mitake
> Date:   Wed Oct 29 14:00:50 2008 -0700
>
>  edac x38: new MC driver module
>
>  I wrote a new module for Intel X38 chipset.  This chipset is very similar
>  to Intel 3200 chipset, but there are some different points, so I copyed
>  i3200_edac.c and modified.
>
>  This is Intel's web page describing this chipset.
>  http://www.intel.com/Products/Desktop/Chipsets/X38/X38-overview.htm
>
>  I've tested this new module with broken memory, and it seems to be working
>  well.
>
>  Signed-off-by: Hitoshi Mitake
>  Signed-off-by: Doug Thompson
>  Signed-off-by: Andrew Morton
>  Signed-off-by: Linus Torvalds
>

先日本ブログで紹介したIntelの2in1サーバ(SR1520ML)には、X38チップセットが搭載されています。このチップセットはECCメモリに対応しているので、1ビットエラーは訂正、2ビットエラー以上は検出可能です。

Linuxカーネルでは、この様なECCイベントをEDACというモジュールで検出することが可能なのですが、今までは、X38用のEDACドライバが存在していなかったので、検出できていませんでした。

それをmitake君が書いてくれたと言う訳です。

いずれ世界中のLinuxマシンに彼の書いたプログラムがのるわけで、これって、とてもすごいことだと思います！

mitake君、おめでとう！
