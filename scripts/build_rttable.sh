#!/usr/bin/env bash

declare -a NICS=("usb0" "usb1" "wlan1" "wlan0")
declare -a TABLES=("verizon" "sprint" "enwifi" "opwifi")
declare -a METRICS=("210" "220" "320" "20")

function help() {
  echo "USAGE: ./build_rttable.sh [interface | all | register]"
  exit
}

## required for the first time!
function register() {
# register the 'foo' table name and give it id 1
  sudo sh -c "echo '100 verizon' >> /etc/iproute2/rt_tables"
  sudo sh -c "echo '200 sprint' >> /etc/iproute2/rt_tables"
  sudo sh -c "echo '300 enwifi' >> /etc/iproute2/rt_tables"
  sudo sh -c "echo '400 opwifi' >> /etc/iproute2/rt_tables"
  cat /etc/iproute2/rt_tables
}

mask2cidr() {
	nbits=0
	IFS=.
	for dec in $1 ; do
			case $dec in
					255) let nbits+=8;;
					254) let nbits+=7;;
					252) let nbits+=6;;
					248) let nbits+=5;;
					240) let nbits+=4;;
					224) let nbits+=3;;
					192) let nbits+=2;;
					128) let nbits+=1;;
					0);;
					*) echo "Error: $dec is not recognised"; exit 1
			esac
	done
	echo "$nbits"
}


# @arg: pass name of interface to lookup
function find_index() {
  local target=$1
  local index=255
  for i in "${!NICS[@]}"; do 
    nic=${NICS[$i]}
    if [ $target == $nic ]; then
      index=$i
      break
    fi
  done
  return $index
}

function build() {
  local target=$1
  find_index $target
  local index=$? 
  if [ "$index" -gt "254" ]; then
    echo "[ERROR] not valid interface $target!"
    help
    exit
  fi

  local is_valid=true
  local nic=${NICS[$index]}
  local table=${TABLES[$index]}
  local metric=${METRICS[$index]}
  echo "===> $i] $nic in $table"
  # sudo ip rule del table $table
  sleep 0.1

  # $nic $ip_address $network_number $router
# get source ip
  src_ip=$2
  echo "src" $src_ip
# get subnetmask
  subnet=$3
  echo "subnet" $subnet
# get gw ip
  gw=$4
  echo "gw" $gw

  if [ -z "$src_ip" ] || [ -z "$gw" ] || [ -z "$subnet" ]; 
  then
    echo "***[ERROR] src_ip, gw, or subnet not detected for $nic***"
  else
    echo "setting up the rt_tables..."
    sleep 1.0
    # sudo ip route del default dev $nic
# setup routing table for 'table'
    # sudo ip route del $subnet dev $nic proto kernel scope link src $src_ip 
    echo "subnet..."
    echo "ip route add $subnet dev $nic src $src_ip table $table metric $metric"
    sudo ip route add $subnet dev $nic src $src_ip table $table metric $metric
    sleep 0.1

    echo "default..."
    # sudo ip route del default via $gw dev $nic
    # sudo ip route add default via $gw table $table
    # sudo ip route del default dev $nic
    echo $(ip route)
    sudo ip route add default via $gw dev $nic table "$table"
    sudo ip route add default via $gw dev $nic metric "$metric"
    sleep 0.1

    echo "table..."
# use routing table 'table' for address $src_ip
    sudo ip rule add from $src_ip table $table
    # if [ "wlan1" == "$nic" ]; then
    #   sudo ip route del default via $gw dev wlan1 
    # fi
    echo "done!"

    # ping 8.8.8.8 -I "$nic" -D -n -W 5 -c 5
  fi
  echo ""
  if [ "wlan0" == "$nic" ]; then
    sudo iw $nic set power_save off
  fi
}

function main() {
  if [ -z $1 ]; then
    help
  fi
  echo "$@"
  interface=$1
  ip_address=$2
  network_number=$3
  subnet_mask=$4
  router=$5

	numbits=$(mask2cidr $4)
  # echo "/$numbits"
  network_number="$network_number/$numbits"
  echo "Net: $network_number"

  if [ $1 == "all" ]; then
    for i in "${!NICS[@]}"; do 
      nic=${NICS[$i]}
      echo "not supported"
      # build $interface $ip_address $network_number $router
    done
  elif [ $1 == "register" ]; then
    register
    # main "all"
  else
    build $interface $ip_address $network_number $router
  fi
}

main "$@"
