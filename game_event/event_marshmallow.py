from config import ma
from .models import Event, EventType
from marshmallow_enum import EnumField
from player.marshmallow import PlayerSchema


class EventSchema(ma.ModelSchema):
    class Meta:
        model = Event
        exclude = ('match_id',)
    event_type = EnumField(EventType, True)
    player = ma.Nested(PlayerSchema())
    