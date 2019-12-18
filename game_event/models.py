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

class EventImage(enum.Enum):
    GO = 'https://c7.uihere.com/files/187/994/415/goal-football-clip-art-hand-painted-football-goals.jpg'
    OWNGO = 'https://mpng.pngfly.com/20180208/wvw/kisspng-football-goal-clip-art-flaming-dragon-cliparts-5a7cad6892f820.297351721518120296602.jpg'
    AS = 'https://cdn2.iconfinder.com/data/icons/sports-v2/512/Football.png'
    YELLOW_CARD = 'https://images.vexels.com/media/users/3/146861/isolated/preview/dcafb4e33c5514e9b53b3d929501feaf-football-yellow-card-icon-by-vexels.png'
    YELLOW_RED_CARD = 'https://cdn1.iconfinder.com/data/icons/soccer-flat/64/soccer-18-512.png'
    RED_CARD = 'https://images.vexels.com/media/users/3/146857/isolated/preview/d55e89657228964a776f7dab3c0537ca-football-red-card-icon-by-vexels.png'

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
