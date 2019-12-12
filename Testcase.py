from flask_testing import TestCase
import unittest, os
from config import db, mail, jwt, ma
from router import api
from flask import Flask

from auth.api_model import auth_api
from player.api_model import player_api
from team.api_model import team_api
from user.api_model import user_api
from club.api_model import club_api
from compeition.api_model import competition_api
from match.api_model import match_api
from statistics.api_model import statistics_api



class AbstractTestCase(TestCase):
    def create_app(self):
        self.file_path = os.path.abspath(os.getcwd())+"/database.db"
        app = Flask(__name__)
        app.config.from_pyfile('test_config.cfg')
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+self.file_path
        mail.init_app(app)
        db.init_app(app)
        jwt.init_app(app)
        api.init_app(app)
        ma.init_app(app)
        api.add_namespace(auth_api, path='/auth')
        api.add_namespace(player_api, path='/player')
        api.add_namespace(team_api, path='/team')
        api.add_namespace(user_api, path='/user')
        api.add_namespace(club_api, path='/club')
        api.add_namespace(competition_api, path='/competition')
        api.add_namespace(match_api, path='/match')
        api.add_namespace(statistics_api, path='/statistics')

        return app

    def setUp(self):
        with self.app.app_context():
            # create all tables
            db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        os.remove(self.file_path)