import json
import os
import re

import bulk_cmd

def format_cdp_entries(file_path):
    with open(file_path, 'r') as f:
        cdp_entries = f.read()
        # Create a list of cdp entries string
        cdp_entries = cdp_entries.split("-------------------------")
        # Delete first element as empty
        return cdp_entries[1:]

def get_device_list(dir):
    device_list = []
    # Iterate through each file of the directory
    for entry in os.scandir("CDP"):
        # Check if the entry is file
        if entry.is_file():
            # Append name of the device
            device_list.append(entry.name.replace(".txt", ""))
    return device_list


def main():

    # Send commands in comandi.txt for devices in hosts.txt, output in /CDP/device_name
    #bulk_cmd.bulk_cmd("CDP")

    # Get list of devices based on the file in CDP Folder
    device_list = get_device_list("CDP")

    network_map = {}
    # Iterate through each device
    for device in device_list:
        i = 0
        neighbor_devices = {}
        # Build the path to the cdp entries file of the device
        cdp_entries = format_cdp_entries(os.path.join("CDP", f"{device}.txt"))
        network_map[device] = []
        # Iterate through each entry
        for cdp_entry in cdp_entries:
            # Get Device ID (Neighbor hostname)
            neighbor_hostname = re.findall(r"Device ID: (.+)", cdp_entry)[0]
            # Get Local interface
            local_interface = re.findall(r"Interface: (.+?),", cdp_entry)
            # Get remote interface
            remote_interface = re.findall(r"Port ID \(outgoing port\): (.+)", cdp_entry)

            # Control if neighbor device has already been seen
            if neighbor_hostname in neighbor_devices:
                # Append just local and remote interfaces to the device neighbor
                network_map[device][neighbor_devices[neighbor_hostname]]["Local Interface"].append(local_interface[0])
                network_map[device][neighbor_devices[neighbor_hostname]]["Remote Interface"].append(remote_interface[0])
            # If it hasn't been seen
            else:
                # Get Neighbor IP Address if found else None
                neighbor_address = re.findall(r"Entry address\(es\):\s*\n\s*IP address: ([0-9.]+)", cdp_entry)
                neighbor_address = neighbor_address[0] if neighbor_address else "None"
                # Get neighbor device model if found else Unkown
                neighbor_model = re.findall(r"Platform: (.+?),", cdp_entry)
                neighbor_model = neighbor_model[0] if neighbor_model else "Unknown"
                # Append the neighbor dictionary to the list of device's neighbors
                network_map[device].append({
                "Device ID": neighbor_hostname,
                "Neighbor Address": neighbor_address,
                "Local Interface": local_interface,
                "Remote Interface": remote_interface,
                "Neighbor Model": neighbor_model,
                })
                # Add the neighbor device to the dictionary of already seen devices
                neighbor_devices[neighbor_hostname] = i
                # Increment the index
                i += 1

    print(json.dumps(network_map, indent = 2))

if __name__ == '__main__':
    main()
