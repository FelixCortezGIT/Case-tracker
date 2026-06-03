from database import db

class User(db.Model):
    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable=False, unique=True)
    password_hash = db.Column(db.String(30), nullable=False)
    role = db.Column(db.String(30), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
