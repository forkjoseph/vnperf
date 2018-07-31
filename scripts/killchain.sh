#!/usr/bin/env bash

while read -r line ; do
  echo "Processing $line"
  echo $(sudo kill $line)
done < <( sudo ps -aux | grep -E dhclient.*$1 | grep -v grep | awk '{print $2}')
