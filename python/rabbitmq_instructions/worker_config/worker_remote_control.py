#######################
# Import Local package
#######################
from python.global_libraries import general_utils  # Generic functions
from python.infrared_remote import bedroom_aircon_driver
from python.infrared_remote import living_aircon_driver
from python.infrared_remote import bedroom_lights_driver
from python.infrared_remote import living_lights_driver
from python.infrared_remote import tv_remote_driver


###########################
# Declare Global Variables
###########################
# Each entry is aircon_name: [relevant_driver, raspberry_pi that controls it, pin]
remote_to_info = {
    'aircon_living': [living_aircon_driver, 'bedroom', 21],
    'aircon_bedroom': [bedroom_aircon_driver, 'bedroom', 21],
    'light_living': [living_lights_driver, 'bedroom', 21],
    'light_bedroom': [bedroom_lights_driver, 'bedroom', 21],
    'tv': [tv_remote_driver, 'bedroom', 21]
}


####################################################################################################
# execute
####################################################################################################
# Revision History :
#   2016-09-30 Adba : Function created
#   2017-05-19 Adba : Added call to read pin configuration
####################################################################################################
def execute(worker_instance, instruction_as_xml, worker_base_response):
    """
    Processes infrared remote instruction

    INPUT
         worker_instance (Worker) worker instance
         instruction_as_xml (lxml.etree) message to process
         worker_base_response (lxml.etree) base of worker response on which to build

    OUTPUT
         (lxml.etree) worker response
    """

    # Creates base response to be completed in instruction
    remote_control_response = worker_base_response

    # Gets name of remote to simulate.
    remote_to_use = instruction_as_xml.get('remote')

    # Retrieves appropriate driver using remote name.
    remote_info = remote_to_info.get(remote_to_use, None)
    if remote_info is not None:

        # Checks if remote is handled by this worker or another. Stops if another.
        if worker_instance.worker_id != remote_info[1]:

            status_code = 0

        else:

            # Retrieves the "button" to simulate (button name or full configuration information).
            #   Example: for tv : 'Power', 'Mute', ....  for aircon : 'on,heat,25,strong,highest'
            configuration_to_send = instruction_as_xml.get('config')
            try:

                # Split the comma-separated info (only puts in array if button name)
                configuration_splitted = configuration_to_send.split(',')

                # Logs remote command to send before sending it, for history and bug tracking
                general_utils.log_message('Request for remote %s : %s' % (remote_to_use,
                                                                          configuration_to_send))

                # Sends all element in array as argument (button name or all config parameter)
                status_code = remote_info[0].send_signal(*configuration_splitted)

            except TypeError:

                # Failed to call function because number of arguments did not match
                details = '(%s, %s)' % (remote_to_use, configuration_to_send)
                status_code = general_utils.log_error(-502, error_details=details)

    else:

        # Remote name did not exist in available remotes.
        status_code = general_utils.log_error(-501, error_details=remote_to_use)

    # Puts status code in response.
    remote_control_response.set('status', str(status_code))

    ###############################
    return remote_control_response
    ###############################

##############
# END execute
##############
