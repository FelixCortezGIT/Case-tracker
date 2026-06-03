from database import db

class Status(db.Model):
    __tablename__ = "status"

    status_id = db.Column(db.Integer, primary_key=True)
    status_name = db.Column(db.String(30), nullable=False, unique=True)
