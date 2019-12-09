'''
=========================================================================

The graph is constructed via Python data structure (https://www.python.org/doc/essays/graphs/)

- The vertices/nodes will denote the components and they are expressed as "key"
- The edges will denote the components to components interaction and they are expressed as "key-value" pair
- The next nodes will be denote the next possible components and they are expressed as "value" (in type of tuples ([<node1>, <node2>], <filter_func>))
** If filter_func is None, it will default to use 0th index in the next-node-list

Filter function:
def <funcName>(message):
    Input:
    - message -> message recieved, message protocol
    Output:
    - component name, string
    <Do something>
    return <componentName>

=========================================================================
'''

# project library
import common.constants as constants

# Filter func
def filter_after_api(message):
    '''
    This function will return the component name based on custom filtering for choosing decoder
    Input:
    - message -> message received, message protocol
    Output:
    - component name, string
    '''

    after_api_mapping = {
        constants.Mode.DEFAULT_TTS: constants.Component.TTS,
        constants.Mode.TRAIN: constants.Component.TRAIN
    }

    # return
    return after_api_mapping[message["mode"]]

# DAG for flow
'''
Each key represent the component,
The value will be as such,
(
    [List of potential next states, could be 1],
    filter_func to decide the state
)
E.g.
API will post stuff to EMBEDDING publisher port, while EMBEDDING listen to it's subscriber port
'''
DAG_FLOW = {
    constants.Component.API: (
        [
            constants.Component.TTS,
            constants.Component.TRAIN
        ],
        filter_after_api
    ),
    constants.Component.TTS: (
        [
            constants.Component.API
        ],
        None
    ),
    constants.Component.TRAIN: (
        [
            constants.Component.API
        ],
        None
    )
}