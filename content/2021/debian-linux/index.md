+++
title = "Debian Linuxのノートパソコンでハイバネート"
date = 2021-01-17
path = "2021/01/debian-linux.html"
+++

Linuxカーネルには、スワップ領域にメモリの内容を書き出してハイバネートする機能がある。 必要な要件等は以下の通り。

- 十分な大きさのスワップデバイスまたはファイルを用意する。(メモリ容量と同じくらいあれば良いが、そこまでなくても良いという情報もある。)
- カーネル起動オプションresume=デバイス名を加えカーネルを起動。
- uswsuspを利用することもできるが、利用しなくても良い。その場合initrdをいじる必要は無い。

参考文献

- [https://wiki.archlinux.jp/index.php/サスペンドとハイバネート](https://wiki.archlinux.jp/index.php/%E3%82%B5%E3%82%B9%E3%83%9A%E3%83%B3%E3%83%89%E3%81%A8%E3%83%8F%E3%82%A4%E3%83%90%E3%83%8D%E3%83%BC%E3%83%88)
- [https://www.kernel.org/doc/Documentation/power/states.txt](https://www.kernel.org/doc/Documentation/power/states.txt)
- [https://www.kernel.org/doc/html/latest/power/basic-pm-debugging.html](https://www.kernel.org/doc/html/latest/power/basic-pm-debugging.html)

以下、実際の設定

/etc/fstab (該当部分のみ)

```
#/dev/nvme0n1p7	swap    swap    defaults  0 0
/swapfile	swap	swap	defaults  0 0
```

デバイスをスワップとして使う場合と、ファイル(/swapfile)をスワップとして使う場合とで必要なカーネルパラメータが異なる。 後者の場合はresume_offsetも必要。オフセット値は以下のように確認可能。この場合86093824がオフセット値。

sudo filefrag -v /swapfile

```
Filesystem type is: ef53
File size of /swapfile is 17179869184 (4194304 blocks of 4096 bytes)
 ext:     logical_offset:        physical_offset: length:   expected: flags:
   0:        0..    2047:   86093824..  86095871:   2048:
   1:     2048..    4095:   86167552..  86169599:   2048:   86095872:
   2:     4096..    8191:   86155264..  86159359:   4096:   86169600:
以下略
```

/boot/grub/grub.cfg (該当部分のみ)

```
menuentry "Debian Linux resume-test1" {
linux /boot/vmlinuz root=/dev/nvme0n1p6 vga=0x305 panic=10 net.ifnames=0 biosdevname=0 resume=/dev/nvme0n1p7
}
menuentry "Debian Linux resume-test2" {
linux /boot/vmlinuz root=/dev/nvme0n1p6 vga=0x305 panic=10 net.ifnames=0 biosdevname=0 resume=/dev/nvme0n1p6 resume_offset=86093824
}
```

ノートパソコンのディスプレイを閉じたときにhibernateする設定

/etc/acpi/events/lid_down

```
event=button[ /]lid
action=/etc/acpi/lid_down.sh
```

/etc/acpi/lid_down.sh

```
#!/bin/sh

grep -q closed /proc/acpi/button/lid/*/state
if [ $? -eq 0 ]
then
	echo platform > /sys/power/disk ; echo disk > /sys/power/state
fi

exit 0
```

以上で、ハイバネートできることを確認した。
