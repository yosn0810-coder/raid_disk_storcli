#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import json
import os
# import requests
import base64


def callback(key, value):
    if key == 'Virtual Drive':
        value = value.split(' ', 1)[0]
    return value


def main():
    if len(sys.argv) < 2:
        print("Usage: {} <DeviceId>".format(sys.argv[0]))
        sys.exit(1)

    result_dict = {}
    list_element = []
    post_list_element = []

    cmd = (
        "/opt/MegaRAID/storcli/storcli64 /c0 /sall show all J | "
        "grep -e "
        "'\\(DISK GROUP:\\)\\|"
        "\\(Physical Disk:\\)\\|"
        "\\(Device Id:\\)\\|"
        "\\(PD Type:\\)\\|"
        "\\(Device Speed:\\)\\|"
        "\\(RAID Level\\)\\|"
        "\\(Virtual Drive:\\)\\|"
        "\\(^Size\\)\\|"
        "\\(^Firmware state:\\)\\|"
        "\\(^Enclosure Device ID:\\)\\|"
        "\\(^Slot Number:\\)'"
    )

    da = os.popen(cmd)
    f = da.readlines()

    level = {'Enclosure Device ID': 0}
    keys = level.keys()

    d = {}
    d[0] = {}
    L = -1

    for line in f:
        key, value = [x.strip() for x in line.split(':', 1)]

        if key in keys:
            L = level[key]
            d[L + 1] = {}
            d[L + 1]["_Index"] = callback(key, value)

            if d[L].get(key) is None:
                d[L][key] = []

            d[L][key].append(d[L + 1])
        else:
            d[L + 1][key] = value

    app_json = json.dumps(d[0])
    json_str = json.loads(app_json)

    services_list = json_str.get('Enclosure Device ID', [])

    post_list_element_dict = {}

    for e in services_list:
        if e.get("Device Id") == sys.argv[1]:
            post_list_element_dict["DeviceSpeed"] = e.get("Device Speed", "")
            post_list_element_dict["Firmwarestate"] = e.get("Firmware state", "")
            post_list_element_dict["PDType"] = e.get("PD Type", "")
            post_list_element.append(post_list_element_dict)
            break

    result = json.dumps(post_list_element_dict)
    print(result)


if __name__ == '__main__':
    main()

