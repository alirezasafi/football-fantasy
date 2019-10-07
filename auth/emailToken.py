from itsdangerous import URLSafeTimedSerializer
from config import app, db


def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

    return serializer.dumps(
        email,
        salt=app.config['REGISTER_SALT']
    )


def confirm_registeration_token(token):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt=app.config['REGISTER_SALT'],
            max_age = app.config['REGISTER_EXPIRATION']
        )
    except:
        return False
    return email
