from flask_restplus import Resource, reqparse
from models.user_model import User
from werkzeug.security import generate_password_hash, check_password_hash
from config import db, api

# deal with single user
class UserView(Resource):
    def get(self, user_id):
        user = User.query.filter_by(id=user_id).first()
        if user is None:
            return {"message": "No user found"}
        user_dict = {
            'username': user.username,
            'email':user.email,
            'password': user.password,
            'id': user.id
        }
        return{'user': user_dict}

    def delete(self, user_id):
        if user_id is not None:
            user = User.query.filter_by(id=user_id).first()
            db.session.delete(user)
            db.session.commit()
            return {"message": "user deleted"}


class UserListView(Resource):
    def get(self):
        users = User.query.all()
        output = []
        for user in users:
            user_dict = {
                'username': user.username,
                'password': user.password,
                'id': user.id,
                'email':user.email
            }
            output.append(user_dict)
        return {'users': output}
