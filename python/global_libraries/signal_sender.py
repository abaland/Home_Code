"""
Based on https://github.com/bschwind/ir-slinger/blob/master/pyslinger.py

This code handles sending messages using infrared signals with pigpio library.

To understand this code, it is important to understand how signals are transmitted.
At this level in the code, signals have been reduced to their almost-basic level, i.e. to a sequence of durations for
"High" and "Low" signals.
However, one lower level exists. To avoid LED consuming too much power, the IR emitter uses a specific frequency and
duty cycle, which is only relevant for "On" state.
When the signal to send is "High" for X milliseconds, the LED will stay Off for X milliseconds, so there is no problem.
When the signal to send is "Low" for X milliseconds, the LED will alternate between On and Off.
   First the X milliseconds duration is split in periods of T milliseconds = 1 / frequency.
   For each of those T milliseconds, the LED will be On for the first T * duty_cycle ms, then Off for the rest.
Due to this, High/Low refers to the LED state ignoring the frequency/duty_cycle, and On/Off, to the actual LED state.
"""

#########################
# Import global packages
#########################
from time import sleep
import pigpio

import general_utils

# RAW IR ones and zeroes. Specify length for one and zero and simply bitbang the GPIO.
# The default values are valid for one tested remote which didn't fit in NEC or RC-5 specifications.
# It can also be used in case you don't want to bother with deciphering raw bytes from IR receiver:
# i.e. instead of trying to figure out the protocol, simply define bit lengths and send them all here.


####################################################################################################################
# PulseConverter
####################################################################################################################
# Revision History :
#   2017-01-22 AdBa : Class created
####################################################################################################################
class PulseConverter:
    """
    This class handles the conversion from a sequence of infrared lengths (matching the time the signal is considering
    UP or down) to a sequence of pulse, which will match exactly when the infrared LED will be ON or OFF based on the
    frequency and duty cycle of the signal.
    """

    ####################################################################################################################
    # __init__
    ####################################################################################################################
    # Revision History :
    #   2017-01-22 AdBa : Function created
    ####################################################################################################################
    def __init__(self, gpio_pin, frequency=36000, duty_cycle=0.33):
        """
        Initialization function. Assigns the signal specific information (frequency and duty_cycle), along with the GPIO
        pin to use for sending message. Finally, initializes the array of pulses that will be sent to the pigpio library

        INPUT:
            gpio_pin (int) gpio pin where IR emitter is connected to
            frequency (int) frequency (Hz) of the pulses to send
            duty_cycle (double) percentage of a "HIGH" period where the IR emitter will actually be on.
        """

        # Assigns main parameters internally
        self.gpio_pin = gpio_pin
        self.frequency = frequency
        self.duty_cycle = duty_cycle

        # Initializes array of pulses to send
        self.pulses = []

    ###############
    # END __init__
    ###############

    #
    #
    #

    ####################################################################################################################
    # add_pulse
    ####################################################################################################################
    # Revision History :
    #   2017-01-22 AdBa : Function created
    ####################################################################################################################
    def add_pulse(self, gpio_on, gpio_off, length_microsec):
        """
        Append a pulse (On or Off state) to the pulse array.

        INPUT:
            gpio_on (int) : binary -> integer representation of the pins to turn on
                If pin must not be turned On, 0.
                For example, to use pin 3, gpio_on = 1000 (binary) ==> 8 (decimal).
                To use pin 5, gpio_on = 100000 (binary) ==> 32 (decimal).
            gpio_off (int) : binary -> integer representation of the pins to turn off
                If pin must not be turned Off, 0.
            delay_microsec (int) duration (micro-seconds) of the pulse.
        """

        # Creates pulse with given parameters, and append it
        new_pulse = pigpio.pulse(gpio_on, gpio_off, length_microsec)
        self.pulses.append(new_pulse)

        #######
        return
        #######

    ################
    # END add_pulse
    ################

    #
    #
    #

    ####################################################################################################################
    # send_low
    ####################################################################################################################
    # Revision History :
    #   2017-01-22 AdBa : Function created
    ####################################################################################################################
    def send_low(self, duration):
        """
        Adds "LOW" segment for a given duration to the full signal.

        INPUT:
            duration (int) duration (micro-seconds) of the LOW state.
        """

        self.add_pulse(0, 1 << self.gpio_pin, duration)

        #######
        return
        #######

    ###############
    # END send_low
    ###############

    #
    #
    #

    ####################################################################################################################
    # send_high
    ####################################################################################################################
    # Revision History :
    #   2017-01-22 AdBa : Function created
    ####################################################################################################################
    def send_high(self, duration):
        """
        Adds "HIGH" segment for a given duration to the full signal.

        INPUT:
            duration (int) duration (micro-seconds) of the HIGH state.
        """

        # Computes duration of one period in micro-seconds (On + Off sequence)
        period_time = 1000000.0 / self.frequency

        # Computes duration of On/Off subparts in each of those periods
        on_duration = int(round(period_time * self.duty_cycle))
        off_duration = int(round(period_time * (1.0 - self.duty_cycle)))

        # Computes the total number of periods required to reach the desired duration
        total_periods = int(round(duration/period_time))

        # For each period, generates two pulses, one On, one Off with the previously computed duration.
        total_pulses = total_periods * 2
        for i in range(total_pulses):

            if i % 2 == 0:

                # On subsignal.
                self.add_pulse(1 << self.gpio_pin, 0, on_duration)

            else:

                # Off subsignal.
                self.add_pulse(0, 1 << self.gpio_pin, off_duration)

        #######
        return
        #######

    ###############
    # END send_high
    ###############

    #
    #
    #

    ####################################################################################################################
    # process_code
    ####################################################################################################################
    # Revision History :
    #   2017-01-22 AdBa : Function created
    ####################################################################################################################
    def process_code(self, ir_all_lengths):
        """
        Converts a sequence of "High/Low" state durations to a sequence of "On", "Off" pulses duration.

        INPUT:
            ir_all_lengths (int[]) duration (microseconds) of the sequential High/Low states, starting with the length
                of a "High" state.

        OUTPUT:
            (pigpio.pulse[]) pulse sequences translation of input durations.
        """

        # Initializes array of pulses to send
        self.pulses = []

        # The first signal to send is always a 1.
        signal_type = True
        for ir_length in ir_all_lengths:

            if signal_type:

                self.send_high(ir_length)

            else:

                self.send_low(ir_length)

            # Next signal will be the opposite of the current one (High -> Low or Low -> High)
            signal_type = not signal_type

        ###################
        return self.pulses
        ###################

        ###################
        # END process_code
        ###################

