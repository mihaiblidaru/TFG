# TFG - Netconf YANG Push Server/Client

## Server
Netconf server in charge of receiving subscription related RPC such as establish-subscription, modify-subscription, etc, and sending the notification data to the subscribers.
## Client
### Client Server
Recieves notifications and saves then into a db or file.
### Client Control Panel WebApp
Manage subscriptions. Send establish-subscription, modify-subscription RPCs to clients.
