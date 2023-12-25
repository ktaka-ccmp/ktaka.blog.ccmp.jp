パソコンからドコモwifiに繋ぐための設定。
```
vaiox:~# cat /etc/wpa_supplicant.conf_docomo_wifi
ctrl_interface=/var/run/wpa_supplicant
network={
 ssid="docomo"
 scan_ssid=1
 key_mgmt=IEEE8021X
 eap=TTLS
 identity="xxxxx-spmode@docomo"
 password="xxxxxx"
 ca_cert="/etc/PCA-3.pem"
 phase2="auth=PAP"
}
```
無線LANチップのドライバーをロードし、wpa_supplicantをデーモンとして起動、dhcpでアドレスを取得すればOK。

```
modprobe ath9k
wpa_supplicant -Dwext -iwlan0 -c /etc/wpa_supplicant.conf_docomo_wifi -B
dhclient wlan0
```
