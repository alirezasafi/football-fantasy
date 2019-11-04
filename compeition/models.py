from config import db
from sqlalchemy.dialects.postgresql import ENUM
import enum
from club.models import Area
from club.models import Club

class CompetitionType(enum.Enum):
    LG = 'League'
    RM = 'Room'

club_competition = db.Table('club_competition',
    db.Column('club_id', db.Integer, db.ForeignKey(Club.id), primary_key=True),
    db.Column('competition_id', db.Integer, db.ForeignKey(Competition.id), primary_key=True)
)

class Competition(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    startDate = db.Column(db.DateTime)
    endDate = db.Column(db.DateTime)
    lastUpdated = db.Column(db.DateTime)
    area_id = db.Column(db.Integer, db.ForeignKey(Area.id))
    image = db.Column(db.String(200))
    type = db.Column(ENUM(CompetitionType, name="CompetitionType"))
    clubs = db.relationship(Club, secondary=club_competition, lazy='subquery',
        backref=db.backref('competition', lazy='dynamic'))