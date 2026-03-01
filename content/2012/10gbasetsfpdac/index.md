+++
title = "10GBaseTとSFP+DACの比較"
date = 2012-05-14
description = "10GBaseTとSFP+DACのレイテンシ、最大ケーブル長、消費電力の比較調査メモ。"
path = "2012/05/10gbasetsfpdac.html"
+++

タイトルの件について調べ物をしたので、メモ。

レイテンシ

10GBaseTの規格ではエラー無くデータを転送するために、ブロックエンコーディングを行う。そのためには、ブロックサイズ分のデータを送信PHYに読み込み、エンコーディングを行ったのち、送信することが必要である。受信側では、その反対が必要である。規格によると、送受信PHYのペアで2.56μsの遅延を許容している。ブロックデータのサイズを考慮に入れると、リンクあたり2μs以下にすることは不可能である。

SFP+の場合には、ブロックエンコーディングが無く、より単純なエレクトロニクス構成であるため、遅延は典型値で300ns程度である。

それぞれの場合に、さらにメディア遅延を考慮する必用があるが、光であれ電気信号であれ、およそ5ns/m程度である。

最大ケーブル長

10GBaseTの場合、Cat6AまたはCat7ケーブルの利用により、100mまで通信可能である。

パッチパネルも使用可能である。

ダイレクトアタッチケーブルの場合、8.5mまでである。

25mまで大丈夫なケーブルも提案されている。

消費電力

10GBaseTは4W-6W/port(片側)

SFP+DACは1.5W/port(片側)

ソースは以下のホワイトペーパー

[http://www.missioncriticalmagazine.com/ext/resources/MC/Home/Files/PDFs/WP_Blade_Ethernet_Cabling.pdf](http://www.missioncriticalmagazine.com/ext/resources/MC/Home/Files/PDFs/WP_Blade_Ethernet_Cabling.pdf)

HPCなどの分野では遅延が少ない方が良いので、SFP+DACの方がお勧めということらしい。

Webやゲームのデータセンター用途で、2.6µsの遅延が問題になるのか、気になるところ。

ちなみにアリスタの10Gスイッチの遅延は、以下のサイトによると10GBaseTで3-3.6µs、SFP+で0.8-1.15µsである。

[http://www.aristanetworks.com/jp/products/7050series/7050t](http://www.aristanetworks.com/jp/products/7050series/7050t)

[http://www.aristanetworks.com/jp/products/7050series/7050s](http://www.aristanetworks.com/jp/products/7050series/7050s)
