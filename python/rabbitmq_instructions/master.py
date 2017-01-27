"""
This module creates a master controller for a RabbitMQ-communication system. Given instructions, it will send them
to a RabbitMQ server for dispatch, and listen to incoming response for a given time.
"""

#########################
# Import Global Packages
#########################
import argparse  # Used to parse command line arguments
import sys  # Core library to get command line inputs
import shlex  # Converts command-line live inputs to array of arguments (as they appear in sys.argv)
import time  # Library to get current time
import uuid
import pika  # RabbitMQ Python port
from lxml import etree  # Converts worker response element to a tree-like object

########################
# Import Local Packages
########################
from python.rabbitmq_instructions.master_config import master_commands  # Message generation/procession on Master-Side
from python.rabbitmq_instructions.worker_config import config_general

from python.global_libraries import general_utils  # Generic functions
from python.global_libraries import pika_connector_manager  # Handles connection with RabbitMQ server

###########################
# Declare Global Variables
###########################
rabbit_configuration_filename = '/Users/abaland/IdeaProjects/Home_Code/configs/RabbitMQConfig.ini'  # Configuration

####################################################################################################################
# CODE START
####################################################################################################################


####################################################################################################################
# version_check
####################################################################################################################
# Revision History:
#   2016-11-26 AB : Function created
####################################################################################################################
def version_check(worker_message_tree):
    """
    Check version status report from worker and print warning if:
        (a) mismatch between worker_version and master_version
        (b) last warning was printed long ago

    INPUT:
        worker_message_tree (lxml.etree) : worker response as <worker id=... status=[S|F] version=NUM>...
    """

    try:

        # Converts response from worker to XML tree
        version_status = worker_message_tree.get('version')

        # Prints correct warning message
        if version_status != str(general_utils.__version__):

            general_utils.log_message('WARNING : CONFIGURATION NOT UP TO DATE.')

    except ValueError as e:

        # Could not interpret version status integer.
        general_utils.log_error(-200, python_error_message=e)

    #######
    return
    #######

    ####################
    # END version_check
    ####################


