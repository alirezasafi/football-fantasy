import requests
from flask_restplus import Resource
from .api_model import database_population_api
from club.models import Club
from compeition.models import Competition
from .database_decorators import database_empty_required
from config import db
from flask import current_app

available_competitions = [
    # 2000,2001,
    2002,2003,2013,2014,2015,2016,2017,2018,2019,2021
]
@database_population_api.route('/clubs-competitions')
class PopulateClubsCompetitions(Resource):
    @database_empty_required(Club)
    @database_empty_required(Competition)
    def get(self):
        """population order : 2"""
        for competition in available_competitions:
            url = "https://api.football-data.org/v2/competitions/%s/teams"% competition
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
