+++
title = "10GBaseTイーサネットに関して調べ物"
date = 2012-05-10
description = "CX4、SFP+ファイバー、SFP+ DAC、10GBaseTなど10Gbeインターフェースの特徴比較と対応製品の紹介。"
path = "2012/05/10gbaset.html"
+++

10GbeのインターフェイスにはCX4、SFP+ファイバー、SFP+ダイレクトアタッチカッパー(DAC)、10GBaseTなどがある。

CX4

- 古い技術で、ケーブルの太さやコネクタの大きさなどから、高集積化には向かない。ケーブル長15mまで。

SFP+ファイバー　10GBase-SR

- 高価である

- 低消費電力、ケーブル長300mまで。

- サーバにネットワークカードの増設が必用。

SFP+DAC

- 比較的安価である。ケーブル長は7mまで。

- サーバにネットワークカードの増設が必用。

10GBaseT

- 安価である。

- 従来、消費電力が大きく、高コストであると思われていたが、最近のプロセステクノロジーによりそうでもなくなった。NICの消費電力が初期の25W/portから6W/portに低下した。

- 1000BaseTイーサネット環境とポート互換性がある。1ギガビットのNICを持つサーバを10GBaseTのスイッチに接続でき、10GBaseTのNICを持つサーバを1ギガのスイッチに接続することができる。

- サーバにネットワークカードの増設が必用。10GBaseTポートが搭載されたマザーが出始めている。

- レイテンシー2μs～4μs。HPCユーザや高頻度な金融取引の用途では、気になるかもしれない。

- 普通はCPUの割り込み負荷低減のために、Interrupt Moderationが使われ、その場合には～100μsのレイテンシーが意図的に追加されるので問題ない。

以上、Intelのホワイトペーパーより

[http://www.intel.com/content/www/us/en/network-adapters/10-gigabit-network-adapters/10-gigabit-ethernet-10gbase-t-paper.html](http://www.intel.com/content/www/us/en/network-adapters/10-gigabit-network-adapters/10-gigabit-ethernet-10gbase-t-paper.html)

10GBaseTポート標準搭載のサーバの例

Supermicro 1027R-WRFT+

[http://www.supermicro.com/products/system/1U/1027/SYS-1027R-WRFT_.cfm](http://www.supermicro.com/products/system/1U/1027/SYS-1027R-WRFT_.cfm)

Supermicro 6017R-N3RFT+

[http://www.supermicro.com/products/system/1U/6017/SYS-6017R-N3RFT_.cfm](http://www.supermicro.com/products/system/1U/6017/SYS-6017R-N3RFT_.cfm)

10GBaseT x 48ポートスイッチ

Arista 7050T-52/7050T-64

[http://www.aristanetworks.com/jp/products/7050series/7050t](http://www.aristanetworks.com/jp/products/7050series/7050t)

いずれも弊社から、販売可能です！
