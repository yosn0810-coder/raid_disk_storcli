import sys
import json
import os
import re
import codecs
import subprocess
import argparse
from subprocess import check_output, CalledProcessError
import logging

info= os.popen("/opt/FiMo3/common/utils/runcached.py -c 300 python /opt/FiMo3/raid_disk_storcli/nodefiles/script/get_meacli_pdinfo.py")
res=info.read()
#print res
json_str = json.loads(res)
all_mega_pd_info = json_str['Enclosure Device ID']


for findes in all_mega_pd_info:
	if findes["Device Id"]==sys.argv[1]:
		print(findes["_Index"]+":"+findes["Slot Number"])
	#smartlld["{#ENID}"]=findes["_Index"]
	#smartlld["{#SLOTNUM}"]=findes["Slot Number"]

