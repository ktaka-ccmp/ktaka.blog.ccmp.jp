+++
title = "sshuttle vpnでサーバのリモート管理を便利に"
date = 2013-07-25
path = "2013/07/sshuttle-vpn.html"
+++

データセンタに置かれたサーバに外部からネットワーク経由でアクセスし、電源のON/OFFやBIOS設定、OSインストールなどを行うことができれば、非常に便利です。

最近のサーバには、ネットワーク経由で電源をON/OFFしたり、コーンソール画面を操作するための、IPMI準拠のリモートマネージメント機能が備わっていることが多いので、既に利用されている方も多いと思います。

通常、サーバは、ファイアウォールによりネットワーク的に守られた場所にあるので、踏み台サーバにsshログインして、そこからアクセスしている場合も多いでしょう。

このような場合、リモートマネージメント機能を使うには、オフィスからデータセンタにvpnを張れると便利なのですが、vpnを張るのもなかなか面倒です。

今回、sshuttle([https://github.com/apenwarr/sshuttle](https://github.com/apenwarr/sshuttle))という、sshポートのみの開放でOKな、簡易vpnツールを見つけたので紹介したいと思います。

sshuttleはLinuxとMacOSで利用可能な、簡易vpnです。踏み台サーバにはssh経由でアクセスするので、SSHのDynamic Port forwardingによるSOCKS proxyにプラスアルファしたような働きをします。

プラスアルファの部分は何かというと、あるIPアドレス、あるネットワークアドレスに対しては、クライアントプログラムでは何の設定も無しに透過的にproxyを使うことができるということです。

たとえば、以下のポンチ絵の様に、client、proxy、targetの3台のマシンがあったとします。

>                        |
>
>                        |   sshd:22
>
>  client  proxy  target(192.168.20.153)
>                        |
>                        |

ここで、clientとproxyの間にはファイアウォールがあり、proxyへは22番ポートへのアクセスしか許可されていません。したがって、当然ながらclientからtargetへも直接アクセスできません。

踏み台サーバproxy:22へのsshコネクションを経由してtargetへアクセスできるようにするには次のコマンドのみでOKです。

> vaiox:~# sshuttle  -r ktaka@proxy:22 192.168.20.153
>
> Connected.

これだけで、以下のようにclientとporxy間にトンネルが張られます。

>                        |
>
>      sshuttlesshd:22
>  client  proxy  target(192.168.20.153)
>                        |
>                        |

トンネルを張った後に、clientからtargetに http, https, vncなどでアクセスしようとすると、

sshuttlesshd:22のトンネルを通り、targetにアクセスできるようになります。

>                        |                http, https
>
>    sshuttlesshd:22  ------------------->
>  client  proxy  target(192.168.20.153)
>                        |
>                        |

クライアントマシンで、どうなっているかを見てみると。

- 192.168.20.153宛のパケットはTTL=42以外であれば、全て12300番ポートにリダイレクトしています

> vaiox:~# iptables -L -n -t nat
>
> Chain PREROUTING (policy ACCEPT)
>
> target     prot opt source               destination      
>
> sshuttle-12300  all  --  0.0.0.0/0            0.0.0.0/0        
>
> Chain INPUT (policy ACCEPT)
>
> target     prot opt source               destination      
>
> Chain OUTPUT (policy ACCEPT)
>
> target     prot opt source               destination      
>
> sshuttle-12300  all  --  0.0.0.0/0            0.0.0.0/0        
>
> Chain POSTROUTING (policy ACCEPT)
>
> target     prot opt source               destination      
>
> Chain sshuttle-12300 (2 references)
>
> target     prot opt source               destination      
>
> REDIRECT   tcp  --  0.0.0.0/0            192.168.20.153       TTL match TTL != 42 redir ports 12300
>
> RETURN     tcp  --  0.0.0.0/0            127.0.0.0/8         

- 12300番ポートでは、pyhtonプログラム(sshuttle)が待ち受けています。

> vaiox:~# netstat -lnp|grep 12300
>
> tcp        0      0 127.0.0.1:12300         0.0.0.0:*               LISTEN      5059/python    

これにより192.168.20.153宛のパケットは、ほぼ(TTL=42を除き) sshuttleが張ったコネクションを通るということになるのです。
