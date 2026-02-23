import sys
import json
import os
import requests
import base64

def callback(key,value):
	if key == 'Virtual Drive':
		value = value.split(' ',1)[0]
	return value
def main():


	result_dict = dict()
	list_element = list()
	post_list_element = list()
	da= os.popen("/opt/MegaRAID/MegaCli/MegaCli64 -PDList -aALL -NoLog | grep -e '\(DISK GROUP:\)\|\(Physical Disk:\)\|\(Device Id:\)\|\(PD Type:\)\|\(Device Speed:\)\|\(RAID Level\)\|\(Virtual Drive:\)\|\(^Size\)\|\(^Firmware state:\)\|\(^Enclosure Device ID:\)\|\(^Slot Number:\)'")

	f = da.readlines() #block / wait
#	print f

	level = {'Enclosure Device ID':0}
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
#	print( app_json )
	#return 0
	json_str = json.loads(app_json)
	services_list= json_str['Enclosure Device ID']
	for e in services_list:
		post_list_element_dict = dict()
		post_list_element_dict["key"]="fimo.device.speed["+e["Device Id"]+"]"
		post_list_element_dict["value"]=e["Device Speed"]
		post_list_element.append(post_list_element_dict)
        #for e in services_list:
                post_list_element_dict = dict()
                post_list_element_dict["key"]="fimo.device.firmwarestate["+e["Device Id"]+"]"
                post_list_element_dict["value"]=e["Firmware state"]
		post_list_element.append(post_list_element_dict)
        #for e in services_list:
                post_list_element_dict = dict()
                post_list_element_dict["key"]="fimo.device.pdtype["+e["Device Id"]+"]"
                post_list_element_dict["value"]=e["PD Type"]
                post_list_element.append(post_list_element_dict)
	

	
	result = json.dumps(post_list_element)
#	print result


	data = result
#data = [{"key":"fimo.device.speed[18]","value":"6.0Gb/s"}]
	access_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJIb3N0IjoiRGlza19jb21wdXRlNjQiLCJTZXJ2aWNlSVAiOiIxMC4yMTQuNjcuOTMiLCJTZXJ2aWNlUG9ydCI6IjgwIn0.DZQRRYY1qlfa7GSls3DnbuIqE7xoNrGE44VUR88qYXE"


 	token = access_token.split('.')
	a=token[1]
	missing_padding = 4 - len(a) % 4
	if missing_padding:
		a += b'=' * missing_padding
	b = base64.b64decode(a)
	json_str = json.loads(b)
	url = "http://"+json_str["ServiceIP"]+":"+json_str["ServicePort"]+"/rest/service/sendIBData"




	#url = "http://10.214.67.93/rest/service/sendIBData"
	result = requests.post(url,
	      headers={'Content-Type':'application/json',
               'Authorization': 'Bearer {}'.format(access_token)},data=data,verify=False)
	#print result.json()
	print(result.text)




if __name__ == '__main__':
    main()
