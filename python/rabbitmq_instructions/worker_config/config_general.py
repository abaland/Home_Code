import worker_remote_control

is_default = False

config_version = 1

worker_to_instruction = {
    'living-room': ['remote_control']
}

instruction_to_module = {
    'remote_control': worker_remote_control
}
