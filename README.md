# How to setup
## Windows
- Pull the repository `git pull "https://github.com/GiulioPontiggia/Cisco_net_drawer"`
- Create a "CDP" and "logs" directory to contain files used buy the script `mkdir CDP, logs`
- Create a .env file to contain credentials for accessing your devices `(echo USER=user & echo PSW=psw) > .env`
- Install requirements `pip install -r requirements.txt`
- Create a hosts.txt file containing all IPs of devices to access separated by newline
## Linux
- Pull the repository `git pull "https://github.com/GiulioPontiggia/Cisco_net_drawer"`
- Create a "CDP" and "logs" directory to contain files used buy the script `mkdir CDP logs`
- Create a .env file to contain credentials for accessing your devices `echo -e "USER=user\nPSW=psw > .env`
- Create a hosts.txt file containing all IPs of devices to access separated by newline

# How to use
Once the setup is done it will be enough to run the net mapper file `python3 net_mapper.py`. The script will connect to each switch in the hosts.txt file to find cdp neighbors and it will draw a map, you can save the map by writing the name of the png file at the end or just press enter to avoid saving it. By default the nodes (network devices) are shown with name and IP as labels and each edge (connection between devices) is shown with the interfaces of both devices on the respective side of the link.
