from config import db
from .api_model import auth_api, registeration_model, login_model, reset_password_model
from flask_restplus import Resource
from user.models import User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required
from .emailToken import confirm_registeration_token, generate_confirmation_token, send_email, generate_reset_password_token, confirm_reset_password_token
from flask import render_template, url_for, request
import smtplib

@auth_api.route('/login')
class Login(Resource):
    
    @auth_api.expect(login_model)
    def post(self):
        """login view"""
        args = auth_api.payload

        username = args['username']
        email = args['email']
        password = args['password']

        if not username and not email or not password:
            return {'message': 'Missing credentials.'}

        user = User.query.filter(
            db.or_(User.email == email, User.username == username)).first()

        if not user:
            return {'message': 'No user found!'}

        if check_password_hash(user.password, password):
            access_token = create_access_token(
                identity={
                    "username": user.username,
                    'is_admin': user.is_admin,
                    'email': user.email,
                    'is_confirmed':user.is_confirmed
                }
            )
            refresh_token = create_refresh_token(
                identity={
                    "username": user.username,
                    'is_admin': user.is_admin,
                    'email': user.email,
                    'is_confirmed':user.is_confirmed
                }
            )
            return {
                'message': 'successful login',
                'access_token': access_token,
                'refresh_token': refresh_token
            }
        else:
            return {'message': 'wrong password'}

@auth_api.route('/registeration')
class Register(Resource):

    @auth_api.expect(registeration_model)
    def post(self):
        """registeration view"""
        args = auth_api.payload

        username = args['username']
        email = args['email']
        password1 = args['password1']
        password2 = args['password2']
        hashed_password = generate_password_hash(password1)

        if not username and not email or not password1 or not password2:
            return {'message': 'Compelete the fields'}

        if password2 != password1:
            return {'message': 'Both password fileds must be the same'}

        check_user = User.query.filter(
            db.or_(User.username == username, User.email == email)).first()
        if check_user is not None:
            return {'message': 'User already registered'}

        user = User(
            username=username,
            email=email,
            password=hashed_password,
            is_confirmed=False,
            is_admin=False
        )

        # generating token
        access_token = create_access_token(
            identity={"username": user.username, 'is_admin': user.is_admin, 'email': user.email})
        refresh_token = create_refresh_token(
            identity={"username": user.username, 'is_admin': user.is_admin, 'email': user.email})

        # sending email
        token = generate_confirmation_token(user.email)
        confirm_url = url_for('confirm_registeration_email',
                              token=token, _external=True)
        html = render_template('actvate_email.html', confirm_url=confirm_url)
        try:
            send_email(
                user.email, "SE project : Registeration confirmation email", html)
        except smtplib.SMTPRecipientsRefused:
            return {'message': 'unable to send email to {}'.format(user.email)}

        #applying changes to database
        db.session.add(user)
        db.session.commit()

        return {
            'message': 'Registration successful, confirmation email is sent to your email.',
            'access_token': access_token,
            'refresh_token': refresh_token
        }

@auth_api.route('/registeration/activate/<token>')
class RegisterConfirmation(Resource):
    def get(self, token):
        """Account actication view"""
        try:
            email = confirm_registeration_token(token)
        except:
            return {'message': 'Invalid link or expiered link.'}

        user = User.query.filter_by(email=email).first_or_404()

        if user.is_confirmed:
            return {'message': 'Already confirmed; please login.'}
        else:
            user.is_confirmed = True
            db.session.add(user)
            db.session.commit()
            return {'message': 'Account confirmed successfully'}

@auth_api.route('/reset-password/<token>')
class ResetPasswordConfirmation(Resource):
    @jwt_required
    @auth_api.expect(reset_password_model)
    def post(self,token):
        """Account reset password view; token required"""
        try:
            email = confirm_registeration_token(token)
        except:
            return {'message': 'Invalid link or expiered link.'}

        args = auth_api.payload

        old_password = args['old_password']
        new_password1 = args['new_password1']
        new_password2 = args['new_password2']

        message = None

        if not old_password or not new_password1 or not new_password2:
            message = "Complete the fields."

        if new_password2 != new_password1:
            message = "Old passwords should match."

        user = User.query.filter_by(email=email).first_or_404()

        if check_password_hash(user.password, old_password):
            user.password = generate_password_hash(new_password2)
            db.session.add(user)
            db.session.commit()
            message = "New password has been set."
        else:
            message = "Password is wrong."
        
        return {'message':message}

class ResetPassword(Resource):
    @jwt_required
    def get(self):
        """Reset password view; token required"""
        #extracting info
        email = get_jwt_identity()['email']
        #creating and sending email
        token = generate_reset_password_token(email)
        reset_url = url_for('reset_password_confirmation',
                              token=token, _external=True)
        html = render_template('reset_password.html', reset_url = reset_url)
        send_email(email, "SE project Reset password",html)
        try:
            send_email(email, "SE project Reset password",html)
            return {'message':'Reset password email has been sent.'}
        except smtplib.SMTPRecipientsRefused:
            return {'message': 'unable to send email to {}'.format(email)}