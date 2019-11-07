from config import ma
from .models import Area

class AreaSchema(ma.ModelSchema):
    class Meta:
        model = Area
        fields=(
            'id',
            'name',
        )