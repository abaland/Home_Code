"""
This module defines all message-handling functions from the master functions, i.e. functions that 
    create the message to send RabbitMQ server, and functions that process the response received 
    from it.
"""

#################
# LOCAL PACKAGES
#################
from . import master_heartbeat
from . import master_update
from . import master_remote_control
from . import master_files
from . import master_sensors
from . import master_ssh

#############
# CODE START
#############

__author__ = 'Adrien Baland'


all_instructions = ['remote_control', 'files', 'sensors', 'ssh']


# What message and timeout info to send master program. All of them have 'get_message' and
# 'process_response' instructions
instruction_to_functions = {
    'heartbeat': master_heartbeat,
    'update': master_update,
    'remote_control': master_remote_control,
    'files': master_files,
    'sensors': master_sensors,
    'ssh': master_ssh,
}
