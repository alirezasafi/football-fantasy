from flask_restplus import Resource, reqparse
from models.user_model import User
from werkzeug.security import generate_password_hash, check_password_hash
from config import db, api

user_parser = reqparse.RequestParser()
user_parser.add_argument('username')
user_parser.add_argument('password')

#deal with single user
class UserView(Resource):
    def get(self,user_id):
        user = User.query.filter_by(id=user_id).first()
        if user is None:
            return {"message":"No user found"}
        user_dict = {
                'username':user.username,
                'password':user.password,
                'id':user.id
            }
        return{'user':user_dict}

    def delete(self,user_id):
        if user_id is not None:
            user = User.query.filter_by(id=user_id).first()
            db.session.delete(user)
            db.session.commit()
            return {"message":"user deleted"}

class UserListView(Resource):
    def get(self):
        users = User.query.all()
        output=[]
        for user in users:
            user_dict = {
                'username':user.username,
                'password':user.password,
                'id':user.id
            }
            output.append(user_dict)
        return {'users':output}
    @api.expect(user_parser)
    def post(self):
        args = user_parser.parse_args()
        username = args['username']
        hashed_password = generate_password_hash(args['password'])
        user = User(username = username,password = hashed_password)
        db.session.add(user)
        db.session.commit()
        return {'message':'user added'}, 201