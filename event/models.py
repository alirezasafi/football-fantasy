from config import db
import enum
from sqlalchemy.dialects.postgresql import ENUM

import player.models
import match.models
class Type(enum.Enum):
    GO = 'Goal'
    AS = 'Assist'
    CD = 'Card'


class Event(db.Model):
    __tablename__ = 'Event'
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('Player.id'))
    type = db.Column(ENUM(Type, name="Type"))
    minute = db.Column(db.Integer)
    match_id = db.Column(db.Integer, db.ForeignKey('Match.id'))
