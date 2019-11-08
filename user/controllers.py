from flask_restplus import Resource, reqparse
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from config import db
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from .permissions import admin_required

from .api_model import user_api

@user_api.route('/<int:user_id>')
class UserView(Resource):
    @jwt_required
    @admin_required
    def get(self, user_id):
        """get user by id; only admin has access"""
        user = User.query.filter_by(id=user_id).first()
        if user is None:
            return {"message": "No user found"}
        user_dict = {
            'username': user.username,
            'email': user.email,
            'is_admin': user.is_admin,
            'password': user.password,
            'id': user.id
        }
        return{'user': user_dict}

    @jwt_required
    @admin_required
    def delete(self, user_id):
        """delete user by id; only admin has access"""
        if user_id is not None:
            user = User.query.filter_by(id=user_id).first()
            if user ==None:
                return {"message": "No such user found."}
            db.session.delete(user)
            db.session.commit()
            return {"message": "User deleted."}
        else:
            return {'message': 'Specify the user.'}

@user_api.route('/list')
class UserListView(Resource):
    @jwt_required
    @admin_required
    def get(self):
        """list all users; only admin has access"""
        users = User.query.all()
        output = []
        for user in users:
            user_dict = {
                'username': user.username,
                'password': user.password,
                'id': user.id,
                'email': user.email,
                'is_admin':user.is_admin
            }
            output.append(user_dict)
        return {'users': output}