####################################################################################################################
# RabbitMaster
####################################################################################################################
# Revision History :
#   2016-11-26 AdBa : Class created
####################################################################################################################
class RabbitMaster:
    """
    Master instance, with a RabbitMQ connection to the RabbitMQ server.
    A master sends instructions to Worker instances through RabbitMQ
    """

    ####################################################################################################################
    # __init__
    ####################################################################################################################
    # Revision History:
    #   2016-11-26 AB : Function created
    ####################################################################################################################
    def __init__(self, configuration_filename):
        """
        Creates a Master instance, which opens a RabbitMQ connection to the RabbitMQ server.
        A master sends instructions to Worker instances through RabbitMQ
        
        INPUT:
            configuration_filename (str) : path to the RabbitMQ configuration file
        """
        
        # Connexion manager with RabbitMQ server
        self.pika_connector = pika_connector_manager.PikaConnectorManager(self)
        self.pika_connector.load_config(configuration_filename)
        self.pika_connector.establish_rabbit_connection()
        
        # Exchange used to communicate
        self.exchange_name = ''

        # Working status. If 0, everything is fine, otherwise a fatal error has occured
        self.error_status = self.pika_connector.error_status
        
        # List of instruction left to send the worker
        self.instruction_to_send = []
        
        # Latest instruction name + code, to match with response received
        self.sent_instruction_info = [None, None]

        # Default time to wait (s) for response from Workers
        self.response_wait_timeout = 10

        # List of bindings from instructions to workers that support them
        self.instruction_to_worker_list = {}
        
        # Checklist of worker response that have been received + total amount
        self.response_received_checklist = {}
        self.total_response_received = 0
        
        # Flag to allow the response queue queue to be deleted when the response timeout has elapsed.
        self.delete_queue_flag = False

        # Class Instance where Worker responses should be forwarded
        self.forward_response_target = None
        
        # Parameters in addition to KeyboardInterrupt or timeout to stop listening for worker responses
        self.keep_listening_for_response = True

        # Whether to return the created object immediately or to switch to CL feed.
        self.has_commandline_feed = False

    ###############
    # END __init__
    ###############

    #
    #
    #

    ####################################################################################################################
    # set_exchange
    ####################################################################################################################
    # Revision History:
    #   2016-11-26 AB : Function created
    ####################################################################################################################
    def set_exchange(self, exchange_name):
        """
        Sets exchange to be used by worker in its transactions with RabbitMQ server

        INPUT:
            exchange_name (str) : name of the exchange to use
        """
    
        # Declares the exchange used to communicate
        self.exchange_name = exchange_name
        self.pika_connector.declare_exchange(self.exchange_name)
        self.error_status = self.pika_connector.error_status

        #######
        return
        #######

    ###################
    # END set_exchange
    ###################

    #
    #
    #
    
    ####################################################################################################################
    # get_instruction_to_worker
    ####################################################################################################################
    # Revision History:
    #   2016-11-26 AB : Function created
    ####################################################################################################################
    def get_instruction_to_worker(self):
        """
        Initiates the binding from instruction to workers that support them. This reverses the binding in
            worker_to_instruction.
        """

        # Gets the worker to instruction mapping, to reverse.
        worker_to_keys = config_general.worker_to_instruction

        # Initializes an array (which will contain the workers) for each instruction
        self.instruction_to_worker_list['heartbeat'] = []
        self.instruction_to_worker_list['update'] = []
        for worker_instruction in master_commands.all_instructions:

            self.instruction_to_worker_list[worker_instruction] = []

        # Goes through every worker-to-instruction mappping, and augment the appropriate arrays.
        for worker_id, worker_all_instructions in worker_to_keys.iteritems():

            # Alls workers must listen to heartbeat and update
            self.instruction_to_worker_list['heartbeat'].append(worker_id)
            self.instruction_to_worker_list['update'].append(worker_id)

            # For other instruction, only apply mapping for relevant instructions
            for worker_instruction in worker_all_instructions:

                self.instruction_to_worker_list[worker_instruction].append(worker_id)
                
        #######
        return
        #######
    
    ################################
    # END get_instruction_to_worker
    ################################

    #
    #
    #
    
    ####################################################################################################################
    # get_relevant_worker_list
    ####################################################################################################################
    # Revision History:
    #   2016-11-26 AB : Function created
    ####################################################################################################################
    def get_relevant_worker_list(self, instruction_name):
        """
        Gets list of worker that are relevant for a given instruction

        INPUT:
            instruction_name (str) : name of the instruction to send
        """
    
        relevant_worker_list = self.instruction_to_worker_list[instruction_name]
        
        ############################
        return relevant_worker_list
        ############################

    ###############################
    # END get_relevant_worker_list
    ###############################

    #
    #
    #

    ####################################################################################################################
    # get_end_timeout_summary
    ####################################################################################################################
    # Revision History:
    #   2016-11-26 AB : Function created
    ####################################################################################################################
    def post_timeout_actions(self, temporary_queue_name):
        """
        Applies all relevant actions after timeout has been reached.
        Starts by processing all messages that are still in the queue but that have not been processed yet.
        When all received responses are processed, deletes temporary elements, to avoid receiving messages during the
            post-processing, which would be unhandled.
        After queue has been deleted, print which responses were not received.

        INPUT:
            temporary_queue_name (str) : name of the temporary queue created to receive response
        """

        # Tests if the response queue is empty and if not, processes messages until it becomes so
        # Only do it if everything went well up to that point.
        if self.pika_connector.error_status == 0:
        
            self.delete_queue_flag = False

            # First set a delete_queue flag to True. If a message is in the response queue, function process_order will
            # be called, settings the flag to false. Otherwise, the code exists the loop.
            while not self.delete_queue_flag:

                self.delete_queue_flag = True
                self.pika_connector.process_data_events()

        # Tests why master stopped listening to responses : all received or timeout elapsed
        if self.total_response_received == len(self.response_received_checklist):

            print('\nResponse received from everyone')

        else:

            print('\nTimeout reached.')

            # Prints summary of which worker have failed to send response
            for worker_id, Has_Received_Response in self.response_received_checklist.iteritems():
                
                if not Has_Received_Response:

                    print('Response was not received from worker ' + str(worker_id))
                    
                    if self.forward_response_target is not None:
                        
                        self.forward_response_target.add_response(self.sent_instruction_info[0], worker_id, None)
                                
        # Deletes the temporary element that were created to receive responses
        self.pika_connector.remove_temporary_queue(temporary_queue_name)
        
        self.sent_instruction_info = [None, None]
        self.response_received_checklist = {}
        self.total_response_received = 0
        
        #######
        return
        #######
    
    ##############################
    # END get_end_timeout_summary
    ##############################

    #
    #
    #

    ####################################################################################################################
    # process_base_response
    ####################################################################################################################
    # Revision History:
    #   2016-11-26 AB : Function created
    ####################################################################################################################
    def process_base_response(self, worker_message_string):
        """
        Processes the base-information from a worker response.
        Takes out which worker responded, whether the response status is a success or a failure, and if there
            worker version was up-to-date.
        Returns the message in a tree form (lxml.etree) if response status was a success, otherwise returns None.

        INPUT:
            worker_message_string (str) : worker response as <worker id=... status=[S|F] version=NUM>...

        OUTPUT:
            (lxml.etree) : worker response as <worker id=... status=S version=NUM> if success, None otherwise
        """

        # Converts message to the lxml.etree format
        worker_message_tree = general_utils.convert_message_to_xml(worker_message_string)

        # If parsing successful, starts processing.
        if worker_message_tree is not None:

            worker_id = worker_message_tree.get('id')

            # Makes sure everything went ok with the response received. No duplicate response, expected response, ...
            if worker_id is not None:

                print('from worker ' + str(worker_id) + ' ..'),

                version_check(worker_message_tree)

                # Tests if the worker_id is valid.
                if worker_id not in self.response_received_checklist.keys():

                    worker_message_tree = None
                    general_utils.log_error(-201, error_details=str(worker_id))

                # Duplicate response. Should not happen. Queues are worker-specific => message should be answered once
                elif self.response_received_checklist[worker_id]:

                    worker_message_tree = None
                    general_utils.log_error(-202, error_details=str(worker_id))

                # Normal behavior : received response from expected worker
                else:

                    # Updates the list of received responses.
                    self.response_received_checklist[worker_id] = True
                    self.total_response_received += 1

                    # Checks for successful response
                    worker_response_status = worker_message_tree.get('status')
                    if worker_response_status == '0':

                        print('Success! Response will be processed')

                    else:

                        print('Failure! Response will be ignored.')
                        worker_message_tree = None

        ###########################
        return worker_message_tree
        ###########################

    ############################
    # END process_base_response
    ############################

    #
    #
    #

    ####################################################################################################################
    # process_response
    ####################################################################################################################
    # Revision History:
    #   2016-11-26 AB : Function created
    ####################################################################################################################
    def process_response(self, _,  pika_method, message_properties, message_content):
        """
        Defines how to process the response emitted by a worker
        First checks for the instruction the response corresponds to, then processes it appropriately

        INPUT:
             channel (pika) : pika channel object. UNUSED because available in the Worker.pika_connector object
             pika_method (pika) : !!!!NO IDEA!!!!
             message_properties (pika Properties) : additional properties about the message received
             message_content (str) : response content
        """
        
        print('\nReceived response..'),

        # Response queue contained a message, so prevent the queue from being deleted as it might contain more.
        self.delete_queue_flag = False

        # Checks whether the instruction id matches the response id, to make sure response fits.
        sent_instruction_name, sent_instruction_id = self.sent_instruction_info

        if sent_instruction_id == message_properties.correlation_id:
    
            # Checks the worker that sent the response, the success/failure report, and converts to tree structure
            worker_message_formatted = self.process_base_response(message_content)
                
            # Response had a success status report, so process it appropriately
            if worker_message_formatted is not None:

                # Finds appropriate response processing function in the master configuration folder
                appropriate_module = master_commands.instruction_to_functions.get(sent_instruction_name, None)
             
                if appropriate_module is None:
    
                    general_utils.log_error(-9)
                    
                else:
    
                    try:

                        # Processes the response from worker, and extracts a string to display
                        appropriate_module.process_response(self, worker_message_formatted)
                        
                        # Prints the string, and sends it to the GUI if GUI exists
                        if self.forward_response_target is not None:
                            
                            worker_id = worker_message_formatted.get('id')
                            self.forward_response_target.add_response(sent_instruction_name, worker_id,
                                                                      worker_message_formatted)
                        
                    # Module does not contain a get_response function
                    except AttributeError:

                        general_utils.log_error(-14)

            # Acknowledges message delivery when the response has been processed
            self.pika_connector.acknowledge_message(pika_method)

        #######
        return
        #######

    #######################
    # END process_response
    #######################

    #
    #
    #

    ####################################################################################################################
    # ask_worker
    ####################################################################################################################
    # Revision History:
    #   2016-11-26 AB : Function created
    ####################################################################################################################
    def ask_worker(self, instruction_name, message_to_send, response_timeout, checklist_override=None):
        """
        Sends a request to the RabbitMQ server with a given routing key.
        Waits for responses for a given amount of seconds.

        INPUT:
            instruction_name (str) : routing key to use to transit the message (=instruction title for workers)
            message_to_send (lxml.etree) : message to send workers, starting with <instruction type=...>
            response_timeout (int>0): time to wait for a response from workers
        """

        # Declares the response queue. If it fails, stops execution.
        created_queue_name = self.pika_connector.declare_temporary_queue(self.process_response)
        if self.pika_connector.error_status != 0:

            self.error_status = self.pika_connector.error_status

            #######
            return
            #######

        # When will the Master stop listening for responses
        timeout_timestamp = time.time() + response_timeout

        # Gives unique id to the query (sent back by worker) to make sure response and instruction match
        self.sent_instruction_info = [instruction_name, str(uuid.uuid4())]

        # Sets generic info (command to send)
        message_headers = {'type': instruction_name}

        message_properties = pika.BasicProperties(delivery_mode=2,  # Makes message persistent
                                                  headers=message_headers,  # Instruction header
                                                  reply_to=created_queue_name,  # Client queue in which to send answer
                                                  correlation_id=self.sent_instruction_info[1])  # Request id

        # If no worker checklist is provided, uses the internal list (worker who support the request)
        if checklist_override is None:
    
            checklist_override = self.instruction_to_worker_list[instruction_name]

        # Initializes the response checklist array to see which worker whose response to expect
        self.response_received_checklist = {}
        for worker_id in checklist_override:

            self.response_received_checklist[worker_id] = False

        # Converts the list of worker targets to a string
        target_worker_list = ','.join(checklist_override)
        message_to_send.set('target', target_worker_list)
        total_response_to_receive = len(self.response_received_checklist)
        
        # Converts message to a string before sending
        message_to_send = etree.tostring(message_to_send)

        # Publishes the message to the server
        self.pika_connector.publish_message(self.exchange_name, instruction_name, message_to_send, message_properties)
        
        # Checks if succeeded in publishing the message. Stop if it did not
        if self.pika_connector.error_status != 0:

            self.error_status = self.pika_connector.error_status

            #######
            return
            #######

        # Waits for a response until timeout / received all responses / user interruption, then delete the queue
        try:

            while self.keep_listening_for_response and self.total_response_received < total_response_to_receive and \
                            time.time() < timeout_timestamp:

                self.pika_connector.rabbit_connection.process_data_events()

        except KeyboardInterrupt:

            print('Waiting phase stopped manually.')

        # On timeout, check which worker have not sent a response in time and prints the result
        self.post_timeout_actions(created_queue_name)
        
        # Propagates the RabbitMQ connector status to this object
        self.error_status = self.pika_connector.error_status

        #######
        return
        #######

    #################
    # END ask_worker
    #################

    #
    #
    #

    ####################################################################################################################
    # parse_timeout
    ####################################################################################################################
    # Revision History:
    #   2016-11-26 AB : Function created
    ####################################################################################################################
    def parse_timeout(self, candidate_new_timeout=None):
        """
        Converts a timeout string to a number (float).
        If an error occurs during the conversion or that no arguments are provided, returns the default timeout value.

        INPUT:
            candidate_new_timeout (str) : string representation of the timeout desired (float). Must be > 0

        OUTPUT:
            timeout (float) : the converted timeout if successfull, the default global timeout if failed.
        """
        
        # Default value
        response_wait_timeout = self.response_wait_timeout

        if candidate_new_timeout is not None:

            try:
    
                response_wait_timeout = float(candidate_new_timeout)

            # Value unconvertible to float. Not terminal (replace by default)
            except ValueError as e:

                general_utils.log_error(-5, python_error_message=e)

            # Value unconvertible to float. Not terminal (replace by default)
            except TypeError as e:

                general_utils.log_error(-5, python_error_message=e)

        # Negative or zero-value
        if response_wait_timeout <= 0:

            general_utils.log_error(-6, error_details=str(response_wait_timeout))
            response_wait_timeout = self.response_wait_timeout

        #############################
        return response_wait_timeout
        #############################

    ####################
    # END parse_timeout
    ####################
    
    #
    #
    #

    ####################################################################################################################
    # send_command
    ####################################################################################################################
    # Revision History:
    #   2016-11-26 AB : Function created
    ####################################################################################################################
    def send_command(self, user_instruction_as_array):
        """
        Sends instruction to the RabbitMQ server, in order of appearance in the input.

        INPUT:
            user_instruction_as_array (str[]) : the instruction to send the instruction module.
                e.g. ['remote_control', 'tv', 'KEY_POWER']
        """

        # Something went wrong and caused an error, so try to recover connexion to RabbitMQ
        if self.error_status != 0:

            #######
            return
            #######

        # Checks if command is not empty. If it is, moves on to next command
        if len(user_instruction_as_array) == 0:

            general_utils.log_error(-8)

            #######
            return
            #######

        # Retrieves the instruction-dependent function to obtain message to send worker with instruction
        appropriate_module = master_commands.instruction_to_functions.get(user_instruction_as_array[0], None)

        # Checks that the function actually exists (otherwise, instruction probably invalid), so skip command
        if appropriate_module is None:

            general_utils.log_error(-9, error_details=str(user_instruction_as_array[0]))

            #######
            return
            #######

        base_instruction_message = etree.Element('instruction', type=user_instruction_as_array[0])
        # Calls appropriate function to get message to send to the RabbitMQ server in addition to the instruction
        try:

            message_to_send, response_wait_timeout = appropriate_module.get_message(self, base_instruction_message,
                                                                                    user_instruction_as_array[1:])

        except TypeError as e:

            # Too many arguments for a given instruction. Skip command
            general_utils.log_error(-10, error_details=str(user_instruction_as_array), python_error_message=str(e))

            #######
            return
            #######

        except ValueError as e:

            # Wrong argument sent
            general_utils.log_error(-13, error_details=str(user_instruction_as_array), python_error_message=str(e))

            #######
            return
            #######

        except AttributeError as e:

            # Module does not contain required functions
            general_utils.log_error(-14, error_details=str(user_instruction_as_array), python_error_message=str(e))

            #######
            return
            #######

        # Sends commands + message to the RabbitMQ server.
        self.ask_worker(user_instruction_as_array[0], message_to_send, response_wait_timeout)

        #######
        return
        #######

    ###################
    # END send_command
    ###################

    #
    #
    #

    ####################################################################################################################
    # process_live_commands
    ####################################################################################################################
    # Revision History:
    #   2016-11-26 AB : Function created
    ####################################################################################################################
    def process_live_commands(self, user_instruction_as_array):
        """
        Processes instruction taken from a live feed (from either GUI or ccommand line).

        INPUT:
            user_instruction_as_array (str[]) : all elements to send to the worker, before being processed
        """

        # Instruction to apply
        sent_instruction_name = user_instruction_as_array[0]
        print('Instruction chosen : ' + str(sent_instruction_name))

        ##########
        # TIMEOUT
        ##########
        # Tests for meta-instructions timeout. Must contain exactly 1 argument (+ 'timeout')
        if sent_instruction_name == 'timeout':

            # Tests for correct number of arguments
            if len(user_instruction_as_array) == 2:

                # Updates timeout value
                self.response_wait_timeout = self.parse_timeout(user_instruction_as_array[1])
                print('New timeout value : ' + str(self.response_wait_timeout))

            else:

                general_utils.log_error(-12)

            # Goes back to process new commands
            #######
            return
            #######

        #######
        # HELP
        #######
        # Tests for meta-instruction help. Contains no argument (summary of all instruction), or instruction name
        #   (detailed information about given instruction)
        if sent_instruction_name == 'help':

            if len(user_instruction_as_array) == 1:

                # No argument, global summary
                for instruction_name in master_commands.instruction_to_functions.keys():

                    try:

                        master_commands.instruction_to_functions[instruction_name].get_help_message(False)
                        print('')

                    except AttributeError:

                        general_utils.log_error(-14, error_details=instruction_name)

            elif len(user_instruction_as_array) == 2:

                instruction_name = user_instruction_as_array[1]

                # Argument provided, detailled description
                if instruction_name in master_commands.instruction_to_functions.keys():

                    try:

                        master_commands.instruction_to_functions[instruction_name].get_help_message(True)

                    except AttributeError:

                        general_utils.log_error(-14, error_details=instruction_name)

                else:

                    general_utils.log_error(-9, error_details=str(instruction_name))

            else:

                general_utils.log_error(-10)

            # Processing done : next instruction.

            #######
            return
            #######

        #######################
        # Non-meta instruction
        #######################
        # Applies the instruction
        self.send_command(user_instruction_as_array)

        #######
        return
        #######

    ############################
    # END process_live_commands
    ############################

    #
    #
    #

    ####################################################################################################################
    # listen_to_live_commands
    ####################################################################################################################
    # Revision History:
    #   2016/11/26 AdBa : Created the function
    ####################################################################################################################
    def listen_to_live_commands(self):
        """
        Starts listening to a live instruction feed (in command line) and sends them to be processed.
        """
        
        print('\n\nNow listening to command line inputs.\n'
              'Enter "exit" to stop the code, "timeout (number)" to set default timeout value, "help", "help (str)" or '
              'a valid instruction')

        # Apply the "wait for instruction -> execute" sequence until the user types exit
        while True:
    
            # Something went wrong and caused an error, so try to recover connexion to RabbitMQ
            if self.error_status != 0:

                break
    
            # Waits to receive instruction unless waiting time is stopped manually
            try:
                user_instruction = raw_input('\n\nEnter your instruction : ')
                
            except KeyboardInterrupt:
                
                print('Code stopped by user.')
                break
    
            #######
            # EXIT
            #######
            # Tests for meta-instructions exit
            if user_instruction == 'exit':

                break

            # Converts the instruction string (one string) to an array of arguments.
            # Ex : 'print "a b" 3' returns ['print', 'a b', '3']
            user_instruction_as_array = shlex.split(str(user_instruction))
            if len(user_instruction_as_array) == 0:

                general_utils.log_error(-11)
    
                #######
                return
                #######

            # Not asked to exit, so process the instruction
            self.process_live_commands(user_instruction_as_array)
            
        #######
        return
        #######
    
    ##############################
    # END listen_to_live_commands
    ##############################

    ####################################################################################################################
    # parse_arguments
    ####################################################################################################################
    # Revision History:
    #   2016/11/26 AdBa : Created the function
    ####################################################################################################################
    def parse_arguments(self, command_line_arguments):
        """
        Parses all command lines arguments and processes them appropriatly

        INPUT:
            command_line_arguments (str list)
        """

        # Creates a parser and sets its accepted arguments. 'c' flag is set to append because a user writing
        # [-c time -c print x -c time] should execute three commands in a row, and not just the last one
        argument_parser = argparse.ArgumentParser()
        argument_parser.add_argument('-gui', action='store_true')

        # Parses the arguments
        print('Reading arguments..'),
        parsed_arguments, to_ignore_arguments = argument_parser.parse_known_args(command_line_arguments)
        print ('Done.')

        # If unhandled arguments exist, ignore them but print warning.
        if len(to_ignore_arguments) > 0:

            general_utils.log_error(-4, error_details=str(to_ignore_arguments))

        # Starts the live command line feed if GUI option is not enabled
        if not parsed_arguments.gui:

            self.has_commandline_feed = True

        #######
        return
        #######

    ######################
    # END parse_arguments
    ######################

    #
    #
    #
    
    ####################################################################################################################
    # on_connection_recovery
    ####################################################################################################################
    # Revision History:
    #   2016-11-26 AB : Function created
    ####################################################################################################################
    def on_connection_recovery(self):
        """
        Recreates all elements that need to be recreated when connection to RabbitMQ server was lost and is recovered.
        """
    
        # Redeclares exchange
        self.set_exchange(self.exchange_name)
    
        #######
        return
        #######
    
    #########################
    # on_connection_recovery
    #########################

    #
    #
    #

