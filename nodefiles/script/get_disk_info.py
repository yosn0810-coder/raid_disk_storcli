import sys
import json
import os
import re
import codecs
import subprocess
info= os.popen("python /opt/FiMo3/raid_disk_storcli/nodefiles/script/lld_disk.py")
res=info.read()

json_str = json.loads(res)
r_info = json_str['data']
match = next(d for d in r_info if d['{#NAME}'] == sys.argv[1])

list_element_dict = dict()
list_element_dict["MOEL"] = match['{#MOEL}']
list_element_dict["VENDER"] = match['{#VENDER}']
list_element_dict["SIZE"] = match['{#SIZE}']
list_element_dict["ISRAID"] = match['{#ISRAID}']

print(json.dumps(list_element_dict))
