+++
title = "Intel SSDの保証とsmart情報について"
date = 2014-08-11
description = "Intel SSDの保証条件とMedia Wearout Indicatorの関係を調査し、smartctlでの取得方法をRAIDカード経由の実例とともに解説。"
path = "2014/08/intel-ssd.html"
+++

こんにちは。暑い日が続きますね。

Intel SSDの保証期間について調べる機会がありましたので、 忘れないようにメモしておきます。

何のことはなくインテルの以下のページに、よくまとまってかかれています。

[http://www.intel.com/jp/support/ssdc/hpssd/sb/CS-029645.htm](http://www.intel.com/jp/support/ssdc/hpssd/sb/CS-029645.htm)

これによると、保証の条件は製品によって若干異なるようですが、大まかに言って、次の二つに大別されるようです。

- SSDのフラッシュメディアのWear out(摩耗)情報が取れるものに関しては、それが限度に達するか、5年または3年の保証。

- 上記に当てはまらないものは、5年または3年の保証。

SSDには書き込み寿命がありますので、保証期間内であっても、メディアが寿命を越えてしまった場合には、保証の対象外となってしまう場合があるようです。

手元に、Intel 520 SSD 240GBと、DC S3500 120GBがありましたので、詳しく調べてみました。

### まず、Intel 520 SSD 240GBの場合。

以下のページを見ると、520は、"E9 メディア消耗指数 (Media Wear-Out Indicator) が利用できない"らしく、上述の保証条件の2番に当てはまりそうです。

[http://www.intel.com/jp/support/ssdc/hpssd/sb/cs-032511.htm](http://www.intel.com/jp/support/ssdc/hpssd/sb/cs-032511.htm)

なるほど、"Media Wear-Out Indicator"は取得できないのですね…確かめてみましょう。

手元のIntel 520 SSD 240GBと言うのは、実は、LSIのMegaraid 9266-8iという、それはそれは高性能なRAIDカードの配下にぶら下がっています。

Megaraid配下のドライブの"Media Wear-Out Indicator"情報を取得するには、RAIDのユーティリティ(megacli, storcli等)でドライブIDを特定し、smartctlでsmart情報を取得すれば良いようです。

まず、storcliでDriveIDを取得します。

```
# /opt/MegaRAID/storcli/storcli64 /c0 /eall /sall show
Controller = 0
Status = Success
Description = Show Drive Information Succeeded.
Drive Information :
=================
----------------------------------------------------------------------------
EID:Slt DID State DG       Size Intf Med SED PI SeSz Model               Sp
----------------------------------------------------------------------------
252:0     8 Onln   0 223.062 GB SATA SSD N   N  512B INTEL SSDSC2CW240A3 U
252:1    46 UBad   - 223.062 GB SATA SSD N   N  512B INTEL SSDSC2CW240A3 U
252:2    48 Onln   0 223.062 GB SATA SSD N   N  512B INTEL SSDSC2CW240A3 U
252:3     9 Onln   0 223.062 GB SATA SSD N   N  512B INTEL SSDSC2CW240A3 U
252:4    37 Onln   0 223.062 GB SATA SSD N   N  512B INTEL SSDSC2CW240A3 U
252:5    11 Onln   0 223.062 GB SATA SSD N   N  512B INTEL SSDSC2CW240A3 U
252:6    47 Onln   0 223.062 GB SATA SSD N   N  512B INTEL SSDSC2CW240A3 U
252:7    12 JBOD   - 232.375 GB SATA HDD N   N  512B ST9250421AS         U
----------------------------------------------------------------------------
EID-Enclosure Device ID|Slt-Slot No.|DID-Device ID|DG-DriveGroup
DHS-Dedicated Hot Spare|UGood-Unconfigured Good|GHS-Global Hotspare
UBad-Unconfigured Bad|Onln-Online|Offln-Offline|Intf-Interface
Med-Media Type|SED-Self Encryptive Drive|PI-Protection Info
SeSz-Sector Size|Sp-Spun|U-Up|D-Down|T-Transition|F-Foreign
```

この例では、{8,46,48,9,37,11,47,12}が各スロットにつながっているSSD/HDDのDriveIDとなります。

スロット0番のSSDのスマート情報を取得するには、例えば以下の様にすれば良いです。

```
# smartctl  -d megaraid,8  /dev/sdb -A
smartctl 5.41 2011-06-09 r3365 [x86_64-linux-3.13.2-64kvmh01] (local build)
Copyright (C) 2002-11 by Bruce Allen, http://smartmontools.sourceforge.net
/dev/sdb [megaraid_disk_08] [SAT]: Device open changed type from 'megaraid' to 'sat'
=== START OF READ SMART DATA SECTION ===
SMART Attributes Data Structure revision number: 10
Vendor Specific SMART Attributes with Thresholds:
ID# ATTRIBUTE_NAME          FLAG     VALUE WORST THRESH TYPE      UPDATED  WHEN_FAILED RAW_VALUE
  5 Reallocated_Sector_Ct   0x0032   100   100   000    Old_age   Always       -       0
  9 Power_On_Hours          0x0032   000   000   000    Old_age   Always       -       257801117878698
 12 Power_Cycle_Count       0x0032   100   100   000    Old_age   Always       -       362
170 Unknown_Attribute       0x0033   100   100   010    Pre-fail  Always       -       0
171 Unknown_Attribute       0x0032   100   100   000    Old_age   Always       -       0
172 Unknown_Attribute       0x0032   100   100   000    Old_age   Always       -       0
174 Unknown_Attribute       0x0032   100   100   000    Old_age   Always       -       353
184 End-to-End_Error        0x0033   100   100   090    Pre-fail  Always       -       0
187 Reported_Uncorrect      0x0032   100   100   000    Old_age   Always       -       0
192 Power-Off_Retract_Count 0x0032   100   100   000    Old_age   Always       -       353
225 Load_Cycle_Count        0x0032   100   100   000    Old_age   Always       -       1902970
226 Load-in_Time            0x0032   100   100   000    Old_age   Always       -       65535
227 Torq-amp_Count          0x0032   100   100   000    Old_age   Always       -       56
228 Power-off_Retract_Count 0x0032   100   100   000    Old_age   Always       -       65535
232 Available_Reservd_Space 0x0033   100   100   010    Pre-fail  Always       -       0
233 Media_Wearout_Indicator 0x0032   097   097   000    Old_age   Always       -       0
241 Total_LBAs_Written      0x0032   100   100   000    Old_age   Always       -       1902970
242 Total_LBAs_Read         0x0032   100   100   000    Old_age   Always       -       2432048
249 Unknown_Attribute       0x0013   100   100   000    Pre-fail  Always       -       50803# smartctl  -d megaraid,8  /dev/sdb -A
smartctl 5.41 2011-06-09 r3365 [x86_64-linux-3.13.2-64kvmh01] (local build)
Copyright (C) 2002-11 by Bruce Allen, http://smartmontools.sourceforge.net
/dev/sdb [megaraid_disk_08] [SAT]: Device open changed type from 'megaraid' to 'sat'
=== START OF READ SMART DATA SECTION ===
SMART Attributes Data Structure revision number: 10
Vendor Specific SMART Attributes with Thresholds:
ID# ATTRIBUTE_NAME          FLAG     VALUE WORST THRESH TYPE      UPDATED  WHEN_FAILED RAW_VALUE
  5 Reallocated_Sector_Ct   0x0032   100   100   000    Old_age   Always       -       0
  9 Power_On_Hours          0x0032   000   000   000    Old_age   Always       -       257801117878698
 12 Power_Cycle_Count       0x0032   100   100   000    Old_age   Always       -       362
170 Unknown_Attribute       0x0033   100   100   010    Pre-fail  Always       -       0
171 Unknown_Attribute       0x0032   100   100   000    Old_age   Always       -       0
172 Unknown_Attribute       0x0032   100   100   000    Old_age   Always       -       0
174 Unknown_Attribute       0x0032   100   100   000    Old_age   Always       -       353
184 End-to-End_Error        0x0033   100   100   090    Pre-fail  Always       -       0
187 Reported_Uncorrect      0x0032   100   100   000    Old_age   Always       -       0
192 Power-Off_Retract_Count 0x0032   100   100   000    Old_age   Always       -       353
225 Load_Cycle_Count        0x0032   100   100   000    Old_age   Always       -       1902970
226 Load-in_Time            0x0032   100   100   000    Old_age   Always       -       65535
227 Torq-amp_Count          0x0032   100   100   000    Old_age   Always       -       56
228 Power-off_Retract_Count 0x0032   100   100   000    Old_age   Always       -       65535
232 Available_Reservd_Space 0x0033   100   100   010    Pre-fail  Always       -       0
233 Media_Wearout_Indicator 0x0032   097   097   000    Old_age   Always       -       0
241 Total_LBAs_Written      0x0032   100   100   000    Old_age   Always       -       1902970
242 Total_LBAs_Read         0x0032   100   100   000    Old_age   Always       -       2432048
249 Unknown_Attribute       0x0013   100   100   000    Pre-fail  Always       -       50803
```

上記のsmart情報で、16進数でE9、すなわち233番がMedia_Wearout_Indicatorとなっていることが分かります。上記の場合、現在の値が97で、ワースト値が97、しきい値が0ということになります。

よく分からないので調べてみると、どうやら、新品のSSDはMedia_Wearout_Indicatorの値が100で、使用するにつれてだんだん減っていき、1になるともうダメと言うことのようです。

> Media Wear-out Indicator は、正規化した (normalized) 値が 100 で (SSD が新規工場出荷時)、1 へと減少していきます。値が 1 になった時、それは消耗の限界に到達したことを意味し、データ消滅を防ぐためにその SSD を交換するか、バックアップを取ることが推奨されます。 

> [http://www.intel.com/jp/support/ssdc/hpssd/sb/CS-032510.htm](http://www.intel.com/jp/support/ssdc/hpssd/sb/CS-032510.htm)

しきい値0と言うのは、smartの世界では、障害予測に用いないということを意味する、特別な値を示しているようです。

> [http://www.hdsentinel.com/smart/index.php](http://www.hdsentinel.com/smart/index.php)[http://www.easis.com/smart-value-interpretation.html](http://www.easis.com/smart-value-interpretation.html) 

インテルの保証のページには、520シリーズのSSDは"Media Wear-out Indicatorが取得できない"種類のSSDに大別されていましたが、どうやら取得できてしまうようですσ(^_^;)

どうせ壊れるんなら、保証期間内かつMedia Wear-out Indicatorが1になる前に壊れてくれることを祈りましょう。。。

ちなみにデータシートによると、241のTotal_LBAs_WrittenのRawValueは総書き込み量を32MByteで割ったもの、同じく242のTotal_LBAs_ReadのRawValueは総読み出し量を32MByteで割ったものであるようです。

したがって、この場合の書き込み総量は、60,895,040Mbyte = 約61Tbyte、読み出し総量は、77,825,536Mbyte = 約78TByteとなります。

かなり書き込んでるにも関わらず、Media Wear-out Indicatorが3しか減っていないと言うのはうれしいですね。(この割合で行くと仮定すると、あと1PB位は余裕で書けちゃいそうですね。)

### 次に、DC S3500 120GBの場合です。

以下のドキュメントによると、DC S3500シリーズのSSDは保証期間に加えて、Media Wear-out Indicatorも、保証の条件として考慮されるようです。

> [http://download.intel.com/support/ssdc/hpssd/sb/DC_S3500_Warranty_r0_Japanese.pdf](http://download.intel.com/support/ssdc/hpssd/sb/DC_S3500_Warranty_r0_Japanese.pdf)

では、実際にMedia Wear-out Indicatorの値を確かめて見ましょう。

手元のDC 3500 120GBと言うのは、Adaptec 5805Zと言う、とっても高性能なRAIDコントローラーにぶら下がっています。

AdaptecのRAIDコントローラにぶら下がった、SSDやHDDのsmart情報を取得するには、次のようなコマンドを実行すれば良いはずです。

> # smartctl -d sat /dev/sg3 -i

AdaptecのRAIDカードの場合、scsi genericドライバを読み込めば、/dev/sgXにデバイスファイルを作成してくれるので、それはそれは便利です。/dev/sgXのXの値が何になるかは、dmesgの出力を見て判別してもいいですが、/dev/sgXの数自体がそんなに多くなければ、順番にsmartctl -d sat /dev/sgX -iで調べていってもいいでしょう。

dmesgの出力例

```
# dmesg |grep scsi
scsi0 : aacraid
scsi 0:0:0:0: Direct-Access     Adaptec  1                V1.0 PQ: 0 ANSI: 2
scsi 0:0:1:0: Direct-Access     Adaptec  Device 1         V1.0 PQ: 0 ANSI: 2
scsi 0:1:0:0: Direct-Access     INTEL    SSDSC2BB12       D201 PQ: 1 ANSI: 5
scsi 0:1:1:0: Direct-Access     INTEL    SSDSC2CW24       400i PQ: 1 ANSI: 5
scsi 0:1:2:0: Direct-Access     INTEL    SSDSC2BB12       D201 PQ: 1 ANSI: 5
scsi 0:1:3:0: Direct-Access     INTEL    SSDSC2BB12       D201 PQ: 1 ANSI: 5
scsi 0:1:4:0: Direct-Access     INTEL    SSDSC2BB12       D201 PQ: 1 ANSI: 5
scsi 0:1:5:0: Direct-Access     INTEL    SSDSC2BB12       D201 PQ: 1 ANSI: 5
scsi 0:1:6:0: Direct-Access     INTEL    SSDSC2BB12       D201 PQ: 1 ANSI: 5
scsi 0:1:7:0: Direct-Access     INTEL    SSDSC2BB12       D201 PQ: 1 ANSI: 5
scsi 0:3:0:0: Enclosure         ADAPTEC  Virtual SGPIO  0 0001 PQ: 0 ANSI: 5
scsi 0:3:1:0: Enclosure         ADAPTEC  Virtual SGPIO  1 0001 PQ: 0 ANSI: 5
sd 0:0:0:0: Attached scsi generic sg0 type 0
sd 0:0:1:0: Attached scsi generic sg1 type 0
scsi 0:1:0:0: Attached scsi generic sg2 type 0
scsi 0:1:1:0: Attached scsi generic sg3 type 0
scsi 0:1:2:0: Attached scsi generic sg4 type 0
scsi 0:1:3:0: Attached scsi generic sg5 type 0
scsi 0:1:4:0: Attached scsi generic sg6 type 0
scsi 0:1:5:0: Attached scsi generic sg7 type 0
scsi 0:1:6:0: Attached scsi generic sg8 type 0
scsi 0:1:7:0: Attached scsi generic sg9 type 0
scsi 0:3:0:0: Attached scsi generic sg10 type 13
scsi 0:3:1:0: Attached scsi generic sg11 type 13
scsi1 : ata_piix
scsi2 : ata_piix
scsi3 : ata_piix
scsi4 : ata_piix
scsi 2:0:1:0: CD-ROM            TEAC     DV-28S-V         1.0B PQ: 0 ANSI: 5
scsi 2:0:1:0: Attached scsi generic sg12 type 5
```

/dev/sg2で試して見ます。

```
# smartctl -d sat /dev/sg2 -i
smartctl 5.41 2011-06-09 r3365 [x86_64-linux-3.14.4-64kvmh01] (local build)
Copyright (C) 2002-11 by Bruce Allen, http://smartmontools.sourceforge.net
=== START OF INFORMATION SECTION ===
Device Model:     INTEL SSDSC2BB120G4
Serial Number:    BTWL40150AQK120LGN
LU WWN Device Id: 5 5cd2e4 04b5637db
Firmware Version: D2010370
User Capacity:    120,034,123,776 bytes [120 GB]
Sector Sizes:     512 bytes logical, 4096 bytes physical
Device is:        Not in smartctl database [for details use: -P showall]
ATA Version is:   8
ATA Standard is:  ACS-2 revision 3
Local Time is:    Mon Aug 11 13:57:01 2014 JST
SMART support is: Available - device has SMART capability.
SMART support is: Enabled
```

Media Wear-out Indicatorの値は以下のように取得できます。

```
# smartctl -d sat /dev/sg2 -A
smartctl 5.41 2011-06-09 r3365 [x86_64-linux-3.14.4-64kvmh01] (local build)
Copyright (C) 2002-11 by Bruce Allen, http://smartmontools.sourceforge.net
=== START OF READ SMART DATA SECTION ===
SMART Attributes Data Structure revision number: 1
Vendor Specific SMART Attributes with Thresholds:
ID# ATTRIBUTE_NAME          FLAG     VALUE WORST THRESH TYPE      UPDATED  WHEN_FAILED RAW_VALUE
  5 Reallocated_Sector_Ct   0x0032   100   100   000    Old_age   Always       -       0
  9 Power_On_Hours          0x0032   100   100   000    Old_age   Always       -       798
 12 Power_Cycle_Count       0x0032   100   100   000    Old_age   Always       -       14
170 Unknown_Attribute       0x0033   100   100   010    Pre-fail  Always       -       0
171 Unknown_Attribute       0x0032   100   100   000    Old_age   Always       -       0
172 Unknown_Attribute       0x0032   100   100   000    Old_age   Always       -       0
174 Unknown_Attribute       0x0032   100   100   000    Old_age   Always       -       9
175 Program_Fail_Count_Chip 0x0033   100   100   010    Pre-fail  Always       -       17188520638
183 Runtime_Bad_Block       0x0032   100   100   000    Old_age   Always       -       0
184 End-to-End_Error        0x0033   100   100   090    Pre-fail  Always       -       0
187 Reported_Uncorrect      0x0032   100   100   000    Old_age   Always       -       0
190 Airflow_Temperature_Cel 0x0022   074   074   000    Old_age   Always       -       26 (Min/Max 23/27)
192 Power-Off_Retract_Count 0x0032   100   100   000    Old_age   Always       -       9
194 Temperature_Celsius     0x0022   100   100   000    Old_age   Always       -       33
197 Current_Pending_Sector  0x0032   100   100   000    Old_age   Always       -       0
199 UDMA_CRC_Error_Count    0x003e   100   100   000    Old_age   Always       -       0
225 Load_Cycle_Count        0x0032   100   100   000    Old_age   Always       -       6850
226 Load-in_Time            0x0032   100   100   000    Old_age   Always       -       30
227 Torq-amp_Count          0x0032   100   100   000    Old_age   Always       -       76
228 Power-off_Retract_Count 0x0032   100   100   000    Old_age   Always       -       47910
232 Available_Reservd_Space 0x0033   100   100   010    Pre-fail  Always       -       0
233 Media_Wearout_Indicator 0x0032   100   100   000    Old_age   Always       -       0
234 Unknown_Attribute       0x0032   100   100   000    Old_age   Always       -       0
241 Total_LBAs_Written      0x0032   100   100   000    Old_age   Always       -       6850
242 Total_LBAs_Read         0x0032   100   100   000    Old_age   Always       -       21958
```

Media_Wearout_Indicatorの値は100です。つまり、新品同様です。

Total_LBAs_WrittenやTotal_LBAs_Readで見ても、それぞれ、219,200Mbyte、702,656Mbyte相当となりますので、まだまだたくさん使えそうです。

### まとめ

Intel SSDの保証とsmart情報について調べて見ました。保証の条件は製品により異なりますが、Media Wearout Indicatorの値が取得できるとされる製品とそうでないものに大別され、前者の場合、Media Wearout Indicatorが１になってしまうと、保証交換が受けられないと考えられます。Media Wearout Indicatorはsmartctlコマンドで取得できます。手元にあったIntel 520とDC S3500は両方とも値が取得できました。SMART情報には、他にもTotal LBA WrittenなどSSDの使用状況を確認するのにちょうど良い値が記録されているので、いろいろ調べてみると良いでしょう。
