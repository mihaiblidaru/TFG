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

# Add requierements.txt and install
ADD publisher/requirements.txt /
RUN pip3 install -r requirements.txt

# Add and install the modified version of netconf 
ADD netconf-extended/ /netconf-extended
WORKDIR /netconf-extended
RUN pip3 install -r requirements.txt
RUN python3 setup.py build
RUN python3 setup.py install

# Add supervisor config file
ADD publisher/supervisor.conf /etc/supervisor.conf

# Add the remaining files
ADD publisher/datasource.py /
ADD publisher/start_server.py /
ADD publisher/publisher_server.py /
ADD publisher/notifications.py /
ADD publisher/config.py /
ADD publisher/ssh/id_rsa /ssh/id_rsa
ADD publisher/ssh/id_rsa.pub /ssh/id_rsa.pub

# Expose default Netconf-over-SSH 
EXPOSE 830
EXPOSE 55555

# Expose MongoDB port for testing
EXPOSE 27017 

CMD ["supervisord", "-c", "/etc/supervisor.conf"]


