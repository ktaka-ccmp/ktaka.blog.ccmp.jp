+++
title = "SSH踏み台サーバを経由して社内サーバにアクセスする"
date = 2021-01-21
path = "2021/01/ssh.html"
+++

最近のリモートワークの状況下で自宅から職場のサーバにアクセスしなければならないことも多いと思います。

VPNを使ったり、OAuth付きのproxyサーバを立てたり、いろいろとやり方があると思います。今回はSSHの踏み台サーバ経由で職場内のWEBサーバにアクセスする方法について、やり方を記録して置こうと思います。

昔から、1. SSHのダイナミックフォワードでトンネルを掘る、2. ブラウザにproxy.pacを読ませて特定の(社内サーバ)URLのみにそのトンネルを使わせる、といった方法は利用していましたが、あるバージョンを境にChromeでproxy.pacファイルを読まなくなってしまい、放置していました。

今回改めてやり方を調べてみたというのが背景です。

トンネル掘り

トンネルにはSSHのダイナミックフォワードを使います。例えば以下のような感じ。

hirakegoma.sh

```
#!/bin/bash

while true; do

echo "Connecting gw.example.com:22 ... "
ssh -4ND 18888 gw.example.com -p 22

sleep 1
echo retrying
done
```

職場内のサーバ、xxx.inside.example.comへのアクセスを上で作ったトンネルを経由させるには、例えば以下のようにすれば良い。

proxy.pac

```
function FindProxyForURL(url, host)

{

if (dnsDomainIs(host, ".inside.example.com"))
        if (isResolvable(host))
                return "DIRECT";
        else
                return "SOCKS5 localhost:18888";
        else

return "DIRECT";

}
```

会社内ではサーバ名前解決ができるであろうから、名前ができないときのみトンネルを通すようになっている。

Chrome起動オプション

Chromeでproxy.pacのありかを指定するには、システムの環境設定でやればいいらしい。残念なことにLinuxの場合にはそういうわけにもいかず、Chrome起動時にオプションを引数として渡してあげる必要がある。

以前は以下のような感じでうまく行っていた。

```
google-chrome %U --proxy-pac-url=file:///home/ktaka/proxy.pac
```

最近は"--proxy-pac-url=f"でファイルを指定しても無視されてしまうようなので、[ワークアラウンド](https://bugs.chromium.org/p/chromium/issues/detail?id=839566#c22)が必要である。

結局行き着いたのが以下のオプション。

```
google-chrome %U --proxy-pac-url='data:application/x-javascript-config;base64,'$(base64 -w0 /home/me/proxy.pac)
```

最近のサーバやワークステーションは、BMCというミニプロセッサが載っていて、Webブラウザー経由で電源のオンオフ、ハードリセット、BIOS設定の変更などができます。

今回のような簡易プロキシを使うことによって、これらの職場内にあるサーバに、外部から簡単にアクセスすることができるようになります。

BMC搭載の高性能なワークステーションはこちらをどうぞ→[AMD Ryzen™ Threadripper™ ECCメモリ IPMI搭載 ワークステーション](https://ccmp.jp/hardware/workstation/373-amd-threadripper.html)
