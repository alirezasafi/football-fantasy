import enum
from sqlalchemy.dialects.postgresql import ENUM
from config import db
from compeition.models import Competition
from club.models import Club
from player.models import Player

class Status(enum.Enum):
    FINISHED = "Finished"
    IN_PLAY = "In Play"
    PAUSED = "Paused"
    SCHEDULED = "Scheduled"


class PlayerPlayingStatus(enum.Enum):
    LN = "Lineup"
    BN = "Bench"


class HomeAway(enum.Enum):
    HOME = "Home"
    AWAY = "Away"

class MatchPlayer(db.Model):
    __tablename__='MatchPlayer'
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey(Player.id), nullable=False)
    match_id = db.Column(db.Integer, db.ForeignKey('match.id'), nullable=False)
    player_score = db.Column(db.Integer)
    lastUpdated = db.Column(db.DateTime)
    minutes_played = db.Column(db.Integer)
    home_away = db.Column(ENUM(HomeAway, name='HomeAway'))
    playerPlayingStatus = db.Column(ENUM(PlayerPlayingStatus, name="PlayerPlayingStatus"))

class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    competition_id = db.Column(db.Integer, db.ForeignKey(Competition.id), nullable=False)
    competition = db.relationship("Competition", foreign_keys=[competition_id])
    utcDate = db.Column(db.DateTime, nullable=False)
    lastUpdated = db.Column(db.DateTime, nullable=False)
    status = db.Column(ENUM(Status, name="status"), nullable=False)
    events = db.relationship('Event', backref='match', lazy='dynamic')
    homeTeam_id = db.Column(db.Integer, db.ForeignKey(Club.id), nullable=False)
    awayTeam_id = db.Column(db.Integer, db.ForeignKey(Club.id), nullable=False)
    homeTeam = db.relationship("Club", foreign_keys=[homeTeam_id])
    awayTeam = db.relationship("Club", foreign_keys=[awayTeam_id])
    homeTeamCaptain_id = db.Column(db.Integer, db.ForeignKey(Player.id))
    awayTeamCaptain_id = db.Column(db.Integer, db.ForeignKey(Player.id))
    homeTeamCaptain = db.relationship("Player", foreign_keys=[homeTeamCaptain_id])
    awayTeamCaptain = db.relationship("Player", foreign_keys=[awayTeamCaptain_id])
    homeTeamScore = db.Column(db.Integer)
    awayTeamScore = db.Column(db.Integer)
    players = db.relationship('MatchPlayer', backref='match', lazy='dynamic')