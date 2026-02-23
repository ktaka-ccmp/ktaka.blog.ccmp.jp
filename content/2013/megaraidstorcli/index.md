+++
title = "MegaRAIDのStorCLIを試してみました。"
date = 2013-05-22
path = "2013/05/megaraidstorcli.html"
+++

みなさんこんにちは！

今日も相変わらず良い天気ですね。そろそろ、長袖のシャツでは暑く感じることも多くなってきました。

さて、本日は、LSIのRAIDカードの管理ユーティリティーツール、StorCLIについて、ご紹介したいと思います。

皆さんは、RAIDカードの管理ユーティリティーと言ったら、何を思い浮かべますか？

多くの方は、綺麗なGUIツールでRAIDのアレイ削除を行ったり、Webブラウザーを使って管理することを思い浮かべるかもしれません。

今回ご紹介するのは、そういうものではなくて、sshログインしたサーバ上でコマンドラインでRAIDの設定を行う、ソフトウェアです。

古くは、3wareのtw_cliであったり、Adaptecのarcconf、LSIのmegacliをご存知の方にとっては、お馴染みかもしれません。

私個人的には、tw_cliは使いこなしており、その後、arcconfなども使っておりましたが、LSIのmegacliはあまり使いやすいとは感じておりませんでした。

つい最近、LSIのサイトでドライバなどを探していた時に、たまたま、StorCLIという比較的新しいツールがリリースされていましたので、試しに使ってみました。

インストールは以下の通り

```
# wget http://www.lsi.com/downloads/Public/MegaRAID%20Common%20Files/1.03.11_StorCLI.zip
# unzip 1.03.11_StorCLI.zip
# cd StorCli_All_OS/Linux/
# alien  -t storcli-1.03.11-1.noarch.rpm
# tar tvf storcli-1.03.11.tgz
drwxr-xr-x root/root         0 2013-05-23 01:57 ./
drwxr-xr-x root/root         0 2013-05-23 01:57 ./opt/
drwxr-xr-x root/root         0 2013-05-23 01:57 ./opt/MegaRAID/
drwxr-xr-x root/root         0 2013-05-23 01:57 ./opt/MegaRAID/storcli/
-rwxr-xr-x root/root   4956856 2013-01-30 19:25 ./opt/MegaRAID/storcli/storcli64
-rwxr-xr-x root/root   4907676 2013-01-30 19:25 ./opt/MegaRAID/storcli/storcli
# tar  xf storcli-1.03.11.tgz  -C /
# tree /opt/
/opt/
`-- MegaRAID
    `-- storcli
        |-- storcli
        `-- storcli64
2 directories, 2 files
```

storcli64が64bit Linux用のバイナリです。早速、コマンドを叩いてみると、

```
# /opt/MegaRAID/storcli/storcli64
     Storage Command Line Tool  Ver 1.03.11 Jan 30, 2013
     (c)Copyright 2012, LSI Corporation, All Rights Reserved.

help - lists all the commands with their usage. E.g. storcli help
help - gives details about a particular command. E.g. storcli add help
List of commands:
Commands   Description
-------------------------------------------------------------------
add        Adds/creates a new element to controller like VD,Spare..etc
delete     Deletes an element like VD,Spare
show       Displays information about an element
set        Set a particular value to a property
start      Start background operation
stop       Stop background operation
pause      Pause background operation
resume     Resume background operation
download   Downloads file to given device
expand     expands size of given drive
insert     inserts new drive for missing
transform  downgrades the controller
/cx        Controller specific commands
/ex        Enclosure specific commands
/sx        Slot/PD specific commands
/vx        Virtual drive specific commands
/dx        Disk group specific commands
/fx        Foreign configuration specific commands
/px        Phy specific commands
/bbu       Battery Backup Unit related commands
Other aliases : cachecade, freespace, sysinfo
Use a combination of commands to filter the output of help further.
E.g. 'storcli cx show help' displays all the show operations on cx.
Use verbose for detailed description E.g. 'storcli add  verbose help'
Use 'page=[x]' as the last option in all the commands to set the page break.
X=lines per page. E.g. 'storcli help page=10'

