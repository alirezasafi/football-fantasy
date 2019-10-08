from flask_restplus import reqparse

login_parser = reqparse.RequestParser()
login_parser.add_argument('username')
login_parser.add_argument('email')
login_parser.add_argument('password', required=True)

registeration_parser = reqparse.RequestParser()
registeration_parser.add_argument('username', required=True)
registeration_parser.add_argument('email', required=True)
registeration_parser.add_argument('password1', required=True)
registeration_parser.add_argument('password2', required=True)

reset_password_parser = reqparse.RequestParser()
registeration_parser.add_argument('old_password1', required=True)
registeration_parser.add_argument('old_password2', required=True)
registeration_parser.add_argument('new_password', required=True)