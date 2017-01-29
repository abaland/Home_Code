"""
Monitor different variables from sensor connected to the Raspberry Pi.

Every t intervals of time, collect measures from all samples.
Every n*t intervals of time, outputs average of collected measures.
To reduce variation in output, output is smoothed by outputting the average of the last k sample-averages.

Example:
     If t = 5, n = 3, k = 3 and that the first 4 sequences of collected samples are [19, 20, 21], [21, 22, 21], [21, 20,
     21], [21, 24, 24].
     The sample averages are 20, 21.33, 20.66 and 23, and the values exported 20, 20.66, 20.66, 21.66

NOTES:
    (1) For unknown reason, calling Sensehat then DHT11 does not work (only 38/40 bits get read). Calling DHT11 then
        Sensehat works without problem. Other sensors not tested, but to be safe, put Sensehat at the end of config.
"""

#########################
# Import global packages
#########################

import ConfigParser  # Reads configuration files for sensor plugged into Raspberry
import os  # Allows file creation/deletion (for output values)
import time  # Measures when to print output, collect samples, ...
import urllib2  # Connects to website to post measured data

import BME280_Driver  # BME280 Sensor. Extension to official Adafruit module
import DHT11_Driver  # DHT11 Sensor
import DS18B20_Driver  # DS18B20 (One-wire) Sensor
import TSL2561_Driver  # TSL2561_Driver

########################
# Import Local Packages
########################

import python.global_libraries.general_utils as general_utils
import python.temperature_monitoring.Sensehat_Driver as Sensehat_Driver  # Sensehat

__author__ = 'Baland Adrien'  # That's me, yeay.

###########################
# Declare global variables
###########################

# Location of the configuration file in Raspberry, with information for each connected sensor, thingspeak, ...
config_file_url = '/home/pi/Home_Code/configs/SensorConfig.ini'

# Defaults parameters if missing in config file.
sample_interval = 5  # Seconds to wait between two successive sensor reads
n_sample_for_average = 6  # Number of successive samples taken before they are averaged and an output is made
n_average_for_smooth = 5  # Number of successive averaged samples used for smoothing (value printed)

thingspeak_url = None  # Address where to post data online if thingspeak_key present in config file.

list_all_output_directories = []  # List of all output directories to use, to avoid redundancy between sensors

# Mapping from all supported sensor types to their respective driver module.
sensor_to_driver = {
    'BME280': BME280_Driver,
    'DS18B20': DS18B20_Driver,
    'DHT11': DHT11_Driver,
    'Sensehat': Sensehat_Driver,
    'TSL2561': TSL2561_Driver
}

##############################################
# Characteristics for each of the sensors
##############################################
all_sensors = [
    # Each entry has the form
    {
        'name': 'sensor_name',  # additional info about sensor (e.g. where it is)
        'type': 'BME280',  # Sensor type. One of BME280, DS18B20, Sensehat, DHT11
        'address': 0x76,  # Sensor address, (I2C for BME280, 1wire for DS18B20, GPIO Pin for DHT11, None for Sensehat)
        'correction': 0.0,  # Correction for sensor (only applied for temperature now, might be changed later)
        'warmup': 0.0,  # Time necessary for a sensor to warmup (measures ignored during warmup)
        'last_failed_measure_time': 0.0,  # Last time a sensor measurement could not be made
        'output_directory': '/home/pi/...',  # Where to create .dat files with measure values,
        'samples_to_average': {},  # list of samples for all available measurements, before they are averaged
        'n_last_averages': {},  # list of previous measurements averages, to be averaged for output (smoothing),
        'smoothed_average': {}  # Last smoothed average measurements.
    }
]


########################################################################################################################
# Function (convert_localtime_to_string)
########################################################################################################################
# Revision History:
#   2016-10-27 AB - Function Created
########################################################################################################################
def convert_localtime_to_string(stamp):
    """
    Converts a time.localtime() object to a string formatted as YYY-MM-DD hh:mm:ss

    INPUT:
        Stamp : time.localtime object to convert

    RETURNS:
        (str) string-formatted timestamp
    """

    formatted_stamp = '%02d-%02d-%02d %02d:%02d:%02d' % (stamp[0], stamp[1], stamp[2], stamp[3], stamp[4], stamp[5])

    #######################
    return formatted_stamp
    #######################

##################################
# END convert_localtime_to_string
##################################


