import os
from enum import Enum
import sqlite3
import logging
from contextlib import contextmanager

LOGGER = logging.getLogger(__name__)


def create_qmarks(container):
    return ",".join(["?"] * len(container))


def create_where_qmarks(data):
    return " AND ".join(f"{field}=?" for field in data._fields)


class SqlDatabase:
    def __init__(self, columns, db_file):
        self.columns = columns
        self.db_file = db_file

    def create_db(self):
        self.cur.execute(f"CREATE TABLE if not exists passwords{self.columns}")

    def create(self, data):
        cmd = f"INSERT INTO passwords VALUES ({create_qmarks(data)})"
        self.cur.execute(cmd, data)

    def read(self, data):
        cmd = (
            f"SELECT password, salt FROM passwords WHERE ({create_where_qmarks(data)})"
        )
        self.cur.execute(cmd, [val for val in data])
        return self.cur.fetchall()

    def read_all(self):
        cmd = f"SELECT * FROM passwords"
        self.cur.execute(cmd)
        return self.cur.fetchall()

    def update(self, data):
        pass

    def delete(self, data):
        pass

    def open_connection(self):
        self.connection = sqlite3.connect(self.db_file)
        self.connection.set_trace_callback(LOGGER.debug)
        self.cur = self.connection.cursor()

    def close_connection(self):
        self.connection.close()


DatabaseLocation = Enum("DatabaseType", ["LOCAL"])


@contextmanager
def init_db(columns, location: DatabaseLocation = None, db_file=None):
    if location == DatabaseLocation.LOCAL:
        DB = SqlDatabase(columns=columns, db_file=db_file)
    DB.open_connection()
    DB.create_db()
    try:
        yield DB
    finally:
        DB.connection.commit()
        DB.close_connection()
