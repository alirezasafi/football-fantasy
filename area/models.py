from config import db

class Area(db.Model):
    __tablename__ = 'Area'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    clubs = db.relationship('Club', backref='area', lazy=True)
    competitions = db.relationship('Competition', backref='area', lazy=True)