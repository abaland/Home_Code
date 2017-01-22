"""
This code converts raw infrared lengths from mode2 instruction (linux LIRC package) into a set of binary elements, that
decrypt a command send by a aircon remote control.

This is reverse-engineering of the signal using an adaptation of
http://www.instructables.com/id/Reverse-engineering-of-an-Air-Conditioning-control/

An example of file generated by lirc is found in data/heater_auto_auto_25_on_off.txt. Since this is reverse engineering
of output data with a different IR sensor, noise is to be expected in the data, so that text file contains transitions
(OFF->ON, ON->OFF) repeated 5 times. This gives 20 lines of output (each instruction produces twice the same command in
theory. By grouping all 10 lines of OFF->ON, we can identify which one is actually "correct".

Example of output after post-processing (selection of correct one)
(Heater, Auto, Auto, 25) : On
11000100 11010011 01100100 10000000 00000000 00000100 00010000 10010000 00001100 00000010 00000000 00000000 00000000
00000000 00000000 00000000 00000000 01101101
(Heater, Auto, Auto, 25) : Off
11000100 11010011 01100100 10000000 00000000 00000000 00010000 10010000 00001100 00000010 00000000 00000000 00000000
00000000 00000000 00000000 00000000 01101001
In this example, the 6-th bit of the 6-th is used to code the On-Off state (last byte also has a change, but serves as
checksum.
"""

__author__ = "Adrien Baland"

####################
# Global parameters
####################

# All times are in microseconds

filename = '../../data/heater_auto_auto_25_on_off.txt'  # File with signals to process

# Threshold length for a signal (pulse/space) to be "too short". Matching signal will be merged with neighbor.
threshold_too_short = 275
# Threshold length for a signal (pulse/space) to be "too long". Sent by remote as a "stop" sign.
threshold_too_large = 3700

# Length to expect for the start of a signal. ALl signals sents by the remote should be like H1, H2, command.
headers = [3500, 1600]
headers_delta = 300


space_length = 485  # Average length for a "space" signal. (Not pulse)
pulse_one_length = 1230  # Average length for a long-pulse signal.
pulse_zero_length = 380  # Average length for a short-pulse signal.
length_delta = 35  # Spread we allow compared to average to still be valid.


########################################################################################################################
# merge_tiny_signals
########################################################################################################################
# Revision History:
#   13/01/2016 AB - Created function
########################################################################################################################
def merge_tiny_signals(all_lengths):
    """
    First pass of signal. Merge all signals that are too short to be realistic. THis means we need to correct these
    length. Merge the very short signals with other signal. After looking at data, merging all adjacent tiny signals
    together as a first step is the best thing to do (these aggregate signals are merged themselves later).

    INPUT:
        all_lengths (int[])  list of all length recorded by mode2 (space + pulse).

    OUTPUT:
        all_length_converted (int[]) same as input, after adjacent tiny length were merged together
    """

    all_length_converted = []
    in_too_short_phase = False
    for one_length in all_lengths:

        # If very short signal currently seen and previous signal was also very short, merge them together.
        if one_length < threshold_too_short and in_too_short_phase:

            all_length_converted[-1] += one_length

        # Otherwise if first very short signal, initialize the "to-be-merged" value.
        elif one_length < threshold_too_short:

            in_too_short_phase = True
            all_length_converted.append(one_length)

        # If normal value, ignore.
        else:

            in_too_short_phase = False
            all_length_converted.append(one_length)

    ############################
    return all_length_converted
    ############################

#########################
# END merge_tiny_signals
#########################


