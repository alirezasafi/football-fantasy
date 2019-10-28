from config import db
import enum
from sqlalchemy.dialects.postgresql import ENUM


class Position(enum.Enum):
    GP = 'Goalkeeper'
    DF = 'Defender'
    MF = 'Midfielder'
    FD = 'Forward'


class Status(enum.Enum):
    I = "injured"
    C = "cure"
    D = "doubtful"


class Player(db.Model):
    __tablename__ = 'Player'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    shirt_name = db.Column(db.String(140))
    price = db.Column(db.Float)
    image = db.Column(db.String(100))
    shirt_number = db.Column(db.Integer)
    club = db.Column(db.String(140))
    position = db.Column(ENUM(Position, name="Position"))
    status = db.Column(ENUM(Status, name="status"))