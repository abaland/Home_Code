"""
This driver takes cares of storing information about and sending infrared signals to control my 
living room lights

First, a dictionnary of the different commands is available, which linked to the data bits to send.
Then, when a button must be simulated, these databits are converted to IR lengths to send, expanded 
on with headers and trailing signals, and finally sent.

== Signals ==
Starts with data bits where each 1 is (High, Low) of (1300, 400) and each 0 is (High, Low) of 
    (400, 1300). **1
Follows the repetition signal  (High, Low) of (450, 22700)
Follows the same data bits as before
Finally, the signal concludes with a Trail (High, Low) of (450, 22700)

**1 : data-bit 1 and 0 could be reversed,
"""

########################
# Import local packages
########################
from python.global_libraries import signal_sender
from python.global_libraries import general_utils

####################
# Global parameters
####################

__author__ = 'Baland Adrien'

# Signal parameters
header_signal = []  # Header of signal, before any data bit (On, Off)

one_bit = [1300, 380]  # Length for 1-data bit (On, Off)
zero_bit = [450, 1220]  # Length for 0-data bit (Off)

n_repeat = 3  # Number of time the signal will be repeated. If > 0, repeat must be non-empty
repeat_signal = [460, 22700]  # (On, Off) separating signal repetition.
trail_signal = [460, 22700]  # (On, Off) to notify the end of the signal

all_codes = {
    'Power':   '11010000010',
    'Bright+': '11010000100',
    'Bright-': '11010010000',
    'Yellow':  '11010010100',
    'White':   '11010011000',
    'Minimum': '11010001100',
    'Maximum': '11010001000',
    'A':       '11010011100',
    'B':       '11010010010',
    'Mute':    '11010010001'
}


####################################################################################################
# send_signal
####################################################################################################
# Revision History:
#   2017-01-27 AB - Created function
####################################################################################################
def send_signal(remote_button):
    """
    Sends infrared signal to air conditioning system with given options.

    INPUT:
        remote_button (str)
    """

    data_bytes = all_codes.get(remote_button, None)

    if data_bytes is None:

        details = '%s' % (remote_button,)
        ############################################################
        return general_utils.log_error(-505, error_details=details)
        ############################################################

    # Uses remote specific data and data_bytes information to get all sub-signals to create, and
    # order in which to send them to get the full signal to send.
    all_wave_lengths, wave_order = \
        signal_sender.convert_bits_to_length(data_bytes, one_bit, zero_bit, header_signal,
                                             repeat_signal, trail_signal, n_repeat)

    # Creates pigpio interface to send infrared signal
    ir = signal_sender.PigpioInterface(21, 38000, 0.5)

    send_status = ir.send_code(all_wave_lengths, wave_order)

    ###################
    return send_status
    ###################

##################
# END send_signal
##################
