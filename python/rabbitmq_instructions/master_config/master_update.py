import argparse
from lxml import etree
import os

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
# Revision History:
#   2016-11-26 AB - Function Created
####################################################################################################
def get_help_message(with_details=False):
    """
    Prints information message about instruction.

    INPUT:
         with_details (Boolean) whether only general information about instruction should be 
            printed, or detailed.
    """

    print('update.')
    print('Orders worker to update its configuration, by copying configuration in '
          'worker_config_main.')
    print('Compares it with current time of this program.')

    if with_details:
        
        argument_parser.print_help()

    #######
    return
    #######

#######################
# END get_help_message
#######################


####################################################################################################
# copy_folder_structure
####################################################################################################
# Revision History:
#   2016-11-26 AB - Function Created
####################################################################################################
def copy_folder_structure(base_instruction_message, main_config_folder_name,
                          worker_config_folder_name):
    """
    Converts the configuration folder to be used by worker into a xml-formatted string.

    INPUT:
         Rabbit_Main_Object (Main)  main controller, sending instruction to RabbitMQ server.
         my_time_out (str, opt) : timeout value

    OUTPUT:
        message (str): worker config-folder formatted as xml
        timeout (float): the timeout value to apply
    """
    
    # Names where worker config folder is in Main Controller system, and in the Worker system.
    base_instruction_message.set('to_delete', worker_config_folder_name)
    
    # Creates top folder as <dir name='config_updated' parent='.'>, which will be parent of all
    # other items.
    config_as_xml = etree.Element('dir', name=worker_config_folder_name, parent='')
    
    # Goes through worker configuration folder to create other entries in the xml-formatted string
    for config_top_folder_names, config_folder_names, config_file_names in os.walk(
            main_config_folder_name):
        
        # Updates file/folder parent path to respect parent architecture instead of worker one.
        config_top_folders_name_new = str(config_top_folder_names)\
            .replace(main_config_folder_name, worker_config_folder_name)

        # Adds all folders from the configuration
        for config_folder_name in config_folder_names:

            xml_to_append = etree.Element('dir', name=str(config_folder_name),
                                          parent=str(config_top_folders_name_new))
            config_as_xml.append(xml_to_append)
        
        # Adds all .py files from the configuration
        for config_file_name in config_file_names:
            
            if not config_file_name.endswith('.py'):

                continue

            xml_to_append = etree.Element('file', name=str(config_file_name),
                                          parent=str(config_top_folders_name_new))
            
            with open(config_top_folder_names + '/' + config_file_name, 'r') as Config_File:

                xml_to_append.text = Config_File.read()

            config_as_xml.append(xml_to_append)

    base_instruction_message.append(config_as_xml)
    
    #######
    return
    #######

############################
# END copy_folder_structure
############################


####################################################################################################
# get_message
####################################################################################################
# Revision History:
#   2016-11-26 AB - Function Created
####################################################################################################
def get_message(rabbit_main_object, base_instruction_message, command_arguments):
    """
    Converts the configuration folder to be used by worker into a xml-formatted string.
    Only folder + files ending with extension .py get converted
    Each file/folder will have its own tag (<dir> or <file>) and file content will be in their text 
    attribute.

    INPUT:
         main (Main) : the main controller object, sending instruction to the RabbitMQ server.
         my_time_out (str, opt) : timeout value

    OUTPUT:
        message (str): worker config-folder formatted as xml
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

    computer_python_code_folder = '/Users/abaland/IdeaProjects/Home_Code/python'
    raspberry_python_code_folder = '/home/pi/Home_Code/python'

    # Goes through the hierarchy
    copy_folder_structure(base_instruction_message, computer_python_code_folder,
                          raspberry_python_code_folder)
    
    # Converts the object to a string.
    ###################################################################################
    return base_instruction_message, rabbit_main_object.parse_timeout(input_timeout)
    ###################################################################################

##################
# END get_message
##################


####################################################################################################
# process_response
####################################################################################################
# Revision History:
#   2016-11-26 AB - Function Created
####################################################################################################
def process_response(_, received_worker_message):
    
    del received_worker_message
    
    #######
    return
    #######

#######################
# END process_response
#######################
