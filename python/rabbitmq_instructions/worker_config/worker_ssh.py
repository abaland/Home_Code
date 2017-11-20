import subprocess
from global_libraries import general_utils


####################################################################################################
# test_sshd_alive
####################################################################################################
# Revision History :
#    2017-05-24 Adba : Function created
####################################################################################################
def test_sshd_alive():
    """
    """

    ############
    return True
    ############

######################
# END test_sshd_alive
######################


####################################################################################################
# execute
####################################################################################################
# Revision History :
#    2017-05-24 Adba : Function created
#    2017-05-27 Adba : Fixed empty return
####################################################################################################
def execute(_, instruction_as_xml, worker_base_response):
    """
    Processes ssh instruction

    INPUT
         worker_instance (Worker) worker instance
         instruction_as_xml (lxml.etree) message to process
         worker_base_response (lxml.etree) base of worker response on which to build

    OUTPUT
         (lxml.etree) worker response, with status report on instruction execution
    """

    # sudo /etc/init.d/ssh stop
    # sudo update-rc.d ssh disable

    # Creates base response to be completed in instruction
    ssh_response = worker_base_response

    # Either 'Start' or 'Stop'
    command_to_send = instruction_as_xml.get('command')

    command_status = 0
    if command_to_send in ['Start', 'Stop']:

        is_sshd_alive = test_sshd_alive()
        if command_to_send is 'Start':

            if not is_sshd_alive:

                subprocess.call('/etc/init.d/ssh start && update-rc.d ssh disable')

        else:

            if is_sshd_alive:

                subprocess.call('/etc/init.d/ssh stop && update-rc.d ssh enable')

    else:

        command_status = general_utils.log_error(-307, 'Accepted are {Start, Stop}')

    # Parsing was successfull
    ssh_response.set('status', str(command_status))

    ####################
    return ssh_response
    ####################

##############
# END execute
##############
