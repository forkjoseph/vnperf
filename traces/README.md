# Vehicle-to-Infrastructure (V2I) Traces
We have collected traces of wireless network quality for two cellular networks
(Sprint and Verizon) and one commercial WiFi hotspot (XFinityWiFi) that has been
deployed rapidly in densely-populated area.
The traces are collected in four representative driving scenarios - downtown,
highway, rural, and suburban areas - to measure wireless network quality in each
of unique scenarios. 
The traces were collected in October 2017 around Ann Arbor, each ranging from
40-62 minutes length.


## Methodology
For trace collection, we configured VNperf to measure every 1 second
interval to measure.
We also configured VNperf to declare that latencies of over 5 seconds to
represent blackout (**unavailable**) periods. We found that for WiFi hotspot,
this is a common case because of low signal. We also found out that 
XFinityWiFi supports seamless *WiFi-roaming* that queues packets from one AP
when device is disconnected and deliver to another AP when reconnected. 
Queued packets from one AP can later deliver over another AP at reconnection.
To avoid previous queued packets affects latency of present measurements, VNperf
logs **-1** to declare the network is unavailable or exhibits high latency, if
more than 5 previous measurements have not been successfully completed.
Thus, periods of network unavailability appear to be intervals that exhibit
extremely high latency.

For WPA authentication, XFinityWiFi driver handles WiFi-roaming based on network
interface's MAC address. When more than one access points (APs) are available,
we configured WPA supplicant to associate the one with the highest signal
strength. We noticed that DHCP sometimes incorrectly triggers when the
interface has not been associated with any AP for more than 5 minutes. So, we
used DHCP enter-hook to detect new gateways at every WPA association.

We collected traces in October 2017, each ranging from 40-62 minutes in length.
Trace D1 was collected driving through the downtown areas of Ann Arbor, MI
(population approximately 120,000 and metro area population approximately
350,000).  Trace D2 was collected solely on interstate highway driving,
primarily but not exclusively through rural areas.  Trace D3 was collected on
rural roads in sparsely-populated areas.  Trace D4 was collected in suburban
locations that included neighborhoods, subdivisions, and secondary roads. 

## Summary of traces
The following is a shortened summary of trace analysis.  Details of study is
available in Table 1 of our paper, [RAVEN: Improving Interactive Latency
for the Connected Car](https://goo.gl/JNgHDu). 

| Naming | Scenario | Length | Mean MPH |
| ------ | -------- | ------ | -------- |
| D1 | Downtown | ~62 mins | 5.33 |
| D2 | Highway | ~53 mins | 66.55 |
| D3 | Rural | ~49 mins | 35.71 | 
| D4 | Suburban | ~40 mins | 7.52 |

Throughout the four traces, we found that 
* No network consistently offers the lowest RTTs.
* It appears quite challenging to predict which network will lower the lowest
  RTT over short time scales.
* At the tail of each CDF, RTTs are very high, which will substantially degrade
  interactive applications.
* High RTTs are weakly correlated. High RTTs on one network could be masked by
  using another network.

## Trace Format
For each row, there are 6 columns:

| Column name  | Meaning  | 
| ------------ | --------- |
| vehiclespeed| Speed of vehicle|
| latitude| Latitude of vehicle|
| longitude| Longitude of vehicle|
| verizon| RTT over Verizon|
| sprint| RTT over Sprint|
| xfinitywifi| RTT over XFinityWiFi|

Each row contains measurements of Verizon, Sprint, and XFinityWiFi along with
vehicle speed and location. As noted previously, we configured VNperf to measure
at every 1 second interval to minimize external variables.
For each scenario, the vehicle was driven without previously designed route to
remove bias. However, the speed limit in each route was strictly enforced.

## Visual Route Map 
Each map.d[1,2,3,4].html contains graphical overview of routes taken in each
scenario around Ann Arbor. To view the map, 
```bash
$ cd vnperf/traces
$ git clone https://gist.github.com/4dec208e28b36ce554d43c8653123050.git maps/
$ mv maps/*.html .
$ python -m SimpleHTTPServer
# open your favorite web browser
# goto http://localhost:8080 
```

## Replay Traces in a Testbed
Replay script emulates latency changing condition by replaying a selected trace
in testbed.
```bash
# make sure you have Linux TC setup
$ cd vnperf/traces
$ python replay/replay.py public.d1_downtown.csv
```

#

## License
All source code, documentation, and related artifacts associated with the
cloudlet open source project are licensed under the [Apache License, Version
2.0](http://www.apache.org/licenses/LICENSE-2.0.html).
