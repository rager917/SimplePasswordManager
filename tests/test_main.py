import main
import pytest
import os
import shutil
from unittest import mock
from main import FlowManager

user_create_db_flow = [
    ("LOCAL", "MyTestDB.db", "MyKey", "CREATE", "TempUserName", "TempApp", "TempPass", "READ", "TempUserName", "TempApp", "DONE")
]

@pytest.mark.parametrize("args", user_create_db_flow)
def test_user_creation_db_interactive(caplog, args, monkeypatch):
    # try:
    try:
        TEST_ENV = "test_env"
        if not os.path.exists(TEST_ENV):
            os.mkdir(TEST_ENV)
        os.chdir(TEST_ENV)
        args = iter(args)
        monkeypatch.setattr('builtins.input', lambda _: next(args))
        my_args=['-interactive','1']
        FlowManager(my_args).run()
    finally:
        os.chdir("../")
        shutil.rmtree(TEST_ENV)


