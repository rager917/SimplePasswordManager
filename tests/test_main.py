import main
import pytest
import os
import shutil
from unittest import mock
from main import FlowManager
import tempfile

user_create_db_flow = [
    ("LOCAL", "MyTestDB.db", "MyKey", "CREATE", "TempUserName", "TempApp", "TempPass", "READ", "TempUserName", "TempApp", "DONE")
]

# TODO[MS]: Add a way to actually check output
@pytest.mark.parametrize("args", user_create_db_flow)
def test_user_creation_db_interactive(caplog, args, monkeypatch):
    # try:
    with tempfile.TemporaryDirectory() as tmpdirname:
        os.chdir(tmpdirname)
        args = iter(args)
        monkeypatch.setattr('builtins.input', lambda _: next(args))
        my_args=['-interactive','1']
        FlowManager(my_args).run()
        os.chdir("../")


