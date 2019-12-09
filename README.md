# Text to Speech Voice Cloning

Reference from <https://github.com/CorentinJ/Real-Time-Voice-Cloning>

## System Dependencies

- docker version: 18.09.3, build 774a1f4
- Docker Engine version: 18.09.3, build 774a1f4
- docker-compose version: 1.24.0, build 0aa59064
- nvidia-docker version: 2.0.3
- CUDA version: >= 10.0

## Requirements

Need at least 6GB GPU to run

## Setup

1. Create your own copy of `.env` by running
`cp .env_sample .env`
2. `docker-compose up --build`

## API call

```bash
curl -X POST -F "files[]=@full.wav" -F "text=They developed superpowers after years of drinking from a lead-poisoned water supply But just having incredible abilities doesn't make them superheroes" localhost:8080/api/tts -o r.json
```

## Limitations

- Can only be able to generate one sentence at a time (For 6GB GPU)
- Lack of crash handling (GPU OOM)

## Future Work

- Add [Waveglow](https://github.com/NVIDIA/waveglow)
- Retraining of model