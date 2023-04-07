import tempfile
import os

import pytest
from main import FlowManager
from main import get_user_flags

user_create_db_flow = [
    (
        "MyTestDB.db",
        "MyKey",
        "CREATE",
        "TempUserName",
        "TempApp",
        "TempPass",
        "READ",
        "TempUserName",
        "TempApp",
        "DONE",
    )
]

# TODO[MS]: Add a way to actually check output
@pytest.mark.parametrize("args", user_create_db_flow)
def test_user_creation_db_interactive(args, monkeypatch):
    # try:
    with tempfile.TemporaryDirectory() as tmpdirname:
        os.chdir(tmpdirname)
        args = iter(args)
        monkeypatch.setattr("builtins.input", lambda _: next(args))
        my_args = ["-interactive"]
        FlowManager(get_user_flags(my_args)).run()
        os.chdir("../")
