from config import db

class Area(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    clubs = db.relationship('Club', backref='area', lazy='dynamic')
    # competitions = db.relationship('Competition', backref='area', lazy='dynamic')