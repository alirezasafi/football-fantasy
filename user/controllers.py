from flask_restplus import Resource, reqparse
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from config import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from .permissions import admin_required
from auth.permissions import account_activation_required
from .api_model import user_api, delete_profile_model, update_profile_model
from flask import make_response, jsonify, url_for, render_template
from werkzeug.exceptions import BadRequest
from flask_jwt_extended import create_access_token, create_refresh_token
from auth.emailToken import generate_confirmation_token, send_email
import smtplib
from .user_marshmallow import UserSchema
from team.models import User_Player,Fantasy_cards
from .api_model import user_api

@user_api.route('/user/<int:user_id>')
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
            db.session.delete(user)
            db.session.commit()
            return {"message": "User deleted."}
        else:
            return {'message': 'Specify the user.'}

@user_api.route('/user')
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


@user_api.route('/profile')
class Profile(Resource):
    @jwt_required
    # @account_activation_required
    def get(self):
        email = get_jwt_identity()['email']
        user_obj = User.query.filter_by(email=email).first()
        user_response = UserSchema(only={'budget', 'id','username', 'overall_point', 'squad_name', 'email'})
        user_response = user_response.dump(user_obj)
        response = make_response(jsonify(user_response), 200)
        return response

    @user_api.expect(update_profile_model)
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

    @user_api.expect(delete_profile_model)
    @jwt_required
    @account_activation_required
    def delete(self):
        args = user_api.payload
        password = args.get('password')
        email = get_jwt_identity()['email']
        user_obj = User.query.filter_by(email=email).first()
        if check_password_hash(user_obj.password, password):
            db.session.query(User_Player).filter_by(user_id=user_obj.id).delete()
            db.session.query(Fantasy_cards).filter_by(user_id=user_obj.id).delete()
            db.session.delete(user_obj)
            db.session.commit()

            response = make_response(jsonify({'message': 'successfully deleted.'}), 200)
            return response
        else:
            raise BadRequest(description="password is incorrect!")