import enum
from sqlalchemy.dialects.postgresql import ENUM
from config import db
from compeition.models import Competition
from club.models import Club
from player.models import Player

class Status(enum.Enum):
    FN = "Finished"
    SC = "scheduled"


class PlayerStatus(enum.Enum):
    LN = "Lineup"
    BN = "Bench"

class MatchPlayer(db.Model):
    __tablename__='MatchPlayer'
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey(Player.id), nullable=False)
    match_id = db.Column(db.Integer, db.ForeignKey('match.id'), nullable=False)
    playerStatus = db.Column(ENUM(PlayerStatus, name="playerstatus"))

class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    competition_id = db.Column(db.Integer, db.ForeignKey(Competition.id), nullable=False)
    utcDate = db.Column(db.DateTime, nullable=False)
    status = db.Column(ENUM(Status, name="status"), nullable=False)
    events = db.relationship('Event', backref='match', lazy='dynamic')
    homeTeam = db.Column(db.Integer, db.ForeignKey(Club.id), nullable=False)
    awayTeam = db.Column(db.Integer, db.ForeignKey(Club.id), nullable=False)