from config import ma
from marshmallow import Schema, fields
from player.player_marshmallow import PlayerSchema
from club.club_marshmallow import ClubSchema
from game_event.marshmallow import EventSchema
from match.match_marshmallow import MatchSchema, Match_PlayerSchema
from club.models import Club
from flask import jsonify


class Match_player_detail_Schema(Match_PlayerSchema):
    utcDate = fields.Method('get_utcDate')
    match_result = fields.Method('get_match_result')
    opponent = fields.Method('get_opponent')

    def get_match_result(self, obj):
        result = {'awayTeamScore': obj.match.awayTeamScore, 'homeTeamScore': obj.match.homeTeamScore}
        return result

    def get_utcDate(self, obj):
        return str(obj.match.utcDate)

    def get_opponent(self, obj):
        if obj.home_away.value == "Home":
            return Club.query.filter_by(id=obj.match.awayTeam).first().name
        return Club.query.filter_by(id=obj.match.homeTeam).first().name


class PlayerStatisticsSchema(Schema):
    player = ma.Nested(PlayerSchema(exclude={'club', 'matches', 'events'}))
    club = ma.Nested(ClubSchema(exclude={'lastUpdated'}))
    # matches = ma.Nested(MatchSchema(only={'id', 'utcDate', 'status', 'awayTeamScore', 'homeTeamScore'}), many=True)
    matches = ma.Nested(Match_player_detail_Schema(exclude={'player', 'lastUpdated'}), many=True)
    events = ma.Nested(EventSchema(exclude={'player'}), many=True)