TFG - Netconf YANG Push Server/Client
#####################################

.. contents:: Table of Contents

Components
**********

Publisher (netconf-server)
==========================
Netconf server with yang push capabilities. This server receives subscription related RPC such as establish-subscription, modify-subscription, etc, and sends periodic or on-change notifications based on requested subscription terms.

Subscriber (netconf-client)
===========================

Client Daemon
-------------

Client Control Panel (django web-app)
-------------------------------------

Instalation
***********

I assume you have cloned or downloaded this git repository and that you
have an open bash shell and changed directory to the root folder of this
repository.

::

   git clone https://github.com/mihaiblidaru/TFG.git
   cd TFG

Instalation without docker
==========================

::

   TODO

Instalation with docker
=======================
Docker architecture

.. image:: https://github.com/mihaiblidaru/TFG-doc/blob/master/graphics/docker.png

Build publisher and subscriber containers

:: 

   cd publisher && ./build_docker_container.sh && cd ..
   cd subscriber && ./build_docker_container.sh && && cd ..

Start docker containers using ``docker run``

::

   docker run -d publisher
   docker run -d subscriber

Check if the containers are running using ``docker ps``

::

   mihai@X3:~/TFG$ docker ps
   CONTAINER ID        IMAGE               COMMAND                  CREATED              STATUS              PORTS                  NAMES
   ff2002341328        subscriber          "docker-entrypoint.s…"   38 seconds ago       Up 37 seconds       8000/tcp, 27017/tcp    quizzical_einstein
   fbf551e1cd98        publisher           "docker-entrypoint.s…"   About a minute ago   Up About a minute   27017/tcp, 55555/tcp   mystifying_jepsen

Development
***************

Auxiliary modules
=======================
Simple_IPC
------------------

Probably usefull modules
========================

::

   https://github.com/robshakir/pyangbind

