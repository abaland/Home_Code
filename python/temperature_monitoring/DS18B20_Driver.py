#########################
# Import global packages
#########################

import os  # Allows navigation through filesystem to read values

########################
# Import local packages
########################

from python.global_libraries import general_utils  # Prints starting/ending message as well as all errors messages

__author__ = 'Baland Adrien'


########################################################################################################################
# FUNCTION (is_valid_address)
########################################################################################################################
# Revision History:
#   2016-11-04 AB - Function Created
########################################################################################################################
def is_valid_address(address_string):
    """
    Tests whether provided address is a valid DS18B20 address for such sensors

    INPUT:
        address_string (string) : address to test

    RETURNS:
        (Boolean) whether the address is a valid DS18B20 address
        (string) address to use to collect samples
    """

    # Checks whether the address provided is indeed 15 characters (is this an actual requirement??)
    if len(address_string) == 15:

        ############################
        return True, address_string
        ############################

    #################
    return False, ''
    #################

#######################
# END is_valid_address
#######################


########################################################################################################################
# FUNCTION (get_measurement_types)
########################################################################################################################
# Revision History:
#   2016-11-05 AB - Function Created
########################################################################################################################
def get_measurement_types():
    """
    Returns names of all type of measurement that can be collected from sensor.

    RETURNS:
        (string[]) list of all types of measure from sensor (e.g. temperature, humidity, ...)
    """

    all_measures = ['temperature']

    ####################
    return all_measures
    ####################

############################
# END get_measurement_types
############################


########################################################################################################################
# FUNCTION (read_temperature)
########################################################################################################################
def read_temperature(address):

    # Initializes temperature
    temperature = None

    # Address of the file containing the measure
    url_file = '/sys/devices/w1_bus_master1/' + str(address) + '/w1_slave'
    
    if os.path.isfile(url_file):
        
        # Array to contain content of slave_file
        slave_info = []
        
        # Gets name of all slaves (names are used later, to open this file as short as possible)
        with open(url_file, 'r') as slave_file:
            
            # Slave file has 2 lines : crc/detect info, and value info.
            for line in slave_file:

                # Strips linebreak
                slave_info.append(line[:-1])
            
            # First line contain crc/detect info => metadata. Second line contains value at the end
            meta = slave_info[0]
            value = slave_info[1]
            
            # Only process the value if the metadata line says the measure is ok
            if not meta.startswith('00 00 00 00 00 00 00 00 00') and not meta.endswith('NO'):
                
                try:

                    # Reads temperature (written as 28000 for 28C, so divide by 1000) and adds correction
                    temperature = float(value.split('t=')[1]) / 1000

                except ValueError as e:
    
                    details = '(' + address + '). Could not parse temperature.'
                    general_utils.log_error(-409, details, str(e))

            else:

                details = '(' + address + '). Bad content in file.'
                general_utils.log_error(-409, details)

    else:

        details = '(' + address + '). Slave file does not exist.'
        general_utils.log_error(-409, details)
        
    ##################
    return temperature
    ##################

#######################
# END read_temperature
#######################


####################################################################################################################
# Function(get_measurements)
####################################################################################################################
# Revision History:
#   2016-11-04 AB - Function Created
########################################################################################################################
def get_measurements(address, temperature_correction):
    """
    Measures and returns all available measurements for the room as a dictionnary.

    INPUT:
        address (None) address of one-wire sensor
        temperature_correction (float) correction to apply to measurement value, to account for external effects.


    RETURNS:
        (Dict) dictionnary as {'temperature': value}
    """

    # Initializes dictionnary of measurements collected
    all_values = {
        'temperature': None
    }

    # Reads temperature
    temperature = read_temperature(address)

    # If temperature was successfully measured, applies correction
    if temperature is not None:

        all_values['temperature'] = temperature - temperature_correction

    ##################
    return all_values
    ##################

##########################
# END get_measurements()
##########################
