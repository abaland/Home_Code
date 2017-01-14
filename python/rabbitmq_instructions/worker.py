"""
This module creates worker for a RabbitMQ-communication system. Given a specific id, it will receive id-related
instruction to execute sequentially from a RabbitMQ-server, process those reques, and eventually send response if it
is necessary.
"""

#########################
# Import Global Packages
#########################
import argparse  # Used to parse command line arguments
import os  # Facilitates update of configuration folders
import shutil  # Facilitates update of configuration folders
import sys  # Core library to get command line inputs
import time  # Waits appropriate amount of time
import traceback  # Gets full information about unhandled exceptions

import pika  # RabbitMQ Python port
import psutil  # Gets information about CPU usage and processes
from lxml import etree  # Converts some of the message (in a xml format) to a xml-like object

from python.global_libraries import general_utils  # Generic functions + Logs errors / messages in console and syslog
from python.global_libraries import pika_connector_manager  # Handles connection with RabbitMQ server
from worker_config import config_general

###########################
# Declare Global Variables
###########################
rabbit_configuration_filename = '/home/pi/Home_Code/configs/RabbitMQConfig.ini'  # Configuration file

####################################################################################################################
# CODE START
####################################################################################################################


####################################################################################################################
# RabbitWorker
####################################################################################################################
# Revision History :
#   2016-11-26 AdBa : Class created
####################################################################################################################
class RabbitWorker:

    ####################################################################################################################
    # __init__
    ####################################################################################################################
    # Revision History :
    #   2016-11-26 AB : Function created
    ####################################################################################################################
    def __init__(self, configuration_filename):
        """
        Creates a Worker instance, which opens a RabbitMQ connection to the RabbitMQ server.
        A worker always listens to 'update' instructions and listen to other instructions depending on its id

        INPUT:
            configuration_filename (str) : path to the RabbitMQ configuration file
        """

        # Connexion with RabbitMQ server
        self.pika_connector = pika_connector_manager.PikaConnectorManager(self)
        self.pika_connector.load_config(configuration_filename)
        self.pika_connector.establish_rabbit_connection()
        
        # Working status. If 0 : everything is fine. Otherwise, contains code for fatal error that occured
        self.error_status = self.pika_connector.error_status
        
        # Name of exchange to use to communicate with RabbitMQ server
        self.exchange_name = ''
        
        # Worked name/id. Determines which queue the worker listens to and is submitted in the worker responses
        self.worker_id = ''
        
        # Keys that a worker listens to. Update and heartbeat are always there, since they allow worker to signal they
        # exist and to update their configurations
        self.accepted_keys = ['update', 'heartbeat']
        
        # Whether to restart worker after config update. False = No restart. True = restart.
        # Warning : requires a "run script on restart" with /etc/rc.local)
        self.restart_flag = False
        
        # Sandbox for worker config modules to store values. Due to reload of configuration that reloads modules from
        #   scratch, there is a need for a parameters that memorizes values inside a worker through reload. To avoid
        #   conflict between module, each key in the sand_box should match the instruction name.
        # Example : worker.sand_box['remote'] = [1,2,3]
        self.sand_box = {}
        
    ###############
    # END __init__
    ###############

    #
    #
    #
        
    ####################################################################################################################
    # on_connection_recovery
    ####################################################################################################################
    # Revision History :
    #   2016-11-26 AB : Function created
    ####################################################################################################################
    def on_connection_recovery(self):
        """
        Recreates all elements that need to be recreated when connection to RabbitMQ server was lost and is recovered.
        """
        
        # Redeclares exchange
        self.set_exchange(self.exchange_name)
        
        # Recreates / rebinds queues
        self.link_queue_to_worker()
        
        ######
        return
        ######
    #########################
    # on_connection_recovery
    #########################
    
    #
    #
    #

    ####################################################################################################################
    # set_exchange
    ####################################################################################################################
    # Revision History :
    #   2016-11-26 AB : Function created
    ####################################################################################################################
    def set_exchange(self, exchange_name):
        """
        Sets exchange to be used by worker in its transactions with RabbitMQ server

        INPUT:
            exchangeName (str) : name of the exchange to use
        """
    
        # Declares the exchange used to communicate
        self.exchange_name = exchange_name
        self.pika_connector.declare_exchange(self.exchange_name)
        self.error_status = self.pika_connector.error_status
    
    ###################
    # END set_exchange
    ###################

    #
    #
    #

    ####################################################################################################################
    # make_base_response
    ####################################################################################################################
    # Revision History :
    #   2016-11-26 AB : Function created
    ####################################################################################################################
    def make_base_response(self):
        """
        Creates the common base for all worker response, whatever the instruction. This base has the form
            <worker id='workerId' status='F' version=[0|1|2]>.
        All responses from worker have this as root, with 'S' status instead in case of success, 'F' if failure
        Version attribute is 0 if all versions are up-to-date, 1 or 2 otherwise.
        
        INPUT:
            version_status (int) : up-to-date status for code versions

        OUTPUT:
            worker_based_response (etree Element) : root element for future worker responses
        """
        
        worker_based_response = etree.Element('worker',
                                              id=str(self.worker_id),
                                              status='1',
                                              timestamp=general_utils.convert_localtime_to_string(time.localtime()),
                                              version=str(general_utils.__version__),
                                              cpu=str(psutil.cpu_percent()))
        
        #############################
        return worker_based_response
        #############################
    
    #########################
    # END make_base_response
    #########################

    #
    #
    #

    ####################################################################################################################
    # update_config
    ####################################################################################################################
    # Revision History :
    #   2016-11-26 AB : Function created
    ####################################################################################################################
    def update_config(self, message_as_xml, worker_base_response):
        """
        Updates configuration folder when Master Controller calls for an update. This overwrites the whole config
        folder.

        INPUT:
            body (str) : workerConfiguration folder content in a xml-format

        OUTPUT:
            config_update_status (str) : config update status report in the form <worker id=... status=...>
        """

        # Initializes the update status report to Failure (changed to Success only at the end, if everything succeeded)
        configuration_updated_status = worker_base_response

        self.restart_flag = True
        
        # The message could be interpreted as a XML tree, so delete the configuration folder and replace it
        shutil.rmtree(message_as_xml.get('to_delete'), True)

        # Creates config folder. If an error occurs, delete whole folder to avoid partial configurations
        try:

            for directory_to_create in message_as_xml.iter('dir'):

                parent_directory_url = directory_to_create.get('parent')
                
                if parent_directory_url == '':
    
                    os.mkdir(directory_to_create.get('name'))
                    
                else:
    
                    os.mkdir(parent_directory_url + '/' + directory_to_create.get('name'))
                
            for file_to_create in message_as_xml.iter('file'):

                with open(file_to_create.get('parent') + '/' + file_to_create.get('name'), 'w') as file_object:

                    if file_to_create.text is not None:
                        
                        file_object.write(file_to_create.text)

            # Update succeded, so set request status to Success
            configuration_updated_status.set('status', '0')

        # Error occured while adding files / directories in the configuration folder.
        except OSError as e:

            self.error_status = general_utils.log_error(-306, python_error_message=str(e))
            general_utils.log_message('Aborting configuration update.')

        ####################################
        return configuration_updated_status
        ####################################
    
    ####################
    # END update_config
    ####################

    #
    #
    #

    ####################################################################################################################
    # send_response
    ####################################################################################################################
    # Revision History :
    #   2016-11-26 AB : Function created
    ####################################################################################################################
    def send_response(self, in_properties, response_to_send):
        """
        Sends response to RabbitMQ server.

        INPUT:
             in_properties (pika properties) : properties received in the callback function used by Pika
             response_to_send (str) : response content
        """
        
        # Sends a response if the RabbitMQ message contains information about where to send it.
        # This should always be the case, but better make sure
        if in_properties.reply_to is not None:

            out_properties = pika.BasicProperties(delivery_mode=2,  # Make message persistent
                                                  correlation_id=in_properties.correlation_id)  # Links response+message
                
            # Publishes message
            self.pika_connector.publish_message('', in_properties.reply_to, response_to_send, out_properties)
                                            
        #######
        return
        #######
    
    ####################
    # END send_response
    ####################

    #
    #
    #

    ####################################################################################################################
    # get_response
    ####################################################################################################################
    # Revision History :
    #   2016-11-26 AB : Function created
    ####################################################################################################################
    def get_response(self, instruction_name, message_to_process):
        """
        Executes appropriate instruction, gets an answer, and returns it

        INPUT:
            instruction (str) : the instruction to execute
            message_to_process (lxml.etree): message received through RabbitMQ

        OUTPUT:
            response_to_send (lxml.etree) : response to send the RabbitMQ server (before string conversion)
        """
        
        response_to_send = self.make_base_response()
        finished_processing = False
        
        # Update configuration and heartbeat are special. They exist for all workers.
        # Sends an acitivity signal with worker ID
        if instruction_name == 'heartbeat':

            response_to_send.set('status', '0')
            finished_processing = True
        
        # Creates the worker-specific configuration
        if instruction_name == 'update':

            response_to_send = self.update_config(message_to_process, response_to_send)
            finished_processing = True

        # Received a non-default instruction although current worker config is default.
        # Instruction cannot be processed => skip it and return empty answer
        if not finished_processing and config_general.is_default:

            general_utils.log_error(-303)
            finished_processing = True

        # If instruction was not default, look at configuration folder for function to use
        if not finished_processing:
    
            # Get appropriate module from the configuration folder to compute a response
            appropriate_module = config_general.instruction_to_module.get(instruction_name, None)
    
            # Calls the module execute function and returns its output (should be the response to send)
            if appropriate_module is not None:

                response_to_send = appropriate_module.execute(self,
                                                              message_to_process,
                                                              response_to_send)

            else:
    
                # No appropriate module could be found, so impossible to process,
                general_utils.log_error(-304)

        ########################
        return response_to_send
        ########################
    
    ###################
    # END get_response
    ###################

    #
    #
    #

    ####################################################################################################################
    # apply_reboot
    ####################################################################################################################
    # Revision History :
    #   2016-11-26 AB : Function created
    ####################################################################################################################
    def apply_reboot(self, pika_method):
        """
        Processes how worker should reboot and terminates/closes relevant processes

        INPUT:
            pika_method (pika object) : !!!!NO IDEA!!!!
        """

        # Stops queue consumption (avoids messages trapped in  restarting worker)
        # Include a message acknowledgement
        self.pika_connector.stop_consume(pika_method)

        # Forces os reboot in worker.
        os.system('systemctl reboot -i')
    
        # NOTE : If this line is reached, the reboot failed.
        self.error_status = general_utils.log_error(-997)
        
        ######
        return
        ######

    ##################
    # END test_reboot
    ##################

    #
    #
    #

    ####################################################################################################################
    # must_be_filtered
    ####################################################################################################################
    # Revision History :
    #   2016-11-26 AB : Function created
    ####################################################################################################################
    def must_be_filtered(self, message_as_xml):
        """
        Checks if received instruction possesses a 'target' attribute, and if so, checks if the worker is in the target.
        If target exists but worker is not in it, Returns True

        INPUT:
             message_as_xml (lxml.etree) :
        """
    
        if 'target' in message_as_xml.attrib:
            
            all_targets = message_as_xml.get('target').split(',')
        
            if self.worker_id in all_targets:
                
                # Worker is among the target, so do not filter
                #############
                return False
                #############

            # Targets are given but worker not among them, so filter
            ############
            return True
            ############

        # No target is found, do not fitler to be safe.
        ############
        return True
        ############

    #######################
    # END must_be_filtered
    #######################

    #
    #
    #
    
    ####################################################################################################################
    # process_order
    ####################################################################################################################
    # Revision History :
    #   2016-11-26 AB : Function created
    ####################################################################################################################
    def process_order(self, _, pika_method, in_properties, message_received):
        """
        Defines how to process order from the master program.
        If the request has a timeout and the reception occurs too late : acknowledges messages and stops.
        Calls the appropriate instruction, sends an answer (optional + timeoutcheck) and acknowledges message afterwards
        The whole code might be restarted if the instruction processed required it

        INPUT:
             channel (pika object) : pika channel object. UNUSED Because available in the Worker.pika_connector object
             pika_method (pika object) : !!!!NO IDEA!!!!
             in_properties (pika Properties) : additional properties about the message received
             message_received (str) : message content
        """
        
        try:
            
            message_as_xml = general_utils.convert_message_to_xml(message_received)
            
            if message_as_xml is None or self.must_be_filtered(message_as_xml):
                
                self.pika_connector.acknowledge_message(pika_method)

                #######
                return
                #######
            
            instruction_name = message_as_xml.get('type')
            general_utils.log_message('Received %s request.' % (str(instruction_name),))
            
            # Apply the instruction to the message
            response_to_send = self.get_response(instruction_name, message_as_xml)
            response_to_send = etree.tostring(response_to_send)
        
            # Sends the response or not depending on current time and timeout
            self.send_response(in_properties, response_to_send)

        except KeyError as e:
            
            general_utils.log_error(-302, python_error_message=str(e))
            self.pika_connector.acknowledge_message(pika_method)

            #######
            return
            #######

        # Failed to send response => error with RabbitMQ connection => Cannot acknowledge
        if self.error_status != 0:
        
            #######
            return
            #######

        # Acknowledges message has been received and goes back to listening if no reboot required, restart otherwise.
        if self.restart_flag:

            self.apply_reboot(pika_method)

        else:
            self.pika_connector.acknowledge_message(pika_method)

        #######
        return
        #######
    
    ####################
    # END process_order
    ####################

    #
    #
    #

    ####################################################################################################################
    # get_queue_name
    ####################################################################################################################
    # Revision History :
    #   2016-11-26 AB : Function created
    ####################################################################################################################
    def get_queue_name(self, instruction_name):
        """
        Returns name of the queue to declare based on worker id and key to follow
        
        INPUT :
            key (str) : Name of the routing key for the queue

        OUTPUT :
            (str) Name of the queue to matching that key
        """
    
        queue_name = '' + str(self.worker_id) + '__' + instruction_name

        ##################
        return queue_name
        ##################

    #####################
    # END get_queue_name
    #####################

    #
    #
    #

    ####################################################################################################################
    # link_queue_to_worker
    ####################################################################################################################
    # Revision History :
    #   2016-11-26 AB : Function created
    ####################################################################################################################
    def link_queue_to_worker(self):
        """
        Declare queues in the system and makes the worker listen to message coming from these queues.
        Queues are durable, meaning they survive through crashes of RabbitMQ server and of the Worker
        """
        
        # Adds the queues using the pikaConnectorManager.
        self.pika_connector.declare_permanent_queues(self.accepted_keys, self.exchange_name, self.get_queue_name,
                                                     self.process_order)

        #######
        return
        #######
    
    ###########################
    # END link_queue_to_worker
    ###########################

    #
    #
    #
    ####################################################################################################################
    # get_valid_instructions
    ####################################################################################################################
    # Revision History :
    #   2016-11-26 AB : Function created
    ####################################################################################################################
    def get_valid_instructions(self):
        """
        Extracts appropriate routing keys (= instruction to obey to) given a worker ID.
        Keeps the default instructions in case of failure (heartbeat + update)
        """

        # Uses the configuration folder to get the mapping between workers and relevant instructions.
        # Gets the worker-relevant instructions using the worker ID
        print('Getting supported instruction..'),
        worker_specific_instructions = config_general.worker_to_instruction.get(str(self.worker_id), [])
        print ('Done.')
        
        # Appends all the obtained valid instructions to the internal list
        self.accepted_keys = ['heartbeat', 'update']
        if isinstance(worker_specific_instructions, list) and len(worker_specific_instructions) > 0:
        
            for instruction_name in worker_specific_instructions:
        
                self.accepted_keys.append(instruction_name)
        
        #######
        return
        #######
    
    #############################
    # END get_valid_instructions
    #############################

    #
    #
    #
    
    ####################################################################################################################
    # update_listened_queues
    ####################################################################################################################
    # Revision History :
    #   2016-11-26 AB : Function created
    ####################################################################################################################
    def update_listened_queues(self):
        
        old_instruction = set(self.accepted_keys)
        
        new_instructions = set(config_general.worker_to_instruction.get(self.worker_id, [])).union(
            {'heartbeat', 'update'})
        
        # List of keys that are not listened to anymore.
        to_remove_keys = list(old_instruction.difference(new_instructions))
        to_add_keys = list(new_instructions.difference(old_instruction))

        # Accepted keys must be updated BEFORE updating queues, because ConnectionException will recreate ALL queues
        #   => up-to-date accepted_keys required
        self.accepted_keys = list(new_instructions)

        # Remove not-listened-to-anymore instructions
        for to_remove_key in to_remove_keys:
            
            queue_name = '%s__%s' % (self.worker_id, to_remove_key)
            self.pika_connector.delete_permanent_queue(queue_name)

        # Adds the queues using the pikaConnectorManager.
        self.pika_connector.declare_permanent_queues(to_add_keys, self.exchange_name, self.get_queue_name,
                                                     self.process_order)

        #######
        return
        #######
    
    #########################
    # update_listened_queues
    #########################

    #
    #
    #

    ####################################################################################################################
    # parse_arguments
    ####################################################################################################################
    # Revision History :
    #   2016-11-26 AB : Function created
    ####################################################################################################################
    def parse_arguments(self, command_line_arguments):
        """
        Parse arguments from the command line to detect the worker id to use

        INPUT:
            command_line_args (str list)
        """

        # Creates a parser and sets its accepted arguments.
        argument_parser = argparse.ArgumentParser()
        argument_parser.add_argument('workerID', help='ID of the worker to create.', nargs='?')
    
        # Parses the arguments. Currently just the first positional argument
        print('Reading arguments..'),
        parsed_arguments, to_ignore_arguments = argument_parser.parse_known_args(command_line_arguments)
        print ('Done.')
    
        # If unhandled arguments exist, ignore them but print warning.
        if len(to_ignore_arguments) > 0:
            
            general_utils.log_error(-4, error_details=str(to_ignore_arguments))
            
        # Either assigns the given workerID, or stops because no workerID were given.
        if parsed_arguments.workerID is None:
            
            self.error_status = general_utils.log_error(-15)

        else:
            
            self.worker_id = parsed_arguments.workerID
        
        ######
        return
        ######
        
    ######################
    # END parse_arguments
    ######################

