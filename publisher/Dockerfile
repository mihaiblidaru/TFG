FROM python:3
ADD start_server.py /
ADD publisher_server.py /
ADD subscription.py /
ADD notifications.py /
ADD config.py /
ADD server_config.json /
ADD ssh/id_rsa /ssh/id_rsa
ADD ssh/id_rsa.pub /ssh/id_rsa.pub 
RUN pip install netconf pymongo python-daemon

EXPOSE 55555

CMD [ "python", "./start_server.py" ]
