"""
This module defines all message-handling functions from the master functions, i.e. functions that create the message to
 send the RabbitMQ server, and functions that process the response received from it.
"""

#################
# LOCAL PACKAGES
#################
import master_heartbeat
import master_update
import master_remote_control

#############
# CODE START
#############

__author__ = 'Adrien Baland'


all_instructions = ['remote_control']


# What message and timeout info to send the master program. All of them have 'get_message' and 'process_response'
# instructions
instruction_to_functions = {
    'heartbeat': master_heartbeat,
    'update': master_update,
    'remote_control': master_remote_control,
}
