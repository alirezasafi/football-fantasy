from flask_restplus import Resource
from .club_marshmallow import AreaSchema, ClubSchema
from auth.permissions import account_activation_required
from flask_jwt_extended import jwt_required
from .api_model import club_api
from compeition.models import Competition
# from .marshmallow import ClubSchema


@club_api.route('/<int:competition_id>/clubs')
class ClubByCompetition(Resource):
    @jwt_required
    # @account_activation_required
    def get(self, competition_id):
        """pass competition id and get its clubs"""
        competition = Competition.query.filter(Competition.id == competition_id).first()
        if competition == None:
            return {'message':"There's no such competition in database"}, 404

        clubs = competition.clubs

        output = []
        club_schema = ClubSchema(many = True)
        output = club_schema.dump(clubs)
        return {'clubs':output}, 200