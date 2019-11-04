from config import db
import enum
from sqlalchemy.dialects.postgresql import ENUM
from club.models import Club

class PlayerPosition(enum.Enum):
    GP = 'Goalkeeper'
    DF = 'Defender'
    MF = 'Midfielder'
    AT = 'Attacker'


class PlayerStatus(enum.Enum):
    I = "injured"
    C = "cure"
    D = "doubtful"


class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    price = db.Column(db.Float)
    image = db.Column(db.String(100))
    shirt_number = db.Column(db.Integer)
    club_id = db.Column(db.Integer, db.ForeignKey(Club.id))
    position = db.Column(ENUM(PlayerPosition, name="playerposition"))
    status = db.Column(ENUM(PlayerStatus, name="playerstatus"))
    events = db.relationship('Event', backref='player', lazy='dynamic')

