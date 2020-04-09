from config import ma
from marshmallow_enum import EnumField
from club.club_marshmallow import ClubSchema
from compeition.competition_marshmallow import CompetitionSchema
from player.player_marshmallow import PlayerSchema
from game_event.event_marshmallow import EventSchema
from .models import Match, MatchPlayer, PlayerPlayingStatus, HomeAway, Status


class MatchListSchema(ma.ModelSchema):
    class Meta:
        model = Match
        exclude = ('players','homeTeamCaptain', 'awayTeamCaptain', 'events')
    status = EnumField(Status, True)
    homeTeam = ma.Nested(ClubSchema())
    awayTeam = ma.Nested(ClubSchema())
    competition = ma.Nested(CompetitionSchema())

class MatchDetailSchema(ma.ModelSchema):
    class Meta:
        model = Match
        exclude = ('players',)
    status = EnumField(Status, True)
    homeTeam = ma.Nested(ClubSchema())
    awayTeam = ma.Nested(ClubSchema())
    homeTeamCaptain = ma.Nested(PlayerSchema())
    awayTeamCaptain = ma.Nested(PlayerSchema())
    competition = ma.Nested(CompetitionSchema())
    events = ma.Nested(EventSchema, many = True)


class MatchSchema(ma.ModelSchema):
    status = EnumField(Status, True)

    class Meta:
        model = Match


class Match_PlayerSchema(ma.ModelSchema):
    home_away = EnumField(HomeAway, True)
    playerPlayingStatus = EnumField(PlayerPlayingStatus, True)

    class Meta:
        model = MatchPlayer
