import sys
import json
import os
import re
import codecs
import subprocess
result_dict = dict()
list_element = list()
#da= os.popen("lsblk -d -o NAME,VENDOR,SIZE,MODEL,TRAN -r -n")
#da= os.popen("lsblk -d -o NAME,VENDOR,SIZE,MODEL -r -n")
da= os.popen("lsblk -d -o NAME,VENDOR,SIZE,MODEL,HCTL -r -n -b")
f = da.readlines()
for line in f:
    #print line
    try:
        blk_list = line.split();
        name=blk_list[0].replace('\\x20', ' ')
        vender=blk_list[1].replace('\\x20', '')
        size=blk_list[2].replace('\\x20', ' ')
        model=blk_list[3].replace('\\x20', ' ')
        HCTL=blk_list[4].replace('\\x20', ' ')
        list_element_dict = dict()
        list_element_dict["{#NAME}"]= name.strip()
        list_element_dict["{#VENDER}"] = vender.strip()
        list_element_dict["{#ISRAID}"] = "0"
        #print list_element_dict["{#VENDER}"]
        if list_element_dict["{#VENDER}"] == "MSCC" or list_element_dict["{#VENDER}"] == "Adaptec":

            disk_p = os.popen("/opt/FiMo3/common/utils/runcached.py -c 300 arcconf getconfig 1 LD |grep 'Disk Name'")
            all_disk_path_f = disk_p.readlines()
            for all_disk_path in all_disk_path_f:
                disk_path = all_disk_path.split(':')[1].strip()
                check_disk_path = disk_path.split('/')[2]
                if check_disk_path == list_element_dict["{#NAME}"]:
                    list_element_dict["{#ISRAID}"] = "1"
        elif list_element_dict["{#VENDER}"] == "LSI" or list_element_dict["{#VENDER}"] == "AVAGO":	
            content=subprocess.Popen("python /opt/FiMo3/raid_disk_storcli/nodefiles/script/lld_vdlist.py",shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)        
            stdout, stderr = content.communicate()
            json_str = json.loads(stdout)
            vdinfoarray=json_str["data"]
            for vdinfo in vdinfoarray:
                if vdinfo["{#VIDDKPATH}"] == list_element_dict["{#NAME}"]:
                    list_element_dict["{#ISRAID}"] = "1"                
            
            
            
            
            # lsi_p = os.popen("/opt/MegaRAID/MegaCli/MegaCli64 -LDInfo -Lall -aALL  |grep 'Virtual Drive:'")
            # r_all_disk_path = lsi_p.readlines()
            # for all_disk_path in r_all_disk_path:
                # value = all_disk_path.split(':',1)[1]
                # targetno=value.strip().split(' ')
                # command = 'dev=`ls -l /dev/disk/by-path/ | grep -E "scsi-[0-9]:[0-9]:%d:[0-9] " | awk \'{print($11)}\'`;echo ${dev##*\/}' %int(targetno[0])
                # xdisk_path = os.popen(command)
                # disk_path = xdisk_path.read().strip()
                # if disk_path == list_element_dict["{#NAME}"]:
                    # list_element_dict["{#ISRAID}"] = "1"
                    
                    
                    
                    
        list_element_dict["{#SIZE}"] = size.strip()
        list_element_dict["{#MOEL}"] = model.strip()
        list_element_dict["{#HCTL}"] = HCTL.strip()
        list_element.append(list_element_dict)
    except:
        pass


result_dict["data"] = list_element
result = json.dumps(result_dict)
print(result)
