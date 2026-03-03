import sys
import json
import os

def callback(key,value):
        if key == 'Virtual Drive':
                value = value.split(' ',1)[0]
        if key == 'PD':
                value = value.split(' ',1)[0]
        return value
def main():


	result_dict = dict()
	list_element = list()
        #da= os.popen("/opt/MegaRAID/MegaCli/MegaCli64 -ldpdinfo -aALL -NoLog | grep -e '\(DISK GROUP:\)\|\(Physical Disk:\)\|\(Device Id:\)\|\(PD Type:\)\|\(Device Speed:\)\|\(RAID Level\)\|\(Virtual Drive:\)\|\(^Size\)\|\(^Firmware state:\)\|\(^PD\)'")
#        da= os.popen("/opt/MegaRAID/MegaCli/MegaCli64 -ldpdinfo -aALL -NoLog | grep -e '\(DISK GROUP:\)\|\(Physical Disk:\)\|\(Device Id:\)\|\(RAID Level\)\|\(Virtual Drive:\)\|\(^Size\)\|\(^PD:\)'")
	da= os.popen("/opt/FiMo3/common/utils/runcached.py -c 300 arcconf getconfig 1 PD |grep -e '\(State\)\|\(Vendor\)\|\(Device #\)\|\(Total Size\)\|\(Model\)\|\(Channel #\)\|\(Reported Location\)\|\(Transfer Speed\)\|\(SSD\)\|\(Serial number\)\|\(Rotational Speed\)'")

	f = da.readlines() #block / wait
#	print f

	level = {'Channel':0,'Device':1}
	keys = level.keys()
	d = {}
	d[0] = {}
	L=-1

	for line in f:
		#print line
		if 'Channel' in line:
			key, value = [ x.strip() for x in line.split('#',1)]
			value = value.replace(':',"")
		elif 'Device' in line:
			key, value = [ x.strip() for x in line.split('#',1)]	
		else:
			key, value = [ x.strip() for x in line.split(':',1)]
		#print key
		#print value
		if key in keys :
			#print "is key"
			L = level[key]
			d[L+1] = {}
			d[L+1]["_Index"] = callback(key,value)
			if( d[L].get(key) == None ):
				d[L][key] = []
			d[L][key].append(d[L+1])
	
		else:
			#print "no"
			d[L+1][key] = value

	app_json = json.dumps( d[0] )
	print( app_json )

#	json_str = json.loads(app_json)
#	services_list= json_str['Virtual Drive']
#	for e in services_list:
#		print e['_Index']
#		device_list= e['PD']
#		for i in device_list:
#			print i['_Index']
#			list_element_dict = dict()
#			list_element_dict["{#VID}"] = e["_Index"]
#			list_element_dict["{#PD}"] = i["_Index"]	
#			if "Device Id" in i:
#				list_element_dict["{#DID}"] = i["Device Id"]
#			list_element.append(list_element_dict)	

#	result_dict["data"] = list_element
#	result = json.dumps(result_dict)
#	print result


if __name__ == '__main__':
    main()

