#!/usr/bin/env bash

echo "killing all dhclient!!"
sudo ps -ef | grep dh
sudo pkill dhclient
