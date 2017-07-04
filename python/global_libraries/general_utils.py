#########################
# Import Global Packages
#########################
import os
import syslog
import time
import logging
import logging.handlers


__author__ = 'Adrien Baland'
__version__ = '1.0.2'


custom_logger = None

all_error_messages = {
    # Loading / Input interpretation
    -1: 'Configuration section was missing.',
    -2: 'Configuration option parameter missing.',
    -3: 'RabbitMQ port must be an integer (not a string).',
    -4: 'Found unexpected arguments which will be ignored : ',
    -5: 'Could not convert timeout value to float. Using default value. ',
    -6: 'Timeout value must have a positive value. Using default value. ',
    -7: 'No commands were provided and no flag for live commands was found. Nothing to do.',
    -8: 'Encountered an empty instruction. Ignoring',
    -9: 'Encountered an non-valid instruction. Ignoring. ',
    -10: 'Encountered more/less arguments than required for instruction. Skipping the instruction.',
    -11: 'No instruction given. To quit the code, type "exit"',
    -12: 'Exactly one value (float/int) must be given after the timeout instruction',
    -13: 'Inappropriate arguments for instruction to send.',
    -14: 'Module missing required base instructions (get_message, process_response, help_message)',
    -15: 'No worker Id given in argument',
    ##################
    # RabbitMQ server
    ##################
    -101: 'Rabbit credentials wrong.',
    -106: 'Failed to acknowledge the message.',
    -108: 'Failed to stop consumption from bound queues.',
    #######
    # LXML
    #######
    -200: 'Failed to interpret worker response as xml tree.',
    -201: 'Response was not supposed to be received by the worker.',
    -202: 'Response was already received from that worker.',
    ################################
    # RabbitMQ instruction provided
    ################################
    -301: 'Timeout value header could not be interpreted. Ignoring.',
    -302: 'Could not interpret the instruction received. Skipping instruction.',
    -303: 'Received non-default instruction although default configuration. Skipping instruction',
    -304: 'No module could be found for instruction. Maybe the config version is not latest.',
    -305: 'Failed to interpret new configuration. Aborting update.',
    -306: 'Failed to create files/folder for the worker configuration folder',
    -307: 'Within-module command invalid.',
    ###########
    # Sensors
    ###########
    # Loading / Input interpretation errors
    -401: 'Could not locate config file.',
    -402: 'Unsupported type for sensor.',
    -403: 'Missing type of address for sensor.',
    -404: 'Not valid address for sensor.',
    -405: 'No/Wrong correction for sensor.',
    -406: 'No output_directory for sensor.',
    -407: 'No location for sensor.',
    -408: 'Could not create output directories.',
    -409: 'Failed to get information from sensor.',
    -410: 'Could not write file.',
    -411: 'Could not delete file.',
    -412: 'Missing/Wrong parameters value in config file.',
    -413: 'Outlier filtered.',
    -414: 'Redundancy in sensors.',
    -415: 'No sensors found in configuration file.',
    -416: 'Failed to parse heater information.',
    -417: 'Failed to control heaters.',
    -418: 'Could not load module.',
    -419: 'Failed to connect to website.',
    -420: 'Wrong warmup for sensor.',
    -421: 'Could not read pin value.',
    -422: 'Could not set pin value.',
    -423: 'No valid sensor could be found.',
    -424: 'Missing measure from sensor.',
    -425: 'Problem with sensor module.',
    ###########
    # Infrared
    ###########
    -501: 'Remote name is not in available remotes.',
    -502: 'Too many/few arguments for remote information to send.',
    -503: 'Could not create wave with given pulses.',
    -504: 'Wave id to send is nost listed in available wave ids.',
    -505: 'Argument for configuration is invalid.',
    -506: 'Error in SignalSender.',
    -507: 'Pigpio package error',
    ##########
    # OS
    ##########
    -601: 'Could not get space information',
    ##########
    # General
    ##########
    -994: 'Mail client handler is not properly configured',
    -995: 'Could not set up custom logger',
    -996: 'Custom logger did not have correct permissions.',
    -997: 'Failed to reboot worker.',
    -998: 'Interrupted by user.',
    -999: 'Others.'
}


