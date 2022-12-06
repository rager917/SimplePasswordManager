import command
import logging
import encrypt
import database
import os
import argparse
import cryptography

class CustomFormatter(logging.Formatter):
    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

def config_log():
    ch = logging.StreamHandler()
    ch.setFormatter(CustomFormatter())
    fh = logging.FileHandler('SimplePasswordManager.log', mode='w')
    logging.basicConfig(handlers=[fh, ch], level=logging.INFO)    

CommandTypes = {
    "READ": ['username','application'],
    "GEN": ['username','application'],
    "CREATE": ['username','application','password'],
    "UPDATE": ['username','application','password'],
    "DELETE": ['username','application'],
    "PRINT_ALL": [],
    "DONE": [],
    # TODO[MS]: The commands below are internal - find a way to exclude users from using them (probably some "Command" object)
    "CREATE_ENCRYPTION_KEY": ['encryption_key'],
    "CHOOSE_DATABASE_LOCATION": ['db_location'],
    # TODO[MS]: This information should be provided by the DB module (necessary info for DB location)
    "DATABASE_DATABASELOCATION_LOCAL": ['db_file']
}

def initialize_cmd():
    command.init_cmd(CommandTypes)

def get_user_flags(args=None):
    parser = argparse.ArgumentParser(allow_abbrev=False)
    parser.add_argument('-interactive', nargs='?', default=0, const=1, help="Start interactive mode")
    parser.add_argument('-encryption_key', help="DB symmetric cryptographic key")
    parser.add_argument('-db_location', help="Choose a DB location (local or remote)")
    parser.add_argument('-db_file', help="DB file location for local databases")
    return parser.parse_args(args=args)

class FlowManager:
    def __init__(self, args=None):
        self.args = get_user_flags(args=args)
        config_log()

    def initialize_db(self):
        DB_COLUMNS = ('username', 'application', 'password', 'salt')
        if self.args.db_location:
            user_db_location = self.args.db_location
        else:
            _, user_args = command.get_user_cmd("CHOOSE_DATABASE_LOCATION")
            user_db_location = user_args.db_location
        db_location = database.DatabaseLocation[user_db_location]
        if db_location == database.DatabaseLocation.LOCAL:
            if self.args.db_file:
                db_file = self.args.db_file
            else:
                # TODO[MS]: add conversion from database.DatabaseLocation enum to a string
                _, location_args = command.get_user_cmd("DATABASE_DATABASELOCATION_LOCAL")
                db_file = location_args.db_file
            return (DB_COLUMNS, db_location, db_file)
            
    def run(self):
        if self.args.interactive:
            self.start_interactive_mode()
        else:
            self.start_non_interactive_mode()

    def start_interactive_mode(self):
        initialize_cmd()
        with database.init_db(*self.initialize_db()) as DB:
            if self.args.encryption_key:
                encryption_key = self.args.encryption_key
            else:
                _, encryption_args = command.get_user_cmd("CREATE_ENCRYPTION_KEY")
                encryption_key = encryption_args.encryption_key
            while True:
                try:
                    mode, cmd = command.get_user_cmd()
                    if mode == command.CommandMode.CREATE:
                        salt = os.urandom(16)
                        encrypt.init_encrypt(encryption_key, salt)
                        DB.create(tuple(cmd._replace(password=encrypt.encrypt(cmd.password))) + (salt,))
                    if mode == command.CommandMode.READ:
                        rows = DB.read(cmd)
                        if not rows:
                            logging.error("The given combination of user and app doesn't exist")
                        elif len(rows) > 2:
                            logging.error("WTF - more than one password for the same user and App")
                        else:
                            encryped_password, salt = rows[0]
                            encrypt.init_encrypt(encryption_key, salt)
                        try:
                            logging.info(encrypt.decipher(encryped_password))
                        except cryptography.fernet.InvalidToken:
                            logging.error("Bad encryption key for this password")
                    if mode == command.CommandMode.PRINT_ALL:
                        logging.info(DB.read_all())
                    if mode == command.CommandMode.DONE:
                        break
                except:
                    pass

    def start_non_interactive_mode(self):
        pass

def main():
    FlowManager().run()

if __name__ == "__main__":
    main()