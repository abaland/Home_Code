# Took inspiration from https://github.com/szazo/DHT11_Python to create this package

#########################
# Import global packages
#########################

from time import sleep  # Waits after sending signal for responses
from time import time as now
try:
    import RPi.GPIO as GPIO  # Controls and reads GPIO Pins
except ImportError:
    GPIO = None

########################
# Import local packages
########################

from global_libraries import general_utils

__author__ = 'Baland Adrien'

###########################
# Declare global variables
###########################
pin_gpio_id = -1  # Pin to which DHT11 Sensor is connected.

no_data_bit_error_spacing = 3600.  # Prevents spam log of errors if the "No 40 bits" error occurs.
no_data_bit_error_last_time = {}  # Each failing sensors should still have its log entry


####################################################################################################
# FUNCTION (is_valid_address)
####################################################################################################
# Revision History:
#   2016-11-04 AB - Function Created
####################################################################################################
def is_valid_address(sensor_address):
    """
    Tests whether provided address is a valid DHT11 address.

    INPUT:
        address (string) : address to test

    RETURNS:
        (boolean) whether the address is a valid DHT11 address,
        (int) DHT11 address to measure for sample collection.
    """

    # Initializes value
    valid_address = False  # Whether address is valid or not
    converted_address = -1  # Sensor address after conversion to appropriate format

    try:

        # Converts the string to its actual value. (GPIO pins, so it should be a normal integer)
        converted_address = int(sensor_address, 10)

        # Tests what GPIO pin number is in the valid range
        if 0 < converted_address < 27:

            # Everything checks out OK, address is valid
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

    all_measures = ['temperature', 'humidity']

    ####################
    return all_measures
    ####################

############################
# END get_measurement_types
############################


####################################################################################################
# Function(collect_pin_values)
####################################################################################################
def collect_pin_values():
    """
    Collect data from DHT11 sensor. Measures as often as possible state (LOW/HIGH) of pin to measure
    The following starting sequence (HIGH, LOW, HIGH) is ignored, as it precedes sensor data 
    response (announces that response will follow).
    Collections stop when measurements stay to HIGH for a long enough time.

    INPUT:

    RETURNS:
        (int[]) array of measurements (HIGH=1, LOW=0) for the given pin.
    """

    # Case-handler if the Rpi.GPIO could not be loaded
    if GPIO is None:

        ##########
        return []
        ##########

    n_same_value_break = 200  # number of successive time same data is seen until collection stops
    n_same_value_count = 0  # Number of successive times the same value was observed
    last_value = -1  # Last measured value
    all_values_collected = []  # All measures collected

    #######################################
    # Skips introduction signal (not data)
    #######################################

    # Wait for DHT to pull pin low => Skips all high
    try:
        while GPIO.input(pin_gpio_id) and n_same_value_count < n_same_value_break:
            n_same_value_count += 1

        # Wait for DHT to pull pin HIGH (next LOW will signal start of data bits) => Skips all low
        n_same_value_count = 0
        while not GPIO.input(pin_gpio_id) and n_same_value_count < n_same_value_break:
            n_same_value_count += 1

        # Wait for DHT to pull pin LOW (start of data bits) => Skips all HIGH
        n_same_value_count = 0
        while GPIO.input(pin_gpio_id) and n_same_value_count < n_same_value_break:
            n_same_value_count += 1

    except IOError:

        # Algorithm failed to read GPIO pin, so stop functions and prints error
        general_utils.log_error(-421, pin_gpio_id)
        ############################
        return all_values_collected
        ############################

    ####################
    # Starts collection
    ####################

    # While measurements are not stable (max_unchanged_count times the same value), reads value and
    # appends it
    n_same_value_count = 0
    while True:

        try:
            # Get current value and appends it
            current_value = GPIO.input(pin_gpio_id)
            all_values_collected.append(current_value)

        except IOError:

            # Algorithm failed to read GPIO pin, so stop functions and prints error
            general_utils.log_error(-421, pin_gpio_id)
            #################
            return all_values_collected
            #################

        # Checks if state changes or stayed the same
        if last_value != current_value:

            # Change occured => Reset counter
            n_same_value_count = 0
            last_value = current_value

        else:

            # Increment counters and tests if stabilized
            n_same_value_count += 1
            if n_same_value_count > n_same_value_break:

                break

    ############################
    return all_values_collected
    ############################

