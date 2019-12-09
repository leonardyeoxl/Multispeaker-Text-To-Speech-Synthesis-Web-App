FROM pytorch/pytorch:1.2-cuda10.0-cudnn7-runtime

RUN apt-get clean \
        && apt-get update \
        && apt-get install -y \ 
        build-essential=12.1ubuntu2 \
        libffi-dev=3.2.1-4 \
        libsndfile1=1.0.25-10ubuntu0.16.04.2 \
        && apt-get -y autoremove

#USER tts
WORKDIR /opt/app

# common
COPY common/requirements.txt /opt/app/common/requirements.txt
RUN pip install -r /opt/app/common/requirements.txt

COPY common /opt/app/common

# component specified
COPY tts/build/requirements.txt /opt/app/requirements.txt
RUN pip install -r /opt/app/requirements.txt

COPY tts/src /opt/app

# entrypoint
ENTRYPOINT python -u /opt/app/tts.py