########################################################################################################################
# Function (parse_sensor_config)
########################################################################################################################
# Revision History:
#   2016-10-27 AB - Function Created
#   2016-11-05 AB - Added SenseHat + Made function more general
########################################################################################################################
def parse_sensor_config(parsed_configuration, sensor_name, sensor_type):
    """
    Parses information for a given sensor from the configuration file.
    
    INPUT:
        parsed_configuration (ConfigParser object) : configuration parsed by ConfigParser
        sensor_name (str) : name of the sensor to parse (SensorX with X integer)
        sensor_type (str) : type of the sensor to parse
        
    RETURNS:
        (int) 0 if sensor was parsed normally, negative number if parsing reached fatal error
    """

    # Creates default parameters in case an option is missing.
    temperature_correction = 0.0  # Correction to apply on temperature measurements (calibration).
    sensor_warmup = 0.0  # Time necessary for sensor to warmup (values are ignored during warmup)
    output_directory = '/home/pi/'  # Where to write measurements : Base directory
    sensor_location = sensor_name  # Where to write measurement : Subdirectory

    #################
    # Sensor address
    #################
    #  If sensor is a sensehat, address does not exist. Otherwise, address required.
    if sensor_type == 'Sensehat':

        sensor_address = None

    # Otherwise, address is a required parameter
    elif not parsed_configuration.has_option(sensor_name, 'address'):

        # No address could be found, log an error and stop parsing for that sensor.
        #################################################
        return general_utils.log_error(-403, sensor_name)
        #################################################

    else:

        # Parse the address as a string (checked later)
        sensor_address = parsed_configuration.get(sensor_name, 'address')

    # Tests whether the address provided is valid using the appropriate drivers and converts to appropriate format
    valid_address, converted_address = sensor_to_driver.get(sensor_type).is_valid_address(sensor_address)

    # Reports problem with address in case it is invalid
    if not valid_address:

        # Stops execution since it will be impossible to get sensor values
        details = '(' + sensor_name + ', ' + sensor_address + ')'
        #############################################
        return general_utils.log_error(-404, details)
        #############################################

    ####################################
    # Temperature correction (optional)
    ####################################
    if parsed_configuration.has_option(sensor_name, 'correction'):

        try:

            # Gets temperature correction to apply (integer of float)
            temperature_correction = parsed_configuration.getfloat(sensor_name, 'correction')

        except ValueError as e:

            # Correction parameter value could not be interpreted, log error but uses 0.0 default.
            details = '(' + sensor_name + ', ' + parsed_configuration.get(sensor_name, 'correction') + ')'
            general_utils.log_error(-405, details, e)

    ################################
    # Sensor warmup time (optional)
    ################################
    if parsed_configuration.has_option(sensor_name, 'warmup'):

        try:

            # Gets time required for sensor to warmup (positive integer or float)
            candidate_sensor_warmup = parsed_configuration.getfloat(sensor_name, 'warmup')

            if candidate_sensor_warmup >= 0.0:

                # Sensor warmup inside configuration is valid : update parameters
                sensor_warmup = candidate_sensor_warmup

            else:

                # Warmup parameter value was negative, log error and uses 0.0 default.
                details = '(' + sensor_name + ', ' + parsed_configuration.get(sensor_name, 'warmup') + ')'
                general_utils.log_error(-420, details)

        except ValueError as e:

            # Correction parameter value could not be interpreted, log error but uses 0.0 default.
            details = '(' + sensor_name + ', ' + parsed_configuration.get(sensor_name, 'warmup') + ')'
            general_utils.log_error(-420, details, e)

    ###############################################################
    # Output directory (to be combined later with location).
    ###############################################################
    if parsed_configuration.has_option(sensor_name, 'output_directory'):

        output_directory = parsed_configuration.get(sensor_name, 'output_directory')

    else:

        # Could not parse output directories, so log error but uses default.
        general_utils.log_error(-406, sensor_name)

    ##################
    # Sensor location
    ##################
    if parsed_configuration.has_option(sensor_name, 'location'):

        sensor_location = parsed_configuration.get(sensor_name, 'location')

    else:

        # Could not parse location (also used for output directory), so uses sensor name as default.
        general_utils.log_error(-407, sensor_name)

    ############################
    #  Parsing done : now apply
    ############################
    # Combines output_directory and sensor_location to get actual directory where output is made
    if output_directory.endswith('/'):

        # Output_directory already ended with '/' => append sensor_location and '/'
        output_directory += sensor_location + '/'

    else:

        # Output_directory did not end with '/' => append '/', sensor_location and '/' again.
        output_directory += '/' + sensor_location + '/'

    ######################################
    # Creates corresponding sensor object
    ######################################

    # Only adds sensor if its unique identifiers (output_directory) have not been added before
    if output_directory not in list_all_output_directories:

        # Gets list of all different measures that the sensor can colllect, to initialze dictionnaries
        all_measurement_types = sensor_to_driver.get(sensor_type).get_measurement_types()

        # Initializes list for collected samples (before average)
        sample_to_average_init = {measurement: [] for measurement in all_measurement_types}

        # Initializes list for computed average (before smoothing). This starts an array with n None entries for each
        # measurement type
        n_last_averages_init = {measurement: [None for _ in range(n_average_for_smooth)] for measurement in
                                all_measurement_types}

        # Initializes list for computed smoothed average
        smoothed_average = {measurement: 0.0 for measurement in all_measurement_types}

        sensor = {
            # Base information
            'name': sensor_location,
            'type': sensor_type,
            'address': converted_address,
            'correction': temperature_correction,
            'warmup': sensor_warmup,
            'output_directory': output_directory,
            # Last time a BME280 measurement failed. Used to incorporate warm-up time.
            'last_failed_measure_time': time.time(),
            # Samples to use for averaging
            'samples_to_average': sample_to_average_init,
            # Averages to use for smoothing
            'n_last_averages': n_last_averages_init,
            # Latest value outputed
            'smoothed_average': smoothed_average
        }

        all_sensors.append(sensor)

    else:

        # Redundancy in information detected, log error and DO NOT adds sensor
        details = '(%s, %s)' % (sensor_location, output_directory)
        general_utils.log_error(-414, details)

    #########
    return 0
    #########

