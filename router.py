from flask import Flask
from config import db, api, jwt, mail
from user.controllers import UserView, UserListView
from auth.controllers import Login, Register, RegisterConfirmation, ResetPasswordConfirmation, ResetPassword
#importing apis
from auth.api_model import auth_api
from player.api_model import player_api
from team.api_model import team_api
from user.api_model import user_api

from team.controllers import PickSquad, ManageTeam
from player.controllers import MediaPlayer
import os


app = Flask(__name__)


#initing api
api.init_app(app)
api.add_namespace(auth_api, path='/auth')
api.add_namespace(player_api, path='/player')
api.add_namespace(team_api, path='/team')
api.add_namespace(user_api, path='/user')

#initing app
app.config.from_pyfile('config.cfg')
app.config['MEDIA_ROOT'] = os.path.join(os.path.dirname(__file__), 'media')
mail.init_app(app)
db.init_app(app)
jwt.init_app(app)
jwt._set_error_handler_callbacks(api)

#creating new database tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
