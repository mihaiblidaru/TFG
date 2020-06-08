import os

inside_container = os.environ.get('DOCKER_CONTAINER', False)

# User and password for authentication
username = "admin"
password = "admin"

# Even if we use user-password authentication the server still needs a private ssh key
ssh_host_key_path = "./ssh/id_rsa"

# Listening port
port = 55555

# Debug. It affects logging levels.
debug = True

# MongoDB backend configuration
mongo_host = "127.0.0.7"
mongo_port = 27017
mongo_user = None
mongo_password = None
mongo_db = "netconf"
mongo_collection = "data"

# Min period between notifications
min_period = 10

if inside_container:
    # Override default values if running inside a docker container
    # 830 is the port for Netconf over SSH
    port = 830  # Inside a container the script run as root and can bind to ports below 1024
