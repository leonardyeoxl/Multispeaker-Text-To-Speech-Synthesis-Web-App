'''
=========================================================================

The port is split by the components in the system. All components (e.g. API, TTS) will have 1x subscription port and 1x publisher port.
To send stuff to the component, one have to send the message via publisher port, and
the component will "subscribe" (while True) at the subscription port

PORT info:
** All publisher ports will be even, and all subscriber ports will be odd

=========================================================================
'''

# project library
from . import constants

# GLOBALS

# PORTS for components
API_PUB_PORT = 50000
API_SUB_PORT = 50001
API_MON_PORT = 55000

TTS_PUB_PORT = 50002
TTS_SUB_PORT = 50003
TTS_MON_PORT = 55001

TRAIN_PUB_PORT = 50004
TRAIN_SUB_PORT = 50005
TRAIN_MON_PORT = 55002

EMBEDDING_PUB_PORT = 50006
EMBEDDING_SUB_PORT = 50007
EMBEDDING_MON_PORT = 55003

# Mapping (component name to ports tuple (publisher port, subscriber port))
PORT_MAPPINGS = {
    constants.Component.API: (API_PUB_PORT, API_SUB_PORT, API_MON_PORT),
    constants.Component.TTS: (TTS_PUB_PORT, TTS_SUB_PORT, TTS_MON_PORT),
    constants.Component.TRAIN: (TRAIN_PUB_PORT, TRAIN_SUB_PORT, TRAIN_MON_PORT),
    constants.Component.EMBEDDING: (EMBEDDING_PUB_PORT, EMBEDDING_SUB_PORT, EMBEDDING_MON_PORT)
}

PUB_PORT_INDEX = 0
SUB_PORT_INDEX = 1
MON_PORT_INDEX = 2