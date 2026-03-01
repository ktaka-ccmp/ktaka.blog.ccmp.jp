+++
title = "ファイル編集前の簡易バックアップ"
date = 2010-09-15
description = "Linuxの設定ファイル編集前にタイムスタンプ付きバックアップを取るシェル関数の紹介。"
path = "2010/09/blog-post.html"
+++

Linuxの設定ファイルなどを編集する際に、編集前のファイルのバックアップを取って置きたいことがある。設定をしくじったりした場合に、元の設定に戻したいからだ。

私は、そのために、次のようなシェルコマンドを自作して利用している。

以下の内容で、~/.functionsを作成する。

> bk ()
>
> {
>
>     file=${1##*/};
>
>     dir=${1%${1##*/}};
>
>     ( if [ "$dir" = "" ]; then
>
>         true;
>
>     else
>
>         if [ -d "$dir" ]; then
>
>             echo cd $dir;
>
>             cd $dir;
>
>         else
>
>             echo "No such directory: $dir ";
>
>             return 1;
>
>         fi;
>
>     fi;
>
>     if [ -f "$file" ]; then
>
>         mkdir -p .bk;
>
>         echo cp -p $file .bk/$file.$(date +"%Y%m%d%H%M" -r $file);
>
>         cp -p $file .bk/$file.$(date +"%Y%m%d%H%M" -r $file);
>
>     else
>
>         echo "No such file: $file ";
>
>     fi )
>
> }

この関数は、以下のような動作をするものである。

- バックアップを取りたいファイルが存在するディレクトリに.bk/とサブディレクトリを作成する。

- ファイルの最終変更日時(mtime)をサフィックスにもつコピーを作成する。

使用例

> ktaka@hana:~$ . ~/.functions
>
> ktaka@hana:~$ ls -la /home/ktaka/hello
>
> -rw-r--r-- 1 ktaka ktaka 1048576000 May 27  2009 /home/ktaka/hello
>
> ktaka@hana:~$ bk /home/ktaka/hello
>
> cd /home/ktaka/
>
> cp -p hello .bk/hello.200905270208
>
> ktaka@hana:~$ ls -la /home/ktaka/.bk/hello.200905270208
>
> -rw-r--r-- 1 ktaka ktaka 1048576000 May 27  2009 /home/ktaka/.bk/hello.200905270208

 ファイルの更新時をサフィックスに持つので、複数のバックアップファイルが存在する場合でも便利である。

~/.bashrcで.functionsを読み込むようにしておくと良い。

> if [ -f ~/.functions ]; then
>
>         . ~/.functions
>
> fi
