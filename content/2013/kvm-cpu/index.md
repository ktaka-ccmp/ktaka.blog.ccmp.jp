+++
title = "kvmによる仮想マシン\"-cpu host\"オプションで性能向上する場合がある"
date = 2013-05-22
path = "2013/05/kvm-cpu.html"
+++

kvmのゲストマシンのチューニングをするために、以下のページを眺めていたら、

[http://www.linux-kvm.org/page/Tuning_KVM](http://www.linux-kvm.org/page/Tuning_KVM)

こんな、記述を発見しました。

> Modern processors come with a wide variety of performance enhancing features such as streaming instructions sets (sse) and other performance-enhancing instructions. These features vary from processor to processor. 

> QEMU and KVM default to a compatible subset of cpu features, so that if you change your host processor, or perform a live migration, the guest will see its cpu features unchanged. This is great for compatibility but comes at a performance cost. 

> To pass all available host processor features to the guest, use the command line switch
>
>  qemu -cpu host

なるほど-cpu hostをつければ、CPUの高速演算機能が使えて、性能が向上するかもしれないのか…

ということで試してみました。

"-cpu host"が無いゲストマシン

```
# egrep model /proc/cpuinfo
model           : 2
model name      : QEMU Virtual CPU version 1.4.1
model           : 2
model name      : QEMU Virtual CPU version 1.4.1
# egrep flags /proc/cpuinfo
flags           : fpu de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pse36 clflush mmx fxsr sse sse2 syscall nx lm rep_good nopl pni cx16 popcnt hypervisor lahf_lm
flags           : fpu de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pse36 clflush mmx fxsr sse sse2 syscall nx lm rep_good nopl pni cx16 popcnt hypervisor lahf_lm
```

"-cpu host"があるゲストマシン

```
# egrep model /proc/cpuinfo
model           : 45
model name      : Intel(R) Xeon(R) CPU E5-2650 0 @ 2.00GHz
model           : 45
model name      : Intel(R) Xeon(R) CPU E5-2650 0 @ 2.00GHz
# egrep flags /proc/cpuinfo
flags           : fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush mmx fxsr sse sse2 ss syscall nx pdpe1gb rdtscp lm constant_tsc arch_perfmon rep_good nopl eagerfpu pni pclmulqdq ssse3 cx16 pcid sse4_1 sse4_2 x2apic popcnt tsc_deadline_timer aes xsave avx hypervisor lahf_lm xsaveopt tsc_adjust
flags           : fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush mmx fxsr sse sse2 ss syscall nx pdpe1gb rdtscp lm constant_tsc arch_perfmon rep_good nopl eagerfpu pni pclmulqdq ssse3 cx16 pcid sse4_1 sse4_2 x2apic popcnt tsc_deadline_timer aes xsave avx hypervisor lahf_lm xsaveopt tsc_adjust
```

CPUの認識のされ方、見えてるflagの数が違います。

実際にlinpackベンチマークを採ってみました。

"-cpu host"が無いゲストマシン　13.0GFlops

```
# cat lin_xeon64.txt
Thu May 23 18:59:36 JST 2013
Intel(R) Optimized LINPACK Benchmark data
Current date/time: Thu May 23 18:59:36 2013
CPU frequency:    1.991 GHz
Number of CPUs: 2
Number of cores: 2
Number of threads: 2
Parameters are set to:
Number of tests: 15
Number of equations to solve (problem size) : 1000  2000  5000  10000 15000 18000 20000 22000 25000 26000 27000 30000 35000 40000 45000
Leading dimension of array                  : 1000  2000  5008  10000 15000 18008 20016 22008 25000 26000 27000 30000 35000 40000 45000
Number of trials to run                     : 4     2     2     2     2     2     2     2     2     2     1     1     1     1     1
Data alignment value (in Kbytes)            : 4     4     4     4     4     4     4     4     4     4     4     1     1     1     1
Maximum memory requested that can be used=3873852256, at the size=22000
=================== Timing linear equation system solver ===================
Size   LDA    Align. Time(s)    GFlops   Residual     Residual(norm) Check
1000   1000   4      0.073      9.1585   1.125766e-12 3.839152e-02   pass
1000   1000   4      0.058      11.5232  1.125766e-12 3.839152e-02   pass
1000   1000   4      0.058      11.5443  1.125766e-12 3.839152e-02   pass
1000   1000   4      0.059      11.2817  1.125766e-12 3.839152e-02   pass
2000   2000   4      0.440      12.1283  4.992673e-12 4.343014e-02   pass
2000   2000   4      0.440      12.1421  4.992673e-12 4.343014e-02   pass
5000   5008   4      6.610      12.6155  2.427966e-11 3.385603e-02   pass
5000   5008   4      6.605      12.6248  2.427966e-11 3.385603e-02   pass
10000  10000  4      51.994     12.8258  8.998519e-11 3.172969e-02   pass
10000  10000  4      51.965     12.8330  8.998519e-11 3.172969e-02   pass
15000  15000  4      174.335    12.9087  2.187028e-10 3.444605e-02   pass
15000  15000  4      173.510    12.9702  2.187028e-10 3.444605e-02   pass
18000  18008  4      298.936    13.0083  2.887995e-10 3.162709e-02   pass
18000  18008  4      298.826    13.0131  2.887995e-10 3.162709e-02   pass
20000  20016  4      409.500    13.0260  3.701985e-10 3.277068e-02   pass
20000  20016  4      408.885    13.0456  3.701985e-10 3.277068e-02   pass
22000  22008  4      544.380    13.0417  4.627267e-10 3.389291e-02   pass
22000  22008  4      544.508    13.0386  4.627267e-10 3.389291e-02   pass
Performance Summary (GFlops)
Size   LDA    Align.  Average  Maximal
1000   1000   4       10.8769  11.5443
2000   2000   4       12.1352  12.1421
5000   5008   4       12.6201  12.6248
10000  10000  4       12.8294  12.8330
15000  15000  4       12.9395  12.9702
18000  18008  4       13.0107  13.0131
20000  20016  4       13.0358  13.0456
22000  22008  4       13.0402  13.0417
Residual checks PASSED
End of tests
Done: Thu May 23 19:53:14 JST 2013
```

"-cpu host"があるゲストマシン　28.1GFlops

```
# cat lin_xeon64.txt
Thu May 23 18:58:46 JST 2013
Intel(R) Optimized LINPACK Benchmark data
Current date/time: Thu May 23 18:58:46 2013
CPU frequency:    1.991 GHz
Number of CPUs: 2
Number of cores: 2
Number of threads: 2
Parameters are set to:
Number of tests: 15
Number of equations to solve (problem size) : 1000  2000  5000  10000 15000 18000 20000 22000 25000 26000 27000 30000 35000 40000 45000
Leading dimension of array                  : 1000  2000  5008  10000 15000 18008 20016 22008 25000 26000 27000 30000 35000 40000 45000
Number of trials to run                     : 4     2     2     2     2     2     2     2     2     2     1     1     1     1     1
Data alignment value (in Kbytes)            : 4     4     4     4     4     4     4     4     4     4     4     1     1     1     1
Maximum memory requested that can be used=3873852256, at the size=22000
=================== Timing linear equation system solver ===================
Size   LDA    Align. Time(s)    GFlops   Residual     Residual(norm) Check
1000   1000   4      0.040      16.7342  1.029343e-12 3.510325e-02   pass
1000   1000   4      0.033      20.1526  1.029343e-12 3.510325e-02   pass
1000   1000   4      0.033      20.1592  1.029343e-12 3.510325e-02   pass
1000   1000   4      0.033      20.1368  1.029343e-12 3.510325e-02   pass
2000   2000   4      0.277      19.2876  4.298950e-12 3.739560e-02   pass
2000   2000   4      0.275      19.4285  4.298950e-12 3.739560e-02   pass
5000   5008   4      3.235      25.7781  2.581643e-11 3.599893e-02   pass
5000   5008   4      3.219      25.9008  2.581643e-11 3.599893e-02   pass
10000  10000  4      24.330     27.4089  9.603002e-11 3.386116e-02   pass
10000  10000  4      24.457     27.2672  9.603002e-11 3.386116e-02   pass
15000  15000  4      80.958     27.7979  2.042799e-10 3.217442e-02   pass
15000  15000  4      80.941     27.8037  2.042799e-10 3.217442e-02   pass
18000  18008  4      139.266    27.9224  2.894987e-10 3.170367e-02   pass
18000  18008  4      139.108    27.9542  2.894987e-10 3.170367e-02   pass
20000  20016  4      191.221    27.8951  4.097986e-10 3.627616e-02   pass
20000  20016  4      191.229    27.8940  4.097986e-10 3.627616e-02   pass
22000  22008  4      252.595    28.1068  4.548092e-10 3.331299e-02   pass
22000  22008  4      252.600    28.1062  4.548092e-10 3.331299e-02   pass
Performance Summary (GFlops)
Size   LDA    Align.  Average  Maximal
1000   1000   4       19.2957  20.1592
2000   2000   4       19.3581  19.4285
5000   5008   4       25.8395  25.9008
10000  10000  4       27.3381  27.4089
15000  15000  4       27.8008  27.8037
18000  18008  4       27.9383  27.9542
20000  20016  4       27.8946  27.8951
22000  22008  4       28.1065  28.1068
Residual checks PASSED
End of tests
Done: Thu May 23 19:25:57 JST 2013
```

"-cpu host"無しで　13.0GFlops、有りで 28.1GFlops。

だいぶ違いますね。

使っている便利マークソフトが、Intelで最適化されたLinpackなので、最新のCPUの高速演算機能を使い倒せるようになっているのだと思います。

この他、sysbenchのcpuテストや、Unixbenchで比べてみましたが、"-cpu host"有り無しでの性能差はありませんでした。

そうすると、ものによっては、最適化によってCPUの機能(sse4やavx等)が使い倒せれば、速くなるということなのかもしれません。
