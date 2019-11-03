from config import db
from sqlalchemy.dialects.postgresql import ENUM
import enum

class Type(enum.Enum):
    LG = 'League'
    RM = 'Room'

club_competition = db.Table('club_competition',
    db.Column('club_id', db.Integer, db.ForeignKey(club.models.Club.id), primary_key=True),
    db.Column('competition_id', db.Integer, db.ForeignKey(Competition.id), primary_key=True)
)

class Competition(db.Model):
    __tablename__ = 'Competition'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    startDate = db.Column(db.DateTime)
    endDate = db.Column(db.DateTime)
    lastUpdated = db.Column(db.DateTime)
    area_id = db.Column(db.Integer, db.ForeignKey('Area.id'), nullable=False)
    image = db.Column(db.String(200))
    type = db.Column(ENUM(Type, name="Type"))
    clubs = db.relationship('Club', secondary=club_competition, lazy='subquery',
        backref=db.backref('Competition', lazy=True))