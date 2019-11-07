from flask import Flask
from config import db, api, jwt, mail, ma
from user.controllers import UserView, UserListView
from auth.controllers import Login, Register, RegisterConfirmation, ResetPasswordConfirmation, ResetPassword
from flask_cors import CORS
from game_event.models import Event

#importing apis
from auth.api_model import auth_api
from player.api_model import player_api
from team.api_model import team_api
from user.api_model import user_api
from database_population.api_model import database_population_api
from compeition.api_model import competition_api
from club.api_model import club_api


#importing controllers
from team.controllers import PickSquad, ManageTeam
from database_population.areas_population_controller import PopulateAreas
from database_population.competition_club_population_controller import PopulateClubsCompetitions
from database_population.player_population_controller import PopulatePlayers
from database_population.match_event_population_controller import PopulateMatchesEvents
from player.controllers import MediaPlayer
from compeition.controllers import CompetitionListView
from club.controller import ClubByCompetition


import os

import logging
app = Flask(__name__)

#initing api
api.init_app(app)
api.add_namespace(auth_api, path='/auth')
api.add_namespace(player_api, path='/player')
api.add_namespace(team_api, path='/team')
api.add_namespace(user_api, path='/user')
api.add_namespace(database_population_api, path='/populate')
api.add_namespace(competition_api, path='/competition')
api.add_namespace(club_api, path='/club')

#initing app
app.config.from_pyfile('config.cfg')
app.config['MEDIA_ROOT'] = os.path.join(os.path.dirname(__file__), 'media')
mail.init_app(app)
db.init_app(app)
jwt.init_app(app)
ma.init_app(app)
jwt._set_error_handler_callbacks(api)

#creating new database tables
with app.app_context():
    db.create_all()


CORS(app)#, resources={r"/*": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'
if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
