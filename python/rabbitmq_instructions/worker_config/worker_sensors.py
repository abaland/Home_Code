from lxml import etree  # Converts worker response element to a tree-like object
import os
from temperature_monitoring import home_environment_sensors
from global_libraries import general_utils


####################################################################################################
# get_sensor_list
####################################################################################################
# Revision History :
#    2017-05-23 Adba : Function created
####################################################################################################
def get_sensor_list(rabbit_worker_object):
    """
    Gets list of sensor information

    INPUT
        rabbit_worker_object (Worker) worker instance
    """

    # Makes home_environment_sensors script read sensor configuration, to update sensor list
    home_environment_sensors.read_configuration(home_environment_sensors.config_file_url)
    
    # Gets list of sensors parsed in configuration
    all_sensors = home_environment_sensors.all_sensors
    
    # Initializes the list of mapping between sensor name and their output directories
    sensor_to_output_mapping = {}
    
    # Adds sensor mapping one by one. I2C part.
    for sensor_dictionnary in all_sensors:
        
        sensor_to_output_mapping[sensor_dictionnary['name']] = {
            'type': sensor_dictionnary['type'],
            'measurement_type': sensor_dictionnary['samples_to_average'].keys(),
            'output': sensor_dictionnary['output_directory']
        }

    # Adds sensor mapping to worker internal parameters, to avoid reparsing configuration later
    rabbit_worker_object.sand_box['sensors'] = sensor_to_output_mapping
    
    general_utils.log_message('Finished parsing sensor configuration.')

    ################################
    return sensor_to_output_mapping
    ################################

######################
# END get_sensor_list
######################


####################################################################################################
# get_sensor_values
####################################################################################################
# Revision History :
#    2017-05-23 Adba : Function created
####################################################################################################
def get_sensor_values(output_directory, measurement_type_list, sensor_status):
    """
    Inspects folder created by home_environment_sensors (code must be running) and reports its
    current output.

    INPUT
        output_directory (str) directory where all measurements from sensors are reported
        measurement_type_list (str[]) list of measurement types supported by this sensor
        sensor_status (lxml.etree) xml tag for that sensor to put all measurement values
    """

    for measurement_type in measurement_type_list:

        # Measurement file is simply concatenation of output_directory and measurement type
        output_file_name = '%s/%s.dat' % (output_directory, measurement_type)

        # Retrieves value from file if possible, otherwise, set value to None
        if os.path.isfile(output_file_name):

            try:

                measurement_file = open(output_file_name, 'r')
                measurement_value = measurement_file.read()
                measurement_file.close()

            except OSError:

                measurement_value = None

        else:

            measurement_value = None

        # If retrieving value was successfull, update the xml tag.
        if measurement_value is not None:

            sensor_status.set(measurement_type, measurement_value)

    #######
    return
    #######

########################
# END get_sensor_values
########################


####################################################################################################
# execute
####################################################################################################
# Revision History :
#    2017-05-23 Adba : Function created
#    2017-05-27 Adba : Fixed missing .sand_box and fixed empty return
####################################################################################################
def execute(worker_instance, instruction_as_xml, worker_base_response):
    """
    Processes sensor instruction

    INPUT
         worker_instance (Worker) worker instance
         instruction_as_xml (str, Useless) message to process
         worker_base_response (lxml.etree) base of worker response on which to build

    OUTPUT
         (lxml.etree) worker response, with info about sensors
    """

    # Useless
    del instruction_as_xml

    # Creates base response to be completed in instruction
    sensor_response = worker_base_response

    # Checks if the list of directories was already created earlier. If not, creates it
    if 'sensors' not in worker_instance.sand_box.keys():

        get_sensor_list(worker_instance)

    # Gets the relevant directories to go through
    all_sensor_directories = worker_instance.sand_box['sensors']

    # Goes through all sensors to get their measurement
    for sensor_name, sensor_info_dictionary in all_sensor_directories.iteritems():

        # Initialze lxml tag for current sensor
        sensor_status = etree.Element('sensor', type=sensor_info_dictionary['type'],
                                      name=sensor_name)

        # Gets list of measurements supported by this sensor
        measurement_list = sensor_info_dictionary['measurement_type']

        # Retrieves latest values for this sensor
        get_sensor_values(sensor_info_dictionary['output'], measurement_list, sensor_status)

        # Adds measurement for current sensor to the list
        sensor_response.append(sensor_status)

    general_utils.log_message('Finished creating sensor.')

    # Parsing was successfull
    sensor_response.set('status', '0')

    #######################
    return sensor_response
    #######################

##############
# END execute
##############
