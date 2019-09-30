from flask import Flask
from config import db, api, jwt
from user.controllers import UserView, UserListView
from auth.controllers import Login, Register
app = Flask(__name__)

#initing app
app.config.from_pyfile('config.cfg')
db.init_app(app)
api.init_app(app)
jwt.init_app(app)
jwt._set_error_handler_callbacks(api)

#creating new database tables
with app.app_context():
    db.create_all()

#routing the entire project
api.add_resource(UserView, '/user/<int:user_id>')
api.add_resource(UserListView, '/user')
api.add_resource(Login,'/login')
api.add_resource(Register, '/registeration')

if __name__ == '__main__':
    app.run(debug=True)