# Vehicle-to-Infrastructure (V2I) Trace
We have collected traces for wireless network quality in four representative
driving scenarios. 

## Methodology
# __TODO__ add methodology in details..
We collected four traces using VNperf that simultaneously measures network
quality over multiple wireless networks. 

| Naming | Scenario | Length |
| ------ | -------- | ------ |
| D1 | Downtown | ~60mins | 
| D2 | Highway | ~60mins | 
| D3 | Rural | ~60mins | 
| D4 | Suburban | ~60mins |

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



## Map 
Each map.d[1,2,3,4].html graphical overview of routes taken for each scenario
around Ann Arbor. To view the map, 
```bash
$ python -m SimpleHTTPServer
# open your favorite web browser
# http://localhost:8080
```

# __TODO__: clarify what I mean by unavailable.
Note that **-1** means the measurement was **unavailable** (i.e., no signal,
previous 5 measurements have not been completed, etc).

## License
All source code, documentation, and related artifacts associated with the
cloudlet open source project are licensed under the [Apache License, Version
2.0](http://www.apache.org/licenses/LICENSE-2.0.html).
