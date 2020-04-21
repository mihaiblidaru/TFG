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
This is a module for interprocess communication using JSON as marshaling language and unix(or TCP) sockets for transport. It uses a client-server architecture where the server acts similar to a http server, it can answer requests from client but it cannot initiate the communication itself.

Right now I'm using it for sending messages between the Client Daemon and the Client Control Panel, as they are separate processes.


Probably usefull modules
========================

Tareas
======

21 de abril de 2020
-------------------

 * [X] Hacer que funcione el panel de control para establish-subscriptions.  
 * [X] Terminal la función de establish-subscriptions en client.py validando todos los campos (probar rapidamente pyangbind para crear bindings de las rpcs, si no funciona lo vamos a hacer a mano con ncutils y lxlml).  
 * [X] Hacer que el cliente mande establish-subscriptions a servidores.  
 * [X] Crear hilos en cliente para guardar los datos de notificaciones en la base de datos.
 * [ ] Implementar el cierre de sesiones desde la web en cliente (tanto front, como backend de control como en el propio cliente)
 
22 de abril de 2020
-------------------
 
 * [ ] Escribir 2 páginas del estado del arte
 * [ ] Validar las peticiones de subscripciones en el servidor al 100 %
 * [ ] Implementar anchor-time en las subscripciones periodicas
 * [ ] Implementar las notificaciones on-change de forma básica
 * [ ] Rellenar con datos basados en modelos yang soportados la base de datos al arrancar el servidor netconf
 
Tareas a corto plazo
--------------------
 
 * [ ] Preguntar a Jorge que hay que poner en la parte de Desarrollo
 
Tareas a largo plazo
--------------------
 
 * [ ] Escribir pruebas unitarias para cliente y servidor