####################################################################################################
# setup_log_file
####################################################################################################
# Revision History:
#    2017-02-10 AdBa: Created the function
#    2017-02-17 AdBa: Changed permission check
####################################################################################################
def setup_log_file(log_file_url, logger_name):
    """
    Sets up an custom log file (instead of default syslog) for error messages.

    INPUT:
        log_file_url (str) : Candidate url to use for custom log file
    """

    parent_folder = os.path.dirname(log_file_url)

    # Creates necessary directories if they did not exist already
    if not os.path.exists(parent_folder):

        try:

            # Creates directories recursively to reach desired address
            os.makedirs(parent_folder)

        except OSError as e:

            # Could not create all directories, so stop code execution
            ##############################################################
            return log_error(-410, parent_folder, str(e))
            ##############################################################

    # Parent folder has been created or already existed. Checks if write permission for log file
    try:

        # Permissions ok, assign the custom logger
        global custom_logger
        custom_logger = logging.getLogger(logger_name)
        custom_logger.setLevel(logging.DEBUG)

        # create console handler and set level to debug
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)

        # create formatter
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

        # Add the log message handler to the logger
        handler = logging.handlers.TimedRotatingFileHandler(log_file_url, when='D', interval=7,
                                                            backupCount=5)
        handler.setFormatter(formatter)
        custom_logger.addHandler(handler)

        #########
        return 0
        #########

    except IOError as e:

        # Permissions were not valid, so log error and give up (will be put in syslog)
        #############################################
        return log_error(-996, log_file_url, str(e))
        #############################################

#####################
# END setup_log_file
#####################


####################################################################################################
# write_to_log
####################################################################################################
# Revision History:
#    2017-02-10 AdBa: Created the function
####################################################################################################
def write_to_log(message, error_level):
    """
    Writes a message into the log with the appropriate level (info, error, warning).
    If no custom logger have been setup, message is printed to syslog

    INPUT:
        message (str) : Message to log
        error_level ({'info','error','warning'})
    """

    print(message)
    if custom_logger is None:

        syslog.syslog(message)

    elif error_level == 'error':

        custom_logger.error(message)

    elif error_level == 'warning':

        custom_logger.warning(message)

    elif error_level == 'info':

        custom_logger.info(message)

    else:

        # Unhandled case : go back to default syslog.
        syslog.syslog(message)

    #########
    return 0
    #########

###################
# END write_to_log
###################


####################################################################################################
# test_fatal_error
####################################################################################################
# Revision History:
#    2016/07/29 AdBa: Created the function
####################################################################################################
def test_fatal_error(class_instance, class_title):
    """
    Tests whether a fatal error has occurred and exits code if it has.

    INPUT:
        class_instance (Class) : An class instance with an integer 'status' property.
        class_title (str) : name of the class using this function. (Worker / Master / ...)
    """
    
    if class_instance.error_status != 0:

        # Fatal error occurred
        write_to_log('A fatal error has occured.', 'error')
        get_welcome_end_message(class_title, False)
        
        exit(1)
    
    # No fatal error
    ######
    return
    ######

#######################
# END test_fatal_error
#######################


####################################################################################################
# get_welcome_end_message
####################################################################################################
# Revision History:
#    2016/11/26 AdBa: Created the function
####################################################################################################
def get_welcome_end_message(class_title, is_start):
    """
    Prints introductory message or termination messagefor the code

    INPUT:
        class_title (str) : name of the class using this function. (Worker / Master / ...)
        class_title (bool) : whether the message is welcoming or terminating.
    """

    time_as_string = str(convert_localtime_to_string(time.localtime()))
    message_to_print = 'Starting ' if is_start else 'Ending '
    message_to_print += 'code %s. UTC %s. Version %s.\n' % (str(class_title),
                                                            time_as_string,
                                                            str(__version__))

    write_to_log(message_to_print, 'info')

    #######
    return
    #######

##############################
# END get_welcome_end_message
##############################


####################################################################################################
# log_error
####################################################################################################
# Revision History:
#    2016/07/29 AdBa: Created the function
####################################################################################################
def log_error(error_code, error_details=None, python_message=None):
    """
    Print an appropriate error message given a code

    INPUT:
    code (int) : the error number
    details (str) : details to complement the generic error message.
    error_message (str) : Explanation on why error occured. Usually holds python exception messages

    OUTPUT:
    code (int) : code given as input.

    EXAMPLE :
        log_error(-102, queue_name, pika_error)

    """

    base_error_message = all_error_messages.get(error_code, 'Unlisted error')

    write_to_log('ERROR %d : %s.' % (error_code, base_error_message), 'error')

    if error_details is not None:

        write_to_log(str(error_details) + '.', 'error')

    if python_message is not None:

        write_to_log(str(python_message), 'error')

    ##################
    return error_code
    ##################

