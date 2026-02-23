+++
title = "[備忘録] jfbterm終了時に固まることがある件"
date = 2009-10-26
path = "2009/10/jfbterm.html"
+++

ここを参考に、以下のように変更

ktaka@lets:~/SRC$ diff -c jfbterm-0.4.7_orig/term.c jfbterm-0.4.7/term.c
*** jfbterm-0.4.7_orig/term.c   2003-09-16 00:45:31.000000000 +0900
--- jfbterm-0.4.7/term.c        2009-10-26 23:09:54.000000000 +0900
***************
*** 76,82 ****
  void sigchld(sig) int sig; {
        int st;
        int ret;
!       ret = wait(&st);
        if (ret == gChildProcessId || ret == ECHILD) {
                tvterm_unregister_signal();
                tterm_final(&gTerm);
--- 76,82 ----
  void sigchld(sig) int sig; {
        int st;
        int ret;
!       ret = waitpid(gChildProcessId, &st, WNOHANG);
        if (ret == gChildProcessId || ret == ECHILD) {
                tvterm_unregister_signal();
                tterm_final(&gTerm);

但し、asm/page.hが無といわれたり、コンパイルが通らないので、
最新のデビアン用の[パッチ](http://ftp.de.debian.org/debian/pool/main/j/jfbterm/jfbterm_0.4.7-8.diff.gz)を当て、コンパイルを通す。

今のところ直っているようにみえる。
