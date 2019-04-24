# Troubleshooting
This is a journal of troubleshooting (== number of times I shouted **FML**) while building VNperf.

### TP-LINK T4U Installation
```
$ sudo apt install rtl8812au-dkms
$ sudo modprobe 8812au rtw_power_mgnt=0 rtw_enusbss=0 rtw_ips_mode=2 # load module 
```

### Cellular modem does not work (mostly Novatel modem)
```
$ lsmod | grep 'cdc\|usb\|rndis\|option\|hid'

# Make sure to check no related modules loaded
$ sudo modprobe -r usbhid rndis_host cdc_acm cdc_ether
$ sudo usb_modeswitch -v 1410 -p 9030 -u 2

# wait for a minute
$ sudo usb_modeswitch -v 1410 -p 9030 -u 1
```

### Weird wireless interface namings
For Ubuntu 16.04, your WiFi & USB cellular interfaces would look like this:
```
$ ifconfig
	enp0s20f0u1 ... # FML FML FML
	wlp58s0
```
Make sure to change to normal (```wlan0, usb0, ...```) by editing grub config
(```/etc/default/grub```):
```
$ vim /etc/default/grub
> find, replace, and save
  GRUB_CMDLINE_LINUX="net.ifnames=0 biosdevname=0" 
$ sudo update-grub && sudo reboot 
```

