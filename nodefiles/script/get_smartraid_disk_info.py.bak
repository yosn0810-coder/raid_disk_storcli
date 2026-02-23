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


info= os.popen("/opt/FiMo3/common/utils/runcached.py -c 300 python /opt/FiMo3/raid_disk_storcli/nodefiles/script/lldsmartraid.py")
res=info.read()
#print res
list_element = list()
json_str = json.loads(res)
all_pd_info = json_str
my_gen = (item for item in all_pd_info['Channel'] if item['_Index'] == sys.argv[1])
for c_item in my_gen:
    #print c_item			
    d_my_gen = (item for item in c_item['Device'] if item['_Index'] == sys.argv[2])				
    for d_item in d_my_gen:
        list_element_dict = dict()
        transtype= d_item["Transfer Speed"].split(' ')
        if transtype[0]=="SAS":
            transtype_value=0
        elif transtype[0]=="SATA":
            transtype_value=1
        else:
            transtype_value=2	
        list_element_dict["TRANSTYPE"] = transtype_value
        if d_item["SSD"] == "No":
            disktype=0
            list_element_dict["DISKROTSP"] = d_item["Rotational Speed"]
        elif d_item["SSD"] == "Yes": 
            disktype=1
        else:
            disktype=2
        list_element_dict["DISKTYPE"] = disktype
        list_element_dict["DISKMODEL"] = d_item["Model"]
        list_element_dict["DISKCMD"] = d_item["Reported Location"]
        list_element_dict["DISKSN"] = d_item["Serial number"]
        list_element_dict["DISKCHID"] = sys.argv[1]
        list_element_dict["DISKTRANSP"] = d_item["Transfer Speed"]
        list_element_dict["DISKDEVSP"] = d_item["Transfer Speed"].split(' ')[1]+" "+d_item["Transfer Speed"].split(' ')[2]
        list_element_dict["DISKPDTYPE"] = d_item["Transfer Speed"].split(' ')[0]
        list_element_dict["DISKTOLSZ"] = d_item["Total Size"]
        list_element_dict["DISKSTATE"] = d_item["State"]
        
        list_element_dict["DISKDEVID"] = sys.argv[2]
        list_element_dict["RAIDTYPE"] = "MSCC"
        #list_element.append(list_element_dict)	
        break
	
print(json.dumps(list_element_dict))