Command options must be entered in the same order as displayed in the help of
the respective commands.
```

新しいCLIツールと聞いて薄々感づいていましたが、どうやら、tw_cliと構文がそっくりです。

3wareは、2009年にLSIに買収されたのですが、使い易いと評判だった3wareのCLIの良い部分を、既存のMegaraidのプロダクトラインでも使えるようにしたのでしょう。

コントローラの情報を表示してみます。

```
# /opt/MegaRAID/storcli/storcli64 show
Status Code = 0
Status = Success
Description = None
Number of Controllers = 1
Host Name = 151
Operating System  = Linux3.8.8-64kvmh01
System Overview :
===============
----------------------------------------------------------------
Ctl Model   Ports PDs DGs DNOpt VDs VNOpt BBU  sPR DS  EHS ASOs
----------------------------------------------------------------
  0 9266-8i     8   6   0     0   0     0 Msng On  1&2 Y      2
----------------------------------------------------------------
Ctl=Controller Index|DGs=Drive groups|VDs=Virtual drives|Fld=Failed
PDs=Physical drives|DNOpt=DG NotOptimal|VNOpt=VD NotOptimal|Opt=Optimal
Msng=Missing|Dgd=Degraded|NdAtn=Need Attention|Unkwn=Unknown
sPR=Scheduled Patrol Read|DS=DimmerSwitch|EHS=Emergency Hot Spare
Y=Yes|N=No|ASOs=Advanced Software Options|BBU=Battery backup unit
```

コントローラ0番が9266-8i であることがわかりますね。ポート数は8で、現在接続されているドライブは6本、BBUはMissing　…　あってます。

下の方に書いてある、説明が地味に便利ですね。

コントローラ0番の情報を、さらに詳しく見てみましょう。

```
# /opt/MegaRAID/storcli/storcli64 /c0 show
Controller = 0
Status = Success
Description = None
Product Name = LSI MegaRAID SAS 9266-8i
Serial Number = SV22625074
SAS Address =  500605b0050719c0
Mfg. Date = 07/03/12
System Time = 05/23/2013 02:16:39
Controller Time = 05/22/2013 17:16:38
FW Package Build = 23.9.0-0018
BIOS Version = 5.38.00_4.12.05.00_0x05180000
FW Version = 3.220.35-1998
Driver Name = megaraid_sas
Driver Version = 06.504.01.00-rc1
Controller Bus Type = N/A
PCI Slot = N/A
PCI Bus Number = 6
PCI Device Number = 0
PCI Function Number = 0
Physical Drives = 6
PD LIST :
=======
----------------------------------------------------------------------------
EID:Slt DID State DG       Size Intf Med SED PI SeSz Model               Sp
----------------------------------------------------------------------------
252:0    39 JBOD  -  223.062 GB SATA SSD N   N  512B INTEL SSDSC2CW240A3 U
252:1     8 JBOD  -  223.062 GB SATA SSD N   N  512B INTEL SSDSC2CW240A3 U
252:2    38 UGood -  223.062 GB SATA SSD N   N  512B INTEL SSDSC2CW240A3 U
252:3     9 UGood -  223.062 GB SATA SSD N   N  512B INTEL SSDSC2CW240A3 U
252:4    37 UGood -  223.062 GB SATA SSD N   N  512B INTEL SSDSC2CW240A3 U
252:5    11 UGood -  223.062 GB SATA SSD N   N  512B INTEL SSDSC2CW240A3 U
----------------------------------------------------------------------------
EID-Enclosure Device ID|Slt-Slot No.|DID-Device ID|DG-DriveGroup
DHS-Dedicated Hot Spare|UGood-Unconfigured Good|GHS-Global Hotspare
UBad-Unconfigured Bad|Onln-Online|Offln-Offline|Intf-Interface
Med-Media Type|SED-Self Encryptive Drive|PI-Protection Info
SeSz-Sector Size|Sp-Spun|U-Up|D-Down|T-Transition|F-Foreign
```

ああ、良いですね、いろんな情報とれてます。文法は、tw_cliそのまんまですね。

せっかくですので、RAIDのアレイを作ってみましょう…まずは、ヘルプを…

```
# /opt/MegaRAID/storcli/storcli64 add help
     Storage Command Line Tool  Ver 1.03.11 Jan 30, 2013

     (c)Copyright 2012, LSI Corporation, All Rights Reserved.

