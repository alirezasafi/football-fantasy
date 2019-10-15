from functools import wraps
from flask_jwt_extended import get_jwt_identity

#decorator to check the is user account is activated
def account_actication_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        decodedToken = get_jwt_identity()
        is_confirmed = decodedToken['is_confirmed']
        email = decodedToken['email']
        if not is_confirmed:
            return {"message":"Activate your account by email sent to {}".format(email)}
        return f(*args, *kwargs)
    return decorated_function
