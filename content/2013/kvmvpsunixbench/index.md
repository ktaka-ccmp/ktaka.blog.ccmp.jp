+++
title = "KVMのゲストマシンとさくらのVPSでUnixBench採ってみました"
date = 2013-05-09
path = "2013/05/kvmvpsunixbench.html"
+++

みなさん、こんにちは(^^)/

楽しかったゴールデンウィークも終わってしましたが、いかがお過ごしでしょうか？

私はというと、行楽日和の晴天を横目に、薄暗い事務所の中でコンピューターに向かって黙々と仕事をこなす毎日ですw

さて、仕事でUnixBenchを採る機会がありましたので、個人的な備忘録の意味も含め、ここに記録して(晒して)おきたいと思います。

UnixBenchは以下のページから取ってきます。

[https://code.google.com/p/byte-unixbench/](https://code.google.com/p/byte-unixbench/)

> wget http://byte-unixbench.googlecode.com/files/UnixBench5.1.3.tgz
>
> tar xvf UnixBench5.1.3.tgz
>
> cd UnixBench

USAGEをざっと眺めると、makeして./Runスクリプトを実行すれば用意されたすべてのテストが実行されるらしいです。

バージョン5.1から新しく用意されたGRAPHICテストを実行したい場合には、Makefileを編集し"GRAPHIC_TESTS = defined"の行を有効にしてmakeする必要がありますが、今回は不要です。 

CPUが二つ以上のシステムの場合、テストは二回実行されます。一回目は一セットのテストが同時実行され、二回目はCPUの数をNとすると、Nセットのテストが並列に同時実行されます。 

テストの実行時間は一セットおよそ29分で、マルチCPUマシン上で、GRAPHICテストを行わない場合、およそ、58分程度かかるということです。

今回UnixBenchを実行したのは以下のマシンです。

(1)さくらのVPS512@980円　

> CPU  Intel(R) Core(TM)2 Duo CPU T7700 @ 2.40GHz　x 2
>
> メモリー　1GByte
>
> OS Debian 6.0.7 Kernel 2.6.32 SMP x86_64

(2)内製KVMゲストマシン1　(ホストCPU　Xeon X5650 @ 2.67GHz)

> CPU   QEMU Virtual CPU version 1.0 2.67GHz x 2
>
> メモリー 512MByte
>
> OS Debian 7.0 Kernel 3.9.1 SMP x86_64

(3)内製KVMゲストマシン2　(ホストCPU　Xeon X3440  @ 2.53GHz)

> CPU   QEMU Virtual CPU version 1.0 2.52GHz x 2
>
> メモリー 512MByte
>
> OS Debian 7.0 Kernel 3.8.8 SMP x86_64

(4)(3)のホストマシン　

> CPU   Intel(R) Xeon(R) CPU  X3440  @ 2.53GHz　4core 8thread
>
> メモリー 4GByte
>
> OS Debian 6.0.7 Kernel 3.4.0 SMP x86_64

(1)さくらのVPS512の結果

> ```
   BYTE UNIX Benchmarks (Version 5.1.3)

   System: sak1: GNU/Linux
   OS: GNU/Linux -- 2.6.32-5-amd64 -- #1 SMP Mon Jan 9 20:49:59 UTC 2012
   Machine: x86_64 (unknown)
   Language: en_US.utf8 (charmap="ANSI_X3.4-1968", collate="ANSI_X3.4-1968")
   CPU 0: Intel(R) Core(TM)2 Duo CPU T7700 @ 2.40GHz (5320.2 bogomips)
          x86-64, MMX, Physical Address Ext, SYSENTER/SYSEXIT, SYSCALL/SYSRET
   CPU 1: Intel(R) Core(TM)2 Duo CPU T7700 @ 2.40GHz (5320.2 bogomips)
          x86-64, MMX, Physical Address Ext, SYSENTER/SYSEXIT, SYSCALL/SYSRET
   13:48:04 up 146 days, 11:37,  1 user,  load average: 0.22, 0.12, 0.04; runlevel

------------------------------------------------------------------------
Benchmark Run: Wed May 08 2013 13:48:04 - 14:16:18
2 CPUs in system; running 1 parallel copy of tests

Dhrystone 2 using register variables       24085942.4 lps   (10.0 s, 7 samples)
Double-Precision Whetstone                     3098.5 MWIPS (9.9 s, 7 samples)
Execl Throughput                               2249.6 lps   (30.0 s, 2 samples)
File Copy 1024 bufsize 2000 maxblocks        671875.9 KBps  (30.0 s, 2 samples)
File Copy 256 bufsize 500 maxblocks          196527.3 KBps  (30.0 s, 2 samples)
File Copy 4096 bufsize 8000 maxblocks       1413265.2 KBps  (30.0 s, 2 samples)
Pipe Throughput                             1897140.7 lps   (10.0 s, 7 samples)
Pipe-based Context Switching                 287952.8 lps   (10.0 s, 7 samples)
Process Creation                               5839.1 lps   (30.0 s, 2 samples)
Shell Scripts (1 concurrent)                   5899.8 lpm   (60.0 s, 2 samples)
Shell Scripts (8 concurrent)                   1365.4 lpm   (60.0 s, 2 samples)
System Call Overhead                        3301152.6 lps   (10.0 s, 7 samples)

System Benchmarks Index Values               BASELINE       RESULT    INDEX
Dhrystone 2 using register variables         116700.0   24085942.4   2063.9
Double-Precision Whetstone                       55.0       3098.5    563.4
Execl Throughput                                 43.0       2249.6    523.2
File Copy 1024 bufsize 2000 maxblocks          3960.0     671875.9   1696.7
File Copy 256 bufsize 500 maxblocks            1655.0     196527.3   1187.5
File Copy 4096 bufsize 8000 maxblocks          5800.0    1413265.2   2436.7
Pipe Throughput                               12440.0    1897140.7   1525.0
Pipe-based Context Switching                   4000.0     287952.8    719.9
Process Creation                                126.0       5839.1    463.4
Shell Scripts (1 concurrent)                     42.4       5899.8   1391.5
Shell Scripts (8 concurrent)                      6.0       1365.4   2275.7
System Call Overhead                          15000.0    3301152.6   2200.8
                                                                   ========
System Benchmarks Index Score                                        1217.3

------------------------------------------------------------------------
Benchmark Run: Wed May 08 2013 14:16:18 - 14:44:33
2 CPUs in system; running 2 parallel copies of tests

Dhrystone 2 using register variables       48543864.7 lps   (10.0 s, 7 samples)
Double-Precision Whetstone                     6093.3 MWIPS (10.0 s, 7 samples)
Execl Throughput                               6641.9 lps   (29.6 s, 2 samples)
File Copy 1024 bufsize 2000 maxblocks        775102.5 KBps  (30.0 s, 2 samples)
File Copy 256 bufsize 500 maxblocks          214100.7 KBps  (30.0 s, 2 samples)
File Copy 4096 bufsize 8000 maxblocks       2170934.3 KBps  (30.0 s, 2 samples)
Pipe Throughput                             3701877.8 lps   (10.0 s, 7 samples)
Pipe-based Context Switching                 603992.9 lps   (10.0 s, 7 samples)
Process Creation                              21862.8 lps   (30.0 s, 2 samples)
Shell Scripts (1 concurrent)                  10135.8 lpm   (60.0 s, 2 samples)
Shell Scripts (8 concurrent)                   1410.2 lpm   (60.0 s, 2 samples)
System Call Overhead                        5432476.9 lps   (10.0 s, 7 samples)

System Benchmarks Index Values               BASELINE       RESULT    INDEX
Dhrystone 2 using register variables         116700.0   48543864.7   4159.7
Double-Precision Whetstone                       55.0       6093.3   1107.9
Execl Throughput                                 43.0       6641.9   1544.6
File Copy 1024 bufsize 2000 maxblocks          3960.0     775102.5   1957.3
File Copy 256 bufsize 500 maxblocks            1655.0     214100.7   1293.7
File Copy 4096 bufsize 8000 maxblocks          5800.0    2170934.3   3743.0
Pipe Throughput                               12440.0    3701877.8   2975.8
Pipe-based Context Switching                   4000.0     603992.9   1510.0
Process Creation                                126.0      21862.8   1735.1
Shell Scripts (1 concurrent)                     42.4      10135.8   2390.5
Shell Scripts (8 concurrent)                      6.0       1410.2   2350.3
System Call Overhead                          15000.0    5432476.9   3621.7
                                                                   ========
System Benchmarks Index Score                                        2166.7
```

(2)内製KVMゲストマシン1　(ホストCPU　Xeon X5650 @ 2.67GHz)

> ```
BYTE UNIX Benchmarks (Version 5.1.3)
   System: v147: GNU/Linux
   OS: GNU/Linux -- 3.9.1-64kvmg01 -- #1 SMP Wed May 8 22:00:45 JST 2013
   Machine: x86_64 (unknown)
   Language: en_US.utf8 (charmap="ANSI_X3.4-1968", collate="ANSI_X3.4-1968")
   CPU 0: QEMU Virtual CPU version 1.0 (5333.3 bogomips)
          x86-64, MMX, Physical Address Ext, SYSENTER/SYSEXIT, SYSCALL/SYSRET
   CPU 1: QEMU Virtual CPU version 1.0 (5333.3 bogomips)
          x86-64, MMX, Physical Address Ext, SYSENTER/SYSEXIT, SYSCALL/SYSRET
   15:34:32 up 0 min,  1 user,  load average: 0.16, 0.03, 0.01; runlevel 2
------------------------------------------------------------------------
Benchmark Run: Thu May 09 2013 15:34:32 - 16:02:31
2 CPUs in system; running 1 parallel copy of tests
Dhrystone 2 using register variables       30879094.2 lps   (10.0 s, 7 samples)
Double-Precision Whetstone                     3749.0 MWIPS (9.1 s, 7 samples)
Execl Throughput                               4534.2 lps   (30.0 s, 2 samples)
File Copy 1024 bufsize 2000 maxblocks       1097888.6 KBps  (30.0 s, 2 samples)
File Copy 256 bufsize 500 maxblocks          301066.2 KBps  (30.0 s, 2 samples)
File Copy 4096 bufsize 8000 maxblocks       2055234.3 KBps  (30.0 s, 2 samples)
Pipe Throughput                             2216106.5 lps   (10.0 s, 7 samples)
Pipe-based Context Switching                 381391.5 lps   (10.0 s, 7 samples)
Process Creation                               5417.9 lps   (30.0 s, 2 samples)
Shell Scripts (1 concurrent)                   9541.0 lpm   (60.0 s, 2 samples)
Shell Scripts (8 concurrent)                   2040.2 lpm   (60.0 s, 2 samples)
System Call Overhead                        4035159.8 lps   (10.0 s, 7 samples)
System Benchmarks Index Values               BASELINE       RESULT    INDEX
Dhrystone 2 using register variables         116700.0   30879094.2   2646.0
Double-Precision Whetstone                       55.0       3749.0    681.6
Execl Throughput                                 43.0       4534.2   1054.5
File Copy 1024 bufsize 2000 maxblocks          3960.0    1097888.6   2772.4
File Copy 256 bufsize 500 maxblocks            1655.0     301066.2   1819.1
File Copy 4096 bufsize 8000 maxblocks          5800.0    2055234.3   3543.5
Pipe Throughput                               12440.0    2216106.5   1781.4
Pipe-based Context Switching                   4000.0     381391.5    953.5
Process Creation                                126.0       5417.9    430.0
Shell Scripts (1 concurrent)                     42.4       9541.0   2250.2
Shell Scripts (8 concurrent)                      6.0       2040.2   3400.3
System Call Overhead                          15000.0    4035159.8   2690.1
                                                                   ========
System Benchmarks Index Score                                        1681.5
------------------------------------------------------------------------
Benchmark Run: Thu May 09 2013 16:02:31 - 16:30:31
2 CPUs in system; running 2 parallel copies of tests
Dhrystone 2 using register variables       61886737.4 lps   (10.0 s, 7 samples)
Double-Precision Whetstone                     7438.8 MWIPS (9.1 s, 7 samples)
Execl Throughput                               8960.8 lps   (30.0 s, 2 samples)
File Copy 1024 bufsize 2000 maxblocks       1356632.6 KBps  (30.0 s, 2 samples)
File Copy 256 bufsize 500 maxblocks          228901.8 KBps  (30.0 s, 2 samples)
File Copy 4096 bufsize 8000 maxblocks       3404779.9 KBps  (30.0 s, 2 samples)
Pipe Throughput                             4411432.3 lps   (10.0 s, 7 samples)
Pipe-based Context Switching                 792350.4 lps   (10.0 s, 7 samples)
Process Creation                              29506.4 lps   (30.0 s, 2 samples)
Shell Scripts (1 concurrent)                  16737.4 lpm   (60.0 s, 2 samples)
Shell Scripts (8 concurrent)                   2339.6 lpm   (60.0 s, 2 samples)
System Call Overhead                        6544409.1 lps   (10.0 s, 7 samples)
System Benchmarks Index Values               BASELINE       RESULT    INDEX
Dhrystone 2 using register variables         116700.0   61886737.4   5303.1
Double-Precision Whetstone                       55.0       7438.8   1352.5
Execl Throughput                                 43.0       8960.8   2083.9
File Copy 1024 bufsize 2000 maxblocks          3960.0    1356632.6   3425.8
File Copy 256 bufsize 500 maxblocks            1655.0     228901.8   1383.1
File Copy 4096 bufsize 8000 maxblocks          5800.0    3404779.9   5870.3
Pipe Throughput                               12440.0    4411432.3   3546.2
Pipe-based Context Switching                   4000.0     792350.4   1980.9
Process Creation                                126.0      29506.4   2341.8
Shell Scripts (1 concurrent)                     42.4      16737.4   3947.5
Shell Scripts (8 concurrent)                      6.0       2339.6   3899.4
System Call Overhead                          15000.0    6544409.1   4362.9
                                                                   ========
System Benchmarks Index Score                                        2963.7
```

(3)内製KVMゲストマシン2　(ホストCPU　Xeon X3440  @ 2.53GHz)

> ```
BYTE UNIX Benchmarks (Version 5.1.3)
   System: v153: GNU/Linux
   OS: GNU/Linux -- 3.8.8-64kvmg01 -- #1 SMP Mon Apr 22 23:44:25 JST 2013
   Machine: x86_64 (unknown)
   Language: en_US.utf8 (charmap="ANSI_X3.4-1968", collate="ANSI_X3.4-1968")
   CPU 0: QEMU Virtual CPU version 1.4.1 (5066.6 bogomips)
          x86-64, MMX, Physical Address Ext, SYSENTER/SYSEXIT, SYSCALL/SYSRET
   CPU 1: QEMU Virtual CPU version 1.4.1 (5066.6 bogomips)
          x86-64, MMX, Physical Address Ext, SYSENTER/SYSEXIT, SYSCALL/SYSRET
   04:21:48 up 2 min,  2 users,  load average: 0.06, 0.02, 0.01; runlevel 2
------------------------------------------------------------------------
Benchmark Run: Fri May 10 2013 04:21:48 - 04:49:56
2 CPUs in system; running 1 parallel copy of tests
Dhrystone 2 using register variables       28700468.1 lps   (10.0 s, 7 samples)
Double-Precision Whetstone                     3603.2 MWIPS (10.0 s, 7 samples)
Execl Throughput                               4820.8 lps   (30.0 s, 2 samples)
File Copy 1024 bufsize 2000 maxblocks       1136729.9 KBps  (30.0 s, 2 samples)
File Copy 256 bufsize 500 maxblocks          313902.4 KBps  (30.0 s, 2 samples)
File Copy 4096 bufsize 8000 maxblocks       2329713.1 KBps  (30.0 s, 2 samples)
Pipe Throughput                             1937085.6 lps   (10.0 s, 7 samples)
Pipe-based Context Switching                 416442.2 lps   (10.0 s, 7 samples)
Process Creation                               4905.0 lps   (30.0 s, 2 samples)
Shell Scripts (1 concurrent)                   5206.7 lpm   (60.0 s, 2 samples)
Shell Scripts (8 concurrent)                   2342.7 lpm   (60.0 s, 2 samples)
System Call Overhead                        3696866.5 lps   (10.0 s, 7 samples)
System Benchmarks Index Values               BASELINE       RESULT    INDEX
Dhrystone 2 using register variables         116700.0   28700468.1   2459.3
Double-Precision Whetstone                       55.0       3603.2    655.1
Execl Throughput                                 43.0       4820.8   1121.1
File Copy 1024 bufsize 2000 maxblocks          3960.0    1136729.9   2870.5
File Copy 256 bufsize 500 maxblocks            1655.0     313902.4   1896.7
File Copy 4096 bufsize 8000 maxblocks          5800.0    2329713.1   4016.7
Pipe Throughput                               12440.0    1937085.6   1557.1
Pipe-based Context Switching                   4000.0     416442.2   1041.1
Process Creation                                126.0       4905.0    389.3
Shell Scripts (1 concurrent)                     42.4       5206.7   1228.0
Shell Scripts (8 concurrent)                      6.0       2342.7   3904.5
System Call Overhead                          15000.0    3696866.5   2464.6
                                                                   ========
System Benchmarks Index Score                                        1606.1
------------------------------------------------------------------------
Benchmark Run: Fri May 10 2013 04:49:56 - 05:18:04
2 CPUs in system; running 2 parallel copies of tests
Dhrystone 2 using register variables       54903785.4 lps   (10.0 s, 7 samples)
Double-Precision Whetstone                     6894.6 MWIPS (10.0 s, 7 samples)
Execl Throughput                               9306.8 lps   (30.0 s, 2 samples)
File Copy 1024 bufsize 2000 maxblocks       1347898.4 KBps  (30.0 s, 2 samples)
File Copy 256 bufsize 500 maxblocks          354944.7 KBps  (30.0 s, 2 samples)
File Copy 4096 bufsize 8000 maxblocks       3256880.8 KBps  (30.0 s, 2 samples)
Pipe Throughput                             3680672.6 lps   (10.0 s, 7 samples)
Pipe-based Context Switching                 740043.1 lps   (10.0 s, 7 samples)
Process Creation                              34071.7 lps   (30.0 s, 2 samples)
Shell Scripts (1 concurrent)                  17647.1 lpm   (60.0 s, 2 samples)
Shell Scripts (8 concurrent)                   2415.1 lpm   (60.0 s, 2 samples)
System Call Overhead                        5929544.7 lps   (10.0 s, 7 samples)
System Benchmarks Index Values               BASELINE       RESULT    INDEX
Dhrystone 2 using register variables         116700.0   54903785.4   4704.7
Double-Precision Whetstone                       55.0       6894.6   1253.6
Execl Throughput                                 43.0       9306.8   2164.4
File Copy 1024 bufsize 2000 maxblocks          3960.0    1347898.4   3403.8
File Copy 256 bufsize 500 maxblocks            1655.0     354944.7   2144.7
File Copy 4096 bufsize 8000 maxblocks          5800.0    3256880.8   5615.3
Pipe Throughput                               12440.0    3680672.6   2958.7
Pipe-based Context Switching                   4000.0     740043.1   1850.1
Process Creation                                126.0      34071.7   2704.1
Shell Scripts (1 concurrent)                     42.4      17647.1   4162.0
Shell Scripts (8 concurrent)                      6.0       2415.1   4025.1
System Call Overhead                          15000.0    5929544.7   3953.0
                                                                   ========
System Benchmarks Index Score                                        2991.1
```

(4)(3)のホストマシン　

> ```
BYTE UNIX Benchmarks (Version 5.1.3)
   System: kvm: GNU/Linux
   OS: GNU/Linux -- 3.4.0-64kvmh01 -- #1 SMP Fri May 25 14:59:18 JST 2012
   Machine: x86_64 (unknown)
   Language: en_US.utf8 (charmap="ANSI_X3.4-1968", collate="ANSI_X3.4-1968")
   CPU 0: Intel(R) Xeon(R) CPU X3440 @ 2.53GHz (5066.2 bogomips)
          Hyper-Threading, x86-64, MMX, Physical Address Ext, SYSENTER/SYSEXIT, SYSCALL/SYSRET, Intel virtualization
   CPU 1: Intel(R) Xeon(R) CPU X3440 @ 2.53GHz (5066.2 bogomips)
          Hyper-Threading, x86-64, MMX, Physical Address Ext, SYSENTER/SYSEXIT, SYSCALL/SYSRET, Intel virtualization
   CPU 2: Intel(R) Xeon(R) CPU X3440 @ 2.53GHz (5066.2 bogomips)
          Hyper-Threading, x86-64, MMX, Physical Address Ext, SYSENTER/SYSEXIT, SYSCALL/SYSRET, Intel virtualization
   CPU 3: Intel(R) Xeon(R) CPU X3440 @ 2.53GHz (5066.2 bogomips)
          Hyper-Threading, x86-64, MMX, Physical Address Ext, SYSENTER/SYSEXIT, SYSCALL/SYSRET, Intel virtualization
   CPU 4: Intel(R) Xeon(R) CPU X3440 @ 2.53GHz (5066.2 bogomips)
          Hyper-Threading, x86-64, MMX, Physical Address Ext, SYSENTER/SYSEXIT, SYSCALL/SYSRET, Intel virtualization
   CPU 5: Intel(R) Xeon(R) CPU X3440 @ 2.53GHz (5066.2 bogomips)
          Hyper-Threading, x86-64, MMX, Physical Address Ext, SYSENTER/SYSEXIT, SYSCALL/SYSRET, Intel virtualization
   CPU 6: Intel(R) Xeon(R) CPU X3440 @ 2.53GHz (5066.2 bogomips)
          Hyper-Threading, x86-64, MMX, Physical Address Ext, SYSENTER/SYSEXIT, SYSCALL/SYSRET, Intel virtualization
   CPU 7: Intel(R) Xeon(R) CPU X3440 @ 2.53GHz (5066.2 bogomips)
          Hyper-Threading, x86-64, MMX, Physical Address Ext, SYSENTER/SYSEXIT, SYSCALL/SYSRET, Intel virtualization
   20:37:04 up 113 days,  7:51,  2 users,  load average: 0.50, 0.22, 0.52; runlevel 2
------------------------------------------------------------------------
Benchmark Run: Thu May 09 2013 20:37:04 - 21:05:17
8 CPUs in system; running 1 parallel copy of tests
Dhrystone 2 using register variables       28301315.7 lps   (10.0 s, 7 samples)
Double-Precision Whetstone                     3470.1 MWIPS (10.0 s, 7 samples)
Execl Throughput                               1569.0 lps   (29.9 s, 2 samples)
File Copy 1024 bufsize 2000 maxblocks        841958.4 KBps  (30.0 s, 2 samples)
File Copy 256 bufsize 500 maxblocks          235274.3 KBps  (30.0 s, 2 samples)
File Copy 4096 bufsize 8000 maxblocks       1938405.5 KBps  (30.0 s, 2 samples)
Pipe Throughput                             1827474.3 lps   (10.0 s, 7 samples)
Pipe-based Context Switching                  54481.2 lps   (10.0 s, 7 samples)
Process Creation                               3844.0 lps   (30.0 s, 2 samples)
Shell Scripts (1 concurrent)                   3859.0 lpm   (60.0 s, 2 samples)
Shell Scripts (8 concurrent)                   2910.4 lpm   (60.0 s, 2 samples)
System Call Overhead                        3240538.1 lps   (10.0 s, 7 samples)
System Benchmarks Index Values               BASELINE       RESULT    INDEX
Dhrystone 2 using register variables         116700.0   28301315.7   2425.1
Double-Precision Whetstone                       55.0       3470.1    630.9
Execl Throughput                                 43.0       1569.0    364.9
File Copy 1024 bufsize 2000 maxblocks          3960.0     841958.4   2126.2
File Copy 256 bufsize 500 maxblocks            1655.0     235274.3   1421.6
File Copy 4096 bufsize 8000 maxblocks          5800.0    1938405.5   3342.1
Pipe Throughput                               12440.0    1827474.3   1469.0
Pipe-based Context Switching                   4000.0      54481.2    136.2
Process Creation                                126.0       3844.0    305.1
Shell Scripts (1 concurrent)                     42.4       3859.0    910.1
Shell Scripts (8 concurrent)                      6.0       2910.4   4850.6
System Call Overhead                          15000.0    3240538.1   2160.4
                                                                   ========
System Benchmarks Index Score                                        1104.1
------------------------------------------------------------------------
Benchmark Run: Thu May 09 2013 21:05:17 - 21:33:41
8 CPUs in system; running 8 parallel copies of tests
Dhrystone 2 using register variables      110467624.7 lps   (10.0 s, 7 samples)
Double-Precision Whetstone                    21211.4 MWIPS (9.9 s, 7 samples)
Execl Throughput                              12952.9 lps   (30.0 s, 2 samples)
File Copy 1024 bufsize 2000 maxblocks        495833.5 KBps  (30.0 s, 2 samples)
File Copy 256 bufsize 500 maxblocks          134897.1 KBps  (30.0 s, 2 samples)
File Copy 4096 bufsize 8000 maxblocks       1547822.4 KBps  (30.0 s, 2 samples)
Pipe Throughput                             2276741.3 lps   (10.0 s, 7 samples)
Pipe-based Context Switching                 455844.3 lps   (10.0 s, 7 samples)
Process Creation                              30000.0 lps   (30.0 s, 2 samples)
Shell Scripts (1 concurrent)                  28230.5 lpm   (60.0 s, 2 samples)
Shell Scripts (8 concurrent)                   3724.5 lpm   (60.0 s, 2 samples)
System Call Overhead                        3454619.9 lps   (10.0 s, 7 samples)
System Benchmarks Index Values               BASELINE       RESULT    INDEX
Dhrystone 2 using register variables         116700.0  110467624.7   9465.9
Double-Precision Whetstone                       55.0      21211.4   3856.6
Execl Throughput                                 43.0      12952.9   3012.3
File Copy 1024 bufsize 2000 maxblocks          3960.0     495833.5   1252.1
File Copy 256 bufsize 500 maxblocks            1655.0     134897.1    815.1
File Copy 4096 bufsize 8000 maxblocks          5800.0    1547822.4   2668.7
Pipe Throughput                               12440.0    2276741.3   1830.2
Pipe-based Context Switching                   4000.0     455844.3   1139.6
Process Creation                                126.0      30000.0   2381.0
Shell Scripts (1 concurrent)                     42.4      28230.5   6658.1
Shell Scripts (8 concurrent)                      6.0       3724.5   6207.5
System Call Overhead                          15000.0    3454619.9   2303.1
                                                                   ========
System Benchmarks Index Score                                        2686.9
```

以上の結果を見ると、CPU8個のサーバより、2CPUの仮想マシンゲストの方が最終スコアが高かったり、FileCopy関連のインデックスが仮想マシンの方が軒並み高かったり、理解に苦しむ結果が出ています。

今後、別のベンチマークツールで試してみたいと思います。

追記　System Benchmarks Index Scoreではなく、個別のテストごとに比較すべきか。
