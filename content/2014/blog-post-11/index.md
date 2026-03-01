+++
title = "今日の逸品"
date = 2014-11-03
description = "Intel PCIe SSD DC P3700 1.6TBの実機ベンチマーク結果をdd・fio・mysqlslapで計測し、AWS RDSとも比較。"
path = "2014/11/blog-post.html"
+++

こんにちは。三連休の最終日、お天気は快晴で絶好の行楽日和となりましたね！

本当はどこかに出かけるか、外で思いっきりスポーツでもしたいところですが、某代理店さんからお借りしている最新の超高性能デバイスを本日中に返送しないといけないので、休日返上でブログを書きながらレポートしたいと思います(^^;)

まずは、写真をと。。。。じゃじゃーん！今日の逸品はこちらです！

<img src="/2014/11/blog-post.html/image/IMG_20141028_000418_mini.jpg" width="320" height="180">

IntelのPCI express typeのSSD DC P3700です。大きなヒートシンクに囲われていて、かっこいいですね！まあ、どんだけ熱くなるんだってお話もありますが。。。

<img src="/2014/11/blog-post.html/image/IMG_20141028_000931_mini.jpg" width="320" height="180">

裏面も、NANDチップがびっしりです。どんだけ大容量なんだ！

<img src="/2014/11/blog-post.html/image/IMG_20141028_001036.jpg" width="320" height="180">

どうやら1.6TBのようです！！

<img src="/2014/11/blog-post.html/image/IMG_20141028_001253.jpg" width="320" height="180">

こんな風に、サーバのPCIeスロットに装着します。ちょっと、見えづらいかも知れませんが、この1Uサイズのサーバは、PCIeスロットが二段になっていて、上段がP3700、下段がLSI RAIDカードとなっています。

インテル® Solid-State Drive DC P3700 シリーズのカタログスペックは、こんな感じです。

| 容量  | Sequencial Read/Write  [MB/s] | 4KB Random Read / Write [IOPS] | 8KB Random Read / Write [IOPS] |
| --- | --- | --- | --- |
| 400 GB | 2,700 / 1,080 | 450,000 / 75,000 | 275,000 / 32,000 |
| 800 GB | 2,800 / 1,900 | 460,000 / 90,000 | 285,000 / 45,000 |
| 1.6 TB | 2,800 / 1,900 | 450,000 / 150,000 | 290,000 / 75,000 |
| 2.0 TB | 2,800 / 2,000 | 450,000 / 175,000 | 295,000 / 90,000 |

