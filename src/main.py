import command
import logging
import encrypt
from database import SqlDatabase
import database
import os
import argparse
from collections import namedtuple
import cryptography
import string
from getpass import getpass
import random


class CustomFormatter(logging.Formatter):
    grey = "\x1b[38;20m"
    green = "\x1b[1;32m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    blue = "\x1b[1;34m"
    format = (
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"
    )

    FORMATS = {
        logging.DEBUG: green + format + reset,
        logging.INFO: blue + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def config_log(args):
    ch = logging.StreamHandler()
    ch.setFormatter(CustomFormatter())
    fh = logging.FileHandler("SimplePasswordManager.log", mode="w")
    logging.basicConfig(
        handlers=[fh, ch], level=logging.DEBUG if args.debug else logging.INFO
    )


CommandTypes = {
    "READ": ["username", "application"],
    "GENERATE": ["username", "application", "password_length"],
    "CREATE": ["username", "application", "password"],
    "UPDATE": ["username", "application", "password"],
    "DELETE": ["username", "application"],
    "PRINT_ALL": [],
    "SHOW_DB_FILE": [],
    "PRINT_ALL_ENCRYPTED": [],
    "DONE": [],
    # TODO[MS]: The commands below are internal - find a way to exclude users from using them (probably some "Command" object)
    "CHOOSE_DATABASE_FILE": ["db_file"],
}


def initialize_cmd():
    command.init_cmd(CommandTypes)


def get_user_flags(args=None):
    parser = argparse.ArgumentParser(allow_abbrev=False)
    parser.add_argument(
        "-interactive", nargs="?", default=0, const=1, help="Start interactive mode"
    )
    parser.add_argument("-encryption_key", help=argparse.SUPPRESS)
    parser.add_argument(
        "-db_file",
        help="DB file location for local databases",
        default="SimplePasswordManager.db",
    )
    parser.add_argument(
        "-include_punctuation_in_password_generation",
        default=1,
        help="Self explanatory",
    )
    parser.add_argument(
        "-debug", default=0, const=1, nargs="?", help="Self explanatory"
    )
    return parser.parse_args(args=args)


class FlowManager:
    def __init__(self, args=None):
        self.args = args

    def initialize_db(self):
        DB_COLUMNS = ("username", "application", "password", "salt")
        if self.args.db_file:
            db_file = self.args.db_file
        else:
            _, user_args = command.get_user_cmd("CHOOSE_DATABASE_FILE")
            db_file = user_args.db_file
        return (DB_COLUMNS, db_file)

    def run(self):
        if self.args.interactive:
            self.start_interactive_mode()

    def get_random_string(self, length: int):
        # choose from all lowercase letter
        letters = string.ascii_lowercase + string.ascii_uppercase + string.digits - '"'
        if self.args.include_punctuation_in_password_generation:
            letters = letters + string.punctuation
        return "".join(random.choice(letters) for _ in range(length))

    def call_db_create(self, DB: SqlDatabase, encryption_key, cmd):
        salt = os.urandom(16)
        encrypt.init_encrypt(encryption_key, salt)
        DB.create(tuple(cmd._replace(password=encrypt.encrypt(cmd.password))) + (salt,))

    def call_db_read(self, DB: SqlDatabase, encryption_key: str, cmd):
        rows = DB.read(cmd)
        if not rows:
            logging.error("The given combination of user and app doesn't exist")
        elif len(rows) > 2:
            logging.error("WTF - more than one password for the same user and App")
        else:
            encryped_password, salt = rows[0]
            encrypt.init_encrypt(encryption_key, salt)
            try:
                print(encrypt.decipher(encryped_password))
            except cryptography.fernet.InvalidToken:
                logging.error("Bad encryption key for this password")

    def remove_and_add_fields_to_named_tuple(
        self, my_named_tuple, fields_to_remove: set, fields_to_add: dict
    ):
        common_dict = {
            field: val
            for field, val in my_named_tuple._asdict().items()
            if field not in fields_to_remove
        }
        common_fields_type = namedtuple(
            "COMMON_FIELDS_TYPE", list(common_dict.keys()) + list(fields_to_add.keys())
        )
        return common_fields_type(**common_dict, **fields_to_add)

    def execute_user_command(self, user_cmd, DB: SqlDatabase, encryption_key: str):
        mode, cmd = user_cmd
        if mode == command.CommandMode.CREATE:
            self.call_db_create(DB=DB, encryption_key=encryption_key, cmd=cmd)
        if mode == command.CommandMode.READ:
            self.call_db_read(DB=DB, encryption_key=encryption_key, cmd=cmd)
        if mode == command.CommandMode.PRINT_ALL:
            for row in DB.read_all():
                user_name, app, encrypted_password, salt = row
                encrypt.init_encrypt(encryption_key, salt)
                try:
                    dec_password = encrypt.decipher(encrypted_password)
                except cryptography.fernet.InvalidToken:
                    logging.error(
                        "PRINT_ALL isn't supported with multiple encryption keys"
                    )
                    break
                print(f"{user_name}, {app}, {dec_password}")
        if mode == command.CommandMode.PRINT_ALL_ENCRYPTED:
            for row in DB.read_all():
                user_name, app, encrypted_password, salt = row
                print(f"{user_name}, {app}, {encrypted_password}, {salt}")
        if mode == command.CommandMode.GENERATE:
            new_cmd = self.remove_and_add_fields_to_named_tuple(
                cmd,
                {"password_length"},
                {"password": self.get_random_string(int(cmd.password_length))},
            )
            self.call_db_create(DB=DB, encryption_key=encryption_key, cmd=new_cmd)
            logging.info(f"Succesfully generated new password: {new_cmd.password}")
        if mode == command.CommandMode.SHOW_DB_FILE:
            logging.info(os.path.abspath(DB.get_db_location()))
        if mode == command.CommandMode.DONE:
            return True

    def start_interactive_mode(self):
        initialize_cmd()
        with database.init_db(*self.initialize_db()) as DB:
            if self.args.encryption_key:
                encryption_key = self.args.encryption_key
            else:
                encryption_key = input("ENCRYPTION_KEY: ")
            while True:
                user_cmd = command.get_user_cmd()
                if user_cmd:
                    done = self.execute_user_command(user_cmd, DB, encryption_key)
                    if done:
                        break


def main():
    args = get_user_flags()
    config_log(args)
    try:
        FlowManager(args).run()
    except Exception as e:
        logging.critical(str(e))


if __name__ == "__main__":
    main()
