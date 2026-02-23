+++
title = "もろもろLinpack Benchmarkしてみました"
date = 2013-05-21
path = "2013/05/linpack-benchmark.html"
+++

こんにちは！

今日は、引きこもって仕事をするには、もったいないくらいの良いお天気でしたね♪

なかなか良い季節になってきたので、週末が楽しみです。

前回に引き続き、いくつかのサーバでベンチマークを採る機会があったので、ここに晒します。

Linpack ベンチマークは「一番じゃなきゃダメですか」で有名なスパコンのランキングを決定するためにも使われる、有名なベンチマークソフトです。

> LINPACK ベンチマークは LINPACK に基づいたベンチマークプログラムで、システムの浮動小数点演算性能を評価する。ジャック・ドンガラが考案したもので、理学・工学で一般的な n×n の線型方程式系 Ax = b を解く速度を測定する。このベンチマークの最新版はTOP500で世界の高速なコンピュータの性能値としてランキングに使用されている。　[http://ja.wikipedia.org/wiki/LINPACK](http://ja.wikipedia.org/wiki/LINPACK)　より

 スパコンの評価のためには、並列計算用のMPIライブラリや、行列計算ライブラリ、LINPACK本体等、いろいろセットアップが必要です。

クラスター構成ではない普通のSMPマシンを評価するには、IntelのOptimized LINPACK Benchmarkというのを使えば、お手軽にベンチマークができそうです。

まず、以下のページから、tarボールをダウンロードし、展開します。

> [http://software.intel.com/en-us/articles/intel-math-kernel-library-linpack-download/](http://software.intel.com/en-us/articles/intel-math-kernel-library-linpack-download/)
>
> wget http://registrationcenter.intel.com/irc_nas/3058/l_lpk_p_11.0.3.008.tgz
>
> tar xvf  l_lpk_p_11.0.3.008.tgz

以下のディレクトリにベンチマーク本体、スクリプト、入力ファイルなどが用意されているので、そのディレクトリで標準的なrunme_xeon64などのスクリプトを実行すれば良さそうです。

> cd  linpack_11.0.3/benchmarks/linpack/

 試しに実行してみます。

```
./runme_xeon64
This is a SAMPLE run script for SMP LINPACK. Change it to reflect
the correct number of CPUs/threads, problem input files, etc..
Tue May 14 18:47:46 JST 2013
Intel(R) Optimized LINPACK Benchmark data
Current date/time: Tue May 14 18:47:46 2013
CPU frequency:    2.932 GHz
Number of CPUs: 1
Number of cores: 4
Number of threads: 8
Parameters are set to:
Number of tests: 15
Number of equations to solve (problem size) : 1000  2000  5000  10000 15000 18000 20000 22000 25000 26000 27000 30000 35000 40000 45000
Leading dimension of array                  : 1000  2000  5008  10000 15000 18008 20016 22008 25000 26000 27000 30000 35000 40000 45000
Number of trials to run                     : 4     2     2     2     2     2     2     2     2     2     1     1     1     1     1
Data alignment value (in Kbytes)            : 4     4     4     4     4     4     4     4     4     4     4     1     1     1     1
Maximum memory requested that can be used=3202964416, at the size=20000
=================== Timing linear equation system solver ===================
Size   LDA    Align. Time(s)    GFlops   Residual     Residual(norm) Check
1000   1000   4      0.038      17.4850  1.236872e-12 4.218050e-02   pass
1000   1000   4      0.037      17.9669  1.236872e-12 4.218050e-02   pass
1000   1000   4      0.037      17.9904  1.236872e-12 4.218050e-02   pass
1000   1000   4      0.037      18.0328  1.236872e-12 4.218050e-02   pass
2000   2000   4      0.271      19.7349  4.570122e-12 3.975446e-02   pass
2000   2000   4      0.270      19.7479  4.570122e-12 3.975446e-02   pass
5000   5008   4      2.512      33.1981  2.113014e-11 2.946428e-02   pass
5000   5008   4      2.492      33.4647  2.113014e-11 2.946428e-02   pass
10000  10000  4      17.385     38.3576  9.365270e-11 3.302289e-02   pass
10000  10000  4      17.431     38.2572  9.365270e-11 3.302289e-02   pass
15000  15000  4      59.425     37.8704  2.005595e-10 3.158845e-02   pass
15000  15000  4      60.409     37.2536  2.005595e-10 3.158845e-02   pass
18000  18008  4      103.157    37.6964  2.980711e-10 3.264245e-02   pass
18000  18008  4      102.891    37.7938  2.980711e-10 3.264245e-02   pass
20000  20016  4      142.172    37.5190  3.917629e-10 3.467960e-02   pass
20000  20016  4      142.003    37.5634  3.917629e-10 3.467960e-02   pass
Performance Summary (GFlops)
Size   LDA    Align.  Average  Maximal
1000   1000   4       17.8687  18.0328
2000   2000   4       19.7414  19.7479
5000   5008   4       33.3314  33.4647
10000  10000  4       38.3074  38.3576
15000  15000  4       37.5620  37.8704
18000  18008  4       37.7451  37.7938
20000  20016  4       37.5412  37.5634
Residual checks PASSED
End of tests
Done: Tue May 14 19:01:30 JST 2013
```

上記は、4コア、8スレッドのCPUを搭載したサーバーですが、自動的にCPUの数を認識して、適切なThread数を設定してくれているようです。

runme_xeon64スクリプトの中で、"export OMP_NUM_THREADS=4"のように明示的にスレッド数を指定することも可能です。

入力ファイルでいくつかproblem sizeが指定されていますが、搭載しているメモリの容量から判断して、大きすぎるものは実行されないようです。

swapを含む、メモリ容量で実行可否を判断しているようなので、可能ならswapoff -aするか、あるいは、入力ファイルから大きすぎるものを削除した方が良いかもしれません。

上記の結果からは、最大で、38.4GFlopsの性能であると、判断できます。

さて、このLinpackベンチマークを、弊社にあるいくつかの物理マシン、仮想マシン上で実行してみました。

物理マシン

| マシン名 | CPU スペック | HT | メモリ GByte | 総クロック GHz | スコア GFlops | スコア/総クロック |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Xeon E5-2650 2.00GHz 8 core x 2cpu | on | 96 | 32 | 229.8 | 7.18 |
| 2 | Xeon E5-2650 2.00GHz 8 core x 2cpu | off | 96 | 32 | 231.0 | 7.22 |
| 3 | Xeon E5-2650 2.00GHz 4 core x 2cpu | on | 96 | 16 | 117.1 | 7.32 |
| 4 | Xeon E5-2603 1.80GHz 4 core x 2cpu | na | 96 | 14.4 | 103.8 | 7.21 |
| 5 | Xeon X5650 2.67GHz 6 core x 2cpu | on | 16 | 32.04 | 114.1 | 3.56 |
| 6 | Xeon X3440 2.53GHz 4 core x 1cpu | on | 4 | 10.12 | 38.0 | 3.75 |
| 7 | Xeon X3440 2.53GHz 4 core x 1cpu | on | 4 | 10.12 | 38.4 | 3.79 |

マシンスペック

1,2,3は同一マシンで、Supermicro 1027R-WRF/Xeon E5-2650 x 2/メモリ 96MByte/Intel 520 SSD 240GB。2ではBIOSでHyperThreadingを無効化、3ではBIOSでアクティブコア数を4個に制限しています。

4 はSupermicro 1027R-WR/Xeon E5-2603 x 2/メモリ 96MByte/Intel 520 SSD 240GB

5 はIntel S5520SC/Xeon X5650 x 2/メモリ 16MByte/Adaptec ASR-5405/HGST SATA 2TB HDD

6,7 Intel S3420GP /Xeon X3440 x 1/メモリ 4MByte/Seagate SATA 320GB HDD

表中の総クロックGHzはクロックxコア数で計算してあります。

1と2を比べるとHyperThreadingをOFFにしても、スコアが変わらないことがわかります。また、1と3を比べると、コア数が半分になり総クロックが半分になると、スコアが約半分になっています。

また、3と4からは、総クロックにだいたい比例しているようです。

したがって、Linpack性能は、同じ世代のCPUであればHTの有無には依存せず、総クロックに比例すると考えられます。

CPUの世代の異なる1と5を比べると、最新のXeon E5-2650(Sandybridge)のスコアは約230GFlopsで、一世代前のXeon X5650(Westmere)のスコア約114GFlops比べて、倍以上の性能があることがわかります。

Xeon X5650(Westmere)とXeon X3440(Lynnfield)は同じ世代のプロセッサですが、 5と6を比べてみると、だいたい総クロックに比例した性能になっていることがわかります。

一番右の行にスコア/総クロックを示してみましたが、[このページ](http://ja.wikipedia.org/wiki/FLOPS)によると理論性能は、Nehalem/Westmere/Lynnfield世代で4、Sandybridge世代で8であるので、だいたいこれに近い値になっていることがわかります。

次の上記のマシン上に作成した仮想マシンの性能を調べてみました。

仮想マシン

| マシン名 | 仮想マシン種類 | CPU スペック | メモリGByte | 総クロックGHz | スコアGFlops | スコア/総クロック |
| --- | --- | --- | --- | --- | --- | --- |
| kvm1 | kvm | 2.0GHz x 2 (Xeon E5-2650)   | 4 | 4 | 28.2 | 7.05 |
| kvm2 | kvm | 2.0GHz x 16 (Xeon E5-2650) | 4 | 32 | 187.3 | 5.85 |
| kvm3 | kvm | 2.67GHz x 2 (Xeon X5650) | 2 | 5.34 | 21.9 | 4.10 |
| kvm4 | kvm | 2.53GHz x 2 (Xeon X3440) | 2 | 5.06 | 20.13 | 3.98 |
| sak1 | Sakura VPS | 2.4GHz x 2 (Core 2 DuoT7700) | 1 | 4.8 | 11.7 | 2.43 |
| xen1 | xenserver 6.1 | 1.8GHz x 8 (Xeon E5-2603) | 4 | 14.4 | 6.8 | 0.47 |
| xen2 | xenserver 6.1 | 1.8GHz x 1 (Xeon E5-2603) | 4 | 1.8 | 6.8 | 3.78 |

kvm1のスコア/総クロックは7.05で理論値の8に近く、上の物理マシン表と比べても遜色なく、なかなか優秀と言えます。しかしながらkvm2の場合には、5.85と若干下がった値になっています。kvmのゲストカーネルはNUMA対応カーネルにしていないので、それが原因かもしれません。

kvm3、kvm4のスコア/総クロックを見ると優秀ではありますが、理論値の4に非常に近いか、又は超えてしまっており、ちょっと不自然です。ターボブースト機能により、実際のコアのクロックが上がっているのかもしれません。

sak1のスコア/総クロックは2.43は、Core 2 Duoの理論値4よりもだいぶ小さく、あまり優秀ではありません。

xen1、xen2も、Sandybridge世代の理論値8よりもかなり小さく、全く優秀ではありません。xen1は8CPUにも関わらず、1CPUのxen2とスコアが変わらず、仮想の8CPUのスレッドが、一個の物理コア上で実行されているように見受けられます。

以上、まとめると、

Linpackの性能はCPUの世代間で進歩があり、同じ世代のCPUであれば、おおよそクロックxコア数に比例しています。

また、kvmの仮想マシンは総じて優秀であるが、NUMAアーキテクチャのホストでホストのCPUと同じくらいのCPUをゲストに割り当てようとすると、性能は総クロックで期待されるよりも落ちてしまう。

xenserverはあまり、優秀ではありません。

SakuraのVPSもあまり優秀ではありません。

性能を求めるなら、最新の物理サーバを用いるのがおすすめで、仮想マシンを使いたいなら、VPSサービスではなく、自前でkvmによる仮想環境作るのが良いと言えるでしょう。