#####################
# END PulseConverter
#####################


#
#
#


####################################################################################################################
# PigpioInterface
####################################################################################################################
# Revision History :
#   2017-01-22 AdBa : Class created
####################################################################################################################
class PigpioInterface:
    """
    This class handles most interactions with the pigpio module, like initialization connexion to module,
    clearance of previous pigpio data, parametrization and start of signal to send, ...
    """

    ####################################################################################################################
    # __init__
    ####################################################################################################################
    # Revision History :
    #   2017-01-22 AdBa : Function created
    #   2017-01-27 AdBa : Added internal parameter all_wave_ids
    ####################################################################################################################
    def __init__(self, gpio_pin, frequency, duty_cycle):
        """
        Initialization function. Assigns the signal specific information (frequency and duty_cycle), along with the GPIO
        pin to use for sending message. Initializes connexion with pigpio daemon.

        INPUT:
            gpio_pin (int) gpio pin where IR emitter is connected to
            frequency (int) frequency (Hz) of the pulses to send
            duty_cycle (double) percentage of a "HIGH" period where the IR emitter will actually be on.
        """

        # Initializes connexion to pigpio module.
        self.pigpio = pigpio.pi()

        # Sets pin mode to output.
        self.pigpio.set_mode(gpio_pin, pigpio.OUTPUT)

        # Initializes High/Low durations to On/Off durations converted.
        self.pulse_converter = PulseConverter(gpio_pin, frequency, duty_cycle)

        # List of created wave ids
        self.all_wave_ids = []

    ###############
    # END __init__
    ###############

    #
    #
    #

    ####################################################################################################################
    # make_wave
    ####################################################################################################################
    # Revision History :
    #   2017-01-25 AdBa : Function created
    #   2017-01-27 AdBa : Added better return if failure
    ####################################################################################################################
    def make_wave(self, ir_all_lengths):
        """
        Creates a signal wave based on a sequence of ir lengths in pigpio library and returns its ids
        after creation for future references.

        INPUT:
            ir_all_lengths (int[]) series of 'HIGH' 'LOW' lengths (microseconds) that compose the wave

        OUTPUT:
            (int) id of the created wave is >= 0, error code otherwise.
        """

        # Decomposes the ir lengths into a sequence of pulses of ON, OFF status for the LED.
        all_pulses = self.pulse_converter.process_code(ir_all_lengths)

        # Assigns pulses to a new wave to create
        wave_config_status = self.pigpio.wave_add_generic(all_pulses)

        # If assignment failed, reports error and return
        if wave_config_status < 0:

            #######################################################################
            return general_utils.log_error(-503, error_details=wave_config_status)
            #######################################################################

        # Validates created wave and gets its corresponding id
        try:

            wave_id = self.pigpio.wave_create()

        except pigpio.error as e:

            ##########################################################################################
            return general_utils.log_error(-507, error_details='wave_create', python_error_message=e)
            ##########################################################################################

        # Updates internal parameters
        self.all_wave_ids.append(wave_id)

        ###############
        return wave_id
        ###############

    ################
    # END make_wave
    ################

    #
    #
    #

    ####################################################################################################################
    # send_code
    ####################################################################################################################
    # Revision History :
    #   2017-01-22 AdBa : Function created
    #   2017-01-25 AdBa : Modified whole function.
    #   2017-01-27 AdBa : Reviewed function structure
    ####################################################################################################################
    def send_code(self, all_wave_lengths, wave_order):
        """
        Sends an infrared signal using previously created wave, blocks until signal is sent, deletes all waves used in
        pigpio and stops connection to pigpio library.

        INPUT:
            all_wave_ids (int[]) list of wave ids to call sequentially, in order (repetition allowed)

        OUTPUT:
            (int) 0 if successfull, negative number otherwise
        """

        # Resets parameter (internal and pigpio-related)
        self.all_wave_ids = []
        self.pigpio = pigpio.pi()
        self.pigpio.wave_clear()

        # Creates all waves matching subsignals to send in pigpio
        for one_wave_length in all_wave_lengths:

            # Creates wave in pigpio and retrieves its corresponding id
            creation_status = self.make_wave(one_wave_length)

            # If result is negative, an error occured (ids are >= 0), so stop execution and reports error.
            if creation_status < 0:

                #######################
                return creation_status
                #######################

        # Uses wave sending order to get wave id sending sequence
        wave_id_order = [self.all_wave_ids[wave_index] for wave_index in wave_order]

        # Sends the signal using created wave ids in order.
        self.pigpio.wave_chain(wave_id_order)

        # Pauses until the signal is sent.
        while self.pigpio.wave_tx_busy():

            sleep(0.0000001)

        # After signal has been sent, removes all waves created to send signal. (set function makes ids unique)
        for wave_id in set(self.all_wave_ids):

            general_utils.log_message("Deleting wave")
            self.pigpio.wave_delete(wave_id)

            try:

                # Remove wave id internally
                self.all_wave_ids.remove(wave_id)

            except ValueError:

                # Could not remove wave id because it was already not there, so nothing to do. This should not happen.
                pass

        # Closes connexion with daemon.
        general_utils.log_message("Terminating pigpio")
        self.pigpio.stop()

        #########
        return 0
        #########

    ################
    # END send_code
    ################

    #
    #
    #