###################
# END RabbitMaster
###################


####################################################################################################################
# main
####################################################################################################################
# Revision History :
#   2016-11-26 AB : Function created
####################################################################################################################
def main(args):
    """
    Creates a worker and assigns him to the relevant queues depending on its workerId (command line argument)

    INPUT:
         args (str array) : command line arguments, should be [#workerId]
    """

    class_name = 'Worker'
    general_utils.get_welcome_end_message(class_name, True)

    # Creates worker and establishes connexion with the RabbitMQ server
    rabbit_worker_instance = RabbitWorker(rabbit_configuration_filename)
    general_utils.test_fatal_error(rabbit_worker_instance, class_name)

    # Sets the exchange to use for transactions
    rabbit_worker_instance.set_exchange('ex')
    general_utils.test_fatal_error(rabbit_worker_instance, class_name)
    
    # Reads the workerId provided. If none provided, there is nothing to do, so stop the code
    rabbit_worker_instance.parse_arguments(args)
    general_utils.test_fatal_error(rabbit_worker_instance, class_name)

    # Gets the keys for the relevant queues based on the workerId
    rabbit_worker_instance.get_valid_instructions()
    
    # Links the worker to all relevant queues
    rabbit_worker_instance.link_queue_to_worker()
    general_utils.test_fatal_error(rabbit_worker_instance, class_name)

    # Makes the worker start waiting for messages
    rabbit_worker_instance.pika_connector.start_consume()

    # If we reach this end, Worker stopped consuming. Either worker stopped, or an error occured
    general_utils.test_fatal_error(rabbit_worker_instance, class_name)
        
    general_utils.get_welcome_end_message('Worker', False)
    exit(0)

####################################################################################################################
# END main
####################################################################################################################

if __name__ == "__main__":

    try:

        main(sys.argv[1:])

    except Exception as unhandled_exception:
    
        # Unforeseen exception has occured. Log it for analysis, with all information about where it happened
        full_error_message = traceback.format_exc()
        general_utils.log_error(-999, error_details=unhandled_exception, python_error_message=full_error_message)
