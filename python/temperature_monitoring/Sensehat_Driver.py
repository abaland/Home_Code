########################
# Import Local Packages
########################

from global_libraries import general_utils

#########################
# Import global packages
#########################

try:

    from sense_hat import SenseHat  # Controls sensehat part on Raspberry

except ImportError as ex:

    # If package not installed, log error and cancel tsl2561 object
    SenseHat = None
    error_details = 'Is sensehat package installed (pip)?'
    general_utils.log_error(-425, error_details, ex)


__author__ = 'Baland Adrien'


####################################################################################################
# FUNCTION (is_valid_address)
####################################################################################################
# Revision History:
#   2016-11-04 AB - Function Created
####################################################################################################
def is_valid_address(address):
    """
    Tests whether provided address is a valid Sensehat address

    INPUT:
        address (None) : address to test (should be None)

    RETURNS:
        (Boolean) whether the address is a valid Sensehat address
        (None) address to use for Sensehat
    """

    # Checks whether the address provided is indeed None (no need for an address in Sensehat)
    if address is None:

        ##################
        return True, None
        ##################

    # Address is irrelevant here, but function needs to follow given format.
    ###################
    return False, None
    ###################

#######################
# END is_valid_address
#######################


####################################################################################################
# FUNCTION (get_measurement_types)
####################################################################################################
# Revision History:
#   2016-11-05 AB - Function Created
####################################################################################################
def get_measurement_types():
    """
    Returns names of all type of measurement that can be collected from sensor.

    RETURNS:
        (string[]) list of all types of measure from sensor (e.g. temperature, humidity, ...)
    """

    all_measures = ['temperature', 'humidity', 'pressure']

    ####################
    return all_measures
    ####################

############################
# END get_measurement_types
############################


####################################################################################################
# Function(get_measurements)
####################################################################################################
# Revision History:
#   2016-11-04 AB - Function Created
####################################################################################################
def get_measurements(address, temperature_correction):
    """
    Measures and returns all available measurements for the room as a dictionnary.

    INPUT:
        address (None) address of sensehat (to ignore)
        temperature_correction (float) correction to apply to measurement value, to account for 
            external effects.

    RETURNS:
        (Dict) dictionnary as {'temperature': value1, 'humidity': value2, 'pressure': value3}
    """

    # Removes address since it is irrelevant
    del address

    # Initializes dictionnary of measurements collected
    all_values = {
        'temperature': None,
        'humidity': None,
        'pressure': None
    }

    if SenseHat is not None:

        try:
            # Gets all measurements from Sensehat, and applies correction
            sense = SenseHat()
            all_values['temperature'] = sense.get_temperature() + temperature_correction
            all_values['humidity'] = sense.get_humidity()
            all_values['pressure'] = sense.get_pressure()

        except Exception as e:

            # Something went wrong when retrieving the values. Log error.
            general_utils.log_error(-409, 'Sensehat', str(e))

    ##################
    return all_values
    ##################

#######################
# END get_measurements
#######################
