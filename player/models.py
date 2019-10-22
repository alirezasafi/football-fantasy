from config import db
import enum


class Position(enum.Enum):
    GP = 'Goalkeeper'
    DF = 'Defender'
    MF = 'Midfielder'
    FD = 'Forward'


class Player(db.Model):
    __tablename__ = 'Player'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(160), nullable=False, unique=True)
    price = db.Column(db.Float)
    image = db.Column(db.String(100))
    shirt_number = db.Column(db.Integer)
    club = db.Column(db.String(140))
    position = db.Column(db.Enum(Position), nullable=False)
    status = db.Column(db.String(140))
