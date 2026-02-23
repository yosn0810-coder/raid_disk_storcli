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
result_dict = dict()
list_element = list()

arcconf_info = os.popen("/opt/FiMo3/common/utils/runcached.py -c 300 arcconf getconfig 1 LD |grep 'Logical Device number'")
arc_res=arcconf_info.readlines()
for line in arc_res:
	ldnum = re.sub("[!A-Za-z]","",line)




	command = '/opt/FiMo3/common/utils/runcached.py -c 300 arcconf GETCONFIG 1 LD %d |grep "Disk Name"' %int(ldnum)
	arcconf_PD_info = os.popen(command)
	arc_pd_res=arcconf_PD_info.read()
	diskname= arc_pd_res.split(':')
	short_diskname=diskname[1].replace('/dev/', '').strip()








#	command = '/opt/FiMo3/common/utils/runcached.py -c 300 arcconf GETCONFIG 1 LD %d |grep "Present"|cut -d "(" -f2|cut -d ")" -f1' %int(ldnum)
	command = '/opt/FiMo3/common/utils/runcached.py -c 300 arcconf GETCONFIG 1 LD %d |grep "Present"' %int(ldnum)	
	arcconf_PD_info = os.popen(command)
	arc_pd_res=arcconf_PD_info.readlines()
	for i in arc_pd_res:
		ld_deviceid=i.split(':')
	#	print ld_deviceid[0].strip()

		b= re.findall(r'[(](.*?)[)]',i.strip())
	#	print b[0]
		device_information=b[0]
		get_i=device_information.strip()
		pd_info=get_i.split(',')
		channel_id= pd_info[3].strip().split(':')
		device_id= pd_info[4].strip().split(':')
		list_element_dict = dict()		
		#list_element_dict["{#LDDEVICEID}"] = ld_deviceid[0].strip()
		list_element_dict["{#LDDEVICEID}"] = ld_deviceid[0].strip().split(" ")[1]
		list_element_dict["{#DISKCHID}"] = channel_id[1]
		list_element_dict["{#DISKDEVID}"] = device_id[1]
		list_element_dict["{#RAIDID}"] = ldnum.strip()
		list_element_dict["{#VIDDKPATH}"]=short_diskname
		list_element.append(list_element_dict)	


result_dict["data"] = list_element

print(json.dumps(result_dict))




