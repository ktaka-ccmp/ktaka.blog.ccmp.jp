+++
title = "簡易VPN、sshuttleが強力過ぎる"
date = 2013-01-02
path = "2013/07/sshuttle.html"
+++

外出先から社内のWindowsサーバにリモートデスクトップ接続したいのだが、
```
# sshuttle  --dns -r ktaka@fumidai.clustcom.com:22 192.168.20.0/22
Connected.
ktaka@vaiox:~$ rdesktop -r sound:local -f winserver.intra.clustcom.com
```
たったこれだけでOK。
