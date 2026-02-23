import sys
import json
import os
import re
import codecs
import subprocess
info= os.popen("/opt/FiMo3/common/utils/runcached.py -c 300 python /opt/FiMo3/raid_disk_storcli/nodefiles/script/lld_ld_disk.py")
res=info.read()
#print res
json_str = json.loads(res)
r_info = json_str['data']
#print r_info

match = next(d for d in r_info if d['{#LDDEVICEID}'] == sys.argv[1])
#print match
print(match['{#DISKCHID}']+":"+match['{#DISKDEVID}'])

