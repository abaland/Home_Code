"""
Strongly based on https://github.com/bschwind/ir-slinger/blob/master/pyslinger.py

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
    # send_zero
    ####################################################################################################################
    # Revision History :
    #   2017-01-22 AdBa : Function created
    ####################################################################################################################
    def send_zero(self, duration):
        """
        Adds "LOW" segment for a given duration to the full signal.

        INPUT:
            duration (int) duration (micro-seconds) of the LOW state.
        """

        self.add_pulse(0, 1 << self.gpio_pin, duration)

        #######
        return
        #######

    ################
    # END send_zero
    ################

    #
    #
    #

    ####################################################################################################################
    # send_one
    ####################################################################################################################
    # Revision History :
    #   2017-01-22 AdBa : Function created
    ####################################################################################################################
    def send_one(self, duration):
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
    # END send_one
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

                self.send_one(ir_length)

            else:

                self.send_zero(ir_length)

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


####################################################################################################################
# SignalSendManager
####################################################################################################################
# Revision History :
#   2017-01-22 AdBa : Class created
####################################################################################################################
class SignalSendManager:
    """
    This class handles most interactions with the pigpio module, like initialization connexion to module,
    clearance of previous pigpio data, parametrization and start of signal to send, ...
    """

    ####################################################################################################################
    # __init__
    ####################################################################################################################
    # Revision History :
    #   2017-01-22 AdBa : Function created
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

    ###############
    # END __init__
    ###############

    #
    #
    #

    ####################################################################################################################
    # send_code
    ####################################################################################################################
    # Revision History :
    #   2017-01-22 AdBa : Function created
    ####################################################################################################################
    def send_code(self, ir_all_lengths):
        """
        Takes care of all interaction with pigpio library and sends infrared signal.

        INPUT:
            ir_all_lengths (int[]) duration (microseconds) of the sequential High/Low states, starting with the length
                of a "High" state.

        OUTPUT:
            (int) 0 if successfull, negative number otherwise
        """

        # Makes sure all previous signal data is cleared from pigpio.
        clear = self.pigpio.wave_clear()
        if clear != 0:

            print("Error in clearing wave!")

            #########
            return 1
            #########

        # Configuration the signal parameters based on the input argument
        all_pulses = self.pulse_converter.process_code(ir_all_lengths)
        wave_config_status = self.pigpio.wave_add_generic(all_pulses)
        if wave_config_status < 0:

            print("Error in adding wave!")

            ##########################
            return wave_config_status
            ##########################

        # Creates signal wave based on parameters sent.
        wave_id = self.pigpio.wave_create()

        # Sends wave
        if wave_id >= 0:

            print("Sending wave...")
            wave_send_status = self.pigpio.wave_send_once(wave_id)

            if wave_send_status >= 0:

                print("Success! (result: %d)" % wave_send_status)

            else:

                print("Error! (result: %d)" % wave_send_status)

                ########################
                return wave_send_status
                ########################

        else:

            print("Error creating wave: %d" % wave_id)

            ###############
            return wave_id
            ###############

        # Pauses until the signal is sent.
        while self.pigpio.wave_tx_busy():

            sleep(0.1)

        # After signal has been sent, removes the wave from pigpio.
        print("Deleting wave")
        self.pigpio.wave_delete(wave_id)

        # Closes connexion with daemon.
        print("Terminating pigpio")
        self.pigpio.stop()

########################
# END SignalSendManager
########################
