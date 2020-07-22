"""Handles monitoring of the all the RabbitMQ-connected Pis.
 Periodically querries the raspberry with a heartbeat request.
 If a pi does not answer after 5 trials, send an email to warn, and flag Pi as unresponsive.
 At most one mail will be sent per day.
"""


##################
# Global packages
##################
import configparser  # Parses .ini files for config information
import os  # Interacts with filesystem (checks for config file exitence)
import time  # Makes sure correct amount of time is waited
from lxml import etree  # Converts some of the message (in a xml format) to a xml-like object
import traceback  # Gets full information about unhandled exceptions

#################
# Local packages
#################
from rabbitmq_instructions import main  # code for Rabbit Main Controller
from global_libraries import general_utils
from global_libraries import mail_sender


###################
# Global variables
###################

monitoring_config_url = '/Users/abaland/IdeaProjects/Home_Code/configs/heartbeatMonitorConfig.ini'


####################################################################################################
# CODE START
####################################################################################################


####################################################################################################
# HeartbeatMonitoring
####################################################################################################
# Revision History:
#   2017-11-21 AdBa - Class Created
####################################################################################################
class HeartbeatMonitoring:

    #
    #
    #

    ################################################################################################
    # __init__
    ################################################################################################
    # Revision History:
    #   2017-11-21 AdBa - Function Created
    ################################################################################################
    def __init__(self, rabbit_main_object):
        """
        Creates instance of Rabbit Main that will monitor activity of other pis
        
        INPUT:
            rabbit_main_object (RabbitMain) : instance of RabbitMain to send/receive message        
        """

        self.error_status = 0
        
        # Main Controller script
        self.rabbit_main = rabbit_main_object  # Reference to the Main Controller
        self.rabbit_main.forward_response_target = self  # Ref to this constructor inside main

        # Mail Sender object to send gmail failure report
        self.mail_sender = mail_sender.create_mail_sender()
        self.report_mail_destination = None

        # Checklists for workers whose activity must be monitored.
        self.activity_checklist = {}
        self.last_mail_sent = {}

        self.request_interval = 300  # Time between two heartbeat request to check activity
        self.mail_min_delay = 84000

    ###############
    # END __init__
    ###############

    #
    #
    #

    ################################################################################################
    # Function (read_configuration)
    ################################################################################################
    # Revision History:
    #   2017-11-21 AB - Function Created
    ################################################################################################
    def read_configuration(self, configuration_filename):
        """
        Reads configuration file containing all HeartbeatMonitor information and updates internal
        parameters accordingly
        Parameters include:
            All requirement time parameters to monitor heartbeat
            Instructions that can be sent to worker

        INPUT:
            configuration_filename (str) name of configuration file

        OUTPUT:
            error_code (int) 0 if no fatal error occured, negative integer otherwise
        """

        # List of all parameters which must be present in configuration file, and their type.
        # (1) Time interval (s) between two activity checks (integer)
        # (2) List of workers to watch (comma separated, spaces not supported in names)
        all_required_parameters = [['request_interval', int],
                                   ['mail_min_delay', int],
                                   ['all_workers', lambda x: x.replace(' ', '').split(',')],
                                   ['report_mail_destination', str]]

        # Dictionnary to hold the parsed information from configuration.
        parsed_parameters = {}

        # Checks that the configuration file does exist
        if not os.path.isfile(configuration_filename):
        
            ############################################################
            return general_utils.log_error(-401, configuration_filename)
            ############################################################

        # Creates configuration parser + parses
        parsed_configuration = configparser.RawConfigParser()
        parsed_configuration.read(configuration_filename)
    
        ###################################################
        # Checks if config parsing has required parameters
        ###################################################
        # Checks existence of general section
        if not parsed_configuration.has_section('General'):
        
            # Configuration file was missing required section, so stop execution
            ###############################################
            return general_utils.log_error(-419, 'General')
            ###############################################

        # Checks existence of all required (General, X) options.
        for required_parameter in all_required_parameters:

            if not parsed_configuration.has_option('General', required_parameter[0]):
    
                # Configuration file was missing required section, so stop execution
                ###########################################################
                return general_utils.log_error(-412, required_parameter[0])
                ###########################################################
            
            try:

                # Parse value as string, converts it to appropriate type, and puts it in dictionnary
                parsed_value = parsed_configuration.get('General', required_parameter[0])
                parsed_parameters[required_parameter[0]] = required_parameter[1](parsed_value)
    
            except ValueError as e:
                
                # Value did not match required type
                value_from_config = parsed_configuration.get('General', required_parameter)
                details = '(%s, %s)' % (required_parameter, value_from_config)
                #####################################################
                return general_utils.log_error(-412, details, str(e))
                #####################################################

        # Parsing finished successfully. Assigns values.
        self.request_interval = parsed_parameters['request_interval']
        self.report_mail_destination = parsed_parameters['report_mail_destination']
        self.mail_min_delay = parsed_parameters['mail_min_delay']
        for worker_id in parsed_parameters['all_workers']:
            self.activity_checklist[worker_id] = False
            self.last_mail_sent[worker_id] = -1

        #########
        return 0
        #########

    #########################
    # END read_configuration
    #########################

    #
    #
    #

    ################################################################################################
    # add_response
    ################################################################################################
    # Revision History:
    #   2017-11-21 AB - Function Created
    ################################################################################################
    def add_response(self, _, worker_id, worker_message_formatted):
        """
        Processed a worker response to an heartbeat request

        INPUT:
            instruction_name (str): (Useless) name of instruction worker responded to (heartbeat)
            worker_id (str): Name of the worker who responded
            worker_message_formatted (lxml.etree|None): Parsed response from worker
        """
    
        # If worker_message_formatted is None, worker_id failed to respond => Not alive
        # If worker_message_formatted is not None, worker_id alive
        if worker_message_formatted is not None:

            print('Worker %s is active!' % (worker_id,))
            # Worker was in fact active, update internal parameters
            self.activity_checklist[worker_id] = True
                        
        #######
        return
        #######

    ###################
    # END add_response
    ###################

    #
    #
    #

    ################################################################################################
    # send_failure_report
    ################################################################################################
    # Revision History:
    #   2017-11-21 AB - Function Created
    ################################################################################################
    def maybe_send_failure_report(self):
        """
        Send mail to report the inactive worker
        """

        message_to_send = 'Warning.\n\n' \
                          'The following worker(s) are missing activity reports:\n'
        send_message = False

        for worker_id in self.activity_checklist.keys():

            # Message must be sent only if it
            if not self.activity_checklist[worker_id] and \
                    time.time() > self.last_mail_sent[worker_id] + self.mail_min_delay:

                send_message = True
                message_to_send += worker_id + '\n'
                self.last_mail_sent[worker_id] = time.time()

        if send_message:

            self.mail_sender.send_message(message_to_send, self.report_mail_destination)

        #######
        return
        #######

    ##########################
    # END send_failure_report
    ##########################

    #
    #
    #

    ################################################################################################
    # monitor_activity
    ################################################################################################
    # Revision History:
    #   2017-11-21 AB - Function Created
    ################################################################################################
    def monitor_activity(self):
        """
        Applies one iteration of the worker activity monitoring
        """

        workers_to_monitor = self.activity_checklist.keys()
        for worker_id in workers_to_monitor:
            self.activity_checklist[worker_id] = False

        # Sends request to workers to check if they are active or not. The processing function
        #   will be called by the main object (self.rabbit_main) when it receives response
        base_instruction_message = etree.Element('instruction', type='heartbeat')
        self.rabbit_main.ask_worker('heartbeat', base_instruction_message, self.request_interval,
                                      workers_to_monitor)

        self.maybe_send_failure_report()

    #######################
    # END monitor_activity
    #######################

