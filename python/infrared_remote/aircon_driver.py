"""
This driver help converting the desired settng for the air conditioning ystem in my house to the appropriate signal
length to send through infrared, and takes care of sending these signals.

After examination of the receiver signals (with convert_aircon_ir.py code) on many tests configuration. The following
conclusions were taken.

== Signals ==
A signal is started by a Header (High, Low) of (3400, 1750)
Follows the data bits where each 1 is a (High, Low) of (450, 1300) and each 0 is a (High, Low) of (450, 420)
Follows the repetition signal  (High, Low) of (440, 17100)
Follows the same data bits as before
Finally, the signal concludes with a Trail (High, Low) of (440, 17100)

== Configuration ==
Off, On     : 6-th byte,  6th bit     : 0=Off,    1=On
Temperature : 8-th byte,  1st-4th bit : 0000=16,  1000=17,  0100=18,  0010=20,  0001=24,  1111=31
Wind speed  : 10-th byte, 1st-2nd bit : 00=auto,  10=low,  01=middle,  11=high
Wind direct : 10-th byte, 4th-6th bit : 000=auto, 100=lowest,  010=low,  110=center,  001=high,  101=highest,  111=loop
Sound       : 10-th byte, 7th-8th bit : 10=1beep,  01 = 2 beeps.  (THIS ONE IS NOT SURE). MAYBE 0 STOPS SOUNDS
Mode        :
    (1) 7-th byte, 4th-5th bit : 10=heater, 11=cooler, 01=dryer
    (2) 9th byte, 2th-3rd bit : 00=heater, 11=cooler, 10=dryer
Checksum    : last byte, all bits.
    Read all but last bytes as (1,2,4,8,16,32,64,128) (convert to integer)
    Sum these integer
    Convert this sum to 8-bit using (1,2,4,8,16,32,64,128)
"""

#########################
# Import global packages
#########################
import copy

########################
# Import local Packages
########################
from python.global_libraries import signal_sender

####################
# Global parameters
####################

__author__ = 'Baland Adrien'

# Signal parameters
header_signal = [3400, 1750]  # Header of signal, before any data bit (On, Off)

one_bit = [450, 1300]  # Length for 1-data bit (On, Off)
zero_bit = [450, 420]  # Length for 0-data bit (On, Off)

n_repeat = 1  # Number of time the signal will be repeated. If > 0, repeat must be non-empty
repeat_signal = [440, 17100]  # (On, Off) separating signal repetition.
trail_signal = [440, 17100]  # (On, Off) to notify the end of the signal


# Signal construction
base_signal = [
    '11000100',
    '11010011',
    '01100100',
    '10000000',
    '00000000',
    '00000X00',  # On/Off
    '000XX000',  # Mode (Heat/Dry/Cold)
    'XXXX0000',  # Temperature
    '0XX01100',  # Mode (Heat/Dry/Cold)
    'XX0YYY10',  # X: Fan speed, Y: Fan direction
    '00000000',
    '00000000',
    '00000000',
    '00000000',
    '00000000',
    '00000000',
    '00000000',
    'XXXXXXXX',  # Checksum
]


########################################################################################################################
# compute_checksum
########################################################################################################################
# Revision History:
#   19/01/2016 AB - Created function
########################################################################################################################
def compute_checksum(all_data_bytes):
    """
    Computes the final byte to send, which contains the checksum of all data bytes.

    INPUT:
        all_data_bytes ({'0', '1'}[8][]) all data bytes send before, to use for checksum

    RETURN:
        ({'0', '1'}[8] checksum of the sent data bytes
    """

    # Sum all data bytes as integer
    all_bytes_sum = 0
    for data_byte in all_data_bytes:

        # Reverse the byte to fit the standard binary format. Bytes to send are written as (1, 2, 4, 8, ...)
        reverse_byte = data_byte[::-1]

        all_bytes_sum += int(reverse_byte, 2)

    # Only keep the 8 lowest signicant bits to make the checksum byte.
    all_bytes_sum %= 256

    # Converts the resulting integer to binary, and reverts the string, to fit the format (1, 2, 4, 8, ...)
    checksum = bin(all_bytes_sum)[2:].zfill(8)

    ######################
    return checksum[::-1]
    ######################

