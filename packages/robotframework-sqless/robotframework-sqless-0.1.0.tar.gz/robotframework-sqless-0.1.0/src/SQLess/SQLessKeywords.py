import os
import yaml

from robot.api import logger



class SQLessKeywords(object):
    ROBOT_LIBRARY_SCOPE = 'Global'

    def __init__(self, schema_path='schema.yml', db_config_path=None):
        logger.console(db_config_path)
        self.schema = self._read_schema(schema_path)
        self.database_config = self._read_config(db_config_path)
        self.adaptor = self._get_adaptor()

    def _get_adaptor(self):
        """
        Helper method to get the correct adaptor

        """
        if self.database_config['dbms'] == 'sqlite':
            from SQLess.adapters.sqlite import SQLiteAdapter
            adaptor = SQLiteAdapter

        elif self.database_config['dbms'] == 'mysql':
            from SQLess.adapters.mysql import MysqlAdapter
            adaptor = MysqlAdapter

        elif self.database_config['dbms'] == 'postgres':
            from SQLess.adapters.postgres import PostgresqlAdapter
            adaptor = PostgresqlAdapter

        elif self.database_config['dbms'] == 'oracle':
            from SQLess.adapters.oracle import OracleAdapter
            adaptor = OracleAdapter

        return adaptor(**self.database_config)

    def _read_config(self, db_config_path):
        """
        Reads the config from the config file

        :returns: dict

        """
        with open(db_config_path) as file:
            database_config = yaml.load(file, Loader=yaml.FullLoader)
        return database_config


    def _read_schema(self, schema_path):
        """
        Reads the schema from the schema defintion file

        :returns: dict

        """
        with open(schema_path) as file:
            schema_defintion = yaml.load(file, Loader=yaml.FullLoader)
        return schema_defintion

    def _get_tablename_and_fields(self, identifier):
        tablename = self.schema.get(identifier.lower())['tablename']
        fields = self.schema.get(identifier.lower())['fields']
        return (tablename, fields)

    def execute_sql_string(self, query):
        """
        Passes the query to the adaptor and returns the result

        """
        return self.adaptor.execute_sql(query)

    def get_all(self, identifier):
        """
        Returns all rows from the table identified by the `identifier`.

        Keyword usage example:
            ${users}   Get All    Users

        The `identifier` must match a table defintion in the schema defintion file.

        :returns: list of dicts
        example:
        [
            {
                'id': 1,
                'username': 'TestUser1'
            },
            ...
        ]
        """
        tablename, fields = self._get_tablename_and_fields(identifier)
        return self.adaptor.get_all(tablename, fields)

    def get_by_filter(self, identifier, **filters):
        """
        Returns the rows from the table identified by the `identifier`, where the filter matches.

        Keyword usage example:
            ${users}   Get By Filter    Users    email=someothername@someotherdomain.tld

        The `identifier` must match a table defintion in the schema defintion file and the filter keys must
        match row names in the schema defintion file.


        :returns: list of dicts
        example:
        [
            {
                'id': 1,
                'username': 'TestUser1'
            },
            ...
        ]
        """
        tablename, fields = self._get_tablename_and_fields(identifier)
        return self.adaptor.get_by_filter(tablename, fields, **filters)

    def count(self, identifier, **filters):
        """
        Counts the matching rows and returns.

        :returns: integer

        """
        tablename, _ = self._get_tablename_and_fields(identifier)
        return self.adaptor.count(tablename, **filters)

    def create(self, identifier, **attributes):
        """
        Creates a row in the database identified by the `identifier`.

        Keyword usage:
            ${user}   Create    Users    username=AnotherUser

        :returns: dict
        example:
            {
                'id': 1,
                'username': 'TestUser1'
            }
        """
        tablename, fields = self._get_tablename_and_fields(identifier)
        return self.adaptor.create(tablename, fields, **attributes)

    def delete_all(self, identifier):
        """
        Deletes all rows in the database identified by the `identifier`.

        Keyword usage:
            ${amount}    Delete All    Users

        :returns: None

        """
        tablename, fields = self._get_tablename_and_fields(identifier)
        return self.adaptor.delete_all(tablename)

    def delete_by_filter(self, identifier, **filters):
        """
        Deletes all rows in the database identified by the `identifier`.

        Keyword usage:
            ${amount}    Delete By Filter    Users    username=TestUser1

        :returns: None

        """
        tablename, fields = self._get_tablename_and_fields(identifier)
        return self.adaptor.delete_by_filter(tablename, **filters)

    def update_all(self, identifier, **attributes):
        """
        Updates all rows in the database identified by the `identifier`
        with the passed attributes.

        Keyword usage:
            Update All    Songs    in_collection=1

        :returns: None

        """
        tablename, fields = self._get_tablename_and_fields(identifier)
        return self.adaptor.update_all(tablename, **attributes)

    def update_by_filter(self, identifier, filters, **attributes):
        """
        Updates the rows in the database identified by the `identifier`
        and filtered by the passed filters with the passed attributes.
        The filters must be a dict containing the keys and values to identify rows.


        Keyword usage:
            ${filter}    Create Dictionary    artist=Nightwish
            Update By Filter    Songs    ${filter}    album=Decades: Live in Buenos Aires

        :returns: None

        """
        tablename, fields = self._get_tablename_and_fields(identifier)
        return self.adaptor.update_by_filter(tablename, filters, **attributes)
