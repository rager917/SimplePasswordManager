import os
from enum import Enum
import sqlite3
import logging 

LOGGER = logging.getLogger(__name__)

def create_qmarks(container):
    return ','.join(["?"] * len(container))

class Database:
    def __init__(self, columns):
        self.cur = self.read_from_storage().cursor()
        self.columns = columns

    def create_db(self):
        self.cur.execute(f"CREATE TABLE passwords{self.columns}")
        LOGGER.info("Created new DB successfully")

    def create(self, data):
        self.cur.execute("""
        INSERT INTO movie VALUES
          """)
        pass 

    def read(self, data):
        pass

    def update(self, data):
        pass

    def delete(self, data):
        pass

    def generate(self, data):
        pass

    def read_from_storage(self):
        pass

    def write_to_storage(self):
        pass

class LocalDB(Database):
    def __init__(self, db_file, columns):
        self.db_file = db_file
        super().__init__(columns)

    def read_from_storage(self):
        return sqlite3.connect(self.db_file)

    def write_to_storage(self):
        pass


DatabaseLocation = Enum('DatabaseType', ["LOCAL", "GOOGLE_DRIVE"])

# TODO[MS]: implement db config
def init_db_from_config():
    pass

def write_db_config():
    pass

DB = None
def init_db(location : DatabaseLocation = None, location_args = None, columns = None):
    if db_config_exists():
        init_db_from_config()
    else:
        global DB        
        if location == DatabaseLocation.LOCAL:
            DB = LocalDB(location_args.db_file, columns)
        # TODO[MS]: Support GOOGLE_DRIVE database location
        if location == DatabaseLocation.GOOGLE_DRIVE:
            logging.info("This feature is still under construction")
        DB.create_db()
        write_db_config()

def db_config_exists():
    return os.path.isfile("db_config.ini")
