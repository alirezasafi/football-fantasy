from config import db, api
from flask_restplus import Resource, reqparse
from models.user_model import User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token


login_parser = reqparse.RequestParser()
login_parser.add_argument('username')
login_parser.add_argument('email')
login_parser.add_argument('password', required=True)

register_parser = reqparse.RequestParser()
register_parser.add_argument('username', required=True)
register_parser.add_argument('email', required=True)
register_parser.add_argument('password1', required=True)
register_parser.add_argument('password2', required=True)


class Login(Resource):
    @api.expect(login_parser)
    def post(self):
        args = login_parser.parse_args()

        username = args['username']
        email = args['email']
        password = args['password']

        if not username and not email or not password:
            return {'message': 'missing credentials'}
        
        user = User.query.filter(db.or_(User.email==email,User.username==username)).first()

        if not user:
            return {'message': 'no user found'}

        if check_password_hash(user.password, password):
            access_token = create_access_token(identity=username)
            refresh_token = create_refresh_token(identity=username)
            return {
                'message': 'successful login',
                'access_token': access_token,
                'refresh_token': refresh_token
            }
        else:
            return {'message': 'wrong password'}


class Register(Resource):
    @api.expect(register_parser)
    def post(self):
        args = register_parser.parse_args()

        username = args['username']
        email=args['email']
        password1 = args['password1']
        password2 = args['password2']
        hashed_password = generate_password_hash(password1)

        if not username and not email or not password1 or not password2:
            return {'message': 'Complete the fields'}

        if password2 != password1:
            return {'message': 'Both password fileds should be the same'}

        check_user = User.query.filter(db.or_(User.username==username, User.email==email)).first()
        if check_user is not None:
            return {'message': 'User already registered'}

        user = User(username=username,email=email, password=hashed_password)

        db.session.add(user)
        db.session.commit()

        access_token = create_access_token(identity=username)
        refresh_token = create_refresh_token(identity=username)

        return {
            'message': 'Registration successful',
            'access_token':access_token,
            'refresh_token':refresh_token
            }