storcli /cx add vd type=raid[0|1|5|6|00|10|50|60]
 [Size=,,..|all] [name=,..]
 drives=e:s|e:s-x|e:s-x,y,e:s-x,y,z [PDperArray=x][SED]
 [pdcache=on|off|default][pi][DimmerSwitch(ds)=default|automatic(auto)|
 none|maximum(max)|MaximumWithoutCaching(maxnocache)][wt|wb][nora|ra]
 [direct|cached] [CachedBadBBU|NoCachedBadBBU] [cachevd]
 [Strip=] [AfterVd=X]
 [Spares = [e:]s|[e:]s-x|[e:]s-x,y] [force]
storcli /cx add vd each type=raid0 [name=,..] [drives=e:s|e:s-x|e:s-x,y]
 [SED] [pdcache=on|off|default][pi] [DimmerSwitch(ds)=default|automatic(auto)|
 none|maximum(max)|MaximumWithoutCaching(maxnocache)] [wt|wb] [nora|ra]
 [direct|cached] [CachedBadBBU|NoCachedBadBBU]
 [Strip=]
storcli /cx add vd cachecade Type = raid[0,1,10] drives = [e:]s|[e:]s-x|
 [e:]s-x,y [WT| WB] [assignvds = 0,1,2]
storcli /cx[/ex]/sx add hotsparedrive [DGs=] [enclaffinity] [nonrevertible]
```

  なるほど…　スロット2，3，4のドライブを使って、RAID5のアレイ=バーチャルドライブを作ってみます。

```
# /opt/MegaRAID/storcli/storcli64 /c0 add vd type=raid5  drives=252:2,252:3,252:4
Controller = 0
Status = Success
Description = Add VD Succeeded
```

うまくいったみたいなので、確認します。

```
# /opt/MegaRAID/storcli/storcli64 /c0 show
Controller = 0
Status = Success
Description = None
Product Name = LSI MegaRAID SAS 9266-8i
Serial Number = SV22625074
SAS Address =  500605b0050719c0
Mfg. Date = 07/03/12
System Time = 05/23/2013 02:36:32
Controller Time = 05/22/2013 17:36:30
FW Package Build = 23.9.0-0018
BIOS Version = 5.38.00_4.12.05.00_0x05180000
FW Version = 3.220.35-1998
Driver Name = megaraid_sas
Driver Version = 06.504.01.00-rc1
Controller Bus Type = N/A
PCI Slot = N/A
PCI Bus Number = 6
PCI Device Number = 0
PCI Function Number = 0
Drive Groups = 1
TOPOLOGY :
========
--------------------------------------------------------------------------
DG Arr Row EID:Slot DID Type  State BT       Size PDC  PI SED DS3  FSpace
--------------------------------------------------------------------------
 0 -   -   -        -   RAID5 Optl  N  446.125 GB enbl N  N   none N
 0 0   -   -        -   RAID5 Optl  N  446.125 GB enbl N  N   none N
 0 0   0   252:2    38  DRIVE Onln  N  223.062 GB enbl N  N   none -
 0 0   1   252:3    9   DRIVE Onln  N  223.062 GB enbl N  N   none -
 0 0   2   252:4    37  DRIVE Onln  N  223.062 GB enbl N  N   none -
--------------------------------------------------------------------------
DG=Disk Group Index|Arr=Array Index|Row=Row Index|EID=Enclosure Device ID
DID=Device ID|Type=Drive Type|Onln=Online|Rbld=Rebuild|Dgrd=Degraded
Pdgd=Partially degraded|Offln=Offline|BT=Background Task Active
PDC=PD Cache|PI=Protection Info|SED=Self Encrypting Drive|Frgn=Foreign
DS3=Dimmer Switch 3|dflt=Default|Msng=Missing|FSpace=Free Space Present
Virtual Drives = 1
VD LIST :
=======
-----------------------------------------------------------
DG/VD TYPE  State Access Consist Cache sCC       Size Name
-----------------------------------------------------------
0/0   RAID5 Optl  RW     No      RaWTD -   446.125 GB
-----------------------------------------------------------
Cac=CacheCade|Rec=Recovery|OfLn=OffLine|Pdgd=Partially Degraded|dgrd=Degraded
Optl=Optimal|RO=Read Only|RW=Read Write|B=Blocked|Consist=Consistent|
Ra=Read Ahead Adaptive|R=Read Ahead Always|NR=No Read Ahead|WB=WriteBack|
AWB=Always WriteBack|WT=WriteThrough|C=Cached IO|D=Direct IO|sCC=Scheduled
Check Consistency
Physical Drives = 6
PD LIST :
=======
----------------------------------------------------------------------------
EID:Slt DID State DG       Size Intf Med SED PI SeSz Model               Sp
----------------------------------------------------------------------------
252:0    39 JBOD  -  223.062 GB SATA SSD N   N  512B INTEL SSDSC2CW240A3 U
252:1     8 JBOD  -  223.062 GB SATA SSD N   N  512B INTEL SSDSC2CW240A3 U
252:2    38 Onln  0  223.062 GB SATA SSD N   N  512B INTEL SSDSC2CW240A3 U

