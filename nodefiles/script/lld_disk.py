#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import json
import os
import subprocess
import re

def parse_lsblk_line(line):
    """Parses a line from lsblk -P output."""
    # Example: NAME="sda" VENDOR="ATA" SIZE="500107862016" MODEL="WDC WD5000AAKX-0" HCTL="0:0:0:0" TRAN="sata"
    pattern = r'(\w+)="([^"]*)"'
    return dict(re.findall(pattern, line))

def main():
    script_dir = os.path.dirname(os.path.realpath(__file__))
    runcached_path = os.path.join(script_dir, "runcached.py")

    result_dict = {"data": []}

    try:
        # Get lsblk info in Pair format
        cmd = ["lsblk", "-d", "-o", "NAME,VENDOR,SIZE,MODEL,HCTL,TRAN", "-b", "-P", "-n"]
        output = subprocess.check_output(cmd, text=True)
    except Exception as e:
        # Fallback to older method if -P is not supported or other errors occur
        try:
            cmd = ["lsblk", "-d", "-o", "NAME,VENDOR,SIZE,MODEL,HCTL,TRAN", "-b", "-r", "-n"]
            output = subprocess.check_output(cmd, text=True)
            # Simple space splitting for raw format
            lines = output.splitlines()
            output_lines = []
            for line in lines:
                parts = line.split()
                if len(parts) >= 1:
                    # Construct pseudo-pairs for our parser
                    pseudo = f'NAME="{parts[0]}"'
                    if len(parts) > 1: pseudo += f' VENDOR="{parts[1]}"'
                    if len(parts) > 2: pseudo += f' SIZE="{parts[2]}"'
                    if len(parts) > 3: pseudo += f' MODEL="{parts[3]}"'
                    if len(parts) > 4: pseudo += f' HCTL="{parts[4]}"'
                    if len(parts) > 5: pseudo += f' TRAN="{parts[5]}"'
                    output_lines.append(pseudo)
            output = "\n".join(output_lines)
        except Exception as inner_e:
            sys.stderr.write(f"Error running lsblk: {inner_e}\n")
            print(json.dumps(result_dict))
            return

    for line in output.splitlines():
        if not line.strip():
            continue
            
        data = parse_lsblk_line(line)
        name = data.get("NAME", "").replace('\\x20', ' ')
        vendor = data.get("VENDOR", "").replace('\\x20', '').strip()
        size = data.get("SIZE", "").replace('\\x20', ' ')
        model = data.get("MODEL", "").replace('\\x20', ' ').strip()
        hctl = data.get("HCTL", "").replace('\\x20', ' ')
        tran = data.get("TRAN", "").replace('\\x20', ' ')

        element = {
            "{#NAME}": name,
            "{#VENDOR}": vendor,
            "{#VENDER}": vendor, # Keeping misspelled key for backward compatibility
            "{#SIZE}": size,
            "{#MODEL}": model,
            "{#MOEL}": model,    # Keeping misspelled key for backward compatibility
            "{#HCTL}": hctl,
            "{#TRAN}": tran,
            "{#ISRAID}": "0",
            "{#DISK_TYPE}": "SINGLE"
        }

        # RAID detection logic
        is_raid = False
        if vendor in ["MSCC", "Adaptec"]:
            # Check arcconf
            try:
                # Use runcached to avoid repeated expensive calls
                r_cmd = f"python3 {runcached_path} -c 300 arcconf getconfig 1 LD"
                res = subprocess.check_output(r_cmd, shell=True, text=True, stderr=subprocess.DEVNULL)
                if f"Disk Name : /dev/{name}" in res:
                    is_raid = True
            except Exception:
                pass
        elif vendor in ["LSI", "AVAGO"]:
            # Check MegaRAID virtual disks
            try:
                vdlist_script = os.path.join(script_dir, "lld_vdlist.py")
                res_vd = subprocess.check_output([sys.executable, vdlist_script], text=True, stderr=subprocess.DEVNULL)
                vd_json = json.loads(res_vd)
                vd_data = vd_json.get("data", [])
                for vd in vd_data:
                    if vd.get("{#VIDDKPATH}") == name:
                        is_raid = True
                        break
            except Exception:
                pass

        if is_raid:
            element["{#ISRAID}"] = "1"
            element["{#DISK_TYPE}"] = "RAID"

        result_dict["data"].append(element)

    print(json.dumps(result_dict))

if __name__ == "__main__":
    main()
