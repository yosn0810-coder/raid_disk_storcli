#!/usr/bin/python
# -*- coding: UTF-8 -*-
from __future__ import print_function, division

import os
import subprocess
import json
import re
import zlib
import base64

class NodeData:
    def __init__(self):
        self.WORKDIR = os.path.dirname(os.path.realpath(__file__))
        self.KEYFILE = os.path.join(self.WORKDIR, "Raid_Disk_Data.key")
        self.PROCCOUNT = 5
        self.lock = os.path.basename(__file__) + ".lock"
        self.metrics = {}

    # 替代 commands.getstatusoutput (Python2/3 通用)
    def getstatusoutput(self, cmd):
        try:
            p = subprocess.Popen(cmd, shell=True,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
            out, err = p.communicate()

            if isinstance(out, bytes):
                out = out.decode("utf-8", "ignore")
            return p.returncode, out.strip()
        except Exception as e:
            return 1, str(e)

    def run(self):

        # 一般 Item
        cmd = (
            "cat %s | grep -v '^@' | "
            "xargs -I{} -P %d sh -c 'ret=$(zabbix_get -s 127.0.0.1 -p 20050 -k {} | sed -r \"s/%%/%%%%/g\"); "
            "cnt=0; while ! mkdir \"%s\"; do sleep 0.01; cnt=$((cnt+1)); "
            "if [[ $cnt -gt 500 ]]; then break; fi; done; "
            "printf \"{}{=BEGIN=}$ret{=END=}\n\"; rmdir \"%s\";' 2>/dev/null"
            % (self.KEYFILE, self.PROCCOUNT, self.lock, self.lock)
        )

        status, output = self.getstatusoutput(cmd)

        match = re.findall(r'(.+?){=BEGIN=}(.+?){=END=}', output, re.DOTALL)
        for k in match:
            self.metrics[k[0].strip()] = k[1]

        # LLD Rule
        with os.popen("cat %s | grep '^@'" % self.KEYFILE, "r") as lld:
            while True:
                rKey = lld.readline()
                if not rKey:
                    break

                rKey = rKey.strip()
                if not rKey:
                    continue

                self.lldHandler(rKey[1:])

        packagedata = json.dumps(self.metrics)
        self.packagegather2(packagedata)

    def packagegather2(self, data):
        hresult_dict = {}
        result_dict = {}
        list_element = []

        dict_json = json.loads(data)

        for key in dict_json:
            list_element.append({"k": key, "v": dict_json[key]})
        compressed_data = zlib.compress(json.dumps(list_element).encode('utf-8'))
        compress_str = base64.b64encode(compressed_data).decode('utf-8')

        result_dict["data"] = compress_str
        hresult_dict["version"] = "2.0"
        hresult_dict["type"] = "compress"
        result_dict["gather.metadata"] = hresult_dict

        print(json.dumps(result_dict))

    def lldHandler(self, rKey):

        lldFile = "%s/%s.lld" % (self.WORKDIR, rKey)

        if not os.path.isfile(lldFile):
            return

        with open(lldFile, "r") as f:
            config = f.read().strip()

        # --- Filter ---
        filter = {}
        match = re.findall(r'^@([^=]+)=(.+)$', config, re.MULTILINE)
        for x in match:
            key, pattern = x[0], x[1]
            filter.setdefault(key, []).append(re.compile(pattern))

        # --- Item Prototype ---
        lldTemplate = ""
        match = re.findall(r'^([^@]+)$', config, re.MULTILINE)
        for x in match:
            lldTemplate += x

        # --- Get LLD data ---
        cmd = "zabbix_get -s 127.0.0.1 -p 20050 -k %s" % rKey
        status, output = self.getstatusoutput(cmd)

        self.metrics[rKey] = output

        try:
            lldData = json.loads(output)
        except:
            return

        items = lldData.get("data", [])

        allKeys = ""

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

        # --- Execute allKeys ---
        if not allKeys.strip():
            return

        cmd = (
            "xargs -I{} -P %d sh -c 'ret=$(zabbix_get -s 127.0.0.1 -p 20050 -k {} | sed -r \"s/%%/%%%%/g\"); "
            "cnt=0; while ! mkdir \"%s\"; do sleep 0.01; cnt=$((cnt+1)); "
            "if [[ $cnt -gt 500 ]]; then break; fi; done; "
            "printf \"{}{=BEGIN=}$ret{=END=}\n\"; rmdir \"%s\";' 2>/dev/null"
            % (self.PROCCOUNT, self.lock, self.lock)
        )

        p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        outs, errs = p.communicate(input=allKeys.encode('utf-8'))

        if isinstance(outs, bytes):
            outs = outs.decode('utf-8', 'ignore')

        match = re.findall(r'(.+?){=BEGIN=}(.+?){=END=}', outs, re.DOTALL)
        for k in match:
            self.metrics[k[0].strip()] = k[1]


if __name__ == '__main__':
    n = NodeData()
    n.run()
