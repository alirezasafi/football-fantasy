from flask import Flask
from config import db, api, jwt, mail
from user.controllers import UserView, UserListView
from auth.controllers import Login, Register, RegisterConfirmation, ResetPasswordConfirmation, ResetPassword
app = Flask(__name__)

#initing app
app.config.from_pyfile('config.cfg')
mail.init_app(app)
db.init_app(app)
api.init_app(app)
jwt.init_app(app)
jwt._set_error_handler_callbacks(api)

#creating new database tables
with app.app_context():
    db.create_all()

#routing the entire project

#routing user
api.add_resource(UserView, '/user/<int:user_id>')
api.add_resource(UserListView, '/user')
#routing authentication
api.add_resource(Login,'/auth/login')
api.add_resource(Register, '/auth/registeration')
api.add_resource(RegisterConfirmation,'/auth/registeration/activate/<token>', endpoint = 'confirm_registeration_email')
api.add_resource(ResetPassword, '/auth/reset-password', endpoint='reset_password')
api.add_resource(ResetPasswordConfirmation, '/auth/reset-password/<token>', endpoint = 'reset_password_confirmation')

if __name__ == '__main__':
    app.run(debug=True)