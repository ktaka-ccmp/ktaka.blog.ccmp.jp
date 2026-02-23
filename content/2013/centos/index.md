+++
title = "CentOSをネットワークインストールしてみる"
date = 2013-01-10
path = "2013/01/centos.html"
+++

みなさんこんにちは！

ここ2、3年、OSのインストールも自分でやらなくなってしまった気がしますが、とあるサーバーにCentOS 6.3をインストールすることになりました。備忘録的に記録を書いておこうと思います。

CentOSのダウンロードサイトは、[この辺り](http://www.centos.org/modules/tinycontent/index.php?id=30)にリスト化されているので、この中のどれかから持ってくれば良さそうです。

今回、linuxカーネルダウンロードでおなじみの[kernel.orgのサイト](http://mirrors.kernel.org/centos/)からダウンロードして来ようと思います。

ディレクトリを眺めていると、/centos/6.3/os/x86_64/images/pxeboot にネットワークインストールに必要なカーネルとinitrdイメージが置いてあるようなので、ダウンロードしてpxeサーバに置いておきます。

```
initrd.img                    06-Jul-2012 10:13   30M
vmlinuz                       06-Jul-2012 10:13  3.8M
```

それにしても、カーネルもinitrdもでかいですね…(^_^;)

pxelinux..cfg/defaultに以下の行を追加

> label cent63
>         kernel img/centos/6.3-x86_64/vmlinuz
>         append vga=normal initrd=img/centos/6.3-x86_64/initrd.img panic=10 text console=tty0 

上記で指定した場所に、先ほどファイルを置いておきます。

> # tree  img/centos/6.3-x86_64/
> img/centos/6.3-x86_64/
> ├── initrd.img
> └── vmlinuz
> 0 directories, 2 files

そして対象サーバをpxebootすると、弊社のサーバでは以下の様なメニュー画面が表示されます。

<img src="/2013/01/centos.html/image/20130110_01.jpg" width="400" height="243">

cent63を選択すると、無事インストーラが立ち上がりました。

<img src="/2013/01/centos.html/image/20130110_02.jpg" width="400" height="243">

後は普通にインストールを進めます。

ネットワーク経由でインストールするので、次のメニューではURLを選択します。

<img src="/2013/01/centos.html/image/20130110_03.jpg" width="400" height="242">

URLには、　http://mirrors.kernel.org/centos/6.3/os/x86_64/　と入力し、OKを押します。

<img src="/2013/01/centos.html/image/20130110_04.jpg" width="400" height="243">

すると、インストールイメージを取得します。

<img src="/2013/01/centos.html/image/20130110_05.jpg" width="400" height="243">

その後メニューで、textモードを選択するとインストーラーが起動します。

<img src="/2013/01/centos.html/image/20130110_06.jpg" width="400" height="243">

後は、普通にインストールすればOKです。
