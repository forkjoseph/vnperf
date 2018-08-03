# Trace Format
Each trace has 6 columns by default. 
* mph: Speed of vehicle
* lat: Latitude
* lon: Longitude
* bz_vz: RTT over Verizon to Brazos server
* bz_sp: RTT over Sprint to Brazos server
* bz_w1: RTT over XFinityWiFi to Brazos server

Note that **-1** means the measurement was **unavailable** (i.e., no signal,
previous 5 measurements have not been completed, etc).


CSV is formated as following:
```
count, timestamp, mph, latitude, longitude, bz_vz, bz_sp, bz_w1, ec_vz, ec_sp, ec_w1
```
where ```bz``` and ```ec``` stand for ```brazos``` server in UMich and ```AWS
EC2``` server in Ohio, respectively.  ```vz``` and ```sp``` stand for Verizon
and Sprint cellular networks. Note that traces in ```traces/``` folder omit
count and timestamp.

## License
All source code, documentation, and related artifacts associated with the
cloudlet open source project are licensed under the [Apache License, Version
2.0](http://www.apache.org/licenses/LICENSE-2.0.html).
