'''
This implementation uses SYNCHRONISE to control the messaging system within the StockHolm offline worker containers,
the DAG flow is implemented at zmq_map_logic.py
'''
# standard library
import os
from multiprocessing import Process

# external library
import zmq
from zmq.devices.monitoredqueuedevice import MonitoredQueue
from zmq.utils.strtypes import asbytes

# project library
import common.zmq_port as zmq_port
import common.constants as constants
import zmq_map_logic

def start_monitored_queue_ZMQ(ip_addr, pub_port, sub_port, monitor_port, identifier=''):
    '''
    This function will start ZMQ monitored queue for based on given ports, used
    mainly for multiprocessing.Process

    Input:
    - ip_addr -> ip address to bind, string
    - pub_port -> port for publisher, int
    - sub_port -> port for subscriber, int
    - monitor_port -> port for monitor, int
    - identifier -> identifier for the monitored queue, string
    Output:
    - Does not return
    '''
    # Prepare our context and sockets
    in_prefix=asbytes(identifier + '_in')
    out_prefix=asbytes(identifier + '_out')
    try:
        # start the MonitoredQueue
        monitoring_device = MonitoredQueue(zmq.XREP, zmq.XREQ, zmq.PUB, in_prefix, out_prefix)
        
        monitoring_device.bind_in("tcp://{ip_addr}:{pub_port}".format(ip_addr=ip_addr, pub_port=pub_port))
        monitoring_device.bind_out("tcp://{ip_addr}:{sub_port}".format(ip_addr=ip_addr, sub_port=sub_port))
        monitoring_device.bind_mon("tcp://{ip_addr}:{monitor_port}".format(ip_addr=ip_addr, monitor_port=monitor_port))
        
        monitoring_device.setsockopt_in(zmq.RCVHWM, 1)
        monitoring_device.setsockopt_out(zmq.SNDHWM, 1)
        # logging
        print("{identifier}: Monitoring device has started".format(identifier=identifier))
        # start the monitoring
        monitoring_device.start()  
        # Not supposed to return, as the monitoring_device is blocking
    except:
        # have exception
        pass 

def send_message(ip_addr, pub_port, message, timeout_mins):
    '''
    Input:
    - ip_addr -> ip address to bind, string
    - pub_port -> port for publisher, int
    - message -> message to send to publisher port in queue, message protocol
    - timeout_mins -> mins for timeout in the system, int
    Output:
    - return response message, message protocol
    '''
    # create zmq context
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://{ip_addr}:{pub_port}".format(ip_addr=ip_addr, pub_port=pub_port))
    socket.send_json(message)
    # blocking operation, set timeout, https://github.com/zeromq/pyzmq/issues/132
    poller = zmq.Poller()
    poller.register(socket, zmq.POLLIN) # POLLIN for recv, POLLOUT for send
    # check for timeout
    if poller.poll(timeout_mins * 60 * 1000): # N mins, in millisec
        return_msg = socket.recv_json()
    else:
        raise IOError("Timeout from processing the message")
    # clean up
    socket.close()
    context.term()
    # return
    return return_msg

def master_proc(ip_addr, sub_port, end_state, status_code, timeout_mins=15):
    '''
    Input:
    - ip_addr -> ip address to bind, string
    - sub_port -> port for subscriber, int
    - end_state -> end state of flow e.g. API or PREPROCESSING, string
    - status_code -> status of master DAG, bool
    - timeout_mins -> mins for timeout in the system, default=15, int
    Output:
    - Does not return 
    '''

    # create context
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.connect("tcp://{ip_addr}:{sub_port}".format(ip_addr=ip_addr, sub_port=sub_port))
    while True:
        # recieve message
        curr_msg = socket.recv_json()
        print("Recieved messsage")

        # check if DAG flow, always fail the job if DAG don't flow as intended
        if status_code == False:
            curr_msg["status"] = constants.Status.ERROR
            curr_msg["message"] = "Error in DAG flow"
            socket.send_json(curr_msg)
            # skip the rest
            continue

        # surround with try/except
        try:
            # flow through zmq_map_logic.DAG_FLOW
            while True:
                # get next state
                next_state_list, filter_func = zmq_map_logic.DAG_FLOW[curr_msg["component_name"]]
                next_state = next_state_list[0] # default to be index 0
                # check if exist filterFunc
                if filter_func != None:
                    next_state = filter_func(curr_msg)

                # check if next_state same as end_state
                if next_state == end_state:
                    # break out of loop
                    break

                # update curr_msg
                port = zmq_port.PORT_MAPPINGS[next_state][zmq_port.PUB_PORT_INDEX]
                print("Sending to {}".format(port))
                curr_msg = send_message(ip_addr, port, curr_msg, timeout_mins)

                # check if curr_msg is okay
                if curr_msg["status"] == constants.Status.ERROR:
                    raise Exception(curr_msg["message"])
        except Exception as e:
            # attach err message and update status not okay
            curr_msg["status"] = constants.Status.ERROR
            curr_msg["message"] = str(e)

        # send to start component
        socket.send_json(curr_msg)

if __name__ == "__main__":
    # init
    ip_addr = "0.0.0.0" # default master hold the queue
    # master_proc_count = int(os.environ["MASTER_PROC_COUNT"])
    # start_state = os.environ["MASTER_START_STATE"] #"API"
    # end_state = os.environ["MASTER_END_STATE"] #"API"
    # timeout_mins = int(os.environ["MASTER_TIMEOUT_MINS"])
    master_proc_count = 1
    start_state = constants.Component.API
    end_state = constants.Component.API
    timeout_mins = 9999

    status_code = True

    # get node via the key in zmq_map_logic.DAG_FLOW
    for node in zmq_map_logic.DAG_FLOW:
        # setup queue
        pub_port = zmq_port.PORT_MAPPINGS[node][zmq_port.PUB_PORT_INDEX]
        sub_port = zmq_port.PORT_MAPPINGS[node][zmq_port.SUB_PORT_INDEX]
        mon_port = zmq_port.PORT_MAPPINGS[node][zmq_port.MON_PORT_INDEX]
        # spawn queue process
        Process(
            target=start_monitored_queue_ZMQ, 
            args=(ip_addr, pub_port, sub_port, mon_port, node)
        ).start()
        # spawn monitoring process, moved monitoring process to monitor component

    # start multiple process of master_proc
    for index in range(master_proc_count):
        # get subscriber port
        sub_port = zmq_port.PORT_MAPPINGS[start_state][zmq_port.SUB_PORT_INDEX]
        # spawn process
        Process(
            target=master_proc, 
            args=(ip_addr, sub_port, end_state, status_code, timeout_mins)
        ).start()
    
    print("MASTER - DONE Setting up")
