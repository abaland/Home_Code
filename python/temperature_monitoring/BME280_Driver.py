########################
# Import local packages
########################

import BME280_Driver_Official_Adafruit  # Official BME280_Driver module, on which this relies.
import python.global_libraries.general_utils

__author__ = 'Baland Adrien'


####################################################################################################
# FUNCTION (is_valid_address)
####################################################################################################
# Revision History:
#   2016-11-04 AB - Function Created
####################################################################################################
def is_valid_address(sensor_address):
    """
    Tests whether provided address is a valid BME280 address for such sensors

    INPUT:
        address (string) : address to test

    RETURNS:
        (boolean) whether the address is a valid BME280 address,
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
        address (None) address of one-wire sensor
        temperature_correction (float) correction to apply to measurement value, to account for 
            external effects.


    RETURNS:
        (Dict) dictionnary as {'temperature': value}
    """

    # Initializes dictionnary of measurements collected
    all_values = {
        'temperature': None,
        'humidity': None,
        'pressure': None
    }

    # Creates BME280 object to measurements desired values.
    sensor_driver_object = BME280_Driver_Official_Adafruit.BME280(address)

    try:
        # Gets values from object created
        temperature = sensor_driver_object.read_temperature()
        humidity = sensor_driver_object.read_humidity()
        pressure = sensor_driver_object.read_pressure()

        # Applies correction to temperature
        temperature += temperature_correction

        # Updates dictionnary of values
        all_values = {
            'temperature': temperature,
            'humidity': humidity,
            'pressure': pressure
        }

    except TypeError as e:

        # Something went wrong when retrieving the values. Log error.
        details = 'Failed to get measures from BME280. %s' % str(e)
        python.global_libraries.general_utils.log_error(-409, details)

    ##################
    return all_values
    ##################

##########################
# END get_measurements()
##########################
