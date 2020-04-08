FROM python:3
ADD start_server.py /
ADD requirements.txt /
ADD publisher_server.py /
ADD notifications.py /
ADD config.py /
ADD server_config_docker.json /
ADD ssh/id_rsa /ssh/id_rsa
ADD ssh/id_rsa.pub /ssh/id_rsa.pub 
RUN pip install -r requirements.txt

EXPOSE 55555

CMD [ "python", "./start_server.py" , "--conf=server_config_docker.json"]


