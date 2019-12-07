from config import db
import enum
from sqlalchemy.dialects.postgresql import ENUM
from club.models import Club

class PlayerPosition(enum.Enum):
    Goalkeeper = 'Goalkeeper'
    Defender = 'Defender'
    Midfielder = 'Midfielder'
    Attacker = 'Attacker'


class PlayerStatus(enum.Enum):
    I = "injured"
    C = "cure"
    D = "doubtful"


class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float)
    point = db.Column(db.Integer)
    image = db.Column(db.String(100))
    lastUpdated = db.Column(db.DateTime)
    matches = db.relationship('MatchPlayer', backref='player', lazy='dynamic')
    shirt_number = db.Column(db.Integer)
    club_id = db.Column(db.Integer, db.ForeignKey(Club.id))
    position = db.Column(ENUM(PlayerPosition, name="playerposition"))
    status = db.Column(ENUM(PlayerStatus, name="playerstatus"))
    events = db.relationship('Event', backref='player', lazy='dynamic')