( [http://www.intel.co.jp/content/www/jp/ja/solid-state-drives/intel-ssd-dc-family-for-pcie.html](http://www.intel.co.jp/content/www/jp/ja/solid-state-drives/intel-ssd-dc-family-for-pcie.html) こちらのページより抜粋 )

シーケンシャルのリード/ライトが2.8GB/s、1.9GB/s、4KBのランダムリード/ライトが45万IOPS、15万IOPS　！！

一気に眠気が吹き飛びます！！

ちなみに、7200rpmのSATA HDDの場合は、ざっくりとシーケンシャル100MB、ランダム100IOPS程度ですので、どれだけ高性能かおわかりいただけるでしょう。

ライバルは、もしかしてこれ？

<img src="/2014/11/blog-post.html/image/IMG_2038.JPG" width="320" height="240">

使ってみたいですよね？それでは使ってみましょう。このカードは、PCIe SSDの新しい規格NVMe ([http://en.wikipedia.org/wiki/NVM_Express](http://en.wikipedia.org/wiki/NVM_Express))に対応していますので、Linuxカーネルでnvmeドライバがロードされている必要があります。

バニラカーネルをコンパイルする際には、CONFIG_BLK_DEV_NVME=m　などとなるようにします。

うまく認識されると、/dev/nvmexxxとして、見えるようになります。

> wheezy64:~# fdisk  -l /dev/nvme0n1
>
> Disk /dev/nvme0n1: 1600.3 GB, 1600321314816 bytes
>
> 64 heads, 32 sectors/track, 1526185 cylinders, total 3125627568 sectors
>
> Units = sectors of 1 * 512 = 512 bytes
>
> Sector size (logical/physical): 512 bytes / 512 bytes
>
> I/O size (minimum/optimal): 512 bytes / 512 bytes
>
> Disk identifier: 0xc55b79ff
>
>         Device Boot      Start         End      Blocks   Id  System

fdiskでパーティション作成します。

> wheezy64:~# fdisk /dev/nvme0n1
>
> Command (m for help): n
>
> Partition type:
>
>    p   primary (0 primary, 0 extended, 4 free)
>
>    e   extended
>
> Select (default p): p
>
> Partition number (1-4, default 1): 1
>
> First sector (2048-3125627567, default 2048):
>
> Using default value 2048
>
> Last sector, +sectors or +size{K,M,G} (2048-3125627567, default 3125627567):
>
> Using default value 3125627567
>
> Command (m for help): p
>
> Disk /dev/nvme0n1: 1600.3 GB, 1600321314816 bytes
>
> 64 heads, 32 sectors/track, 1526185 cylinders, total 3125627568 sectors
>
> Units = sectors of 1 * 512 = 512 bytes
>
> Sector size (logical/physical): 512 bytes / 512 bytes
>
> I/O size (minimum/optimal): 512 bytes / 512 bytes
>
> Disk identifier: 0xc55b79ff
>
>         Device Boot      Start         End      Blocks   Id  System
>
> /dev/nvme0n1p1            2048  3125627567  1562812760   83  Linux
>
> Command (m for help): w
>
> The partition table has been altered!
>
> Calling ioctl() to re-read partition table.
>
> Syncing disks.

ファイルシステム作ります。

> wheezy64:~# time mkfs.ext4 /dev/nvme0n1p1
>
> mke2fs 1.42.5 (29-Jul-2012)
>
> Discarding device blocks: done                          
>
> Filesystem label=
>
> OS type: Linux
>
> Block size=4096 (log=2)
>
> Fragment size=4096 (log=2)
>
> Stride=0 blocks, Stripe width=0 blocks
>
> 97681408 inodes, 390703190 blocks
>
> 19535159 blocks (5.00%) reserved for the super user
>
> First data block=0
>
> Maximum filesystem blocks=4294967296
>
> 11924 block groups
>
> 32768 blocks per group, 32768 fragments per group
>
> 8192 inodes per group
>
> Superblock backups stored on blocks:
>
>         32768, 98304, 163840, 229376, 294912, 819200, 884736, 1605632, 2654208,
>
>         4096000, 7962624, 11239424, 20480000, 23887872, 71663616, 78675968,
>
>         102400000, 214990848
>
> Allocating group tables: done                          
>
> Writing inode tables: done                          
>
> Creating journal (32768 blocks): done
>
> Writing superblocks and filesystem accounting information: done     
>
>
>
> real    0m13.304s
>
> user    0m2.230s
>
> sys     0m0.440s

マウントします。

> wheezy64:~# mkdir /mnt/p3700
>
> wheezy64:~# mount /dev/nvme0n1p1 /mnt/p3700/ 

> wheezy64:~# df -h
>
> Filesystem      Size  Used Avail Use% Mounted on
>
> rootfs           48G  510M   47G   2% /
>
> tmpfs            48G  510M   47G   2% /
>
> tmpfs           9.5G  228K  9.5G   1% /run
>
> tmpfs           5.0M     0  5.0M   0% /run/lock
>
> tmpfs            10M     0   10M   0% /dev
>
> tmpfs            19G     0   19G   0% /run/shm
>
> /dev/nvme0n1p1  1.5T   70M  1.4T   1% /mnt/p3700 

とりあえず、100GB程度、読み書きしてみます。まずは、Write。

> wheezy64:~# time dd if=/dev/zero of=/mnt/p3700/hello bs=100M count=1000 oflag=direct
>
> 1000+0 records in
>
> 1000+0 records out
>
> 104857600000 bytes (105 GB) copied, 77.9616 s, **1.3 GB/s**
>
> real    1m17.964s
>
> user    0m0.000s
>
> sys     0m45.700s 

そして、Read。

> wheezy64:~# time dd of=/dev/null if=/mnt/p3700/hello bs=100M count=1000 iflag=direct
>
> 1000+0 records in
>
> 1000+0 records out
>
> 104857600000 bytes (105 GB) copied, 40.6814 s, **2.6 GB/s**
>
> real    0m40.684s
>
> user    0m0.010s
>
> sys     0m22.650s

カタログスペックには若干届かないですけど、爆速です！！

大事なのでもう一度、**爆速です！！**

ランダムIOを測ってみます。まずはrandomwrite。

> wheezy64:~# fio --filename=/mnt/p3700/hello  --direct=1 --rw=randwrite --bs=4k --size=2G --numjobs=64 --runtime=180 --name=file1 --ioengine=aio --iodepth=512 --group_reporting
>
> file1: (g=0): rw=randwrite, bs=4K-4K/4K-4K, ioengine=libaio, iodepth=512
>
> ...
>
> file1: (g=0): rw=randwrite, bs=4K-4K/4K-4K, ioengine=libaio, iodepth=512
>
> 2.0.8
>
> Starting 64 processes
>
> Jobs: 1 (f=1): [____________________________________________________________w___] [98.4% done] [0K/833.5M /s] [0 /213K iops] [eta 00m:03s]s]
>
> file1: (groupid=0, jobs=64): err= 0: pid=20537
>
>   write: io=129218MB, bw=734950KB/s, iops=183737 , runt=180039msec
>
>     slat (usec): min=3 , max=2162.1K, avg=322.56, stdev=12338.02
>
>     clat (usec): min=12 , max=9825.2K, avg=166237.67, stdev=381829.66
>
>      lat (usec): min=20 , max=9825.2K, avg=166560.46, stdev=382293.33
>
>     clat percentiles (msec):
>
>      |  1.00th=[    5],  5.00th=[    6], 10.00th=[    7], 20.00th=[    8],
>
>      | 30.00th=[    9], 40.00th=[   11], 50.00th=[   13], 60.00th=[   22],
>
>      | 70.00th=[   70], 80.00th=[  208], 90.00th=[  519], 95.00th=[  898],
>
>      | 99.00th=[ 1844], 99.50th=[ 2343], 99.90th=[ 3458], 99.95th=[ 3884],
>
>      | 99.99th=[ 5211]
>
>     bw (KB/s)  : min=    0, max=310600, per=1.82%, avg=13395.80, stdev=22803.92
>
>     lat (usec) : 20=0.01%, 50=0.01%, 100=0.01%, 250=0.01%, 500=0.01%
>
>     lat (usec) : 750=0.01%, 1000=0.01%
>
>     lat (msec) : 2=0.01%, 4=0.02%, 10=39.48%, 20=19.46%, 50=8.79%
>
>     lat (msec) : 100=4.69%, 250=9.58%, 500=7.63%, 750=3.74%, 1000=2.47%
>
>     lat (msec) : 2000=3.33%, >=2000=0.79%
>
>   cpu          : usr=0.92%, sys=13.35%, ctx=29141732, majf=0, minf=3026598
>
>   IO depths    : 1=0.1%, 2=0.1%, 4=0.1%, 8=0.1%, 16=0.1%, 32=0.1%, >=64=100.0%
>
>      submit    : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.0%
>
>      complete  : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.1%
>
>      issued    : total=r=0/w=33079899/d=0, short=r=0/w=0/d=0
>
> Run status group 0 (all jobs):
>
>   WRITE: io=129218MB, aggrb=734949KB/s, minb=734949KB/s, maxb=734949KB/s, mint=180039msec, maxt=180039msec
>
> Disk stats (read/write):
>
>   nvme0n1: ios=0/33078988, merge=0/0, ticks=0/5930480, in_queue=5933370, util=99.60%

そしてRandomRead。

> wheezy64:~# fio --filename=/mnt/p3700/hello  --direct=1 --rw=randread --bs=4k --size=2G --numjobs=64 --runtime=180 --name=file1 --ioengine=aio --iodepth=512 --group_reporting
>
> file1: (g=0): rw=randread, bs=4K-4K/4K-4K, ioengine=libaio, iodepth=512
>
> ...
>
> file1: (g=0): rw=randread, bs=4K-4K/4K-4K, ioengine=libaio, iodepth=512
>
> 2.0.8
>
> Starting 64 processes
>
> Jobs: 12 (f=6): [r__r____r___r__r__________r_r_r_r________________________r_r_r__] [93.2% done] [1403M/0K /s] [359K/0  iops] [eta 00m:08s]]
>
> file1: (groupid=0, jobs=64): err= 0: pid=21635
>
>   read : io=131072MB, bw=1194.3MB/s, iops=305724 , runt=109754msec
>
>     slat (usec): min=1 , max=104416 , avg=181.86, stdev=2273.95
>
>     clat (usec): min=88 , max=1698.4K, avg=94142.32, stdev=89737.06
>
>      lat (usec): min=102 , max=1698.5K, avg=94324.37, stdev=89854.71
>
>     clat percentiles (msec):
>
>      |  1.00th=[   17],  5.00th=[   27], 10.00th=[   32], 20.00th=[   37],
>
>      | 30.00th=[   42], 40.00th=[   57], 50.00th=[   72], 60.00th=[   85],
>
>      | 70.00th=[  102], 80.00th=[  131], 90.00th=[  180], 95.00th=[  241],
>
>      | 99.00th=[  478], 99.50th=[  594], 99.90th=[  865], 99.95th=[  979],
>
>      | 99.99th=[ 1270]
>
>     bw (KB/s)  : min=    6, max=164272, per=1.77%, avg=21641.11, stdev=11545.90
>
>     lat (usec) : 100=0.01%, 250=0.01%, 500=0.01%, 750=0.01%, 1000=0.01%
>
>     lat (msec) : 2=0.01%, 4=0.03%, 10=0.40%, 20=1.29%, 50=34.99%
>
>     lat (msec) : 100=32.37%, 250=26.29%, 500=3.75%, 750=0.66%, 1000=0.15%
>
>     lat (msec) : 2000=0.05%
>
>   cpu          : usr=1.34%, sys=37.50%, ctx=2798932, majf=0, minf=1003485
>
>   IO depths    : 1=0.1%, 2=0.1%, 4=0.1%, 8=0.1%, 16=0.1%, 32=0.1%, >=64=100.0%
>
>      submit    : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.0%
>
>      complete  : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.1%
>
>      issued    : total=r=33554432/w=0/d=0, short=r=0/w=0/d=0
>
> Run status group 0 (all jobs):
>
>    READ: io=131072MB, aggrb=1194.3MB/s, minb=1194.3MB/s, maxb=1194.3MB/s, mint=109754msec, maxt=109754msec
>
> Disk stats (read/write):
>
>   nvme0n1: ios=33536051/4, merge=0/0, ticks=4207010/0, in_queue=4260150, util=100.00%

レポートから結果を抜粋してみると。 **write 183,737iops、read 305,724iops**とこれも**爆速****です！！ ** 

最後にざっくりとmysqlのベンチマークを実行してみます。

Intel SSD DC P3700の場合

MySQLバージョン: "5.5.38"

> root@kvm3:~# time mysqlslap --concurrency=50 --iterations=1 --auto-generate-sql --engine=innodb --auto-generate-sql-load-type=write --number-of-queries=5000000  --port=3306 --host=197.3.o -proot
>
> Benchmark
>
> Running for engine innodb
>
> Average number of seconds to run all queries: 153.368 seconds
>
> Minimum number of seconds to run all queries: 153.368 seconds
>
> Maximum number of seconds to run all queries: 153.368 seconds
>
> Number of clients running queries: 50
>
> Average number of queries per client: 100000
>
>
>
> real 2m33.485s
>
> user 0m38.288s
>
> sys 4m37.968s

5,000,000クエリーを213.485秒で処理したので、約23,420クエリー/秒の処理性能でした。

ちなみに、AWSのRDSの場合は以下の通りでした。

インスタンスタイプ: db.t2.medium

MySQLバージョン: "5.6.17"

ストレージサイズ: 10GB

> root@aws2:~# time mysqlslap --concurrency=50 --iterations=1 --auto-generate-sql --engine=innodb --auto-generate-sql-load-type=write --number-of-queries=5000000  --port=3306 --host=test.hsjektsilal9.ap-northeast-1.rds.amazonaws.com -p -vv
>
> Building Create Statements for Auto
>
> Building Query Statements for Auto
>
> Generating INSERT Statements for Auto
>
> Parsing engines to use.
>
> Starting Concurrency Test
>
> Loading Pre-data
>
> Generating primary key list
>
> Generating stats
>
> Benchmark
>
>         Running for engine innodb
>
>         Average number of seconds to run all queries: 1082.128 seconds
>
>         Minimum number of seconds to run all queries: 1082.128 seconds
>
>         Maximum number of seconds to run all queries: 1082.128 seconds
>
>         Number of clients running queries: 50
>
>         Average number of queries per client: 100000
>
>
>
> real    18m2.874s
>
> user    0m8.965s
>
> sys     0m46.891s

5,000,000クエリーを1082.128秒で処理したので、約4,620クエリー/秒の処理性能でした。

これも**爆速**といえるでしょう！！

MySQL用のストレージとして、Intel DC P3700いかがでしょうか？

現場からは以上です！