########################################################################################################################
# merge_large_signal
########################################################################################################################
# Revision History:
#   13/01/2016 AB - Created function
########################################################################################################################
def merge_large_signal(all_lengths):
    """
    Second pass of signal. Merge all large lengths analyzed by mode2 when they are too close to each other. Due to the
    noise explained in phase1, a raw signal like 231000 10 10 10 10 300 10 10 10 10 329300 would be converted into
    231000 40 300 40 329300 after phase 1. However, knowledge about how the signal SHOULD be tells us that this is
    another type of noise and that the two holes of "40" are mistakes. This pass will merge these numbers together to
    give 560680.

    In short : merges large length together if these are close enough together.

    INPUT:
        all_lengths (int[])  list of all length recorded by mode2 (space + pulse), with short-length merged.

    OUTPUT:
        all_length_converted (int[][]) same as input, after close large length were merged together, and after the split
           of the full data into each individual signal
    """

    all_lengths_converted = []
    past_large_index = None
    for index in range(len(all_lengths)-1):

        # Check if value is very large length.
        if all_lengths[index] > threshold_too_large:

            # If first very large length, just remember the position.
            if past_large_index is None:

                past_large_index = index
                continue

            # Otherwise, looks how many lengths are there between the two successive very large length. If small number
            #   a signal could not have been send in between, so apply mergure.
            if index - past_large_index < 10:

                all_lengths[index] += sum(all_lengths[past_large_index:index])

            else:

                # If large number, a signal might be between those bounds so append it to list
                all_lengths_converted.append(all_lengths[past_large_index:index])

            past_large_index = index

    all_lengths_converted.append(all_lengths[past_large_index:])

    #############################
    return all_lengths_converted
    #############################

#########################
# END merge_large_signal
#########################


########################################################################################################################
# repair_headers
########################################################################################################################
# Revision History:
#   13/01/2016 AB - Created function
########################################################################################################################
def repair_headers(all_signals):
    """
    Third pass : creates the separate full signals and makes sure that their heading values are correct.
    Each remote has its own 2 number that they first send before the actual command. Makes sure that the two numbers
    are there at the beginning (merges some lengths if necessary to reobtain them).

    INPUT:
        all_signals (int[][])  list of all signals (space + pulse), with short-length and longth-length and longth

    OUTPUT:
        int[][] each full signal sent by the remote, with one value to ignore and the 2 headers as a start for each
    """

    all_signals_repaired = []
    for one_signal in all_signals:

        # First header value. Checks if first item is signal is in [H0 - DH, H0 + DH]. If not, attempt reconstruction
        if not (-headers_delta <= one_signal[1] - headers[0] <= headers_delta):

            # Tests if merging two signals together works to obtain that value.
            if -headers_delta <= sum(one_signal[1:3]) - headers[0] <= headers_delta:

                # If it did, apply merge.
                one_signal[1] += one_signal.pop(2)

            # Tests if merging three signals together works to obtain that value.
            elif -headers_delta <= sum(one_signal[1:4]) - headers[0] <= headers_delta:

                # If it did, apply merge.
                one_signal[1] += one_signal.pop(2)
                one_signal[1] += one_signal.pop(2)

            else:

                # If still not possible to obtain first header value, give up and cancel signal to show failure.
                one_signal = None
                print('Could not convert signal beginning.')

        # Second header value. Checks if first item is signal is in [H1 - DH, H1 + DH]. If not, attempt reconstruction
        if one_signal is not None and not (-headers_delta <= one_signal[2] - headers[1] <= headers_delta):

            # Tests if merging two signals together works to obtain that value.
            if -headers_delta <= sum(one_signal[2:4]) - headers[1] <= headers_delta:

                one_signal[2] += one_signal.pop(3)

            # Tests if merging three signals together works:
            elif -headers_delta <= sum(one_signal[2:5]) - headers[1] <= headers_delta:

                one_signal[2] += one_signal.pop(3)
                one_signal[2] += one_signal.pop(3)

            else:

                # If still not possible to obtain second header value, give up and cancel signal to show failure.
                one_signal = None
                print('Could not convert signal beginning.')

        # Append the reconstructed signal (or failure sign) to the list
        all_signals_repaired.append(one_signal)

    ############################
    return all_signals_repaired
    ############################

#####################
# END repair_headers
#####################


