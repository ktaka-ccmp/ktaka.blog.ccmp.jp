+++
title = "LinuxルーターでのIPv6 IPoE設定"
date = 2020-05-04
description = "フレッツ回線のLinuxルーターでIPv6 IPoE接続を設定し、SLAACやradvdによるLAN側アドレス配布、ip6tablesの設定を行った記録。"
path = "2020/05/linuxipv6-ipoe.html"
+++

こんにちは、コロナの影響でステイホームでリモートワークを励行しています。多くの人たちが業務のために自宅からインターネットにアクセスしたり、外に遊びに行けず自宅でネットコンテンツを長時間視聴するためか、日時を問わずNTTフレッツ回線のネットワークが非常に遅くなっているような気がします。

フレッツ回線の混雑の情報をネットで調べてみると、もともと回線設備の容量が少なめで、主にIPv4のPPPoE接続で利用しているNTTのNGNの網終端装置で回線が混み合っているのではないかということです。

([https://eng-blog.iij.ad.jp/archives/5536](https://eng-blog.iij.ad.jp/archives/5536) [http://enog.jp/wp-content/uploads/2018/08/20180720-ENOG51-Kashiwazaki.pdf](http://enog.jp/wp-content/uploads/2018/08/20180720-ENOG51-Kashiwazaki.pdf))

これを回避するには比較的空いているIPv6の接続口を利用するのが良いとのことでした。NTTのNGNネットワークとインターネットの境界の設備は、NTTの方針に依存せず増強できるとのことです。

そこでIPv6 IPoE + DS-Lite なプロバイダと契約し、もともと自宅で利用していたLinuxルーターをIPv6に対応させました。

今回契約したのはBB.exciteコネクト(IPoE接続プラン)というもので、既存のフレッツ回線に月々700円(税抜)追加でIPv6のインターネット接続を利用できるようになります。

[https://bb.excite.co.jp/norikae/ipoe/](https://bb.excite.co.jp/norikae/ipoe/)

ちなみに、本題から外れますが、我が家のルーターは手のひらサイズのIntelのNUCです。NICが一個しかついていないため、eth0からTag VLANを利用してeth0.10のインターフェースを仮想的に作りWAN側に用いています。eth0とeth0.10を後述のコマンド例で使いますが、前者が内側、後者が外側ということです。

<img src="/2020/05/linuxipv6-ipoe.html/image/2020-05-04-4.jpg" width="320" height="240">

<img src="/2020/05/linuxipv6-ipoe.html/image/2020-05-04-5.jpg" width="320" height="240">

ちなみに、ルーターのOSはDebian Busterをtarで固めたものをUSBメモリに入れ、起動時にtmpfsに展開して、ディスクレスで運用しています。こうすることで、万が一NUCが壊れたとしても適当なパソコンをルーターとしてブートすることが可能です。

<img src="/2020/05/linuxipv6-ipoe.html/image/2020-05-04-3.jpg" width="320" height="240">

### WANインターフェースの設定

IPv6の世界では、Stateless Address Auto-Configuration(SLAAC)という仕組みがあり、基本的に何もしなくてもIPv6アドレスがアサインされます。

Linuxの場合、IPv6関連のコンフィグオプションを有効にしたカーネルがあり、かつicmpv6のパケットを送受信できる環境であれば、いつの間にか勝手にIPv6アドレスが付与されます。

今回契約したのBB.exciteコネクト(IPoE接続プラン)は、transixというVirtual Network Enabler(VNE)が実際の通信サービスを提供しており、transixから払い出された/64のプリフィックスがアドバタイズ(Router Advertisement (RA))され、それを受信したLinuxカーネルが、自動的にネットワーク設定を行います。

RAの内容はこのような感じになっています。

```
# /bin/rdisc6 -1 -r 3 eth0.10
Soliciting ff02::2 (ff02::2) on eth0.10...

Hop limit : 64 ( 0x40)
Stateful address conf. : No
Stateful other conf. : Yes
Mobile home agent : No
Router preference : medium
Neighbor discovery proxy : No
Router lifetime : 1800 (0x00000708) seconds
Reachable time : 300000 (0x000493e0) milliseconds
Retransmit time : 10000 (0x00002710) milliseconds
Source link-layer address: 00:yy:yy:yy:53:C3
MTU : 1500 bytes (valid)
Prefix : 2409:x:x:x::/64
On-link : Yes
Autonomous address conf.: Yes
Valid time : 2592000 (0x00278d00) seconds
Pref. time : 604800 (0x00093a80) seconds
from fe80::y:y:y:53c3
```

(参考: [https://hirose31.hatenablog.jp/entry/20060418/1145354566](https://hirose31.hatenablog.jp/entry/20060418/1145354566) )

上記のRAに基づいて自動的に設定されたIPアドレスの様子。

```
eth0.10@eth0:  mtu 1500 qdisc noqueue state UP group default qlen 1000
    link/ether c0:3f:d5:69:6f:b0 brd ff:ff:ff:ff:ff:ff
    inet6 2409:x:x:x:y:y:y:6fb0/64 scope global dynamic mngtmpaddr
```

同時に登録されるルーティング情報。

```
2409:x:x:x::/64 dev eth0.10 proto kernel metric 256 pref medium
default via fe80::y:y:y:53c3 dev eth0.10 proto ra metric 1024 expires 1784sec hoplimit 64 pref medium
```

SLAACによりアサインされるアドレスは、transixから払い出されたプリフィックス (2409:x:x:x::/64)とNICのMACアドレスを組み合わせたものです。

このようなIPv6アドレスを用いるとMACアドレスが一意であるため、これを用いてユーザーの行動が追跡される可能性があるなどプライバシーの上の問題があります。

この問題に対処するためにPrivacy Extensionという仕様が公開されており、これを用いると払い出されたプリフィックスとランダムな数字を組み合わせたIPv6アドレスを利用することができます。

つまりPrivacy Extensionを有効にするとMACアドレス由来でないアドレスもインターフェースにアサインすることができるのです。Linuxの場合はuse_tempaddrというパラメータを利用します。

[https://www.tldp.org/HOWTO/Linux+IPv6-HOWTO/ch06s05.html](https://www.tldp.org/HOWTO/Linux+IPv6-HOWTO/ch06s05.html)

[https://www.kernel.org/doc/Documentation/networking/ip-sysctl.txt](https://www.kernel.org/doc/Documentation/networking/ip-sysctl.txt)

```
use_tempaddr - INTEGER
 Preference for Privacy Extensions (RFC3041).
     1 : enable Privacy Extensions and prefer temporary
          addresses over public addresses.
 Default:  0 (for most devices)
   -1 (for point-to-point devices and loopback devices)
```

実際にパラメータを設定してみると、

```
echo 2 > /proc/sys/net/ipv6/conf/eth0.10/use_tempaddr
```

Temporaryなアドレスもアサインされます。

```
    inet6 2409:x:x:x:y:y:y:d384/64 scope global temporary dynamic
       valid_lft 569580sec preferred_lft 50999sec
```

(追記：最近ではSemantically Opaque Interface Identifiersと呼ばれる、よりプライバシーに考慮したアドレスアサイン方式があるようなのでそれにも[対応しました](/2020/05/linuxslaac-ipv6.html)。)

### LANインターフェースの設定

次にLAN側のネットワークをどうするか考えます。まず思いつくのは以下の3通りの方法です。

- WANインターフェースとLANインターフェースをブリッジ接続し、WANから流れてきたRAをLANにそのまま流す。

- WAN側で受け取ったグローバルなプリフィックスを、radvdというプログラムでLANに再広報する。

- WAN側とは別のプライベートなIPv6アドレス(ユニークローカルアドレス)のプリフィックスをradvdでLANに広報する。

ある程度の試行錯誤の末、上記のうち3の方法を採用することにしました。

まず1の構成では、IPv6に関してはL3レベルでネットワークが分離されていないため、やはりセキュリティ設定に不安があります。まあ要するにLAN内に自分の知らないicmpv6のパケットが入ってくること自体が気持ち悪くて受け入れられないということです。

2の構成に関しては、以下に示すような技術課題があり、とりあえず設定はできるのですが、上手いルーティング設定とSLAAC自動設定が両立できません。 

- WANとLANで同じプリフィックスを利用すると、ゲートウェイ上でのルーティング設定がめんどう。

- /64を/65に分割してつかうとSLAACが機能しない。

WANで受け取ったプリフィックスを利用しLAN側のeth0にアドレスをアサインすると、ルーティングテーブルが以下のようになります。

```
2409:x:x:x::/64 dev eth0.10 proto kernel metric 256 expires 2591991sec pref medium
2409:x:x:x::/64 dev eth0 proto kernel metric 256 pref medium
```

この場合の問題点は、2409:x:x:x::/64宛のパケットに対するルーティング設定が2行あり、eth0側にパケットを流したくても先にあるeth0.10側にパケットが流れてしまい、通信がうまくいきません。

2409:x:x:x::/64向けのパケットはeth0側に流したいので、1行目を削除すれば良いのですが、この1行目の設定は、WAN側のSLAACの自動設定により自動追加されるものなので、しばらくするとまた追加されてしまいます。

この問題を回避するために2409:x:x:x::/64で許されるアドレスレンジの内半分の2409:x:x:x:8000::/65を、LAN内プリフィックスとして利用することを試みました。ルーティングルールでは長いプリフィックスの方が優先されるので、2409:x:x:x:8000::/65宛のパケットを必ずeth0に流すことができるというもくろみです。

この方法でルーティング自体はうまくいくのですが、SLAACによる自動アドレス設定はプリフィックスが64であることが前提であるため、各マシンに手動でIPv6アドレスを設定する必要が出てきます。

つまり、IPoEで配布されるグローバルプリフィックスが/64である場合、ルーティングをきれいに動かすためにLANのプリフィックスをそれより長くすると、SLAACによるLAN内の自動アドレス設定ができなくなってしまいます。

(ひかり電話契約がある場合には/56のプレフィックスが配布されるらしいが、我が家はひかり電話では無いので/64で。。。みんな/56とか、せめて/63で配布してくれれば良いのに。)

結局、このような理由から、「2. WAN側で受け取ったグローバルなプリフィックスを、radvdというプログラムでLANに再広報する。」という方法は断念しました。

### LAN側はプライベートなアドレスを利用

仕方が無いので、LAN内ではユニークローカルアドレスfd00::/8を利用する第３の方法を用いることにしました。具体的にはradvdでfd00:0:0:x::/64なプリフィックスを配布します。そうするとLAN内の様々なクライアントがSLAACにより自動的にアドレスを生成し、IPv6により通信できるようになります。

/etc/radvd.confの例

```
interface eth0
{
        AdvSendAdvert on;
        MinRtrAdvInterval 30;
        MaxRtrAdvInterval 100;
        prefix fd00:0:0:x::/64
        {
                AdvOnLink on;
                AdvAutonomous on;
                AdvRouterAddr off;
        };
        RDNSS fd00:0:0:x::1
        {
        };
};
```

この構成だとLAN内はグローバルIPではなく、外に出る際にMASQUERADEすることが必要になります。NATが必要無いというIPv6のメリットの一つを損なってしまいますが仕方が無いです。

考えようによっては、IPv4で慣れ親しんだ構成でもあるので、管理は難しく無いというメリットもあります。

外部からのL3フィルタリング設定も、慣れ親しんだiptableと同様に行うことができます。

ip6tables設定。

/etc/ip6t.save (使用例 /sbin/ip6tables-restore < /etc/ip6t.save)

```
*nat
:PREROUTING ACCEPT [0:0]
:INPUT ACCEPT [0:0]
:POSTROUTING ACCEPT [0:0]
:OUTPUT ACCEPT [0:0]
-A POSTROUTING -o eth0.10 -j MASQUERADE  # <- マスカレード設定
COMMIT
*filter
:INPUT DROP [0:0]
:FORWARD DROP [0:0]
:OUTPUT ACCEPT [0:0]
-A INPUT -i lo -j ACCEPT
-A INPUT -m state --state RELATED,ESTABLISHED -j ACCEPT
-A INPUT -s fd00:0:0:x::/64 -i eth0 -j ACCEPT
-A INPUT -p udp --dport 53 -j ACCEPT
-A INPUT -p tcp --dport 53 -j ACCEPT
-A INPUT -p ipv6-icmp -j ACCEPT
-A FORWARD -d fd00:0:0:x::/64 -j ACCEPT
-A FORWARD -s fd00:0:0:x::/64 -i eth0 -o eth0.10 -j ACCEPT
-A FORWARD -m state --state RELATED,ESTABLISHED -j ACCEPT
COMMIT
```

### 外部からのアクセス

SLAACにより設定されるアドレスは、NICのMACアドレスから生成されるため決して覚えやすいものではありません。"プリフィックス::1"という分かり易いアドレスをマニュアルアサインすることで、外部からのアクセスが僅かながら容易になります。

```
/sbin/ip add add 2409:x:x:x::1/64  dev eth0.10
```

ただしtransixから払い出されるプリフィックスは固定であるという約束はありません。プリフックス変わった場合にはそれを検知してマニュアルアサインしたアドレスも付け直し、そしてDNSなどを更新する必要があるでしょう(これについてはいまのところ未実装です) 。

固定のプリフィックスを払い出してくれるISPがあったら乗り換えたいです。

###

###

### IPv4をどうするか

IPv4に関してはPPPoE接続の固定IPの契約が元々あるので、そのまま利用することにしました。

今回契約した、DS-Liteのサービスでは、IPv4 NATとIPIPトンネリングを利用したIPv4 over IPv6接続が利用できます。PPPoE接続をやめてこちらの経路を利用することでIPv4回線も空いている方を利用できることになりますが、グローバルなIPv4アドレスを他のユーザと共用する必要があるため、いまのところそれほど魅力を感じていません。

transixも固定IPのサービスがあるのでそれが利用可能かつ安価なISPがあれば考えたいです。([https://www.mfeed.ad.jp/transix/staticip/](https://www.mfeed.ad.jp/transix/staticip/))

(追記：後日、ポリシールーティングを使ってHTTP、HTTPSの通信のみDS-Liteを使うようにしました。→[こちら](/2020/05/linuxds-lite.html))

別のVNEである、JPNEからも同様な、v6オプション固定IPサービスがあるようなので、こちらも安価なISPがあれば考えたいです。([https://www.jpne.co.jp/service/v6plus-static/](https://www.jpne.co.jp/service/v6plus-static/))

### その他の注意点

Linuxボックスでipv6のフォワーディングを有効にするとルーティング情報が消えてしまい、これに悩まされました。

forwarding=1でもRouter Advertisement（RA）を受信できるようにするために、以下が必要です。

```
echo 1 > /proc/sys/net/ipv6/conf/all/forwarding
echo 2 > /proc/sys/net/ipv6/conf/eth0.10/accept_ra
```

( [http://strugglers.net/~andy/blog/2011/09/04/linux-ipv6-router-advertisements-and-forwarding/](http://strugglers.net/~andy/blog/2011/09/04/linux-ipv6-router-advertisements-and-forwarding/) )

### まとめ

IPv6 IPoE + DS-Lite なプロバイダと契約し、LinuxルーターのIPv6設定を行いました。WAN側アドレスはSLAACにより自動的に設定されるものを用いました。LAN側アドレスはユニークローカルアドレスを利用し、MASQUERADEとフィルタリングの設定を行いました。

今後の課題としては、(1)64より短いプリフィックスが得られるなら、LAN内もグローバルアドレスを利用したい、(2)LinuxのルーティングがSLAACと両立できるようになったら、LAN内もグローバルアドレスを利用したい、(３)固定プリフィックスが利用できるISPがあれば乗り換えたい、(4)固定グローバルIPのIPv4 over IPv6が利用可能かつ安価なISPがあれば乗り換えたい、などがあります。