######################
# END PigpioInterface
######################


########################################################################################################################
# convert_bits_to_length
########################################################################################################################
# Revision History:
#   19/01/2016 AB - Created function
#   26/01/2016 AB - Added trailing signal.
########################################################################################################################
def convert_bits_to_length(all_data_bytes, one_bit, zero_bit, header_signal, repeat_signal, trail_signal, n_repeat):
    """
    Converts a constructed data signal (list of bytes from the base signal formatted as binary string) into a list of
    lengths of High/Low states for the IR emitter. The first length matches an On status.

    INPUT:
        all_data_bytes ({'0','1'}[]) list of all data bits, string-formatted, to send the aircon
        one_bit (int[]) length in microseconds of ('High', 'Low') sequence corresponding to a 1-data-bit
        zero_bit (int[]) length in microseconds of ('High', 'Low') sequence corresponding to a 0-data-bit
        header_signal (int[]) length in microseconds of ('High', 'Low') sequence preceding the databits
        repeat_signal (int[]) length in microseconds of ('High', 'Low') sequence between two databits
        trail_signal (int[]) length in microseconds of ('High', 'Low') sequence to conclude the signal

    OUTPUT:
        (int[][]) list of length to apply for High/Low state of the IR emitter for each of the subparts of the signal.
        (int[]) order in which the here-above subparts should be sent to get the full signal
    """

    # Starts by merging all the bytes together to facilitate the loop through bits to come
    if not isinstance(all_data_bytes, basestring):

        details = 'all_data_bytes is not a string : %s' % (all_data_bytes,)
        ##################################################################
        return None, general_utils.log_error(-506, error_details=details)
        ##################################################################

    full_data_signal = ''.join(all_data_bytes)

    data_signal_as_length = []
    # Then each data bit is converted into an (On, Off) sequence.
    for data_bit in full_data_signal:

        if data_bit == '0':

            data_signal_as_length.extend(zero_bit)

        else:

            data_signal_as_length.extend(one_bit)

    # Creates all possible subsignals that can be sent through the full signal to transmit.
    all_signal_types = []
    if len(header_signal) > 0:

        all_signal_types.append(header_signal)

    all_signal_types.append(data_signal_as_length)

    if len(repeat_signal) > 0:

        all_signal_types.append(repeat_signal)

    if len(trail_signal) > 0:

        all_signal_types.append(trail_signal)

    # Initializes the repeat index value and starts looping
    sent_index = 0
    signal_types_order = []
    while sent_index <= n_repeat:

        # For every repeat, the signal first starts with the header part
        if len(header_signal) > 0:

            signal_types_order.append(all_signal_types.index(header_signal))

        signal_types_order.append(all_signal_types.index(data_signal_as_length))

        # After the data bytes are all sent, the "repeat" information must be sent to signal the receiver the message
        #     will be repeated. If no repeat are necessary anymore, signal is complete.
        if sent_index < n_repeat and len(repeat_signal) > 0:

            signal_types_order.append(all_signal_types.index(repeat_signal))

        sent_index += 1

    # Adds trailing signal after everything else is sent
    if len(trail_signal) > 0:

        signal_types_order.append(all_signal_types.index(trail_signal))

    ############################################
    return all_signal_types, signal_types_order
    ############################################

#############################
# END convert_bits_to_length
#############################
