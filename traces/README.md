# Vehicle-to-Infrastructure (V2I) Traces


## Methodology
We have collected traces of wireless network quality for two cellular networks
(Sprint and Verizon) and commercial WiFi hotspot (XFinityWiFi) in four
representative driving scenarios (in downtown, highway, rural, and suburban
areas). 


We collected fo
We collected four traces using VNperf that simultaneously measures network
quality over multiple wireless networks. VNperf


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

### Unavailable measurement
Note that **-1** means the measurement was **unavailable** (i.e., no signal,
previous 5 measurements have not been completed, etc).

## Visual Map 
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

## License
All source code, documentation, and related artifacts associated with the
cloudlet open source project are licensed under the [Apache License, Version
2.0](http://www.apache.org/licenses/LICENSE-2.0.html).
