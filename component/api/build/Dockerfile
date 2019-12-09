FROM python:3.7.5-slim

#USER api
WORKDIR /opt/app

# common
COPY common/requirements.txt /opt/app/common/requirements.txt
RUN pip install -r /opt/app/common/requirements.txt

COPY common /opt/app/common

# component specific
COPY api/build/requirements.txt /opt/app/requirements.txt
RUN pip install -r /opt/app/requirements.txt

COPY api/src /opt/app

# Expose Port 8080
EXPOSE 8080

# entrypoint
ENTRYPOINT python -u /opt/app/api.py
