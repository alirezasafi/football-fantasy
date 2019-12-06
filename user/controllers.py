from flask_restplus import Resource, reqparse
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from config import db
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from .permissions import admin_required
from auth.permissions import account_activation_required
from .api_model import user_api, delete_account_model, update_account_model
from flask import make_response, jsonify, url_for, render_template
from werkzeug.exceptions import BadRequest
from flask_jwt_extended import create_access_token, create_refresh_token
from auth.emailToken import generate_confirmation_token, send_email
import smtplib
from .user_marshmallow import UserSchema, ProfileSchema
from .api_model import user_api

@user_api.route('/<int:user_id>')
class UserView(Resource):
    @jwt_required
    @admin_required
    def get(self, user_id):
        """get user by id; only admin has access"""
        user = User.query.filter_by(id=user_id).first()
        if user is None:
            return {"message": "No user found"}, 404
        user_dict = {
            'username': user.username,
            'email': user.email,
            'is_admin': user.is_admin,
            'password': user.password,
            'id': user.id
        }
        return{'user': user_dict}, 200

    @jwt_required
    @admin_required
    def delete(self, user_id):
        """delete user by id; only admin has access"""
        if user_id is not None:
            user = User.query.filter_by(id=user_id).first()
            if user ==None:
                return {"message": "No such user found."}, 404
            db.session.delete(user)
            db.session.commit()
            return {"message": "User deleted."}, 200
        else:
            return {'message': 'Specify the user.'}, 400

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
        return {'users': output}, 200


@user_api.route('/profile')
class Profile(Resource):
    @jwt_required
    # @account_activation_required
    def get(self):
        email = get_jwt_identity()['email']
        user_obj = User.query.filter_by(email=email).first()
        profile_schema = ProfileSchema()
        response = profile_schema.dump({'user': user_obj, 'squads': user_obj.squads})
        response = make_response(response, 200)
        return response


@user_api.route('/account')
class account(Resource):
    @user_api.expect(update_account_model)
    @jwt_required
    @account_activation_required
    def put(self):
        args = user_api.payload
        email = get_jwt_identity()['email']
        user_obj = User.query.filter_by(email=email).first()
        new_email = args.get('email')
        new_username = args.get('username')
        new_password = args.get('password')
        if not new_password and not new_email and not new_username:
            raise BadRequest(description="there is no change")
        check_user = User.query.filter(db.or_(User.email==new_email, User.username == new_username)).first()

        if check_user is None:
            message = 'successfully updated'
            if new_username:
                user_obj.username = new_username
            if new_email:
                user_obj.email = new_email
                user_obj.is_confirmed = False
                token = generate_confirmation_token(user_obj.email)
                confirm_url = url_for('auth_register_confirmation',
                                      token=token, _external=True)
                html = render_template('reset_email.html', confirm_url=confirm_url)
                try:
                    send_email(
                        user_obj.email, "SE project : reset email", html)
                except smtplib.SMTPRecipientsRefused:
                    return {'message': 'unable to send email to {}'.format(user_obj.email)}

                message = 'successfully updated, confirmation email is sent to your email.'
            if new_password:
                user_obj.password = generate_password_hash(new_password)
            db.session.commit()
            access_token = create_access_token(
                identity={
                    "username": user_obj.username,
                    'is_admin': user_obj.is_admin,
                    'email': user_obj.email,
                    'is_confirmed': user_obj.is_confirmed
                }
            )
            refresh_token = create_refresh_token(
                identity={
                    "username": user_obj.username,
                    'is_admin': user_obj.is_admin,
                    'email': user_obj.email,
                    'is_confirmed': user_obj.is_confirmed
                }
            )
            response_data = {'message': message, 'access_token': access_token, 'refresh_token': refresh_token}
            response = make_response(jsonify(response_data), 200)
            return response
        else:
            raise BadRequest(description="User already registered")

    @user_api.expect(delete_account_model)
    @jwt_required
    @account_activation_required
    def delete(self):
        args = user_api.payload
        if 'password' not in args.keys():
            raise BadRequest(description="BAD REQUEST")
        password = args.get('password')
        email = get_jwt_identity()['email']
        user_obj = User.query.filter_by(email=email).first()
        if not user_obj:
            raise BadRequest(description="NOT FOUND")
        if check_password_hash(user_obj.password, password):
            db.session.delete(user_obj)
            db.session.commit()
            response = make_response(jsonify({'message': 'successfully deleted.'}), 200)
            return response
        else:
            raise BadRequest(description="password is incorrect!")