##########################
# END parse_sensor_config
##########################


########################################################################################################################
# Function (read_configuration)
########################################################################################################################
# Revision History:
#   2016-10-27 AB - Function Created
#   2016-11-02 AB - Added heater configuration parsing
#   1016-11-05 AB - Remove heater configuration (not relevant at home).
########################################################################################################################
def read_configuration(config_filename):
    """
    Reads configuration file containing all sensor/heater information and updates internal parameters accordingly.
    Parameters include:
        General parameters (time between measurements, number of measurements for average, smoothing)
        Sensor parameters (location, output, correction, ...)

    INPUT:
        config_filename (str) name of configuration file
        
    OUTPUT:
        error_code (int) 0 if no fatal problem while reading configuration file, negative integer otherwise
    """

    # Deletes example sensor from code (in global variable)
    all_sensors.pop()

    ########################################
    # Creates configuration parser + parses
    ########################################
    parsed_config = ConfigParser.RawConfigParser()
    if not os.path.isfile(config_filename):

        #####################################################
        return general_utils.log_error(-401, config_filename)
        #####################################################

    else:

        parsed_config.read(config_filename)

    ############################################################
    # Gets general parameters for sample collection / averaging
    ############################################################
    if parsed_config.has_section('General'):

        ##################
        # Sample Interval
        ##################
        if parsed_config.has_option('General', 'sample_interval'):

            try:

                # Reads value from config file.
                candidate_sample_interval = parsed_config.getfloat('General', 'sample_interval')

                # Tests if value in configuration is valid (positive number)
                if candidate_sample_interval > 0.0:

                    # Valid value : update internal parameters
                    global sample_interval
                    sample_interval = candidate_sample_interval

                else:

                    # Value was number, but not positive
                    value_from_config = parsed_config.get('General', 'sample_interval')
                    details = 'Value must be positive (%s, %s).' % ('sample_interval', value_from_config)
                    general_utils.log_error(-412, details)

            except ValueError as e:

                # Value was not a number
                value_from_config = parsed_config.get('General', 'sample_interval')
                details = 'Value must be a number (%s, %s).' % ('sample_interval', value_from_config)
                general_utils.log_error(-412, details, str(e))

        else:

            # Configuration file did not have parameter
            general_utils.log_error(-412, 'sample_interval')

        ###################
        # N Sample For Avg
        ###################
        if parsed_config.has_option('General', 'n_sample_for_average'):

            try:

                # Reads value from config file.
                candidate_n_sample_for_average = parsed_config.getint('General', 'n_sample_for_average')

                # Tests if value in configuration is valid (positive integer)
                if candidate_n_sample_for_average > 0:

                    global n_sample_for_average
                    n_sample_for_average = candidate_n_sample_for_average

                else:

                    # Value was integer, but not positive
                    value_from_config = parsed_config.get('General', 'n_sample_for_average')
                    details = 'Value must be positive integer (%s, %s).' % ('n_sample_for_average', value_from_config)
                    general_utils.log_error(-412, details)

            except ValueError as e:

                # Value was not an integer
                value_from_config = parsed_config.get('General', 'n_sample_for_average')
                details = 'Value must be integer (%s, %s).' % ('n_sample_for_average', value_from_config)
                general_utils.log_error(-412, details, str(e))

        else:

            # Configuration file did not have parameter
            general_utils.log_error(-412, 'n_sample_for_average')

        ###################
        # N Avg For Smooth
        ###################
        if parsed_config.has_option('General', 'n_average_for_smooth'):

            try:

                # Reads value from config file
                candidate_n_average_for_smooth = parsed_config.getint('General', 'n_average_for_smooth')

                # Tests if value in configuration is valid (positive integer)
                if candidate_n_average_for_smooth > 0:

                    global n_average_for_smooth
                    n_average_for_smooth = candidate_n_average_for_smooth

                else:

                    # Value was integer, but not positive
                    value_from_config = parsed_config.get('General', 'n_average_for_smooth')
                    details = 'Value must be positive integer (%s, %s).' % ('n_average_for_smooth', value_from_config)
                    general_utils.log_error(-412, details)

            except ValueError as e:

                # Value was not an integer
                value_from_config = parsed_config.get('General', 'n_average_for_smooth')
                details = 'Value must be integer (%s, %s).' % ('n_average_for_smooth', value_from_config)
                general_utils.log_error(-412, details, str(e))

        else:

            # Configuration file did not have parameter
            general_utils.log_error(-412, 'n_average_for_smooth')

        ################################
        # Thingspeak API URL (Optional)
        ################################
        if parsed_config.has_option('General', 'thingspeak_key'):

            # Configuration file only contains API key, so after it is parsed, merged it with base url.
            global thingspeak_url
            thingspeak_key = parsed_config.get('General', 'thingspeak_key')
            thingspeak_url = 'https://api.thingspeak.com/update?api_key=%s' % thingspeak_key

    ######################################
    # Gets all supported sensors to query
    ######################################
    sensor_index = 0
    while True:

        sensor_name = 'Sensor' + str(sensor_index)

        # Check whether the sensor exist. Assumes config file has sensor listed as 'Sensor17, 'Sensor2', 'Sensor3', ...
        if parsed_config.has_section(sensor_name):

            # Check whether the sensor has the fundamental characteristics (type and address)
            if parsed_config.has_option(sensor_name, 'type'):

                # Checks if sensor is a supported i2c or 1wire sensor
                sensor_type = parsed_config.get(sensor_name, 'type')
                if sensor_type in sensor_to_driver.keys():

                    # If supported sensor, parses its information and adds it to sensor list
                    parse_sensor_config(parsed_config, sensor_name, sensor_type)

                else:

                    # Saw an unidentified sensor, print an error but keep parsing
                    details = '(%s, %s)' % (sensor_name, sensor_type)
                    general_utils.log_error(-402, details)

            else:

                # Saw a sensor without required info, log error but keep parsing
                general_utils.log_error(-403, sensor_name)

            # Sensor processing finished. Moves on to the next sensor
            sensor_index += 1

        else:

            # If the sensor did not exist, stop searching.
            break

    # No sensors could be detected if config file
    if sensor_index == 0:

        #####################################################
        return general_utils.log_error(-415, config_filename)
        #####################################################

    # No VALID sensor could be detected in config file
    if len(all_sensors) == 0:

        ####################################
        return general_utils.log_error(-423)
        ####################################

    ########
    return 0
    ########

