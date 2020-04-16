from config import ma
from flask import current_app
from .models import Player, PlayerPosition, PlayerStatus
from marshmallow_enum import EnumField
from marshmallow import fields
from club.club_marshmallow import ClubSchema


class PlayerSchema(ma.ModelSchema):
    class Meta:
        model = Player
        exclude = ('matches','events')
    position = fields.Method('get_position')
    image = fields.Method('get_image')
    # position = EnumField(PlayerPosition, True)
    status = EnumField(PlayerStatus, True)

    def get_image(self, obj):
        return "{}player/media/{}.png".format(current_app.config['DOMAIN_ADDRESS'], obj.image)

    def get_position(self, obj):
        if obj.position == None:
            return None
        if obj.position.value == "Attacker":
            return "Forward"
        return obj.position.value

    def dump_players(self, data, lineup):
        players = self.dump(data, many=True)
        for player in players:
            player['lineup'] = lineup
        return players

class PlayerEventSchema(ma.ModelSchema):
    class Meta:
        model = Player
        exclude = ('matches','events')
    position = fields.Method('get_position')
    # position = EnumField(PlayerPosition, True)
    status = EnumField(PlayerStatus, True)
    club = ma.Nested(ClubSchema())
    
    def get_position(self, obj):
        if obj.position == None:
            return None
        if obj.position.value == "Attacker":
            return "Forward"
        return obj.position.value

    def dump_players(self, data, lineup):
        players = self.dump(data, many=True)
        for player in players:
            player['lineup'] = lineup
        return players

