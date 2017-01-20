
#########################
# Import global packages
#########################

# Signal parameters
signal_header = [3400, 1750]  # Header of signal, before any data bit (On, Off)

bit_separator = 450  # Length between each 0/1 data bit (On)
one_bit = 1300  # Length for 1-data bit (Off)
zero_bit = 420  # Length for 0-data bit (Off)

n_repeat = 1  # Number of time the signal will be repeated. If > 0, repeat must be non-empty
repeat = [440, 17100]  # (On, Off) separating signal repetition.


# Signal construction
base_signal = [
    '00100011',
    '11001011',
    '00100110',
    '00000001',
    '00000000',
    '00X00000',  # Controls On/Off
    '00XXX000',  # Controls Mode (Heat/Dry/Cold/Auto)
    '0000XXXX',  # Controls temperature
    'XXXX0YY0',  # X : Control fan direction,  Y : Controls Mode (Heat/Dry/Cold/Auto)
    'XXXXXXXX',  # Controls Fan Speed
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
# convert_bits_to_length
########################################################################################################################
# Revision History:
#   19/01/2016 AB - Created function
########################################################################################################################
def convert_bits_to_length(all_data_bytes):
    """
    Converts a constructed data signal (updated list of bytes from the base signal) into a list of length of On/Off for
    the IR emitter. The first length matches an On status.

    INPUT:
        all_data_bytes ({0,1}[8][]) list of string-formatted bytes containing the "info" to send the aircon.

    OUTPUT:
        all_lengths (int[]) list of length to apply for on/off state of the IR emitter.
    """

    all_lengths = []

    # Starts by merging all the bytes together to facilitate the loop through bits to come
    full_data_signal = ''.join(all_data_bytes)

    # Initializes the repeat index value and starts looping
    sent_index = 0
    while sent_index <= n_repeat:

        # For every repeat, the signal first starts with the header part
        all_lengths.extend(signal_header)

        # Then each data bit is converted into an (On, Off) sequence, where On has fixed length and Off variable
        #     depending on whether 0-bit or 1-bit.
        for data_bit in full_data_signal:

            # Fixed length separator (On)
            all_lengths.append(bit_separator)

            # Variable length depending on bit value
            if data_bit == '0':

                all_lengths.append(zero_bit)

            else:

                all_lengths.append(one_bit)

        # After the data bytes are all sent, the "repeat" information must be sent to signal the receiver the message
        #     will be repeated. If no repeat are necessary anymore, signal is complete.
        if sent_index < n_repeat:

            all_lengths.extend(repeat)

        sent_index += 1

    ###################
    return all_lengths
    ###################

#############################
# END convert_bits_to_length
#############################


########################################################################################################################
# convert_info_to_bits
########################################################################################################################
# Revision History:
#   19/01/2016 AB - Created function
########################################################################################################################
def convert_info_to_bits(is_turned_on, mode, temperature):
    """
    Converts the information to send the aircon from human-readable (turned on in heater mode at 26 degree) to the byte
    version to be interpreted by the aircon receiver.

    INPUT:
        is_turned_on {'on', 'off'} whether aircon is on or off
        mode {'heater', 'cold', 'dry', 'auto'} which mode the aircon is running in
        temperature {int} temperature target
    """

    # On/Off of aircon. Initializes it to '0' (Off) and pushes it to '1' depending on argument
    value = '0'
    if is_turned_on == 'on':

        value = '1'

    base_signal[5][2] = value

    # Mode of aircon. Initializes it at ['100', '00'], (Auto) and changes it to other value dependng on arguments
    value = ['100', '00']
    if mode == 'heat':

        value = ['001', '00']

    elif mode == 'dry':

        value = ['010', '01']

    elif mode == 'cold':

        value = ['011', '11']

    base_signal[6][2:5] = value[0]
    base_signal[8][5:7] = value[1]

    # Temperature of aircon. Initializes it at 22 '0110' and changes it to other value depending on argument
    value = '0110'
    if 15 < temperature < 32:

        value = bin(temperature - 16).zfill(4)

    base_signal[7][4:] = value

###########################
# END convert_info_to_bits
###########################