################
# END log_error
################


####################################################################################################
# log_message
####################################################################################################
# Revision History:
#    2016/11/26 AdBa: Created the function
####################################################################################################
def log_message(message_to_log):
    """
    Print provided message to syslog

    INPUT:
        message_to_log (str) : The message to print inside the log

    OUTPUT:
        code (int) : code given as input.

    EXAMPLE :
        log_error(-102, queue_name, pika_error)

    """

    if message_to_log is not None:

        write_to_log(str(message_to_log), 'warning')

    #######
    return
    #######

##################
# END log_message
##################


####################################################################################################
# convert_message_to_xml
####################################################################################################
# Revision History:
#    2016/11/26 AdBa: Created the function
####################################################################################################
def convert_message_to_xml(xml_message_as_string):
    """
    Attemps to converts a XML-formatted message from a string to an lxml.etree object

    INPUT:
        xml_message_as_string (str) : an XML object formatted as a string

    OUTPUT:
        (lxml.etree|None) same XML object formatted as lxml.etree. None if error occured during 
            conversion.
    """

    from lxml import etree  # Converts some of the message (in a xml format) to a xml-like object

    worker_message_tree = None

    try:
        # Converts response from worker to XML tree
        worker_message_tree = etree.fromstring(xml_message_as_string)

    # The response string had a wrong format or did not follow the XML syntax.
    except (ValueError, etree.XMLSyntaxError) as e:

        log_error(-200, error_details=str(xml_message_as_string), python_message=e)

    ###########################
    return worker_message_tree
    ###########################

#############################
# END convert_message_to_xml
#############################


####################################################################################################
# Function (convert_localtime_to_string)
####################################################################################################
# Revision History:
#    2016/11/26 AdBa: Created the function
####################################################################################################
def convert_localtime_to_string(stamp, date_time_separator=' '):
    """
    Converts a time.localtime() object to a string formatted as YYY-MM-DD hh:mm:ss

    INPUT:
        Stamp (time.localtime()) : time.localtime object to convert
        Date_Time_Separator (str) : separator between the date part and the hour part.

    RETURNS:
        (str) string-formatted timestamp
    """

    formatted_stamp = '%04d-%02d-%02d%s%02d:%02d:%02d' % (stamp[0], stamp[1], stamp[2],
                                                          date_time_separator,
                                                          stamp[3], stamp[4], stamp[5])

    #######################
    return formatted_stamp
    #######################

##################################
# END convert_localtime_to_string
##################################


####################################################################################################
# Function (delete_os_file)
####################################################################################################
# Revision History:
#    2016/11/26 AdBa: Created the function
####################################################################################################
def delete_os_file(file_name):
    """
    Deletes file on OS filesystem.

    INPUT:
        file_name (str) : URl of the file to delete

    RETURNS:
        (int) 0 if successfull, negative number if error occured
    """

    try:

        if os.path.isfile(file_name):

            os.remove(file_name)

    except OSError as e:

        ##########################################
        return log_error(-411, file_name, str(e))
        ##########################################

    #########
    return 0
    #########

#####################
# END delete_os_file
#####################


####################################################################################################
# Function (create_os_file)
####################################################################################################
# Revision History:
#    2016/11/26 AdBa: Created the function
####################################################################################################
def create_os_file(file_name, file_content):
    """
    Creates and initializes file on OS filesystem.

    INPUT:
        file_name (str) : URl of the file to create
        file_content (str) : The content to write inside the file

    RETURNS:
        (int) 0 if successfull, negative number if error occured
    """

    try:

        # Creates output file, write value in it, and close the file (Part Latest data)
        output_file = open(file_name, 'wb')
        output_file.write(file_content)
        output_file.close()

    except OSError as e:

        ##########################################
        return log_error(-410, file_name, str(e))
        ##########################################

    #########
    return 0
    #########

#####################
# END create_os_file
#####################
