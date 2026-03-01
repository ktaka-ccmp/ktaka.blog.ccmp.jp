+++
title = "Intel 10GBaseT NICのドライバ"
date = 2012-05-14
description = "Intel X540 10GBaseT NICのLinuxドライバixgbeがカーネル2.6.38からサポートされていることの確認メモ。"
path = "2012/05/intel-10gbaset-nic.html"
+++

linuxでは、Intel の10G NIC X540はixgbeでサポートされるようだ。

Device 8086:1528

[http://pci-ids.ucw.cz/read/PC/8086/1528](http://pci-ids.ucw.cz/read/PC/8086/1528)

2.6.38からサポートされている

[http://kernelnewbies.org/Linux_2_6_38-DriversArch](http://kernelnewbies.org/Linux_2_6_38-DriversArch)

drivers/net/ethernet/intel/ixgbe/ixgbe_x540.c

バニラカーネルであれば使えそう。
