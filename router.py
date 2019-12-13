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
from database_population.api_model import database_population_update_api
from compeition.api_model import competition_api
from club.api_model import club_api
from match.api_model import match_api
from statistics.api_model import statistics_api

#importing controllers
from team.controllers import PickSquad, ManageTeam
from database_population.areas_population_controller import PopulateAreas
from database_population.competition_club_population_controller import PopulateClubsCompetitions
from database_population.player_population_controller import PopulatePlayers
from database_population.match_event_population_controller import PopulateMatchesEvents
from player.controllers import MediaPlayer, CompetitionPlayers
from compeition.controllers import CompetitionListView
from club.controller import ClubByCompetition
from database_population.player_score_calculator_controller import PlayerScoreCalc
from database_population.match_event_update_controller import UpdateMatchEvents
from team.squad_point_calculator_controller import CalculateSquadPoint
from match.controllers import CurrentWeekMatches
from database_population.cards_update_controller import UpdateCards
from statistics.controllers import PlayerStatistics, SquadStatistics

import os

import logging
app = Flask(__name__)

#initing api
api.init_app(app)
api.add_namespace(auth_api, path='/auth')
api.add_namespace(player_api, path='/player')
api.add_namespace(team_api, path='/team')
api.add_namespace(user_api, path='/user')
api.add_namespace(database_population_update_api, path='/populate-update')
api.add_namespace(competition_api, path='/competition')
api.add_namespace(club_api, path='/club')
api.add_namespace(match_api, path='/match')
api.add_namespace(statistics_api, path='/statistics')

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