#########################
# END collect_pin_values
#########################


####################################################################################################
# Function(get_high_voltage_counts)
####################################################################################################
def get_high_voltage_counts(data):
    """
    Converts array of 1 and 0 into an array of how many successive times 1 appear, e.g. [1, 1, 0, 1,
        0, 1] => [2, 1, 1].
    Since only high-voltage are relevant for DHT11 (short-signal = 0-bit, long-signal = 1-bit, only 
    the number of times a 1 was measured in a row is relevant.

    INPUT
        data (int[]): array of 0 and 1 to aggregate

    RETURNS
        (int[]) array of consecutive times 1-values are observed
    """

    # Each data bit is a LOW____HIGH. Length of HIGH will vary for 1-bit or 0-bit
    all_high_voltage_counts = []  # List of all consecutive-1 counts
    current_high_voltage_count = 0  # Current counter of consecutive-1
    last_voltage_value = 0  # Latest measured voltage.
    for voltage_measure in data:

        # Measuring HIGH voltage => increment counter (nothing else to do)
        if voltage_measure == 1:

            current_high_voltage_count += 1

        # Moves from HIGH TO LOW, append current counter and start a new one.
        elif last_voltage_value == 1 and voltage_measure == 0:

            all_high_voltage_counts.append(current_high_voltage_count)
            current_high_voltage_count = 0

        # Otherwise (LOW to LOW), do nothing
        else:

            pass

        # Updates latest measured voltage
        last_voltage_value = voltage_measure

    ###############################
    return all_high_voltage_counts
    ###############################

##############################
# END get_high_voltage_counts
##############################


####################################################################################################
# Function(get_data_bits)
####################################################################################################
def get_data_bits(all_high_voltage_counts):
    """
    Converts sequence of consecutive-1 counts into array of corresponding data bit values (0 or 1).
    HIGH signal for a long time means 1-bit, for a short time means 0-bit. If each sample was 
    collected at equal interval, we consider HIGH-voltage with high count as 1, and low count as 0.

    INPUT:
        high_voltage_length (int[]) : HIGH voltage consecutive counts.

    RETURNS:
        (Boolean[]) corresponding data-bits emitted by DHT11.

    """

    # Start by finding smallest and highest count of HIGH.
    # Using average of both, we can link data to being 1-bit or 0-bit
    smallest_one_count = min(all_high_voltage_counts)
    highest_one_count = max(all_high_voltage_counts)

    # use the halfway to determine whether the period it is long or short
    splitting_threshold = (smallest_one_count + highest_one_count) / 2.

    all_data_bits = []
    # For each count, converts it as 0-bit or 1-bit depending on count value w.r.t. threshold
    for signal_length in all_high_voltage_counts:

        data_bit = False

        # Above threshold = 1-bit.
        if signal_length > splitting_threshold:

            data_bit = True

        # Append value
        all_data_bits.append(data_bit)

    #####################
    return all_data_bits
    #####################

#####################
# END get_data_bits
#####################


####################################################################################################
# Function(send_and_sleep)
####################################################################################################
def send_and_sleep(output, sleep_time):
    """
    Sets output value and waits for a given amount of time.

    INPUT:
        output (0|1) : value to set as output for the pin
        sleep_time (Float) : amount of seconds to wait

    RETURNS:
        (int) 0 if everything went well, negative number if an error occured.
    """

    try:

        # Sets output value
        GPIO.output(pin_gpio_id, output)

        # Waits for given amount of time
        sleep(sleep_time)

    except IOError:

        # Failed to execute, so return failure status
        general_utils.log_error(-422, pin_gpio_id)
        ##########
        return -1
        ##########

    # Everything went smoothly.
    #########
    return 0
    #########

#####################
# END send_and_sleep
#####################


####################################################################################################
# Function(convert_data_bits)
####################################################################################################
def convert_data_bits(all_data_bits):
    """
    Converts the sequence of 40 databits into 5 bytes (integer).

    INPUT:
        all_data_bits (Boolean[40]) : list of all data bits from DHT11 sensor

    RETURNS:
        (int[5]) : corresponding bytes.
    """

    all_bytes = []

    # Initializes the value for the byte at 0 = 00000000,
    one_byte = 0
    for i in range(len(all_data_bits)):

        # Shifts all bits in the currently constructed byte by 1 to the left.  00010100 => 00101000
        one_byte <<= 1

        # If current bit to process is one, update the left-most bit in the in-construction byte!
        if all_data_bits[i]:

            one_byte |= 1

        else:

            one_byte |= 0

        # If 8 bits processed, full byte was reconstructed, so save it, and start with a new byte
        if (i + 1) % 8 == 0:

            all_bytes.append(one_byte)
            one_byte = 0

    #################
    return all_bytes
    #################

