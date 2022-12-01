from enum import Enum
from collections import namedtuple
import logging

LOGGER = logging.getLogger(__name__)

# TODO[MS]: add 'options' and 'defaults' functionality for this module

CommandTypes = None
CommandTypesObjects = None
CommandMode = None
def init_cmd(UserCommandTypes):
    global CommandTypes, CommandTypesObjects, CommandMode
    CommandTypes = UserCommandTypes
    CommandTypesObjects = {
        mode: namedtuple(mode, CommandTypes[mode]) for mode in CommandTypes
    }
    CommandMode = Enum('CommandMode', [mode for mode in CommandTypes])

def get_possible_cmds():
    return CommandTypes

def get_user_cmd(user_cmd = None):
    if not user_cmd:
        user_cmd = input("Give password manager a command: ")
    if user_cmd in CommandTypes:
        user_args = []
        for field in CommandTypes[user_cmd]:
            user_args.append(input(f'{field.upper()}: '))
        LOGGER.debug(f"{user_cmd} was called with args: {CommandTypesObjects[user_cmd](*user_args)}")
        return CommandMode[user_cmd],CommandTypesObjects[user_cmd](*user_args)
    else:
        LOGGER.error(f"'{user_cmd}' ain't a legal command!")
        

