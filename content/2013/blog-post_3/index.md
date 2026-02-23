+++
title = "出荷を待つファイルサーバー"
date = 2013-07-03
path = "2013/07/blog-post_3.html"
+++

某お客様向けのファイルサーバーです。フロントに2.5インチのホットスワップHDDベイを8個備えています。

<img src="/2013/07/blog-post_3.html/image/IMG_2828.JPG" width="320" height="240">

今回はSeagateの1TByte SATAドライブを8本搭載します。合計8TByteの構成です。

<img src="/2013/07/blog-post_3.html/image/IMG_2830.JPG" width="320" height="240">

HDDはバックプレーンからminiSASケーブルを介してLSIのRAIDカードMegaRAID SAS 9271-8iに接続されています。このカードにはキャッシュ保護のためにCacheVaultというモジュールが取り付けられています。

<img src="/2013/07/blog-post_3.html/image/IMG_2832.JPG" width="320" height="240">

CPUはXeon E3-1270v2、メモリは8GByte x4 合計32GByteと、なかなかハイスペックな構成です。8本のHDDドライブをSSDに交換すれば、そこそこ高速なDBサーバとしても使えそうです。

<img src="/2013/07/blog-post_3.html/image/IMG_2831.JPG" width="320" height="240">

12,000回転のカウンターローテイティングファンを5個でシステムを冷却。CPUもメモリもRAIDカードも十分に冷却できます。

<img src="/2013/07/blog-post_3.html/image/IMG_2833.JPG" width="320" height="240">

電源は500Wの電源モジュール2個で冗長化されています。

<img src="/2013/07/blog-post_3.html/image/IMG_2835.JPG" width="320" height="240">

IOインターフェースは、PS/2 マウス、キーボード、IPMI専用LANポート、USBx2、シリアルポート、VGAポート、GLANポートｘ2となっています。

<img src="/2013/07/blog-post_3.html/image/IMG_2836.JPG" width="320" height="240">

筐体内部のほぼ全体写真です。配線もまあまあ、スッキリしています。

<img src="/2013/07/blog-post_3.html/image/IMG_2834.JPG" width="320" height="240">

以上です。

こんなサーバが欲しいというご要望がありましたら、是非ともご相談ください。
