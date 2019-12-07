from config import db
import enum
from sqlalchemy.dialects.postgresql import ENUM

from player.models import Player
from match.models import Match
class EventType(enum.Enum):
    GO = 'Goal'
    OWNGO = 'OwnGoal'
    AS = 'Assist'
    YELLOW_CARD = 'YellowCard'
    YELLOW_RED_CARD = 'YellowRedCard'
    RED_CARD = 'RedCard'

class MatchSubstitution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_in_id = db.Column(db.Integer, db.ForeignKey(Player.id))
    player_out_id = db.Column(db.Integer, db.ForeignKey(Player.id))
    minute = db.Column(db.Integer)
    match_id = db.Column(db.Integer, db.ForeignKey(Match.id))
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey(Player.id))
    event_type = db.Column(ENUM(EventType, name="event_type"))
    minute = db.Column(db.Integer)
    match_id = db.Column(db.Integer, db.ForeignKey(Match.id))
