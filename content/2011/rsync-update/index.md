+++
title = "rsync --updateオプションで悩む"
date = 2011-04-13
path = "2011/04/rsync-update.html"
+++

rsyncの--updateオプションは、転送先ファイルのmtimeが転送元よりも新しい場合に、そのファイルのコピーをスキップするオプションである。

しかしながら、シンボリックリンクやスペシャルファイルの場合は、このオプションがあっても、コピーはスキップされない。

> -u, --update

> This forces rsync to skip any files which exist on the destination  and  have  a modified  time  that is newer than the source file.  (If an existing destination file has a modification time equal to the source file’s, it will be  updated  if the sizes are different.)

> **Note that this does not affect the copying of symlinks or other special files.**  Also, a difference of file format between the sender and receiver is always considered to be important enough for an update, no matter what date is on the objects.  In other words, if the source has a directory where the destination has a file, the transfer would occur regardless of the timestamps.

コピー先のシンボリックの方が新しい場合には、コピーをスキップしたいのだが、どうすれば良いのでしょう？
