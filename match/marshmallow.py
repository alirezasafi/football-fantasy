from marshmallow_enum import EnumField
from config import ma
from .models import Match, MatchPlayer, PlayerPlayingStatus, HomeAway, Status


class MatchSchema(ma.ModelSchema):
    status = EnumField(Status, True)

    class Meta:
        model = Match


class Match_PlayerSchema(ma.ModelSchema):
    home_away = EnumField(HomeAway, True)
    playerPlayingStatus = EnumField(PlayerPlayingStatus, True)

    class Meta:
        model = MatchPlayer
