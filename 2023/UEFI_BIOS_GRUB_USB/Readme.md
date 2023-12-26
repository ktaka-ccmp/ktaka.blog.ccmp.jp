目次
=================

   * [要旨](#要旨)
   * [はじめに](#はじめに)
   * [やり方](#やり方)
   * [実際にブートできるのか](#実際にブートできるのか)
   * [まとめ](#まとめ)

## 要旨
  UEFIモードとBIOSモードのどちらでもGRUBを起動可能なUSBメモリの作成を試みた。
  どちらの場合でもGRUBの起動が可能であるはずのUSBメモリを作成した。
  SupermicroワークステーションとIntel NUCで実機検証したところ、Supermicroのワークステーションでは、どちらのモードでもブート可能であったが、Intel NUCはそうではなかった。
  ハードウェアによってはBIOSブート時にパーティションにbootable(active)フラグが必要であるものがあり、その場合は、UEFIブートと両立できないことがわかった。

## はじめに
  
  USBメモリからLinuxが起動できると便利である。サーバのメンテナンスや新規OSインストールなどの様々な場面で、ディスクレスなLinuxをUSBメモリから起動し役立てることができる。私の場合、自宅や会社のルータとして、USBから起動したDebian Linuxを利用している。ファイルシステムをメモリ(tmpfs)上に展開しディスクレスで運用しているので、なにか設定をしくじった場合にも再起動すればもとの状態に戻すことができるし、ハードウェアが故障してしまった場合などは別のマシンにUSBメモリを差し替えれば簡単に復旧できるので大変重宝している。
  
  Linuxを起動するにはGRUBというブートローダを利用することが多い。GRUBはLinuxカーネルのロードが可能なだけでなく、Windowsのチェインロードも可能である。
  かつてのPCは、BIOSというファームウェアがドライブの先頭にあるGRUBをロードしていたが、最近のPCではUEFIがESPにあるGRUBをロードするように仕様に変わった。
  BIOSとUEFIではブート仕様が異なるので、GRUBのインストールの方式も異なっていて、一方の方式でLinux及びGRUBインストールしたドライブをもう一方の方式のPCで利用することができない。通常は、HDDやSSD等の起動ドライブをPC間で移動することはあまりないのでそれぞれのPCにそれぞれ適した方式でインストールすれば問題ない。
 
  しかしメンテナンス用のUSBメモリは、できれば、古いBIOS方式でも新しいUEFI方式でも、どちらでも使えるようにしておきたい。
  そこで、今回、UEFIモードでもBIOSモードでも、GRUBを起動することができるUSBメモリの作成を試みた。

## やり方

LinuxパソコンにUSBメモリを挿したとき、/dev/sdaとして認識されているとし、そこにパーティションテーブルを作成しGRUBのインストールを行う。
以下の手順は、ストレージのパーティションを操作するので、/dev/sdaが確かに操作しようとしているUSBメモリなのかをよく確認してから行う必要がある。

### パーティション初期化と作成
  
  Linuxのルートパーティション、ESPパーティション、BIOSブートパーティションを作成する。ESPパーティションは先頭から512Mbyte、Linuxルートパーティションは残り全部を割り当てる。最近のパーティションツールは、先頭の先頭に2047セクタ分の空きを残すようなので、そこにBIOSブートパーティションを作成する。
  
```
TOP_DIR=./
dev=/dev/sda

# Clear partition table
sgdisk -Z $dev

# Create ESP partition
sgdisk -n 2::+512M  $dev
sgdisk -t 2:ef00 $dev

# Create Linux partition
sgdisk -n 1:: $dev

# Create BIOS boot partition
sgdisk -a 1 -n 3:34:2047 $dev
sgdisk -t 3:ef02 $dev

# Change the GPT name of each partition
sgdisk -c 1:Linux -c 2:ESP -c 3:BIOS $dev 

# Show current status
sgdisk -p $dev
```

LinuxルートパーティションとESPパーティションをフォーマットし、ファイルシステムにマウント。
```
# Format ESP and Linux partition
mkfs.fat -F32 -n ESP ${dev}2 
mkfs.ext4 -F -L usbdebian ${dev}1

# Create mount point and mount file systems
mkdir -p ${TOP_DIR}/mnt
mount -L usbdebian ${TOP_DIR}/mnt
mkdir -p ${TOP_DIR}/mnt/boot/efi
mount -L ESP ${TOP_DIR}/mnt/boot/efi
```

BIOS用GRUBのインストール。MBR（ディスクの先頭512Byte）とBIOSブートパーティションにgrubをインストール。
```
# BIOS setup
grub-install --target=i386-pc --boot-directory=./mnt/boot/ $dev
```

動作確認用のGRUBメニューの設定ファイルを作成。今回はLinuxカーネルは入れず、このメニューが表示できるところまでがゴールなので、仮のもので良い。
```
# Create minimum grub.cfg for testing
cat << \EOF > ${TOP_DIR}/mnt/boot/grub/grub.cfg
set default=1
set timeout=5
menuentry "Debian Linux" {
linux /boot/vmlinuz
}
EOF
```

UEFIモードでブートするには、UEFI設定にブートするバイナリとその優先順位を登録することが一般的であるが、USBメモリの場合リームーバブルメディアであるので適さない。
UEFIブートではUEFI設定で他に指定がない場合、EFI/boot/bootx64.efiにフォールバックするので、grubx64.efiをその名前で置いておけば良い。grubx64.efiは同じディレクトリのgrub.cfgを参照するので、そこに/boot/grub/grub.cfgを更に参照するように書いておく。
 
UEFIモードの場合にはセキュアブートも可能である。その場合には、shimx64.efi -> grubx64.efi -> grub.cfgの順で読み込ませたいので、shimx64.efiをEFI/boot/bootx64.efiとして置き、同じディレクトリに、grubx64.efiとgrub.cfgを置けば良い。この時、shimx64.efiとgrubx64.efiは署名済みのものを用いる必要がある。

```
# UEFI boot setup
mkdir -p ${TOP_DIR}/mnt/boot/efi/EFI/boot

cp /usr/lib/grub/x86_64-efi/monolithic/grubx64.efi ${TOP_DIR}/mnt/boot/efi/EFI/boot/bootx64.efi

cat << \EOF > ${TOP_DIR}/mnt/boot/efi/EFI/boot/grub.cfg
search.fs_label usbdebian root
set prefix=($root)'/boot/grub'
configfile $prefix/grub.cfg
EOF

# Unmount filesystem
umount ${TOP_DIR}/mnt/boot/efi/ && umount ${TOP_DIR}/mnt/
```
  
作成したUSBメモリのパーティション構成
```
root@dyna:~# sgdisk -p /dev/sda
Disk /dev/sda: 60088320 sectors, 28.7 GiB
Model: Ultra Fit       
Sector size (logical/physical): 512/512 bytes
Disk identifier (GUID): 21780B2C-8682-42A0-9564-D7E7D726A7EC
Partition table holds up to 128 entries
Main partition table begins at sector 2 and ends at sector 33
First usable sector is 34, last usable sector is 60088286
Partitions will be aligned on 2-sector boundaries
Total free space is 0 sectors (0 bytes)

Number  Start (sector)    End (sector)  Size       Code  Name
   1         1050624        60088286   28.2 GiB    8300  Linux
   2            2048         1050623   512.0 MiB   EF00  ESP
   3              34            2047   1007.0 KiB  EF02  BIOS
```

作成したUSBメモリのファイルシステム確認（unmout前に確認）
```
root@dyna:~# tree -L 3 ${TOP_DIR}/mnt/
mnt/
├── boot
│   ├── efi
│   │   └── EFI
│   └── grub
│       ├── fonts
│       ├── grub.cfg
│       ├── grubenv
│       ├── i386-pc
│       └── locale
└── lost+found

8 directories, 2 files

root@dyna:~# tree ${TOP_DIR}/mnt/boot/efi/
mnt/boot/efi/
└── EFI
    └── boot
        ├── bootx64.efi
        └── grub.cfg

2 directories, 2 files
```
  
以上でGRUBまで立ち上がるUSBは完成である。

## 実際にブートできるのか
  
  作成したUSBメモリで実際にブート可能であるかを、SupermicroのワークステーションとIntel NUCで試してみた。
  Supermicroのワークステーションでは、UEFIブートであってもBIOSブートであっても、GRUBメーニュー画面が表示できた。
  Intel NUCの場合は、UEFIモードでは無事にGRUBのメニューが表示されたが、BIOSモードでのブートができなかった。
  
  Intel NUCの場合には、BIOSモードでブートする場合、次の手順でPMBRのパーティションテーブルでbootable(active)フラグを立ててやる必要があった。
```
root@dyna:~# sfdisk -A  /dev/sda 1
Activation is unsupported for GPT -- entering nested PMBR.
The bootable flag on partition 1 is enabled now.

The partition table has been altered.
Syncing disks.

root@dyna:~# sgdisk -O  /dev/sda 
Disk size is 60088320 sectors (28.7 GiB)
MBR disk identifier: 0x00000000
MBR partitions:

Number  Boot  Start Sector   End Sector   Status      Code
   1      *              1     60088319   primary     0xEE  
```

  PMBRのパーティションテーブルでbootable(active)フラグを立てた場合、今度はUEFIブートができなくなってしまった。どうやらUEFIブートのUEFIブートの規格でPMBR上でそのフラグを立てることを明確に禁止しているらしい。
  再度、UEFIブートするには、以下のように、bootable(active)フラグを戻す必要がある。
  
```
root@dyna:~# sfdisk -A /dev/sda -
Activation is unsupported for GPT -- entering nested PMBR.
The bootable flag on partition 1 is disabled now.

The partition table has been altered.
Syncing disks.  
```
古いハードウェアには、bootable(active)フラグが立っているパーティションが無いとBIOSブートできないものがあり、どうやらIntel NUCはそのようなハードウェアのひとつであるようだ。

参考
 * https://wiki.archlinux.org/title/Partitioning#Tricking_old_BIOS_into_booting_from_GPT (このやり方はうまく行かなかった)
 * https://unix.stackexchange.com/a/325899

## まとめ
  
   今回、UEFIモードでもBIOSモードでも、GRUBを起動することができるUSBメモリの作成を試みた。
  作成したUSBメモリでGRUB画面の表示までたどり着けるか試してみた。
  Supermicroのワークステーションでは、BIOSブート、UEFIブートのどちらでもGRUB画面にたどり着くことができたが、Intel NUCではPMBR上でbootable(active)フラグの切り替えが必要であった、

  UEFIブートの規格でPMBR上でそのフラグを立てることを明確に禁止しているらしい。
  しかし古いハードウェアにはBIOSブート時に、bootable(active)フラグが立っているパーティションが必要であるものがあることが確認された。
  その場合には、ブートモードに応じて作成したUSBメモリのbootable(active)フラグを切り替えることがどうしても必要になってしまうことがわかった。
