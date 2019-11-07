from config import ma
from .models import User

class UserSchema(ma.TableSchema):
    class Meta:
        table = User.__table__
        exclude = ('password',)