"""
This python script contain functions to generically wrap any worker container that conforms to the function template.

wrapper.Worker(func_to_run, component_name, master_ip, [logger_obj])

=========================================================================

Function Template:

def <func_name>(input_dict):
    '''
    Do stuff here, embedding
    input_dict contains the following:
        "data": message["data"],
        "text": message["text"],
        "dataset": message["dataset"]
    '''
    return <output_dict>

=========================================================================
"""
# standard library
import base64
import traceback

# external library
import zmq

# project library
from . import zmq_port
from . import constants

class WorkerWrapper:

    def __init__(self, wrapped_func, component_name, master_ip, logger_obj=None):
        '''
        The wrapper will call the wrapped function by saving the files from message struct into save directory,
        posting the files back to fileserver when the wrapped function is done
        Input:
        - wrapped_func -> function to be called when there is a message from queue, function
        - component_name -> name of the running component (all CAPS alphabet), string
        - master_ip -> the ip address of the master component, string
        - logger_obj -> logger obj for logging, klass logger, default=None
        '''
        self.wrapped_func = wrapped_func
        self.component_name = component_name
        self.master_ip = master_ip
        self.logger_obj = logger_obj

    def run(self):
        '''
        This function will constantly wait for message from ZMQ and run the wrapped function,
        it will handles the file download for input files and file upload for output files and replying back to ZMQ
        Input:
        - Nil
        Output:
        - This function will never return
        '''
        # while loop to consume message
        context = zmq.Context()
        socket = context.socket(zmq.REP) #have to set from REP to XREP, to prevent having the need to reply the 'REQ'
        socket.connect("tcp://{IP}:{port}".format(IP=self.master_ip, port=zmq_port.PORT_MAPPINGS[self.component_name][zmq_port.SUB_PORT_INDEX]))
        while True:
            # received as json if zmq.REP else zmq.XREP will send '\x00k\x8bEo' gibberish, not json
            message = socket.recv_json()

            # B64 decode
            data_dict = {}
            for key, value in message["data"].items():
                data_dict[key] = base64.b64decode(value)

            # extract the essential information
            # local pathing
            input_dict = {
                "data": data_dict,
                "text": message["text"],
                "dataset": message["dataset"]
            }

            # set component_name
            message["component_name"] = self.component_name

            # surround with try/except
            try:
                # logging 
                if self.logger_obj != None:
                    self.logger_obj.log_info("Input dict: {}".format(input_dict))
                # call the wrapped function
                output_dict = self.wrapped_func(input_dict)

                # loop to update message
                for output_key in output_dict:
                    if output_key == "data":
                        # base64 encode it
                        for inner_key in output_dict[output_key]:
                            with open(output_dict[output_key][inner_key], "rb") as f:
                                output_dict[output_key][inner_key] = base64.b64encode(f.read()).decode('ascii')
                    message[output_key] = output_dict[output_key]

                # logging 
                if self.logger_obj != None:
                    self.logger_obj.log_info("Output message: {}".format(output_dict))
            except Exception as e:
                # logging 
                if self.logger_obj != None:
                    self.logger_obj.log_info("Error: {}".format(e))
                # attach err message and update status not okay
                message["status"] = constants.Status.ERROR
                message["message"] = "[{component_name}] - {error}, {traceback}".format(
                    component_name=self.component_name,
                    error=str(e),
                    traceback=traceback.format_exc()
                )

            # send back via same socket
            socket.send_json(message, flags=zmq.NOBLOCK)