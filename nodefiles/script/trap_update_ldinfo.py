#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import json
import os
import subprocess
import base64


def raidchange(argument):
    # switcher = {
    #     "Primary-0, Secondary-0, RAID Level Qualifier-0": "Raid-0",
    #     "Primary-1, Secondary-0, RAID Level Qualifier-0": "Raid-1",
    #     "Primary-5, Secondary-0, RAID Level Qualifier-3": "Raid-5",
    #     "Primary-6, Secondary-0, RAID Level Qualifier-3": "Raid-6",
    #     "Primary-1, Secondary-3, RAID Level Qualifier-0": "Raid-10"
    # }

    switcher = {
        "Primary-0, Secondary-0, RAID Level Qualifier-0": "0",
        "Primary-1, Secondary-0, RAID Level Qualifier-0": "1",
        "Primary-5, Secondary-0, RAID Level Qualifier-3": "5",
        "Primary-6, Secondary-0, RAID Level Qualifier-3": "6",
        "Primary-1, Secondary-3, RAID Level Qualifier-0": "10"
    }

    return switcher.get(argument, "nothing")


def callback(key, value):
    if key == 'Virtual Drive':
        value = value.split(' ', 1)[0]
    if key == 'PD':
        value = value.split(' ', 1)[0]
    return value


def main():
    if len(sys.argv) < 2:
        print("Usage: {} <VID>".format(sys.argv[0]))
        sys.exit(1)

    vid = sys.argv[1]

    cmd = "/opt/MegaRAID/storcli/storcli64 /c0 /vall show all J"

    content = subprocess.Popen(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout, stderr = content.communicate()

    if content.returncode != 0:
        print(stderr.decode())
        sys.exit(2)

    json_str = json.loads(stdout.decode())
    controller = json_str["Controllers"][0]["Response Data"]

    properties_key = "VD" + vid + " Properties"
    disk_path = controller[properties_key]["OS Drive Name"].split('/')

    ld_key = "/c0/v" + vid
    raidlevel = controller[ld_key][0]["TYPE"]
    raidsize = controller[ld_key][0]["Size"]
    raidstate = controller[ld_key][0]["State"]

    list_element_dict = {}
    list_element_dict["raidlevel"] = raidlevel
    list_element_dict["raidsize"] = raidsize
    list_element_dict["raidstate"] = raidstate
    list_element_dict["raidpath"] = disk_path[2]

    result = json.dumps(list_element_dict)
    print(result)


if __name__ == '__main__':
    main()

