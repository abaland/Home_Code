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
target_to_driver = {
    'living_aircon': living_aircon_driver,
    'living_light': living_lights_driver,
    'bedroom_aircon': bedroom_aircon_driver,
    'bedroom_light': bedroom_lights_driver,
    'tv': tv_remote_driver
}


####################################################################################################
# read_pin_configuration
####################################################################################################
# Revision History :
#   2017-05-19 Adba : Function created
####################################################################################################
def read_pin_configuration(sand_box):
    """
    Processes infrared remote instruction

    INPUT:
         sand_box (dict): worker sand_box attribute, to update with info about which pin to
            control when sending signal to a given machine
    """


    #######
    return
    #######

#############################
# END read_pin_configuration
#############################


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

    INPUT:
         worker (Worker): worker instance
         instruction_as_xml (lxml.etree): message to process
         base_response (lxml.etree): base of worker response on which to build

    OUTPUT :
         (lxml.etree): worker response
    """

    if 'remote' not in worker_instance.sand_box.keys():

        read_pin_configuration(worker_instance.sand_box)

    # Creates base response to be completed in instruction
    remote_control_response = worker_base_response

    # Gets name of remote to simulate.
    remote_to_use = instruction_as_xml.get('remote')

    # Retrieves appropriate driver using remote name.
    appropriate_driver = target_to_driver.get(remote_to_use, None)
    if appropriate_driver is not None:

        # Retrieves the "button" to simulate (button name or full configuration information).
        #   Example: for tv : 'Power', 'Mute', ....  for aircon : 'on,heat,25,strong,highest'
        configuration_to_send = instruction_as_xml.get('config')
        try:

            # Split the comma-separated info (only puts in array if button name)
            configuration_splitted = configuration_to_send.split(',')

            # Sends each element in array as argument (button name or each of full config parameter)
            status_code = appropriate_driver.send_signal(*configuration_splitted)

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
