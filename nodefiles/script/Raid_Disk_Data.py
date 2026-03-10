#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import os
import subprocess
import json
import re

class NodeData:
    def __init__(self):
        self.WORKDIR = os.path.dirname(os.path.realpath(__file__))
        self.KEYFILE = self.WORKDIR + '/Raid_Disk_Data.key'
        self.PROCCOUNT = 5
        self.lock = os.path.basename(__file__) + ".lock"
        self.metrics = {}

    # 替代 commands.getstatusoutput
    def getstatusoutput(self, cmd):
        try:
            result = subprocess.run(cmd, shell=True, text=True, capture_output=True)
            return result.returncode, result.stdout.strip()
        except Exception as e:
            return 1, str(e)

    def run(self):
        # 一般 Item
        # status, output = self.getstatusoutput(
            # f"cat {self.KEYFILE} | grep -v '^@' | xargs -I{{}} -P {self.PROCCOUNT} "
            # f"sh -c 'ret=$(zabbix_get -s 127.0.0.1 -p 20050 -k {{}} | sed -r \"s/%/%%/g\"); "
            # f"cnt=0; while ! mkdir \"{self.lock}\"; do sleep 0.01; cnt=$(( $cnt + 1 )); "
            # f"if [[ $cnt -gt 500 ]]; then break; fi; done; "
            # f"printf \"{{}}{=BEGIN=}$ret{{=END=}}\n\"; rmdir \"{self.lock}\";' 2>/dev/null"
        # )


        status, output = self.getstatusoutput("cat " + self.KEYFILE + " | grep -v '^@' | xargs -I{} -P " + str(self.PROCCOUNT) + " sh -c 'ret=$(zabbix_get -s 127.0.0.1 -p 20050 -k {} | sed -r \'s/%/%%/g\'); cnt=0; while ! mkdir \"" + self.lock + "\"; do sleep 0.01; cnt=$(( $cnt + 1 )); if [[ $cnt -gt 500 ]]; then break; fi; done; printf \"{}{=BEGIN=}$ret{=END=}\n\"; rmdir \"" + self.lock + "\";' 2>/dev/null")        
        
        
        match = re.findall(r'(.+?){=BEGIN=}(.+?){=END=}', output, re.DOTALL)
        for k in match:
            self.metrics[k[0].strip()] = k[1]

        # LLD Rule
        with subprocess.Popen(f"cat {self.KEYFILE} | grep '^@'", shell=True, text=True, stdout=subprocess.PIPE) as lld:
            while True:
                rKey = lld.stdout.readline().strip()
                if not rKey:
                    break
                self.lldHandler(rKey[1:])

        print(json.dumps(self.metrics))

    def lldHandler(self, rKey):
        lldFile = f"{self.WORKDIR}/{rKey}.lld"
        if not os.path.isfile(lldFile):
            return

        with open(lldFile, "r") as f:
            config = f.read().strip()

        # 获取 LLD File 内的过滤条件
        filter = {}
        match = re.findall(r'^@([^=]+)=(.+)$', config, re.MULTILINE)
        for x in match:
            if x[0] in filter:
                filter[x[0]].append(re.compile(x[1]))
            else:
                filter[x[0]] = [re.compile(x[1])]

        # 获取 LLD File 内 Item Prototype
        lldTemplate = ''
        match = re.findall(r"^([^@]+)$", config, re.MULTILINE)
        for x in match:
            lldTemplate += x





        print(rKey)
        status, output = self.getstatusoutput(f"zabbix_get -s 127.0.0.1 -p 20050 -k {rKey}")
        self.metrics[rKey] = output
        lldData = json.loads(output)
        items = lldData["data"]

        allKeys = ''
        for item in items:
            itemKeys = lldTemplate
            found = True
            for k in item:
                if found and k in filter:
                    for pattern in filter[k]:
                        if not pattern.match(str(item[k])):
                            found = False
                            break

                if found:
                    itemKeys = itemKeys.replace(k, str(item[k]))

            if found:
                allKeys += itemKeys + "\n"



        p = subprocess.Popen(["xargs -I{} -P " + str(self.PROCCOUNT) + " sh -c 'ret=$(zabbix_get -s 127.0.0.1 -p 20050 -k {} | sed -r \'s/%/%%/g\'); cnt=0; while ! mkdir \"" + self.lock + "\"; do sleep 0.01; cnt=$(( $cnt + 1 )); if [[ $cnt -gt 500 ]]; then break; fi; done; printf \"{}{=BEGIN=}$ret{=END=}\n\"; rmdir \"" + self.lock + "\";' 2>/dev/null"], stdout=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
        outs, errs = p.communicate(input=allKeys.encode('utf-8'))  
        outs = outs.decode('utf-8')  
        match = re.findall(r'(.+?){=BEGIN=}(.+?){=END=}', outs, re.DOTALL)
        for k in match:
            self.metrics[k[0].strip()] = k[1]











if __name__ == '__main__':
    n = NodeData()
    n.run()