###################
# END RabbitMaster
###################


########################################################################################################################
# main
########################################################################################################################
# Revision History:
#   2016-11-26 AB : Function created
####################################################################################################################
def main(args):
    """
    Sends instructions to a RabbitMQ server, for dispatch to workers. Available flags are :
        -timeout (str) : Global timeout value (seconds) that overrides the default (1s).
        -c : instruction to send. Commands with response have an optional timeout overriding the global value
        -input : switch to live instruction feed after all the -c flag commands have been processed

    INPUT:
         args (str list) : the command lines arguments, excluding the first one (containing program name)

    OUTPUT :
         master (Master) : the master instance.
    """

    class_name = 'Master'
    general_utils.get_welcome_end_message(class_name, True)

    # Creates the Master object, which establishes the RabbitMQ connexion
    rabbit_master_instance = RabbitMaster(rabbit_configuration_filename)
    general_utils.test_fatal_error(rabbit_master_instance, class_name)

    # Sets the exchange to use for transactions
    rabbit_master_instance.set_exchange('ex')
    general_utils.test_fatal_error(rabbit_master_instance, class_name)

    # Creates mapping from instruction names to the worker that support them
    rabbit_master_instance.get_instruction_to_worker()

    # Checks if request name is valid, and adds relevant parameters (the current time for the 'time' request)
    rabbit_master_instance.parse_arguments(args)

    print('Master initialization complete.')

    # Switches to live feed mode for commands if necessary
    if rabbit_master_instance.has_commandline_feed:

        rabbit_master_instance.listen_to_live_commands()

    ##############################
    return rabbit_master_instance
    ##############################

###########
# END main
###########

if __name__ == "__main__":

    main(sys.argv[1:])

    # Exits code
    general_utils.get_welcome_end_message('Master', False)
    
    exit(0)
