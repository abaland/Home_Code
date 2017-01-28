########################
# Import Global package
########################
import argparse


####################################################################################################################
# DEFAULTS
####################################################################################################################

####################################################################################################################
# INSTRUCTION PARSER
####################################################################################################################
# Creates parser for all options in camera control
argument_parser = argparse.ArgumentParser()

# Instruction parameter : one of the available choices. REQUIRED
Remote_Name_To_Help = 'Remote to use.\n'
argument_parser.add_argument('remote_name', action='store', type=str, help=Remote_Name_To_Help)

# Framerate argument, integer
Button_To_Press_Help = 'Button to press on remote or configuration to send through IR (for aircon).'
argument_parser.add_argument('configuration', action='store', type=str, help=Button_To_Press_Help)

# Timeout argument
Timeout_Help = 'Number of seconds to wait for a response.\n'
argument_parser.add_argument('--timeout', '-t', action='store', nargs='?', type=int, help=Timeout_Help)

#########################
# END INSTRUCTION PARSER
#########################


####################################################################################################################
# get_help_message
####################################################################################################################
# Revision History :
#   2016-11-26 AdBa : Function created
####################################################################################################################
def get_help_message(with_details=False):
    """
    Prints information message about instruction.

    INPUT:
         with_details (Boolean) : whether only general information about instruction should be printed, or detailed.
    """

    print('remote_control.')
    print('Send remote controls instruction to controlled devices.')

    if with_details:
        
        argument_parser.print_help()

    #######
    return
    #######

#######################
# END get_help_message
#######################


####################################################################################################################
# get_message
####################################################################################################################
# Revision History :
#   2016-11-26 AdBa : Function created
####################################################################################################################
def get_message(rabbit_master_object, base_instruction_message, command_arguments):
    """
    Sends a camera status request to the RabbitMQ server

    INPUT:
         rabbit_master_object (Master) : the master controller object, sending instruction to the RabbitMQ server.
         instruction (str) : instruction to send camera
         my_time_out (str, opt) : timeout value

    OUTPUT:
        message (lxml.etree): XML representation of instruction to send, as <camera instruction='...'>
        timeout (float): the timeout value to apply
    """

    try:
    
        parsed_command_arguments, _ = argument_parser.parse_known_args(command_arguments)

    except SystemExit:
    
        argument_parser.print_usage()
        
        #############################################
        raise ValueError('Could not parse command.')
        #############################################

    # Reads values to sends (combines defaults and user selections
    remote_to_use = parsed_command_arguments.remote_name
    configuration_to_send = parsed_command_arguments.configuration
    remote_timeout = parsed_command_arguments.timeout

    # Creates camera instruction to send
    base_instruction_message.set('remote', remote_to_use)
    base_instruction_message.set('config', configuration_to_send)
    
    ####################################################################################
    return base_instruction_message, rabbit_master_object.parse_timeout(remote_timeout)
    ####################################################################################

##################
# END get_message
##################


####################################################################################################################
# process_response
####################################################################################################################
# Revision History :
#   2016-11-26 AdBa : Function created
####################################################################################################################
def process_response(_, received_worker_message):
    """
    Processes camera report from a worker.

    INPUT:
         master (Master) : Unused here.
         received_worker_message (lxml.etree object) : message from worker in the form <worker id=... status=...>
    """
    
    print('Remote control response received.')
    
    try:
        
        # Starts with no sensors detected
        print(received_worker_message.get('response'))
    
    except Exception as e:
        
        print('Could not parse response' + str(e))
    
    #######
    return
    #######

#######################
# END process_response
#######################
