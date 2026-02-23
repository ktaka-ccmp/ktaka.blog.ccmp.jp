+++
title = "GNU tarでシンボリックリンクのタイムスタンプが保存されない - 1.24以降ならOK"
date = 2011-04-07
path = "2011/04/gnu-tar124ok.html"
+++

>

>

GNU tar 1.24以降であれば、タイムスタンプが保存されるようである。

[http://git.savannah.gnu.org/cgit/tar.git/plain/NEWS?id=release_1_24](http://git.savannah.gnu.org/cgit/tar.git/plain/NEWS?id=release_1_24)

> ** Symbolic link attributes When extracting symbolic links, tar now restores attributes such as last-modified time and link permissions, if the operating system supports this.  For example, recent versions of the Linux kernel support setting times on symlinks, and some BSD kernels also support symlink permissions.

```

```

Debian squeeze のtarは1.23である。

> ktaka@hana:~$ tar --version
>
> tar (GNU tar) 1.23
>
> Copyright (C) 2010 Free Software Foundation, Inc.
>
> License GPLv3+: GNU GPL version 3 or later .
>
> This is free software: you are free to change and redistribute it.
>
> There is NO WARRANTY, to the extent permitted by law.
>
>
>
> Written by John Gilmore and Jay Fenlason.

タイムスタンプがApr 1 00:00のシンボリックリンクを作成。

> ktaka@hana:~$ mkdir p

> ktaka@hana:~$ for i in  a b c d e f g ; do ln -s /tmp/$i p/$i; touch -ht 04010000 p/$i ; done
>
> ktaka@hana:~$ ls -la p
>
> total 8
>
> drwxr-xr-x  2 ktaka ktaka 4096 Apr  8 03:03 .
>
> drwx------ 79 ktaka ktaka 4096 Apr  8 03:03 ..
>
> lrwxrwxrwx  1 ktaka ktaka    6 Apr  1 00:00 a -> /tmp/a
>
> lrwxrwxrwx  1 ktaka ktaka    6 Apr  1 00:00 b -> /tmp/b
>
> lrwxrwxrwx  1 ktaka ktaka    6 Apr  1 00:00 c -> /tmp/c
>
> lrwxrwxrwx  1 ktaka ktaka    6 Apr  1 00:00 d -> /tmp/d
>
> lrwxrwxrwx  1 ktaka ktaka    6 Apr  1 00:00 e -> /tmp/e
>
> lrwxrwxrwx  1 ktaka ktaka    6 Apr  1 00:00 f -> /tmp/f
>
> lrwxrwxrwx  1 ktaka ktaka    6 Apr  1 00:00 g -> /tmp/g

tarアーカイブを作成

> ktaka@hana:~$ (cd p; tar cf - .)|gzip > p.tgz

中身を確認すると、確かに正しいタイムスタンプでアーカイブが作成されている。

> ktaka@hana:~$ tar ztvf p.tgz
>
> drwxr-xr-x ktaka/ktaka       0 2011-04-08 03:03 ./
>
> lrwxrwxrwx ktaka/ktaka       0 2011-04-01 00:00 ./f -> /tmp/f
>
> lrwxrwxrwx ktaka/ktaka       0 2011-04-01 00:00 ./c -> /tmp/c
>
> lrwxrwxrwx ktaka/ktaka       0 2011-04-01 00:00 ./g -> /tmp/g
>
> lrwxrwxrwx ktaka/ktaka       0 2011-04-01 00:00 ./a -> /tmp/a
>
> lrwxrwxrwx ktaka/ktaka       0 2011-04-01 00:00 ./e -> /tmp/e
>
> lrwxrwxrwx ktaka/ktaka       0 2011-04-01 00:00 ./d -> /tmp/d
>
> lrwxrwxrwx ktaka/ktaka       0 2011-04-01 00:00 ./b -> /tmp/b

アーカイブをqディレクトリに展開

> ktaka@hana:~$ mkdir q; (cd q; tar zxf ../p.tgz) ; date
>
> Fri Apr  8 03:16:26 JST 2011

タイムスタンプがアーカイブを展開した時刻になってしまう。

> ktaka@hana:~$ ls -la q/
>
> total 8
>
> drwxr-xr-x  2 ktaka ktaka 4096 Apr  8 03:03 .
>
> drwx------ 79 ktaka ktaka 4096 Apr  8 03:16 ..
>
> lrwxrwxrwx  1 ktaka ktaka    6 Apr  8 03:16 a -> /tmp/a
>
> lrwxrwxrwx  1 ktaka ktaka    6 Apr  8 03:16 b -> /tmp/b
>
> lrwxrwxrwx  1 ktaka ktaka    6 Apr  8 03:16 c -> /tmp/c
>
> lrwxrwxrwx  1 ktaka ktaka    6 Apr  8 03:16 d -> /tmp/d
>
> lrwxrwxrwx  1 ktaka ktaka    6 Apr  8 03:16 e -> /tmp/e
>
> lrwxrwxrwx  1 ktaka ktaka    6 Apr  8 03:16 f -> /tmp/f
>
> lrwxrwxrwx  1 ktaka ktaka    6 Apr  8 03:16 g -> /tmp/g

GNU tar 1.24で試してみる。

> ktaka@hana:~$ ./tar-1.24/_inst/bin/tar --version
>
> tar (GNU tar) 1.24
>
> Copyright (C) 2010 Free Software Foundation, Inc.
>
> License GPLv3+: GNU GPL version 3 or later .
>
> This is free software: you are free to change and redistribute it.
>
> There is NO WARRANTY, to the extent permitted by law.
>
>
>
> Written by John Gilmore and Jay Fenlason.

 ディレクトリrに展開してみる。

> ktaka@hana:~$ mkdir r; (cd r; ../tar-1.24/_inst/bin/tar zxf ../p.tgz) ; date
>
>
>
> Fri Apr  8 03:35:37 JST 2011

> ktaka@hana:~$ ls -la r
>
> total 8
>
> drwxr-xr-x  2 ktaka ktaka 4096 Apr  8 03:03 .
>
> drwx------ 81 ktaka ktaka 4096 Apr  8 03:35 ..
>
> lrwxrwxrwx  1 ktaka ktaka    6 Apr  1 00:00 a -> /tmp/a
>
> lrwxrwxrwx  1 ktaka ktaka    6 Apr  1 00:00 b -> /tmp/b
>
> lrwxrwxrwx  1 ktaka ktaka    6 Apr  1 00:00 c -> /tmp/c
>
> lrwxrwxrwx  1 ktaka ktaka    6 Apr  1 00:00 d -> /tmp/d
>
> lrwxrwxrwx  1 ktaka ktaka    6 Apr  1 00:00 e -> /tmp/e
>
> lrwxrwxrwx  1 ktaka ktaka    6 Apr  1 00:00 f -> /tmp/f
>
> lrwxrwxrwx  1 ktaka ktaka    6 Apr  1 00:00 g -> /tmp/g

正しいタイムスタンプで シンボリックリンクを展開することができた。

参考リンク

- [http://www.mail-archive.com/bug-tar@gnu.org/msg02281.html](http://www.mail-archive.com/bug-tar@gnu.org/msg02281.html)
