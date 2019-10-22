from config import db
from user.models import User
from player.models import Player


class Squad(db.Model):
    __tablename__ = 'Squad'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey(Player.id), nullable=False)
    lineup = db.Column(db.Boolean, nullable=True, default=False)
