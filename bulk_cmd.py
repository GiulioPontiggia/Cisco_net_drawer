# Import libraries
import os
import time
import sys

from dotenv import load_dotenv
from netmiko import ConnectHandler

def get_hosts_list(file_path):
    '''return the list of hosts in the file'''
    with open(file_path,  'r') as f:
        hosts_list = f.read().splitlines()
        return hosts_list

def get_command_list(file_path):
    '''Return list of commands retrieved from file'''
    with open(file_path, 'r') as f:
        commands = f.read().splitlines()
        return commands

def write_to_file(path, cdp_output):
    with open(path, 'w+') as fLog:
        for item in cdp_output:
            fLog.write(f"{item} \n\n")

def get_credentials():
    # Load .env file
    load_dotenv()
    user = os.getenv('USER')
    psw = os.getenv('PSW')
    return([user, psw])

def bulk_cmd(log_folder):
    
    commands_file = 'commands.txt'
    hosts_file = 'hosts.txt'

    command_list = get_command_list(commands_file)
    hosts_list = get_hosts_list(hosts_file)

    user, psw = get_credentials()

    for host in hosts_list:
        switch = {
            'device_type': 'cisco_ios',
            'ip': host,
            'username': user,
            'password': psw
        }          

        # Retry 3 times to connect to the device (when connected breaks the cycle)
        for tries in range(2):
            try:
                print(f"\nTrying to connect to {host} for {tries + 1}th time... ")
                net_connect = ConnectHandler(**switch, conn_timeout=120)

                # Takes the prompt of the device and remove the #
                hostname = net_connect.find_prompt().replace("#", "")
                out_list = list()
                
                # Run each command in the list on the device and write the output to a file
                for command in command_list:
                    # Send command to device and takes output
                    output = net_connect.send_command(command, max_loops = 2000)
                    # Append output to output list (it will be written in the output file)
                    out_list.append(f"\n{output}\n")
                    print(f'#[{host}] sent command -> {command}')

                # Writes the output to device's file
                logFile = f"{log_folder}\{hostname}.txt" 
                net_connect.disconnect()
                write_to_file(logFile, out_list)
                break
            
            # Exit script if CTRL + C is pressed
            except KeyboardInterrupt:
                print("Exiting script")
                try:
                    # Disconnect from the device if connected
                    net_connect.disconnect()
                except:
                    None
                sys.exit()

            # Print connection error if both tries failed
            except:
                if (tries == 1):
                    print(f'[{host}] connection error')

    print(f'Performed bulk commands on {len(hosts_list)} devices!')

if __name__ == '__main__':
    bulk_cmd()