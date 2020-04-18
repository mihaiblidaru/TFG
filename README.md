# TFG - Netconf YANG Push Server/Client

## Server
Netconf server in charge of receiving subscription related RPC such as establish-subscription, modify-subscription, etc, and sending the notification data to the subscribers.
## Client
### Client Server
Recieves notifications and saves then into a db or file.
### Client Control Panel WebApp
Manage subscriptions. Send establish-subscription, modify-subscription RPCs to clients.


## Instalation
I assume you have cloned or downloaded this git repository and that you have an open bash shell and changed directory to the root folder of this repository.

```
git clone https://github.com/mihaiblidaru/TFG.git
cd TFG
```

### Instalation without docker
```
TODO
``` 
### Instalation with docker
Build publisher and subscriber containers

```bash
cd publisher && ./build_docker_container.sh && cd ..
cd subscriber && ./build_docker_container.sh && && cd ..
```

Start docker containers using `docker run`
```
docker run -d publisher
docker run -d subscriber
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