##############################
# Function(convert_data_bits)
##############################


####################################################################################################
# Function(compute_checksum)
####################################################################################################
def compute_checksum(all_bytes):
    """
    Computes checksum of the four data bytes emitted by DHT11 sensor. This checksum is computed as
    the sum of all four bytes with a 0xFF mask.

    INPUT:
        all_bytes (int[5]) data bytes from DHT11 sensor

    RETURNS:
        (int) checksum for first four data bytes
    """

    checksum = all_bytes[0] + all_bytes[1] + all_bytes[2] + all_bytes[3] & 0xFF

    ################
    return checksum
    ################

#######################
# END compute_checksum
#######################


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
        address (None) address of DHT11 sensor (GPIO pin)
        temperature_correction (float) correction to apply to measurement value, to account for 
            external effects.


    RETURNS:
        (Dict) dictionnary as {'temperature': value}
    """

    global pin_gpio_id
    global no_data_bit_error_last_time

    max_number_retry = 5  # Times script will try to get data from sensor in case of failure

    all_values = {
        'temperature': None,
        'humidity': None
    }

    # Case-handler if the Rpi.GPIO could not be loaded
    if GPIO is None:

        ##################
        return all_values
        ##################

    # Sets the pin to use internally.
    pin_gpio_id = address

    # Sets appropriate mode for GPIO pins
    GPIO.setmode(GPIO.BCM)

    index_retry = 1  # Current trial for sensor info.
    while True:

        # Sets pins for output (to send start signal)
        GPIO.setup(address, GPIO.OUT)

        # Set pin high for 500ms (makes sure everything is freed)
        send_and_sleep(GPIO.HIGH, 0.5)

        # MCU sends start signal and pull down voltage for at least 18milliseconds (initial phase)
        send_and_sleep(GPIO.LOW, 0.020)

        # Change to input using pull up (prepares for response from sensor)
        GPIO.setup(address, GPIO.IN, GPIO.PUD_UP)

        # Collect data into an array
        all_voltage_measurements = collect_pin_values()

        # parse lengths of all data pull up periods
        high_voltage_counts = get_high_voltage_counts(all_voltage_measurements)

        # Tests if exactly 40-bits of data parsed (otherwise, no point in trying to convert them)
        if len(high_voltage_counts) == 40:

            # Get all 40 data bits value (0 or 1)
            all_data_bits = get_data_bits(high_voltage_counts)

            # Aggregate all 40 parsed data bits into 5 data bytes.
            all_data_bytes = convert_data_bits(all_data_bits)

            # Tests whether the checksum in data matches self-calculated checksum.
            if all_data_bytes[4] == compute_checksum(all_data_bytes):

                # Checksum success. Temperature and Humidity computed.
                # DHT11 Does not handle decimal parts, so only first and third bytes are relevant.
                all_values['temperature'] = all_data_bytes[2] + temperature_correction
                all_values['humidity'] = all_data_bytes[0]

                # Success. Can leave the loop
                break

            else:

                # Log errors if checksum test failed (only log error after n failures)
                if index_retry == max_number_retry:

                    general_utils.log_error(-409, 'Checksum did not match in DHT.')
                    break

        else:

            # Log errors if failed to get 40 data bits from sensor (only log error after n failures)
            if index_retry == max_number_retry:

                # Initializes the last time an error has been logged for that particular address
                if pin_gpio_id not in no_data_bit_error_last_time.keys():

                    no_data_bit_error_last_time[pin_gpio_id] = 0

                # Checks if error should be logged
                if now() > no_data_bit_error_last_time[pin_gpio_id] + no_data_bit_error_spacing:

                    error_details = 'Address %d.' % (pin_gpio_id,)
                    general_utils.log_error(-409, 'Not 40 data bits for DHT11', error_details)
                    no_data_bit_error_last_time = now()
                    break

        # Failed to get measures in current trial, increment counter and try again
        index_retry += 1

    ##################
    return all_values
    ##################

#######################
# END get_measurements
#######################
