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
        host = re.findall(r"(?:[0-9]{1,3}\.){3}[0-9]{1,3}" ,cdp_entries[0])[0]
        return host, cdp_entries[1:]

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
    bulk_cmd.bulk_cmd("CDP")

    input("Commands sent, file created, input to continue...")
    # Get list of devices based on the file in CDP Folder
    device_list = get_device_list("CDP")

    network_links = list()
    i = 0
    # Iterate through each device
    for device in device_list:
        neighbor_devices = {}
        # Build the path to the cdp entries file of the device
        host, cdp_entries = format_cdp_entries(os.path.join("CDP", f"{device}.txt"))
        print(f"Going through entries of device {host}")
        # Iterate through each entry
        for cdp_entry in cdp_entries:
            # Get Device ID (Neighbor hostname)
            neighbor_hostname = re.findall(r"Device ID: (.+)", cdp_entry)[0]
            # Get Local interface
            local_interface = re.findall(r"Interface: (.+?),", cdp_entry)
            # Get remote interface
            remote_interface = re.findall(r"Port ID \(outgoing port\): (.+)", cdp_entry)
            # parameter used for link identification
            end_devices = tuple(sorted([device, neighbor_hostname]))

            # If device pair hasn't been seen
            if end_devices not in neighbor_devices:
                # Get Neighbor IP Address if found else None
                neighbor_address = re.findall(r"Entry address\(es\):\s*\n\s*IP address: ([0-9.]+)", cdp_entry)
                neighbor_address = neighbor_address[0] if neighbor_address else "None"
                
                # Append the neighbor dictionary to the list of device's neighbors
                network_links.append({
                "Devices": end_devices,
                f"{device}_ip": host,
                f"{neighbor_hostname}_ip" : neighbor_address,
                f"{device}_int" : local_interface,
                f"{neighbor_hostname}_int": remote_interface,
                })
                # Add the neighbor device to the dictionary of already seen devices
                neighbor_devices[end_devices] = i
                # Increment the index
                i += 1
            # Control if device pair has already been seen
            elif local_interface[0] not in network_links[neighbor_devices[end_devices]][f"{device}_int"]:
                # Append just local and remote interfaces to the device neighbor
                network_links[neighbor_devices[end_devices]][f"{device}_int"].append(local_interface[0])
                network_links[neighbor_devices[end_devices]][f"{neighbor_hostname}_int"].append(remote_interface[0])

    print(json.dumps(network_links, indent = 2))

if __name__ == '__main__':
    main()
