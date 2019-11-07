from flask_restplus import Resource
from .marshmallow import AreaSchema
from auth.permissions import account_activation_required
from flask_jwt_extended import jwt_required
from .api_model import club_api
from compeition.models import Competition
from .marshmallow import ClubSchema


@club_api.route('/<int:competition_id>/clubs')
class ClubByCompetition(Resource):
    # @account_activation_required
    # @jwt_required
    def get(self, competition_id):
        """pass competition id and get its clubs"""
        competition = Competition.query.filter(Competition.id==competition_id).first()
        if competition == None:
            return {'message':"There's no such competition in database"}

        clubs = competition.clubs

        output = []
        club_schema = ClubSchema()
        for club in clubs:
            serialized_club = club_schema.dump(club)
            output.append(serialized_club)
        return {'clubs':output}