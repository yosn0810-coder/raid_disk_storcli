import sys
import json
import os
import re
import codecs
result_dict = dict()
list_element = list()
#da= os.popen("lsblk -d -o NAME,VENDOR,SIZE,MODEL,TRAN -r -n")
#da= os.popen("lsblk -d -o NAME,VENDOR,SIZE,MODEL -r -n")

#print sys.argv[1]


da= os.popen("/opt/FiMo3/common/utils/runcached.py -c 300 smartctl -a /dev/bus/0 -d megaraid,"+sys.argv[1]+"|awk '/Error/ {for(i=0;i<5;i++) {getline;print}}'|awk 'NR==5{print}'")
f = da.read()
#print f
sas_ecc_info=f.split();
#print sas_ecc_info[0];
#for line in f:
#       print line
#        blk_list = line.split();
        #for info in blk_list:  
#        name=blk_list[0].replace('\\x20', ' ')
#        vender=blk_list[1].replace('\\x20', '')
#        size=blk_list[2].replace('\\x20', ' ')
#        model=blk_list[3].replace('\\x20', ' ')
        #tran=blk_list[4].replace('\\x20', ' ')


list_element_dict = dict()
list_element_dict["ErrorsCorrectedByRewrites"]= sas_ecc_info[3].strip()
list_element_dict["WriteErrorsCorrectedByECCDelayed"]= sas_ecc_info[2].strip()
list_element_dict["WriteErrorsCorrectedByECCFast"]= sas_ecc_info[1].strip()
list_element_dict["TotalWriteErrorsCorrected"]= sas_ecc_info[4].strip()
list_element_dict["TotalUncorrectedWriteErrors"]= sas_ecc_info[7].strip()


da= os.popen("/opt/FiMo3/common/utils/runcached.py -c 300 smartctl -a /dev/bus/0 -d megaraid,"+sys.argv[1]+" |awk '/Error/ {for(i=0;i<5;i++) {getline;print}}'|awk 'NR==4{print}'")
f = da.read()
#print f
sas_ecc_info=f.split();
list_element_dict["ErrorsCorrectedByRereads"]= sas_ecc_info[3].strip()
list_element_dict["ReadErrorsCorrectedByECCDelayed"]= sas_ecc_info[2].strip()
list_element_dict["ReadErrorsCorrectedByECCFast"]= sas_ecc_info[1].strip()
list_element_dict["TotalReadErrorsCorrected"]= sas_ecc_info[4].strip()
list_element_dict["TotalUncorrectedReadErrors"]= sas_ecc_info[7].strip()
print(json.dumps(list_element_dict))
#        list_element.append(list_element_dict)
#result_dict["data"] = list_element
#result = json.dumps(result_dict)
#print result
