from config import ma
from .models import User
from marshmallow import post_load

class UserSchema(ma.TableSchema):
    class Meta:
        table = User.__table__
        exclude = ('password',)

    @post_load
    def load(self, data):
        return User(**data)