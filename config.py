from flask_sqlalchemy import SQLAlchemy
from flask_restplus import Api
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_marshmallow import Marshmallow

authorizations = {
    'Bearer Auth': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'authorization',
        'description': "Type in the *'Value'* input box below: **'Bearer &lt;JWT&gt;'**, where JWT is the token"
    }
}

api = Api(
    title='Football fantasy api',
    version='1.0',
    description='software engineering project',
    security='Bearer Auth',
    authorizations=authorizations
)
ma = Marshmallow()
db = SQLAlchemy()
jwt = JWTManager()
mail = Mail()