#########################
# Import Global packages
#########################
import os

#######################
# Import Local package
#######################
from python.global_libraries import general_utils  # Generic functions


####################################################################################################
# convert_magnitude
####################################################################################################
# Revision History :
#   2017-05-22 Adba : Function created
####################################################################################################
def convert_magnitude(byte_value):
    """
    Converts bytes used to a string as (e.g.) 1B, 2K, 3M, 4G to get appropriate magnitude

    INPUT
        byte_value (int) number of byte

    OUTPUT
        (str) number of bytes converted to the appropriate magnitude (byte, kb, mb, gb)
    """
    
    if byte_value < 1024:
        
        # Bytes
        size_as_string = '%dB' % byte_value

    elif byte_value < 1048576:

        # Kilo.
        size_as_string = '%.2fK' % (1.0 * byte_value / 1024)

    elif byte_value < 1073741824:

        # Mega
        size_as_string = '%.2fM' % (1.0 * byte_value / 1048576)

    else:

        # Giga
        size_as_string = '%.2fG' % (1.0 * byte_value / 1073741824)
        
    ######################
    return size_as_string
    ######################

########################
# END convert_magnitude
########################


####################################################################################################
# execute
####################################################################################################
# Revision History :
#   2017-05-22 Adba : Function created
####################################################################################################
def execute(_, instruction_as_xml, worker_base_response):
    """
    Processes space instruction

    INPUT
         _ (Worker) worker instance
         instruction_as_xml (lxml.etree) message to process
         worker_base_response (lxml.etree) base of worker response on which to build

    OUTPUT
         (lxml.etree) worker response, with info about sensor on the one-wire bus
    """

    del instruction_as_xml

    space_response = worker_base_response

    try:

        space_info = os.statvfs('/')
        free_space = space_info.f_bavail * space_info.f_frsize
        total_space = space_info.f_blocks * space_info.f_frsize
        used_space = (space_info.f_blocks - space_info.f_bfree) * space_info.f_frsize

        space_response.set('total', convert_magnitude(total_space))
        space_response.set('used', convert_magnitude(used_space))
        space_response.set('free', convert_magnitude(free_space))

        status_code = 0

    except OSError as exception:

        # Failed to call function because number of arguments did not match
        status_code = general_utils.log_error(-601, error_details=exception)

    space_response.set('status', str(status_code))

    #######
    return
    #######

##############
# END execute
##############
