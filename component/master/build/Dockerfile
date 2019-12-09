FROM python:3.7.5-slim

#USER master
WORKDIR /opt/app

# common
COPY common/requirements.txt /opt/app/common/requirements.txt
RUN pip install -r /opt/app/common/requirements.txt

COPY common /opt/app/common

# component specific
COPY master/src /opt/app

# expose
EXPOSE 50000-50010
EXPOSE 55000-55005

# entrypoint
ENTRYPOINT python -u /opt/app/master.py