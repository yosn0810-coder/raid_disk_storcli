#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import sys
import json
import os
import subprocess

def main():
    if len(sys.argv) < 2:
        sys.exit(1)

    disk_name = sys.argv[1]
    script_dir = os.path.dirname(os.path.realpath(__file__))
    lld_disk_path = os.path.join(script_dir, "lld_disk.py")

    try:
        # Run lld_disk.py to get all disks info
        output = subprocess.check_output([sys.executable, lld_disk_path], text=True)
        json_data = json.loads(output)
        disks = json_data.get('data', [])

        # Find the matching disk
        match = next((d for d in disks if d.get('{#NAME}') == disk_name), None)

        if not match:
            sys.exit(1)

        # Prepare result with keys matching what's expected by Zabbix items
        list_element_dict = {
            "MODEL": match.get('{#MODEL}', ''),
            "MOEL": match.get('{#MOEL}', ''), # backward compatibility
            "VENDOR": match.get('{#VENDOR}', ''),
            "VENDER": match.get('{#VENDER}', ''), # backward compatibility
            "SIZE": match.get('{#SIZE}', ''),
            "ISRAID": match.get('{#ISRAID}', '0'),
            "DISK_TYPE": match.get('{#DISK_TYPE}', 'SINGLE')
        }

        print(json.dumps(list_element_dict))

    except Exception:
        sys.exit(1)

if __name__ == "__main__":
    main()
