class AbstractAdapter:
    """
    Base class which defines the minimal set of functions, that all
    inherhting classes have to implement.

    """

    def __init__(self, **config):
        raise NotImplementedError()

    def execute_sql(self, query):
        raise NotImplementedError()

    def get_all(self, tablename, fields):
        raise NotImplementedError()

    def get_by_filter(self, tablename, fields, **filters):
        raise NotImplementedError()

    def count(self, tablename, **filters):
        raise NotImplementedError()

    def create(self, tablename, fields, **attributes):
        raise NotImplementedError()

    def delete_all(self, tablename, **filters):
        raise NotImplementedError()

    def delete_by_filter(self, tablename, **filters):
        raise NotImplementedError()
