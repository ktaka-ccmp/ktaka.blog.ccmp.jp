+++
title = "社外からSOCKS5プロキシ経由でRemoteDesktop接続"
date = 2021-01-22
path = "2021/01/socks5remotedesktop.html"
+++

SOCKS5トンネル掘り 

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

xfreerdpのラッパースクリプト

社内(≈名前解決可能)なら直接、そうでないならSOCKS5プロキシ経由でRDP接続する。

rdp.sh

```
#!/bin/bash

case "$1" in
	host1)
	user=user1
	host=host1.inside.example.com
	;;
	host2)
	user=user2
	host=host2.inside.example.com
	;;
	*)
	echo Usage $1 host_nick_name
	exit
esac

if host $host ; then
	echo Connecting $user@$host
	xfreerdp /u:$user /size:1400x900 /v:$host
else
	echo Connecting $user@$host via SOCKS proxy
	xfreerdp /u:$user /size:1400x900 /v:$host /proxy:socks5://localhost:18888
fi
```
