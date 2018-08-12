# V2I Trace


# TODO: add methodology 

## Trace Format
For each row, there are 6 columns:
* vehiclespeed: Speed of vehicle
* latitude: Latitude of vehicle
* longitude: Longitude of vehicle
* verizon: RTT over Verizon
* sprint: RTT over Sprint
* xfinitywifi: RTT over XFinityWiFi

# TODO: clarify what I mean by unavailable.
Note that **-1** means the measurement was **unavailable** (i.e., no signal,
previous 5 measurements have not been completed, etc).

## License
All source code, documentation, and related artifacts associated with the
cloudlet open source project are licensed under the [Apache License, Version
2.0](http://www.apache.org/licenses/LICENSE-2.0.html).
