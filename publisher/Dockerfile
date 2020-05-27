FROM mongo:latest

# install Python 3
RUN apt-get update && apt-get install -y python3.6 python3-pip

RUN apt-get -y install supervisor && \
  mkdir -p /var/log/supervisor && \
  mkdir -p /etc/supervisor/conf.d

RUN mkdir -p /data/db2 \
    && echo "dbpath = /data/db2" > /etc/mongodb.conf \
    && echo "bind_ip = 0.0.0.0" >> /etc/mongodb.conf \
    && chown -R mongodb:mongodb /data/db2

ADD publisher/requirements.txt /
RUN pip3 install -r requirements.txt

ADD netconf-extended/ /netconf-extended
WORKDIR /netconf-extended
RUN pip3 install -r requirements.txt
RUN python3 setup.py install

ADD publisher/supervisor.conf /etc/supervisor.conf
ADD publisher/start_server.py /
ADD publisher/publisher_server.py /
ADD publisher/notifications.py /
ADD publisher/config.py /
ADD publisher/server_config_docker.json /
ADD publisher/ssh/id_rsa /ssh/id_rsa
ADD publisher/ssh/id_rsa.pub /ssh/id_rsa.pub
EXPOSE 55555

# Expose MongoDB port for testing
EXPOSE 27017 

CMD ["supervisord", "-c", "/etc/supervisor.conf"]