#########################
# END read_configuration
#########################


########################################################################################################################
# Function (initialize_data_files)
########################################################################################################################
# Revision History:
#   2016-10-27 AB - Function Created
########################################################################################################################
def initialize_data_files():
    """
    Initializes all required folders to export measurements from sensor.
    
    RETURNS:
        error_code (int) 0 if no fatal problem while initializing output folders, negative integer otherwise
    """

    # For each i2c sensor registered
    for sensor in all_sensors:

        output_directory = sensor['output_directory']

        # Creates necessary directories if they did not exist already
        if not os.path.exists(output_directory):

            try:

                # Creates directories recursively to reach desired address
                os.makedirs(output_directory)

            except OSError as e:

                # Could not create all directories, so stop code execution
                ##############################################################
                return general_utils.log_error(-410, output_directory, str(e))
                ##############################################################

    #########
    return 0
    #########

############################
# END initialize_data_files
############################


########################################################################################################################
# Function (read_sensor_values)
########################################################################################################################
# Revision History:
#   2016-10-27 AB - Function Created
#   2016-10-28 AB - Added filter for outliers and warmup phase
########################################################################################################################
def read_sensor_values():
    """
    Collects sample from all registered sensors.
    """

    # For each sensor registered
    for sensor_object in all_sensors:

        sensor_name = sensor_object['name']
        sensor_address = sensor_object['address']

        try:

            # Fetched the relevant module depending on sensor type and calls its get_measurements function.
            appropriate_driver = sensor_to_driver.get(sensor_object['type'])
            all_values = appropriate_driver.get_measurements(sensor_address, sensor_object['correction'])

            # Ignore value if sensor is in a warm-up phase.
            current_time = time.time()
            in_warmup = current_time < sensor_object['last_failed_measure_time'] + sensor_object['warmup']

            # Only adds if value must not be filtered
            if not in_warmup:

                # Adds every type of measurement collected by the sensor. (Temperature, Humidity, Pressure, ...)
                for measurement in all_values.keys():

                    # Only adds measure if it succeedeed
                    if all_values[measurement] is not None:

                        sensor_object['samples_to_average'][measurement].append(all_values[measurement])

        except IOError as e:

            # Measuring sensor failed => Assume disconnection and assume warm-up must take place again
            sensor_object['last_failed_measure_time'] = time.time()

            details = '(' + sensor_name + ', ' + hex(sensor_address) + ')'
            general_utils.log_error(-409, details, str(e))

        except ImportError as e:

            # NOTE : This error would be linked to core files missing instead, so reboot might be necessary.
            # Measuring sensor failed => Assume disconnection and assume warm-up must take place again
            sensor_object['last_failed_measure_time'] = time.time()

            details = '(' + sensor_name + ', ' + hex(sensor_address) + ')'
            general_utils.log_error(-409, details, str(e))

    #######
    return
    #######