252:3     9 Onln  0  223.062 GB SATA SSD N   N  512B INTEL SSDSC2CW240A3 U
252:4    37 Onln  0  223.062 GB SATA SSD N   N  512B INTEL SSDSC2CW240A3 U

252:5    11 UGood -  223.062 GB SATA SSD N   N  512B INTEL SSDSC2CW240A3 U
----------------------------------------------------------------------------
EID-Enclosure Device ID|Slt-Slot No.|DID-Device ID|DG-DriveGroup
DHS-Dedicated Hot Spare|UGood-Unconfigured Good|GHS-Global Hotspare
UBad-Unconfigured Bad|Onln-Online|Offln-Offline|Intf-Interface
Med-Media Type|SED-Self Encryptive Drive|PI-Protection Info
SeSz-Sector Size|Sp-Spun|U-Up|D-Down|T-Transition|F-Foreign
```

ドライブグループ0番と、バーチャルドライブ0番が、今作成したRAID5のアレイ=VDです。DG=0の情報だけを見るには、次のようにします。

```
# /opt/MegaRAID/storcli/storcli64 /c0/d0 show
Controller = 0
Status = Success
Description = Show Diskgroup Succeeded

TOPOLOGY :
========
--------------------------------------------------------------------------
DG Arr Row EID:Slot DID Type  State BT       Size PDC  PI SED DS3  FSpace
--------------------------------------------------------------------------
 0 -   -   -        -   RAID5 Optl  N  446.125 GB enbl N  N   none N
 0 0   -   -        -   RAID5 Optl  N  446.125 GB enbl N  N   none N
 0 0   0   252:2    38  DRIVE Onln  N  223.062 GB enbl N  N   none -
 0 0   1   252:3    9   DRIVE Onln  N  223.062 GB enbl N  N   none -
 0 0   2   252:4    37  DRIVE Onln  N  223.062 GB enbl N  N   none -
--------------------------------------------------------------------------
DG=Disk Group Index|Arr=Array Index|Row=Row Index|EID=Enclosure Device ID
DID=Device ID|Type=Drive Type|Onln=Online|Rbld=Rebuild|Dgrd=Degraded
Pdgd=Partially degraded|Offln=Offline|BT=Background Task Active
PDC=PD Cache|PI=Protection Info|SED=Self Encrypting Drive|Frgn=Foreign
DS3=Dimmer Switch 3|dflt=Default|Msng=Missing|FSpace=Free Space Present
```

VD=0の情報だけを見るには、以下のようにします。

```
# /opt/MegaRAID/storcli/storcli64 /c0/v0 show
Controller = 0
Status = Success
Description = None

Virtual Drives :
==============
-----------------------------------------------------------
DG/VD TYPE  State Access Consist Cache sCC       Size Name
-----------------------------------------------------------
0/0   RAID5 Optl  RW     No      RaWTD -   446.125 GB
-----------------------------------------------------------
Cac=CacheCade|Rec=Recovery|OfLn=OffLine|Pdgd=Partially Degraded|dgrd=Degraded
Optl=Optimal|RO=Read Only|RW=Read Write|B=Blocked|Consist=Consistent|
Ra=Read Ahead Adaptive|R=Read Ahead Always|NR=No Read Ahead|WB=WriteBack|
AWB=Always WriteBack|WT=WriteThrough|C=Cached IO|D=Direct IO|sCC=Scheduled
Check Consistency
```

ライトキャッシュの設定がWTになっているので、AWBに変えてみます。

```
root@151:~# /opt/MegaRAID/storcli/storcli64 /c0/v0 set wrcache=AWB
Controller = 0
Status = Success
Description = None
Detailed Status :
===============
---------------------------------------
VD Property Value Status  ErrCd ErrMsg
---------------------------------------
 0 wrCache  AWB   Success     0 -
