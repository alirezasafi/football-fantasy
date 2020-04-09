from config import db
from player.models import Player
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200))
    is_admin = db.Column(db.Boolean)
    is_confirmed = db.Column(db.Boolean)
    squads = db.relationship('squad', cascade="all,delete", backref='user')

    def __repr__(self):
        return '<User %r>' % self.username