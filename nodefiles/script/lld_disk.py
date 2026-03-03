#!/usr/bin/env python
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

def get_output(cmd, is_shell=False):
    """Compatibility wrapper for subprocess.check_output."""
    try:
        if sys.version_info[0] >= 3:
            return subprocess.check_output(cmd, shell=is_shell, text=True)
        else:
            return subprocess.check_output(cmd, shell=is_shell)
    except Exception as e:
        sys.stderr.write("Error running command {0}: {1}\n".format(cmd, e))
        return ""

def main():
    script_dir = os.path.dirname(os.path.realpath(__file__))
    runcached_path = os.path.join(script_dir, "runcached.py")

    result_dict = {"data": []}

    # Get lsblk info in Pair format
    cmd = ["lsblk", "-d", "-o", "NAME,VENDOR,SIZE,MODEL,HCTL,TRAN", "-b", "-P", "-n"]
    output = get_output(cmd)

    if not output:
        # Fallback to older method
        cmd = ["lsblk", "-d", "-o", "NAME,VENDOR,SIZE,MODEL,HCTL,TRAN", "-b", "-r", "-n"]
        output = get_output(cmd)
        if output:
            lines = output.splitlines()
            output_lines = []
            for line in lines:
                parts = line.split()
                if len(parts) >= 1:
                    pseudo = 'NAME="{0}"'.format(parts[0])
                    if len(parts) > 1: pseudo += ' VENDOR="{0}"'.format(parts[1])
                    if len(parts) > 2: pseudo += ' SIZE="{0}"'.format(parts[2])
                    if len(parts) > 3: pseudo += ' MODEL="{0}"'.format(parts[3])
                    if len(parts) > 4: pseudo += ' HCTL="{0}"'.format(parts[4])
                    if len(parts) > 5: pseudo += ' TRAN="{0}"'.format(parts[5])
                    output_lines.append(pseudo)
            output = "\n".join(output_lines)

    if not output:
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
            "{#VENDER}": vendor,
            "{#SIZE}": size,
            "{#MODEL}": model,
            "{#MOEL}": model,
            "{#HCTL}": hctl,
            "{#TRAN}": tran,
            "{#ISRAID}": "0",
            "{#DISK_TYPE}": "SINGLE"
        }

        # RAID detection logic
        is_raid = False
        if vendor in ["MSCC", "Adaptec"]:
            r_cmd = '{0} {1} -c 300 arcconf getconfig 1 LD'.format(sys.executable, runcached_path)
            res = get_output(r_cmd, is_shell=True)
            if "Disk Name : /dev/{0}".format(name) in res:
                is_raid = True
        elif vendor in ["LSI", "AVAGO"]:
            try:
                vdlist_script = os.path.join(script_dir, "lld_vdlist.py")
                res_vd = get_output([sys.executable, vdlist_script])
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
