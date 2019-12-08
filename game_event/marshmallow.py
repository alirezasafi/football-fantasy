from config import ma
from marshmallow_enum import EnumField
from .models import EventType, Event


class EventSchema(ma.ModelSchema):
    event_type = EnumField(EventType, True)

    class Meta:
        model = Event
