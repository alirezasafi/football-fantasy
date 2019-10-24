from flask_sqlalchemy import SQLAlchemy
from flask_restplus import Api
from flask_jwt_extended import JWTManager
from flask_mail import Mail

api = Api(
    title='Football fantasy api',
    version='1.0',
    description='software engineering project',
)
db = SQLAlchemy()
jwt = JWTManager()
mail = Mail()