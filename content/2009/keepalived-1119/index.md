+++
title = "keepalived-1.1.19がリリースされました"
date = 2009-10-08
description = "keepalived 1.1.19のリリースとnopreemptオプションによるVRRP改善の紹介。"
path = "2009/10/keepalived-1119.html"
+++

10/1にkeepalived-1.1.19がリリースされました。

keepalivedのvrrpの実装では、ネットワークリンクがダウンするとFAULT Stateに入ります。
ネットワークリンクがアップすると、FAULT StateからいきなりMASTERに昇格してしまい、コネクタの接触不良などの場合に、MASTERがバタバタ入れ替わってしまうという、かなり致命的な危険性がありました。

nopreemptオプションを有効にすることで、リンクの復旧時にBACKUPステートに入るようにでき、その様な危険性がなくなりました。

[http://www.keepalived.org/changelog.html](http://www.keepalived.org/changelog.html)
