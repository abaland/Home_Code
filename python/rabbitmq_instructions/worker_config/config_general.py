from . import worker_remote_control
from . import worker_files
from . import worker_sensors

is_default = False

config_version = 2

worker_to_instruction = {
    'bedroom': ['remote_control', 'files', 'sensors'],
    'living': ['files', 'sensors']
}

instruction_to_module = {
    'remote_control': worker_remote_control,
    'files': worker_files,
    'sensors': worker_sensors
}