#########################
# END read_sensor_values
#########################


########################################################################################################################
# Function (remove_obsolete_data)
########################################################################################################################
# Revision History:
#   2016-10-27 AB - Function Created
#   2016-11-05 AB - Generalized function (measure-independent)
########################################################################################################################
def remove_obsolete_data():
    """
    Removes data from more than N averaged samples ago (if it exists).
    This is only used for the smoothing function
    """

    # Removes "too-old" values for all of the registered sensors.
    for sensor_object in all_sensors:

        try:

            # Removes oldest value for all types of measurements.
            for measurement in sensor_object['n_last_averages'].keys():

                # Removes very first (oldest) average in memory, to keep constant number of entries in smoothing array).
                sensor_object['n_last_averages'][measurement].pop(0)

        except IndexError:

            # The list was empty, so there is nothing to remove.
            # This should NEVER happen, since number of entries should be constant
            pass

    ######
    return
    ######

###########################
# END remove_obsolete_data
###########################


########################################################################################################################
# Function (output_data)
########################################################################################################################
# Revision History:
#   2016-10-27 AB - Function Created
#   2016-11-05 AB - Generalized function (measure-independent)
########################################################################################################################
def output_data(sensor_dictionnary_object):
    """
    Creates .dat files for data to output for a given sensor, and write said output in these files.
    
    INPUT:
        sensor_dictionnary_object {Dict} information about a sensor, as shown in global variables
    """

    # Gets the output directories, where the file must be created
    output_directory = sensor_dictionnary_object['output_directory']

    # For every type of measurement, create a dat.file as  output_directory/measurement_name.dat
    for measurement in sensor_dictionnary_object['smoothed_average'].keys():

        output_filename = '%s%s.dat' % (output_directory, measurement)
        value_to_export = '%0.3f' % (sensor_dictionnary_object['smoothed_average'][measurement],)
        general_utils.create_os_file(output_filename, value_to_export)

    #######
    return
    #######

##################
# END output_data
##################


