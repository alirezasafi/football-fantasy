from flask_restplus import Resource
from .models import Match
from .api_model import match_api
import datetime
from .match_marshmallow import MatchListSchema
from config import db

@match_api.route('/<int:competition_id>/current-week-matches')
class CurrentWeekMatches(Resource):
    def get(self, competition_id):

        today = datetime.datetime.utcnow().date()

        startOfWeek = today - datetime.timedelta(days=today.weekday())
        endOfWeek = startOfWeek + datetime.timedelta(days=7)
        # all_matches = Match.query.filter(db.and_(Match.utcDate >= startOfWeek, Match.competition_id == competition_id)).all()
        all_matches = Match.query.filter(db.and_(Match.utcDate <= endOfWeek, Match.utcDate >= startOfWeek)).all()
        match_schema = MatchListSchema(many = True)
        output = match_schema.dump(all_matches)
        return {"Matches":output}




