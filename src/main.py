import command
import logging
import encrypt
import database

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
    logging.basicConfig(handlers=[fh, ch])    


def initialize_cmd():
    CommandTypes = {
        "READ": ['username','application'],
        "GEN": ['username','application'],
        "CREATE": ['username','application','password'],
        "UPDATE": ['username','application','password'],
        "DELETE": ['username','application'],
        "DONE": [],
        # TODO[MS]: The commands below are internal - find a way to exclude users from using them (probably some "Command" object)
        "REGISTER_GOOGLE_DRIVE": ['username', 'password'],
        "CREATE_ENCRYPTION_KEY": ['encryption_key'],
        "CHOOSE_DATABASE_LOCATION": ['database_location'],
        # TODO[MS]: This information should be provided by the DB module (necessary info for DB location)
        "DATABASE_DATABASELOCATION_LOCAL": ['db_file']
    }
    command.init_cmd(CommandTypes)


def initialize_db():
    DB_COLUMNS = ('username', 'application', 'password')
    if database.db_config_exists():
        database.init_db()
    else:
        _, user_args = command.get_user_cmd("CHOOSE_DATABASE_LOCATION")
        user_database_location = user_args.database_location
        db_location = database.DatabaseLocation[user_database_location]
        if db_location == database.DatabaseLocation.LOCAL:
            # TODO[MS]: add conversion from database.DatabaseLocation enum to a string
            _, location_args = command.get_user_cmd("DATABASE_DATABASELOCATION_LOCAL")
            database.init_db(location=db_location, location_args=location_args, columns=DB_COLUMNS)


def initialize_everything():
    config_log()
    initialize_db()
    initialize_cmd()
    _, user_args = command.get_user_cmd("CREATE_ENCRYPTION_KEY")
    encrypt.init_encrypt(user_args.encryption_key)

def main():
    initialize_everything()
    while True:
        try: 
            mode, cmd = command.get_user_cmd()
            if mode == command.CommandMode.CREATE:
                database.DB.create(cmd._replace(password=encrypt.encrypt(cmd.password)))
            if mode == command.CommandMode.RET:
                database.DB.retrieve(cmd)
            # if mode == command.CommandMode.STORE:
            #     pass_db.create(key, cmd)
            # if mode == command.CommandMode.GEN:
            #     pass_db.generate(key, cmd)
            if mode == command.CommandMode.DONE:
                database.DB.write_to_storage()
                break
        except:
            pass

if __name__ == "__main__":
    main()