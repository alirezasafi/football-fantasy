import requests
from flask_restplus import Resource
from .api_model import database_population_update_api
from area.models import Area
from .database_decorators import database_empty_required
from config import db
from .globals import football_api

@database_population_update_api.route('/areas')
class PopulateAreas(Resource):
    @database_empty_required(Area)
    def get(self):
        """population order : 1"""
        url = football_api["Area"]
        resp = requests.get(url=url)
        areas = resp.json()['areas']
        for area in areas :
            to_insert = Area(
                id = area['id'],
                name = area['name'],
            )
            db.session.add(to_insert)
        db.session.commit()

        return {'message':'Areas are populated'}, 200