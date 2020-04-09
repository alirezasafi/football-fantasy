from flask_restplus import Namespace, fields

user_api = Namespace("user management", description="Admin api for manipulating users")

delete_account_model = user_api.model(
    'password',{
        'password': fields.String(required=True),
    }
)

update_account_model = user_api.model(
    'account',{
        'username': fields.String(required=True),
        'password': fields.String(required=True),
        'email':fields.String(required=True),
    }
)