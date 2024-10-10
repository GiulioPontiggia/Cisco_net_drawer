import bulk_cmd
import json
import os
import re

import networkx as nx
import matplotlib.pyplot as plt

def empty_cdp_folder():
    # List files in CDP folder
    files = os.listdir('CDP')
    # Remove each file
    for file in files:
        os.remove(os.path.join('CDP', file))

def list_cdp_entries(file_path):
    '''Read a file with cdp entries and return a list of all the entries'''
    with open(file_path, 'r') as f:
        cdp_entries = f.read()
        # Create a list of cdp entries string
        cdp_entries = cdp_entries.split("-------------------------")
        # Delete first element as empty
        host = re.findall(r'(?:[0-9]{1,3}\.){3}[0-9]{1,3}' ,cdp_entries[0])[0]
        return host, cdp_entries[1:]

def get_device_list(dir):
    '''Get device list from directory containing all cdp files'''
    device_list = []
    # Iterate through each file of the directory
    for entry in os.scandir(dir):
        # Check if the entry is file
        if entry.is_file():
            # Append name of the device
            device_list.append(entry.name.replace(".txt", ""))
    return device_list

def interface_shortener(interface_name):
    '''Return interface name shortened (instead of GigabitEthernet0/0/0 G0/0/0)'''
    # Takes the type of interface G for Gigabit, F for Fast...
    int_type = interface_name[0]
    # Takes number of interface through regex
    int_number = '/'.join(re.findall(r"(\d{1,3})(?=\/|$)", interface_name))
    return(f"{int_type}{int_number}")

def handle_cdp_entries(device_list):
    '''Handle cdp entries to create a list of all the network links'''
    network_links = list()
    i = 0
    # Iterate through each device
    for device in device_list:
        neighbor_devices = {}
        # Build the path to the cdp entries file of the device
        host, cdp_entries = list_cdp_entries(os.path.join("CDP", f"{device}.txt"))
        # Iterate through each entry
        for cdp_entry in cdp_entries:
            # Get Device ID (Neighbor hostname), remove domain by splitting in a list with . and takes just device name
            neighbor_hostname = re.findall(r"Device ID: (.+)", cdp_entry)[0].split('.')[0]
            # Get Local interface
            local_interface = interface_shortener(re.findall(r"Interface: (.+?),", cdp_entry)[0])
            # Get remote interface
            remote_interface = interface_shortener(re.findall(r"Port ID \(outgoing port\): (.+)", cdp_entry)[0])
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
                f"{device}_int" : [local_interface],
                f"{neighbor_hostname}_int": [remote_interface],
                })
                # Add the neighbor device to the dictionary of already seen devices
                neighbor_devices[end_devices] = i
                # Increment the index
                i += 1
            # Control if device pair has already been seen
            elif local_interface[0] not in network_links[neighbor_devices[end_devices]][f"{device}_int"]:
                # Append just local and remote interfaces to the device neighbor
                network_links[neighbor_devices[end_devices]][f"{device}_int"].append(local_interface)
                network_links[neighbor_devices[end_devices]][f"{neighbor_hostname}_int"].append(remote_interface)

    return network_links

def draw_graph(network_links, image_name = None):
    '''Draws the graph of the network'''
    G = nx.Graph()

    # Add nodes (devices) and links with interfaces label
    for link in network_links:
        device1, device2 = link["Devices"]
        # Get interfaces
        device1_int = link[f"{device1}_int"]
        device2_int = link[f"{device2}_int"]
        # Adding IP to device names
        device1 = f"{device1}\n{link[f'{device1}_ip']}"
        device2 = f"{device2}\n{link[f'{device2}_ip']}"
        
        # Add nodes
        G.add_node(device1)
        G.add_node(device2)
        
        int_label = ""
        # Add links with interfaces as labels
        for i in range(len(device1_int)):
            if int_label == "":
                int_label = f"{device1_int[i]} ↔ {device2_int[i]}"
            else:
                int_label = f"{int_label}\n{device1_int[i]} ↔ {device2_int[i]}"
        G.add_edge(device1, device2, label=int_label)

    # Node positions
    pos = nx.spring_layout(G)

    # Draw network nodes
    nx.draw_networkx_nodes(G, pos, node_size=1000, node_color='lightblue')

    # Draw node labels (device names)
    nx.draw_networkx_labels(G, pos, font_size=6)

    # Draw links
    nx.draw_networkx_edges(G, pos)

    # Draw link labels (interface names)
    edge_labels = nx.get_edge_attributes(G, 'label')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, label_pos=0.4, font_color='black', font_size=6, alpha=0.4)

    # Set title and disable axis
    plt.title("Network")
    plt.axis('off')

    # Remove margins
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    
    if image_name:
        # Configure image size
        figure = plt.gcf()
        # You can change the dimension of the image and DPI (resolution)
        figure.set_size_inches(16, 16)
        # Save the graph
        plt.savefig(f'{image_name}.png', dpi=250)

    # Show the image
    plt.show()

def main():

    # Remove old files from previous execution
    empty_cdp_folder()

    # Send commands in comandi.txt for devices in hosts.txt, output in /CDP/device_name
    bulk_cmd.bulk_cmd("CDP")

    # Get list of devices based on the file in CDP Folder
    device_list = get_device_list("CDP")

    # Generate list of links of the network
    network_links = handle_cdp_entries(device_list)

    # Log the list of links in a file
    with open(r"logs\network_links.txt", "w+") as debug_file:
        debug_file.write(json.dumps(network_links, indent = 2))
    
    os.system("cls")
    # Ask user the name of the image
    image_name = input("(Press Enter if you don't want to save)\nName the file for the drawing: ")

    # Draw the network
    draw_graph(network_links, image_name)

if __name__ == '__main__':
    main()
