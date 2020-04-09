import requests
from flask_restplus import Resource
from .api_model import database_population_update_api
from club.models import Club
from compeition.models import Competition
from .database_decorators import database_empty_required
from config import db
from flask import current_app
from .globals import football_api, available_competitions
from user.permissions import admin_required
from flask_jwt_extended import jwt_required


@database_population_update_api.route('/clubs-competitions')
class PopulateClubsCompetitions(Resource):
    # @database_empty_required(Club)
    # @database_empty_required(Competition)
    @jwt_required
    @admin_required
    def get(self):
        """population order : 2"""
        for competition in available_competitions:
            url = football_api['CompetitionClub']% competition
            headers ={}
            headers['X-Auth-Token'] =  current_app.config['SOURCE_API_SECRET_KEY']

            resp = requests.get(url=url,headers = headers)
            resp = resp.json()
            competitionn = resp['competition']
            clubs = resp['teams']

            competition_to_insert = Competition(
                id = competitionn['id'],
                name = competitionn['name'],
                startDate = resp['season']['startDate'],
                endDate = resp['season']['endDate'],
                area_id = competitionn['area']['id'],
                lastUpdated = competitionn['lastUpdated']
            )

            for club in clubs:
                club_to_insert = Club(
                    id = club['id'],
                    name = club['name'],
                    shortName = club['shortName'],
                    area_id = club['area']['id'],
                    image = club['crestUrl'],
                    lastUpdated = club['lastUpdated']
                )

                competition_to_insert.clubs.append(club_to_insert)

                db.session.add(club_to_insert)
            db.session.add(competition_to_insert)
        db.session.commit()
        return {'message':'clubs and competitions are populated'}, 200
