import worker_remote_control

is_default = False

config_version = 2

worker_to_instruction = {
    'bedroom': ['remote_control'],
    'living-pi': []
}

instruction_to_module = {
    'remote_control': worker_remote_control
}
