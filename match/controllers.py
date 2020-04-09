from flask_restplus import Resource
from .models import Match
from .api_model import match_api
import datetime
from .match_marshmallow import MatchListSchema, MatchDetailSchema
from config import db
from functools import wraps

@match_api.route('/<int:competition_id>/current-week-matches')
class CurrentWeekMatches(Resource):
    def get(self, competition_id):

        today = datetime.datetime.utcnow().date()

        startOfWeek = today - datetime.timedelta(days=today.weekday())
        endOfWeek = startOfWeek + datetime.timedelta(days=7)
        all_matches = Match.query.filter(db.and_(Match.competition_id == competition_id, Match.utcDate <= endOfWeek, Match.utcDate >= startOfWeek)).all()
        match_schema = MatchListSchema(many = True)
        output = match_schema.dump(all_matches)
        status = 200
        if len(output) == 0:
            recent_matches = Match.query.filter(Match.competition_id == competition_id).all()
            recent_matches = recent_matches[-10:]
            # status = 404
            # output = "there are no mathces available."
            output = match_schema.dump(recent_matches)
        return {"Matches":output}, status



@match_api.route('/<int:match_id>/details')
class MatchDetail(Resource):
    # @match_exsists
    def get(self, match_id):
        match = Match.query.filter(Match.id == match_id).first()
        output = ""
        status = 200
        if match == None:
            output = "Such match is not found."
            status = 404
        else:
            output = MatchDetailSchema().dump(match)
        return {'match':output}, status


