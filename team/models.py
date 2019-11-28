from config import db
from user.models import User
from player.models import Player
from compeition.models import Competition


class squad(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    competition_id = db.Column(db.Integer, db.ForeignKey(Competition.id), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    name = db.Column(db.String(80), nullable=True)
    captain = db.Column(db.Integer, db.ForeignKey(Player.id))
    point = db.Column(db.Integer, default=0)
    budget = db.Column(db.Float, default=100.0)
    players = db.relationship('squad_player', cascade="all,delete", backref='squad', lazy='dynamic')
    cards = db.relationship('Fantasy_cards', cascade="all,delete", backref='squad', uselist=False)


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
