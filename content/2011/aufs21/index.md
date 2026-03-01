+++
title = "aufs2.1を試してみる。"
date = 2011-04-09
description = "スタッカブルファイルシステムaufs2.1のインストール手順と、ファイル・ディレクトリの作成・削除時の動作検証。"
path = "2011/04/aufs21.html"
+++

Aufs(AnotherUnionfs)は、複数のディレクトリを単一のディレクトリに見せるスタッカブルなファイルシステムです。Aufsを用いると、リードオンリーなディレクトリの上に、読み書き専用のディレクトリを重ねてマウントすることができます。

今回、これについて試してみました。

**インストール手順**

[http://aufs.sourceforge.net/](http://aufs.sourceforge.net/)にあるドキュメントを参考にインストールします。

レポジトリの同期とチェックアウト

今回はバニラカーネルにパッチを当てて、カーネルモジュールとしてコンパイルするので、aufs2-standalone.gitのみ同期します。

> root@hana:~/tmp# git clone http://git.c3sl.ufpr.br/pub/scm/aufs/aufs2-standalone.git aufs2-standalone.git
>
> Cloning into aufs2-standalone.git... 

使用するバニラカーネルのバージョンは2.6.38.2なので、aufs2.1-38 をチェックアウトします。

> root@hana:~/tmp# cd aufs2-standalone.git/ 

> root@hana:~/tmp/aufs2-standalone.git# git checkout origin/aufs2.1-38
>
> Note: checking out 'origin/aufs2.1-38'.
>
> You are in 'detached HEAD' state. You can look around, make experimental
>
> changes and commit them, and you can discard any commits you make in this
>
> state without impacting any branches by performing another checkout.
>
> If you want to create a new branch to retain commits you create, you may
>
> do so (now or later) by using -b with the checkout command again. Example:
>
>   git checkout -b new_branch_name
>
> HEAD is now at 4c5ce8c... aufs2.1 standalone version for linux-2.6.38 

> root@hana:~/tmp/aufs2-standalone.git# ls -la
>
> total 356
>
> drwxr-xr-x 7 root root   4096 Apr  8 14:08 .
>
> drwxr-xr-x 3 root root   4096 Apr  8 14:06 ..
>
> drwxr-xr-x 8 root root   4096 Apr  8 14:08 .git
>
> -rw-r--r-- 1 root root  17990 Apr  8 14:07 COPYING
>
> -rw-r--r-- 1 root root 268285 Apr  8 14:08 ChangeLog
>
> drwxr-xr-x 3 root root   4096 Apr  8 14:08 Documentation
>
> -rw-r--r-- 1 root root   1365 Apr  8 14:07 Makefile
>
> -rw-r--r-- 1 root root  14421 Apr  8 14:08 README
>
> -rw-r--r-- 1 root root   2971 Apr  8 14:08 aufs2-base.patch
>
> -rw-r--r-- 1 root root    978 Apr  8 14:08 aufs2-kbuild.patch
>
> -rw-r--r-- 1 root root   8732 Apr  8 14:08 aufs2-standalone.patch
>
> -rw-r--r-- 1 root root   2793 Apr  8 14:08 config.mk
>
> drwxr-xr-x 2 root root   4096 Apr  8 14:08 design
>
> drwxr-xr-x 3 root root   4096 Apr  8 14:08 fs
>
> drwxr-xr-x 3 root root   4096 Apr  8 14:07 include

linux-2.6.38用のパッチが作成されました。

カーネルソースディレクトリに移動し、パッチを当てます。

> root@hana:~/Kernel/linux-2.6.38.2# patch -p1
> patching file fs/splice.c
>
> patching file include/linux/namei.h
>
> patching file include/linux/splice.h
>
> root@hana:~/Kernel/linux-2.6.38.2# patch -p1
> patching file fs/Kconfig
>
> patching file fs/Makefile
>
> patching file include/linux/Kbuild
>
> root@hana:~/Kernel/linux-2.6.38.2# patch -p1
> patching file fs/file_table.c
>
> patching file fs/inode.c
>
> patching file fs/namei.c
>
> patching file fs/namespace.c
>
> patching file fs/notify/group.c
>
> patching file fs/notify/mark.c
>
> patching file fs/open.c
>
> patching file fs/splice.c
>
> patching file security/commoncap.c
>
> patching file security/device_cgroup.c
>
> patching file security/security.c

必要なファイルもコピーします。

> root@hana:~/Kernel/linux-2.6.38.2# cp -R ~/tmp/aufs2-standalone.git/Documentation ./
>
> root@hana:~/Kernel/linux-2.6.38.2# cp -R ~/tmp/aufs2-standalone.git/fs ./
>
> root@hana:~/Kernel/linux-2.6.38.2# cp -R ~/tmp/aufs2-standalone.git/include/linux/aufs_type.h ./include/linux/ 

make menuconfig で必要な設定をします。aufsに関する設定パラメータは以下の通りです。

> root@hana:~/Kernel/linux-2.6.38.2# egrep AUFS .config
>
> CONFIG_AUFS_FS=m
>
> CONFIG_AUFS_BRANCH_MAX_127=y
>
> # CONFIG_AUFS_BRANCH_MAX_511 is not set
>
> # CONFIG_AUFS_BRANCH_MAX_1023 is not set
>
> # CONFIG_AUFS_BRANCH_MAX_32767 is not set
>
> CONFIG_AUFS_SBILIST=y
>
> CONFIG_AUFS_HNOTIFY=y
>
> CONFIG_AUFS_HFSNOTIFY=y
>
> CONFIG_AUFS_RDU=y
>
> CONFIG_AUFS_SP_IATTR=y
>
> CONFIG_AUFS_SHWH=y
>
> CONFIG_AUFS_BR_RAMFS=y
>
> CONFIG_AUFS_BR_FUSE=y
>
> CONFIG_AUFS_POLL=y
>
> CONFIG_AUFS_BDEV_LOOP=y
>
> CONFIG_AUFS_DEBUG=y
>
> CONFIG_AUFS_MAGIC_SYSRQ=y

カーネルをコンパイル、インストールして再起動します。

> root@hana:~# modprobe aufs

> root@hana:~# lsmod |grep auf
>
> aufs                  464609  0 

> root@hana:~# modinfo aufs
>
> filename:       /lib/modules/2.6.38.2-64aufs01/kernel/fs/aufs/aufs.ko
>
> version:        2.1-standalone.tree-38-20110404
>
> description:    aufs -- Advanced multi layered unification filesystem
>
> author:         Junjiro R. Okajima
>
> license:        GPL
>
> srcversion:     D52E89D4B96A545C9E3E064
>
> depends:      
>
> vermagic:       2.6.38.2-64aufs01 SMP mod_unload modversions
>
> parm:           sysrq:MagicSysRq key for aufs (charp)
>
> parm:           debug:debug print (int)
>
> parm:           brs:use /fs/aufs/si_*/brN (int)

インストールは以上です。Debian squeezeだとmountコマンドは最初からaufsをサポートしているようです（？要確認）

**試してみます。**

テストディレクトリを作成する。

> mkdir /tmp/{base,cover,mnt}

> /tmp/base ベースディレクトリ、リードオンリーマウントする
>
> /tmp/cover  上から重ねるディレクトリ。書き込み可能
>
> /tmp/mnt マウントポイント

ベースディレクトリにテストディレクトリdir1、テストファイルfile1、file11を作成する。

> mkdir /tmp/base/dir1
>
> echo 1 > /tmp/base/file1
>
> echo 11 > /tmp/base/dir1/file11

aufsでマウントする。

> mount -t aufs -o br=/tmp/cover=rw:/tmp/base=ro none /tmp/mnt/
>
> mount|grep aufs
>
> none on /tmp/mnt type aufs (rw,br=/tmp/cover=rw:/tmp/base=ro)

ディレクトリ構造は、それぞれ次のようになる。

> tree -a /tmp/{base,cover,mnt}
>
> /tmp/base
>
> |-- dir1
>
> |   `-- file11
>
> `-- file1
>
> /tmp/cover
>
> |-- .wh..wh.aufs
>
> |-- .wh..wh.orph
>
> `-- .wh..wh.plnk
>
> /tmp/mnt
>
> |-- dir1
>
> |   `-- file11
>
> `-- file1
>
> 4 directories, 5 files

マウントしたディレクトリに新たにファイルを作成する。

> echo 2 > /tmp/mnt/file2

リードオンリーの/tmp/baseは変わらずに、書き込み可能な/tmp/coverにfile2が作成される。

> tree -a /tmp/{base,cover,mnt}
>
> /tmp/base
>
> |-- dir1
>
> |   `-- file11
>
> `-- file1
>
> /tmp/cover
>
> |-- .wh..wh.aufs
>
> |-- .wh..wh.orph
>
> |-- .wh..wh.plnk
>
> `-- file2
>
> /tmp/mnt
>
> |-- dir1
>
> |   `-- file11
>
> |-- file1
>
> `-- file2
>
> 4 directories, 7 files

ファイルの削除

/tmp/mnt/file1を削除すると、/tmp/cover/.wh.file1が作成され、/tmp/mnt/file1が見えなくなる。

/tmp/mnt/file2を削除すると、単純に/tmp/coverからfile2が消える。

> rm /tmp/mnt/file{1,2}
>
> tree -a /tmp/{base,cover,mnt}
>
> /tmp/base
>
> |-- dir1
>
> |   `-- file11
>
> `-- file1
>
> /tmp/cover
>
> |-- .wh..wh.aufs
>
> |-- .wh..wh.orph
>
> |-- .wh..wh.plnk
>
> `-- .wh.file1
>
> /tmp/mnt
>
> `-- dir1
>
>     `-- file11 

> 4 directories, 5 files

元とは違う内容で/tmp/mnt/file1を作成すると、/tm/cover/にもfile1が作成される。

> echo x > /tmp/mnt/file1
>
> tree -a /tmp/{base,cover,mnt}
>
> /tmp/base
>
> |-- dir1
>
> |   `-- file11
>
> `-- file1
>
> /tmp/cover
>
> |-- .wh..wh.aufs
>
> |-- .wh..wh.orph
>
> |-- .wh..wh.plnk
>
> `-- file1
>
> /tmp/mnt
>
> |-- dir1
>
> |   `-- file11
>
> `-- file1
>
> 4 directories, 6 files

それぞれのファイルの内容を確認すると、/tmp/base/file1のみが元の内容のままで、/tmp/cover/file1、/tmp/mnt/file1は新しい内容になっていることがわかる。

> head /tmp/{base,cover,mnt}/file1
>
> ==> /tmp/base/file1  /tmp/cover/file1  /tmp/mnt/file1
> x

ディレクトリの削除

/tmp/mnt/dir1を削除すると/tmp/mntからはdir1が消え、/tmp/coverに.wh.dir1が作成される。

> rm -r /tmp/mnt/dir1
>
> tree -a /tmp/{base,cover,mnt}
>
> /tmp/base
>
> |-- dir1
>
> |   `-- file11
>
> `-- file1
>
> /tmp/cover
>
> |-- .wh..wh.aufs
>
> |-- .wh..wh.orph
>
> |-- .wh..wh.plnk
>
> `-- .wh.dir1
>
> /tmp/mnt
>
> `-- file1
>
> 3 directories, 5 files

もう一度/tmp/mnt/dir1を作成してみると、/tmp/coverにあった.wh.dir1が無くなり、新たに/tmp/cover/dir1、/tmp/cover/dir1/.wh..wh..opqが作成される。

> mkdir /tmp/mnt/dir1
>
> tree -a /tmp/{base,cover,mnt}
>
> /tmp/base
>
> |-- dir1
>
> |   `-- file11
>
> `-- file1
>
> /tmp/cover
>
> |-- .wh..wh.aufs
>
> |-- .wh..wh.orph
>
> |-- .wh..wh.plnk
>
> `-- dir1
>
>     `-- .wh..wh..opq
>
> /tmp/mnt
>
> |-- dir1
>
> `-- file1
>
> 5 directories, 5 files

/tmp/cover/dir1/.wh..wh..opq　の中身は空である。

> file /tmp/cover/dir1/.wh..wh..opq
>
> /tmp/cover/dir1/.wh..wh..opq: empty

/tmp/mnt/dir1/file11を作成してみると、/tmp/cover/dir1/file11が作成される。

> echo xx > /tmp/mnt/dir1/file11
>
> tree -a /tmp/{base,cover,mnt}
>
> /tmp/base
>
> |-- dir1
>
> |   `-- file11
>
> `-- file1
>
> /tmp/cover
>
> |-- .wh..wh.aufs
>
> |-- .wh..wh.orph
>
> |-- .wh..wh.plnk
>
> `-- dir1
>
>     |-- .wh..wh..opq
>
>     `-- file11
>
> /tmp/mnt
>
> |-- dir1
>
> |   `-- file11
>
> `-- file1
>
> 5 directories, 7 files

それぞれのディレクトリにあるfile11の内容は以下の通りで、/tmp/base/dir1/file11が元の内容、/tmp/cover/dir1/file11、/tmp/mnt/dir1/file11が新しい内容である。

> head /tmp/{base,cover,mnt}/dir1/file11
>
> ==> /tmp/base/dir1/file11  /tmp/cover/dir1/file11  /tmp/mnt/dir1/file11
> xx

**まとめ**

スタッカブルなファイルシステムaufsについて試してみた。リードオンリーなディレクトリの上に、読み書き専用のディレクトリを重ねてマウントできることが確認できた。

また、簡単な例のみであるが、ファイルの作成、削除、ディレクトリの作成、削除を行った際に、どのような動作をするのか何となくわかった。
