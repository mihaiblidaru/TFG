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

#ADD requirements.txt /
#RUN pip3 install -r requirements.txt
ADD *.whl /
RUN pip3 install *.whl

ADD supervisor.conf /etc/supervisor.conf
ADD ssh/id_rsa /ssh/id_rsa
ADD client_daemon.py /
ADD ssh/id_rsa.pub /ssh/id_rsa.pub
ADD simple_ipc /simple_ipc
ADD subscriber-cp /subscriber-cp
WORKDIR /subscriber-cp
RUN pip3 install -r requirements.txt
WORKDIR /simple_ipc
RUN python3 setup.py build && python3 setup.py install

EXPOSE 8000

# Expose MongoDB port for testing
EXPOSE 27017 

CMD ["supervisord", "-c", "/etc/supervisor.conf"]


