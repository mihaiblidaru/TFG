import os

inside_container = os.environ.get('DOCKER_CONTAINER', False)

# Configuration
username = "admin"
password = "admin"
ssh_host_key_path = "./ssh/id_rsa"
port = 55555
debug = True
mongo_host = "127.0.0.7"
mongo_port = 27017
mongo_db = "netconf"
mongo_collection = "data"

if inside_container:
    # Override default values if running inside a docker container
    # 830 is the port for Netconf over SSH
    port = 830 # Inside a container the script run as root and can bind to ports below 1024