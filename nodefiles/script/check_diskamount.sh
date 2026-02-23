#!/bin/bash
FILE=/opt/FiMo/paas_node/script/diff.txt
if [ -f $FILE ]
then
	/opt/FiMo/paas_node/script/discover_hddchk.sh > /opt/FiMo/paas_node/script/diff2.txt
	changeStr=$(diff /opt/FiMo/paas_node/script/diff.txt /opt/FiMo/paas_node/script/diff2.txt)
	if [[ $? -eq 0 ]]; then
		echo "no change"
	else
		echo "$changeStr"
	fi
	mv /opt/FiMo/paas_node/script/diff2.txt /opt/FiMo/paas_node/script/diff.txt
else
	/opt/FiMo/paas_node/script/discover_hddchk.sh > /opt/FiMo/paas_node/script/diff.txt
  echo "no change"

fi


