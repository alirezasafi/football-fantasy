from config import ma
from .models import Club
from area.marshmallow import AreaSchema

class ClubSchema(ma.ModelSchema):
    class Meta:
        model = Club
        fields = (
            'id',
            'name',
            'name',
            'shortname',
            'image',
            'lastUpdated',
            'area',
        )
    area = ma.Nested(AreaSchema())