# Text to Speech Voice Cloning

Reference from <https://github.com/CorentinJ/Real-Time-Voice-Cloning>

## System dependencies

- docker version: 18.09.3, build 774a1f4
- Docker Engine version: 18.09.3, build 774a1f4
- docker-compose version: 1.24.0, build 0aa59064
- nvidia-docker version: 2.0.3
- CUDA version: >= 10.0

## Setup

git clone https://github.com/CorentinJ/Real-Time-Voice-Cloning in `reference` directory

Create your own copy of `.env` before running
`cp .env_sample .env`

Modify the path variables appropriately

## Running the training

`docker-compose up --build`
