"""
This script contains the common constants shared to all modules.

TTS system message protocol (v1.0):
{
    "mode": <string>, (what mode? normal TTS? train?)
    "data": {
        <audio_name>: b64encoded(),
    }, (all data related to current job)
    "dataset": [<list of dataset name>],
    "text": <string>, (text to convert to audio)
    "component_name": <string>,
    "status": <ok | err, string> (denotes if process is okay)
    "message": <"" | <error message>, string> (indicate what error messsage)
}

# CHANGELOG
v1.0:
- Release first version
- Training not supported yet
"""

# Standard libraries
from enum import Enum

class Mode(str, Enum):
    DEFAULT_TTS = "tts_0"
    TRAIN = "train"

class Component(str, Enum):
    API = "API"
    TTS = "TTS"
    TRAIN = "TRAIN"
    EMBEDDING = "EMBEDDING"

class Status(str, Enum):
    OK = 'ok'
    ERROR = 'err'
