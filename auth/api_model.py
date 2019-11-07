from flask_restplus import Namespace, fields

auth_api = Namespace('Authentication',description="authentication apis")

login_model = auth_api.model(
    'Login',{
        'username':fields.String(description='Login username'),
        'email':fields.String(description='Login email'),
        'password':fields.String(description='Login password')
    }
)

registeration_model = auth_api.model(
    'Registeration',{
        'username':fields.String(required=True, description='Registeration username'),
        'email':fields.String(required=True, description='Registeration email'),
        'password1':fields.String(required=True, description='Registeration password'),
        'password2':fields.String(required=True, description='Registeration password confrimation')
    }
)

reset_password_model = auth_api.model(
    'Reset-password',{
        'old_password':fields.String(required=True, description='old password'),
        'new_password1':fields.String(required=True, description='new password'),
        'new_password2':fields.String(required=True, description='new password confrimation')
    }
)

