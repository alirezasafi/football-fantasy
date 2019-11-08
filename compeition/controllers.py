from config import db
from flask_restplus import Resource
from compeition.models import Competition
from flask_jwt_extended import jwt_required
from auth.permissions import account_activation_required
from .api_model import competition_api
from .competition_marshmallow import CompetitionSchema
from config import ma

@competition_api.route('/list')
class CompetitionListView(Resource):
    # @account_activation_required
    @jwt_required
    def get(self):
        all_competitions = Competition.query.all()
        output = []
        competition_schema = CompetitionSchema()

        for competition in all_competitions:
            comp = competition_schema.dump(competition)
            output.append(comp)
        
        return {'competitions':output}
