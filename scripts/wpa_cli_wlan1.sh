#!/bin/bash

case "$2" in
    CONNECTED)
      echo "$1 $2" >> /tmp/joseph.tmp
      echo "$WPA_CTRL_DIR $WPA_ID $WPA_ID_STR" >> /tmp/wpa.tmp
      echo $(date)
      echo $(iwgetid -a -r) >> /tmp/ap.tmp
      notify-send -t 1 "WPA supplicant: connection established";

      # $1 is network inteface
      sudo dhclient -4 -cf /etc/dhcp/vnperf-dhclient.conf -v $1

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
      ;;
esac
