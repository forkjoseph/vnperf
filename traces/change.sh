#!/usr/bin/env bash
# ** ONLY 3 NETWORKS!!! **
rtt_3=$1"ms"
rtt_4=$2"ms"
rtt_5=$3"ms"

loss_3="0.0%"
loss_4="0.0%"
loss_5="0.0%"

if [ ! -z $5 ]; then
  loss_3="$5%"
fi 

if [ ! -z $6 ]; then
  loss_4="$6%"
fi 

if [ ! -z $7 ]; then
  loss_5="$7%"
fi 

eth_3="eth3"
ifb_3="ifb3"

eth_4="eth4"
ifb_4="ifb4"

eth_5="eth5"
ifb_5="ifb5"

# delays & loss - 3
tc qdisc change dev $eth_3 parent 1:30 handle 30: \
  netem delay $rtt_3 loss $loss_3
tc qdisc change dev $ifb_3 parent 1:35 handle 35: \
  netem delay $rtt_3 loss $loss_3


# delays & loss - 4
tc qdisc change dev $eth_4 parent 1:40 handle 40: \
  netem delay $rtt_4 loss $loss_4
tc qdisc change dev $ifb_4 parent 1:45 handle 45: \
  netem delay $rtt_4 loss $loss_4

# delays & loss - 5
tc qdisc change dev $eth_5 parent 1:50 handle 50: \
  netem delay $rtt_5 loss $loss_5
tc qdisc change dev $ifb_5 parent 1:55 handle 55: \
  netem delay $rtt_5 loss $loss_5
