import command
import pytest
from collections import OrderedDict
import logging
from main import CommandTypes


user_arguments = [
    ("READ", OrderedDict([("username","rager917"), ("application","gmail")])),
    ("GEN", OrderedDict([("username","rager917"), ("application","gmail")])),
    ("CREATE", OrderedDict([("username","rager917"), ("application","gmail"), ("password","my_password")])),
    ("DONE", OrderedDict([]))
]

def user_arguments_id(val):
    return val[0]

@pytest.mark.parametrize("args", user_arguments, ids=user_arguments_id)
def test_get_user_cmd(args, monkeypatch):
    command.init_cmd(CommandTypes)
    initial_cmd = [args[0]]
    cmd_args = args[1].values()
    user_inputs = iter(initial_cmd + list(cmd_args))
    monkeypatch.setattr('builtins.input', lambda _: next(user_inputs))
    mode, cmd = command.get_user_cmd()
    assert mode == command.CommandMode[args[0]]
    for name, value in cmd._asdict().items():
        assert value == args[1][name]


def test_get_user_cmd_when_command_isnt_supported(caplog, monkeypatch):
    command.init_cmd(CommandTypes)
    monkeypatch.setattr('builtins.input', lambda _: "BAD")
    cmd = command.get_user_cmd()
    assert "'BAD' ain't a legal command!" in caplog.text

