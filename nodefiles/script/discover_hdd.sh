
#!/bin/bash
#disks=`ls -l /dev/sd* | awk '{print $NF}' | sed 's/[0-9]//g' | uniq`
disks=`cat /proc/diskstats|awk '{print $3}'|grep -E '^[a-z]+$'|sort|uniq 2>/dev/null`


echo "{"
echo "\"data\":["

comma=""
for disk in $disks
do
echo "    $comma{\"{#DISKNAME}\":\"/dev/$disk\",\"{#SHORTDISKNAME}\":\"$disk\"}"
comma=","
done

echo "]"
echo "}"

