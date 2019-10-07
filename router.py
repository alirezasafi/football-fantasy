from flask import Flask
from config import db, api, jwt, mail
from user.controllers import UserView, UserListView
from auth.controllers import Login, Register, RegisterConfirmation
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
api.add_resource(Login,'/login')
api.add_resource(Register, '/registeration')
api.add_resource(RegisterConfirmation,'/registeration/<token>', endpoint = 'confirm_registeration_email')

if __name__ == '__main__':
    app.run(debug=True)