FROM mongo:latest
# Use mongo image as base

# Set an environment variable that will be used for programs to know if they are running 
# inside a container
ENV DOCKER_CONTAINER True

# Install python3 and pip
RUN apt-get update && apt-get install -y python3.6 python3-pip

# Install supervisor. Supervisor is used to launch multiple long-running programs as daemons,
# monitor them, relaunch them if necesary, etc.
RUN apt-get -y install supervisor && \
  mkdir -p /var/log/supervisor && \
  mkdir -p /etc/supervisor/conf.d

# Configure some mongodb variables
RUN mkdir -p /data/db2 \
    && echo "dbpath = /data/db2" > /etc/mongodb.conf \
    && echo "bind_ip = 0.0.0.0" >> /etc/mongodb.conf \
    && chown -R mongodb:mongodb /data/db2


# Add and install the modified version of netconf 
ADD netconf-extended/ /netconf-extended
WORKDIR /netconf-extended
RUN pip3 install -r requirements.txt
RUN python3 setup.py build
RUN python3 setup.py install

# Add & install simple_ipc module
ADD simple_ipc /simple_ipc
WORKDIR /simple_ipc
RUN python3 setup.py build && python3 setup.py install

# Add supervisor config file
ADD subscriber/supervisor.conf /etc/supervisor.conf

# Add subscriber control panel and install its dependencies
ADD subscriber/subscriber-cp /subscriber-cp
WORKDIR /subscriber-cp
RUN pip3 install -r requirements.txt

# Add remaining files
ADD subscriber/ssh/id_rsa /ssh/id_rsa
ADD subscriber/client_daemon.py /
ADD subscriber/ssh/id_rsa.pub /ssh/id_rsa.pub


# Expose 8000 post for the django control panel
EXPOSE 8000

# Expose MongoDB port for testing
EXPOSE 27017 

CMD ["supervisord", "-c", "/etc/supervisor.conf"]


