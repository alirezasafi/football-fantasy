from config import db
from area.models import Area

class Club(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    shortName = db.Column(db.String(50), unique=True)
    image = db.Column(db.String(200))
    lastUpdated = db.Column(db.DateTime)
    area_id = db.Column(db.Integer, db.ForeignKey(Area.id))
    players = db.relationship('Player', backref='club', lazy='dynamic')
