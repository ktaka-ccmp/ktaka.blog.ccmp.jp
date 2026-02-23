+++
title = "LinuxルーターでのDS-Lite設定"
date = 2020-05-05
path = "2020/05/linuxds-lite.html"
+++

昨日に引き続き、自宅のLinuxルーター上でDS-Liteの設定を行いました。

BB.exciteコネクト(IPoE接続プラン)ではIPv6回線のトンネルを通して、インターネットにIPv4接続することが可能です。

実際のサービスはtransixのDS-Liteを使うことになるのですが、この回線を使うことで混み合っているNGNの網終端を通らずに済むことになるので、快適なネットライフが待っているらしいのです。

ところが我が家ではすでにPPPoEでのIPv4の固定IP契約があり、その固定IPをVPN、DNSサーバなどいろいろなサービスに使っていて、別のIPアドレスに変わってしまって困ります。またDS-Liteの場合にはグローバルIPアドレスを複数のユーザーで共有して使うので、なおさら外部からのアクセスなどには使うことができません。
そういった理由で、IPv4に関しては既存のPPPoEのままにするつもりでいました。

しかしながらWebページの閲覧やYutubeコンテンツの視聴に使われるHTTPやHTTPSに限れば固定IPは不要です。また、Linuxルーターの場合には、宛先のIPやプロトコル、ポート番号に応じてきめ細かく接続先の経路を選ぶことができます。そこで、せっかくなので今回、HTTPとHTTPSに限って、DS-Liteの経路を利用する設定を試してみました。

IPv4 over IPv6のトンネルセットアップ

```
ip -6 tunnel add dslite mode ip4ip6 \
         remote 2404:8e00::feed:100 local 2409:x:x:x::1  dev eth0.10
ip link set dev dslite up
```

宛先が192.168.0.0/16以外(宛先がWAN向き)で、宛先ポート80、443のパケットにマークをつける。

```
iptables -A PREROUTING -i eth0 -t mangle \
       ! -d 192.168.0.0/16 -p tcp --dport 443 -j MARK --set-mark 1
iptables -A PREROUTING -i eth0 -t mangle \
       ! -d 192.168.0.0/16 -p tcp --dport 80 -j MARK --set-mark 1
```

マークがついているパケットだけDS-Liteのトンネルを通るようにする。

```
ip route add default dev dslite table 100
ip rule add from all fwmark 1 table 100 prio 100
```

これで自宅LAN内の任意のマシンからDS-Lite回線をHTTP、HTTPS接続できるようになりました。

経路が変わっているかどうかは、WEB上にあるアクセス元IPを判別するページ(例えば[ここ](https://www.cman.jp/network/support/go_access.cgi))などで確認可能で、ちゃんと切り替わっていることが確認できました。

いままで回線の遅さに悩んでいましたが、これで解決されるのか楽しみです。
