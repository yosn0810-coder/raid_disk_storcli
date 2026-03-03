import sys
import json
import os


def callback(key,value):
	if key == 'Virtual Drive':
		value = value.split(' ',1)[0]
	return value
def main():

	result_dict = dict()
	list_element = list()
	ldpd= os.popen("python /opt/FiMo3/raid_disk_storcli/nodefiles/script/ori_ldpdinfo.py").read()
	pd= os.popen("python /opt/FiMo3/raid_disk_storcli/nodefiles/script/ori_pdinfo.py").read()
#	print ldpd
#	print pd
        a = json.loads(ldpd)
        b = json.loads(pd)
#	print b
#        ldpd=a["Device Id"]
        pd=b['Device Id']
        pdp=json.dumps(pd)
        print pdp
	
	ldpd = a['Virtual Drive']	
        ldpdp=json.dumps(ldpd)
        print ldpdp
	

	for pdget in pd:
		print pdget['_Index']

	
	







	return 0


	a = json.loads(ldpd)
	b = json.loads(pd)
	ldpd=a['data']
	pd=b['data']
	fldpd=json.dumps(ldpd)
	print fldpd

	for pdget in pd:
		print pdget
		list_element_dict = dict()
		list_element_dict["{#DID}"] = pdget['{#DID}']
		list_element_dict["{#FS}"] = pdget['{#FS}']
		list_element_dict["{#DS}"] = pdget['{#DS}']
		list_element_dict["{#PDT}"] = pdget['{#PDT}']
		for ldpdget in ldpd:
			print ldpdget['{#DID}']
			if pdget['{#DID}'] ==ldpdget['{#DID}']:
				print "match"
				list_element_dict["{#VID}"] = ldpdget['{#VID}']
				list_element_dict["{#VDType}"] = 1
				break
			else:
				list_element_dict["{#VDType}"] = 0
		list_element.append(list_element_dict)	
	result_dict["data"] = list_element
	result = json.dumps(result_dict)
	print result				
if __name__ == '__main__':
    main()
