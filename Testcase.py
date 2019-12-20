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
from compeition.models import Club, Competition
from user.models import User
from werkzeug.security import generate_password_hash
from flask_jwt_extended import create_access_token
from player.models import PlayerStatus, Player, PlayerPosition
from team.models import squad_player, squad, Fantasy_cards
import random


class AbstractTestCase(TestCase):
    def create_app(self):
        self.file_path = os.path.abspath(os.getcwd())+"/database.db"
        app = Flask(__name__)
        app.config.from_pyfile('test_config.cfg')
        # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+self.file_path
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:se23571113@localhost/SE_TEST'
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
        # os.remove(self.file_path)

    def create_competition(self, name="abc_comp"):
        competition = Competition(name=name)
        db.session.add(competition)
        db.session.commit()
        return competition

    def create_clubs(self, competition):
        clubs = []
        for i in range(20):
            club = Club(name='%s %s' % (competition.name, i))
            competition.clubs.append(club)
            db.session.add(club)
            clubs.append(club)
        db.session.add(competition)
        db.session.commit()
        return clubs

    def create_club(self, name="abc_club", competition_name="abc_comp"):
        competition = self.create_competition(name=competition_name)
        club = Club(name=name)
        competition.clubs.append(club)
        db.session.add(club)
        db.session.add(competition)
        db.session.commit()
        return club

    def create_player(self, name="abc_player", status=PlayerStatus.C.name, position=PlayerPosition.Goalkeeper.name):
        club = self.create_club()
        player = Player(name=name,
                        position=position,
                        status=status,
                        price=5,
                        club_id=club.id
                        )
        db.session.add(player)
        db.session.commit()
        return player

    def create_players_of_club(self, club=None):
        if club is None:
            club = self.create_club()
        club_name = club.name
        gk, df, mf, fw = 0, 0, 0, 0
        for j in range(1, 21):
            if gk != 3:
                gk_player = Player(
                    name='%s %s' % (club_name, j),
                    position=PlayerPosition.Goalkeeper.name,
                    status=PlayerStatus.C.name,
                    price=random.randint(4, 7),
                    club_id=club.id
                )
                db.session.add(gk_player)
                gk += 1
            elif df != 6:
                df_player = Player(
                    name='%s %s' % (club_name, j),
                    position=PlayerPosition.Defender.name,
                    status=PlayerStatus.C.name,
                    price=random.randint(4, 7),
                    club_id=club.id
                )
                db.session.add(df_player)
                df += 1
            elif mf != 6:
                mf_player = Player(
                    name='%s %s' % (club_name, j),
                    position=PlayerPosition.Midfielder.name,
                    status=PlayerStatus.C.name,
                    price=random.randint(4, 7),
                    club_id=club.id
                )
                db.session.add(mf_player)
                mf += 1
            elif fw != 5:
                fw_player = Player(
                    name='%s %s' % (club_name, j),
                    position=PlayerPosition.Attacker.name,
                    status=PlayerStatus.C.name,
                    price=random.randint(4, 7),
                    club_id=club.id
                )
                db.session.add(fw_player)
                fw += 1
        db.session.commit()

    def create_players_of_competition(self, competition=None):
        if competition is None:
            competition = self.create_competition()
        clubs = self.create_clubs(competition=competition)
        for club in clubs:
            self.create_players_of_club(club=club)

    def pick_squad_data(self, competition, to_error=False):
        if competition is None:
            return
        clubs = competition.clubs
        squad_gk = Player.query.filter_by(position='Goalkeeper', club_id=clubs[0].id).limit(2).all()
        squad_df1 = Player.query.filter_by(position='Defender', club_id=clubs[1].id).limit(3).all()
        squad_df2 = Player.query.filter_by(position='Defender', club_id=clubs[2].id).limit(2).all()
        squad_mf1 = Player.query.filter_by(position='Midfielder', club_id=clubs[3].id).limit(3).all()
        squad_mf2 = Player.query.filter_by(position='Midfielder', club_id=clubs[4].id).limit(2).all()
        squad_fw = Player.query.filter_by(position='Attacker', club_id=clubs[5].id).limit(3).all()
        if to_error:
            squad_mf1 = Player.query.filter_by(position='Midfielder', club_id=clubs[3].id).limit(4).all()
            squad_mf2 = Player.query.filter_by(position='Midfielder', club_id=clubs[4].id).limit(1).all()

        squad_player_obj = squad_gk + squad_df1 + squad_df2 + squad_mf1 + squad_mf2 + squad_fw
        return squad_player_obj

    def create_squad(self, name="abc_squad", user=None, competition=None):
        if user is None:
            user = self.creat_user()
        if competition is None:
            competition = self.create_competition()

        squad_obj = squad(
            name=name,
            user_id=user.id,
            competition_id=competition.id
        )
        cards = Fantasy_cards(squad=squad_obj)
        db.session.add(cards)
        db.session.add(squad_obj)
        db.session.commit()
        return squad_obj

    def creat_user(self, username="abc", email="abc@gmail.com", password="abcabc", is_admin=False, is_confirmed=False):
        user = User(
            username=username,
            email=email,
            password=generate_password_hash(password),
            is_admin=is_admin,
            is_confirmed=is_confirmed
        )
        db.session.add(user)
        db.session.commit()
        return user

    def active_card(self, card, squad_obj):
        squad_obj.cards.__setattr__(card, 1)
        db.session.commit()

    def use_card(self, card, squad_obj):
        squad_obj.cards.__setattr__(card, -1)
        db.session.commit()

    def inactive_card(self, card, squad_obj):
        squad_obj.cards.__setattr__(card, 0)
        db.session.commit()

    def create_user_access_token(self, user):
        access_token = create_access_token(
            identity={
                "id" : user.id ,
                "username": user.username,
                'is_admin': user.is_admin,
                'email': user.email,
                'is_confirmed':user.is_confirmed
            }
        )
        return access_token