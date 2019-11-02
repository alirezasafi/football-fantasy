from config import db
from user.models import User
from player.models import Player


class User_Player(db.Model):
    __tablename__ = 'User_Player'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey(Player.id), nullable=False)
    lineup = db.Column(db.Boolean, nullable=True, default=False)


class Fantasy_cards(db.Model):
    __tablename__ = 'fantasy_cards'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    bench_boost = db.Column(db.Integer, default=0, nullable=False)
    free_hit = db.Column(db.Integer, default=0, nullable=False)
    triple_captain = db.Column(db.Integer, default=0, nullable=False)
    wild_card = db.Column(db.Integer, default=0, nullable=False)