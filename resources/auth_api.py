from config import db, api
from flask_restplus import Resource, reqparse
from models.user_model import User
from werkzeug.security import generate_password_hash, check_password_hash

login_parser = reqparse.RequestParser()
login_parser.add_argument('username',required=True)
login_parser.add_argument('password',required=True)

register_parser = reqparse.RequestParser()
register_parser.add_argument('username',required=True)
register_parser.add_argument('password1',required=True)
register_parser.add_argument('password2',required=True)

class Login(Resource):
    @api.expect(login_parser)
    def post(self):
        args = login_parser.parse_args()
        username = args['username']
        password = args['password']
        if not username or not password:
            return {'message':'missing username or password'}
        user = User.query.filter_by(username=username).first()
        if not user:
            return {'message': 'no user found with this username'}
        if check_password_hash(user.password,password):
            return {'message':'successful login'}
        else:
            return {'message':'wrong password'}

class Register(Resource):
    @api.expect(register_parser)
    def post(self):
        args = register_parser.parse_args()
        username = args['username']
        password1 = args['password1']
        password2 = args['password2']
        if not username or not password1 or not password2:
            return {'message':'Complete the fields'}
        if password2!=password1:
            return {'message':'Both password fileds should be the same'}
        check_user = User.query.filter_by(username=username).first()
        if check_user is not None:
            return {'message':'User already registered'}
        hashed_password = generate_password_hash(password1)
        user = User(username=username,password = hashed_password)
        db.session.add(user)
        db.session.commit()
        return {'message':'Registration successful'}