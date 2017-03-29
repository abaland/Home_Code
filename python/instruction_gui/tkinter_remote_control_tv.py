##################
# GLOBAL PACKAGES
##################
import Tkinter as Tk  # GUI Packages


####################################################################################################
# get_command_inputs
####################################################################################################
# Revision History:
#   2016-11-26 AB - Function Created
####################################################################################################
def get_command_inputs(button_name):

    #############################################
    return ['remote_control', 'tv', button_name]
    #############################################

#########################
# END get_command_inputs
#########################


####################################################################################################
# create_remote
####################################################################################################
# Revision History:
#   2016-11-26 AB - Function Created
####################################################################################################
def create_remote(tkinter_frame, command_sender):
    """
     ____________________________________
    |               POWER               | Power(0, 0, 1R, 6C)
    |-----------------------------------|
    |    BACK    |   UP    |    MODE    | Back(1, 0, 1R, 2C)  Up(1, 2, 1R, 2C)   Mode(1, 4, 1R, 2C)
    |____________|_________|____________|
    |            |         |            |
    |    LEFT    |   OK    |   RIGHT    | Left(2, 0, 1R, 2C)  Ok(2, 2, 1R, 2C)   Right(2, 4, 1R, 2C)
    |____________|_________|____________|
    |            |  DOWN   |            |                     Down(3, 2, 1R, 2C)
    |____________|_________|____________|
    |            |         |            |
    |     1      |    2    |     3      | 1(4, 0, 1R, 2C)     2(4, 2, 1R, 2C)     3(4, 4, 1R, 2C)
    |____________|_________|____________|
    |            |         |            |
    |     4      |    5    |     6      | 4(5, 0, 1R, 2C)     5(5, 2, 1R, 2C)     6(5, 4, 1R, 2C)
    |____________|_________|____________|
    |            |         |            |
    |     7      |    8    |     9      | 7(6, 0, 1R, 2C)     8(6, 2, 1R, 2C)     9(6, 4, 1R, 2C)
    |____________|_________|____________|
    |                 |                 |
    |      VOL+       |       CH+       | Vol+(7, 0, 1R, 3C)                      Ch+(7, 3, 1R, 3C)
    |_________________|_________________|
    |                 |                 |
    |      VOL-       |       CH-       | Vol-(8, 0, 1R, 3C)                      Ch-(8, 3, 1R, 3C)
    |_________________|_________________|
    |      SUBS       |      MUTE       | Subs(9, 0, 1R, 3C)                      Mute(9, 3, 1R, 3C)
    |_________________|_________________|

    Conclusion : 6 columns, 10 rows.
    -----------------
    """

    for i in range(10):

        Tk.Grid.rowconfigure(tkinter_frame, i, weight=1)

    for i in range(6):

        Tk.Grid.columnconfigure(tkinter_frame, i, weight=1)

    # Starts creating the button

    # Power
    Tk.Button(tkinter_frame, text='Power',
              command=lambda: command_sender(get_command_inputs('KEY_POWER'))).\
        grid(row=0, column=0, rowspan=1, columnspan=6, sticky='NWSE')

    # Arrows, Ok, Mode, Back
    Tk.Button(tkinter_frame, text='Back',
              command=lambda: command_sender(get_command_inputs('KEY_BACK'))). \
        grid(row=1, column=0, rowspan=1, columnspan=2, sticky='NWSE')

    Tk.Button(tkinter_frame, text='Mode',
              command=lambda: command_sender(get_command_inputs('KEY_MODE'))). \
        grid(row=1, column=4, rowspan=1, columnspan=2, sticky='NWSE')

    Tk.Button(tkinter_frame, text='Up',
              command=lambda: command_sender(get_command_inputs('KEY_UP'))). \
        grid(row=1, column=2, rowspan=1, columnspan=2, sticky='NWSE')

    Tk.Button(tkinter_frame, text='Left',
              command=lambda: command_sender(get_command_inputs('KEY_LEFT'))). \
        grid(row=2, column=0, rowspan=1, columnspan=2, sticky='NWSE')

    Tk.Button(tkinter_frame, text='Ok',
              command=lambda: command_sender(get_command_inputs('KEY_OK'))). \
        grid(row=2, column=2, rowspan=1, columnspan=2, sticky='NWSE')

    Tk.Button(tkinter_frame, text='Right',
              command=lambda: command_sender(get_command_inputs('KEY_RIGHT'))). \
        grid(row=2, column=4, rowspan=1, columnspan=2, sticky='NWSE')

    Tk.Button(tkinter_frame, text='Bottom',
              command=lambda: command_sender(get_command_inputs('KEY_DOWN'))). \
        grid(row=3, column=2, rowspan=1, columnspan=2, sticky='NWSE')

    # Numeric Keypad
    Tk.Button(tkinter_frame, text='1',
              command=lambda: command_sender(get_command_inputs('KEY_NUMERIC_1'))). \
        grid(row=4, column=0, rowspan=1, columnspan=2, sticky='NWSE')

    Tk.Button(tkinter_frame, text='2',
              command=lambda: command_sender(get_command_inputs('KEY_NUMERIC_2'))). \
        grid(row=4, column=2, rowspan=1, columnspan=2, sticky='NWSE')

    Tk.Button(tkinter_frame, text='3',
              command=lambda: command_sender(get_command_inputs('KEY_NUMERIC_3'))). \
        grid(row=4, column=4, rowspan=1, columnspan=2, sticky='NWSE')

    Tk.Button(tkinter_frame, text='4',
              command=lambda: command_sender(get_command_inputs('KEY_NUMERIC_4'))). \
        grid(row=5, column=0, rowspan=1, columnspan=2, sticky='NWSE')

    Tk.Button(tkinter_frame, text='5',
              command=lambda: command_sender(get_command_inputs('KEY_NUMERIC_5'))). \
        grid(row=5, column=2, rowspan=1, columnspan=2, sticky='NWSE')

    Tk.Button(tkinter_frame, text='6',
              command=lambda: command_sender(get_command_inputs('KEY_NUMERIC_6'))). \
        grid(row=5, column=4, rowspan=1, columnspan=2, sticky='NWSE')

    Tk.Button(tkinter_frame, text='7',
              command=lambda: command_sender(get_command_inputs('KEY_NUMERIC_7'))). \
        grid(row=6, column=0, rowspan=1, columnspan=2, sticky='NWSE')

    Tk.Button(tkinter_frame, text='8',
              command=lambda: command_sender(get_command_inputs('KEY_NUMERIC_8'))). \
        grid(row=6, column=2, rowspan=1, columnspan=2, sticky='NWSE')

    Tk.Button(tkinter_frame, text='9',
              command=lambda: command_sender(get_command_inputs('KEY_NUMERIC_9'))). \
        grid(row=6, column=4, rowspan=1, columnspan=2, sticky='NWSE')

    # Volume / Chanel
    Tk.Button(tkinter_frame, text='Ch+',
              command=lambda: command_sender(get_command_inputs('KEY_CHANNELUP'))). \
        grid(row=7, column=0, rowspan=1, columnspan=3, sticky='NWSE')

    Tk.Button(tkinter_frame, text='Vol+',
              command=lambda: command_sender(get_command_inputs('KEY_VOLUMEUP'))). \
        grid(row=7, column=3, rowspan=1, columnspan=3, sticky='NWSE')

    Tk.Button(tkinter_frame, text='Ch-',
              command=lambda: command_sender(get_command_inputs('KEY_CHANNELDOWN'))). \
        grid(row=8, column=0, rowspan=1, columnspan=3, sticky='NWSE')

    Tk.Button(tkinter_frame, text='Vol-',
              command=lambda: command_sender(get_command_inputs('KEY_VOLUMEDOWN'))). \
        grid(row=8, column=3, rowspan=1, columnspan=3, sticky='NWSE')

    # Subs / Mute
    Tk.Button(tkinter_frame, text='Subs',
              command=lambda: command_sender(get_command_inputs('KEY_SUBTITLE'))). \
        grid(row=9, column=0, rowspan=1, columnspan=3, sticky='NWSE')

    Tk.Button(tkinter_frame, text='Mute',
              command=lambda: command_sender(get_command_inputs('KEY_MUTE'))). \
        grid(row=9, column=3, rowspan=1, columnspan=3, sticky='NWSE')
