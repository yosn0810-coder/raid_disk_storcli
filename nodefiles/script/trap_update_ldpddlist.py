#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import json
import os
import subprocess
import base64


def raidchange(argument):
    # 原本顯示用 RAID 名稱（保留註解）
    # switcher = {
    #     "Primary-0, Secondary-0, RAID Level Qualifier-0": "Raid-0",
    #     "Primary-1, Secondary-0, RAID Level Qualifier-0": "Raid-1",
    #     "Primary-5, Secondary-0, RAID Level Qualifier-3": "Raid-5",
    #     "Primary-6, Secondary-0, RAID Level Qualifier-3": "Raid-6",
    #     "Primary-1, Secondary-3, RAID Level Qualifier-0": "Raid-10"
    # }

    # 實際回傳數字（你目前在用的）
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
    if len(sys.argv) < 3:
        print("Usage: {} <VID> <SLOT>".format(sys.argv[0]))
        sys.exit(1)

    vid = sys.argv[1]          # Virtual Drive ID
    slot = sys.argv[2]         # Slot number

    cmd = "/opt/MegaRAID/storcli/storcli64 /c0 /vall show all J"

    try:
        content = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = content.communicate()

        if content.returncode != 0:
            print("storcli error:", stderr.decode("utf-8"))
            sys.exit(2)

        json_str = json.loads(stdout.decode("utf-8"))

    except Exception as e:
        print("Failed to execute storcli:", str(e))
        sys.exit(3)

    controller = json_str["Controllers"][0]["Response Data"]

    PDstatusname = "PDs for VD " + vid

    if PDstatusname not in controller:
        print("No such Virtual Drive:", vid)
        sys.exit(4)

    PDstatus = controller[PDstatusname]

    for PDs in PDstatus:
        # EID:Slt 格式例如 "252:3"
        eid_slt = PDs.get("EID:Slt", "")
        if ":" not in eid_slt:
            continue

        eid, slt = eid_slt.split(":", 1)

        if slt == slot:
            # 只輸出 DID（維持你原本行為）
            print(PDs.get("DID", ""))
            return

    # 找不到對應 Slot
    print("")


if __name__ == '__main__':
    main()

