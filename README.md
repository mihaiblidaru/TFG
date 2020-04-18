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


## How to build & run publisher-subscriber docker containers

```
git clone https://github.com/mihaiblidaru/TFG.git
cd TFG
cd publisher && ./build_docker_container.sh && docker run -d publisher && cd ..
cd subscriber && ./build_docker_container.sh && docker run -d subscriber && cd ..
```

Check if the containers are running using `docker ps`
```
mihai@X3:~/TFG$ docker ps
CONTAINER ID        IMAGE               COMMAND                  CREATED              STATUS              PORTS                  NAMES
ff2002341328        subscriber          "docker-entrypoint.s…"   38 seconds ago       Up 37 seconds       8000/tcp, 27017/tcp    quizzical_einstein
fbf551e1cd98        publisher           "docker-entrypoint.s…"   About a minute ago   Up About a minute   27017/tcp, 55555/tcp   mystifying_jepsen
```







# Probably usefull modules
```
https://github.com/robshakir/pyangbind

```





