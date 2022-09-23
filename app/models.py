from flask_login import UserMixin
from app import db

class User(UserMixin, db.Model):
    __tablename__ = 'USERS'
    email = db.Column(db.String(255), primary_key=True)
    last_name = db.Column(db.String(100), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    hash = db.Column(db.String(60))
    salt = db.Column(db.String(60))