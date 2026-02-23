import sys
import json
import os
import re
import codecs
import subprocess
import argparse
from subprocess import check_output, CalledProcessError
import logging



def run(command):
    """ Run shell command.
    Args:
        command (str): command with attributes.
    Returns: command output, or False on error.
    """

    commands = command.split()

    try:
        res = check_output(commands, stderr=open(os.devnull, 'wb'))
        return res
    except CalledProcessError as e:
        if args.verbose:
            logger.error(e)
        return False

def col_value(data, key, index=0):
    """ Parse data as columns and returns 'value' for given 'key'.
    Args: 
        data    (str): raw output of 'arconf'.
        key     (str): key to search for.
        index   (int): if data consist of repeatable parts (multiple keys) - return N's key value. 
    Returns: 
        value of a key or False if key was not found.
    """

    col_index = 0

    for line in data.splitlines():
        columns = line.split(' : ')
        col_num = len(columns)
        col_key = columns[0].strip()
        if col_key == key:
            if col_index == index:
                if col_num == 2:
                    return columns[1].strip()
                elif col_num == 3:
                    return columns[1].strip() + ' ' + columns[2].strip()
            col_index += 1
                
    # Nothing found?
    return False

def last_value(data, key, index=0):
    """" Parse data to find the 'key' and returns the last digit/word in the line.
    Args:
        data    (str): raw output of 'arconf'.
        key     (str): key to search for.
        index   (int): if data consist of repeatable parts (multiple keys) - return N's key value.
    Returns:
        last digit/word in the line.
    """

    col_index = 0

    for line in data.splitlines():
        if key in line:
            if col_index == index:
                return line.split()[-1]

    # Nothing found?
    return False



#info= os.popen("/opt/FiMo3/common/utils/runcached.py -c 300 python /opt/FiMo/osv0/os/script/get_meacli_pdinfo.py")
#res=info.read()
##print res
#json_str = json.loads(res)
#all_mega_pd_info = json_str['Enclosure Device ID']




info= os.popen("/opt/FiMo3/common/utils/runcached.py -c 300 python /opt/FiMo3/raid_disk_storcli/nodefiles/script/lldsmartraid.py")
res=info.read()
#print res
json_str = json.loads(res)
all_pd_info = json_str

info= os.popen("/opt/FiMo3/common/utils/runcached.py -c 300 python /opt/FiMo3/raid_disk_storcli/nodefiles/script/lld_disk.py")
res=info.read()
#print res
json_str = json.loads(res)
r_info = json_str['data']
result_dict = dict()
list_element = list()
for e in r_info:
#	print e["{#VENDER}"]
    if e["{#VENDER}"] in "MSCC" or e["{#VENDER}"] in "Adaptec":
#		print "go MSCC"
        arcconf_info = os.popen("/opt/FiMo3/common/utils/runcached.py -c 300 arcconf getconfig 1 LD |grep 'Logical Device number'")
        arc_res=arcconf_info.readlines()
        for line in arc_res:
            ldnum = re.sub("[!A-Za-z]","",line)
            command = '/opt/FiMo3/common/utils/runcached.py -c 300 arcconf GETCONFIG 1 LD %d |grep "Disk Name"' %int(ldnum)
            arcconf_PD_info = os.popen(command)
            arc_pd_res=arcconf_PD_info.read()
            diskname= arc_pd_res.split(':')
            short_diskname=diskname[1].replace('/dev/', '').strip()
#			print short_diskname
#			print e["{#NAME}"]
            if e["{#NAME}"]==short_diskname:
