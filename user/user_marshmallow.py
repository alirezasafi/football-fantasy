from config import ma
from .models import User
from marshmallow import post_load, Schema, fields
from team.models import squad
from player.models import Player

class UserSchema(ma.TableSchema):
    class Meta:
        table = User.__table__
        exclude = ('password',)

    @post_load
    def load(self, data):
        return User(**data)


class UserSquadSchema(ma.TableSchema):
    captain = fields.Method('get_captain')
    competition = fields.Method('get_competition')

    class Meta:
        model = squad.__table__
        fields = ('name', 'captain', 'point', 'budget', 'competition')

    def get_competition(self, obj):
        from compeition.competition_marshmallow import CompetitionSchema, Competition
        competition = Competition.query.filter_by(id=obj.competition_id).first()
        competition_schema = CompetitionSchema()
        return competition_schema.dump(competition)

    def get_captain(self, obj):
        from player.player_marshmallow import PlayerSchema
        captain = Player.query.filter_by(id=obj.captain).first()
        captain_schema = PlayerSchema(only={'name', 'image', 'point', 'position', 'price', 'shirt_number', 'status'})
        return captain_schema.dump(captain)


class ProfileSchema(Schema):
    user = fields.Nested(UserSchema, only={'username', 'email'})
    squads = fields.Nested(UserSquadSchema, many=True)
