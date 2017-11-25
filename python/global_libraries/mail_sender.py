"""
This module contains a gmail-client handler, to send message through a gmail account
"""

#########################
# Import Global Packages
#########################
import os  # Facilitates update of configuration folders
import configparser
import smtplib  # Library to send mail through Gmail
import socket  # Library used to catch exceptions from smtplib

########################
# Import Local Packages
########################
import general_utils

###########################
# Declare Global Variables
###########################
account_configuration_filename = '/home/pi/Home_Code/configs/mailConfig.ini'  # Config file

####################################################################################################
# CODE START
####################################################################################################


####################################################################################################
# MailSender
####################################################################################################
# Revision History :
#   2017-07-04 AdBa : Class created
####################################################################################################
class MailSender:
    """Objects to send messages through a gmail account"""

    ################################################################################################
    # __init__
    ################################################################################################
    # Revision History :
    #   2017-07-04 AB : Function created
    ################################################################################################
    def __init__(self):
        """
        Creates an empty MailSender instance
        """

        self.error_status = 0  # 0 If no errors occured so far, negative number otherwise

        self.username = None  # Email address of sender
        self.password = None  # Password of sender
        self.client = None

    ###############
    # END __init__
    ###############

    #
    #
    #

    ################################################################################################
    # test_credentials
    ################################################################################################
    # Revision History:
    #   2017-07-04 AdBa : Function created
    ################################################################################################
    def test_credentials(self):
        """
        Tests validity of credentials loaded in system by trying to log-in to gmail.

        OUTPUT
            (bool) Whether or not credentials managed to be used to log into account
        """

        test_status = False

        if self.error_status == 0 and self.username is not None:

            try:

                # Tests credentials
                mail_server = smtplib.SMTP(self.client)
                mail_server.starttls()
                mail_server.login(self.username, self.password)
                mail_server.quit()

                # Successfull
                general_utils.log_message('Valid credentials')
                test_status = True

            except smtplib.SMTPException as e:

                # An error occured whe trying credentials
                self.error_status = general_utils.log_error(-994, python_message=e)

            except socket.gaierror:

                # Discovered during debugging phase that this exception occurs when offline. smtplib
                #    call socket.create_connection, which raises an exception.
                error_details = 'Test internet connection status'
                self.error_status = general_utils.log_error(-994, error_details=error_details)

        else:

            general_utils.log_message('Credential failed due to no credentials or previously '
                                      'reported error')

        ###################
        return test_status
        ###################

    #######################
    # END test_credentials
    #######################

    #
    #
    #

    ################################################################################################
    # load_config
    ################################################################################################
    # Revision History :
    #   2017-07-04 AdBa : Function created
    ################################################################################################
    def load_config(self, configuration_filename):
        """
        Loads and test gmail account configuration from configuration file

        INPUT
            configuration_filename (str) name of the gmail configuration file to load
        """

        # Makes sure that the configuration file exists between tyring to load it
        if os.path.isfile(configuration_filename):

            try:

                # Creates configuration parser and starts parsing configuration file.
                rabbit_config = configparser.RawConfigParser()
                rabbit_config.read(configuration_filename)

                # Extracts credentials for connection
                self.username = rabbit_config.get('Gmail', 'username')
                self.password = rabbit_config.get('Gmail', 'password')
                self.client = rabbit_config.get('Gmail', 'mailhub')

                # Successully parsed configuration.
                general_utils.log_message('Mail configuration loaded.')

                # Tests if credentials do work or not
                self.test_credentials()

            except configparser.NoSectionError as e:

                # File does not exist, or section (Gmail) does not exist
                self.error_status = general_utils.log_error(-1, python_message=e,
                                                            error_details='Gmail')

            except configparser.NoOptionError as e:

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
    # send_message
    ################################################################################################
    # Revision History:
    #   2017-07-04 AdBa : Function created
    ################################################################################################
    def send_message(self, message_to_send, destination_address):
        """
        Sends message through gmail.

        INPUT
            message_to_send (str) the message to send to the destination
            destination_address (mail address of the destination)

        OUTPUT
            whether or not send was successfull or not
        """

        send_status = False

        # Validity of credentials is called right after the configuration load.
        if self.error_status == 0 and self.username is not None:

            try:

                mail_server = smtplib.SMTP(self.client)
                mail_server.ehlo()
                mail_server.starttls()
                mail_server.login(self.username, self.password)
                mail_server.sendmail(self.username, destination_address, message_to_send)
                mail_server.quit()

                general_utils.log_message('Successfully sent message.')
                send_status = True

            except smtplib.SMTPException as e:

                # An error occured whe trying credentials
                self.error_status = general_utils.log_error(-994, python_message=e)

            except socket.gaierror:

                # Discovered during debugging phase that this exception occurs when offline. smtplib
                #    call socket.create_connection, which raises an exception.
                error_details = 'Test internet connection status'
                self.error_status = general_utils.log_error(-994, error_details=error_details)

        else:

            general_utils.log_message('Message sending failed due to no credentials or previously '
                                      'reported error')

        ###################
        return send_status
        ###################

    ###################
    # END send_message
    ###################

#################
# END MailSender
#################


####################################################################################################
# create_mail_sender
####################################################################################################
# Revision History :
#   2017-11-23 AdBa : Function created
####################################################################################################
def create_mail_sender():

    mail_sender = MailSender()

    mail_sender.load_config(account_configuration_filename)

    #######
    return
    #######

#########################
# END create_mail_sender
#########################
