class BaseAdapter:
    """
    Base class which defines the minimal set of functions, that all
    inherhting classes have to implement and some common methods.

    """

    def __init__(self, **config):
        raise NotImplementedError()

    @staticmethod
    def make_list(result, fieldnames):
        result_list = []
        for item in result:
            result_list.append(dict(zip(fieldnames, item)))
        return result_list

    @staticmethod
    def make_update_partial(tablename, **attributes):
        settings = ", ".join([f"{key}='{value}'" for key, value in attributes.items()])
        return f"UPDATE {tablename} SET {settings}"

    @staticmethod
    def make_select_partial(tablename, fields):
        return "SELECT %s FROM %s" % (', '.join(fields.keys()) ,tablename)

    @staticmethod
    def make_single_filter_partial(filters):
        filter = " AND ".join(f"{key}='{value}'" for key, value in filters.items())
        return filter

    @staticmethod
    def make_delete_partial(tablename):
        return "DELETE FROM %s" % (tablename)

    def make_where_partial(self, filters):
        where_partial = ""
        if filters:
            if isinstance(filters, dict):
                filter = self.make_single_filter_partial(filters)
            if isinstance(filters, list):
                clauses = []
                for clause in filters:
                    clauses.append(self.make_single_filter_partial(clause))
                filter = " OR ".join(clauses)
            where_partial = f"WHERE {filter}"
        return where_partial

    def execute_sql(self, query):
        with self.database_cursor(self.database_settings) as cursor:
            cursor.execute(query)
            result = cursor.fetchall()
        return result

    def get_all(self, tablename, fields):
        with self.database_cursor(self.database_settings) as cursor:
            query = self.make_select_partial(tablename, fields)
            cursor.execute(query)
            result = self.make_list(cursor.fetchall(), fields.keys())
        return result

    def get_by_filter(self, tablename, fields, **filters):
        select_partial = self.make_select_partial(tablename, fields)
        where_partial = self.make_where_partial(filters)
        query = f"{select_partial} {where_partial}"
        with self.database_cursor(self.database_settings) as cursor:
            cursor.execute(query)
            result = self.make_list(cursor.fetchall(), fields.keys())
        return result

    def count(self, tablename, **filters):
        count_partial = self.make_count_partial(tablename)
        where_partial = self.make_where_partial(filters)
        query = f"{count_partial} {where_partial}"
        with self.database_cursor(self.database_settings) as cursor:
            cursor.execute(query)
            result = cursor.fetchone()
        return result[0]

    def create(self, tablename, fields, **attributes):
        raise NotImplementedError()

    def delete_all(self, tablename, **filters):
        with self.database_cursor(self.database_settings) as cursor:
            query = self.make_delete_partial(tablename, **filters)
            cursor.execute(query)

    def delete_by_filter(self, tablename, **filters):
        with self.database_cursor(self.database_settings) as cursor:
            delete_partial = self.make_delete_partial(tablename)
            where_partial = self.make_where_partial(filters)
            cursor.execute(f"{delete_partial} {where_partial}")

    def update_all(self, tablename, **attributes):
        with self.database_cursor(self.database_settings) as cursor:
            update_partial = self.make_update_partial(tablename, **attributes)
            cursor.execute(update_partial)

    def update_by_filter(self, tablename, filters, **attributes):
        with self.database_cursor(self.database_settings) as cursor:
            update_partial = self.make_update_partial(tablename, **attributes)
            where_partial = self.make_where_partial(filters)
            cursor.execute(f"{update_partial} {where_partial}")
