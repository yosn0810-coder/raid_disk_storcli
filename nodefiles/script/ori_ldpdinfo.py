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
	da= os.popen("/opt/MegaRAID/MegaCli/MegaCli64 -ldpdinfo -aALL -NoLog | grep -e '\(DISK GROUP:\)\|\(Physical Disk:\)\|\(Device Id:\)\|\(RAID Level\)\|\(Virtual Drive:\)\|\(^Size\)\|\(^PD:\)'")

	f = da.readlines() #block / wait
	#print f

	level = {'Virtual Drive':0,'PD':1}
	keys = level.keys()
	d = {}
	d[0] = {}
	L=-1

	for line in f:
		#print line
		key, value = [ x.strip() for x in line.split(':',1)]
		if key in keys :
			L = level[key]
			d[L+1] = {}
			d[L+1]["_Index"] = callback(key,value)
			if( d[L].get(key) == None ):
				d[L][key] = []
			d[L][key].append(d[L+1])
	
		else:
			d[L+1][key] = value

	app_json = json.dumps( d[0] )
	print( app_json )

if __name__ == '__main__':
    main()