########################################################################################################################
# repairs_signal
########################################################################################################################
# Revision History:
#   13/01/2016 AB - Created function
########################################################################################################################
def repairs_signal(all_signals):
    """
    Fourth pass : Attempts to make final mergure to obtain the correct size for a signal. Uses the possible values for
    the different lengths to make the attempt at repair.

    INPUT:
        all_signals (int[][]) each full signal sent by the remote
    
    OUTPUT:
        int[][] same as input, but with all lengths matching what is possible in reality. int[] is None if failure for a
           signal.
    """

    all_signals_repaired = []
    for one_signal in all_signals:

        # Otherwise starts check (at position three since beginning was already checked in third pass
        index = 3
        while one_signal is not None and len(one_signal) > 292 and index < len(one_signal) - 1:

            # If odd index : value should be around "space_length"
            if index % 2 == 1:

                # Tests if value is indeed around space_length
                if not (-length_delta < one_signal[index] - space_length < length_delta):

                    if -length_delta < sum(one_signal[index:index+2]) - space_length < length_delta:

                        # Too far away from space_length. Attempt to merge 2 adjacent lengths to obtain space_length.
                        one_signal[index] += one_signal.pop(index+1)

                    elif -length_delta < sum(one_signal[index:index+3]) - space_length < length_delta:

                        # Too far away from space_length. Attempt to merge 3 adjacent lengths to obtain space_length.
                        one_signal[index] += one_signal.pop(index+1)
                        one_signal[index] += one_signal.pop(index+1)

                    else:

                        # Could not obtain space_length. Give up and export failure.
                        one_signal = None
                        break

            # If even index, either number is around pulse_one_length or pulse_zero_length
            else:

                # Tests if value is indeed around pulse_one_length or pulse_zero_length
                if not (-length_delta < one_signal[index] - pulse_one_length < length_delta) \
                        and not (-length_delta < one_signal[index] - pulse_zero_length < length_delta):

                    if -length_delta < sum(one_signal[index:index+2]) - pulse_one_length < length_delta \
                            or -length_delta < sum(one_signal[index:index+2]) - pulse_zero_length < length_delta:

                        # Too far away from pulse_length. Attempt to merge 2 adjacent lengths to obtain pulse_length.
                        one_signal[index] += one_signal.pop(index+1)

                    elif -length_delta < sum(one_signal[index:index+3]) - pulse_one_length < length_delta \
                            or -length_delta < sum(one_signal[index:index+3]) - pulse_zero_length < length_delta:

                        # Too far away from pulse_length. Attempt to merge 3 adjacent lengths to obtain pulse_length.
                        one_signal[index] += one_signal.pop(index+1)
                        one_signal[index] += one_signal.pop(index+1)

                    else:

                        # Could not obtain pulse_length. Give up and export failure.
                        one_signal = None
                        break

            index += 1

        all_signals_repaired.append(one_signal)

    ############################
    return all_signals_repaired
    ############################

#####################
# END repairs_signal
#####################


########################################################################################################################
# to_binary
########################################################################################################################
# Revision History:
#   13/01/2016 AB - Created function
########################################################################################################################
def to_binary(all_signals):
    """
    Fifth pass : Goes through each signal and converts it to its binary form, i.e. converts all pulse lengths to either
     1 or 0 depending on whether the length was closer to pulse_zero_length or pulseone_length.

    INPUT:
        all_signals (int[][]) each full signal sent by the remote

    OUTPUT:
        str[] all_signals converted into their binary form, where a space separates each byte
    """

    all_signals_converted = []
    for one_signal in all_signals:

        if one_signal is None:

            all_signals_converted.append('None')
            continue

        # Signal could be reconstructed with previous passes. The signal already has the correct form, so all we need to
        #   do is convert to binary with no further check required. Starts at index 4 to ignore header.
        #   One out of two lengths is skipped (space_length) because it just aims to separate long for short pulse.

        one_signal_convert = ''
        for index in range(4, len(one_signal), 2):

            # Adds space to separate bytes
            if (index - 4) % 16 == 0:

                one_signal_convert += ' '

            # Tests for short pulse vs long pulse.
            if -length_delta < one_signal[index] - pulse_zero_length < length_delta:

                one_signal_convert += '0'

            else:

                one_signal_convert += '1'

        # Signal reconstructed and converted. Append it to list (after removing initial tab.
        all_signals_converted.append(one_signal_convert[1:])

    #############################
    return all_signals_converted
    #############################

################
# END to_binary
################


########################################################################################################################
# START
########################################################################################################################
with open(filename, 'r') as fileIn:

    full_signal = fileIn.read()

if full_signal is None:

    print('Fail')
    exit(1)

full_signal = full_signal.replace('-pulse', '').replace('-space', '')

full_signal_int = [int(x) for x in full_signal.split()]

full_signal_int = merge_tiny_signals(full_signal_int)
full_signal_int = merge_large_signal(full_signal_int)
full_signal_int = repair_headers(full_signal_int)
full_signal_int = repairs_signal(full_signal_int)
full_signal_bin = to_binary(full_signal_int)

print('\n'.join(full_signal_bin))