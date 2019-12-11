from config import ma
from .models import Match, Status
from marshmallow_enum import EnumField
from club.club_marshmallow import ClubSchema
from compeition.competition_marshmallow import CompetitionSchema
from player.marshmallow import PlayerSchema
from game_event.event_marshmallow import EventSchema

class MatchListSchema(ma.ModelSchema):
    class Meta:
        model = Match
        exclude = ('players',)
    status = EnumField(Status, True)
    homeTeam = ma.Nested(ClubSchema())
    awayTeam = ma.Nested(ClubSchema())
    homeTeamCaptain = ma.Nested(PlayerSchema())
    awayTeamCaptain = ma.Nested(PlayerSchema())
    competition = ma.Nested(CompetitionSchema())
    # events = 
    events = ma.Nested(EventSchema, many = True)