---------------------------------------
```

確認は次のようにします。

```
root@151:~# /opt/MegaRAID/storcli/storcli64 /c0/v0 show
Controller = 0
Status = Success
Description = None

Virtual Drives :
==============
------------------------------------------------------------
DG/VD TYPE  State Access Consist Cache  sCC       Size Name
------------------------------------------------------------
0/0   RAID5 Optl  RW     No      RaAWBD -   446.125 GB
------------------------------------------------------------
Cac=CacheCade|Rec=Recovery|OfLn=OffLine|Pdgd=Partially Degraded|dgrd=Degraded
Optl=Optimal|RO=Read Only|RW=Read Write|B=Blocked|Consist=Consistent|
Ra=Read Ahead Adaptive|R=Read Ahead Always|NR=No Read Ahead|WB=WriteBack|
AWB=Always WriteBack|WT=WriteThrough|C=Cached IO|D=Direct IO|sCC=Scheduled
Check Consistency
```

AWB　Always WriteBackに変わりました。

次に、ホットスペアドライブを設定してみます。まずはヘルプで、コマンドシンタックスを確認します。

```
# /opt/MegaRAID/storcli/storcli64 /c0/e252/s5 add help
     Storage Command Line Tool  Ver 1.03.11 Jan 30, 2013
     (c)Copyright 2012, LSI Corporation, All Rights Reserved.

NAME: Add Hot Spare Drive
SYNTAX: storcli /cx[/ex]/sx add hotsparedrive [DGs=]
        [enclaffinity] [nonrevertible]
DESCRIPTION: This command creates a hotspare drive.
OPTIONS:
DGs          - Specifies the drive group to which the hotspare drive is
               dedicated.
enclaffinity - Specifies the enclosure to which the hotspare is associated
               with. If this option is specified, affinity is set; if it is
               not specified, there is no affinity.NOTE Affinity cannot be
               removed once it is set for a hotspare drive.
nonrevertible- Sets the drive as a nonrevertible hotspare.
CONVENTION:
/cx - specifies a controller where X is the controller index.
/ex - specifies a enclosure where X is the enclosure device ID.
/sx - specifies a physical drive where X is the slot number.
```

そしてスロット5番のドライブをホットスペアに設定します。

```
# /opt/MegaRAID/storcli/storcli64 /c0/e252/s5 add hotsparedrive
Controller = 0
Status = Success
Description = Add Hot Spare Succeeded.
```

確認してみます。

```
root@151:~# /opt/MegaRAID/storcli/storcli64 /c0/e252/s5 show
Controller = 0
Status = Success
Description = Show Drive Information Succeeded.

Drive Information :
=================
----------------------------------------------------------------------------
EID:Slt DID State DG       Size Intf Med SED PI SeSz Model               Sp
----------------------------------------------------------------------------
252:5    11 GHS   -  223.062 GB SATA SSD N   N  512B INTEL SSDSC2CW240A3 U
----------------------------------------------------------------------------
EID-Enclosure Device ID|Slt-Slot No.|DID-Device ID|DG-DriveGroup
DHS-Dedicated Hot Spare|UGood-Unconfigured Good|GHS-Global Hotspare
UBad-Unconfigured Bad|Onln-Online|Offln-Offline|Intf-Interface
Med-Media Type|SED-Self Encryptive Drive|PI-Protection Info
SeSz-Sector Size|Sp-Spun|U-Up|D-Down|T-Transition|F-Foreign
```

スロット5番のドライブがグローバルホットスペアになったようです。

グローバルホットスペアの機能を確認するために、今RAID5のアレイの作成に用いたドライブの内、スロット2番のドライブをオフラインにしてみます。

```
# /opt/MegaRAID/storcli/storcli64 /c0/e252/s2 set offline
Controller = 0
Status = Success
Description = Set Drive Offline Succeeded.
```

バーチャルドライブの状態を見てみます。

```
# /opt/MegaRAID/storcli/storcli64 /c0/v0 show all
Controller = 0
Status = Success
Description = None

