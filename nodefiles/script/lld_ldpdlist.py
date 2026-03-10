import os
import json
import subprocess

def callback(key, value):
    if key == 'Virtual Drive':
        value = value.split(' ', 1)[0]
    if key == 'PD':
        value = value.split(' ', 1)[0]
    return value

def main():
    result_dict = dict()
    list_element = list()

    try:
        content = subprocess.Popen(
            "/opt/MegaRAID/storcli/storcli64 /c0 /vall show J", 
            shell=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE
        )
        stdout, stderr = content.communicate()

        if stderr:
            print(f"Error: {stderr.decode('utf-8')}", file=sys.stderr)
            result_dict["data"] = []
            print(json.dumps(result_dict))
            return

        json_str = json.loads(stdout)
        controllers = json_str.get("Controllers", [])

        if not controllers or "Response Data" not in controllers[0] or "Virtual Drives" not in controllers[0]["Response Data"]:
            result_dict["data"] = []
            print(json.dumps(result_dict))
            return

        VirtualDrives = controllers[0]["Response Data"]["Virtual Drives"]

        for vd in VirtualDrives:
            dgvd = vd["DG/VD"].split('/')
            vid = dgvd[1]

            content = subprocess.Popen(
                "/opt/MegaRAID/storcli/storcli64 /c0 /vall show all J", 
                shell=True, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE
            )
            stdout, stderr = content.communicate()

            if stderr:
                print(f"Error: {stderr.decode('utf-8')}", file=sys.stderr)
                continue

            json_str = json.loads(stdout)
            controller = json_str["Controllers"][0]["Response Data"]

            PDstatusname = f"PDs for VD {vid}"
            PDstatus = controller.get(PDstatusname, [])

            Properties = f"VD{vid} Properties"
            disk_path = controller.get(Properties, {}).get("OS Drive Name", "").split('/')

            for PDs in PDstatus:
                DID = PDs["DID"]
                PD = PDs["EID:Slt"].split(':')

                list_element_dict = dict()
                list_element_dict["{#VID}"] = vid
                list_element_dict["{#DID}"] = str(DID)
                list_element_dict["{#PD}"] = PD[1]
                list_element_dict["{#VIDDKPATH}"] = disk_path[2] if len(disk_path) > 2 else ""
                list_element.append(list_element_dict)

    except Exception as e:
        print(f"Exception occurred: {str(e)}", file=sys.stderr)
        result_dict["data"] = []
        print(json.dumps(result_dict))
        return

    result_dict["data"] = list_element
    result = json.dumps(result_dict)
    print(result)

if __name__ == "__main__":
    main()