########################################################################################################################
# Function (delete_output_files)
########################################################################################################################
# Revision History:
#   2016-10-27 AB - Function Created
#   2016-11-05 AB - Generalized function (measure-independent)
########################################################################################################################
def delete_output_files(sensor_dictionnary_object):
    """
    Deletes .dat files that were created by this script.
    Used when failing to get value from the sensors => avoid having a file that gives the impression that code is still
    working fine
    
    INPUT:
        sensor_dictionnary_object {Dict} information about a sensor, as shown in global variables
    """

    # Gets the output directories, where the files were created
    output_directory = sensor_dictionnary_object['output_directory']

    # For every type of measurement, removes dat.file
    for measurement in sensor_dictionnary_object['smoothed_average'].keys():

        output_filename = '%s%s.dat' % (output_directory, measurement)
        general_utils.delete_os_file(output_filename)

    #######
    return
    #######

##########################
# END delete_output_files
##########################


########################################################################################################################
# Function (average_ignore_none)
########################################################################################################################
# Revision History:
#   2016-10-27 AB - Function Created
########################################################################################################################
def average_ignore_none(array_with_none):
    """
    Computes the average of an array that may contain None entries, by filtering these entries then averaging on the
    residue.
    
    INPUT:
        array_with_none ((float|int|None)[]) : array of values for average computation
        
    RETURNS:
        (float) : average value in array, discarding None values
    """

    not_none_count = 0
    array_average = 0.0

    # Only count/add non-None elements
    for element in array_with_none:

        if element is not None:

            array_average += element
            not_none_count += 1

    # Returns zero if the array contains nothing but None
    if not_none_count == 0:

        array_average = 0.0

    # Else return the average of entries grabbed
    else:

        array_average /= not_none_count

    ####################
    return array_average
    ####################

##########################
# END average_ignore_none
##########################


########################################################################################################################
# Function (average_sensor_measures)
########################################################################################################################
# Revision History:
#   2016-10-27 AB - Function Created
#   2016-11-05 AB - Generalized function (measure-independent)
########################################################################################################################
def average_sensor_measures(sensor_dictionnary_object):
    """
    Averages successive sample values into on intermediary average, smoothes it using previous averages, then outputs
    it

    INPUT:
        sensor_dictionnary_object {Dict} information about a sensor, as shown in global variables
    """

    # Applies the process to all types of measurements made
    for measurement in sensor_dictionnary_object['samples_to_average'].keys():

        # One of the measure could never be collected.
        if len(sensor_dictionnary_object) == 0:

            details = '(%s, %s)' % (sensor_dictionnary_object['name'], measurement)
            general_utils.log_error(-424, details)
            continue

        # Gets all samples to create average (before smoothing)
        latest_data_samples = sensor_dictionnary_object['samples_to_average'][measurement]

        # Computes average (before smoothing)
        sample_average = 1.0 * sum(latest_data_samples) / len(latest_data_samples)

        # Deletes samples used (will not be used later)
        sensor_dictionnary_object['samples_to_average'][measurement] = []

        # Adds newly computed average to list of averages
        sensor_dictionnary_object['n_last_averages'][measurement].append(sample_average)

        ############
        # Smoothing
        ############

        # Gets sequence of last averages computed
        n_last_averages = sensor_dictionnary_object['n_last_averages'][measurement]

        # Smoothes these average by computing their own average (discarding None)
        smoothed_average = average_ignore_none(n_last_averages)

        # Updates smoothed_average value in sensor info.
        sensor_dictionnary_object['smoothed_average'][measurement] = smoothed_average

        #########
        # Output
        #########

        print("Average %s : %2.2f" % (measurement, sample_average))
        print("Smoothed Average %s : %2.2f" % (measurement, smoothed_average))

    # Writes all new measures into appropriate files once all computations are over
    output_data(sensor_dictionnary_object)

    #######
    return
    #######

##############################
# END average_sensor_measures
##############################


