from config import ma
from .models import Player, PlayerPosition, PlayerStatus
from marshmallow_enum import EnumField


class PlayerSchema(ma.ModelSchema):
    class Meta:
        model = Player
    position = EnumField(PlayerPosition, True)
    status = EnumField(PlayerStatus, True)