#!/bin/bash
#disks=`ls -l /dev/sd* | awk '{print $NF}' | sed 's/[0-9]//g' | uniq`
disks=`cat /proc/diskstats|awk '{print $3}'|grep -E '^[a-z]+$'|sort|uniq 2>/dev/null`
amount=0
for disk in $disks
do
  let "amount++"
done
echo "$amount"

