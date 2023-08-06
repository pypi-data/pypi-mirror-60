import psycopg2
from robot.api import logger

from .adapter import BaseAdapter


class DatabaseCursor:
    def __init__(self, database_settings):
        self.connection = psycopg2.connect(**database_settings)
        self.cursor = self.connection.cursor()

    def __enter__(self):
        return self.cursor

    def __exit__(self, *args):
        self.connection.commit()
        self.connection.close()


class PostgresqlAdapter(BaseAdapter):

    def __init__(self, **config):
        self.database_settings = config
        self.database_settings.pop('dbms')
        self.database_cursor = DatabaseCursor

    @staticmethod
    def make_select_partial(tablename, fields):
        return "SELECT %s FROM \"%s\"" % (', '.join(fields.keys()) ,tablename)

    @staticmethod
    def make_delete_partial(tablename):
        return "DELETE FROM \"%s\"" % (tablename)

    @staticmethod
    def make_count_partial(tablename):
        return f"SELECT COUNT(*) FROM \"{tablename}\""

    def create(self, tablename, fields, **attributes):
        keys = ", ".join(attributes.keys())
        values = ", ".join([f"'{value}'" for value in attributes.values()])
        query = f"INSERT INTO \"{tablename}\" ({keys}) VALUES ({values}) RETURNING id"
        with self.database_cursor(self.database_settings) as cursor:
            cursor.execute(query)
            last_id = cursor.fetchone()[0]

            cursor.connection.commit()
            result = self.get_by_filter(tablename, fields, id=last_id)[0]
        return result
