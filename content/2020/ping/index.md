+++
title = "pingが通らない時"
date = 2020-11-25
description = "ファイルシステムコピー時にcapabilityが欠落してpingが動作しなくなる問題の原因と、setcapでの復旧方法。"
path = "2020/11/ping.html"
+++

pingができなくなるのは、うっかりファイルシステムをコピーした際にcapabilityを落としてしまったことが原因であることもあるらしい。
rsyncやtarでファイルシステムごとコピーする際は、--xattrsを忘れずに。

pingが通らない。

```
$ ping str
ping: socket: Address family not supported by protocol
$ ping -4 str
ping: socket: Operation not permitted
```

capabilityの確認。何も付いてない。

```
$ sudo getcap /bin/ping
```

capabilityの付与と確認。

```
$ sudo setcap cap_net_raw=ep /bin/ping
$ sudo getcap /bin/ping
/bin/ping = cap_net_raw+ep
```

"cap_net_raw+ep"が付与された。

そしてping通るようになった。

   

```
$ ping str
PING stretch.h.ccmp.jp (192.168.60.3) 56(84) bytes of data.
64 bytes from stretch.h.ccmp.jp (192.168.60.3): icmp_seq=1 ttl=64 time=6.89 ms
64 bytes from stretch.h.ccmp.jp (192.168.60.3): icmp_seq=2 ttl=64 time=3.100 ms
64 bytes from stretch.h.ccmp.jp (192.168.60.3): icmp_seq=3 ttl=64 time=3.53 ms
```

以下ちょっと実験する際などに役立つコマンド達 

capability, xattrの確認コマンド、何もない時

   

```
# getcap /bin/ping
# getfattr -n security.capability /bin/ping
/bin/ping: security.capability: No such attribute
# sudo getfattr -d /bin/ping
# sudo attr -l  /bin/ping
```

capability, xattrの確認コマンド、権限がちゃんと付与されている時

```
# getcap /bin/ping
/bin/ping = cap_net_raw+ep

# attr -l  /bin/ping
Attribute "capability" has a 20 byte value for /bin/ping

# getfattr -n security.capability /bin/ping
getfattr: Removing leading '/' from absolute path names
# file: bin/ping
security.capability=0sAQAAAgAgAAAAAAAAAAAAAAAAAAA=
```

xattrごと削除するコマンド

   

```
# setfattr -x security.capability /bin/ping
```

参考文献

- [https://man7.org/linux/man-pages/man5/attr.5.html](https://man7.org/linux/man-pages/man5/attr.5.html)
- tarの場合 --xattrsを付ける [https://www.gnu.org/software/tar/manual/html_node/Extended-File-Attributes.html](https://www.gnu.org/software/tar/manual/html_node/Extended-File-Attributes.html)
- rsyncの場合も --xattrs, -Xを付ける [https://man7.org/linux/man-pages/man1/rsync.1.html](https://man7.org/linux/man-pages/man1/rsync.1.html)
- [https://wiki.archlinux.org/index.php/capabilities](https://wiki.archlinux.org/index.php/capabilities)
