"""
This driver takes cares of storing information about and sending infrared signals to control my tv remote.

First, a dictionnary of the different commands is available, which linked to the data bits to send.
Then, when a button must be simulated, these databits are converted to IR lengths to send, expanded on with headers and
trailing signals, and finally sent.

== Signals ==
A signal is started by a Header (High, Low) of (3400, 1700)
Follows the data bits where each 1 is a (High, Low) of (430, 1250) and each 0 is a (High, Low) of (430, 410)
Finally, the signal concludes with a Trail (High, Low) of (440, 17100)
"""

########################
# Import local packages
########################
from python.global_libraries import signal_sender

####################
# Global parameters
####################

__author__ = 'Baland Adrien'

# Signal parameters
header_signal = [3400, 1700]  # Header of signal, before any data bit (On, Off)

one_bit = [430, 1250]  # Length for 1-data bit (On, Off)
zero_bit = [430, 410]  # Length for 0-data bit (On, Off)

n_repeat = 0  # Number of time the signal will be repeated. If > 0, repeat must be non-empty
repeat_signal = []  # (On, Off) separating signal repetition.
trail_signal = [440, 17100]  # (On, Off) to notify the end of the signal

all_codes = {
    '1': '010101010101101011110001010010000111001001001100',
    '2': '010101010101101011110001010010001111001001000100',
    '3': '010101010101101011110001010010000000101001000011',
    '4': '010101010101101011110001010010001000101001001011',
    '5': '010101010101101011110001010010000100101001000111',
    '6': '010101010101101011110001010010001100101001001111',
    '7': '010101010101101011110001010010000010101001000001',
    '8': '010101010101101011110001010010001010101001001001',
    '9': '010101010101101011110001010010000110101001000101',
    'Power': '010101010101101011110001010010000110100010001011',
    'Vol+': '010101010101101011110001010010000010100010001111',
    'Vol-': '010101010101101011110001010010001010100010000111',
    'Ch+': '010101010101101011110001010010001000100010000101',
    'Ch-': '010101010101101011110001010010000100100010001001',
    'Down': '010101010101101011110001010010000000010010000001',
    'Ok': '010100110101101011110001010010000100101010001011',
    'Right': '010101010101101011110001010010000001101110001111',
    'Left': '010101010101101011110001010010001110101110000000',
    'Up': '010101010101101011110001010010001110101010000001',
    'Back': '010101010101101011110001010010000010011110000000',
    'Menu': '010101010101101011110001010010000010001110000100',
    'Mute': '010101010101101011110001010010001110100010000011',
    'Subtitle': '010101010101101011110001010010001110011001000001'
}


########################################################################################################################
# send_signal
########################################################################################################################
# Revision History:
#   2017-01-27 AB - Created function
########################################################################################################################
def send_signal(remote_button):
    """
    Sends infrared signal to air conditioning system with given options.

    INPUT:
        remote_button (str)
    """

    data_bytes = all_codes.get(remote_button, None)

    # Uses remote specific data and data_bytes information to get all sub-signals to create, and order in which to send
    #   them to get the full signal to send.
    all_wave_lengths, wave_order = signal_sender.convert_bits_to_length(data_bytes, one_bit, zero_bit, header_signal,
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
