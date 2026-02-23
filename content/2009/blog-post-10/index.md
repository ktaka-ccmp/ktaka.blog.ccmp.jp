+++
title = "[備忘録] ノートパソコンの起動時間の短縮をしたい"
date = 2009-10-26
path = "2009/10/blog-post.html"
+++

Let's note T7に Debianを入れたものを外出先で使っているのですが、Grubでカーネルを選択してから、Xが立ち上がるまでに1分近くかかっていました。その後emobileに接続したりと、メールやWebが見れるまでにはさらに時間がかかっていました。これだと、ちょこっと情報を確認したい時にはちょっと面倒です。
そこでiPhoneを導入し、それはそれで快適に使えているわけですが、ノートパソコンの方ももう少し起動時間短縮できるよう頑張ってみたいと思います。

方針は

- 余分なサービスの停止
- X windowが無くても何とかなるように

- フレームバッファを使えるようにする

- テキストコンソールでメールの読み書きができるように。候補emacs+wanderlust
- テキストコンソールでWebの閲覧検索ができるように。候補はemacs+w3m
- 切換えはscreenで

- カーネルをスリムに
- SSD化、IntelのX-25M 80GB辺りを物色中

先ず、色々といらないサービスを起動しないようにします。
update-rc -f dhcpd3-server remove
update-rc -f tftpd-hpa remove
update-rc -f hogehoge remove

/etc/init.d/rcで
CONCURRENCY=none → CONCURRENCY=shell

フレームバッファを使えるようにする
lspci
00:02.0 VGA compatible controller: Intel Corporation Mobile GM965/GL960 Integrated Graphics Controller (rev 03)
00:02.1 Display controller: Intel Corporation Mobile GM965/GL960 Integrated Graphics Controller (rev 03)
とあるので、intelfbを使うことにします。

おそらく関係するのはこの辺り
ktaka@lets:~/Kernel/linux-2.6.31.5$ egrep FB .config|egrep -v "^#"
CONFIG_FB=y
CONFIG_FB_DDC=y
CONFIG_FB_BOOT_VESA_SUPPORT=y
CONFIG_FB_CFB_FILLRECT=y
CONFIG_FB_CFB_COPYAREA=y
CONFIG_FB_CFB_IMAGEBLIT=y
CONFIG_FB_FOREIGN_ENDIAN=y
CONFIG_FB_BOTH_ENDIAN=y
CONFIG_FB_MODE_HELPERS=y
CONFIG_FB_TILEBLITTING=y
CONFIG_FB_INTEL=y
CONFIG_FB_INTEL_DEBUG=y
CONFIG_FB_INTEL_I2C=y

上記設定確認後、カーネルを再コンパイルしました。

そしてカーネルのオプションは、
video=intelfb:accel=0 vga=0x318
とすれば上手く行くことがわかりました。intelfbのデフォルトだとaccel=1になっていて、上手くいかないようです。

コンソールで日本語を表示する為に、jfbtermを使ってみる。

環境変LC_ALL=ja_JPでないと、日本語が表示できなかったりする。
コンソールでjfbtermを使わずにmanページを見ることもあるので、普段はLC_ALL=Cで使いたい。
.bashrcで、TERM=jfbtermの時のみLC_ALL=ja_JPにするよう設定します。

if [ `tty|sed -e 's/.*tty.*/tty/g'` == "tty" ] ; then
   export LC_ALL=C
fi

if [ $TERM == "jfbterm" ] ; then
   export LC_ALL=ja_JP
   export LANG=ja_JP.UTF-8
fi

以上の設定の後、
コンソールログイン→screen起動→emacs/M-x w3mで日本語ページが表示できるようになりました。

このページもその環境から編集していますが、bloggerにログインする際、クッキーが使えないと叱られた。
.emacsに
(setq w3m-use-cookies t)
と書くことで解決しました。

残りは、後日。