#				print "match"
                ldnum = re.sub("[!A-Za-z]","",line)
                command = '/opt/FiMo3/common/utils/runcached.py -c 300 arcconf GETCONFIG 1 LD %d |grep "Present"|cut -d "(" -f2|cut -d ")" -f1' %int(ldnum)
                arcconf_PD_info = os.popen(command)
                arc_pd_res=arcconf_PD_info.readlines()
                for i in arc_pd_res:
                    get_i=i.strip()
                    pd_info=get_i.split(',')
                    channel_id= pd_info[3].strip().split(':')
                    device_id= pd_info[4].strip().split(':')
                    my_gen = (item for item in all_pd_info['Channel'] if item['_Index'] == channel_id[1])
                    for c_item in my_gen:
						#print c_item			
                        d_my_gen = (item for item in c_item['Device'] if item['_Index'] == device_id[1])				
                        for d_item in d_my_gen:
		#                                        print json.dumps(d_item)

                            list_element_dict = dict()
                            transtype= d_item["Transfer Speed"].split(' ')
							#print transtype[0]
                            if transtype[0]=="SAS":
                                transtype_value=0
                            elif transtype[0]=="SATA":
                                transtype_value=1
                            else:
                                transtype_value=2	
                            list_element_dict["{#TRANSTYPE}"] = transtype_value
                            if d_item["SSD"] == "No":
                                disktype=0
                            elif d_item["SSD"] == "Yes": 
                                disktype=1
                            else:
                                disktype=2
                            list_element_dict["{#DISKTYPE}"] = disktype
                            list_element_dict["{#DISKMODEL}"] = d_item["Model"]
                            list_element_dict["{#DISKCMD}"] = d_item["Reported Location"]
                            list_element_dict["{#DISKSN}"] = d_item["Serial number"]
                            list_element_dict["{#DISKCHID}"] = channel_id[1]
                            list_element_dict["{#DISKDEVID}"] = device_id[1]
                            list_element_dict["{#DISKLINKPATH}"]=short_diskname
                            list_element_dict["{#RAIDTYPE}"] = "MSCC"
                            list_element.append(list_element_dict)	


                break

#print json.dumps(list_element)

info= os.popen("/opt/FiMo3/common/utils/runcached.py -c 300 /opt/FiMo3/raid_disk_storcli/nodefiles/script/new_smartctl-disks-discovery.pl")
res=info.read()
#print res
json_str = json.loads(res)
oyther_pydisk=json_str["data"]
#print json.dumps(oyther_pydisk)
for smartlld in oyther_pydisk:
#	print smartlld
    if("megaraid" in smartlld["{#DISKCMD}"]):
        getdeviceid=smartlld["{#DISKCMD}"].split(',')
        smartlld["{#DISKDEVID}"] = getdeviceid[1]
        smartlld["{#RAIDTYPE}"]="LSI"
                
        info_vd= os.popen("/opt/FiMo3/common/utils/runcached.py -c 300 python /opt/FiMo3/raid_disk_storcli/nodefiles/script/lld_ldpdlist.py")
        res_vd=info_vd.read()
                #print res
        json_str_vd = json.loads(res_vd)
        vdinf=json_str_vd["data"]


        for checkvdid in vdinf:
            if checkvdid["{#DID}"]== getdeviceid[1]:
                command = 'dev=`ls -l /dev/disk/by-path/ | grep -E "scsi-[0-9]:[0-9]:%d:[0-9] " | awk \'{print($11)}\'`;echo ${dev##*\/}' %int(checkvdid["{#VID}"])
       			         #print command
                xdisk_path = os.popen(command)
                disk_path = xdisk_path.read().strip()
                smartlld["{#DISKLINKPATH}"]=disk_path
                break
            else:
                smartlld["{#DISKLINKPATH}"]=""

		#print all_mega_pd_info
#		for findes in all_mega_pd_info:
#			if findes["Device Id"]==getdeviceid[1]:
#				#print "find id"+":"+ findes["_Index"]+":"+findes["Slot Number"]
#				smartlld["{#ENID}"]=findes["_Index"]
#				smartlld["{#SLOTNUM}"]=findes["Slot Number"]
#				break
    else:	
        if("Adaptec" in smartlld["{#VENDOR}"]):
            break
        else:
            smartlld["{#RAIDTYPE}"]="SMARTCTL"
            disk_r_name = smartlld["{#DISKNAME}"].split("/")[2]
			
            for e in r_info:
                if e["{#NAME}"] == disk_r_name:
                    smartlld["{#DISKRNAME}"]=e["{#NAME}"]
                    smartlld["{#DISKHCTL}"]=e["{#HCTL}"]
                    smartlld["{#DISKLINKPATH}"]=e["{#NAME}"]
                    break
		
    list_element.append(smartlld)
	
result_dict = dict()	
result_dict["data"] = list_element

print json.dumps(result_dict)



#	        res = run(command)
#		print res
#	        if res:
#	            value = col_value(res, "Disk Name")
#	            if value:
#        	        print value		
#match = next(d for d in r_info if d['{#NAME}'] == sys.argv[1])
#print match
#print json.dumps(match)