/c0/v0 :
======
------------------------------------------------------------
DG/VD TYPE  State Access Consist Cache  sCC       Size Name
------------------------------------------------------------
0/0   RAID5 Dgrd  RW     Yes     RaAWBD -   446.125 GB
------------------------------------------------------------
Cac=CacheCade|Rec=Recovery|OfLn=OffLine|Pdgd=Partially Degraded|dgrd=Degraded
Optl=Optimal|RO=Read Only|RW=Read Write|B=Blocked|Consist=Consistent|
Ra=Read Ahead Adaptive|R=Read Ahead Always|NR=No Read Ahead|WB=WriteBack|
AWB=Always WriteBack|WT=WriteThrough|C=Cached IO|D=Direct IO|sCC=Scheduled
Check Consistency

PDs for VD 0 :
============
----------------------------------------------------------------------------
EID:Slt DID State DG       Size Intf Med SED PI SeSz Model               Sp
----------------------------------------------------------------------------
252:5    11 Rbld   0 223.062 GB SATA SSD N   N  512B INTEL SSDSC2CW240A3 U
252:3     9 Onln   0 223.062 GB SATA SSD N   N  512B INTEL SSDSC2CW240A3 U
252:4    37 Onln   0 223.062 GB SATA SSD N   N  512B INTEL SSDSC2CW240A3 U

----------------------------------------------------------------------------
EID-Enclosure Device ID|Slt-Slot No.|DID-Device ID|DG-DriveGroup
DHS-Dedicated Hot Spare|UGood-Unconfigured Good|GHS-Global Hotspare
UBad-Unconfigured Bad|Onln-Online|Offln-Offline|Intf-Interface
Med-Media Type|SED-Self Encryptive Drive|PI-Protection Info
SeSz-Sector Size|Sp-Spun|U-Up|D-Down|T-Transition|F-Foreign

VD0 Properties :
==============
Strip Size = 256 KB
Span Depth = 1
Number of Drives Per Span = 3
Disk Cache Policy = Enabled
Encryption = None
Data Protection = Disabled
Active Operations = None
Exposed to OS = Yes
Creation Date = 22-05-2013
Creation Time = 05:28:54 PM
Emulation type = None
```

vd0はDegradedとなり、ホットスペアにしてあったスロット5番のドライブがvd0に加わり、Rebuild状態になっていることがわかります。

最後にvd0を削除してみます。

```
root@151:~#  /opt/MegaRAID/storcli/storcli64 /c0/v0 del
Controller = 0
Status = Success
Description = Delete VD succeeded
```

```
#  /opt/MegaRAID/storcli/storcli64 /c0/e252/s2-5 show
Controller = 0
Status = Success
Description = Show Drive Information Succeeded.

Drive Information :
=================
----------------------------------------------------------------------------
EID:Slt DID State DG       Size Intf Med SED PI SeSz Model               Sp
----------------------------------------------------------------------------
252:2    38 UGood -  223.062 GB SATA SSD N   N  512B INTEL SSDSC2CW240A3 U
252:3     9 UGood -  223.062 GB SATA SSD N   N  512B INTEL SSDSC2CW240A3 U
252:4    37 UGood -  223.062 GB SATA SSD N   N  512B INTEL SSDSC2CW240A3 U
252:5    11 UGood -  223.062 GB SATA SSD N   N  512B INTEL SSDSC2CW240A3 U
----------------------------------------------------------------------------
EID-Enclosure Device ID|Slt-Slot No.|DID-Device ID|DG-DriveGroup
DHS-Dedicated Hot Spare|UGood-Unconfigured Good|GHS-Global Hotspare
UBad-Unconfigured Bad|Onln-Online|Offln-Offline|Intf-Interface
Med-Media Type|SED-Self Encryptive Drive|PI-Protection Info
SeSz-Sector Size|Sp-Spun|U-Up|D-Down|T-Transition|F-Foreign
```

スロット2，3，4，5のドライブが、最初の状態Unconfigured Goodに戻りました。

以上、見てきたように、StorCLIの使い方について試してみました。

3wareのtw_cliに慣れた管理者の方には、直感的で大変使い易いのではないかと思います。

参考までにStorCLIのダウンロードリンクと、リファレンスマニュアルへの直リンクを貼っておきます。

StorCLI

http://www.lsi.com/downloads/Public/MegaRAID%20Common%20Files/1.03.11_StorCLI.zip

リファレンスマニュアル

http://www.lsi.com/downloads/Public/MegaRAID%20Common%20Files/StorCLI_RefMan_revf_.pdf
