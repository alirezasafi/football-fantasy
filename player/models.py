from config import db
import enum
from sqlalchemy.dialects.postgresql import ENUM
from club.models import Club

class Position(enum.Enum):
    GP = 'Goalkeeper'
    DF = 'Defender'
    MF = 'Midfielder'
    AT = 'Attacker'


class Status(enum.Enum):
    I = "injured"
    C = "cure"
    D = "doubtful"


class Player(db.Model):
    __tablename__ = 'Player'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    price = db.Column(db.Float)
    image = db.Column(db.String(100))
    shirt_number = db.Column(db.Integer)
    club = db.Column(db.Integer, db.ForeignKey('Club.id'))
    position = db.Column(ENUM(Position, name="Position"))
    status = db.Column(ENUM(Status, name="status"))
    events = db.relationship('Event', backref='Player', lazy=True)
