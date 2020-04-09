from functools import wraps

def database_empty_required(table):
    """check if the database is empty"""
    def inner_function(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            rows = table.query.all()
            if len(rows) != 0:
                return {"message":"the database is not empty better to use update endpoint."}, 400
            return func(*args, **kwargs)
        return wrapper
    return inner_function