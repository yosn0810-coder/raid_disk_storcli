#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import os
import json
import sys
import subprocess

def main():
    result_dict = {"data": []}
    list_element = []

    # Check if storcli exists
    storcli_path = "/opt/MegaRAID/storcli/storcli64"
    if not os.path.exists(storcli_path):
        # Also check /opt/MegaRAID/MegaCli/MegaCli64 if needed,
        # but this script specifically uses storcli J (JSON)
        print(json.dumps(result_dict))
        return

    try:
        # Get all virtual drives info in JSON
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

            properties_key = f"VD{vid} Properties"
            properties = response_data.get(properties_key, {})
            os_drive_name = properties.get("OS Drive Name", "")

            # OS Drive Name is typically /dev/sda
            short_name = os_drive_name.split('/')[-1]

            list_element.append({
                "{#VID}": vid,
                "{#VIDDKPATH}": short_name
            })

    except Exception:
        pass

    result_dict["data"] = list_element
    print(json.dumps(result_dict))

if __name__ == '__main__':
    main()
