
########################
# Import Local Packages
########################
from python.global_libraries import general_utils

#########################
# Import global packages
#########################
try:
    import tsl2561

except ImportError as ex:

    # If package not installed, log error and cancel tsl2561 object
    tsl2561 = None
    error_details = 'Is TSL2561 package installed (pip)?'
    general_utils.log_error(-425, error_details, ex)

except SyntaxError as ex:

    # If package exists but raises syntax error, first
    tsl2561 = None
    error_details = 'Check TSL2561 package and remove first import __future__ line'
    general_utils.log_error(-425, error_details, ex)

########################
# Import local packages
########################

__author__ = 'Baland Adrien'


####################################################################################################
# FUNCTION (is_valid_address)
####################################################################################################
# Revision History:
#   2016-11-04 AB - Function Created
####################################################################################################
def is_valid_address(sensor_address):
    """
    Tests whether provided address is a valid TSL2561 address for such sensors

    INPUT:
        address (string) : address to test

    RETURNS:
        (boolean) whether the address is a valid TSL2561 address,
        (int) BME280 address to measure for sample collection.
    """

    # Initializes value
    valid_address = False  # Whether address is valid or not
    converted_address = -1  # Sensor address after conversion to appropriate format

    try:

        # Converts the hex string to its actual value.
        converted_address = int(sensor_address, 16)

        # Address for is between 0x02 and 0x78 for I2C Bus
        if 0x02 < converted_address < 0x78:

            valid_address = True

    # Could not convert the provided address to an integer, so address is not valid
    except ValueError:

        pass

    # Could not convert the provided address to an integer, so address is not valid
    except TypeError:

        pass

    # If address was valid, converted_address contained address to use, otherwise, sends False
    ########################################
    return valid_address, converted_address
    ########################################

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

    all_measures = ['luminosity']

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
def get_measurements(address, _):
    """
    Measures and returns all available measurements for the room as a dictionnary.

    INPUT:
        address (None) address of sensehat (to ignore)
        temperature_correction (float, unused) correction to apply to measurement value, to account 
            for external effects

    RETURNS:
        (Dict) dictionnary as {'luminosity': value1}
    """

    # Initializes dictionnary of measurements collected
    all_values = {
        'luminosity': None
    }

    try:

        if tsl2561 is not None:

            # Gets all measurements from Sensehat, and applies correction
            tsl2561_sensor = tsl2561.TSL2561(address)
            all_values['luminosity'] = tsl2561_sensor.lux()

    except IOError as e:

        # Something went wrong when retrieving the values. Log error.
        general_utils.log_error(-409, 'TSL2561', str(e))

    except Exception as e:

        # Something went wrong when retrieving values. Log error.
        # NOTE : Happened once with Exception 'Sensor is saturated'.
        general_utils.log_error(-409, 'TSL2561', str(e))

    ##################
    return all_values
    ##################

#######################
# END get_measurements
#######################
