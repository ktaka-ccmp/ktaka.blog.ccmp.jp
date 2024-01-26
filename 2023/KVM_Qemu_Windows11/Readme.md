# 目次

- [目次](#目次)
  - [はじめに](#はじめに)
  - [Window11のインストール](#window11のインストール)
    - [KVM仮想マシンの起動方法](#kvm仮想マシンの起動方法)
    - [仮想マシンが立ち上がると、UEFシェルが起動してしまう。](#仮想マシンが立ち上がるとuefシェルが起動してしまう)
    - [インストール先のドライブが見えない](#インストール先のドライブが見えない)
    - [インストール時にMicrosoftアカウントへのサインインを求められる](#インストール時にmicrosoftアカウントへのサインインを求められる)
    - [残りのvirtioドライバーをインストール](#残りのvirtioドライバーをインストール)
  - [普段使いのために](#普段使いのために)
    - [Linuxホストのネットワークセットアップ](#linuxホストのネットワークセットアップ)
    - [Windowsゲスト起動コマンド](#windowsゲスト起動コマンド)
    - [Windowsゲストのネットワーク設定](#windowsゲストのネットワーク設定)
  - [その他のTips](#その他のtips)
  - [参考文献](#参考文献)
    - [QemuでのTPMの使い方](#qemuでのtpmの使い方)
    - [QEMUでのUEFI Secure Bootのやり方](#qemuでのuefi-secure-bootのやり方)
    - [どのUEFI firmwareを使うべきか](#どのuefi-firmwareを使うべきか)
  - [まとめ](#まとめ)

## はじめに

[前回](/2023/03/kvmqemuwindows.html)に引き続き、KVM仮想マシン上にWindows11をインストールするやり方をまとめておきます。

Windows10の時とは以下のような違いがあります。

- Windows11の場合、TPMとUEFI Secure Bootが必須である。
- KVMでTPMを使うには、ホストの/dev/tpm0をパススルーで使う方法と、ソフトウェアのTPMデバイスエミュレーター(swtpm)を使う方法がある。
- KVMでUEFI Secure Bootするには、ovmfパッケージにより提供されるUEFI firmwareを利用する。

## Window11のインストール

### KVM仮想マシンの起動方法

Windows11のインストールメディア、virtioドライバインストール用のisoイメージをダウンロードしておきます。

- [Download Windows 11](https://www.microsoft.com/en-us/software-download/windows11)
- [Windows用virtioドライバのありか](https://fedorapeople.org/groups/virt/virtio-win/direct-downloads/archive-virtio/)

必要パッケジージのインストール

```
sudo apt-get install qemu-system-x86 virt-viewer ovmf
```

qcow2ディスクイメージを作成します。

```
qemu-img create -f qcow2 win11pro.qcow2 40G
```

書き込み用のFirmwareのローカルコピーを作成します。

```
cp /usr/share/OVMF/OVMF_VARS_4M.ms.fd ./
```

#### ホストの/dev/tpm0をパススルーで使う場合

以下のコマンドで仮想マシンを起動できます。

```
sudo qemu-system-x86_64 \
	-machine q35,accel=kvm \
	-m 8192 -cpu host \
	-smp 6,sockets=1,dies=1,cores=6,threads=1 \
	-display spice-app \
	-drive file=./win11pro.qcow2,if=virtio,format=qcow2,discard=unmap \
	-drive file=~/Downloads/Win11_22H2_Japanese_x64v1.iso,index=0,media=cdrom \
	-drive file=~/Downloads/virtio-win-0.1.229.iso,index=1,media=cdrom \
	-drive if=pflash,format=raw,unit=0,file=/usr/share/OVMF/OVMF_CODE_4M.ms.fd,readonly=on \
	-drive if=pflash,format=raw,file=./OVMF_VARS_4M.ms.fd \
	-tpmdev passthrough,id=tpm0,path=/dev/tpm0,cancel-path=/dev/null \
	-device tpm-tis,tpmdev=tpm0 \
```

#### ソフトウェアのTPMデバイスエミュレータを使う場合

TPMデバイスエミュレータswtpmを起動しておきます。

```
mkdir mytpm
swtpm socket --tpmstate dir=./mytpm \
--tpm2 \
--ctrl type=unixio,path=./mytpm/swtpm-sock \
--log level=20
```

以下のコマンドで仮想マシンを起動できます。

```
sudo qemu-system-x86_64 \
	-machine q35,accel=kvm \
	-m 8192 -cpu host \
	-smp 6,sockets=1,dies=1,cores=6,threads=1 \
	-display spice-app \
	-drive file=./win11pro.qcow2,if=virtio,format=qcow2,discard=unmap \
	-drive file=~/Downloads/Win11_22H2_Japanese_x64v1.iso,index=0,media=cdrom \
	-drive file=~/Downloads/virtio-win-0.1.229.iso,index=1,media=cdrom \
	-drive if=pflash,format=raw,unit=0,file=/usr/share/OVMF/OVMF_CODE_4M.ms.fd,readonly=on \
	-drive if=pflash,format=raw,file=./OVMF_VARS_4M.ms.fd \
	-chardev socket,id=chrtpm,path=./mytpm/swtpm-sock \
	-tpmdev emulator,id=tpm0,chardev=chrtpm \
	-device tpm-tis,tpmdev=tpm0 \
```

### 仮想マシンが立ち上がると、UEFシェルが起動してしまう。
  
どうやらUEFIブートの場合、UEFIの設定画面でブートデバイスの優先順位を変更してやる必要があるようです。
UEFIシェルをexitで抜けるとUEFIの設定メニューに入るので、そこでUEFIシェルの優先順位をCDROM/DVDROMなどインストールメディアよりも低くします。
そして、RestまたはContinueで、Windowsインストール用のCDROMからブートします。

<!--[<img src="" width="50%">]() -->
<!-- <a href="" target="_blank"><img src="" width="30%"></a> -->
<a href="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEihrFFZMkVRwJR1x-xab4eUrN5p6I7c62JEHufK8YTtEkCxEBmDekjeremksk36dFa2iVpHmYEfADbCMCpmqkXeXjxu5ALDkteHK3qXBNf24NC7H13pf3XH9NRoajeW-_9GC2zuehDbvF9TOoPTuE7N8tmcUmQ0DT-W57VMcHD-x7oM9gbG-2ZvMos2/s812/UEFI_Interactive_Shell01.png" target="_blank"><img src="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEihrFFZMkVRwJR1x-xab4eUrN5p6I7c62JEHufK8YTtEkCxEBmDekjeremksk36dFa2iVpHmYEfADbCMCpmqkXeXjxu5ALDkteHK3qXBNf24NC7H13pf3XH9NRoajeW-_9GC2zuehDbvF9TOoPTuE7N8tmcUmQ0DT-W57VMcHD-x7oM9gbG-2ZvMos2/s812/UEFI_Interactive_Shell01.png" width="30%"></a>
  <a href="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEiqHreJWPEoR0Fpe_jIgQraetmCskhYNlXq1lbhvB6TOO2J3cxcsAmqnRcdZyhHXrP2IfwjHl3q4Cv4uKjuihbAqCBph6QmXUzK1Lvn8pAFDxQ_kjhHv-kjxUju-VHeV53POKiUNGVlf49nKKsJHExJpJ6zTLZdR0H2F651Yz1mA--UPJ1m6nyljSas/s652/UEFI_Menu03_2.png" target="_blank"><img src="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEiqHreJWPEoR0Fpe_jIgQraetmCskhYNlXq1lbhvB6TOO2J3cxcsAmqnRcdZyhHXrP2IfwjHl3q4Cv4uKjuihbAqCBph6QmXUzK1Lvn8pAFDxQ_kjhHv-kjxUju-VHeV53POKiUNGVlf49nKKsJHExJpJ6zTLZdR0H2F651Yz1mA--UPJ1m6nyljSas/s652/UEFI_Menu03_2.png" width="30%"></a>
  <a href="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjLlqsFcDN-bPtB0kXDk5afq8Z00njv8JZAuTfKN-wsO8rKjY9KoGT7PNaqtUZ2WrKR3YxKiD2sdy55TLNC3Xd4TicCVA97ihFcd4vbcOLHst_cdqrWLhR9RUJLPKalK3w2460Tg55Yr49Ky3u86vbhh-FtuLOeJxaViFVtQreL6vfb0XEfcbsoFJuo/s652/UEFI_Menu05_2.png" target="_blank"><img src="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjLlqsFcDN-bPtB0kXDk5afq8Z00njv8JZAuTfKN-wsO8rKjY9KoGT7PNaqtUZ2WrKR3YxKiD2sdy55TLNC3Xd4TicCVA97ihFcd4vbcOLHst_cdqrWLhR9RUJLPKalK3w2460Tg55Yr49Ky3u86vbhh-FtuLOeJxaViFVtQreL6vfb0XEfcbsoFJuo/s652/UEFI_Menu05_2.png" width="30%"></a>

### インストール先のドライブが見えない

E:ドライブ(virtio-win-xx)にあるドライバを読み込むと、qcow2のディスクイメージが見えるようになるので、そこにWindows11をインストールします。

  <a href="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjPRUFpYwiM6pVv34_N62FADeDOf81gAY92gIJoY5MSI60k7KzcMDMgenuVKqNp_sffAyBDif-5s4GMCeW2yshRsw954np5BvRxYkNjExSJi522HXSUxiUcUsQuJu-EDC0Euqvmod6gwkn1SrWCz8QFbsEri07lV9gAmbrJRBJPQfgjD_dYM1coC5xS/s812/Win11Installer03.png" target="_blank"><img src="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjPRUFpYwiM6pVv34_N62FADeDOf81gAY92gIJoY5MSI60k7KzcMDMgenuVKqNp_sffAyBDif-5s4GMCeW2yshRsw954np5BvRxYkNjExSJi522HXSUxiUcUsQuJu-EDC0Euqvmod6gwkn1SrWCz8QFbsEri07lV9gAmbrJRBJPQfgjD_dYM1coC5xS/s812/Win11Installer03.png" width="30%"></a>
  <a href="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEiieg21QaYwI425apZUogwiSTcIAkZzddzzRVGDty6NHfGoSOH3U_zi2lRbuwMgoGdkOzChtbUq8E7hVlG44Gro40C5Ia_FMj1qtaEPLSD9IgOGBvlYQiRjC1xXQjEyMa8cgCiTl1SK546K9zNRFzNXnr0XPc1MS4n0FdY18GN218YlE1M4xfI_HPUz/s812/Win11Installer04.png" target="_blank"><img src="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEiieg21QaYwI425apZUogwiSTcIAkZzddzzRVGDty6NHfGoSOH3U_zi2lRbuwMgoGdkOzChtbUq8E7hVlG44Gro40C5Ia_FMj1qtaEPLSD9IgOGBvlYQiRjC1xXQjEyMa8cgCiTl1SK546K9zNRFzNXnr0XPc1MS4n0FdY18GN218YlE1M4xfI_HPUz/s812/Win11Installer04.png" width="30%"></a>
  <a href="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgj56FVNkvw7VGKBYY4J9UCf35bImgTQlvElka3lBn-9juHZjYUderh1dnnuuX0BExKce48fEdomkMBaANzi1OKPZVsA6szkgdS2uvjgxx2XN4qFP3oDCGuh2PWq52I8HlFcG-2_nHNh0VBe18r6ygCJJjldeFiTcrdn8nYwjHGbXFpnbjexDPVvRvj/s812/Win11Installer06.png" target="_blank"><img src="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgj56FVNkvw7VGKBYY4J9UCf35bImgTQlvElka3lBn-9juHZjYUderh1dnnuuX0BExKce48fEdomkMBaANzi1OKPZVsA6szkgdS2uvjgxx2XN4qFP3oDCGuh2PWq52I8HlFcG-2_nHNh0VBe18r6ygCJJjldeFiTcrdn8nYwjHGbXFpnbjexDPVvRvj/s812/Win11Installer06.png" width="30%"></a>
  
### インストール時にMicrosoftアカウントへのサインインを求められる

no@thankyou.comで一度サインインに失敗すると、ローカルアカウントが作成できます。

  <a href="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEiDKU4bzc8PYfvrRNVgoQ038q5T9ZVFg2ebpZKjOdwh7njqrTQcp1jEsS3KmGgLqloBInsW-WJu3coySNApuL4JocTbTH6UcridWunnAqF_wPKt0t7OQfpoDc4SY8EncIOxUGXQJ8-cx87vLikZiHOTNGQEInp3nb_CeFw7y2yuJoZumpau3DBUx5V1/s812/Win11Installer10.png" target="_blank"><img src="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEiDKU4bzc8PYfvrRNVgoQ038q5T9ZVFg2ebpZKjOdwh7njqrTQcp1jEsS3KmGgLqloBInsW-WJu3coySNApuL4JocTbTH6UcridWunnAqF_wPKt0t7OQfpoDc4SY8EncIOxUGXQJ8-cx87vLikZiHOTNGQEInp3nb_CeFw7y2yuJoZumpau3DBUx5V1/s812/Win11Installer10.png" width="30%"></a>
  <a href="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEja31VpoXAyUeinucn0m8ug0f-aLRYzvOukM5hjMDsK1l8oStduZ_RavW6v-ciP09VFnmLg0ZCXXXuajWpS5TudHAR0lIigsKno9sZQ_wi1rDA-IfZ-LGkDUDPTbTTrz2pWXDDhfYyxlYP-P8NYjs1EAEMLJgsESmjKOMVDygagXwg548wQwnzh1Lvs/s812/Win11Installer12.png" target="_blank"><img src="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEja31VpoXAyUeinucn0m8ug0f-aLRYzvOukM5hjMDsK1l8oStduZ_RavW6v-ciP09VFnmLg0ZCXXXuajWpS5TudHAR0lIigsKno9sZQ_wi1rDA-IfZ-LGkDUDPTbTTrz2pWXDDhfYyxlYP-P8NYjs1EAEMLJgsESmjKOMVDygagXwg548wQwnzh1Lvs/s812/Win11Installer12.png" width="30%"></a>
  <a href="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjoIYyfVpPWVNmHFkx7aXVfBKjOhhfI0cEMZJD8ZuWRTjMxk5phUD6FvyQT3_vYAkp11U2zDrrXTIr2so5Nxcerx7F9r5xvCSslXd-WpxFvTKLu5MymZC1B1VeJxSSzic4VWfNELkh0xnrPdC08QnPNY3CwU1O_AZkPcC3OsJBOjl4hrLTzE8zNFkZf/s812/Win11Installer13.png" target="_blank"><img src="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjoIYyfVpPWVNmHFkx7aXVfBKjOhhfI0cEMZJD8ZuWRTjMxk5phUD6FvyQT3_vYAkp11U2zDrrXTIr2so5Nxcerx7F9r5xvCSslXd-WpxFvTKLu5MymZC1B1VeJxSSzic4VWfNELkh0xnrPdC08QnPNY3CwU1O_AZkPcC3OsJBOjl4hrLTzE8zNFkZf/s812/Win11Installer13.png" width="30%"></a>

### 残りのvirtioドライバーをインストール

Windowsセットアップ完了後、Windows上でE:ドライブ（virtio-win-0.1.229）を開きます。そこにあるインストーラを起動し、virtioドライバをインストールしておきます。

<a href="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgR_4IR-LHHigsJUqb__6_-AmY3GL1wfXo8G9-lsj7BdPzbkmox22bTZBYAwiuBxTLfdyc0kfg-ny2MhAlQtCLwQ8DKgu0N-l4bC8ftMjqemOkWrUQqp3bziniBOPh6ff1D8ssezNP4YfE9rr6d0V8Z8zxahcrHTvtU6SEAARKw-9N3p0vJk3o5ctUl/s812/virtio_install01.png" target="_blank"><img src="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgR_4IR-LHHigsJUqb__6_-AmY3GL1wfXo8G9-lsj7BdPzbkmox22bTZBYAwiuBxTLfdyc0kfg-ny2MhAlQtCLwQ8DKgu0N-l4bC8ftMjqemOkWrUQqp3bziniBOPh6ff1D8ssezNP4YfE9rr6d0V8Z8zxahcrHTvtU6SEAARKw-9N3p0vJk3o5ctUl/s812/virtio_install01.png" width="30%"></a>
<a href="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjni-rgb1JVtBCy-NMiEReK7pe5TW3w3Ecc3gzmRUHqweir9ebthWDOpS11vTSf3W3ekwB4wpoB-Tl7LCTR-3n-w4XhLxgnfDsPeGycsefskDmLGXXiN4WNTTcrzDTyTjH7Z_oS7plt5aSodaBvw8CRTOo_gbAWEdHp_8ZCmE58lAbCHAruZuPdC1Rn/s812/virtio_install02.png" target="_blank"><img src="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjni-rgb1JVtBCy-NMiEReK7pe5TW3w3Ecc3gzmRUHqweir9ebthWDOpS11vTSf3W3ekwB4wpoB-Tl7LCTR-3n-w4XhLxgnfDsPeGycsefskDmLGXXiN4WNTTcrzDTyTjH7Z_oS7plt5aSodaBvw8CRTOo_gbAWEdHp_8ZCmE58lAbCHAruZuPdC1Rn/s812/virtio_install02.png" width="30%"></a>

以上で、ネットワーク関連は未設定状態ですが、Windows11がインストールされたqcow2ディスクイメージ、win11pro.qcow2ができあがります。
  
## 普段使いのために

Windows11のインストールは、ネットワーク無しで行った。仮想マシン上のWindows11を利用するには、ネットワークが使えないと困るでしょう。
ネットワークを使えるようにするためには、次の3つの準備が必要です。

1. Linuxホスト上でのネットワーク設定
1. KVM起動コマンドをネットワークが使えるように修正
1. Windows11ゲストマシン上でネットワーク設定

### Linuxホストのネットワークセットアップ

Linuxホスト上では、以下の設定を行えば十分です。

```
brdg=kbr0
outif=wlan0
addr=10.0.0.254/24

# ブリッジインターフェースの準備
brctl addbr $brdg
ip add add dev $brdg $addr
ip link set dev $brdg up

# IPマスカレード設定
iptables -t nat -A POSTROUTING -s $addr -o $outif -j MASQUERADE

# IPフォワーディング許可
echo 1 >  /proc/sys/net/ipv4/conf/$outif/forwarding
echo 1 >  /proc/sys/net/ipv4/conf/$brdg/forwarding
```

念の為、上記で用意したものをもとに戻すのは、以下のやり方で良いでしょう。

```
# IPフォワーディング許可を取り消す
echo 0 >  /proc/sys/net/ipv4/conf/$outif/forwarding
echo 0 >  /proc/sys/net/ipv4/conf/$brdg/forwarding

# ブリッジインターフェースを消す
ip link set dev $brdg down
brctl delbr $brdg

# IPマスカレード設定を消す
iptables -t nat -D POSTROUTING -s $addr -o $outif -j MASQUERADE
```

### Windowsゲスト起動コマンド

qemuコマンドはオプションが多いのでスクリプト化しておくと良いでしょう。

```
run.win11.sh:
#!/bin/bash 

sudo qemu-system-x86_64 \
		-m 8192 -cpu host \
		-smp 6,sockets=1,dies=1,cores=6,threads=1 \
        -drive file=./win11pro.qcow2,if=virtio,format=qcow2,discard=unmap \
        -display spice-app \
        -machine q35,accel=kvm \
        -rtc base=localtime,clock=host \
        -drive if=pflash,format=raw,unit=0,file=/usr/share/OVMF/OVMF_CODE_4M.ms.fd,readonly=on \
        -drive if=pflash,format=raw,file=./OVMF_VARS_4M.ms.fd \
        -tpmdev passthrough,id=tpm0,path=/dev/tpm0,cancel-path=/dev/null \
        -device tpm-tis,tpmdev=tpm0 \
        -device virtio-net-pci,netdev=dev1,mac=52:54:00:11:00:12,id=net1 \
        -netdev tap,id=dev1,vhost=on,script=./qemu-ifup
```

仮想マシン起動時にデバイスをホストのブリッジにアタッチします。

```
qemu-ifup:
#!/bin/sh

bridge=kbr0
/sbin/ip link set dev $1 up promisc off
/sbin/brctl addif $bridge $1
```

### Windowsゲストのネットワーク設定

次のアドレスを設定

```
IPv4アドレス: 10.0.0.1/24
ゲートウェイ: 10.0.0.254
DNSサーバ: 192.168.40.1(Linuxホストと同じ設定にすると良いと思う。)
```

  <a href="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEj5VRIXuwnZ1FiZHXeG2lmJDIVphJlT4sqLOKeOK3Sk4eXW-B4r1P_FsjfEq6jvwlFcWtgoMYbGmD2-EFBAPEkBzomgXZH8tuaYG_soLx81SkayPRt-3Vi4fyR0695IlxK3ifT7EmEnI-GWbQC3JWYBAnSjJOek_ZOM2o7ku5m0J-p3nQ3OZOseOxes/s812/network_setup01.png" target="_blank"><img src="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEj5VRIXuwnZ1FiZHXeG2lmJDIVphJlT4sqLOKeOK3Sk4eXW-B4r1P_FsjfEq6jvwlFcWtgoMYbGmD2-EFBAPEkBzomgXZH8tuaYG_soLx81SkayPRt-3Vi4fyR0695IlxK3ifT7EmEnI-GWbQC3JWYBAnSjJOek_ZOM2o7ku5m0J-p3nQ3OZOseOxes/s812/network_setup01.png" width="30%"></a>

この他に、Windows 11 Proの場合はRemote Desktop機能があるので、利用可能にしておくと良いでしょう。

## その他のTips

- 一旦ビューワーを閉じたあともう一度接続するには
```
$ sudo virt-viewer -c spice+unix:///tmp/.JVB811/spice.sock
```
- Remote Desktop接続は、例えば次のようにする
```
user=ktaka
xfreerdp /u:$user /size:1900x1000 +fonts +clipboard  /audio-mode:1 /v:10.0.0.1
```
- qemu起動時にはwindowを表示せず、rdpのみで使うには
`--display spice-app`を`--display none`にすれば良い。

## 参考文献 

### QemuでのTPMの使い方

以下のドキュメントに十分な情報があります。

- [QEMU TPM Device](https://qemu-project.gitlab.io/qemu/specs/tpm.html)

### QEMUでのUEFI Secure Bootのやり方

- [SecureBootVirtualMachine](https://wiki.debian.org/SecureBoot/VirtualMachine)
- [Secure(ish) boot with QEMU](https://www.labbott.name/blog/2016/09/15/secure-ish-boot-with-qemu/)

### どのUEFI firmwareを使うべきか

Debianのドキュメントに書いてあります。

- Secure Boot pre-enabledな、OVMF_CODE_4M.ms.fdとOVMF_VARS_4M.ms.fdをセットで使う。
- 前者はRead Onlyで、後者はコピーしたものをRead Write可能な状態で利用する。
- UEFIのメニューでSaveした設定変更は、OVMF_VARS_4M.ms.fdのコピーに書き込まれる。

/usr/share/doc/ovmf/README.Debian
```
The OVMF_CODE*.fd files provide UEFI firmware for a QEMU guest that is
intended to be read-only. The OVMF_VARS*.fd files provide UEFI variable
template images which are intended to be read-write, and therefore each
guest should be given its own copy. Here's an overview of each of them:

OVMF_CODE_4M.fd
  Use this for booting guests in non-Secure Boot mode. While this image
  technically supports Secure Boot, it does so without requiring SMM
  support from QEMU, so it is less secure. Use the OVMF_VARS.fd template
  with this.

OVMF_CODE_4M.ms.fd
  This is a symlink to OVMF_CODE_4M.secboot.fd. It is useful in the context
  of libvirt because the included JSON firmware descriptors will tell libvirt
  to pair OVMF_VARS.ms.fd with it, which has Secure Boot pre-enabled.

OVMF_CODE_4M.secboot.fd
  Like OVMF_CODE_4M.fd, but will abort if QEMU does not support SMM.
  Use this for guests for which you may enable Secure Boot. Be aware
  that the included JSON firmware descriptors associate this with
  OVMF_CODE_4M.fd. Which means, if you specify this image in libvirt, you'll
  get a guest that is Secure Boot-*capable*, but has Secure Boot disabled.
  To enable it, you'll need to manually import PK/KEK/DB keys and activate
  Secure Boot from the UEFI setup menu. If you want Secure Boot active from
  the start, consider using OVMF_CODE.ms.fd instead.

OVMF_VARS_4M.fd
  This is an empty variable store template, which means it has no
  built-in Secure Boot keys and Secure Boot is disabled. You can use
  it with any OVMF_CODE image, but keep in mind that if you want to
  boot in Secure Boot mode, you will have to enable it manually.

OVMF_VARS_4M.ms.fd
  This template has distribution-specific PK and KEK1 keys, and
  the default Microsoft keys in KEK/DB. It also has Secure Boot
  already activated. Using this with OVMF_CODE.ms.fd will boot a
  guest directly in Secure Boot mode.

OVMF32_CODE_4M.secboot.fd
OVMF32_VARS_4M.fd
  These images are the same as their "OVMF" variants, but for 32-bit guests.

OVMF_CODE.fd
OVMF_CODE.ms.fd
OVMF_CODE.secboot.fd
OVMF_VARS.fd
OVMF_VARS.ms.fd
  These images are the same as their "4M" variants, but for use with guests
  using a 2MB flash device. 2MB flash is no longer considered sufficient for
  use with Secure Boot. This is provided only for backwards compatibility.

OVMF_VARS_4M.snakeoil.fd
  This image is **for testing purposes only**. It includes an insecure
  "snakeoil" key in PK, KEK & DB. The private key and cert are also
  shipped in this package as well, so that testers can easily sign
  binaries that will be considered valid. Intended for use with
  OVMF_CODE_4M.secboot.fd.

PkKek-1-snakeoil.key
PkKek-1-snakeoil.pem
  The private key and certificate for the snakeoil key. Use these
  to sign binaries that can be verified by the key in the
  OVMF_VARS.snakeoil.fd template. The password for the key is
  'snakeoil'.

 -- dann frazier <dannf@debian.org>, Fri, 11 Dec 2020 17:30:59 -0700
```

## まとめ

QEMUコマンドのみでKVM仮想マシンを起動し、Windows11をインストールする方法についてまとめました。
Window10の場合との違いは、TPM及びUEFI Secure Bootが必須であることです。
Windows11の場合も、GUIプログラムvirt-managerでのインストール方法はネット上でよく見かけますが、qemuコマンドのみでのやり方はあまり多くないようです。
余計なものはなるべくインストールしたくない人、ソフトウェアスタックをミニマムに保って中身を理解しながら使いたい人の役に立てば幸いです。
