from .commands_const import CommandConstEnum


def parse(string: str) -> dict:
    commands = [x.value for x in CommandConstEnum]
    robot_name = ''
    robot_command = ''
    value = 0
    robot_complete = None
    
    for command in commands:
        ind = string.find(command)
        if ind >= 0:
            robot_name = string[0:ind]
            if command == 'OK' and command in string:
                robot_complete = True
            else:
                value_str = string[ind + len(command):len(string)]
                try:
                    value = int(value_str)
                except ValueError:
                    value = value_str
            robot_command = command
            break

    robot_dict = {
        'name': robot_name,
        'command': robot_command,
        'value': value,
        'command_complete': robot_complete
    }

    return robot_dict

