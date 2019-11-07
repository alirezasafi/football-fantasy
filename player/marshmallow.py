from config import ma
from .models import Player, PlayerPosition, PlayerStatus
from marshmallow_enum import EnumField
from marshmallow import fields


class PlayerSchema(ma.ModelSchema):
    class Meta:
        model = Player
    position = fields.Method('get_position')
    # position = EnumField(PlayerPosition, True)
    status = EnumField(PlayerStatus, True)
    
    def get_position(self, obj):
        if obj.position == None:
            return None
        if obj.position.value == "Attacker":
            return "Forward"
        return obj.position.value