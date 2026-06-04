from database import db

class Log(db.Model):
    __tablename__ = "log"

    log_id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey("cases.case_id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)

    action = db.Column(db.String(100), nullable=False)

    old_status_id = db.Column(db.Integer, db.ForeignKey("status.status_id"))
    new_status_id = db.Column(db.Integer, db.ForeignKey("status.status_id"))

    created_at = db.Column(db.DateTime, server_default=db.func.now())
