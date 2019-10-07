from config import db, api
from flask_restplus import Resource
from user.models import User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity
from .parsers import login_parser, registeration_parser
from .emailToken import confirm_registeration_token, generate_confirmation_token, send_email
from flask import render_template, url_for
import smtplib

class Login(Resource):
    @api.expect(login_parser)
    def post(self):
        """login view"""
        args = login_parser.parse_args()

        username = args['username']
        email = args['email']
        password = args['password']

        if not username and not email or not password:
            return {'message': 'missing credentials'}

        user = User.query.filter(
            db.or_(User.email == email, User.username == username)).first()

        if not user:
            return {'message': 'no user found'}

        if check_password_hash(user.password, password):
            access_token = create_access_token(
                identity={"username": user.username, 'is_admin': user.is_admin, 'email': user.email})
            refresh_token = create_refresh_token(
                identity={"username": user.username, 'is_admin': user.is_admin, 'email': user.email})
            return {
                'message': 'successful login',
                'access_token': access_token,
                'refresh_token': refresh_token
            }
        else:
            return {'message': 'wrong password'}


class Register(Resource):
    @api.expect(registeration_parser)
    def post(self):
        """registeration view"""
        args = registeration_parser.parse_args()

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
            is_confirmed = False,
            is_admin = False
        )


        #generating token
        access_token = create_access_token(
            identity={"username": user.username, 'is_admin': user.is_admin, 'email': user.email})
        refresh_token = create_refresh_token(
            identity={"username": user.username, 'is_admin': user.is_admin, 'email': user.email})
        
        #sending email
        token = generate_confirmation_token(user.email)
        confirm_url = url_for('confirm_registeration_email', token=token, _external=True)
        html = render_template('actvate_email.html', confirm_url=confirm_url)
        try:
            send_email(user.email, "SE project : Registeration confirmation email", html)
        except smtplib.SMTPRecipientsRefused:
            return {'message':'unable to send email to {}'.format(user.email)}

        db.session.add(user)
        db.session.commit()

        return {
            'message': 'Registration successful, confirmation email is sent to your email.',
            'access_token': access_token,
            'refresh_token': refresh_token
        }


class RegisterConfirmation(Resource):
    def get(self, token):
        try:
            email = confirm_registeration_token(token)
        except:
            return {'message':'Invalid link or expiered link.'}
        
        user = User.query.filter_by(email=email).first_or_404()

        if user.is_confirmed:
            return {'message':'Already confirmed; please login.'}
        else:
            user.is_confirmed = True
            db.session.add(user)
            db.session.commit()
            return {'message':'Account confirmed successfully'}
