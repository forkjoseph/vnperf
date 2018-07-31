# VNperf: Vehicular Network performance measurement tool

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


## Trace Format
Trace is saved in CSV file format to be easily loaded as DataFrame later for
parsing.  Each column contains:
* UNIX timestamp
* Speed of vehicle (in MPH) via OBD2
* Location of vehicle (in lat & lon) via external GPS module
* RTT```s``` to server```s``` (yes, plurals) 

CSV is formated as following:
```
count, timestamp, mph, latitude, longitude, bz_vz, bz_sp, bz_w1, ec_vz, ec_sp, ec_w1
```
where ```bz``` and ```ec``` stand for ```brazos``` server in UMich and ```AWS
EC2``` server in Ohio, respectively.  ```vz``` and ```sp``` stand for Verizon
and Sprint cellular networks. Note that traces in ```traces/``` folder omit
count and timestamp.

***

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
$ sudo cp -v conf/dhclient.conf /etc/dhcp/dhclient.conf
$ ./scripts/build_rttables.sh register
$ sudo mkdir -v /etc/vnperf /etc/vnperf_control
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

## License
All source code, documentation, and related artifacts associated with the
cloudlet open source project are licensed under the [Apache License, Version
2.0](http://www.apache.org/licenses/LICENSE-2.0.html).
