from itsdangerous import URLSafeTimedSerializer
from config import mail
from flask import current_app
from flask_mail import Message


def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])

    return serializer.dumps(
        email,
        salt=current_app.config['REGISTER_SALT']
    )


def confirm_registeration_token(token):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt=current_app.config['REGISTER_SALT'],
            max_age=current_app.config['REGISTER_EXPIRATION']
        )
    except:
        return False
    return email

def generate_reset_password_token(email):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])

    return serializer.dumps(
        email,
        salt=current_app.config['RESET_PASSWORD_SALT']
    )

def confirm_reset_password_token(token):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt=current_app.config['RESET_PASSWORD_SALT'],
            max_age=current_app.config['RESET_PASSWORD_EXPIRATION']
        )
    except:
        return False
    return email

def send_email(to, subject, template):
    msg = Message(
        subject,
        recipients=[to],
        html=template,
        sender=current_app.config['MAIL_DEFAULT_SENDER']
    )
    mail.send(msg)