#######################
# END compute_checksum
#######################


########################################################################################################################
# convert_info_to_bits
########################################################################################################################
# Revision History:
#   19/01/2016 AB - Created function
########################################################################################################################
def convert_info_to_bits(is_turned_on, mode, temperature, wind_speed, wind_direction):
    """
    Converts the information to send the aircon from human-readable (turned on in heater mode at 26 degree) to the byte
    version to be interpreted by the aircon receiver.

    INPUT:
        is_turned_on {'on', 'off'} whether aircon is on or off
        mode {'heater', 'cold', 'dry', 'auto'} which mode the aircon is running in
        temperature {int} temperature target
        wind_speed {'auto', 'low', 'middle', 'high'}
        wind_direction {'auto', 'lowest', 'low', 'middle', 'high', 'highest', 'loop'}

    OUTPUT:
        ({'0','1'}[8][]) all data bytes matching the desired settings
    """

    # Initializes the bytes to send as the base signal.
    final_bytes = copy.deepcopy(base_signal)

    # Updates values related to on/off state.
    value = '0'
    if is_turned_on == 'on':

        value = '1'

    final_bytes[5] = final_bytes[5][:5] + value + final_bytes[5][6:]

    # Updates values related to aircon mode (heat, cold, dry).
    value = ['11', '11']
    if mode == 'heat':

        value = ['10', '00']

    elif mode == 'dry':

        value = ['01', '10']

    final_bytes[6] = final_bytes[6][:3] + value[0] + final_bytes[6][5:]
    final_bytes[8] = final_bytes[8][:1] + value[1] + final_bytes[8][3:]

    # Updates values related to aircon temperature (between 16 and 31 degrees).
    value = '0110'
    if 15 < temperature < 32:

        value = bin(temperature - 16)[2:].zfill(4)

    final_bytes[7] = value + final_bytes[7][4:]

    # Updates value related to wind speed.
    value = '00'
    if wind_speed == 'low':

        value = '10'

    elif wind_speed == 'middle':

        value = '01'

    elif wind_speed == 'high':

        value = '11'

    final_bytes[9] = value + final_bytes[9][2:]

    # Updates value related to wind direction.
    value = '000'
    if wind_direction == 'lowest':

        value = '100'

    elif wind_direction == 'low':

        value = '010'

    elif wind_direction == 'middle':

        value = '110'

    elif wind_direction == 'high':

        value = '001'

    elif wind_direction == 'highest':

        value = '011'

    elif wind_direction == 'loop':

        value = '111'

    final_bytes[9] = final_bytes[9][:3] + value + final_bytes[9][6:]

    final_bytes[17] = compute_checksum(final_bytes[:17])

    ###################
    return final_bytes
    ###################

###########################
# END convert_info_to_bits
###########################


########################################################################################################################
# send_signal
########################################################################################################################
# Revision History:
#   19/01/2016 AB - Created function
########################################################################################################################
def send_signal(is_turned_on, mode, temperature, wind_speed, wind_direction):
    """
    Sends infrared signal to air conditioning system with given options.

    INPUT:
        is_turned_on {'on', 'off'} whether aircon is on or off
        mode {'heater', 'cold', 'dry', 'auto'} which mode the aircon is running in
        temperature {int} temperature target
        wind_speed {'auto', 'low', 'middle', 'high'}
        wind_direction {'auto', 'lowest', 'low', 'middle', 'high', 'highest', 'loop'}
    """

    # Converts all options desired to the data bytes to send, in byte (8 bit-string) array form
    data_bytes = convert_info_to_bits(is_turned_on, mode, temperature, wind_speed, wind_direction)

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

send_signal('on', 'heat', 25, 'auto', 'auto')
