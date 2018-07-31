dev="$1"
sudo ip link set $dev down
sudo ip addr flush  dev $dev
sleep 1
sudo ip link set $dev up
