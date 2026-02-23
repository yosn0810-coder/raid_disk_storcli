import sys
import json
import os
import xml.etree.ElementTree as ET
import json;

def pythonXmlToJson(disk_type,channel,id):
        defs={'1':'SmartStats','0':'SASSmartStats'}
#	print defs[disk_type]
	da= os.popen("/opt/FiMo3/common/utils/runcached.py -c 300 arcconf getsmartstats 1")
	

        f = da.read() #block / wait
        s1_f=f.replace('-',' ')
        s2_f=s1_f.replace('Command completed successfully.',' ')
        s3_f=s2_f.replace('SMART STATS FOR SAS:',' ')
        s4_f=s3_f.replace('SMART STATS FOR SATA:',' ')
        s5_f=s4_f.replace('Controllers found: 1',' ')
#        print s5_f
        xmlStr1= "<test>"+s5_f+"</test>"

#       root = ET.fromstring(xmlStr)
        root = ET.fromstring(xmlStr1)
        #print root1.tag        
#       print  root.tag
#       print root.attrib
	list_element_dict = dict()
        for child in root:
		if child.tag==defs[disk_type]:
#	                print child.tag, child.attrib
	                for child_child in child:
#	                        print child_child.tag, child_child.attrib['id'],child_child.attrib['channel']
				if child_child.attrib['id']==id and child_child.attrib['channel']==channel:
		                        for child_child_child in child_child:
#		                                print  child_child_child.attrib
						if disk_type == "0":
							list_element_dict[child_child_child.attrib['name'].replace(" ", "")]=child_child_child.attrib['Value']	
						elif disk_type == "1":
                                                        list_element_dict[child_child_child.attrib['name'].replace(" ", "")]=child_child_child.attrib['rawValue']

	print(json.dumps(list_element_dict))
							
#       convertedDict = xmltodict.parse(xmlStr);
#       jsonStr = json.dumps(convertedDict, indent=1);
#       print "jsonStr=",jsonStr;

###############################################################################
if __name__=="__main__":
    pythonXmlToJson(sys.argv[1],sys.argv[2],sys.argv[3]);

