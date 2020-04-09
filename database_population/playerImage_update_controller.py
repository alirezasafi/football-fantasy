import requests
from flask_restplus import Resource
from .api_model import database_population_update_api
from .database_decorators import database_empty_required
from config import db
from compeition.models import Competition
from .globals import premier_league_api
from user.permissions import admin_required
from flask_jwt_extended import jwt_required
from club.models import Club
from player.models import Player


@database_population_update_api.route('/players_image/premier_league')
class PopulatePremier(Resource):
    @jwt_required
    @admin_required
    def get(self):
        premier = Competition.query.filter_by(id = 2021).first()
        if not premier:
            return {'message': 'competition not fount.'}, 404
        url = premier_league_api["premier_data"]
        resp = requests.get(url=url)
        teams = resp.json()['teams']
        all_players = resp.json()['elements']
        for team in teams:
            club = premier.clubs.filter(Club.name.contains(team.get("name"))).first()
            if club:
                players = [{"first_name": "{}".format(player.get("first_name")),
                            "second_name": "{}".format(player.get("second_name")),
                            "code": "p{}.png".format(player.get("code"))} for player in all_players if player.get("team") == team.get("id")]
                for element in players:
                    player = club.players.filter((db.or_(Player.name.contains(element.get("second_name",)),
                                                        Player.name.contains(element.get("first_name"))))).first()
                    if player:
                        player.image = premier_league_api.get("player_image") + element.get("code")
        db.session.commit()
        return {'message': 'images are updated'}, 200