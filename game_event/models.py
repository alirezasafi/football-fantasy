from config import db
import enum
from sqlalchemy.dialects.postgresql import ENUM

from player.models import Player
from match.models import Match
class EventType(enum.Enum):
    GO = 'Goal'
    AS = 'Assist'
    CD = 'Card'


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    player_id = db.Column(db.Integer, db.ForeignKey(Player.id))
    event_type = db.Column(ENUM(EventType, name="event_type"))
    minute = db.Column(db.Integer)
    match_id = db.Column(db.Integer, db.ForeignKey(Match.id))
