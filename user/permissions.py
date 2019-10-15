from functools import wraps
from flask_jwt_extended import get_jwt_identity

# decorator to check if the user is admin or not
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        is_admin = get_jwt_identity()['is_admin']
        if not is_admin:
            return {'message': 'Only admin is privilaged.'}
        return f(*args, **kwargs)
    return decorated_function