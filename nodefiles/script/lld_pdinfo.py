#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import os
import json
import sys
import subprocess

def main():
    result_dict = {"data": []}
    list_element = []

    storcli_path = "/opt/MegaRAID/storcli/storcli64"
    if not os.path.exists(storcli_path):
        print(json.dumps(result_dict))
        return

    try:
        # Get all info in JSON
        res = subprocess.run(
            [storcli_path, "/c0", "/vall", "show", "all", "J"],
            capture_output=True,
            text=True
        )

        if res.returncode != 0 or not res.stdout:
            print(json.dumps(result_dict))
            return

        json_data = json.loads(res.stdout)
        controllers = json_data.get("Controllers", [])

        if not controllers or "Response Data" not in controllers[0]:
            print(json.dumps(result_dict))
            return

        response_data = controllers[0]["Response Data"]
        virtual_drives = response_data.get("Virtual Drives", [])

        for vd in virtual_drives:
            dg_vd = vd.get("DG/VD", "").split('/')
            if len(dg_vd) < 2:
                continue
            vid = dg_vd[1]

            pd_status_name = f"PDs for VD {vid}"
            pd_list = response_data.get(pd_status_name, [])

            properties_key = f"VD{vid} Properties"
            os_drive_name = response_data.get(properties_key, {}).get("OS Drive Name", "")
            short_name = os_drive_name.split('/')[-1]

            for pd in pd_list:
                did = pd.get("DID", "")
                eid_slt = pd.get("EID:Slt", "").split(':')
                slot = eid_slt[1] if len(eid_slt) > 1 else ""

                list_element.append({
                    "{#VID}": vid,
                    "{#DID}": str(did),
                    "{#PD}": slot,
                    "{#DISKLINKPATH}": short_name
                })

    except Exception:
        pass

    result_dict["data"] = list_element
    print(json.dumps(result_dict))

if __name__ == '__main__':
    main()
