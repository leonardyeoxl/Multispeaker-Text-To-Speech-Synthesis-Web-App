# standard library
import os
import json
import base64

# external library
import zmq

# project library
import common.zmq_port as zmq_port
import common.constants as constants

def generate_message():
    '''
    This function construct the message to send to zmq
    '''
    return {
        "mode": constants.Mode.DEFAULT_TTS,
        "data": {},
        "dataset": [],
        "text": "",
        "component_name": constants.Component.API,
        "status": constants.Status.OK,
        "message": ""
    }

def base64_encode(file_path):
    result = None
    with open(file_path, "rb") as f:
        result = f.read()
    return base64.b64encode(result).decode('ascii')

def submit_job(master_address, message):
    '''
    This function will submit the job to master using the message

    Input:
    - master_address -> ip or hostname to master, string
    - message -> dict obj that conform to training_system_message_protocol, dict
    Output:
    - result of the job run
    '''
    # setup zmq context
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://{IP}:{port}".format(
        IP=master_address,
        port=zmq_port.PORT_MAPPINGS[constants.Component.API][zmq_port.PUB_PORT_INDEX])
    )

    # send message
    print("********** sending message to Master ************")
    socket.send_json(message)

    # TODO: update to heartbeat instead of timeout
    # poll to handle timeout
    timeout_mins = int(os.environ.get("API_TIMEOUT_MINS", default=999))
    poller = zmq.Poller()
    poller.register(socket, zmq.POLLIN)
    # convert poll time set from milliseconds to minutes
    if poller.poll(timeout_mins * 60 * 1000):
        result_json = socket.recv_json()
    # close master socket connection
    else:
        result_json = {
            "status": constants.Status.ERROR,
            "message": "Timeout from processing the message"
        }
    # close socket
    socket.close()
    # return result_json
    return result_json

def get_str_int(text_string):
    '''
    This function will extract the int
    # TODO: Got chance the int is negative
    
    Input:
    - text_string -> text string to be converted to int, string
    Output:
    - int
    '''
    return int(text_string)

def get_str_list(text_string):
    '''
    This function will extract the list based on text_string
    
    Input:
    - text_string -> text string to be converted to list, string
    Output:
    - list
    '''
    # init
    return_list = []

    # check if it is None
    if text_string == None:
        return []

    try:
        # replace all single quotes to be double quotes
        tmp_list_str = text_string.replace("'", "\"")
        # check if first char is "["
        if tmp_list_str[0] == '[':
            return_list = json.loads(tmp_list_str)
        else:
            # it is single entry
            return_list = [tmp_list_str]
    except Exception as e:
        print(e)
        # return empty list
        return return_list
    
    return return_list


def get_str_dict(text_string):
    '''
    This function will extract the dict based on text_string
    
    Input:
    - text_string -> text string to be converted to dict
    Output:
    - list
    '''
    # init
    return_dict = []

    # check if it is None
    if text_string == None:
        return []

    try:
        # replace all single quotes to be double quotes
        tmp_list_str = text_string.replace("'", "\"")
        # check if first char is "["
        if tmp_list_str[0] == '{':
            return_dict = json.loads(tmp_list_str)
        else:
            # it is single entry
            return_dict = {tmp_list_str}
    except Exception as e:
        print(e)
        # return empty list
        return return_dict
    
    return return_dict

def generate_err_json(message):
    return {
        "status": constants.Status.ERROR,
        "message": message
    }

def parse_form(request_obj, match_dict, optional_dict = {}):
    '''
    This function will parse form data from request obj based on match_dict

    Input:
    - request_obj -> request obj from flask, request
    - match_dict -> key is form_key and value is type, dict
    - optional_dict -> key is form_key and value is type but optional, dict
    Output:
    - dict with all matched key
    '''
    # init
    hit_dict = {}
    optional_hit_dict = {}
    # list of tuple, (match dict, inserted dict)
    dict_ptr_list = [(match_dict, hit_dict), (optional_dict, optional_hit_dict)]
    # match the type to function to check
    type_mapping = {
        "string": None, # none as we just need to check if exist
        "int": get_str_int,
        "list": get_str_list,
        "dict": get_str_dict
    }

    # loop request_obj.form
    for form_key in request_obj.form:
        # loop the dict ptr list
        for dict_ptr, insert_dict_ptr in dict_ptr_list:
            # additional key, just skip
            if form_key not in dict_ptr:
                continue
            # get hit dict
            insert_dict_ptr[form_key] = request_obj.form.get(form_key)
            # get the type
            form_type = dict_ptr[form_key]
            type_func = type_mapping[form_type]
            # check if type_func is None
            if type_func != None:
                # run the function with the form value
                insert_dict_ptr[form_key] = type_func(insert_dict_ptr[form_key])

    # get list of hits and form
    match_list = list(match_dict)
    hit_list = list(hit_dict)
    # get missing list
    missing_list = list(set(match_list) - set(hit_list))
    # check if there is any missing hits
    if len(missing_list) != 0:
        # set up err_msg
        err_msg = ""
        # loop the missing list
        for missing_entry in missing_list:
            err_msg +=", Missing form key: {}".format(missing_entry)
        # set status and message, skip first ", "
        return generate_err_json(err_msg[2:])

    # all okay
    return_dict = generate_message()

    # update with hit_dict
    return_dict.update(hit_dict)

    # update with optional_hit_dict
    return_dict.update(optional_hit_dict)

    # return updated message
    return return_dict