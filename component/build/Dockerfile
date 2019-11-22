FROM pytorch/pytorch:1.3-cuda10.1-cudnn7-devel

WORKDIR "/workspace"
RUN apt-get clean \
        && apt-get update \
        && apt-get install -y \ 
        build-essential=12.1ubuntu2 \
        git=1:2.7.4-0ubuntu1.6 \
        wget=1.17.1-1ubuntu1.5 \
        python-dev=2.7.12-1~16.04 \
        ffmpeg \ 
        libportaudio2 \ 
        python3-pyqt5 \ 
        libffi-dev=3.2.1-4 \
        && apt-get -y autoremove
COPY requirements.txt /workspace/requirements.txt
RUN pip install -r /workspace/requirements.txt

# install python3.7
WORKDIR /tmp
RUN wget https://www.python.org/ftp/python/3.7.2/Python-3.7.2.tar.xz
RUN tar xvf Python-3.7.2.tar.xz
RUN cd Python-3.7.2 \
    && ./configure --enable-optimizations \
    && make -j 8 \
    && make altinstall

# link python3.7 to python3
RUN ln -sf /usr/local/bin/pip3.7 /usr/bin/pip3
RUN ln -sf /usr/local/bin/python3.7 /usr/bin/python3
RUN ln -sf /usr/local/bin/python3.7 /usr/bin/python3.5

# set work dir
WORKDIR /opt/app

# entrypoint
ENTRYPOINT bash
