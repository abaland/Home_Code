"""
"""


##################
# GLOBAL PACKAGES
##################
import tkinter as tk  # GUI Packages
import threading  # Handles multi-threading in code (send RabbitMQ request, check GUI updates, ...)

########################
# Import Local Packages
########################

from rabbitmq_instructions import main as main_script
from global_libraries import general_utils
from . import tkinter_remote_control_tv

####################################################################################################
# CODE START
####################################################################################################


####################################################################################################
# TkinterMain
####################################################################################################
# Revision History:
#   2016-11-26 AB - Class Created
####################################################################################################
class TkinterMain:

    #
    #
    #

    ################################################################################################
    # __init__
    ################################################################################################
    # Revision History:
    #   2016-11-26 AB - Function Created
    ################################################################################################
    def __init__(self, root_window, rabbit_main_object):

        # The GUI itself.
        self.root_window = root_window

        # Creates an empty menu bar in the GUI.
        self.window_menubar = tk.Menu(self.root_window)

        # Main Controller script
        self.rabbit_main = rabbit_main_object  # Makes a reference to the Main Controller
        self.rabbit_main.forward_response_target = self  # Makes reference to GUI inside Main
        
        # Instructions that can be sent to worker. Read by ConfigParser
        self.all_supported_remotes = ['tv', 'aircon']  # List of all possible remote controls
        self.chosen_remote = tk.StringVar()  # Currently chosen instruction index in the list

        self.updatable_frame = tk.Frame(self.root_window)

        ##################
        # Subthread parts
        ##################
        # Creates sandbox for instruction-specific subscripts to use freely.
        self.updatable_frame_elements = {}

        # Subthread to send request to RabbitMQ
        self.requests_thread = None

    ###############
    # END __init__
    ###############

    #
    #
    #

    ################################################################################################
    # set_remote_menu
    ################################################################################################
    # Revision History:
    #   2016-11-26 AB - Function Created
    ################################################################################################
    def set_remote_menu(self):
        """
        Initializes first main frame on the GUI, containing instructions that can be sent to worker.
        This frame is composed of N radio buttons as rows, where each instruction is one such button

        OUTPUT:
            status (int) 0 if no fatal error occured when creating instruction menu, 
                negative number otherwise.
        """

        # In general GUI grid, only one row is used, containing instruction frame + updatable
        # content frame, so set this row to expand to fill the GUI size.
        tk.Grid.rowconfigure(self.root_window, 0, weight=0)
        for i in range(len(self.all_supported_remotes)):

            tk.Grid.columnconfigure(self.root_window, i, weight=1)

        # For each instruction, creates a radio button, locate it in appropriate spot (i-th row,
        # first column) and makes it fill its parent row
        i = 0
        for remote_name in self.all_supported_remotes:

            tk.Radiobutton(self.root_window, text=remote_name, indicatoron=0,
                           variable=self.chosen_remote, value=remote_name,
                           command=self.update_value, padx=5)\
                .grid(row=0, column=i, rowspan=1, columnspan=1, sticky='NWSE')

            i += 1

        #########
        return 0
        #########

    ######################
    # END set_remote_menu
    ######################

    #
    #
    #

    ################################################################################################
    # start_setup
    ################################################################################################
    # Revision History:
    #   2016-11-26 AB - Function Created
    ################################################################################################
    def start_setup(self, window_width, window_height):
        """
        Initializes GUI window entirely.

        Sets the general window to have a given format.
        Adds title to window and menu bar.
        Adds menu with each available command for workers.
        Adds empty updatable frame, to hold worker responses.
        Initializes currently chosen instruction (first one in the list)

        INPUT:
            window_width (int)  width of frame
            window_height (int) height of frame

        OUTPUT:
            status (int) 0 if no fatal error occured when setting up GUI, negative integer otherwise
        """
    
        # Sets size of the window
        self.root_window.resizable(width=False, height=False)
        self.root_window.geometry('{}x{}'.format(window_width, window_height))
        
        # Sets window title
        self.root_window.title('Remote control')

        # Sets list of sendable instruction in window
        self.set_remote_menu()

        # Initializes frame
        tk.Grid.rowconfigure(self.root_window, 1, weight=1)
        self.updatable_frame.grid(row=1, column=0, rowspan=1, columnspan=2, sticky='NWSE')

        # Initializes instruction chosen to be first one, and calls appropriate functions in how to
        # handle that
        self.chosen_remote.set('tv')
        self.update_value()
        
        # Finishes setting-up window.
        self.root_window.config(menu=self.window_menubar)

        #########
        return 0
        #########
    
    #############
    # END set_up
    #############

    #
    #
    #

    ################################################################################################
    # clear_updatable_frame
    ################################################################################################
    # Revision History:
    #   2016-11-26 AB - Function Created
    ################################################################################################
    def clear_updatable_frame(self):
        """
        Clears contents of the updatable frame
        """
    
        # Resets GUI frame of 'response-holder' part (instruction has changed => responses have new
        # structure)
        for updatable_frame_content in self.updatable_frame.winfo_children():

            # Destroy child of the frame to reset one by one
            updatable_frame_content.destroy()

    ############################
    # END clear_updatable_frame
    ############################

    #
    #
    #

    ################################################################################################
    # update_value
    ################################################################################################
    # Revision History:
    #   2016-11-26 AB - Function Created
    ################################################################################################
    def update_value(self):
        """
        Calls relevant submodule given a chosen instruction to send to workers via RabbitMQ. Fetches
         appropriate module inside configuration folder, and calls required function in module to 
         (1) send instructions (2) receive responses (3) apply GUI changes based on response.

        """

        self.clear_updatable_frame()

        # Gets chosen instruction (as a string, instead of its index)
        chosen_remote_name = self.chosen_remote.get()  # Finds matching value

        if chosen_remote_name == 'tv':

            tkinter_remote_control_tv.create_remote(self.updatable_frame, self.send_request)

        #######
        return
        #######
    
    ###################
    # END update_value
    ###################

    #
    #
    #

    ################################################################################################
    # add_response
    ################################################################################################
    # Revision History:
    #   2016-11-26 AB - Function Created
    ################################################################################################
    def add_response(self, instruction_name, worker_id, worker_response):
        """
        Processes response from a worker internally.
        This does NOT update GUI because it is called as a subthread (tkinter only modifies GUI
        through main thread).
        Given the response, worker id, and instruction name, fetches relevant module and updates 
        internal parameters
        appropriatly.

        INPUT:
            instruction_name (str) : currently chosen instruction
            worker_id (str) : id of the worker that sent the response
            worker_response (lxml.etree) : converted response from worker.
        """

        self.updatable_frame_elements['id'] = worker_id

        del instruction_name
        del worker_id
        del worker_response

        #######
        return
        #######
    
    ###################
    # END add_response
    ###################

    #
    #
    #

    ################################################################################################
    # send_request_subordinate
    ################################################################################################
    # Revision History:
    #   2016-11-26 AB - Function Created
    ################################################################################################
    def send_request_subordinate(self, arguments_as_array):
        """
        Starts sending the same request periodically (status request) to workers via RabbitMQ.

        INPUT:
            arguments_as_array (str[]) list of arguments to send RabbitMQ worker, e.g; 
                ['heartbeat', '--timeout', '10']
        """

        # Sends command to RabbitMQ Main Controller script
        self.rabbit_main.keep_listening_for_response = True
        self.rabbit_main.process_live_commands(arguments_as_array)

        #######
        return
        #######

    ##############################
    # send_request_subordinate
    ##############################

    #
    #
    #

    ################################################################################################
    # send_request
    ################################################################################################
    # Revision History:
    #   2016-11-26 AB - Function Created
    ################################################################################################
    def send_request(self, argument_as_array):
        """
        Starts subthread which will send the same request periodically (status request) to workers 
            via RabbitMQ.

        INPUT:
            Arguments_As_Array (str[]) list of arguments to send RabbitMQ worker, e.g; ['heartbeat',
             'timeout', '10']
        """

        # Starts subthread that repeatedly ask main to send a request to worker
        self.requests_thread = threading.Thread(target=self.send_request_subordinate,
                                                args=(argument_as_array,))
        self.requests_thread.start()
    
        #######
        return
        #######

    ###################
    # END send_request
    ###################
        
    #
    #
    #

    ################################################################################################
    # terminate
    ################################################################################################
    # Revision History:
    #   2016-11-26 AB - Function Created
    ################################################################################################
    def terminate(self):
        """
        Sets all necessary flags in code to tell all threads that GUI window was closed (code can 
            stop)
        """

        # Tells main controller script to stop listening for responses
        self.rabbit_main.keep_listening_for_response = False

        #######
        return
        #######

    ################
    # END terminate
    ################

####################
# END TkinterMain
####################


####################################################################################################
# main
####################################################################################################
# Revision History:
#   2016-11-26 AB - Function Created
####################################################################################################
def main():
    """
    Starts Tkinter GUI
    """

    class_name = 'tkinter'
    general_utils.get_welcome_end_message(class_name, True)

    # Creates the instance for a main controller and sets it to listen to GUI commands.
    rabbit_main_program = main_script.main(['-gui'])

    # Creates main window for program GUI
    tkinter_main_window = tk.Tk()

    # Creates GUI Object, to update GUI window
    tkinter_main_object = TkinterMain(tkinter_main_window, rabbit_main_program)

    # Starts building the GUI with all requirement information
    tkinter_main_object.start_setup(400, 300)

    # Update the GUI elements
    tkinter_main_object.root_window.update_idletasks()

    # Starts displaying GUI (blocks the scripts until window is closed)
    tkinter_main_object.root_window.mainloop()

    # Once the window was closed, stops all subthreads.
    tkinter_main_object.terminate()
    
    #######
    return
    #######

###########
# END main
###########


if __name__ == "__main__":
    main()

    # Exits code
    general_utils.get_welcome_end_message('Tkinter', False)

    exit(0)
