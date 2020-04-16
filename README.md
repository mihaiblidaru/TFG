# TFG - Netconf YANG Push Server/Client

## Server
Netconf server in charge of receiving subscription related RPC such as establish-subscription, modify-subscription, etc, and sending the notification data to the subscribers.
## Client
### Client Server
Recieves notifications and saves then into a db or file.
### Client Control Panel WebApp
Manage subscriptions. Send establish-subscription, modify-subscription RPCs to clients.


## Instalation
Because we used the package [netconf](https://pypi.org/project/netconf/) as base for this project during developement we realized that the netconf client provided by this library was unable to receive notification messages from any netconf server. To address this problem we created our own slightly modified build of [netconf](https://pypi.org/project/netconf/). The realized modifications were non-intrusive, allowing the proper functioning of all existing functionality.

The first step is to uninstall all previous versions of [netconf](https://pypi.org/project/netconf/) and install the modified one.

```
pip3 uninstall netconf
cd netconf-extended
python3 setup.py build
python3 setup.py install --user
# If you want to install it as system package use the next command
# sudo python3 setup.py install
cd ..
```


## How to build & run docker publisher module

```
cd publisher
# change mongo host in server_config_docker.json
docker build -t publisher
docker run -d publisher
```

# Probably usefull modules
```
https://github.com/robshakir/pyangbind

```




