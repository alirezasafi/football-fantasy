from config import db
from user.models import User
from player.models import Player
from compeition.models import Competition
from match.models import Match
import datetime
import enum


class squad(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, default =datetime.datetime.utcnow)
    competition_id = db.Column(db.Integer, db.ForeignKey(Competition.id), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    name = db.Column(db.String(80), nullable=True)
    captain = db.Column(db.Integer, db.ForeignKey(Player.id))
    point = db.Column(db.Integer, default=0)
    point_lastUpdated = db.Column(db.DateTime, default = datetime.datetime.utcnow())
    budget = db.Column(db.Float, default=100.0)
    free_transfer = db.Column(db.Boolean, default=True)
    players = db.relationship('squad_player', cascade="all,delete", backref='squad', lazy='dynamic')
    cards = db.relationship('Fantasy_cards', cascade="all,delete", backref='squad', uselist=False)
#squad listener that updates the point last joined when point is changed
@db.event.listens_for(squad.point, 'set')
def after_update(target, value, oldvalue, initiator):
    if oldvalue != value:
        target.point_lastUpdated = datetime.datetime.utcnow()


class squadMatch(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    squad_id = db.Column(db.Integer, db.ForeignKey(squad.id), nullable = False)
    match_id = db.Column(db.Integer, db.ForeignKey(Match.id), nullable = False)
    point = db.Column(db.Integer, default = 0)



class Fantasy_cards(db.Model):
    __tablename__ = 'fantasy_cards'
    id = db.Column(db.Integer, primary_key=True)
    squad_id = db.Column(db.Integer, db.ForeignKey(squad.id), nullable=False)
    bench_boost = db.Column(db.Integer, default=0, nullable=False)
    free_hit = db.Column(db.Integer, default=0, nullable=False)
    triple_captain = db.Column(db.Integer, default=0, nullable=False)
    wild_card = db.Column(db.Integer, default=0, nullable=False)


class squad_player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    squad_id = db.Column(db.Integer, db.ForeignKey(squad.id), nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey(Player.id), nullable=False)
    lineup = db.Column(db.Boolean, nullable=False)
    joined_date = db.Column(db.DateTime, default = datetime.datetime.utcnow())
#listener that updates the last joined
@db.event.listens_for(squad_player.player_id, 'set')
def after_update(target, value, oldvalue, initiator):
    squad_player_table = squad_player.__table__
    if oldvalue != value:
        target.joined_date = datetime.datetime.utcnow()


class CardStatus(enum.Enum):
    active = "1"
    inactive = "0"
    used = "-1"


class CardsType(enum.Enum):
    bench_boost = "bench_boost"
    free_hit = "free_hit"
    triple_captain = "triple_captain"
    wild_card = "wild_card"


class CardsCategory(enum.Enum):
    transfer_cards = ["wild_card", "free_hit"]
    score_cards = ["bench_boost", "triple_captain"]
