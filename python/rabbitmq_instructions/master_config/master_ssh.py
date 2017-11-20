########################
# Import Global package
########################
import argparse


####################################################################################################
# DEFAULTS
####################################################################################################

####################################################################################################
# INSTRUCTION PARSER
####################################################################################################
# Creates parser for all options in camera control
argument_parser = argparse.ArgumentParser()

# Timeout argument
command_help = 'Command to send (Start/Stop).\n'
argument_parser.add_argument('command', action='store', type=str, choices=['Start', 'Stop'],
                             help=command_help)

# Timeout argument
timeout_help = 'Number of seconds to wait for a response.\n'
argument_parser.add_argument('--timeout', '-t', action='store', nargs='?', type=int,
                             help=timeout_help)

#########################
# END INSTRUCTION PARSER
#########################


####################################################################################################
# get_help_message
####################################################################################################
# Revision History :
#   2017-05-25 AdBa : Function created
####################################################################################################
def get_help_message(with_details=False):
    """
    Prints information message about instruction.

    INPUT:
         with_details (Boolean) whether only general information about instruction should be 
            printed, or detailed.
    """

    print('ssh.')
    print('Controls ssh from machine (enables/disables it).')

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
#   2017-05-25 AdBa : Function created
####################################################################################################
def get_message(rabbit_master_object, base_instruction_message, command_arguments):
    """
    Sends a ssh status request to the RabbitMQ server

    INPUT:
         rabbit_master_object (Master) master controller, sending instruction to RabbitMQ server.
         base_instruction_message (lxml.etree) instruction to send camera
         command_arguments (str, opt) : timeout value

    OUTPUT:
        (lxml.etree) XML representation of instruction to send, as <camera instruction='...'>
        timeout value to apply
    """

    try:
    
        parsed_command_arguments, _ = argument_parser.parse_known_args(command_arguments)
        base_instruction_message.set('command', parsed_command_arguments.command)

    except SystemExit:
    
        argument_parser.print_usage()
        
        #############################################
        raise ValueError('Could not parse command.')
        #############################################

    # Reads values to sends (combines defaults and user selections
    remote_timeout = parsed_command_arguments.timeout

    ####################################################################################
    return base_instruction_message, rabbit_master_object.parse_timeout(remote_timeout)
    ####################################################################################

##################
# END get_message
##################


####################################################################################################
# process_response
####################################################################################################
# Revision History :
#   2017-05-25 AdBa : Function created
####################################################################################################
def process_response(_, received_worker_message):
    """
    Processes ssh report from a worker.

    INPUT:
         master (Master) Unused here.
         received_worker_message (lxml.etree object) message from worker as
            <worker id=... status=...>
    """

    del received_worker_message

    print('Ssh response received.')
    
    try:

        pass

    except Exception as e:
        
        print('Could not parse response' + str(e))
    
    #######
    return
    #######

#######################
# END process_response
#######################
