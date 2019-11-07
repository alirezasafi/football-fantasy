from functools import wraps
from flask_jwt_extended import get_jwt_identity

#decorator to check the is user account is activated
def account_activation_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        decodedToken = get_jwt_identity()
        if decodedToken is not None:
            is_confirmed = decodedToken.get('is_confirmed')
            email = decodedToken.get('email')
            if not is_confirmed:
                return {"message":"Activate your account by email sent to {}".format(email)}
            return f(*args, *kwargs)
        else:
            return {"message":"no token is given"}
    return decorated_function
