import argparse
import python.global_libraries.general_utils as general_utils


####################################################################################################
# INSTRUCTION PARSER
####################################################################################################
# Creates parser for all options in camera control
argument_parser = argparse.ArgumentParser()

# Timeout argument
timeout_help = 'Number of seconds to wait for a response.\n'
argument_parser.add_argument('--timeout', '-t', action='store', nargs='?', type=int)

#########################
# END INSTRUCTION PARSER
#########################


####################################################################################################
# get_help_message
####################################################################################################
# Revision History :
#   2016-11-26 AB : Function created
####################################################################################################
def get_help_message(with_details=False):
    """
    Prints information message about instruction.

    INPUT:
         with_details (Boolean) whether only general information about instruction should be 
            printed, or detailed.
    """

    print('heartbeat.')
    print('Orders worker to send an activity signal by sending a basic response.')

    if with_details:
        
        argument_parser.print_help()

    #######
    return
    #######

#######################
# END get_help_message
#######################


####################################################################################################
# get_message
####################################################################################################
# Revision History :
#   2016-11-26 AB : Function created
####################################################################################################
def get_message(rabbit_master_object, base_instruction_message, command_arguments):
    """
    Sends a heartbeat request to the RabbitMQ server

    INPUT:
         rabbit_master_object (Master) master controller, sending instruction to RabbitMQ server.
         my_time_out (str, opt) : timeout value

    OUTPUT:
        message (str): an empty string ('heartbeat' instruction name is sufficient)
        timeout (float): the timeout value to apply
    """

    try:
    
        parsed_command_arguments, _ = argument_parser.parse_known_args(command_arguments)

    except SystemExit:
    
        argument_parser.print_usage()
        
        #############################################
        raise ValueError('Could not parse command.')
        #############################################

    input_timeout = parsed_command_arguments.timeout

    ###################################################################################
    return base_instruction_message, rabbit_master_object.parse_timeout(input_timeout)
    ###################################################################################

##################
# END get_message
##################


####################################################################################################
# process_response
####################################################################################################
# Revision History :
#   2016-11-26 AB : Function created
####################################################################################################
def process_response(_, received_worker_message):
    """
    Processes camera report from a worker.

    INPUT:
         master (Master) : Unused here.
         received_worker_message (lxml.etree object) message from worker as 
            <worker id=... status=...>
    """

    cpu_percentage = received_worker_message.get('cpu')
    timestamp = received_worker_message.get('timestamp')
    code_version = received_worker_message.get('version')

    general_utils.log_message('CPU: %s%%. Timestamp: %s. Version: %s.' % (cpu_percentage,
                                                                          timestamp, code_version))

    #######
    return
    #######

#######################
# END process_response
#######################
