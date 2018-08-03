# VNperf: Vehicular Network performance measurement tool

# This RAEDME.md is still under construction!!!

## Testbed Platform
We have tested VNperf on **Dell XPS 13 Developer** laptop running **Ubuntu16.04
LTS 64bit**. 

For network interfaces, we have tested with three networks:
* usb0: Verizon Wireless MiFi U620L
* usb1: Franklin U772 USB Modem 
* wlan1: TP-LINK T4U v2

For location and vehicle data, we used following hardwares:
* GPS: GlobalSat BU353-S4 USB GPS Receiver
* OBD2: HDE ELM 327 

************


## Setup
VNperf does not use Network-manager. Uses plain wpa_supplicant and dhclient for network configuration.

### Step 1: stop all Ubuntu default network manager
```
$ sudo service network-manager stop
$ sudo service networking stop
$ sudo service wpa_supplicant stop
$ sudo service dhcpd stop
$ sudo service supervisor stop
$ sudo service ModemManager stop
```

### Step 2: 
```
$ sudo cp -v conf/zzz-zz-buildtable /etc/dhcp/dhclient-enter-hooks.d/zzz-zz-buildtable
$ sudo cp -v conf/dhclient.conf /etc/dhcp/vnperf-dhclient.conf
$ ./scripts/build_rttables.sh register
$ sudo mkdir -v /etc/vnperf /etc/vnperf_control /etc/vnperf/
$ sudo cp -rv scripts /etc/vnperf/scripts
$ sudo chown $(whoami):$(whoami) /etc/vnperf && cd /etc/vnperf
$ touch usb0.stat usb1.stat wlan1.stat
```

### Step 3: run WPA on wlan1
```
# new terminal-1
$ sudo wpa_supplicant -d -i wlan1 -Dwext -c $(pwd)/conf/wlan1.conf
# why -Dext? b/c TP-Link T4U AC1200 has RTL chipset (rtl8812AU)
# new terminal-2
$ sudo wpa_cli -p /etc/vnperf_control/wlan -a vnperf/scripts/wpa_cli_wlan1.sh
```

### Step 4: set up cellular networks
```
# after plugging in usb-cell modems
# new terminal-5, Wait for 10 seconds!!!
$ sudo modprobe -r cdc_ether option cdc_acm usbhid
$ sudo kill -9 $(sudo ps -axf | grep "dh.*usb0" | grep -v "grep" | awk '{print $1}')
$ sudo dhclient -d usb0 -v -cf vnperf/conf/dhclient_usb0.conf usb0
```

### Step 5: run server on ***server side***
```
$ ./server.py
```

### Step 6: run VNperf on laptop
```
$ sudo ./vnperf.py -t [IP] -i wlan1 -i usb0 -i usb1 -D -I 0.25
```


## Contribution
VNperf tool is maintained by HyunJong (Joseph) Lee, Jason Flinn from University of
Michigan.

## License
All source code, documentation, and related artifacts associated with the
cloudlet open source project are licensed under the [Apache License, Version
2.0](http://www.apache.org/licenses/LICENSE-2.0.html).
