#!/bin/bash

case "$2" in
    CONNECTED)
      # ping www.google.com -c 8
      echo "$1 $2" >> /tmp/joseph.tmp
      echo "$WPA_CTRL_DIR $WPA_ID $WPA_ID_STR" >> /tmp/wpa.tmp
      echo $(date)
      echo $(iwgetid -a -r) >> /tmp/ap.tmp
      notify-send -t 1 "WPA supplicant: connection established";
      # bash /home/josephlee/raven/netest/tools/killchain.sh $1
      sleep 0.1
      # $1 is network inteface
      sudo dhclient -4 -cf /home/josephlee/raven/netest/conf/dhclient.conf -v $1
      # sudo ip route del $(sudo ip route | grep "wlan1")
      # sudo ip route del default via 10.224.0.1 dev wlan1

      # sleep 0.1
      # sudo ip route del $(sudo ip route | grep "wlan1")
      # sudo ip route add default via 10.224.0.1 dev wlan1 metric 230

      # kill old dhcp...
      echo "my pid ... $$"
      for pid in $(sudo ps -ef | grep 'dh' | grep 'wlan1' | awk '{print $2}');
      do
        if [ "$pid" -lt "$$" ]; then
          echo "MUST kill $pid"
          echo "$(sudo kill $pid)"
        fi
      done

      echo "bye bye $@"
      exit
      ;;
    DISCONNECTED)
      echo "$1 $2 $$" >> /tmp/joseph.tmp
      # notify-send "WPA supplicant: connection lost";
      # bash /home/josephlee/raven/netest/tools/killchain.sh
      # sleep 1
      ;;
esac
