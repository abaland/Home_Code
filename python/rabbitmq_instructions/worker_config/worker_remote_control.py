#########################
# Import Global Packages
#########################
from py_irsend import irsend
import traceback  # Gets full information about unhandled exceptions

###########################
# Declare Global Variables
###########################
from python.global_libraries import general_utils  # Generic functions


####################################################################################################################
# execute
####################################################################################################################
def execute(_, instruction_as_xml, worker_base_response):
    """
    Processes camera instruction

    INPUT:
         worker (Worker): worker instance
         instruction_as_xml (lxml.etree): message to process
         base_response (lxml.etree): base of worker response on which to build

    OUTPUT :
         all_1wire_statuses (lxml.etree): worker response, with info about sensor on the one-wire bus

    Revision History :
        2016-09-30 Adba : Function created
    """
    
    # Creates base response to be completed in instruction
    remote_control_response = worker_base_response
    status_code = 1

    # Gets value from message
    remote_to_use = instruction_as_xml.get('remote')
    button_to_press = instruction_as_xml.get('button')

    if remote_to_use is not None and button_to_press is not None:

        try:

            if remote_to_use not in irsend.list_remotes():

                status_code = general_utils.log_error(-501, remote_to_use)

            elif button_to_press not in irsend.list_codes(remote_to_use):

                status_code = general_utils.log_error(-502, button_to_press)

            else:

                irsend.send_once(remote_to_use, [button_to_press])
                status_code = 0

        except Exception as unhandled_exception:

            # Unforeseen exception has occured. Log it for analysis, with all information about where it happened
            full_error_message = traceback.format_exc()
            status_code = str(general_utils.log_error(-999,
                                                      error_details=unhandled_exception,
                                                      python_error_message=full_error_message))

    remote_control_response.set('status', str(status_code))

    ###############################
    return remote_control_response
    ###############################

##############
# END execute
##############