################################
# END HeartbeatMonitoringMain
################################


####################################################################################################
# main
####################################################################################################
# Revision History:
#   2017-11-21 AB - Function Created
####################################################################################################
def main():
    """
    Starts Heartbeat monitoring program
    """

    try:
        class_name = 'HeartbeatMonitor'
        general_utils.get_welcome_end_message(class_name, True)
    
        # Creates the instance for a main controller and sets it to GUI mode.
        # Sets no_block argument to prevent main from waiting for user command line inputs
        rabbit_main = main.main(['-no_block'])
    
        # Creates GUI Object, to update GUI window
        monitor = HeartbeatMonitoring(rabbit_main)
    
        # Reads config file to get relevant parameters (workers to monitor, monitoring interval)
        monitor.read_configuration(monitoring_config_url)

        # Only starts monitoring if mails can be sent.
        if monitor.mail_sender.test_credentials() and monitor.report_mail_destination is not None:

            # Starts monitoring
            while True:

                monitor.monitor_activity()

    except Exception as e:

        # Unforeseen exception occured. Log it for analysis, with full traceback about it
        full_error_message = traceback.format_exc()
        general_utils.log_error(-999, error_details=e, python_message=full_error_message)

    # Exits code
    general_utils.get_welcome_end_message('HeartbeatMonitor', False)

    #######
    return
    #######

###########
# END main
###########


if __name__ == "__main__":
    
    main()
