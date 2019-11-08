from config import ma
from .models import Competition
from area.marshmallow import AreaSchema

class CompetitionSchema(ma.ModelSchema):
    class Meta:
        model = Competition
        exclude = ('clubs',)
    area = ma.Nested(AreaSchema())
