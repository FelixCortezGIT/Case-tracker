from database import db

class Log(db.Model):
    __tablename__ = "logs"

    log_id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey("cases.case_id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    status_id = db.Column(db.Integer, db.ForeignKey("status.status_id"), nullable=False)
    deadline_date = db.Column(db.Date)
    notes_id = db.Column(db.Integer, db.ForeignKey("notes.note_id"), nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    status = db.relationship("Status")
    user = db.relationship("User")
