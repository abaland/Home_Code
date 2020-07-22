"""
This module defines all message-handling functions from the main functions, i.e. functions that 
    create the message to send RabbitMQ server, and functions that process the response received 
    from it.
"""

#################
# LOCAL PACKAGES
#################
from . import main_heartbeat
from . import main_update
from . import main_remote_control
from . import main_files
from . import main_sensors
from . import main_ssh

#############
# CODE START
#############

__author__ = 'Adrien Baland'


all_instructions = ['remote_control', 'files', 'sensors', 'ssh']


# What message and timeout info to send main program. All of them have 'get_message' and
# 'process_response' instructions
instruction_to_functions = {
    'heartbeat': main_heartbeat,
    'update': main_update,
    'remote_control': main_remote_control,
    'files': main_files,
    'sensors': main_sensors,
    'ssh': main_ssh,
}
