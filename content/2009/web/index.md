+++
title = "[備忘録] テキストコンソールでWeb閲覧"
date = 2009-10-26
path = "2009/10/web.html"
+++

LinuxのテキストコンソールでWeb閲覧したい件
結局、/dev/tty1ならば、ssh-agent -> jfbterm -> screenと自動起動するようにしました。

export LC_ALL=ja_JP
export LANG=ja_JP.UTF-8

if [ `tty` == "/dev/tty1" ] ; then
        exec ssh-agent jfbterm -e screen
fi

screenのwindowでemacsを開き、そこで'M-x w3m'とすれば、Webが閲覧できる。
日本語入力もemacs+skkのおかげでほぼ問題無さそうです。

screenの中からstartxでXが起動できないので、Xを使いたい時は、Alt+F[2-6]で他のttyに切り替えて使用することにします。
