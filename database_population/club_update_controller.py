from flask_restplus import Resource
import requests
from flask import current_app
from .api_model import database_population_update_api
from .globals import football_api, available_competitions
from club.models import Club
from compeition.models import Competition
from config import db
from user.permissions import admin_required
from flask_jwt_extended import jwt_required



@database_population_update_api.route('/club-update')
class UpdateClub(Resource):
    @jwt_required
    @admin_required
    def get(self):
        """Insert clubs if new ones were added"""
        new_clubs = 0
        for competition in available_competitions:
            url = football_api['CompetitionClub']% competition
            headers ={}
            headers['X-Auth-Token'] =  current_app.config['SOURCE_API_SECRET_KEY']

            resp = requests.get(url=url,headers = headers)
            resp = resp.json()
            competitionn = resp['competition']
            comp = Competition.query.filter(Competition.id == competitionn.get('id')).first()
            clubs = resp['teams']
            
            for club in clubs:
                to_insert = Club.query.filter(Club.id == club.get('id')).first()
                if to_insert == None:
                    club_to_insert = Club(
                        id = club['id'],
                        name = club['name'],
                        shortName = club['shortName'],
                        area_id = club['area']['id'],
                        image = club['crestUrl'],
                        lastUpdated = club['lastUpdated']
                    )
                    new_clubs+=1
                    comp.clubs.append(club_to_insert)
            db.session.commit()
        return {'message':"%d new clubs were added to database."%new_clubs}

