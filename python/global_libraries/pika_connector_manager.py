"""
This module handles connexion and interactions with RabbitMQ server
"""


#########################
# Import Global Packages
#########################
import ConfigParser
import os
import urllib2  # Used to check connection to server
from time import sleep

import pika
import pika.exceptions

import general_utils


####################################################################################################
# CODE START
####################################################################################################


####################################################################################################
# PikaConnectorManager
####################################################################################################
# Revision History :
#   2016-11-26 AdBa : Class created
####################################################################################################
class PikaConnectorManager:
    """
    Applies most RabbitMQ server interactions for Worker/Master instances.
    These interactions include queue declaration, RabbitMQ configuration loading, starting 
        connexion, publishing messages, ...
    Keeps track of the interaction with RabbitMQ server using a status parameters
    """

    ################################################################################################
    # __init__
    ################################################################################################
    def __init__(self, caller_class):
        
        # Binding to what element called the PikaConnectorManager (Master or Worker instance)
        self.caller_class = caller_class
        
        # Parameters for the RabbitMQ connection. Stored for potential future reuse (reconnection)
        self.server_parameters = {}
        
        # Connection/Channel with the RabbitMQ server (pika elements)
        self.rabbit_connection = None
        self.rabbit_channel = None
        
        # Working status. If 0, everything is fine, otherwise a fatal error has occured
        self.error_status = 0
        
    ###############
    # END __init__
    ###############

    #
    #
    #

    ################################################################################################
    # load_config
    ################################################################################################
    # Revision History :
    #   2016-11-26 AdBa : Function created
    ################################################################################################
    def load_config(self, configuration_filename):
        """
        Loads a configuration file of RabbitMQ credentials and extracts them

        INPUT:
            configuration_filename (str) : name of the file to parse
        """

        # Makes sure that the configuration file exists between tyring to load it
        if os.path.isfile(configuration_filename):

            try:

                # Creates configuration parser and starts parsing configuration file.
                rabbit_config = ConfigParser.RawConfigParser()
                rabbit_config.read(configuration_filename)

                # Extracts credentials for connection and server information
                self.server_parameters['user'] = rabbit_config.get('RabbitMQ', 'user')
                self.server_parameters['password'] = rabbit_config.get('RabbitMQ', 'password')
                self.server_parameters['host'] = rabbit_config.get('RabbitMQ', 'host')
                self.server_parameters['port'] = rabbit_config.getint('RabbitMQ', 'port')

                # Port used exclusively to test if a RabbitMQ node exists.
                self.server_parameters['management_port'] = rabbit_config.getint('RabbitMQ',
                                                                                 'management_port')

                # Successully parsed configuration.
                general_utils.log_message('Rabbit configuration loaded.')

            except ConfigParser.NoSectionError as e:

                # File does not exist, or section (RabbitMQ) does not exist
                self.error_status = general_utils.log_error(-1, python_message=e)

            except ConfigParser.NoOptionError as e:

                # Option does not exist
                self.error_status = general_utils.log_error(-2, python_message=e)

            except ValueError as e:

                # Port error
                self.error_status = general_utils.log_error(-3, python_message=e)

        else:

            # Configuration file did not exist, stop and return fatal error
            self.error_status = general_utils.log_error(-401, error_details=configuration_filename)

        #######
        return
        #######
    
    ##################
    # END load_config
    ##################

    #
    #
    #

    ################################################################################################
    # test_rabbitmq_node_activity
    ################################################################################################
    # Revision History:
    #   2016-11-26 AdBa : Function created
    ################################################################################################
    def test_rabbitmq_node_activity(self):
        """
        Checks whether the RabbitMQ server is alive or not.
        This assumes that management plug-in is enabled. If it is, http://rabbit_server_ip:15672 is 
            reachable.
        This blocks until the server is detected.
        """

        # Gets URL to which a connexion must be attempted
        rabbit_server_ip = self.server_parameters['host']
        rabbit_server_port = self.server_parameters['management_port']
        rabbitmq_url = 'http://%s:%s' % (str(rabbit_server_ip), str(rabbit_server_port))

        # Creates the connexion and a channel, then returns it
        connection_failed = True
        while connection_failed:
    
            try:

                # Attempts connexion to webpage (with timeout, to make sure we can log failed
                #   attempts)
                urllib2.urlopen(rabbitmq_url, timeout=3)

                # Successfully connected, leave the loop.
                connection_failed = False
                general_utils.log_message('RabbitMQ server is alive.')

            # If connexion establishment fails, wait then try again
            except urllib2.URLError:

                general_utils.log_message('RabbitMQ server not detected. Trying again soon.')
                sleep(3)
                continue
    
        #######
        return
        #######
    
    ##################################
    # END test_rabbitmq_node_activity
    ##################################
        
    #
    #
    #

    ################################################################################################
    # establish_rabbit_connection
    ################################################################################################
    # Revision History:
    #   2016-11-26 AdBa : Function created
    ################################################################################################
    def establish_rabbit_connection(self):
        """
        Establishes a connexion to the RabbitMQ server. Connexion/channel available in 
            pika_connector_manager.
        """

        # Makes sure the configuration could be parsed (only dependency of this function)
        if self.error_status != 0:
            
            #######
            return
            #######
        
        # Sets the connexion parameters to established the connexion with server
        rabbit_user_credentials = pika.PlainCredentials(self.server_parameters['user'],
                                                        self.server_parameters['password'])
        rabbit_parameters = pika.ConnectionParameters(self.server_parameters['host'],
                                                      self.server_parameters['port'],
                                                      '/',
                                                      rabbit_user_credentials)

        # Creates loop that blocks code until RabbitMQ server is detected (checks management page).
        # NOTE : added because pika.BlockingConnection blocks after few attempts => Code blocked.
        self.test_rabbitmq_node_activity()
        
        # Creates the connexion and a channel, then returns
        connection_failed = True
        while connection_failed:
            
            try:
                
                self.rabbit_connection = pika.BlockingConnection(rabbit_parameters)
                self.rabbit_channel = self.rabbit_connection.channel()

                # This will be reached only if connexion created successfully
                connection_failed = False
                general_utils.log_message('Successfully connected to RabbitMQ server.')

            except pika.exceptions.ChannelClosed:

                # If connexion establishment fails, wait then try again
                self.test_rabbitmq_node_activity()
                continue

            except pika.exceptions.ConnectionClosed:

                # If connexion establishment fails, wait then try again
                self.test_rabbitmq_node_activity()
                continue

            except pika.exceptions.ProbableAuthenticationError:

                # Credentials given are wrong. Stop execution.
                self.error_status = general_utils.log_error(-101, self.server_parameters)
                break

            except KeyError:

                # Internal error in pika when connection drops between self.connection and
                # self.channel assignments.
                self.test_rabbitmq_node_activity()
                continue
        
        #######
        return
        #######
    
    ##################################
    # END establish_rabbit_connection
    ##################################

    #
    #
    #

    ################################################################################################
    # declare_exchange
    ################################################################################################
    # Revision History :
    #   2016-11-26 AdBa : Function created
    ################################################################################################
    def declare_exchange(self, exchange_name):
        """
        Declares an exchange in the RabbitMQ system.

        INPUT:
            exchange_name (str) : name of the exchange in which the queues must be declared
        """

        declare_failed = True
        while declare_failed:
            try:

                self.rabbit_channel.exchange_declare(exchange=exchange_name, exchange_type='direct',
                                                     durable=True)

                # Successfully declared the exchange
                general_utils.log_message('Exchange %s successfully created.' % (exchange_name,))
                declare_failed = False
    
            except pika.exceptions.ConnectionClosed:
        
                # If connection failed, recreate it and retry declaration (exchange_declare is made
                # early stage, so do not call .on_recover
                general_utils.log_message(
                    'Connection dropped. Could not declare exchange %s' % (exchange_name,))
                self.establish_rabbit_connection()
                continue
    
            except pika.exceptions.ChannelClosed:

                # If connection failed, recreate it and retry declaration (exchange_declare is made
                # early stage, so do not call .on_recover
                general_utils.log_message(
                    'Connection dropped. Could not declare exchange %s' % (exchange_name,))
                self.establish_rabbit_connection()
                continue

        #######
        return
        #######
    
    #######################
    # END declare_exchange
    #######################

    #
    #
    #

    ################################################################################################
    # publish_message
    ################################################################################################
    # Revision History :
    #   2016-11-26 AdBa : Function created
    ################################################################################################
    def publish_message(self, exchange_name, routing_key, message_content, message_properties):
        """
        Publishes a message to the RabbitMQ server

        INPUT:
            exchange_name (str) name of the exchange to use for the message
            routing_key (str) routing key to use to transit message (=instruction title for workers)
            message_content (str) message to send
            message_properties (pika BasicProperties) properties of the message to send
        """

        publish_failed = True
        while publish_failed:
            try:

                # Successfully declared the exchange
                self.rabbit_channel.basic_publish(exchange=exchange_name,
                                                  routing_key=routing_key,
                                                  body=message_content,
                                                  properties=message_properties)

                general_utils.log_message(
                    'Sent message starting with ' + str(message_content[:200]) + '.')
                publish_failed = False
    
            except pika.exceptions.ConnectionClosed:
        
                # If connection failed, queue gets deleted automatically (channel is deleted)
                # => calls on_recovery
                general_utils.log_message(
                    'Connection dropped. Could not send message %s' % (message_content,))
                self.establish_rabbit_connection()
                self.caller_class.on_connection_recovery()
                continue
            
            except pika.exceptions.ChannelClosed:
        
                # If connection failed, queue gets deleted automatically (channel is deleted)
                # => calls on_recovery
                general_utils.log_message(
                    'Connection dropped. Could not send message %s' % (message_content,))
                self.establish_rabbit_connection()
                self.caller_class.on_connection_recovery()
                continue

        #######
        return
        #######
    
    ######################
    # END publish_message
    ######################

    #
    #
    #

    ################################################################################################
    # declare_temporary_queue
    ################################################################################################
    # Revision History :
    #   2016-11-26 AdBa : Function created
    ################################################################################################
    def declare_temporary_queue(self, callback_function):
        """
        Declares a temporary queue messages from the server and declares the feed from this queue

        INPUT:
            callback_function (fun) callback function when messages are sent from queue to consumer

        OUTPUT:
            queue_name (str) : name of the temporary queue created. '' if failed to create
        """
        
        queue_name = ''

        # Creates queue required. While loop is added to make sure a closed connexion error restarts
        #  a connexion and retries creating the queue
        creation_failed = True
        while creation_failed:
            
            try:
                
                queue_declared = self.rabbit_channel.queue_declare(exclusive=True)

                queue_name = queue_declared.method.queue
    
                self.rabbit_channel.basic_consume(callback_function, queue=queue_name, no_ack=False)
                general_utils.log_message('Temporary queue created.'),

                creation_failed = False
                
            except pika.exceptions.ConnectionClosed:

                general_utils.log_message(
                    'Connection dropped. Could not declare/bind temporary queue.')
                self.establish_rabbit_connection()
                continue
                
            except pika.exceptions.ChannelClosed:

                general_utils.log_message(
                    'Connection dropped. Could not declare/bind temporary queue.')
                self.establish_rabbit_connection()
                continue

        ##################
        return queue_name
        ##################
    
    ##############################
    # END declare_temporary_queue
    ##############################

    #
    #
    #

    ################################################################################################
    # declare_permanent_queues
    ################################################################################################
    # Revision History :
    #   2016-11-26 AdBa : Function created
    ################################################################################################
    def declare_permanent_queues(self, all_routing_keys, exchange_name, queue_name_function=None,
                                 callback_function=None):
        """
        Declares a permanent queue messages from the server and declares the feed.

        INPUT:
            all_routing_keys (str[]): all keys to use for queue declaration
            exchange_name (str): Exchange to which the queue must be bound.
            queue_name_function (Function|None) function to get name of keys based on key (require
                key as argument). If None, the routing key is used by itself
            callback_function (fun|None):
                If not None: function called when a message is received (also declares consumption).
                If None: does not declare any consumption. Simply declare the queue
        """

        # Creates queue required. While loop is added to make sure a closed connexion error simply
        # restarts a connexion and retries creating the queue
        creation_failed = True
        while creation_failed:

            try:
                
                for routing_key in all_routing_keys:

                    # Gets the queue name based on the provided key
                    if queue_name_function is not None:

                        queue_name = queue_name_function(routing_key)
                        
                    else:
                        
                        queue_name = routing_key

                    # Declares and binds queue
                    self.rabbit_channel.queue_declare(queue_name, durable=True)
                    self.rabbit_channel.queue_bind(exchange=exchange_name, routing_key=routing_key,
                                                   queue=queue_name)
        
                    # Declares consumption from queue
                    if callback_function is not None:

                        self.rabbit_channel.basic_consume(callback_function, queue=queue_name,
                                                          no_ack=False, exclusive=True)

                    general_utils.log_message('Permanent queue %s created.' % (str(queue_name, )))

                creation_failed = False
    
            except pika.exceptions.ChannelClosed:
                
                # If failed to declare all queues, start over
                general_utils.log_message(
                    'Connection dropped. Could not declare/bind permanent queue.')
                self.establish_rabbit_connection()
                continue
    
            except pika.exceptions.ConnectionClosed:
                
                # If failed to declare all queues, start over
                general_utils.log_message(
                    'Connection dropped. Could not declare/bind permanent queue.')
                self.establish_rabbit_connection()
                continue

        #######
        return
        #######
    
    ###############################
    # END declare_permanent_queues
    ###############################

    #
    #
    #

    ################################################################################################
    # delete_permanent_queue
    ################################################################################################
    # Revision History :
    #   2016-11-26 AdBa : Function created
    ################################################################################################
    def delete_permanent_queue(self, queue_name):
        """
        Deletes a permanent queue message from the server.

        INPUT:
            queue_name (str): Name of the queue to delete

        """
    
        # Deletes queue required. While loop is added to make sure a closed connexion error simply
        # restarts a connexion and retries deleting the queue
        deletion_failed = True
        while deletion_failed:
        
            try:
                
                self.rabbit_channel.queue_delete(queue_name)

                general_utils.log_message('Permanent queue %s deleted.' % (str(queue_name)))
                deletion_failed = False
        
            except pika.exceptions.ChannelClosed:

                general_utils.log_message(
                    'Connection dropped. Could not delete permanent queue %s' % (queue_name,))
                self.establish_rabbit_connection()
                self.caller_class.on_connection_recovery()
                continue

            except pika.exceptions.ConnectionClosed:
    
                general_utils.log_message(
                    'Connection dropped. Could not delete permanent queue %s' % (queue_name,))
                self.establish_rabbit_connection()
                self.caller_class.on_connection_recovery()
                continue

        #######
        return
        #######
    
    #############################
    # END delete_permanent_queue
    #############################

    #
    #
    #

    ################################################################################################
    # remove_temporary_queue
    ################################################################################################
    # Revision History :
    #   2016-11-26 AdBa : Function created
    ################################################################################################
    def remove_temporary_queue(self, queue_name):
        """
        Removes a temporary queue from the server.

        INPUT:
            queue_name (str) : the name of the queue to remove
        """
        try:
            
            self.rabbit_channel.queue_delete(queue_name, if_empty=True)
    
        except pika.exceptions.ChannelClosed:
            
            # If connection failed, queue gets deleted automatically (channel is deleted)
            general_utils.log_message('Connection dropped.')
            self.establish_rabbit_connection()
            self.caller_class.on_connection_recovery()
            
        except pika.exceptions.ConnectionClosed:
            
            # If connection failed, queue gets deleted automatically (channel is deleted)
            general_utils.log_message('Connection dropped.')
            self.establish_rabbit_connection()
            self.caller_class.on_connection_recovery()

        #######
        return
        #######
    
    #############################
    # END remove_temporary_queue
    #############################

    #
    #
    #

    ################################################################################################
    # acknowledge_message
    ################################################################################################
    # Revision History :
    #   2016-11-26 AdBa : Function created
    ################################################################################################
    def acknowledge_message(self, pika_method):
        """
        Attempts to send acknowledgements for a message received

        INPUT:
            pika_method (pika method) : arguments on callback function from pika

        """

        try:
            
            self.rabbit_channel.basic_ack(delivery_tag=pika_method.delivery_tag)
            general_utils.log_message('Acknowledged message.')

        except pika.exceptions.ChannelClosed as e:

            general_utils.log_message('Connection dropped. Could not acknowledge message.')
            general_utils.log_error(-106, python_message=str(e))
            self.establish_rabbit_connection()
            self.caller_class.on_connection_recovery()

        except pika.exceptions.ConnectionClosed as e:

            general_utils.log_message('Connection dropped. Could not acknowledge message.')
            general_utils.log_error(-106, python_message=str(e))
            self.establish_rabbit_connection()
            self.caller_class.on_connection_recovery()

        #######
        return
        #######
    
    ##########################
    # END acknowledge_message
    ##########################

    #
    #
    #

    ################################################################################################
    # start_consume
    ################################################################################################
    # Revision History :
    #   2016-11-26 AdBa : Function created
    ################################################################################################
    def start_consume(self):
        """
        Initializes the consumption from all linked queues until an issue occurs.
        In case an exception is raised, stop the function but does not crash the code, to let the 
        parent function know the consumption eventually encoutnered an error
        This is an improvement on the default channel.start_consuming, which just exists the code 
            with an exception.
        """
        
        # Starts consuming until user stops consumption. If connexion fails, waits and retry.
        is_currently_consuming = True
        while is_currently_consuming:
            
            try:
                
                general_utils.log_message('Starting queue consumption.')
                self.rabbit_channel.start_consuming()
                
                # Channel was closed by program => Exits
                if self.rabbit_connection is None:

                    break
                
            except pika.exceptions.ChannelClosed:

                # Connection dropped while consuming, so recover the connection and resume
                general_utils.log_message('Connection dropped during queue consumption.')
                self.establish_rabbit_connection()
                self.caller_class.on_connection_recovery()
                continue
                
            except pika.exceptions.ConnectionClosed:

                # Connection dropped while consuming, so recover the connection and resume
                general_utils.log_message('Connection dropped during queue consumption.')
                self.establish_rabbit_connection()
                self.caller_class.on_connection_recovery()
                continue
                
            except KeyboardInterrupt:

                # User interrupted code. So stop consuming.
                general_utils.log_error(-998, 'Start_Consume consume.')
                is_currently_consuming = False
                self.stop_consume()
            
        #######
        return
        #######
    
    ####################
    # END start_consume
    ####################

    #
    #
    #

    ################################################################################################
    # stop_consume
    ################################################################################################
    # Revision History :
    #   2016-11-26 AdBa : Function created
    ################################################################################################
    def stop_consume(self, with_acknowledge=None):
        """
        Terminates the consumption from all linked queues and closes the connexions.
        
        INPUT:
            with_acknowledge (opt, pika.method) whether a message needs to be acknowledge after 
                consumption stops
        """

        # Stop consuming and closes connexion
        try:
            
            self.rabbit_channel.stop_consuming()
            
            if with_acknowledge is not None:
                
                self.acknowledge_message(with_acknowledge)
                
            self.rabbit_connection.close()
            self.rabbit_connection = None
            self.rabbit_channel = None
 
        except pika.exceptions.ChannelClosed as e:

            general_utils.log_message('Connection dropped while stopping consumption.')
            self.error_status = general_utils.log_error(-108, python_message=str(e))

        except pika.exceptions.ConnectionClosed as e:

            general_utils.log_message('Connection dropped while stopping consumption.')
            self.error_status = general_utils.log_error(-108, python_message=str(e))

        except KeyboardInterrupt:
    
            general_utils.log_error(-998, 'Stop consume.')

        #######
        return
        #######
    
    ###################
    # END stop_consume
    ###################

    #
    #
    #

    ################################################################################################
    # process_data_events
    ################################################################################################
    # Revision History :
    #   2016-11-26 AdBa : Function created
    ################################################################################################
    def process_data_events(self):
        """
        Waits for messages coming from queues for a short period of time.
        """
        
        try:

            self.rabbit_connection.process_data_events()
        
        except pika.exceptions.ChannelClosed:
    
            general_utils.log_message('Connection dropped while processing_data_events')
            self.establish_rabbit_connection()
            self.caller_class.on_connection_recovery()
        
        except pika.exceptions.ConnectionClosed:

            general_utils.log_message('Connection dropped while processing_data_events')
            self.establish_rabbit_connection()
            self.caller_class.on_connection_recovery()

        #######
        return
        #######
        
    ##########################
    # END process_data_events
    ##########################

###########################
# END PikaConnectorManager
###########################
