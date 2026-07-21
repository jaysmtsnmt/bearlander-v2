class QueryError(Exception):
    pass

class InvalidOperation(QueryError):
    pass

class CSVError(Exception):
    pass

class WriteError(Exception):
    pass

class SQLError(Exception):
    pass