########################################################################################################################
# Function (post_collection_actions)
########################################################################################################################
# Revision History:
#   2016-10-27 AB - Function Created
########################################################################################################################
def post_collection_actions():
    """
    Applies post-sample-collection actions. If samples successfully collected, averages, smoothes, and prints them. If
    samples failed to be collected, deletes all output_files to show failure.

    """

    # For each  sensor registered
    for sensor_object in all_sensors:

        print("== Sensor %s ==" % sensor_object["name"])

        # Only computes/print smoothed average if values have been retrieved in the last sample_collection
        first_key = sensor_object['samples_to_average'].keys()[0]
        if len(sensor_object['samples_to_average'][first_key]) > 0:

            print("Number of Samples: " + str(len(sensor_object['samples_to_average'])))

            average_sensor_measures(sensor_object)

        # Otherwise, append None to the average list (to balance the remove_obsolete_data function)
        else:

            for measurement in sensor_object['samples_to_average'].keys():

                sensor_object['n_last_averages'][measurement].append(None)
                sensor_object['smoothed_average'][measurement] = None

            # Deletes the .dat files.
            delete_output_files(sensor_object)

            print('No measurement.\n\n')

    ######
    return
    ######

##############################
# END post_collection_actions
##############################


####################################################################################################################
# Function(output_measures_to_web)
####################################################################################################################
def output_measures_to_web():
    """
    Exports all smoothes averages collected from each sensor to thingspeak website.
    """

    all_fields_as_string = ''  # String containing all measure values (arguments for request)
    field_index = 1  # Current index of argument to send

    # Goes through each measurement or each sensor to construct the string
    for sensor_object in all_sensors:

        for measurement in sensor_object['smoothed_average'].keys():

            # Gets value, and augments the string with '&fieldX=YY.YYY' , with X index and YY.YYY value. (ignore None)
            try:

                measurement_value = float(sensor_object['smoothed_average'][measurement])
                all_fields_as_string += '&field%d=%0.3f' % (field_index, measurement_value)

            except TypeError:

                # Value was None, so could not be converted to float => ignore and move on to next measure.
                pass

            # Increments field_index for following arguments
            field_index += 1

    # Constructs URL to use to post data.
    update_url = thingspeak_url + all_fields_as_string

    try:

        # GET request for url to update data.
        urllib2.urlopen(update_url)

    except urllib2.URLError:

        # Failed to send request to update data. Log error but continue
        general_utils.log_error(-419, update_url)

    #######
    return
    #######

#############################
# END output_measures_to_web
#############################


########################################################################################################################
# Function(main)
########################################################################################################################
# Revision History:
#   2016-11-02 AB - Function Created
########################################################################################################################
def main():
    """
    Monitors constantly temperature in the room and print out measurements at regular intervals.
    """

    script_class_name = 'Home-Monitoring'

    # Prints welcome message
    general_utils.get_welcome_end_message(script_class_name, is_start=True)

    # Read configuration file to get values
    print('Reading config...'),
    success_status = read_configuration(config_file_url)
    if success_status == 0:

        print('done.')

    else:

        # An error occured when reading configuration file, so exit.
        general_utils.get_welcome_end_message(script_class_name, is_start=False)
        exit(success_status)

    # Deletes temporary variables now that config has been processed properly
    global list_all_output_directories
    del list_all_output_directories

    # Initializes the data files in which to write to
    print('Checking files...'),
    success_status = initialize_data_files()
    if success_status == 0:

        print('done.')

    else:

        # An error occured when creating output folders, so exit.
        general_utils.get_welcome_end_message(script_class_name, is_start=False)
        exit(success_status)

    # Computes sampling time
    total_waiting_time = sample_interval * n_sample_for_average

    # Infinite loop of sample-collection, averaging, printing
    while True:

        # Current time
        sample_collection_start_time = time.time()

        # Time until sample collection stops and aggregation starts
        sample_collection_end_time = sample_collection_start_time + total_waiting_time

        # Time to print in the output (average of start and end)
        sample_collection_half_time = time.localtime(0.5 * (sample_collection_start_time + sample_collection_end_time))

        # Loop while sample time is within the same minute
        while time.time() < sample_collection_end_time:

            # Reads sensor values and appends them to sample list if value must not be filtered
            read_sensor_values()

            # Pause and re-read sensor value
            time.sleep(sample_interval)

        ##################################################################################
        # All samples recorded for the current minute value. Process the samples retrieved
        ##################################################################################

        # Remove data that has become to old to be used in smoothing
        remove_obsolete_data()

        print("==========================")
        print("=== %s ===" % convert_localtime_to_string(sample_collection_half_time))
        print("==========================")

        # Processes new samples
        post_collection_actions()

        if thingspeak_url is not None:

            output_measures_to_web()

###########
# END main
###########

if __name__ == "__main__":
    main()
